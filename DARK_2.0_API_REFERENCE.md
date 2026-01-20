# dARK 2.0 - API & Library Developer Reference

> This guide is part of the [dARK 2.0 Documentation](README.md).
> See also: [Developer Guide](DARK_2.0_GUIDE.md) | [Architecture](DARK_2.0_ARCHITECTURE.md)

This guide provides technical specifications for developers building APIs, SDKs, or libraries on top of the dARK 2.0 smart contracts.

## 1. Contract Interfaces

### 1.1 Authority Contract (`Authority`)
Manages identity and write permissions.

**View Functions**
*   `is_authorized(address wallet, string val naan) returns (bool)`
    *   Checks if a specific wallet has permission to create/update ARKs for a given NAAN.
    *   *Usage*: Call before attempting `create_ark`.
*   `get_authority(string val uuid) returns (address wallet, string[] naans, bool active)`
    *   Returns full authority details.
    *   *Reverts*: If UUID is not registered.
*   `get_uuid_by_wallet(address wallet) returns (string uuid)`
    *   Reverse lookup.
    *   *Reverts*: If wallet is not associated with any authority.

**Write Functions**
*   `register_authority(string uuid, address wallet, string encrypted_private_key)`
    *   *Access*: Admin only.
    *   *Gas*: ~80k-120k.
    *   *Params*: `encrypted_private_key` - AES-256 encrypted private key (hex encoded).
    *   *Errors*: "UUID already registered", "Wallet already registered", "Empty encrypted key".
*   `get_authority_key(string uuid) returns (string encrypted_private_key)`
    *   *Access*: Admin only.
    *   *Returns*: The encrypted private key for the authority.
    *   *Reverts*: If UUID is not registered.
*   `authorize_naan(string naan)`
    *   *Access*: Registered Active Authority.
    *   *Gas*: ~60k.
    *   *Errors*: "NAAN already authorized".

### 1.2 dARK Contract (`dARK`)
Manages ARK lifecycle and storage.

**View Functions**
*   `resolve(string val naan, string val name) returns (string url)`
    *   Primary resolution function.
    *   *Reverts*: "ARK not found" if does not exist.
*   `ark_exists(string val naan, string val name) returns (bool)`
    *   Safe check without revert.
*   `get_ark(string val naan, string val name) returns (tuple)`
    *   Returns: `(name, naan, url, cid, owner, created_at, updated_at)`.
    *   *Reverts*: "ARK not found".

**Write Functions**
*   `create_ark(string naan, string name, string url, string cid)`
    *   *Access*: Wallet authorized for `naan` via Authority contract.
    *   *Gas*: **High** (~200k - 300k) due to string storage.
    *   *Errors*: "Not authorized for NAAN", "ARK already exists".
*   `update_ark(string naan, string name, string url, string cid)`
    *   *Access*: Original Owner of the ARK **AND** currently authorized for NAAN.
    *   *Errors*: "Not ARK owner", "Not authorized for NAAN".

---

## 2. Event Indexing

For high-performance APIs, index these events instead of making RPC calls.

### Authority Events
```solidity
event AuthorityRegistered(string indexed uuid, address indexed wallet);
event NAANAuthorized(address indexed wallet, string naan);
event NAANRevoked(address indexed wallet, string naan);
```
*   **Indexing Strategy**: Monitor `AuthorityRegistered` to build a local map of `Wallet <-> UUID`. Monitor `NAANAuthorized` to track which wallet controls which NAANs.

### dARK Events
```solidity
event ARKCreated(string naan, string name, address indexed owner, string url, string cid);
event ARKUpdated(string naan, string name, string url, string cid);
```
*   **Indexing Strategy**: The `ARKCreated` event contains **all** necessary data to serve resolution requests off-chain. You do not need to query contract storage if you index this event.
*   **Identifier**: The unique identifier key is the combination `naan` + `name`.

---

## 3. Integration Guidelines

### 3.1 Gas & Transaction Safety
*   **String Handling**: dARK relies heavily on string keys (`naan`, `name`). These are expensive in EVM. Ensure your API client estimates gas correctly, or hardcodes a safe buffer (e.g., 500k for creation).
*   **Status Checks**: Always check `receipt.status == 1`. Simple calls like `create_ark` may fail silently (revert) if the user lost authorization or if the ARK exists, depending on the client library.

### 3.2 Error Handling Map
| Error String | Cause | Action |
| :--- | :--- | :--- |
| `Authority not found` | UUID lookup on non-existent auth | Register authority or check UUID |
| `Wallet already registered` | Registering a wallet twice | Use `get_uuid_by_wallet` to find existing UUID |
| `Not authorized for NAAN` | Wallet tries to create ARK in restricted NAAN | Call `authorize_naan` first |
| `ARK already exists` | Duplicate Creation | Use `update_ark` instead |
| `Not ARK owner` | Update attempt by non-owner | Only original creator can update |

### 3.3 Stack Depth Warning
*   **Legacy Note**: Previous versions had "Stack too deep" issues. v2.0 fixes this by inlining logic. If you fork the code and add modifiers to `create_ark` or `update_ark`, you may hit this limit again. Keep function signatures clean.

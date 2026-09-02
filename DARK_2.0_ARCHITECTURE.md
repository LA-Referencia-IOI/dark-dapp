# dARK 2.0 - Technical Architecture

> This guide is part of the dARK 2.0 documentation. See the repository-level
> architecture and deployment runbook for the complete runtime topology.

This document details the **Authority-Centric** architecture (v2.0) of the dARK decentralized identifier system.

## 1. Core Architecture Changes

The monolithic design has been refactored into two distinct contracts to separate **Access Control** from **Data Storage**.

### 1.1 Authority Contract (`Authority.sol`)
Ref: [Authority.sol](dARK_dapp/contracts/Authority.sol)
*   **Role**: Acts as the central registry for Authorities (organizations) and their permissions.
*   **Key Concept**: One Wallet = One Authority.
*   **Functions**:
    *   `register_authority(uuid, wallet)`: Binds an external Organization UUID to an Ethereum Wallet.
    *   `authorize_naan(naan)`: Authority claims management of a specific NAAN (Name Assigning Authority Number).
    *   `is_authorized(wallet, naan)`: Validates if a wallet has permission to write to a NAAN.

### 1.2 dARK Contract (`dARK.sol`)
Ref: [dARK.sol](dARK_dapp/contracts/dARK.sol)
*   **Role**: Pure storage for ARK identifiers (`ark:/NAAN/Name`).
*   **Dependency**: does **not** manage permissions internally. Instead, it holds a reference to the `Authority` contract.
*   **Modifiers**:
    *   `onlyAuthorizedFor(naan)`: Before creating an ARK, it calls `Authority.is_authorized(msg.sender, naan)`.

---

## 2. Interaction Flow

The lifecycle of an ARK in v2.0 follows this strict sequence:

### Phase 1: Authority Setup (One-time)
1.  **Deploy**: Deploy `Authority.sol`, then `dARK.sol` (linking it to Authority address).
2.  **Register**: Admin calls `register_authority("org-uuid-1", admin_wallet)`.
3.  **Authorize**: Admin calls `authorize_naan("12345")`.

### Phase 2: ARK Management
1.  **Creation**:
    *   User calls `dARK.create_ark("12345", "doc1", url, cid)` on the dARK
        network (`CHAIN_ID=2025`).
    *   `dARK` contract asks `Authority`: "Is `msg.sender` authorized for NAAN `12345`?"
    *   If `true`, ARK is stored.
2.  **Resolution**:
    *   Anyone calls `dARK.resolve("12345", "doc1")`.
    *   Returns `url`.

---

## 3. Key Improvements

| Feature | dARK v1 (Legacy) | dARK v2 (Current) |
| :--- | :--- | :--- |
| **Permissions** | Mixed in `dARK.sol` | Delegated to `Authority.sol` |
| **Identity** | Implicit | Explicit UUID <-> Wallet binding |
| **Scalability** | Harder to upgrade logic | Contracts can be upgraded independently |
| **Gas Cost** | Higher (complex logic) | Optimized (separation of concerns) |

---

## 4. Developer Reference

### Python Usage (Web3.py)
Based on `dark_testing.ipynb`, here is how to interact:

```python
# 1. Register Authority (if not exists)
# encrypted_key = AES-256 encrypted private key (hex encoded)
encrypted_key = "0x..."  # Your encrypted key here
try:
    auth.functions.register_authority("uuid-1", wallet, encrypted_key).transact()
except:
    pass # Already registered

# 2. Authorize NAAN
auth.functions.authorize_naan("55555").transact()

# 3. Create ARK (Note: requires ~200k+ gas)
dark.functions.create_ark("55555", "my-doc", url, cid).transact({'gas': 500000})
```

### Common Pitfalls
*   **"Authority not found"**: You tried to act without registering your wallet first.
*   **"Wallet already registered"**: A wallet can only represent **one** Authority UUID.
*   **"Stack too deep"**: Solved in v2 by optimizing struct visibility and inlining modifiers.

## 5. Runtime integration

The blockchain contracts are one stage of the minter pipeline. Production runs
four independent minter processes: the HTTP API, `MetadataPersistenceWorker`,
`ReplicationReconciliationWorker`, and `ChainPublisherWorker`. Alembic
migrations are applied explicitly before startup; containers do not migrate
the schema automatically. The replication worker verifies and repairs Level 1
and Level 2 replicas and purges retained payloads only after both targets are
met; only the chain worker publishes the Level 1 CID on-chain.

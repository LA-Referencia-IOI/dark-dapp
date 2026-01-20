# dARK 2.0 - Developer Guide

> This guide is part of the [dARK 2.0 Documentation](README.md).
> See also: [Architecture](DARK_2.0_ARCHITECTURE.md) | [API Reference](DARK_2.0_API_REFERENCE.md)

## Overview

**dARK 2.0** is a minimal, gas-optimized smart contract system for managing [ARK (Archival Resource Key)](https://arks.org/) identifiers on the Ethereum blockchain. 

Unlike v1.0, dARK 2.0 uses a **split architecture** that separates access control from storage:
1.  **Authority Contract**: Manages organizations (Authorities) and their permission to mint ARKs for specific NAANs (Name Assigning Authority Numbers).
2.  **dARK Contract**: Pure storage for ARK identifiers, relying on the Authority contract for permission checks.

## Architecture

```mermaid
graph TB
    subgraph "Access Control Layer"
        Auth[Authority.sol<br/>(Registry of Orgs & NAANs)]
    end

    subgraph "Storage Layer"
        Storage[dARK.sol<br/>(ARK Data Store)]
    end
    
    Admin[Admin] -->|register_authority| Auth
    Authority[Authority Wallet] -->|authorize_naan| Auth
    
    User[User/Authority] -->|create_ark| Storage
    Storage -.->|is_authorized?| Auth
    
    Client[External Client] -->|resolve| Storage
```

For a deeper dive into the system design, see [DARK_2.0_ARCHITECTURE.md](DARK_2.0_ARCHITECTURE.md).

## Data Structures

### ARK Struct (`dARK.sol`)
The core identifier record.
```solidity
struct ARK {
    string name;        // The specific identifier (e.g., "abc12345")
    string naan;        // The NAAN (e.g., "12345")
    string url;         // Resolution URL
    string cid;         // IPFS CID for metadata
    address owner;      // Wallet that created the ARK
    uint256 created_at; // Timestamp
    uint256 updated_at; // Timestamp
}
```

### AuthorityData Struct (`Authority.sol`)
Represents an organization managing ARKs.
```solidity
struct AuthorityData {
    string uuid;                  // External Organization ID
    address wallet;               // Wallet address for signing
    bool active;                  // Status
    string encrypted_private_key; // Encrypted key for recovery/transport
}
```

---

## Usage Guide

This section covers the typical lifecycle of interacting with dARK v2.0. For the full function list, see the [API Reference](DARK_2.0_API_REFERENCE.md).

### 1. Setup (Admin)
The **Admin** registers an **Authority** (Organization). This links a UUID (e.g., from an external database) to an Ethereum Wallet.

```javascript
// Register an Authority
await authorityContract.register_authority(
    "org-uuid-v1", 
    "0xAuthoritedWallet...", 
    "0xEncryptedKey..."
);
```

### 2. Authorization (Authority)
The **Authority** claims management rights for a specific NAAN. This allows them to mint identifiers under `ark:/NAAN/...`.

```javascript
// Authority claims their NAAN
// Must be called by "0xAuthoritedWallet..."
await authorityContract.authorize_naan("99999");
```

### 3. Minting (Authority)
The **Authority** mints a new ARK. The contract verifies that the caller is authorized for the provided NAAN.

```javascript
// Mint a new ARK: ark:/99999/b123
await darkContract.create_ark(
    "99999", 
    "b123", 
    "https://museum.org/b123", 
    "QmMetadataHash..."
);
```

### 4. Resolution (Public)
Anyone can resolve an ARK ID to its target URL.

```javascript
const url = await darkContract.resolve("99999", "b123");
console.log(url); // "https://museum.org/b123"
```

---

## Events for Indexing

These events are emitted to allow off-chain indexers (like The Graph) to build a queryable state without reading from the blockchain storage directly.

| Contract | Event | Parameters | Description |
|----------|-------|------------|-------------|
| Authority | `AuthorityRegistered` | `uuid`, `wallet` | New organization onboarded |
| Authority | `NAANAuthorized` | `wallet`, `naan` | Authority claimed a NAAN |
| dARK | `ARKCreated` | `naan`, `name`, `owner`, `url`, `cid` | **Primary indexing event** |
| dARK | `ARKUpdated` | `naan`, `name`, `url`, `cid` | Metadata changed |

---

## Comparison: v1.0 vs v2.0

| Feature | v1.0 (Legacy) | v2.0 (Current) |
| :--- | :--- | :--- |
| **Architecture** | Monolithic (One Contract) | **Modular (Authority + Storage)** |
| **Permissions** | Mixed with storage logic | **Delegated to Authority Registry** |
| **Identifier** | Hash-based / NOID | **Explicit `naan` + `name` strings** |
| **Flexibility** | Rigid ownership | **Flexible Authority-based control** |
| **Gas Efficiency** | Expensive Logic | **Optimized Storage Operations** |

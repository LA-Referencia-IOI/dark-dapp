// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.17;

import "./IAuthority.sol";

/**
 * @title dARK 2.0
 * @notice Minimal decentralized ARK identifier registry
 * @dev Stores ARK identifiers with URL and IPFS CID, managed by authorized authorities
 */
contract dARK {
    // ═══════════════════════════════════════════════════════════════════════
    // STRUCTURES
    // ═══════════════════════════════════════════════════════════════════════

    struct ARK {
        string name;
        string naan;
        string url; // Resolution URL
        string cid; // IPFS CID for metadata
        address owner; // Owner (authority wallet at creation time)
        uint256 created_at; // Creation timestamp
        uint256 updated_at; // Last update timestamp
    }

    // ═══════════════════════════════════════════════════════════════════════
    // STATE
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice Authority contract reference
    IAuthority private _authority;

    /// @notice ARK hash to ARK data mapping (hash of "naan/name")
    mapping(bytes32 => ARK) private _arks;

    /// @notice Total number of ARKs created
    uint256 private _ark_count;
    mapping(address => uint256) private _owned_ark_count;
    address public migration_source;

    // ═══════════════════════════════════════════════════════════════════════
    // EVENTS
    // ═══════════════════════════════════════════════════════════════════════

    event ARKCreated(
        string naan,
        string name,
        address indexed owner,
        string url,
        string cid
    );

    event ARKUpdated(string naan, string name, string url, string cid);
    event ARKOwnershipTransferred(string naan, string name, address indexed previous_owner, address indexed new_owner, address indexed administrator);

    // ═══════════════════════════════════════════════════════════════════════
    // MODIFIERS
    // ═══════════════════════════════════════════════════════════════════════

    modifier onlyAuthorizedFor(string calldata naan) {
        require(
            _authority.is_authorized(msg.sender, naan),
            "Not authorized for NAAN"
        );
        _;
    }

    modifier onlyARKOwner(string calldata naan, string calldata name) {
        bytes32 ark_hash = _compute_hash(naan, name);
        require(_arks[ark_hash].owner == msg.sender, "Not ARK owner");
        _;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CONSTRUCTOR
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Initialize dARK with Authority contract address
     * @param authority_address Address of the Authority contract
     */
    constructor(address authority_address) {
        require(authority_address != address(0), "Invalid authority address");
        _authority = IAuthority(authority_address);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // ARK FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Create a new ARK
     */
    function create_ark(
        string calldata naan,
        string calldata name,
        string calldata url,
        string calldata cid
    ) external onlyAuthorizedFor(naan) {
        require(bytes(name).length > 0, "Empty name");

        bytes32 ark_hash = _compute_hash(naan, name);

        // Verify ARK doesn't exist
        require(_arks[ark_hash].owner == address(0), "ARK already exists");

        // Store ARK
        _arks[ark_hash] = ARK({
            name: name,
            naan: naan,
            url: url,
            cid: cid,
            owner: msg.sender,
            created_at: block.timestamp,
            updated_at: block.timestamp
        });

        // increment counter
        _ark_count += 1;
        _owned_ark_count[msg.sender] += 1;

        emit ARKCreated(naan, name, msg.sender, url, cid);
    }

    /**
     * @notice Update URL and/or CID of an existing ARK
     */
    function update_ark(
        string calldata naan,
        string calldata name,
        string calldata url,
        string calldata cid
    ) external onlyAuthorizedFor(naan) {
        bytes32 ark_hash = _compute_hash(naan, name);
        require(_arks[ark_hash].owner == msg.sender, "Not ARK owner");

        _arks[ark_hash].url = url;
        _arks[ark_hash].cid = cid;
        _arks[ark_hash].updated_at = block.timestamp;

        emit ARKUpdated(naan, name, url, cid);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // VIEW FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice Pin the immutable source once, before importing existing records.
    function set_migration_source(address source) external {
        require(msg.sender == _authority.admin(), "Admin only");
        require(migration_source == address(0) && _ark_count == 0, "Migration already initialized");
        require(source != address(0) && source != address(this), "Invalid source");
        require(dARK(source).get_authority_contract() == address(_authority), "Different authority registry");
        migration_source = source;
    }

    /// @notice Import existing PIDs without changing content, owner or timestamps.
    function import_arks(string[] calldata naans, string[] calldata names) external {
        require(msg.sender == _authority.admin(), "Admin only");
        require(migration_source != address(0), "Migration source not configured");
        require(naans.length == names.length && names.length > 0 && names.length <= 30, "Invalid batch");
        for (uint256 i = 0; i < names.length; i++) {
            bytes32 ark_hash = _compute_hash(naans[i], names[i]);
            require(_arks[ark_hash].owner == address(0), "ARK already exists");
            ARK memory original = dARK(migration_source).get_ark(naans[i], names[i]);
            _arks[ark_hash] = original;
            _owned_ark_count[original.owner] += 1;
            _ark_count += 1;
            emit ARKCreated(original.naan, original.name, original.owner, original.url, original.cid);
        }
    }

    function get_owned_ark_count(address wallet) external view returns (uint256) {
        return _owned_ark_count[wallet];
    }

    function transfer_ark_owner(string calldata naan, string calldata name,
        address expected_owner, address new_owner) external {
        require(msg.sender == _authority.admin(), "Admin only");
        bytes32 ark_hash = _compute_hash(naan, name);
        ARK storage ark = _arks[ark_hash];
        require(ark.owner != address(0), "ARK not found");
        require(ark.owner == expected_owner, "Owner changed");
        require(new_owner != address(0) && new_owner != expected_owner, "Invalid new owner");
        require(_authority.is_active_authority(new_owner), "Destination inactive");
        require(_authority.is_authorized(new_owner, naan), "Destination NAAN unauthorized");
        _owned_ark_count[expected_owner] -= 1;
        _owned_ark_count[new_owner] += 1;
        ark.owner = new_owner;
        ark.updated_at = block.timestamp;
        emit ARKOwnershipTransferred(naan, name, expected_owner, new_owner, msg.sender);
    }

    function resolve(
        string calldata naan,
        string calldata name
    ) external view returns (string memory url) {
        bytes32 ark_hash = _compute_hash(naan, name);
        require(_arks[ark_hash].owner != address(0), "ARK not found");
        return _arks[ark_hash].url;
    }

    function get_ark(
        string calldata naan,
        string calldata name
    ) external view returns (ARK memory ark) {
        bytes32 ark_hash = _compute_hash(naan, name);
        require(_arks[ark_hash].owner != address(0), "ARK not found");
        return _arks[ark_hash];
    }

    function ark_exists(
        string calldata naan,
        string calldata name
    ) external view returns (bool) {
        bytes32 ark_hash = _compute_hash(naan, name);
        return _arks[ark_hash].owner != address(0);
    }

    /**
     * @notice Number of ARKs created (for analytics, not used in logic)
     */
    function get_ark_count() external view returns (uint256) {
        return _ark_count;
    }

    function get_authority_contract() external view returns (address) {
        return address(_authority);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // INTERNAL FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    function _compute_hash(
        string calldata naan,
        string calldata name
    ) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked(naan, "/", name));
    }
}
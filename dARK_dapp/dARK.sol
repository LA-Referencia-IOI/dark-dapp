// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

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
     * @param naan The NAAN (e.g., "12345")
     * @param name The name/identifier within the NAAN (e.g., "abc123")
     * @param url Resolution URL
     * @param cid IPFS CID for metadata
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

        emit ARKCreated(naan, name, msg.sender, url, cid);
    }

    /**
     * @notice Update URL and/or CID of an existing ARK
     * @param naan The NAAN of the ARK
     * @param name The name of the ARK
     * @param url New resolution URL
     * @param cid New IPFS CID
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

    /**
     * @notice Resolve an ARK to its URL
     * @param naan The NAAN
     * @param name The name
     * @return url The resolution URL
     */
    function resolve(
        string calldata naan,
        string calldata name
    ) external view returns (string memory url) {
        bytes32 ark_hash = _compute_hash(naan, name);
        require(_arks[ark_hash].owner != address(0), "ARK not found");
        return _arks[ark_hash].url;
    }

    /**
     * @notice Get full ARK data
     * @param naan The NAAN
     * @param name The name
     * @return ark The complete ARK struct
     */
    function get_ark(
        string calldata naan,
        string calldata name
    ) external view returns (ARK memory ark) {
        bytes32 ark_hash = _compute_hash(naan, name);
        require(_arks[ark_hash].owner != address(0), "ARK not found");
        return _arks[ark_hash];
    }

    /**
     * @notice Check if an ARK exists
     * @param naan The NAAN
     * @param name The name
     * @return True if the ARK exists
     */
    function ark_exists(
        string calldata naan,
        string calldata name
    ) external view returns (bool) {
        bytes32 ark_hash = _compute_hash(naan, name);
        return _arks[ark_hash].owner != address(0);
    }

    /**
     * @notice Get the Authority contract address
     * @return The Authority contract address
     */
    function get_authority_contract() external view returns (address) {
        return address(_authority);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // INTERNAL FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @dev Compute hash from naan and name
     * @param naan The NAAN
     * @param name The name
     * @return The keccak256 hash of "naan/name"
     */
    function _compute_hash(
        string calldata naan,
        string calldata name
    ) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked(naan, "/", name));
    }
}

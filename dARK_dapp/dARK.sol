// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

/**
 * @title dARK 2.0
 * @notice Minimal decentralized ARK identifier registry
 * @dev Stores ARK identifiers with URL and IPFS CID, managed by NAAN owners
 */
contract dARK {
    // ═══════════════════════════════════════════════════════════════════════
    // STRUCTURES
    // ═══════════════════════════════════════════════════════════════════════

    struct ARK {
        string url; // Resolution URL
        string cid; // IPFS CID for metadata
        address owner; // Owner (NAAN owner at creation time)
        uint256 created_at; // Creation timestamp
        uint256 updated_at; // Last update timestamp
    }

    // ═══════════════════════════════════════════════════════════════════════
    // STATE
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice NAAN to owner address mapping
    mapping(string => address) public naan_owners;

    /// @notice ARK hash to ARK data mapping
    mapping(bytes32 => ARK) private _arks;

    // ═══════════════════════════════════════════════════════════════════════
    // EVENTS
    // ═══════════════════════════════════════════════════════════════════════

    event NAANRegistered(string indexed naan, address indexed owner);
    event NAANTransferred(
        string indexed naan,
        address indexed from,
        address indexed to
    );
    event ARKCreated(
        string ark_id,
        address indexed owner,
        string url,
        string cid
    );
    event ARKUpdated(string ark_id, string url, string cid);

    // ═══════════════════════════════════════════════════════════════════════
    // MODIFIERS
    // ═══════════════════════════════════════════════════════════════════════

    modifier onlyNAANOwner(string calldata naan) {
        require(naan_owners[naan] == msg.sender, "Not NAAN owner");
        _;
    }

    modifier onlyARKOwner(string calldata ark_id) {
        bytes32 ark_hash = keccak256(bytes(ark_id));
        require(_arks[ark_hash].owner == msg.sender, "Not ARK owner");
        _;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // NAAN FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Register a new NAAN for the caller
     * @param naan The NAAN to register (e.g., "12345")
     */
    function register_naan(string calldata naan) external {
        require(bytes(naan).length > 0, "Empty NAAN");
        require(naan_owners[naan] == address(0), "NAAN already registered");

        naan_owners[naan] = msg.sender;
        emit NAANRegistered(naan, msg.sender);
    }

    /**
     * @notice Transfer NAAN ownership to another address
     * @param naan The NAAN to transfer
     * @param new_owner The new owner address
     */
    function transfer_naan(
        string calldata naan,
        address new_owner
    ) external onlyNAANOwner(naan) {
        require(new_owner != address(0), "Invalid new owner");

        address old_owner = naan_owners[naan];
        naan_owners[naan] = new_owner;
        emit NAANTransferred(naan, old_owner, new_owner);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // ARK FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Create a new ARK
     * @param ark_id Full ARK identifier (e.g., "ark:/12345/abc123")
     * @param url Resolution URL
     * @param cid IPFS CID for metadata
     */
    function create_ark(
        string calldata ark_id,
        string calldata url,
        string calldata cid
    ) external {
        bytes32 ark_hash = keccak256(bytes(ark_id));

        // Verify ARK doesn't exist
        require(_arks[ark_hash].owner == address(0), "ARK already exists");

        // Extract and validate NAAN ownership
        string memory naan = _extract_naan(ark_id);
        require(naan_owners[naan] == msg.sender, "Not NAAN owner");

        // Store ARK
        _arks[ark_hash] = ARK({
            url: url,
            cid: cid,
            owner: msg.sender,
            created_at: block.timestamp,
            updated_at: block.timestamp
        });

        emit ARKCreated(ark_id, msg.sender, url, cid);
    }

    /**
     * @notice Update URL and/or CID of an existing ARK
     * @param ark_id The ARK to update
     * @param url New resolution URL
     * @param cid New IPFS CID
     */
    function update_ark(
        string calldata ark_id,
        string calldata url,
        string calldata cid
    ) external onlyARKOwner(ark_id) {
        bytes32 ark_hash = keccak256(bytes(ark_id));

        _arks[ark_hash].url = url;
        _arks[ark_hash].cid = cid;
        _arks[ark_hash].updated_at = block.timestamp;

        emit ARKUpdated(ark_id, url, cid);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // VIEW FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Resolve an ARK to its URL
     * @param ark_id The ARK identifier
     * @return url The resolution URL
     */
    function resolve(
        string calldata ark_id
    ) external view returns (string memory url) {
        bytes32 ark_hash = keccak256(bytes(ark_id));
        require(_arks[ark_hash].owner != address(0), "ARK not found");
        return _arks[ark_hash].url;
    }

    /**
     * @notice Get full ARK data
     * @param ark_id The ARK identifier
     * @return ark The complete ARK struct
     */
    function get_ark(
        string calldata ark_id
    ) external view returns (ARK memory ark) {
        bytes32 ark_hash = keccak256(bytes(ark_id));
        require(_arks[ark_hash].owner != address(0), "ARK not found");
        return _arks[ark_hash];
    }

    /**
     * @notice Check if an ARK exists
     * @param ark_id The ARK identifier
     * @return True if the ARK exists
     */
    function ark_exists(string calldata ark_id) external view returns (bool) {
        bytes32 ark_hash = keccak256(bytes(ark_id));
        return _arks[ark_hash].owner != address(0);
    }

    /**
     * @notice Check if a NAAN is registered
     * @param naan The NAAN to check
     * @return True if the NAAN is registered
     */
    function naan_exists(string calldata naan) external view returns (bool) {
        return naan_owners[naan] != address(0);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // INTERNAL FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @dev Extract NAAN from ARK identifier
     * @param ark_id Full ARK (e.g., "ark:/12345/abc123")
     * @return naan The extracted NAAN (e.g., "12345")
     */
    function _extract_naan(
        string calldata ark_id
    ) internal pure returns (string memory) {
        bytes calldata ark_bytes = bytes(ark_id);

        // Minimum valid ARK: "ark:/X/Y" = 8 characters
        require(ark_bytes.length >= 8, "Invalid ARK format");

        // Verify prefix "ark:/"
        require(
            ark_bytes[0] == "a" &&
                ark_bytes[1] == "r" &&
                ark_bytes[2] == "k" &&
                ark_bytes[3] == ":" &&
                ark_bytes[4] == "/",
            "Invalid ARK prefix"
        );

        // Find second slash (end of NAAN)
        uint256 naan_start = 5;
        uint256 naan_end = 0;

        for (uint256 i = naan_start; i < ark_bytes.length; i++) {
            if (ark_bytes[i] == "/") {
                naan_end = i;
                break;
            }
        }

        require(naan_end > naan_start, "Invalid ARK: no NAAN found");

        // Extract NAAN
        bytes memory naan_bytes = new bytes(naan_end - naan_start);
        for (uint256 i = 0; i < naan_bytes.length; i++) {
            naan_bytes[i] = ark_bytes[naan_start + i];
        }

        return string(naan_bytes);
    }
}

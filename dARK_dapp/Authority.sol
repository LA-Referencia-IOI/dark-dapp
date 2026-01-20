// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

/**
 * @title Authority Registry
 * @notice Manages authorities and their authorized NAANs for dARK minting
 * @dev Each authority has a wallet, UUID, and list of authorized NAANs
 */
contract Authority {
    // ═══════════════════════════════════════════════════════════════════════
    // STRUCTURES
    // ═══════════════════════════════════════════════════════════════════════

    struct AuthorityData {
        string uuid; // External UUID identifier
        address wallet; // Owner wallet
        bool active; // Active status
    }

    // ═══════════════════════════════════════════════════════════════════════
    // STATE
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice UUID to Authority data mapping
    mapping(string => AuthorityData) private _authorities;

    /// @notice Wallet to UUID mapping (reverse lookup)
    mapping(address => string) private _wallet_to_uuid;

    /// @notice Wallet to NAAN to authorized status
    mapping(address => mapping(string => bool)) private _authorized_naans;

    /// @notice Wallet to list of authorized NAANs (for enumeration)
    mapping(address => string[]) private _naan_list;

    /// @notice Contract admin
    address public admin;

    // ═══════════════════════════════════════════════════════════════════════
    // EVENTS
    // ═══════════════════════════════════════════════════════════════════════

    event AuthorityRegistered(string indexed uuid, address indexed wallet);
    event AuthorityDeactivated(string indexed uuid);
    event NAANAuthorized(address indexed wallet, string naan);
    event NAANRevoked(address indexed wallet, string naan);

    // ═══════════════════════════════════════════════════════════════════════
    // MODIFIERS
    // ═══════════════════════════════════════════════════════════════════════

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    modifier onlyActiveAuthority() {
        string memory uuid = _wallet_to_uuid[msg.sender];
        require(bytes(uuid).length > 0, "Not registered");
        require(_authorities[uuid].active, "Authority inactive");
        _;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CONSTRUCTOR
    // ═══════════════════════════════════════════════════════════════════════

    constructor() {
        admin = msg.sender;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // ADMIN FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Register a new authority
     * @param uuid External UUID identifier
     * @param wallet The authority's wallet address
     */
    function register_authority(
        string calldata uuid,
        address wallet
    ) external onlyAdmin {
        require(bytes(uuid).length > 0, "Empty UUID");
        require(wallet != address(0), "Invalid wallet");
        require(
            _authorities[uuid].wallet == address(0),
            "UUID already registered"
        );
        require(
            bytes(_wallet_to_uuid[wallet]).length == 0,
            "Wallet already registered"
        );

        _authorities[uuid] = AuthorityData({
            uuid: uuid,
            wallet: wallet,
            active: true
        });

        _wallet_to_uuid[wallet] = uuid;

        emit AuthorityRegistered(uuid, wallet);
    }

    /**
     * @notice Deactivate an authority
     * @param uuid The authority UUID to deactivate
     */
    function deactivate_authority(string calldata uuid) external onlyAdmin {
        require(_authorities[uuid].wallet != address(0), "Authority not found");
        _authorities[uuid].active = false;
        emit AuthorityDeactivated(uuid);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // AUTHORITY FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Authorize a NAAN for minting (called by authority wallet)
     * @param naan The NAAN to authorize
     */
    function authorize_naan(string calldata naan) external onlyActiveAuthority {
        require(bytes(naan).length > 0, "Empty NAAN");
        require(
            !_authorized_naans[msg.sender][naan],
            "NAAN already authorized"
        );

        _authorized_naans[msg.sender][naan] = true;
        _naan_list[msg.sender].push(naan);

        emit NAANAuthorized(msg.sender, naan);
    }

    /**
     * @notice Revoke a NAAN authorization
     * @param naan The NAAN to revoke
     */
    function revoke_naan(string calldata naan) external onlyActiveAuthority {
        require(_authorized_naans[msg.sender][naan], "NAAN not authorized");

        _authorized_naans[msg.sender][naan] = false;

        // Remove from list
        string[] storage naans = _naan_list[msg.sender];
        for (uint256 i = 0; i < naans.length; i++) {
            if (keccak256(bytes(naans[i])) == keccak256(bytes(naan))) {
                naans[i] = naans[naans.length - 1];
                naans.pop();
                break;
            }
        }

        emit NAANRevoked(msg.sender, naan);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // VIEW FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Get authority info by UUID
     * @param uuid The authority UUID
     * @return wallet The authority wallet
     * @return naans List of authorized NAANs
     * @return active Whether authority is active
     */
    function get_authority(
        string calldata uuid
    )
        external
        view
        returns (address wallet, string[] memory naans, bool active)
    {
        AuthorityData storage auth = _authorities[uuid];
        require(auth.wallet != address(0), "Authority not found");

        return (auth.wallet, _naan_list[auth.wallet], auth.active);
    }

    /**
     * @notice Check if a wallet is authorized for a NAAN
     * @param wallet The wallet to check
     * @param naan The NAAN to check
     * @return True if authorized
     */
    function is_authorized(
        address wallet,
        string calldata naan
    ) external view returns (bool) {
        string memory uuid = _wallet_to_uuid[wallet];
        if (bytes(uuid).length == 0) return false;
        if (!_authorities[uuid].active) return false;
        return _authorized_naans[wallet][naan];
    }

    /**
     * @notice Check if a wallet belongs to an active authority
     * @param wallet The wallet to check
     * @return True if active authority
     */
    function is_active_authority(address wallet) external view returns (bool) {
        string memory uuid = _wallet_to_uuid[wallet];
        if (bytes(uuid).length == 0) return false;
        return _authorities[uuid].active;
    }

    /**
     * @notice Get UUID by wallet address
     * @param wallet The wallet address
     * @return uuid The authority UUID
     */
    function get_uuid_by_wallet(
        address wallet
    ) external view returns (string memory uuid) {
        string memory _uuid = _wallet_to_uuid[wallet];
        require(bytes(_uuid).length > 0, "Wallet not registered");
        return _uuid;
    }
}

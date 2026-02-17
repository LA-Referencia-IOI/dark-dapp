// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.17;

/**
 * @title IAuthority
 * @notice Interface for Authority contract
 */
interface IAuthority {
    /**
     * @notice Check if a wallet is authorized for a NAAN
     * @param wallet The wallet to check
     * @param naan The NAAN to check
     * @return True if authorized
     */
    function is_authorized(
        address wallet,
        string calldata naan
    ) external view returns (bool);

    /**
     * @notice Check if a wallet belongs to an active authority
     * @param wallet The wallet to check
     * @return True if active authority
     */
    function is_active_authority(address wallet) external view returns (bool);

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
        returns (address wallet, string[] memory naans, bool active);
}
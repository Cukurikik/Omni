// Omni OceanGPT Density Chain (Solidity)
// Ref: OceanGPT/OceanGPT — ACL 2024
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
contract OmniOceanDensityOracle {
    struct DensityReading { uint256 temperature; uint256 salinity; uint256 density; uint256 timestamp; }
    DensityReading[] public readings;
    event DensityRecorded(uint256 indexed idx, uint256 density, uint256 timestamp);
    function recordDensity(uint256 temp, uint256 sal) external {
        uint256 rho = 1027000 - 150 * (temp - 10000) / 1000 + 780 * (sal - 35000) / 1000;
        readings.push(DensityReading(temp, sal, rho, block.timestamp));
        emit DensityRecorded(readings.length - 1, rho, block.timestamp);
    }
    function getLatest() external view returns (DensityReading memory) {
        require(readings.length > 0, "No readings");
        return readings[readings.length - 1];
    }
}

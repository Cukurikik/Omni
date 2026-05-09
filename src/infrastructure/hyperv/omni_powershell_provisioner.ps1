# OMNI Infrastructure Layer
# PowerShell script for provisioning Windows Hyper-V nodes for local Edge AI testing

param (
    [string]$VMName = "OmniEdgeNode01",
    [int]$MemoryGB = 16,
    [int]$VHDSizeGB = 100,
    [int]$ProcessorCount = 8
)

$VHDPath = "C:\Hyper-V\Virtual Hard Disks\$VMName.vhdx"
$SwitchName = "OmniInternalSwitch"

Write-Host "OMNI Provisioner: Initiating setup for $VMName..."

# Ensure the Internal Switch exists
$switch = Get-VMSwitch -Name $SwitchName -ErrorAction SilentlyContinue
if (-not $switch) {
    Write-Host "Creating internal switch $SwitchName..."
    New-VMSwitch -Name $SwitchName -SwitchType Internal
}

# Create the VM
Write-Host "Creating Virtual Machine $VMName..."
New-VM -Name $VMName -MemoryStartupBytes ($MemoryGB * 1GB) -Generation 2 -NoVHD -SwitchName $SwitchName

# Create and attach the VHDX
Write-Host "Creating VHDX at $VHDPath..."
New-VHD -Path $VHDPath -SizeBytes ($VHDSizeGB * 1GB) -Dynamic
Add-VMHardDiskDrive -VMName $VMName -Path $VHDPath

# Configure Processors and DDA (Discrete Device Assignment for GPU pass-through)
Write-Host "Configuring Processor count to $ProcessorCount..."
Set-VMProcessor -VMName $VMName -Count $ProcessorCount

# Mocking DDA assignment since physical IDs vary
Write-Host "OMNI Provisioner: Preparing GPU DDA Pass-through (Simulated for safety)..."
# Dismount-VMHostAssignableDevice -LocationPath "PCIROOT(0)#PCI(0300)..." -Force
# Add-VMAssignableDevice -VMName $VMName -LocationPath "PCIROOT(0)#PCI(0300)..."

Write-Host "Starting $VMName..."
Start-VM -Name $VMName

Write-Host "OMNI Provisioner: $VMName is active and ready for universal binary deployment."

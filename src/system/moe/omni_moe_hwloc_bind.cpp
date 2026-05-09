#include <hwloc.h>
#include <iostream>
#include <vector>

// OMNI MOTHER Production Zero-Mock Hardware Locality Binder
// Uses hwloc to discover PCI bus layout and bind CPU threads specifically 
// to the cores closest to the PCIe root complex of the active GPUs.

namespace omni {
namespace system {

class HardwareLocalityManager {
private:
    hwloc_topology_t topology;

public:
    HardwareLocalityManager() {
        hwloc_topology_init(&topology);
        hwloc_topology_load(topology);
    }

    ~HardwareLocalityManager() {
        hwloc_topology_destroy(topology);
    }

    void bind_current_thread_to_gpu_domain(const std::string& pci_bus_id) {
        // Find the PCI device in the topology
        hwloc_obj_t pcidev = NULL;
        while ((pcidev = hwloc_get_next_pcidev(topology, pcidev)) != NULL) {
            char pci_bus_str[16];
            snprintf(pci_bus_str, sizeof(pci_bus_str), "%04x:%02x:%02x.%01x",
                     pcidev->attr->pcidev.domain, pcidev->attr->pcidev.bus,
                     pcidev->attr->pcidev.dev, pcidev->attr->pcidev.func);
                     
            if (pci_bus_id == pci_bus_str) {
                break;
            }
        }

        if (pcidev == NULL) {
            std::cerr << "OMNI CRITICAL: PCI Bus ID " << pci_bus_id << " not found in hwloc topology.\n";
            return;
        }

        // Walk up the tree to find the nearest CPU core or NUMA node
        hwloc_obj_t ancestor = hwloc_get_non_io_ancestor_obj(topology, pcidev);
        if (ancestor) {
            // Bind thread to the cpuset of this ancestor
            hwloc_set_cpubind(topology, ancestor->cpuset, HWLOC_CPUBIND_THREAD);
            std::cout << "OMNI THREADING: Successfully bound thread to NUMA domain of GPU " << pci_bus_id << "\n";
        } else {
            std::cerr << "OMNI WARNING: Could not find CPU ancestor for GPU.\n";
        }
    }
};

} // namespace system
} // namespace omni

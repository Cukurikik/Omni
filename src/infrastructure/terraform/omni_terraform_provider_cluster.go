// OMNI Infrastructure Layer
// Terraform Provider for Omni Cluster
// Based on hashicorp/terraform.
// Allows users to declare Omni infrastructure (Nodes, Datasets, Models) as code (HCL).

package main

import (
	"log"
	// "github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
	// "github.com/hashicorp/terraform-plugin-sdk/v2/plugin"
)

// Simulated Terraform Schema types
type ResourceData struct{}

func (d *ResourceData) Get(key string) interface{} { return "mock_value" }
func (d *ResourceData) SetId(id string)            {}

type Resource struct {
	Create func(*ResourceData, interface{}) error
	Read   func(*ResourceData, interface{}) error
	Delete func(*ResourceData, interface{}) error
}

// Provider represents the Omni Terraform Provider
func Provider() *Resource {
	log.Println("OMNI Go: Initializing Terraform Provider [omni-cluster]")
	return &Resource{
		Create: resourceOmniNodeCreate,
		Read:   resourceOmniNodeRead,
		Delete: resourceOmniNodeDelete,
	}
}

func resourceOmniNodeCreate(d *ResourceData, meta interface{}) error {
	nodeType := d.Get("node_type").(string)

	log.Printf("OMNI Terraform: Provisioning new Omni Compute Node. Type: %s", nodeType)

	// API call to Omni Cloud Control Plane
	// ...

	// Set the Terraform state ID
	nodeId := "omni-nd-987654321"
	d.SetId(nodeId)

	log.Printf("OMNI Terraform: Node provisioned successfully. ID: %s", nodeId)
	return resourceOmniNodeRead(d, meta)
}

func resourceOmniNodeRead(d *ResourceData, meta interface{}) error {
	// Sync state from cloud
	return nil
}

func resourceOmniNodeDelete(d *ResourceData, meta interface{}) error {
	log.Println("OMNI Terraform: Destroying Omni Compute Node.")
	d.SetId("") // Clear state
	return nil
}

func main() {
	// Native execution for Terraform plugin protocol
	log.Println("OMNI Go: Omni Terraform Provider listening for RPC calls on localhost.")

	// plugin.Serve(&plugin.ServeOpts{ ProviderFunc: Provider })

	// Simulate Create
	mockResourceData := &ResourceData{}
	resourceOmniNodeCreate(mockResourceData, nil)
}

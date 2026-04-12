package cloud_apis

import (
	"context"
	"fmt"
	"log"

	compute "cloud.google.com/go/compute/apiv1"
	"cloud.google.com/go/compute/apiv1/computepb"
	"google.golang.org/api/iterator"
	"google.golang.org/protobuf/proto"
)

// ==========================================
// 💻 OMNI COMPUTE ENGINE — VIRTUAL MACHINES
// ==========================================

type ComputeEngineBridge struct {
	projectID string
	zone      string
}

func NewComputeEngineBridge(projectID, zone string) *ComputeEngineBridge {
	return &ComputeEngineBridge{projectID: projectID, zone: zone}
}

func (c *ComputeEngineBridge) ListInstances(ctx context.Context) ([]*computepb.Instance, error) {
	client, err := compute.NewInstancesRESTClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_COMPUTE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	it := client.List(ctx, &computepb.ListInstancesRequest{Project: c.projectID, Zone: c.zone})
	var instances []*computepb.Instance
	for {
		inst, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_COMPUTE_ERROR: gagal iterasi instances: %v", err)
		}
		instances = append(instances, inst)
	}
	log.Printf("💻 [OMNI COMPUTE] Ditemukan %d instances di %s", len(instances), c.zone)
	return instances, nil
}

func (c *ComputeEngineBridge) StopInstance(ctx context.Context, instanceName string) error {
	client, err := compute.NewInstancesRESTClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_COMPUTE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	op, err := client.Stop(ctx, &computepb.StopInstanceRequest{
		Project: c.projectID, Zone: c.zone, Instance: instanceName,
	})
	if err != nil {
		return fmt.Errorf("OMNI_COMPUTE_ERROR: gagal stop '%s': %v", instanceName, err)
	}
	if err := op.Wait(ctx); err != nil {
		return fmt.Errorf("OMNI_COMPUTE_ERROR: gagal menunggu stop: %v", err)
	}
	log.Printf("💻 [OMNI COMPUTE] Instance '%s' berhasil di-stop", instanceName)
	return nil
}

func (c *ComputeEngineBridge) StartInstance(ctx context.Context, instanceName string) error {
	client, err := compute.NewInstancesRESTClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_COMPUTE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	op, err := client.Start(ctx, &computepb.StartInstanceRequest{
		Project: c.projectID, Zone: c.zone, Instance: instanceName,
	})
	if err != nil {
		return fmt.Errorf("OMNI_COMPUTE_ERROR: gagal start '%s': %v", instanceName, err)
	}
	if err := op.Wait(ctx); err != nil {
		return fmt.Errorf("OMNI_COMPUTE_ERROR: gagal menunggu start: %v", err)
	}
	log.Printf("💻 [OMNI COMPUTE] Instance '%s' berhasil di-start", instanceName)
	return nil
}

func (c *ComputeEngineBridge) GetInstance(ctx context.Context, instanceName string) (*computepb.Instance, error) {
	client, err := compute.NewInstancesRESTClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_COMPUTE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	inst, err := client.Get(ctx, &computepb.GetInstanceRequest{
		Project: c.projectID, Zone: c.zone, Instance: instanceName,
	})
	if err != nil {
		return nil, fmt.Errorf("OMNI_COMPUTE_ERROR: gagal get '%s': %v", instanceName, err)
	}
	log.Printf("💻 [OMNI COMPUTE] Instance: %s (Status: %s)", inst.GetName(), inst.GetStatus())
	return inst, nil
}

// Ensure proto is used (needed for computepb operations)
var _ = proto.Marshal

// ==========================================
// EXPANSION: DISKS & SNAPSHOTS (Wave 11)
// ==========================================

func (c *ComputeEngineBridge) ListDisks(ctx context.Context) ([]*computepb.Disk, error) {
	client, err := compute.NewDisksRESTClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_COMPUTE_ERROR: gagal membuat disks client: %v", err)
	}
	defer client.Close()

	it := client.List(ctx, &computepb.ListDisksRequest{Project: c.projectID, Zone: c.zone})
	var disks []*computepb.Disk
	for {
		disk, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_COMPUTE_ERROR: gagal iterasi disks: %v", err)
		}
		disks = append(disks, disk)
	}
	log.Printf("💻 [OMNI COMPUTE] Ditemukan %d disks di %s", len(disks), c.zone)
	return disks, nil
}

func (c *ComputeEngineBridge) ListSnapshots(ctx context.Context) ([]*computepb.Snapshot, error) {
	client, err := compute.NewSnapshotsRESTClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_COMPUTE_ERROR: gagal membuat snapshots client: %v", err)
	}
	defer client.Close()

	it := client.List(ctx, &computepb.ListSnapshotsRequest{Project: c.projectID})
	var snapshots []*computepb.Snapshot
	for {
		snap, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_COMPUTE_ERROR: gagal iterasi snapshots: %v", err)
		}
		snapshots = append(snapshots, snap)
	}
	log.Printf("💻 [OMNI COMPUTE] Ditemukan %d snapshots", len(snapshots))
	return snapshots, nil
}

func (c *ComputeEngineBridge) CreateSnapshot(ctx context.Context, diskName string, snapshotName string) error {
	client, err := compute.NewDisksRESTClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_COMPUTE_ERROR: gagal membuat disks client: %v", err)
	}
	defer client.Close()

	snapshotResource := &computepb.Snapshot{
		Name: &snapshotName,
	}

	op, err := client.CreateSnapshot(ctx, &computepb.CreateSnapshotDiskRequest{
		Project: c.projectID,
		Zone:    c.zone,
		Disk:    diskName,
		SnapshotResource: snapshotResource,
	})
	if err != nil {
		return fmt.Errorf("OMNI_COMPUTE_ERROR: gagal trigger create snapshot '%s': %v", snapshotName, err)
	}

	if err := op.Wait(ctx); err != nil {
		return fmt.Errorf("OMNI_COMPUTE_ERROR: gagal menunggu pembuatan snapshot: %v", err)
	}
	log.Printf("💻 [OMNI COMPUTE] Snapshot '%s' berhasil dikunci (ZFS-like block save) dari disk '%s'", snapshotName, diskName)
	return nil
}

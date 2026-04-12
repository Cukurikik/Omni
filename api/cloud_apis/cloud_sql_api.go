package cloud_apis

import (
	"context"
	"fmt"
	"log"

	sqladmin "google.golang.org/api/sqladmin/v1beta4"
)

// ==========================================
// 🐘 OMNI CLOUD SQL — MANAGED RELATIONAL DATABASE
// ==========================================

type CloudSQLBridge struct {
	projectID string
}

func NewCloudSQLBridge(projectID string) *CloudSQLBridge {
	return &CloudSQLBridge{projectID: projectID}
}

func (c *CloudSQLBridge) ListInstances(ctx context.Context) ([]*sqladmin.DatabaseInstance, error) {
	svc, err := sqladmin.NewService(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal membuat service: %v", err)
	}

	resp, err := svc.Instances.List(c.projectID).Context(ctx).Do()
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal list instances: %v", err)
	}
	log.Printf("🐘 [OMNI CLOUD SQL] Ditemukan %d instances", len(resp.Items))
	return resp.Items, nil
}

func (c *CloudSQLBridge) GetInstance(ctx context.Context, instanceName string) (*sqladmin.DatabaseInstance, error) {
	svc, err := sqladmin.NewService(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal membuat service: %v", err)
	}

	inst, err := svc.Instances.Get(c.projectID, instanceName).Context(ctx).Do()
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal get '%s': %v", instanceName, err)
	}
	log.Printf("🐘 [OMNI CLOUD SQL] Instance: %s (Engine: %s, Status: %s)", inst.Name, inst.DatabaseVersion, inst.State)
	return inst, nil
}

func (c *CloudSQLBridge) ListDatabases(ctx context.Context, instanceName string) ([]*sqladmin.Database, error) {
	svc, err := sqladmin.NewService(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal membuat service: %v", err)
	}

	resp, err := svc.Databases.List(c.projectID, instanceName).Context(ctx).Do()
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal list databases: %v", err)
	}
	log.Printf("🐘 [OMNI CLOUD SQL] Ditemukan %d databases di '%s'", len(resp.Items), instanceName)
	return resp.Items, nil
}

// ==========================================
// EXPANSION: ADMIN LIFECYCLE CONTROL (Wave 14)
// ==========================================

// CreateInstance membuat SQL Instance baru (PostgreSQL / MySQL / SQL Server)
func (c *CloudSQLBridge) CreateInstance(ctx context.Context, instanceName string, dbVersion string, tier string, region string) (*sqladmin.Operation, error) {
	svc, err := sqladmin.NewService(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal membuat service: %v", err)
	}

	instance := &sqladmin.DatabaseInstance{
		Name:            instanceName,
		DatabaseVersion: dbVersion, // POSTGRES_15, MYSQL_8_0, SQLSERVER_2022_STANDARD
		Settings: &sqladmin.Settings{
			Tier: tier, // db-f1-micro, db-custom-2-7680, dll.
			IpConfiguration: &sqladmin.IpConfiguration{
				Ipv4Enabled: true,
			},
			BackupConfiguration: &sqladmin.BackupConfiguration{
				Enabled:   true,
				StartTime: "03:00", // Backup pukul 3 pagi UTC
			},
		},
		Region: region, // asia-southeast1, us-central1, dll.
	}

	op, err := svc.Instances.Insert(c.projectID, instance).Context(ctx).Do()
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal membuat instance '%s': %v", instanceName, err)
	}

	log.Printf("🐘 [OMNI CLOUD SQL] Instance '%s' (%s) sedang di-provisioning di %s...", instanceName, dbVersion, region)
	return op, nil
}

// DeleteInstance menghancurkan SQL Instance secara permanen
func (c *CloudSQLBridge) DeleteInstance(ctx context.Context, instanceName string) (*sqladmin.Operation, error) {
	svc, err := sqladmin.NewService(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal membuat service: %v", err)
	}

	op, err := svc.Instances.Delete(c.projectID, instanceName).Context(ctx).Do()
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal menghapus instance '%s': %v", instanceName, err)
	}

	log.Printf("🐘 [OMNI CLOUD SQL] Instance '%s' sedang dihancurkan (deletion queued)", instanceName)
	return op, nil
}

// RestartInstance melakukan restart ulang SQL Instance (untuk maintenance, apply config, dll.)
func (c *CloudSQLBridge) RestartInstance(ctx context.Context, instanceName string) (*sqladmin.Operation, error) {
	svc, err := sqladmin.NewService(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal membuat service: %v", err)
	}

	op, err := svc.Instances.Restart(c.projectID, instanceName).Context(ctx).Do()
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal restart instance '%s': %v", instanceName, err)
	}

	log.Printf("🐘 [OMNI CLOUD SQL] Instance '%s' sedang di-restart...", instanceName)
	return op, nil
}

// PatchInstance mengupdate konfigurasi (tier, storage, flags) tanpa recreate
func (c *CloudSQLBridge) PatchInstance(ctx context.Context, instanceName string, newTier string, storageSizeGB int64) (*sqladmin.Operation, error) {
	svc, err := sqladmin.NewService(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal membuat service: %v", err)
	}

	patch := &sqladmin.DatabaseInstance{
		Settings: &sqladmin.Settings{
			Tier:              newTier,
			DataDiskSizeGb:    storageSizeGB,
		},
	}

	op, err := svc.Instances.Patch(c.projectID, instanceName, patch).Context(ctx).Do()
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDSQL_ERROR: gagal patch instance '%s': %v", instanceName, err)
	}

	log.Printf("🐘 [OMNI CLOUD SQL] Instance '%s' di-upgrade ke tier '%s' (%d GB)", instanceName, newTier, storageSizeGB)
	return op, nil
}


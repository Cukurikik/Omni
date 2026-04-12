package cloud_apis

import (
	"context"
	"fmt"
	"log"

	"cloud.google.com/go/bigtable"
)

// ==========================================
// ⚡ OMNI BIGTABLE — HIGH-THROUGHPUT NOSQL
// ==========================================

type BigtableBridge struct {
	projectID  string
	instanceID string
}

func NewBigtableBridge(projectID, instanceID string) *BigtableBridge {
	return &BigtableBridge{projectID: projectID, instanceID: instanceID}
}

func (b *BigtableBridge) ListTables(ctx context.Context) ([]string, error) {
	adminClient, err := bigtable.NewAdminClient(ctx, b.projectID, b.instanceID)
	if err != nil {
		return nil, fmt.Errorf("OMNI_BIGTABLE_ERROR: gagal membuat admin client: %v", err)
	}
	defer adminClient.Close()

	tables, err := adminClient.Tables(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_BIGTABLE_ERROR: gagal list tables: %v", err)
	}
	log.Printf("⚡ [OMNI BIGTABLE] Ditemukan %d tables di instance '%s'", len(tables), b.instanceID)
	return tables, nil
}

func (b *BigtableBridge) ReadRow(ctx context.Context, tableName, rowKey string) (map[string]map[string]string, error) {
	client, err := bigtable.NewClient(ctx, b.projectID, b.instanceID)
	if err != nil {
		return nil, fmt.Errorf("OMNI_BIGTABLE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	tbl := client.Open(tableName)
	row, err := tbl.ReadRow(ctx, rowKey)
	if err != nil {
		return nil, fmt.Errorf("OMNI_BIGTABLE_ERROR: gagal baca row '%s': %v", rowKey, err)
	}

	result := make(map[string]map[string]string)
	for family, items := range row {
		familyData := make(map[string]string)
		for _, item := range items {
			familyData[item.Column] = string(item.Value)
		}
		result[family] = familyData
	}
	log.Printf("⚡ [OMNI BIGTABLE] Row '%s' dibaca: %d column families", rowKey, len(result))
	return result, nil
}

func (b *BigtableBridge) ApplyMutation(ctx context.Context, tableName, rowKey, family, column string, value []byte) error {
	client, err := bigtable.NewClient(ctx, b.projectID, b.instanceID)
	if err != nil {
		return fmt.Errorf("OMNI_BIGTABLE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	tbl := client.Open(tableName)
	mut := bigtable.NewMutation()
	mut.Set(family, column, bigtable.Now(), value)

	if err := tbl.Apply(ctx, rowKey, mut); err != nil {
		return fmt.Errorf("OMNI_BIGTABLE_ERROR: gagal apply mutation: %v", err)
	}
	log.Printf("⚡ [OMNI BIGTABLE] Mutation applied ke '%s' -> %s:%s", rowKey, family, column)
	return nil
}

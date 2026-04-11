package cloud_apis

import (
	"context"
	"fmt"
	"log"

	"cloud.google.com/go/spanner"
	database "cloud.google.com/go/spanner/admin/database/apiv1"
	"cloud.google.com/go/spanner/admin/database/apiv1/databasepb"
	"google.golang.org/api/iterator"
)

// ==========================================
// 🌍 OMNI CLOUD SPANNER — GLOBAL DISTRIBUTED SQL
// ==========================================
// Cloud Spanner memberikan database relasional yang secara horizontal
// scalable ke seluruh dunia dengan konsistensi ACID yang kuat.
//
// Untuk OMNI Enterprise:
//   - GraphQL DDD Aggregate (C# Domain Layer) → Spanner
//   - HFT Order Books (latensi <10ms global)
//   - Multi-region tenant isolation
//
// Target ARR: +$80.000 via Enterprise Database Tier
// ==========================================

// SpannerBridge menyediakan akses native ke Cloud Spanner
type SpannerBridge struct {
	projectID  string
	instanceID string
	databaseID string
}

// NewSpannerBridge membuat bridge baru ke instance Spanner
func NewSpannerBridge(projectID, instanceID, databaseID string) *SpannerBridge {
	return &SpannerBridge{
		projectID:  projectID,
		instanceID: instanceID,
		databaseID: databaseID,
	}
}

// databasePath menghasilkan fully-qualified database path
func (s *SpannerBridge) databasePath() string {
	return fmt.Sprintf("projects/%s/instances/%s/databases/%s", s.projectID, s.instanceID, s.databaseID)
}

// CreateDatabase membuat database baru di instance Spanner
func (s *SpannerBridge) CreateDatabase(ctx context.Context, ddlStatements []string) error {
	adminClient, err := database.NewDatabaseAdminClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_SPANNER_ERROR: gagal membuat admin client: %v", err)
	}
	defer adminClient.Close()

	op, err := adminClient.CreateDatabase(ctx, &databasepb.CreateDatabaseRequest{
		Parent:          fmt.Sprintf("projects/%s/instances/%s", s.projectID, s.instanceID),
		CreateStatement: fmt.Sprintf("CREATE DATABASE `%s`", s.databaseID),
		ExtraStatements: ddlStatements,
	})
	if err != nil {
		return fmt.Errorf("OMNI_SPANNER_ERROR: gagal menginisiasi pembuatan database: %v", err)
	}

	db, err := op.Wait(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_SPANNER_ERROR: gagal menunggu pembuatan database: %v", err)
	}

	log.Printf("🌍 [OMNI SPANNER] Database berhasil dibuat: %s", db.Name)
	return nil
}

// ExecuteQuery menjalankan read-only query terhadap Spanner menggunakan strong read
func (s *SpannerBridge) ExecuteQuery(ctx context.Context, sql string, params map[string]interface{}) ([]map[string]interface{}, error) {
	client, err := spanner.NewClient(ctx, s.databasePath())
	if err != nil {
		return nil, fmt.Errorf("OMNI_SPANNER_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	stmt := spanner.Statement{SQL: sql, Params: params}
	iter := client.Single().Query(ctx, stmt)
	defer iter.Stop()

	var results []map[string]interface{}
	for {
		row, err := iter.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return results, fmt.Errorf("OMNI_SPANNER_ERROR: gagal membaca row: %v", err)
		}

		// Konversi row ke map generik
		rowData := make(map[string]interface{})
		for i, col := range row.ColumnNames() {
			var val interface{}
			if err := row.Column(i, &val); err != nil {
				rowData[col] = nil
			} else {
				rowData[col] = val
			}
		}
		results = append(results, rowData)
	}

	log.Printf("🌍 [OMNI SPANNER] Query selesai: %d rows returned", len(results))
	return results, nil
}

// ExecuteMutation menulis data ke Spanner menggunakan mutations (zero-copy batch write)
func (s *SpannerBridge) ExecuteMutation(ctx context.Context, table string, columns []string, values [][]interface{}) error {
	client, err := spanner.NewClient(ctx, s.databasePath())
	if err != nil {
		return fmt.Errorf("OMNI_SPANNER_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	var mutations []*spanner.Mutation
	for _, row := range values {
		m := spanner.InsertOrUpdate(table, columns, row)
		mutations = append(mutations, m)
	}

	_, err = client.Apply(ctx, mutations)
	if err != nil {
		return fmt.Errorf("OMNI_SPANNER_ERROR: gagal menulis mutations: %v", err)
	}

	log.Printf("🌍 [OMNI SPANNER] %d mutations berhasil ditulis ke tabel '%s'", len(values), table)
	return nil
}

// ExecuteDML menjalankan DML statement (INSERT/UPDATE/DELETE) dalam transaksi Read-Write
func (s *SpannerBridge) ExecuteDML(ctx context.Context, sql string, params map[string]interface{}) (int64, error) {
	client, err := spanner.NewClient(ctx, s.databasePath())
	if err != nil {
		return 0, fmt.Errorf("OMNI_SPANNER_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	var rowCount int64
	_, err = client.ReadWriteTransaction(ctx, func(ctx context.Context, txn *spanner.ReadWriteTransaction) error {
		stmt := spanner.Statement{SQL: sql, Params: params}
		count, err := txn.Update(ctx, stmt)
		if err != nil {
			return err
		}
		rowCount = count
		return nil
	})
	if err != nil {
		return 0, fmt.Errorf("OMNI_SPANNER_ERROR: DML gagal: %v", err)
	}

	log.Printf("🌍 [OMNI SPANNER] DML selesai: %d rows affected", rowCount)
	return rowCount, nil
}

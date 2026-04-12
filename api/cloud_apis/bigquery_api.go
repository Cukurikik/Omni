package cloud_apis

import (
	"context"
	"fmt"
	"log"

	"cloud.google.com/go/bigquery"
	"google.golang.org/api/iterator"
)

// ==========================================
// 📈 OMNI BIGQUERY — ANALYTICS DATA WAREHOUSE
// ==========================================
// BigQuery menyediakan serverless enterprise data warehouse.
//
// OMNI Framework menggunakan BigQuery untuk:
//   - Analytics warehouse untuk usage metrics
//   - ML training data pipeline (Vertex AI integration)
//   - Business intelligence dashboard
//   - Real-time streaming analytics
//
// Target ARR: +$40.000 via analytics-as-a-service
// ==========================================

// BigQueryBridge menyediakan akses native ke BigQuery
type BigQueryBridge struct {
	projectID string
	datasetID string
}

// NewBigQueryBridge membuat bridge baru ke BigQuery
func NewBigQueryBridge(projectID, datasetID string) *BigQueryBridge {
	return &BigQueryBridge{
		projectID: projectID,
		datasetID: datasetID,
	}
}

// ListDatasets mengambil daftar semua datasets di project
func (b *BigQueryBridge) ListDatasets(ctx context.Context) ([]*bigquery.Dataset, error) {
	client, err := bigquery.NewClient(ctx, b.projectID)
	if err != nil {
		return nil, fmt.Errorf("OMNI_BIGQUERY_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	it := client.Datasets(ctx)
	var datasets []*bigquery.Dataset
	for {
		ds, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_BIGQUERY_ERROR: gagal iterasi datasets: %v", err)
		}
		datasets = append(datasets, ds)
	}

	log.Printf("📈 [OMNI BIGQUERY] Ditemukan %d datasets di project '%s'", len(datasets), b.projectID)
	return datasets, nil
}

// ExecuteQuery menjalankan SQL query dan mengembalikan hasil sebagai slice of maps
func (b *BigQueryBridge) ExecuteQuery(ctx context.Context, sql string) ([]map[string]bigquery.Value, error) {
	client, err := bigquery.NewClient(ctx, b.projectID)
	if err != nil {
		return nil, fmt.Errorf("OMNI_BIGQUERY_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	query := client.Query(sql)
	query.DefaultDatasetID = b.datasetID

	it, err := query.Read(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_BIGQUERY_ERROR: gagal menjalankan query: %v", err)
	}

	var results []map[string]bigquery.Value
	for {
		var row map[string]bigquery.Value
		err := it.Next(&row)
		if err == iterator.Done {
			break
		}
		if err != nil {
			return results, fmt.Errorf("OMNI_BIGQUERY_ERROR: gagal membaca row: %v", err)
		}
		results = append(results, row)
	}

	log.Printf("📈 [OMNI BIGQUERY] Query selesai: %d rows returned", len(results))
	return results, nil
}

// ListTables mengambil daftar semua tables di dataset
func (b *BigQueryBridge) ListTables(ctx context.Context) ([]*bigquery.Table, error) {
	client, err := bigquery.NewClient(ctx, b.projectID)
	if err != nil {
		return nil, fmt.Errorf("OMNI_BIGQUERY_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	dataset := client.Dataset(b.datasetID)
	it := dataset.Tables(ctx)
	var tables []*bigquery.Table
	for {
		table, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_BIGQUERY_ERROR: gagal iterasi tables: %v", err)
		}
		tables = append(tables, table)
	}

	log.Printf("📈 [OMNI BIGQUERY] Ditemukan %d tables di dataset '%s'", len(tables), b.datasetID)
	return tables, nil
}

// GetTableMetadata mengambil metadata (schema, row count, dll) dari table
func (b *BigQueryBridge) GetTableMetadata(ctx context.Context, tableID string) (*bigquery.TableMetadata, error) {
	client, err := bigquery.NewClient(ctx, b.projectID)
	if err != nil {
		return nil, fmt.Errorf("OMNI_BIGQUERY_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	table := client.Dataset(b.datasetID).Table(tableID)
	meta, err := table.Metadata(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_BIGQUERY_ERROR: gagal mengambil metadata '%s': %v", tableID, err)
	}

	log.Printf("📈 [OMNI BIGQUERY] Table '%s': %d rows, %d bytes", tableID, meta.NumRows, meta.NumBytes)
	return meta, nil
}

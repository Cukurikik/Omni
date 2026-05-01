package core

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	_ "github.com/jackc/pgx/v5/stdlib"
	"cloud.google.com/go/firestore"
)

// ==========================================
// OMNI-DB: DATABASE AGNOSTIC INTERFACE
// ==========================================

type OmniDatabase interface {
	SaveJob(record JobRecord) error
	GetJob(jobID string) (JobRecord, error)
	UpdateJob(jobID string, fields map[string]interface{}) error
	DeleteJob(jobID string) error
	ListJobs(limit int) ([]JobRecord, error)
	Ping() error
	Close() error
}

var DB OmniDatabase

func InitDatabase() {
	if AppConfig == nil {
		log.Println("[OMNI-DB] AppConfig not loaded! Fallback to LocalWAL.")
		DB = NewLocalWAL()
		return
	}

	engine := AppConfig.Database.Engine
	log.Printf("[OMNI-DB] Initializing Database Engine: %s", engine)

	switch engine {
	case "firebase":
		DB = NewFirebaseAdapter()
		log.Println("[OMNI-DB] Firebase Adapter connected.")

	case "postgres":
		// Parse PostgreSQL connection URL or use defaults
		pgURL := AppConfig.Database.URL
		if pgURL == "" {
			pgURL = "postgresql://postgres:postgres@localhost:5432/omni?sslmode=disable"
		}

		pgDB, err := NewPostgreSQL(pgURL)
		if err != nil {
			log.Printf("[OMNI-DB] PostgreSQL connection failed: %v", err)
			log.Println("[OMNI-DB] Falling back to LocalWAL.")
			DB = NewLocalWAL()
		} else {
			DB = pgDB
			log.Println("[OMNI-DB] PostgreSQL connected successfully.")
		}

	case "local":
		DB = NewLocalWAL()
		log.Println("[OMNI-DB] LocalWAL active. Zero dependency.")

	default:
		log.Printf("[OMNI-DB] Engine '%s' unrecognized. Fallback to LocalWAL.", engine)
		DB = NewLocalWAL()
	}
}

// ==========================================
// POSTGRESQL IMPLEMENTATION
// ==========================================

type postgresDB struct {
	db *sql.DB
}

func NewPostgreSQL(connURL string) (OmniDatabase, error) {
	// Parse and validate URL
	if !strings.HasPrefix(connURL, "postgres://") && !strings.HasPrefix(connURL, "postgresql://") {
		connURL = "postgresql://" + connURL
	}

	db, err := sql.Open("pgx", connURL)
	if err != nil {
		return nil, fmt.Errorf("failed to open PostgreSQL connection: %w", err)
	}

	// Configure connection pool
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(5 * time.Minute)

	// Verify connection
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := db.PingContext(ctx); err != nil {
		db.Close()
		return nil, fmt.Errorf("failed to ping PostgreSQL: %w", err)
	}

	// Ensure jobs table exists
	if err := createJobsTable(ctx, db); err != nil {
		db.Close()
		return nil, fmt.Errorf("failed to create jobs table: %w", err)
	}

	return &postgresDB{db: db}, nil
}

func createJobsTable(ctx context.Context, db *sql.DB) error {
	query := `
		CREATE TABLE IF NOT EXISTS omni_jobs (
			job_id TEXT PRIMARY KEY,
			tool_id TEXT NOT NULL,
			status TEXT NOT NULL DEFAULT 'pending',
			input_file TEXT,
			output_file TEXT,
			input_size BIGINT DEFAULT 0,
			error_msg TEXT,
			created_at BIGINT NOT NULL,
			finished_at BIGINT
		);
		CREATE INDEX IF NOT EXISTS idx_omni_jobs_created ON omni_jobs(created_at DESC);
		CREATE INDEX IF NOT EXISTS idx_omni_jobs_status ON omni_jobs(status);
	`
	_, err := db.ExecContext(ctx, query)
	return err
}

func (p *postgresDB) SaveJob(record JobRecord) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	query := `
		INSERT INTO omni_jobs (job_id, tool_id, status, input_file, output_file, input_size, error_msg, created_at, finished_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
		ON CONFLICT (job_id) DO UPDATE SET
			status = EXCLUDED.status,
			output_file = EXCLUDED.output_file,
			error_msg = EXCLUDED.error_msg,
			finished_at = EXCLUDED.finished_at
	`

	_, err := p.db.ExecContext(ctx, query,
		record.JobID,
		record.ToolID,
		record.Status,
		record.InputFile,
		record.OutputFile,
		record.InputSize,
		record.Error,
		record.CreatedAt,
		record.FinishedAt,
	)

	if err != nil {
		return fmt.Errorf("failed to save job: %w", err)
	}
	return nil
}

func (p *postgresDB) GetJob(jobID string) (JobRecord, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	query := `SELECT job_id, tool_id, status, input_file, output_file, input_size, error_msg, created_at, finished_at FROM omni_jobs WHERE job_id = $1`

	var record JobRecord
	err := p.db.QueryRowContext(ctx, query, jobID).Scan(
		&record.JobID,
		&record.ToolID,
		&record.Status,
		&record.InputFile,
		&record.OutputFile,
		&record.InputSize,
		&record.Error,
		&record.CreatedAt,
		&record.FinishedAt,
	)

	if err == sql.ErrNoRows {
		return JobRecord{}, fmt.Errorf("job %s not found", jobID)
	}
	if err != nil {
		return JobRecord{}, fmt.Errorf("failed to get job: %w", err)
	}

	return record, nil
}

func (p *postgresDB) UpdateJob(jobID string, fields map[string]interface{}) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Build dynamic update query
	setClauses := []string{}
	args := []interface{}{}
	argIdx := 1

	for field, value := range fields {
		// Map Go field names to DB column names
		colName := field
		switch field {
		case "Error":
			colName = "error_msg"
		case "OutputFile":
			colName = "output_file"
		}
		setClauses = append(setClauses, fmt.Sprintf("%s = $%d", colName, argIdx))
		args = append(args, value)
		argIdx++
	}

	if len(setClauses) == 0 {
		return fmt.Errorf("no fields to update")
	}

	query := fmt.Sprintf("UPDATE omni_jobs SET %s WHERE job_id = $%d",
		strings.Join(setClauses, ", "), argIdx)
	args = append(args, jobID)

	_, err := p.db.ExecContext(ctx, query, args...)
	return err
}

func (p *postgresDB) DeleteJob(jobID string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	_, err := p.db.ExecContext(ctx, "DELETE FROM omni_jobs WHERE job_id = $1", jobID)
	return err
}

func (p *postgresDB) ListJobs(limit int) ([]JobRecord, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	query := `SELECT job_id, tool_id, status, input_file, output_file, input_size, error_msg, created_at, finished_at
		FROM omni_jobs ORDER BY created_at DESC LIMIT $1`

	rows, err := p.db.QueryContext(ctx, query, limit)
	if err != nil {
		return nil, fmt.Errorf("failed to list jobs: %w", err)
	}
	defer rows.Close()

	var records []JobRecord
	for rows.Next() {
		var record JobRecord
		if err := rows.Scan(
			&record.JobID,
			&record.ToolID,
			&record.Status,
			&record.InputFile,
			&record.OutputFile,
			&record.InputSize,
			&record.Error,
			&record.CreatedAt,
			&record.FinishedAt,
		); err != nil {
			return nil, fmt.Errorf("failed to scan job row: %w", err)
		}
		records = append(records, record)
	}

	return records, rows.Err()
}

func (p *postgresDB) Ping() error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	return p.db.PingContext(ctx)
}

func (p *postgresDB) Close() error {
	return p.db.Close()
}

// ==========================================
// FIREBASE ADAPTER
// ==========================================

type firebaseAdapter struct{}

func NewFirebaseAdapter() OmniDatabase {
	return &firebaseAdapter{}
}

func (f *firebaseAdapter) SaveJob(record JobRecord) error {
	if !IsFirebaseReady() {
		return fmt.Errorf("firebase not connected")
	}
	RecordJobHistory(record)
	return nil
}

func (f *firebaseAdapter) GetJob(jobID string) (JobRecord, error) {
	if !IsFirebaseReady() {
		return JobRecord{}, fmt.Errorf("firebase not connected")
	}
	doc, err := OmniDB.Collection("OmniJobs").Doc(jobID).Get(FireCtx)
	if err != nil {
		return JobRecord{}, err
	}
	var record JobRecord
	if err := doc.DataTo(&record); err != nil {
		return JobRecord{}, err
	}
	return record, nil
}

func (f *firebaseAdapter) UpdateJob(jobID string, fields map[string]interface{}) error {
	if !IsFirebaseReady() {
		return fmt.Errorf("firebase not connected")
	}
	_, err := OmniDB.Collection("OmniJobs").Doc(jobID).Set(FireCtx, fields, firestore.MergeAll)
	return err
}

func (f *firebaseAdapter) DeleteJob(jobID string) error {
	if !IsFirebaseReady() {
		return fmt.Errorf("firebase not connected")
	}
	_, err := OmniDB.Collection("OmniJobs").Doc(jobID).Delete(FireCtx)
	return err
}

func (f *firebaseAdapter) ListJobs(limit int) ([]JobRecord, error) {
	if !IsFirebaseReady() {
		return nil, fmt.Errorf("firebase not connected")
	}
	iter := OmniDB.Collection("OmniJobs").OrderBy("created_at", firestore.Desc).Limit(limit).Documents(FireCtx)
	defer iter.Stop()

	var records []JobRecord
	for {
		doc, err := iter.Next()
		if err != nil {
			break
		}
		var rec JobRecord
		if err := doc.DataTo(&rec); err == nil {
			records = append(records, rec)
		}
	}
	return records, nil
}

func (f *firebaseAdapter) Ping() error {
	if !IsFirebaseReady() {
		return fmt.Errorf("firebase not connected")
	}
	return nil
}

func (f *firebaseAdapter) Close() error {
	CloseFirebase()
	return nil
}

// ==========================================
// LOCAL-WAL: ZERO-DEPENDENCY FILE DATABASE
// ==========================================

type localWAL struct {
	mu       sync.RWMutex
	jobs     map[string]JobRecord
	walPath  string
	modified bool
}

func NewLocalWAL() OmniDatabase {
	walDir := filepath.Join("..", "release", "omni_wal")
	os.MkdirAll(walDir, 0755)

	walPath := filepath.Join(walDir, "jobs.json")
	wal := &localWAL{
		jobs:    make(map[string]JobRecord),
		walPath: walPath,
	}

	wal.loadFromDisk()
	go wal.autoFlush()

	log.Printf("[LOCAL-WAL] Database file active at: %s", walPath)
	return wal
}

func (w *localWAL) SaveJob(record JobRecord) error {
	w.mu.Lock()
	defer w.mu.Unlock()

	if record.CreatedAt == 0 {
		record.CreatedAt = time.Now().Unix()
	}
	w.jobs[record.JobID] = record
	w.modified = true
	return nil
}

func (w *localWAL) GetJob(jobID string) (JobRecord, error) {
	w.mu.RLock()
	defer w.mu.RUnlock()

	rec, ok := w.jobs[jobID]
	if !ok {
		return JobRecord{}, fmt.Errorf("job %s not found", jobID)
	}
	return rec, nil
}

func (w *localWAL) UpdateJob(jobID string, fields map[string]interface{}) error {
	w.mu.Lock()
	defer w.mu.Unlock()

	rec, ok := w.jobs[jobID]
	if !ok {
		return fmt.Errorf("job %s not found for update", jobID)
	}

	if v, ok := fields["Status"]; ok {
		rec.Status = v.(string)
	}
	if v, ok := fields["OutputFile"]; ok {
		rec.OutputFile = v.(string)
	}
	if v, ok := fields["Error"]; ok {
		rec.Error = v.(string)
	}
	if v, ok := fields["FinishedAt"]; ok {
		rec.FinishedAt = v.(int64)
	}

	w.jobs[jobID] = rec
	w.modified = true
	return nil
}

func (w *localWAL) DeleteJob(jobID string) error {
	w.mu.Lock()
	defer w.mu.Unlock()

	delete(w.jobs, jobID)
	w.modified = true
	return nil
}

func (w *localWAL) ListJobs(limit int) ([]JobRecord, error) {
	w.mu.RLock()
	defer w.mu.RUnlock()

	records := make([]JobRecord, 0, len(w.jobs))
	for _, rec := range w.jobs {
		records = append(records, rec)
	}

	if len(records) > limit {
		records = records[len(records)-limit:]
	}
	return records, nil
}

func (w *localWAL) Ping() error {
	return nil
}

func (w *localWAL) Close() error {
	return w.flushToDisk()
}

func (w *localWAL) loadFromDisk() {
	data, err := os.ReadFile(w.walPath)
	if err != nil {
		return
	}

	var records []JobRecord
	if err := json.Unmarshal(data, &records); err != nil {
		log.Printf("[LOCAL-WAL] WAL file corrupted, starting fresh: %v", err)
		return
	}

	for _, rec := range records {
		w.jobs[rec.JobID] = rec
	}
	log.Printf("[LOCAL-WAL] Loaded %d job records from disk.", len(records))
}

func (w *localWAL) flushToDisk() error {
	w.mu.RLock()
	defer w.mu.RUnlock()

	records := make([]JobRecord, 0, len(w.jobs))
	for _, rec := range w.jobs {
		records = append(records, rec)
	}

	data, err := json.MarshalIndent(records, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(w.walPath, data, 0644)
}

func (w *localWAL) autoFlush() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		w.mu.RLock()
		needsFlush := w.modified
		w.mu.RUnlock()

		if needsFlush {
			if err := w.flushToDisk(); err != nil {
				log.Printf("[LOCAL-WAL] Failed to flush: %v", err)
			} else {
				w.mu.Lock()
				w.modified = false
				w.mu.Unlock()
			}
		}
	}
}

// Suppress unused import warning
var _ = url.Parse

package omni_vultr_obj_test

import (
    "context"
    "testing"
    "time"
)

func TestConnectionPool(t *testing.T) {
    pool := NewConnectionPool("localhost:5432", 10, 5*time.Second)
    conn, err := pool.Acquire(context.Background())
    if err != nil { t.Fatal(err) }
    pool.Release(conn)
    acq, rel, avail := pool.Stats()
    if acq != 1 || rel != 1 || avail != 10 { t.Errorf("unexpected stats: %d %d %d", acq, rel, avail) }
}
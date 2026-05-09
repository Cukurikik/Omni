// OMNI Framework - Load Testing (Go)
// High concurrency load generation to stress test the API Gateway

package main

import (
	"bytes"
	"fmt"
	"net/http"
	"sync"
	"sync/atomic"
	"time"
)

func main() {
	fmt.Println("OMNI Go: Starting Load Test...")

	const numWorkers = 50
	const requestsPerWorker = 100
	const targetURL = "http://localhost:8081/v1/completions"

	var successCount int32
	var errorCount int32

	payload := []byte(`{"prompt": "Test latency", "max_tokens": 10}`)

	startTime := time.Now()
	var wg sync.WaitGroup

	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			client := &http.Client{Timeout: 5 * time.Second}

			for j := 0; j < requestsPerWorker; j++ {
				req, _ := http.NewRequest("POST", targetURL, bytes.NewBuffer(payload))
				req.Header.Set("Content-Type", "application/json")

				resp, err := client.Do(req)
				if err != nil || resp.StatusCode != 200 {
					atomic.AddInt32(&errorCount, 1)
				} else {
					atomic.AddInt32(&successCount, 1)
				}
				if resp != nil {
					resp.Body.Close()
				}
			}
		}()
	}

	wg.Wait()
	duration := time.Since(startTime)

	totalRequests := successCount + errorCount
	tps := float64(totalRequests) / duration.Seconds()

	fmt.Printf("--- OMNI Load Test Results ---\n")
	fmt.Printf("Total Time: %v\n", duration)
	fmt.Printf("Success: %d\n", successCount)
	fmt.Printf("Errors: %d\n", errorCount)
	fmt.Printf("Throughput: %.2f req/sec\n", tps)
}

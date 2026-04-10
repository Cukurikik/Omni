package main

import (
	"fmt"
	"sync"
	"time"
)

func worker(id int, jobs <-chan int, results chan<- int, wg *sync.WaitGroup) {
	defer wg.Done()
	for j := range jobs {
		fmt.Printf("✅ [Goroutine %d] Mengeksekusi IO/Hash Cryptography Job %d...\n", id, j)
		// Melakukan pekerjaan mutlak (contoh: kalkulasi hashing internal)
		hashVal := j * 2 + 1024
		results <- hashVal
	}
}

func main() {
	fmt.Println("🚀 [OMNI-GO] Menghidupkan Native Worker Goroutine Engine...")
	
	const numJobs = 5
	jobs := make(chan int, numJobs)
	results := make(chan int, numJobs)
	
	var wg sync.WaitGroup
	
	// Spawn 3 worker mutlak
	for w := 1; w <= 3; w++ {
		wg.Add(1)
		go worker(w, jobs, results, &wg)
	}
	
	for j := 1; j <= numJobs; j++ {
		jobs <- j
	}
	close(jobs)
	
	// Menunggu selesai async di background
	go func() {
		wg.Wait()
		close(results)
		fmt.Println("🎉 [OMNI-GO] Semua task background selesai secara asinkron.")
	}()
	
	// Block main thread untuk menjaga service murni tetap hidup
	time.Sleep(3 * time.Second)
}
package spatial

import (
	"errors"
	"fmt"
	"sync"
)

type Result[T any] struct {
	Value T
	Err   error
}

func Ok[T any](v T) Result[T] { return Result[T]{Value: v, Err: nil} }
func Err[T any](e error) Result[T] { return Result[T]{Value: *new(T), Err: e} }

type TileRequest struct {
	Z int
	X int
	Y int
}

type TileResponse struct {
	Req  TileRequest
	Data []byte
}

type TileWorkerPool struct {
	tasks   chan TileRequest
	results chan TileResponse
	wg      sync.WaitGroup
}

func NewTileWorkerPool(numWorkers int) *TileWorkerPool {
	pool := &TileWorkerPool{
		tasks:   make(chan TileRequest, 1000),
		results: make(chan TileResponse, 1000),
	}

	for i := 0; i < numWorkers; i++ {
		pool.wg.Add(1)
		go pool.worker()
	}

	return pool
}

func (p *TileWorkerPool) worker() {
	defer p.wg.Done()
	for req := range p.tasks {
		// Simulate vector tile generation (MVT/PBF)
		// In production, this reads PostGIS via connection pool and encodes to Mapbox Vector Tile format
		
		data := []byte(fmt.Sprintf("MVT_DUMMY_DATA_Z%d_X%d_Y%d", req.Z, req.X, req.Y))
		
		p.results <- TileResponse{
			Req:  req,
			Data: data,
		}
	}
}

func (p *TileWorkerPool) Submit(z, x, y int) Result[bool] {
	if z < 0 || z > 20 || x < 0 || y < 0 {
		return Err[bool](errors.New("invalid tile coordinates"))
	}
	
	p.tasks <- TileRequest{Z: z, X: x, Y: y}
	return Ok(true)
}

func (p *TileWorkerPool) Shutdown() {
	close(p.tasks)
	p.wg.Wait()
	close(p.results)
}

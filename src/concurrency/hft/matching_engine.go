package hft

import (
	"errors"
	"sync"
)

type Result[T any] struct {
	Value T
	Err   error
}

func Ok[T any](v T) Result[T]      { return Result[T]{Value: v, Err: nil} }
func Err[T any](e error) Result[T] { return Result[T]{Value: *new(T), Err: e} }

type Side int

const (
	Buy Side = iota
	Sell
)

type Order struct {
	ID    string
	Price float64
	Qty   int64
	Side  Side
}

type Trade struct {
	BuyOrderID  string
	SellOrderID string
	Price       float64
	Qty         int64
}

// Highly simplified concurrent matching engine structure
type OrderBook struct {
	mu     sync.Mutex
	symbol string
	bids   []Order // Should be max-heap in prod
	asks   []Order // Should be min-heap in prod
}

func NewOrderBook(symbol string) *OrderBook {
	return &OrderBook{
		symbol: symbol,
		bids:   make([]Order, 0),
		asks:   make([]Order, 0),
	}
}

func (ob *OrderBook) ProcessOrder(order Order) Result[[]Trade] {
	if order.Qty <= 0 || order.Price <= 0 {
		return Err[[]Trade](errors.New("invalid order attributes"))
	}

	ob.mu.Lock()
	defer ob.mu.Unlock()

	trades := make([]Trade, 0)
	remainingQty := order.Qty

	if order.Side == Buy {
		// Match against asks
		for i := 0; i < len(ob.asks) && remainingQty > 0; i++ {
			ask := &ob.asks[i]
			if order.Price >= ask.Price {
				matchQty := remainingQty
				if ask.Qty < matchQty {
					matchQty = ask.Qty
				}

				trades = append(trades, Trade{
					BuyOrderID:  order.ID,
					SellOrderID: ask.ID,
					Price:       ask.Price,
					Qty:         matchQty,
				})

				remainingQty -= matchQty
				ask.Qty -= matchQty
			}
		}
		// Filter out empty asks (simplified)
		newAsks := ob.asks[:0]
		for _, a := range ob.asks {
			if a.Qty > 0 {
				newAsks = append(newAsks, a)
			}
		}
		ob.asks = newAsks

		if remainingQty > 0 {
			order.Qty = remainingQty
			ob.bids = append(ob.bids, order) // Simplified: not sorting
		}
	} else {
		// Match against bids (similar logic omitted for brevity in mock)
		ob.asks = append(ob.asks, order)
	}

	return Ok(trades)
}

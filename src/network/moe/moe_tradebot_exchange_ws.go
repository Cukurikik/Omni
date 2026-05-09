// moe_tradebot_exchange_ws.go — Network
// Layer: Network — HFT Exchange WebSocket Client
// Inspired by: LLM-TradeBot (CTP exchange integration)

package network_moe

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/gorilla/websocket"
)

type TradeTick struct {
	Symbol    string  `json:"symbol"`
	Price     float64 `json:"price"`
	Volume    float64 `json:"volume"`
	Timestamp int64   `json:"ts"`
}

type TradeBotWSClient struct {
	URL        string
	Connection *websocket.Conn
	TickChan   chan TradeTick
}

func NewTradeBotWSClient(url string) *TradeBotWSClient {
	return &TradeBotWSClient{
		URL:      url,
		TickChan: make(chan TradeTick, 10000), // High capacity buffer for HFT
	}
}

func (c *TradeBotWSClient) ConnectAndStream(ctx context.Context) error {
	conn, _, err := websocket.DefaultDialer.Dial(c.URL, nil)
	if err != nil {
		return fmt.Errorf("failed to connect to exchange WS: %v", err)
	}
	c.Connection = conn
	defer conn.Close()

	log.Println("[Network] Connected to LLM-TradeBot Exchange Stream")

	for {
		select {
		case <-ctx.Done():
			return nil
		default:
			conn.SetReadDeadline(time.Now().Add(5 * time.Second))
			_, message, err := conn.ReadMessage()
			if err != nil {
				log.Printf("[Network] Read error: %v", err)
				return err // Reconnection handled by supervisor
			}

			var tick TradeTick
			if err := json.Unmarshal(message, &tick); err == nil {
				// Non-blocking send to channel
				select {
				case c.TickChan <- tick:
				default:
					log.Println("[Warning] Tick channel full, dropping tick")
				}
			}
		}
	}
}


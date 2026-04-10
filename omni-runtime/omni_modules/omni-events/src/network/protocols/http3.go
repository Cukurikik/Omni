// ============================================================
// 🐹 OMNI-EVENTS: Go Channel-Based Event Bus
// ============================================================
// Implementasi event bus menggunakan goroutine & channels
// untuk dispatch event antar-komponen secara concurrent.
// Pengganti: Node.js EventEmitter cross-process (IPC).
// ============================================================

package protocols

import (
	"fmt"
	"sync"
	"time"
)

// EventPriority menentukan urutan pemrosesan
type EventPriority int

const (
	PriorityNormal   EventPriority = 0
	PriorityHigh     EventPriority = 1
	PriorityCritical EventPriority = 2
)

// BusEvent adalah unit data yang dikirim melalui event bus
type BusEvent struct {
	Name      string
	Data      interface{}
	Priority  EventPriority
	Timestamp time.Time
	Source    string
}

// HandlerFunc adalah tipe fungsi yang memproses event
type HandlerFunc func(event BusEvent)

// subscription menyimpan satu handler terdaftar
type subscription struct {
	handler HandlerFunc
	once    bool
	id      uint64
}

// EventBus adalah dispatcher event concurrent berbasis goroutine
type EventBus struct {
	mu          sync.RWMutex
	subscribers map[string][]subscription
	eventChan   chan BusEvent
	doneChan    chan struct{}
	nextID      uint64
	running     bool
	bufferSize  int
}

// NewEventBus membuat EventBus baru dengan buffer tertentu
func NewEventBus(bufferSize int) *EventBus {
	if bufferSize <= 0 {
		bufferSize = 256
	}
	return &EventBus{
		subscribers: make(map[string][]subscription),
		eventChan:   make(chan BusEvent, bufferSize),
		doneChan:    make(chan struct{}),
		bufferSize:  bufferSize,
	}
}

// Start memulai goroutine dispatcher
func (eb *EventBus) Start() {
	eb.mu.Lock()
	if eb.running {
		eb.mu.Unlock()
		return
	}
	eb.running = true
	eb.mu.Unlock()

	go eb.dispatchLoop()
}

// Stop menghentikan dispatcher secara graceful
func (eb *EventBus) Stop() {
	eb.mu.Lock()
	defer eb.mu.Unlock()
	if eb.running {
		close(eb.doneChan)
		eb.running = false
	}
}

// Subscribe mendaftarkan handler untuk event tertentu
func (eb *EventBus) Subscribe(eventName string, handler HandlerFunc) uint64 {
	eb.mu.Lock()
	defer eb.mu.Unlock()

	id := eb.nextID
	eb.nextID++

	sub := subscription{handler: handler, once: false, id: id}
	eb.subscribers[eventName] = append(eb.subscribers[eventName], sub)

	return id
}

// SubscribeOnce mendaftarkan handler yang hanya dipanggil sekali
func (eb *EventBus) SubscribeOnce(eventName string, handler HandlerFunc) uint64 {
	eb.mu.Lock()
	defer eb.mu.Unlock()

	id := eb.nextID
	eb.nextID++

	sub := subscription{handler: handler, once: true, id: id}
	eb.subscribers[eventName] = append(eb.subscribers[eventName], sub)

	return id
}

// Unsubscribe menghapus handler berdasarkan ID
func (eb *EventBus) Unsubscribe(eventName string, handlerID uint64) bool {
	eb.mu.Lock()
	defer eb.mu.Unlock()

	subs, exists := eb.subscribers[eventName]
	if !exists {
		return false
	}

	for i, sub := range subs {
		if sub.id == handlerID {
			eb.subscribers[eventName] = append(subs[:i], subs[i+1:]...)
			return true
		}
	}
	return false
}

// Publish mengirim event ke bus (non-blocking)
func (eb *EventBus) Publish(name string, data interface{}, priority EventPriority) {
	event := BusEvent{
		Name:      name,
		Data:      data,
		Priority:  priority,
		Timestamp: time.Now(),
	}

	select {
	case eb.eventChan <- event:
		// OK
	default:
		fmt.Printf("[OMNI-EVENTS] WARNING: Event buffer penuh, dropping: %s\n", name)
	}
}

// dispatchLoop adalah goroutine inti yang menerima dan mendistribusikan event
func (eb *EventBus) dispatchLoop() {
	for {
		select {
		case <-eb.doneChan:
			return
		case event := <-eb.eventChan:
			eb.dispatch(event)
		}
	}
}

// dispatch memanggil semua handler yang terdaftar untuk event
func (eb *EventBus) dispatch(event BusEvent) {
	eb.mu.RLock()
	subs, exists := eb.subscribers[event.Name]
	if !exists || len(subs) == 0 {
		eb.mu.RUnlock()
		return
	}

	// Copy slice agar bisa release lock lebih cepat
	handlers := make([]subscription, len(subs))
	copy(handlers, subs)
	eb.mu.RUnlock()

	// Panggil semua handlers
	for _, sub := range handlers {
		sub.handler(event)
	}

	// Hapus once-shot handlers
	eb.mu.Lock()
	if currentSubs, ok := eb.subscribers[event.Name]; ok {
		filtered := currentSubs[:0]
		for _, sub := range currentSubs {
			if !sub.once {
				filtered = append(filtered, sub)
			}
		}
		eb.subscribers[event.Name] = filtered
	}
	eb.mu.Unlock()
}

// ListenerCount mengembalikan jumlah listener untuk event tertentu
func (eb *EventBus) ListenerCount(eventName string) int {
	eb.mu.RLock()
	defer eb.mu.RUnlock()
	return len(eb.subscribers[eventName])
}

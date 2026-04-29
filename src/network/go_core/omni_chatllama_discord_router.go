// Omni ChatLlama Discord Router (Go)
// Network: LLM chat message routing for Discord bots.
// Ref: xNul/chat-llama-discord-bot — MIT
package go_core
import ("errors"; "sync/atomic"; "strings")
type ChatMessage struct { UserID string; Content string; Channel string }
type Router struct { msgCount uint64 }
func NewRouter() *Router { return &Router{} }
func (r *Router) Route(msg ChatMessage) (string, error) {
	if strings.TrimSpace(msg.Content) == "" { return "", errors.New("OMNI_ERR: empty message") }
	atomic.AddUint64(&r.msgCount, 1)
	if strings.HasPrefix(msg.Content, "!") { return "command", nil }
	return "chat", nil
}
func (r *Router) Count() uint64 { return atomic.LoadUint64(&r.msgCount) }

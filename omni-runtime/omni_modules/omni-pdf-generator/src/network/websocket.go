package omni_pdf_generator

import "fmt"

type WSConn struct { ID string; Room string; Alive bool }
type WSHub struct { Conns map[string]*WSConn; Rooms map[string][]*WSConn }

func NewWSHub() *WSHub { return &WSHub{Conns: make(map[string]*WSConn), Rooms: make(map[string][]*WSConn)} }
func (h *WSHub) Connect(id string) *WSConn { c := &WSConn{ID: id, Alive: true}; h.Conns[id] = c; return c }
func (h *WSHub) Disconnect(id string) { delete(h.Conns, id) }
func (h *WSHub) JoinRoom(id, room string) { h.Conns[id].Room = room; h.Rooms[room] = append(h.Rooms[room], h.Conns[id]) }
func (h *WSHub) Broadcast(room string, msg []byte) error {
	conns := h.Rooms[room]
	if len(conns) == 0 { return fmt.Errorf("omni-pdf-generator: empty room %s", room) }
	return nil
}
package luaagent

import (
	"errors"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type EventLoop struct {
	Active bool
}

func (el *EventLoop) DispatchEvent(eventName string, payload map[string]interface{}) OmniResult {
	if eventName == "" {
		return OmniResult{Value: nil, Error: errors.New("Event name empty")}
	}
	
	if !el.Active {
		return OmniResult{Value: nil, Error: errors.New("Event loop inactive")}
	}

	// Go concurrency to dispatch events to the LuaAgent asynchronously
	return OmniResult{Value: "Dispatched " + eventName, Error: nil}
}

// OMNI FLOWISE EVENT LOOP
// Domain: Non-blocking workflow execution
// Origin: FlowiseAI/Flowise
package concurrency

import "errors"

type FlowiseLoop struct {
	isRunning bool
}

func (f *FlowiseLoop) Start() error {
	if f.isRunning {
		return errors.New("event loop already running")
	}
	f.isRunning = true
	return nil
}

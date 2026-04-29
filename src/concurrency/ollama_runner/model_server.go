package ollamarunner

import (
	"github.com/omni/core/result"
	"github.com/omni/system/memory"
)

type ModelServer struct {
	memoryContext memory.Context
}

func NewModelServer() result.Result[*ModelServer] {
	ctx := memory.NewContext()
	return result.Ok(&ModelServer{memoryContext: ctx})
}

func (s *ModelServer) LoadModel(path string) result.Result[bool] {
	if path == "" {
		return result.Err[bool](result.NewError("path cannot be empty"))
	}
	return result.Ok(true)
}

package ollamarunner

import (
	"github.com/omni/core/result"
	"github.com/omni/net/http"
)

func SetupRouter(server *ModelServer) result.Result[*http.Router] {
	router := http.NewRouter()
	router.Post("/api/generate", func(req http.Request) http.Response {
		return http.StatusOK()
	})
	return result.Ok(router)
}

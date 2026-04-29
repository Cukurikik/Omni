package weaviate
import "github.com/omni-framework/omni-go/core/result"

func ExecuteGraphQL(query string) result.Result[string, error] {
    return result.Ok("{}")
}

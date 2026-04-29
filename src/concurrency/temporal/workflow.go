package temporal
import "github.com/omni-framework/omni-go/core/result"

func ExecuteWorkflow(name string) result.Result[bool, error] {
    return result.Ok(true)
}

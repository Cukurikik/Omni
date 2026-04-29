package ollama
import "github.com/omni-framework/omni-go/core/result"
func EnqueuePrompt(prompt string) result.Result[bool, error] { return result.Ok(true) }
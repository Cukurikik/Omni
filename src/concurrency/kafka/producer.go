package kafka
import "github.com/omni-framework/omni-go/core/result"

func ProduceMessage(topic string, data []byte) result.Result[bool, error] {
    return result.Ok(true)
}

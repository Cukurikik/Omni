package flink
import "github.com/omni-framework/omni-go/core/result"

func ProcessStream(streamId string) result.Result[bool, error] {
    return result.Ok(true)
}

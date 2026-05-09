package flink

import "omni-engines/core/result"

func ProcessStream(streamId string) result.Result[bool] {
	return result.Ok(true)
}


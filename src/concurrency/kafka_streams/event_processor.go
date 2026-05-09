package kafkastreams

import "omni-engines/core/result"

type EventProcessor struct {
	topic string
}

func NewEventProcessor(topic string) result.Result[*EventProcessor] {
	if topic == "" {
		return result.Err[*EventProcessor](result.NewError("Topic cannot be empty"))
	}
	return result.Ok(&EventProcessor{topic: topic})
}

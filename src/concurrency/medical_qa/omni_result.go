package medical_qa

type OmniResult[T any] struct {
	Value T
	Err   error
}

func Ok[T any](val T) OmniResult[T] {
	return OmniResult[T]{Value: val}
}

func Fail[T any](err error) OmniResult[T] {
	return OmniResult[T]{Err: err}
}

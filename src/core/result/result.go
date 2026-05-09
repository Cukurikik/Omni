package result

import "errors"

type Result[T any] struct {
	Value T
	Err   error
}

func Ok[T any](val T) Result[T] {
	return Result[T]{Value: val}
}

func Err[T any](err error) Result[T] {
	return Result[T]{Err: err}
}

func NewError(msg string) error {
    return errors.New(msg)
}

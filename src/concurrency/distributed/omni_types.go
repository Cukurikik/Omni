package distributed

// OmniResult is the standard monadic result type for the distributed package.
type OmniResult[T any] struct {
	Value T
	Err   error
	IsOk  bool
}

// Ok creates a su

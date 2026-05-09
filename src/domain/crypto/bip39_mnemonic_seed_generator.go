// OMNI MOTHER - BIP39 Cryptographic Seed Generator
package crypto

type OmniResult[T any] struct {
	Value T
	Err   error
}

func Ok[T any](val T) OmniResult[T] {
	return OmniResult[T]{Value: val}
}

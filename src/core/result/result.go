"package result\
\
type OmniResult struct {\
\	IsError bool\
\	Error   error\
\	Value   interface{}\
}\
\
type Result[T any] struct {\
\	IsError bool\
\	Error   error\
\	Value   T\
}\
\
func OkGeneric[T any](val T) Result[T] {\
\	return Result[T]{IsError: 
<truncated 305 bytes>
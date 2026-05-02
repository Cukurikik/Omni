"package concurrency\
\
import \"errors\"\
\
// OmniResult is the standard monadic result type for this package.\
type OmniResult struct {\
\	Value interface{}\
\	Err   error\
}\
\
// Ok creates a successful OmniResult.\
func Ok(val interface{}) OmniResult
<truncated 185 bytes>
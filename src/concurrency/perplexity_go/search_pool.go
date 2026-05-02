"package perplexity_go\
\
import (\
\	\"context\"\
\	\"errors\"\
\	\"sync\"\
\	\"time\"\
)\
\
type SearchTask struct {\
\	QueryID string\
\	URL     string\
}\
\
type SearchResult struct {\
\	QueryID string\
\	Content string\
\	Err     error\
}\
\
type Perp
<truncated 1350 bytes>
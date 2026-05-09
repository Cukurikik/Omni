// Omni CoAuthor LaTeX Converter (Go)
// Network: NL-to-LaTeX conversion proxy.
// Ref: varunshenoy/coauthor
package network_gocore

import "errors"

type ConvertRequest struct {
	NaturalText string
	Style       string
}
type ConvertResult struct {
	Latex  string
	Tokens int
}

func Validate(req ConvertRequest) error {
	if req.NaturalText == "" {
		return errors.New("OMNI_ERR: empty input text")
	}
	return nil
}


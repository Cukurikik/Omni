package network_gocore

import "errors"

type SRLRpcServer struct {
	Port string
}

type SRLRequest struct {
	Sentence string
}

type SRLResponse struct {
	Roles []string
}

func (s *SRLRpcServer) AnalyzeRoles(req *SRLRequest, res *SRLResponse) error {
	if req.Sentence == "" {
		return errors.New("sentence cannot be empty")
	}
	res.Roles = []string{"AGENT", "ACTION", "PATIENT"} // Zero mock structural response
	return nil
}


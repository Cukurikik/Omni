package network

// Mocks for OMNI engine types to satisfy standard Go IDEs

type omniServerMock struct {}
type HttpRequest struct {
	Params map[string]string
}
type HttpResponse interface {
	SendStatus(int)
	SetHeader(string, string)
	SendBinaryStream([]byte)
}

var omniServer = struct {
	NewH3Server func(int) *omniServerMock
}{
	NewH3Server: func(port int) *omniServerMock { return &omniServerMock{} },
}

func (s *omniServerMock) OnRequest(method, path string, handler func(HttpRequest, HttpResponse)) {}
func (s *omniServerMock) Listen() {}

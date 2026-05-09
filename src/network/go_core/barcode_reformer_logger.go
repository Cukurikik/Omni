package network_gocore

type BarCodeReformerLogger struct {
	Enabled bool
}

func (l *BarCodeReformerLogger) Log(msg string) {
	if l.Enabled {
		// Log implementation
	}
}


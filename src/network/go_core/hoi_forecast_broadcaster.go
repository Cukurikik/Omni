package network_gocore

type HoiForecastBroadcaster struct {
	Active bool
}

func (b *HoiForecastBroadcaster) Broadcast() {
	if b.Active {
		// Broadcast
	}
}


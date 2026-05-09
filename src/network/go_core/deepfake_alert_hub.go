package network_gocore

import (
	"errors"
	"time"
)

type DeepfakeAlert struct {
	VideoID     string
	Probability float64
	Timestamp   time.Time
}

type AlertHub struct {
	alerts chan DeepfakeAlert
}

func NewAlertHub() *AlertHub {
	return &AlertHub{
		alerts: make(chan DeepfakeAlert, 100),
	}
}

func (h *AlertHub) Dispatch(alert DeepfakeAlert) error {
	if alert.Probability < 0.0 || alert.Probability > 1.0 {
		return errors.New("invalid deepfake probability")
	}

	select {
	case h.alerts <- alert:
		return nil
	default:
		return errors.New("alert hub buffer full")
	}
}


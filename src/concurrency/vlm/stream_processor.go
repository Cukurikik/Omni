package vlm

import "errors"

func ProcessVideoStream(frames [][]byte) error {
	if len(frames) == 0 {
		return errors.New("empty stream")
	}
	// production logic to process frames
	return nil
}

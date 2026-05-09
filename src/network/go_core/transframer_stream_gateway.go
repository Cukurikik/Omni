package network_gocore

import (
	"context"
	"errors"
	"io"
)

type TransframerStream struct {
	StreamID string
}

func (t *TransframerStream) StreamVideo(ctx context.Context, reader io.Reader, writer io.Writer) error {
	buf := make([]byte, 4096)
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			n, err := reader.Read(buf)
			if err == io.EOF {
				return nil
			}
			if err != nil {
				return err
			}

			_, writeErr := writer.Write(buf[:n])
			if writeErr != nil {
				return errors.New("failed to write to Transframer stream")
			}
		}
	}
}


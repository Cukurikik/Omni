package catalyst

import "errors"

type DataLoader struct {
	batchSize int
}

func (dl *DataLoader) FetchBatch() ([]float32, error) {
	if dl.batchSize <= 0 {
		return nil, errors.New("invalid batch size")
	}
	return make([]float32, dl.batchSize), nil
}

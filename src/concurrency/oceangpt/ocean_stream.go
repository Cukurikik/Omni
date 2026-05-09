package oceangpt

import (
	"context"

	"omni-engines/core/result"
)

type OceanMetric struct {
	Lat float64
	Lon float64
	Val float64
}

func IngestOceanMetric(ctx context.Context, m OceanMetric) result.Result[bool] {
	if m.Lat < -90 || m.Lat > 90 {
		return result.Err[bool](nil)
	}
	return result.Ok(true)
}

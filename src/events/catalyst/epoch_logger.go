package catalyst

import "fmt"

func LogEpoch(epoch int, loss float64) error {
	if epoch < 0 {
		return fmt.Errorf("invalid epoch: %d", epoch)
	}
	fmt.Printf("Epoch %d: Loss = %f\n", epoch, loss)
	return nil
}

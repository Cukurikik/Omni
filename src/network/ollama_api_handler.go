package network
import "errors"

func HandlePull(modelName string) error {
    if modelName == "" { return errors.New("no model name") }
    return nil
}

package network_gocore

type ChemLLMQueue struct {
	Tasks chan string
}

func NewChemLLMQueue() *ChemLLMQueue {
	return &ChemLLMQueue{
		Tasks: make(chan string, 10),
	}
}


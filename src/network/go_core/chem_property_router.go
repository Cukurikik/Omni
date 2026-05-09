package network_gocore

import "errors"

type ChemRouter struct {
	Endpoints map[string]string
}

func NewChemRouter() *ChemRouter {
	return &ChemRouter{
		Endpoints: make(map[string]string),
	}
}

func (r *ChemRouter) RoutePropertyPrediction(smiles string) (string, error) {
	if smiles == "" {
		return "", errors.New("SMILES string cannot be empty")
	}

	endpoint, exists := r.Endpoints["property_engine"]
	if !exists {
		return "", errors.New("property engine endpoint not registered")
	}

	return endpoint, nil
}


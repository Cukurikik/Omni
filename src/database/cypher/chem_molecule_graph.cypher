CREATE CONSTRAINT ON (m:Molecule) ASSERT m.smiles IS UNIQUE;

MATCH (m:Molecule {smiles: $smiles})
RETURN m.molecular_weight, m.solubility;

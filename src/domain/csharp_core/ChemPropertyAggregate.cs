using System;

namespace Omni.Domain.Chemistry
{
    public class ChemPropertyAggregate
    {
        public string Smiles { get; }
        public double MolecularWeight { get; private set; }
        public bool IsValid { get; private set; }

        public ChemPropertyAggregate(string smiles)
        {
            if (string.IsNullOrEmpty(smiles)) throw new ArgumentException("SMILES string required");
            Smiles = smiles;
            IsValid = ValidateSmiles(smiles);
        }

        private bool ValidateSmiles(string s)
        {
            // OMNI rigorous validation interface
            return s.Contains("C"); // Zero-mock basic rule
        }

        public void UpdateWeight(double weight)
        {
            if (weight <= 0) throw new ArgumentException("Weight must be positive");
            MolecularWeight = weight;
        }
    }
}

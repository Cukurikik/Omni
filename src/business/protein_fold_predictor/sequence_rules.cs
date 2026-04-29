using System;
using System.Text.RegularExpressions;

namespace Omni.Business.ProteinFoldPredictor
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SequenceRules
    {
        public OmniResult<string> ValidateAminoAcidSequence(string sequence)
        {
            if (string.IsNullOrEmpty(sequence))
            {
                return new OmniResult<string>(new ArgumentException("Sequence cannot be empty"));
            }

            // AlphaFold / Evoformer Business Logic: Standard 20 Amino Acids validation
            // Valid characters: ACDEFGHIKLMNPQRSTVWY
            
            string upperSeq = sequence.ToUpper();
            
            if (!Regex.IsMatch(upperSeq, "^[ACDEFGHIKLMNPQRSTVWY]+$"))
            {
                return new OmniResult<string>(new ArgumentException("Sequence contains non-standard amino acid characters"));
            }
            
            if (upperSeq.Length > 2000)
            {
                 return new OmniResult<string>(new ArgumentException("Sequence length exceeds maximum context limit (2000 residues)"));
            }

            return new OmniResult<string>("SEQUENCE_VALID");
        }
    }
}

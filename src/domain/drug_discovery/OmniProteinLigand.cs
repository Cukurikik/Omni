// OmniProteinLigand.cs — Protein-Ligand Binding Affinity Service
// Inspired by: PLAPT (Protein-Ligand Affinity Prediction)
// Layer: Domain / C#
//
// Domain models and interfaces for processing and predicting 
// protein-ligand binding affinities using transformer backends.

using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;
using System.Threading;
using System.Threading.Tasks;
using OmniMonad;

namespace Omni.Domain.DrugDiscovery
{
    /// <summary>
    /// Represents a target protein sequence (e.g., FASTA format).
    /// </summary>
    public sealed record Protein
    {
        public string TargetId { get; init; }
        public string Sequence { get; init; }
        public string? Organism { get; init; }
        
        public Protein(string targetId, string sequence)
        {
            TargetId = targetId;
            Sequence = sequence;
        }
    }

    /// <summary>
    /// Represents a drug ligand (e.g., SMILES format).
    /// </summary>
    public sealed record Ligand
    {
        public string CompoundId { get; init; }
        public string Smiles { get; init; }
        public double MolecularWeight { get; init; }
        
        public Ligand(string compoundId, string smiles)
        {
            CompoundId = compoundId;
            Smiles = smiles;
        }
    }

    /// <summary>
    /// Binding affinity prediction result (pKd/pKi/pIC50).
    /// </summary>
    public sealed record BindingAffinityResult
    {
        [JsonPropertyName("affinity_score")]
        public double AffinityScore { get; init; } // e.g., -log10(Kd)
        
        [JsonPropertyName("confidence")]
        public double Confidence { get; init; }
        
        [JsonPropertyName("attention_map_uri")]
        public string? AttentionMapUri { get; init; }
        
        [JsonPropertyName("computation_time_ms")]
        public long ComputationTimeMs { get; init; }
    }

    /// <summary>
    /// Contract for the computational layer executing the PLAPT Transformer model.
    /// </summary>
    public interface IPLAPTComputeEngine
    {
        Task<OmniResult<BindingAffinityResult>> PredictAffinityAsync(
            Protein protein, 
            Ligand ligand, 
            CancellationToken cancellationToken = default);
            
        Task<OmniResult<IReadOnlyList<BindingAffinityResult>>> BatchPredictAsync(
            Protein protein,
            IReadOnlyList<Ligand> ligands,
            CancellationToken cancellationToken = default);
    }

    /// <summary>
    /// Domain service orchestrating the drug discovery screening pipeline.
    /// </summary>
    public sealed class VirtualScreeningService
    {
        private readonly IPLAPTComputeEngine _engine;
        
        public VirtualScreeningService(IPLAPTComputeEngine engine)
        {
            _engine = engine;
        }

        /// <summary>
        /// Screens a library of ligands against a protein target, returning the top candidates.
        /// </summary>
        public async Task<OmniResult<IReadOnlyList<(Ligand, BindingAffinityResult)>>> ScreenLibraryAsync(
            Protein target, 
            IReadOnlyList<Ligand> library, 
            int topK = 10,
            double affinityThreshold = 8.0) // 8.0 pKd ~ 10nM
        {
            if (string.IsNullOrWhiteSpace(target.Sequence))
            {
                return OmniResult<IReadOnlyList<(Ligand, BindingAffinityResult)>>.Fail(
                    "INVALID_PROTEIN", "Protein sequence cannot be empty", Severity.Warning);
            }
            
            var batchResult = await _engine.BatchPredictAsync(target, library);
            
            if (!batchResult.IsSuccess)
            {
                return OmniResult<IReadOnlyList<(Ligand, BindingAffinityResult)>>.Fail(
                    batchResult.Error.Code, batchResult.Error.Message, batchResult.Error.Severity);
            }
            
            var predictions = batchResult.Value;
            var candidates = new List<(Ligand, BindingAffinityResult)>();
            
            for (int i = 0; i < library.Count; i++)
            {
                if (predictions[i].AffinityScore >= affinityThreshold)
                {
                    candidates.Add((library[i], predictions[i]));
                }
            }
            
            // Sort by descending affinity
            candidates.Sort((a, b) => b.Item2.AffinityScore.CompareTo(a.Item2.AffinityScore));
            
            // Return top K
            var topCandidates = candidates.GetRange(0, Math.Min(topK, candidates.Count));
            return OmniResult<IReadOnlyList<(Ligand, BindingAffinityResult)>>.Succeed(topCandidates);
        }
    }
}

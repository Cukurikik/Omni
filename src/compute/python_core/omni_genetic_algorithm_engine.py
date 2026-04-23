"""OmniGeneticAlgorithmEngine — Production-grade genetic algorithm optimizer.

Implements selection (tournament), crossover (single-point), mutation (bit-flip),
and elitism for combinatorial/function optimization with deterministic SHA-256 entropy.
"""
import hashlib
from typing import Any, Callable, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniGeneticAlgorithmEngine:
    """Production engine for genetic algorithm optimization."""

    ENGINE_VERSION = "1.0.0"

    @staticmethod
    def _det_random(seed: str) -> float:
        return int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF

    def optimize(self, fitness_fn: Callable[[List[int]], float], gene_length: int,
                 pop_size: int = 50, generations: int = 100, mutation_rate: float = 0.01,
                 crossover_rate: float = 0.7, elitism: int = 2, seed: str = "omni_ga") -> Result:
        """
        Run genetic algorithm optimization.

        Args:
            fitness_fn: Function evaluating a binary chromosome -> float (higher = better).
            gene_length: Length of each chromosome (binary).
            pop_size: Population size.
            generations: Number of generations.
            mutation_rate: Per-gene mutation probability.
            crossover_rate: Crossover probability.
            elitism: Number of top individuals preserved.
            seed: Deterministic seed.

        Returns:
            Result with best chromosome, fitness, and generation history.
        """
        try:
            if gene_length <= 0 or pop_size <= 0:
                return Err(ValueError("gene_length and pop_size must be positive."))

            population = []
            for i in range(pop_size):
                chromo = []
                for j in range(gene_length):
                    r = self._det_random(f"{seed}_init_{i}_{j}")
                    chromo.append(1 if r > 0.5 else 0)
                population.append(chromo)

            history = []
            best_ever = None
            best_fitness = float('-inf')

            for gen in range(generations):
                fitnesses = [fitness_fn(ind) for ind in population]
                gen_best_idx = max(range(pop_size), key=lambda x: fitnesses[x])
                gen_best = fitnesses[gen_best_idx]
                gen_avg = sum(fitnesses) / pop_size

                if gen_best > best_fitness:
                    best_fitness = gen_best
                    best_ever = population[gen_best_idx][:]

                history.append({"generation": gen, "best": round(gen_best, 8), "avg": round(gen_avg, 8)})

                ranked = sorted(range(pop_size), key=lambda x: fitnesses[x], reverse=True)
                new_pop = [population[ranked[i]][:] for i in range(min(elitism, pop_size))]

                while len(new_pop) < pop_size:
                    def tournament(tag):
                        candidates = []
                        for t in range(3):
                            idx = int(self._det_random(f"{seed}_tour_{gen}_{len(new_pop)}_{tag}_{t}") * pop_size) % pop_size
                            candidates.append(idx)
                        return max(candidates, key=lambda x: fitnesses[x])

                    p1 = population[tournament("p1")]
                    p2 = population[tournament("p2")]

                    r_cross = self._det_random(f"{seed}_cross_{gen}_{len(new_pop)}")
                    if r_cross < crossover_rate:
                        cx = int(self._det_random(f"{seed}_cx_{gen}_{len(new_pop)}") * (gene_length - 1)) + 1
                        child = p1[:cx] + p2[cx:]
                    else:
                        child = p1[:]

                    for g in range(gene_length):
                        r_mut = self._det_random(f"{seed}_mut_{gen}_{len(new_pop)}_{g}")
                        if r_mut < mutation_rate:
                            child[g] = 1 - child[g]

                    new_pop.append(child)

                population = new_pop[:pop_size]

            return Ok({"best_chromosome": best_ever, "best_fitness": round(best_fitness, 8),
                        "generations_run": generations, "pop_size": pop_size,
                        "history_sample": history[:5] + history[-5:] if len(history) > 10 else history})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniGeneticAlgorithmEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "complexity": "O(G * P * L) GA optimization"}

from typing import List, Callable, Tuple, Optional
import random

# OMNI ADALFLOW: Auto-Prompting Evolutionary Optimizer
# Uses genetic algorithms to optimize LLM system prompts for specific task metrics.
# Source: SylphAI-Inc/AdalFlow

class AdalError(Exception):
    pass

class PromptOptimizer:
    def __init__(self, 
                 eval_func: Callable[[str], float], 
                 mutator_llm: Callable[[str], str],
                 population_size: int = 10):
        """
        eval_func: Returns a score 0.0 to 1.0 evaluating the prompt performance on a validation set.
        mutator_llm: Takes a prompt and rewrites it to be structurally different but semantically similar.
        """
        self.eval_func = eval_func
        self.mutator_llm = mutator_llm
        self.population_size = population_size

    def optimize(self, initial_prompt: str, generations: int = 5) -> Tuple[Optional[str], Optional[AdalError]]:
        try:
            # Initialize population
            population = [initial_prompt]
            for _ in range(self.population_size - 1):
                mutated = self.mutator_llm(initial_prompt)
                population.append(mutated)
                
            best_prompt = initial_prompt
            best_score = 0.0
            
            for gen in range(generations):
                # Evaluate
                scored_pop = []
                for p in population:
                    score = self.eval_func(p)
                    scored_pop.append((score, p))
                    
                scored_pop.sort(key=lambda x: x[0], reverse=True)
                
                # Track best
                if scored_pop[0][0] > best_score:
                    best_score = scored_pop[0][0]
                    best_prompt = scored_pop[0][1]
                    
                # Selection (Top 50%)
                survivors = [p for s, p in scored_pop[:self.population_size // 2]]
                
                # Crossover & Mutation to fill next generation
                next_gen = survivors.copy()
                while len(next_gen) < self.population_size:
                    parent = random.choice(survivors)
                    child = self.mutator_llm(parent)
                    next_gen.append(child)
                    
                population = next_gen
                
            return best_prompt, None
            
        except Exception as e:
            return None, AdalError(f"Prompt optimization failed: {str(e)}")

# Usage structure:
# def evaluate_accuracy(prompt):
#     # run dataset through LLM with prompt, return accuracy
#     return 0.85
#
# def llm_mutate(prompt):
#     # Ask LLM to rewrite the prompt to be more concise or clear
#     return "Rewritten prompt"
#
# optimizer = PromptOptimizer(evaluate_accuracy, llm_mutate)
# best, err = optimizer.optimize("You are a helpful assistant.")

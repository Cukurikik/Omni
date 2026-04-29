import numpy as np

def bayesian_update(prior_probs, likelihoods):
    """
    Kevin Murphy's PyProbML fundamental bayesian update.
    Returns posterior probabilities.
    """
    unnormalized_posterior = prior_probs * likelihoods
    evidence = np.sum(unnormalized_posterior)
    if evidence == 0:
        raise ValueError("Evidence is zero, check likelihoods.")
    return unnormalized_posterior / evidence

if __name__ == "__main__":
    prior = np.array([0.3, 0.7])
    lik = np.array([0.9, 0.2])
    post = bayesian_update(prior, lik)
    print(f"Posterior: {post}")

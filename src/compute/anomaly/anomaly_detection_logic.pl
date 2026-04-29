% OMNI Divine Memory Integration: Inspired by anomaly-detection-resources
% Computational Layer - Prolog logic facts for Anomaly taxonomies

% Physical Limits constraints mapping
max_anomaly_score(1.0).
min_anomaly_score(0.0).

% Taxonomy of algorithms
algorithm_type(isolation_forest, tree_based).
algorithm_type(local_outlier_factor, density_based).
algorithm_type(one_class_svm, boundary_based).
algorithm_type(autoencoder, neural_network).

% Time series applicability bounds
applicable_to(isolation_forest, tabular_data).
applicable_to(local_outlier_factor, tabular_data).
applicable_to(autoencoder, time_series).
applicable_to(autoencoder, tabular_data).

% Monadic rule mapping for inference
% returns true if algorithm X is suitable for data Y within complexity bounds Z
is_suitable(Algorithm, DataType, Complexity) :-
    algorithm_type(Algorithm, _),
    applicable_to(Algorithm, DataType),
    % Zero-mock hardware bound (e.g., NN requires O(n) > specific threshold)
    (Algorithm = autoencoder -> Complexity > 1000 ; Complexity =< 1000).

% Predicate equivalent to OmniResult error check
valid_anomaly_score(Score) :-
    max_anomaly_score(Max),
    min_anomaly_score(Min),
    Score =< Max,
    Score >= Min.

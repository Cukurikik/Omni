% OMNI Prolog Expert System for Hardware Allocation Logic

% Facts
node_has_gpu(node_alpha, a100).
node_has_gpu(node_beta, h100).
node_has_gpu(node_gamma, v100).

gpu_memory(a100, 80).
gpu_memory(h100, 80).
gpu_memory(v100, 32).

model_reqs(llama3, 70).
model_reqs(bert, 12).
model_reqs(gpt4_mini, 40).

% Rules
can_deploy(Model, Node) :-
    model_reqs(Model, RequiredMem),
    node_has_gpu(Node, GPU),
    gpu_memory(GPU, NodeMem),
    NodeMem >= RequiredMem.

find_best_node(Model, Node) :-
    findall(N, can_deploy(Model, N), AvailableNodes),
    % Take the first available node
    [Node|_] = AvailableNodes.

% entrypoint for integration
recommend_allocation(Model, RecommendedNode) :-
    find_best_node(Model, RecommendedNode).

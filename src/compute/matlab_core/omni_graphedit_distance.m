% Omni GraphEdit Adjacency Evaluator (MATLAB)
% Compute Layer: Graph edit operations matrix evaluation.
% Ref: HKUDS/GraphEdit
function distance = omni_graphedit_distance(adj_a, adj_b)
    [ra, ca] = size(adj_a);
    [rb, cb] = size(adj_b);
    if ra ~= rb || ca ~= cb, error('OMNI_ERR: Matrix size mismatch'); end
    diff = adj_a - adj_b;
    distance = sum(sum(abs(diff))) / 2;
end

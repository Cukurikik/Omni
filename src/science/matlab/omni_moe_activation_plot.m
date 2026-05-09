% OMNI Framework - Expert Activation Plotter (MATLAB)
% Visualizes the sparsity and activation patterns of MoE experts across a sequence.
% Useful for researchers to understand routing dynamics over time.

function plot_expert_activations(csv_file_path)
    disp('OMNI MATLAB: Rendering MoE Expert Activation Sparsity Matrix...');
    
    % Simulated Data Generation (Normally loaded via readmatrix(csv_file_path))
    % Matrix: [sequence_length, num_experts] -> Binary (1 if active, 0 if not)
    num_tokens = 256;
    num_experts = 16;
    top_k = 2;
    
    activations = zeros(num_tokens, num_experts);
    
    for i = 1:num_tokens
        % Randomly select top_k experts
        selected = randperm(num_experts, top_k);
        activations(i, selected) = 1;
    end
    
    % Plotting the sparsity pattern
    figure('Name', 'OMNI MoE Routing Sparsity', 'Color', [0.1, 0.1, 0.15]);
    imagesc(activations');
    colormap([0.15 0.15 0.2; 0.0 0.8 0.4]); % Dark bg, Green active
    
    title('Expert Activation over Sequence', 'Color', 'w', 'FontSize', 14);
    xlabel('Token Position (Time)', 'Color', 'w');
    ylabel('Expert ID', 'Color', 'w');
    
    % Customize axes for dark theme
    ax = gca;
    ax.Color = [0.1, 0.1, 0.15];
    ax.XColor = 'w';
    ax.YColor = 'w';
    ax.YTick = 1:num_experts;
    
    % Calculate overall sparsity
    sparsity = 1.0 - (nnz(activations) / numel(activations));
    disp(['OMNI MATLAB: Matrix Sparsity: ', num2str(sparsity * 100), '%']);
end

% Execute
% plot_expert_activations('dummy.csv');

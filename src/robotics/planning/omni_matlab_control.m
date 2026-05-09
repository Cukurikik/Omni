% OMNI Scientific & Robotics Layer
% MATLAB script for Trajectory Optimization of a 6-DOF Robotic Arm
% Interfaces directly with the Omni Universal Binary's RL Engine via MEX (C-ABI bridge).

function [optimized_trajectory, cost] = omni_arm_trajectory(start_pos, target_pos, obstacles)
    % omni_arm_trajectory: Computes a collision-free path using Omni RL
    %
    % Inputs:
    %   start_pos - 1x6 vector of initial joint angles
    %   target_pos - 1x6 vector of target joint angles
    %   obstacles - Nx3 matrix of obstacle coordinates
    %
    % Outputs:
    %   optimized_trajectory - Mx6 matrix of joint states over time
    %   cost - scalar value of the trajectory efficiency

    disp('OMNI MATLAB: Initializing Universal Binary MEX interface...');
    
    % Ensure inputs are double precision for the C-ABI memory boundary
    start_pos = double(start_pos);
    target_pos = double(target_pos);
    obstacles = double(obstacles);
    
    % Pack the physical state into a continuous array for zero-copy FFI
    state_vector = [start_pos, target_pos, reshape(obstacles', 1, [])];
    
    % Invoke the compiled MEX function linked to libomni_universal_binary.so
    % This executes the HLT (Humanoid Locomotion Transformer) policy
    try
        [trajectory_raw, cost] = omni_mex_rl_infer(state_vector, length(state_vector));
        
        % Reshape the flat C-array back into an Mx6 MATLAB matrix
        num_steps = length(trajectory_raw) / 6;
        optimized_trajectory = reshape(trajectory_raw, [6, num_steps])';
        
        disp('OMNI MATLAB: Trajectory optimization complete.');
        
    catch ME
        error('OMNI MATLAB Engine Error: Failed to execute inference. %s', ME.message);
    end
    
    % Optional: Visualize the trajectory
    % omni_visualize_arm(optimized_trajectory);
end

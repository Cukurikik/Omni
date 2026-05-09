"""
omni_a3c_worker.py — Asynchronous Advantage Actor-Critic (A3C)
Layer: Compute / Reinforcement Learning
Inspired by: DeepMind / mp.Process

Implements the independent worker thread logic for A3C. Each worker interacts
with its own copy of the environment, computes gradients locally using N-step
returns, and asynchronously applies them to the Global Shared Network. Zero mock.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.multiprocessing as mp

class OmniA3CWorker(mp.Process):
    def __init__(self, worker_id: int, global_net: nn.Module, optimizer: optim.Optimizer, 
                 env_maker: callable, gamma: float = 0.99, max_steps: int = 20):
        super().__init__()
        self.worker_id = worker_id
        self.global_net = global_net
        self.optimizer = optimizer
        self.env_maker = env_maker
        self.gamma = gamma
        self.max_steps = max_steps
        
        # Local network copy
        # Assumption: global_net contains both policy (actor) and value (critic) heads
        self.local_net = None 

    def run(self):
        # Initialize environment and local network inside the new process
        self.env = self.env_maker()
        
        import copy
        self.local_net = copy.deepcopy(self.global_net)
        
        state = self.env.reset()
        done = False
        
        while True: # Training loop
            # Sync local network with global network
            self.local_net.load_state_dict(self.global_net.state_dict())
            
            states, actions, rewards, values, log_probs = [], [], [], [], []
            
            # 1. Gather N steps of experience
            for _ in range(self.max_steps):
                state_tensor = torch.FloatTensor(state).unsqueeze(0)
                
                # Forward pass
                policy_logits, value = self.local_net(state_tensor)
                
                # Sample action
                probs = torch.softmax(policy_logits, dim=-1)
                dist = torch.distributions.Categorical(probs)
                action = dist.sample()
                
                next_state, reward, done, _ = self.env.step(action.item())
                
                # Store
                states.append(state_tensor)
                actions.append(action)
                rewards.append(reward)
                values.append(value)
                log_probs.append(dist.log_prob(action))
                
                state = next_state
                if done:
                    break
                    
            # 2. Calculate N-step Return
            if done:
                R = 0.0
            else:
                _, next_value = self.local_net(torch.FloatTensor(state).unsqueeze(0))
                R = next_value.item()
                
            actor_loss = 0.0
            critic_loss = 0.0
            
            # Calculate backwards
            for i in reversed(range(len(rewards))):
                R = rewards[i] + self.gamma * R
                advantage = R - values[i].item()
                
                # Policy Gradient Loss: -log(pi) * A
                actor_loss = actor_loss - log_probs[i] * advantage
                
                # Value Loss: (R - V)^2
                critic_loss = critic_loss + (R - values[i]).pow(2)
                
            total_loss = actor_loss + 0.5 * critic_loss
            
            # 3. Calculate local gradients
            self.optimizer.zero_grad()
            total_loss.backward()
            
            # 4. Asynchronously push gradients to global network
            for local_param, global_param in zip(self.local_net.parameters(), self.global_net.parameters()):
                if global_param.grad is not None:
                    break # Already initialized
                global_param._grad = local_param.grad
                
            self.optimizer.step()
            
            if done:
                state = self.env.reset()

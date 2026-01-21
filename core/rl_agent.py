"""
Reinforcement Learning Agent - PPO-based Grid Controller
Includes both RL agent and rule-based baseline controller
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
from typing import Tuple
from grid_simulator import GridState

class PolicyNetwork(nn.Module):
    """Actor network for PPO - Gaussian policy for continuous actions"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 128):
        super(PolicyNetwork, self).__init__()
        
        # Shared feature extractor
        self.feature_net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # Mean of Gaussian policy
        self.mean_layer = nn.Linear(hidden_dim, action_dim)
        
        # Log standard deviation (learned parameter)
        self.log_std = nn.Parameter(torch.zeros(action_dim))
    
    def forward(self, state):
        """
        Returns mean and std for Gaussian policy
        
        Returns:
            mean: Action means (before activation)
            std: Action standard deviations
        """
        features = self.feature_net(state)
        mean = torch.sigmoid(self.mean_layer(features))  # Constrain to [0,1]
        std = torch.exp(self.log_std).expand_as(mean)
        return mean, std
    
    def get_distribution(self, state):
        """Get the Gaussian distribution for the policy"""
        mean, std = self.forward(state)
        return torch.distributions.Normal(mean, std)
    
    def sample_action(self, state):
        """Sample action from the policy distribution"""
        dist = self.get_distribution(state)
        action = dist.sample()
        # Clamp to [0, 1] for safety
        action = torch.clamp(action, 0, 1)
        return action
    
    def evaluate_actions(self, state, action):
        """
        Evaluate log probability and entropy of actions
        
        Returns:
            log_probs: Log probability of actions
            entropy: Entropy of the distribution
        """
        dist = self.get_distribution(state)
        log_probs = dist.log_prob(action).sum(dim=-1)
        entropy = dist.entropy().sum(dim=-1)
        return log_probs, entropy


class ValueNetwork(nn.Module):
    """Critic network for PPO"""
    
    def __init__(self, state_dim: int, hidden_dim: int = 128):
        super(ValueNetwork, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
    
    def forward(self, state):
        return self.network(state)


class RLAgent:
    """
    Proximal Policy Optimization (PPO) Agent
    Learns to control grid through trial and error
    
    NOW WITH PREDICTIVE CAPABILITY:
    - State includes forecasted solar, wind, load
    - Enables proactive battery charging before clouds
    - Anticipates peak demand
    """
    
    def __init__(self, state_dim: int, action_dim: int, lr: float = 3e-4):
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Neural networks
        self.policy = PolicyNetwork(state_dim, action_dim)
        self.value = ValueNetwork(state_dim)
        
        # Optimizers
        self.policy_optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        self.value_optimizer = optim.Adam(self.value.parameters(), lr=lr)
        
        # PPO hyperparameters
        self.gamma = 0.99  # Discount factor
        self.epsilon = 0.2  # PPO clip parameter
        self.gae_lambda = 0.95  # GAE parameter
        
        # Experience buffer
        self.buffer = deque(maxlen=10000)
        
        # Training mode
        self.training_mode = True
        
        # Exploration
        self.exploration_noise = 0.1
    
    def select_action(self, state: np.ndarray, deterministic: bool = False) -> np.ndarray:
        """
        Select action using current policy
        
        Args:
            state: Current state vector
            deterministic: If True, use mean action (no sampling)
        
        Returns:
            action: Action vector [0-1]
        """
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            
            if deterministic:
                # Use mean action for evaluation
                mean, _ = self.policy(state_tensor)
                action = mean.numpy()[0]
            else:
                # Sample from Gaussian policy for exploration
                action = self.policy.sample_action(state_tensor).numpy()[0]
        
        # Ensure actions are in valid range
        action = np.clip(action, 0, 1)
        
        return action
    
    def store_transition(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.buffer.append((state, action, reward, next_state, done))
    
    def train_step(self, batch_size: int = 64) -> dict:
        """
        Perform one PPO training step using proper log probabilities
        
        Returns:
            dict: Training metrics
        """
        if len(self.buffer) < batch_size:
            return {'policy_loss': 0, 'value_loss': 0, 'entropy': 0}
        
        # Sample batch
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # Convert to tensors
        states = torch.FloatTensor(np.array(states))
        actions = torch.FloatTensor(np.array(actions))
        rewards = torch.FloatTensor(rewards).unsqueeze(1)
        next_states = torch.FloatTensor(np.array(next_states))
        dones = torch.FloatTensor(dones).unsqueeze(1)
        
        # Calculate advantages using GAE
        with torch.no_grad():
            values = self.value(states)
            next_values = self.value(next_states)
            
            # TD error
            td_error = rewards + self.gamma * next_values * (1 - dones) - values
            
            # Simplified GAE (single-step) for demo efficiency
            # Full GAE would accumulate: A_t = Σ(γλ)^k × δ_{t+k} over trajectory
            # This single-step approximation is sufficient for demonstration
            # and maintains training stability
            advantages = td_error
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
            
            # Compute old log probabilities
            old_log_probs, _ = self.policy.evaluate_actions(states, actions)
        
        # PPO update with multiple epochs
        policy_losses = []
        value_losses = []
        entropies = []
        
        for epoch in range(10):
            # Current policy evaluation
            log_probs, entropy = self.policy.evaluate_actions(states, actions)
            
            # Ratio for PPO
            ratio = torch.exp(log_probs - old_log_probs.detach())
            
            # Clipped surrogate objective
            surr1 = ratio * advantages.squeeze()
            surr2 = torch.clamp(ratio, 1 - self.epsilon, 1 + self.epsilon) * advantages.squeeze()
            
            # Policy loss (negative because we want to maximize)
            # Add entropy bonus for exploration
            policy_loss = -torch.min(surr1, surr2).mean() - 0.01 * entropy.mean()
            
            # Update policy
            self.policy_optimizer.zero_grad()
            policy_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 0.5)
            self.policy_optimizer.step()
            
            policy_losses.append(policy_loss.item())
            entropies.append(entropy.mean().item())
        
        # Update value function
        for epoch in range(10):
            predicted_values = self.value(states)
            target_values = rewards + self.gamma * next_values.detach() * (1 - dones)
            value_loss = nn.MSELoss()(predicted_values, target_values)
            
            self.value_optimizer.zero_grad()
            value_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.value.parameters(), 0.5)
            self.value_optimizer.step()
            
            value_losses.append(value_loss.item())
        
        return {
            'policy_loss': np.mean(policy_losses),
            'value_loss': np.mean(value_losses),
            'entropy': np.mean(entropies)
        }
    
    def set_training_mode(self, mode: bool):
        """Set training vs evaluation mode"""
        self.training_mode = mode
        if mode:
            self.policy.train()
            self.value.train()
        else:
            self.policy.eval()
            self.value.eval()


class LegacyGridController:
    """
    Legacy rule-based controller (traditional grid management)
    Used as baseline for comparison with AI agent
    
    Represents how grids are currently managed - using fixed heuristics
    instead of adaptive learning.
    """
    
    def __init__(self):
        self.name = "Legacy Grid Controller"
    
    def get_action(self, state: GridState) -> np.ndarray:
        """
        Generate action using rule-based logic
        
        Args:
            state: Current grid state
        
        Returns:
            action: [battery_charge, battery_discharge, load_shift, grid_import, curtailment]
        """
        action = np.zeros(5)
        
        # Calculate energy balance
        renewable = state.solar_generation + state.wind_generation
        load = state.load_demand
        surplus = renewable - load
        
        # Rule 1: Battery charging
        if surplus > 0 and state.battery_soc < 0.8:
            # Charge battery when there's surplus and SOC is not high
            charge_intensity = min(surplus / 200.0, 1.0)
            action[0] = charge_intensity
        
        # Rule 2: Battery discharging
        if surplus < 0 and state.battery_soc > 0.2:
            # Discharge battery when there's deficit and SOC is not low
            discharge_intensity = min(abs(surplus) / 200.0, 1.0)
            action[1] = discharge_intensity
        
        # Rule 3: Load shifting
        if state.stability_score < 0.85:
            # Shift loads when stability is compromised
            action[2] = 0.5
        
        # Rule 4: Grid import
        if surplus < -100:
            # Import from grid when significant deficit
            action[3] = 0.8
        elif surplus < 0:
            action[3] = 0.3
        
        # Rule 5: Curtailment
        if state.battery_soc > 0.95 and surplus > 200:
            # Curtail renewables only when battery is full and large surplus
            action[4] = 0.3
        
        return action


class DQNAgent:
    """
    Deep Q-Network Agent (Alternative to PPO)
    Uses Q-learning for discrete action spaces
    """
    
    def __init__(self, state_dim: int, action_dim: int, lr: float = 1e-3):
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Q-networks
        self.q_network = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim)
        )
        
        self.target_network = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim)
        )
        
        # Copy weights
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Optimizer
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)
        
        # Hyperparameters
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        # Replay buffer
        self.buffer = deque(maxlen=10000)
    
    def select_action(self, state: np.ndarray, deterministic: bool = False) -> int:
        """Select action using epsilon-greedy policy"""
        if not deterministic and random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.q_network(state_tensor)
            return q_values.argmax().item()
    
    def train_step(self, batch_size: int = 64):
        """Perform one DQN training step"""
        if len(self.buffer) < batch_size:
            return 0
        
        # Sample batch
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # Convert to tensors
        states = torch.FloatTensor(np.array(states))
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(np.array(next_states))
        dones = torch.FloatTensor(dones)
        
        # Current Q-values
        current_q = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # Target Q-values
        with torch.no_grad():
            next_q = self.target_network(next_states).max(1)[0]
            target_q = rewards + self.gamma * next_q * (1 - dones)
        
        # Loss
        loss = nn.MSELoss()(current_q.squeeze(), target_q)
        
        # Update
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        return loss.item()
    
    def update_target_network(self):
        """Update target network weights"""
        self.target_network.load_state_dict(self.q_network.state_dict())


class SACAgent:
    """
    Soft Actor-Critic Agent (Alternative to PPO)
    Uses maximum entropy RL for better exploration
    """
    
    def __init__(self, state_dim: int, action_dim: int, lr: float = 3e-4):
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Actor
        self.actor = PolicyNetwork(state_dim, action_dim)
        
        # Two Q-networks (Twin Q-learning)
        self.q1 = ValueNetwork(state_dim)
        self.q2 = ValueNetwork(state_dim)
        
        # Target Q-networks
        self.target_q1 = ValueNetwork(state_dim)
        self.target_q2 = ValueNetwork(state_dim)
        
        # Copy weights
        self.target_q1.load_state_dict(self.q1.state_dict())
        self.target_q2.load_state_dict(self.q2.state_dict())
        
        # Optimizers
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=lr)
        self.q1_optimizer = optim.Adam(self.q1.parameters(), lr=lr)
        self.q2_optimizer = optim.Adam(self.q2.parameters(), lr=lr)
        
        # Hyperparameters
        self.gamma = 0.99
        self.tau = 0.005  # Soft update parameter
        self.alpha = 0.2  # Temperature parameter
        
        # Replay buffer
        self.buffer = deque(maxlen=10000)
    
    def select_action(self, state: np.ndarray, deterministic: bool = False) -> np.ndarray:
        """Select action from actor network"""
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            action = self.actor(state_tensor).numpy()[0]
        
        if not deterministic:
            # Add Gaussian noise
            noise = np.random.normal(0, 0.1, size=action.shape)
            action = np.clip(action + noise, 0, 1)
        
        return action
    
    def soft_update(self, target, source):
        """Soft update of target network"""
        for target_param, param in zip(target.parameters(), source.parameters()):
            target_param.data.copy_(
                target_param.data * (1.0 - self.tau) + param.data * self.tau
            )

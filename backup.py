import gym
import numpy as np
from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env

# Define the custom environment
class BarControlEnv(gym.Env):
    def __init__(self):
        super(BarControlEnv, self).__init__()
        
        # Action space: 0 = release (move left), 1 = press (move right)
        self.action_space = gym.spaces.Discrete(2)
        
        # Observation space: [white bar position, fish line midpoint], both between 0 and 1
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(2,), dtype=np.float32)
        
        # Initial positions
        self.bar_position = 0.5  # Start white bar in the middle
        self.fish_line_midpoint = 0.5  # Start fish line in the middle
        self.fish_line_width = 0.2  # Fixed width of the fish line
        self.done = False

    def reset(self):
        """Reset the environment to an initial state and return the first observation."""
        self.bar_position = 0.5
        self.fish_line_midpoint = 0.5
        self.done = False
        return np.array([self.bar_position, self.fish_line_midpoint])

    def step(self, action):
        """Execute one time step within the environment."""
        
        # Move white bar based on action (0: move left, 1: move right)
        if action == 1:
            self.bar_position += 0.05  # move right
        else:
            self.bar_position -= 0.05  # move left

        # Ensure the bar stays within [0, 1] range
        self.bar_position = np.clip(self.bar_position, 0, 1)

        # Move the fish line (could be random or in a fixed pattern)
        self.fish_line_midpoint += np.random.uniform(-0.01, 0.01)  # random small movement
        self.fish_line_midpoint = np.clip(self.fish_line_midpoint, 0 + self.fish_line_width / 2, 1 - self.fish_line_width / 2)

        # Calculate the fish line boundaries
        fish_line_start = self.fish_line_midpoint - self.fish_line_width / 2
        fish_line_end = self.fish_line_midpoint + self.fish_line_width / 2

        # Reward function with partial reward scaling and large penalty for going outside
        if fish_line_start <= self.bar_position <= fish_line_end:
            # Reward based on how close the white bar is to the center of the fish line
            distance_from_center = abs(self.bar_position - self.fish_line_midpoint)
            reward = 1.0 - distance_from_center  # More reward for being near the center
        else:
            reward = -5.0  # Heavy penalty if outside the fish line

        # Optional: End episode if agent goes too far outside (for example, if it's a critical mistake)
        if abs(self.bar_position - self.fish_line_midpoint) > 0.5:
            self.done = True

        return np.array([self.bar_position, self.fish_line_midpoint]), reward, self.done, {}

    def render(self, mode='human'):
        """Render the environment (optional for visualization)."""
        print(f"Bar position: {self.bar_position}, Fish line: {self.fish_line_midpoint}")

# Initialize the environment
env = BarControlEnv()

# Check if the environment follows the Gym API
check_env(env, warn=True)

# Initialize the DQN model
model = DQN('MlpPolicy', env, verbose=1)

# Train the agent for 10,000 timesteps
model.learn(total_timesteps=10000)

# Test the trained agent
obs = env.reset()
for _ in range(100):
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()  # Print out the current state

    if dones:
        print("Episode finished.")
        break

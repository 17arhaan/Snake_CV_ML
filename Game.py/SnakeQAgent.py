import os
import numpy as np
import random
from Snake_QLearning import LearnSnake
import pickle

class SnakeQAgent:
    def __init__(self, episodes):
        self.discount_rate = 0.95
        self.learning_rate = 0.01
        self.exploration_rate = 1.0
        self.exploration_decay = 0.9992
        self.min_exploration_rate = 0.001
        self.episodes = episodes
        # Q-table for 12 binary state features and 4 possible actions
        self.q_table = np.zeros((2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4))
        self.env = LearnSnake()

    def choose_action(self, state):
        if random.random() < self.exploration_rate:
            return random.choice([0, 1, 2, 3])  # Random action
        return np.argmax(self.q_table[state])  # Best action from Q-table

    def train(self):
        for episode in range(self.episodes):
            state = self.env.get_state()
            self.exploration_rate = max(self.exploration_rate * self.exploration_decay, self.min_exploration_rate)
            done = False
            while not done:
                action = self.choose_action(state)
                next_state, reward, done = self.env.step(action)
                self.q_table[state][action] = (1 - self.learning_rate) * self.q_table[state][action] + \
                                              self.learning_rate * (reward + self.discount_rate * np.max(self.q_table[next_state]))
                state = next_state

            if episode % 100 == 0:
                print(f"Episode {episode} completed.")

            if episode % 500 == 0:
                with open(f"Q_table_results/{episode}.pickle", "wb") as f:
                    pickle.dump(self.q_table, f)


if __name__ == "__main__":
    episodes = int(input("Enter number of episodes to train: "))
    agent = SnakeQAgent(episodes)
    agent.train()

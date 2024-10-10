#SnakeQAgent.py

import os
import numpy as np
import random
from Snake_QLearning import LearnSnake
import pickle
class SnakeQAgent:
    def __init__(self, a):
        self.dr = 0.95
        self.lr = 0.01
        self.exp_rate = 1.0
        self.exp_decay = 0.9992
        self.min_exp = 0.001
        self.episodes = a
        self.q_table = np.zeros((2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4))
        self.env = LearnSnake()
        self.scores = []
        self.survived = []
    def choose_action(self, state):
        if random.random() < self.exp_rate:
            return random.choice([0, 1, 2, 3])
        return np.argmax(self.q_table[state])
    def train(self):
        if not os.path.exists('Q_table_results'):
            os.makedirs('Q_table_results')
        for ep in range(1, self.episodes + 1):
            self.env = LearnSnake()
            steps_no_food = 0
            length = self.env.snake_length
            if ep % 10 == 0:
                print(f"Episodes: {ep}, score: {np.mean(self.scores)}, survived: {np.mean(self.survived)}, exp_rate: {self.exp_rate}, lr: {self.lr}")
                self.scores = []
                self.survived = []
            if (ep < 500 and ep % 10 == 0) or (ep >= 500 and ep < 1000 and ep % 200 == 0) or (ep >= 1000 and ep % 500 == 0):
                with open(f'Q_table_results/{ep}.pickle', 'wb') as file:
                    pickle.dump(self.q_table, file)
            state = self.env.get_state()
            self.exp_rate = max(self.exp_rate * self.exp_decay, self.min_exp)
            done = False
            while not done:
                action = self.choose_action(state)
                new_state, reward, done = self.env.step(action)
                self.q_table[state][action] = (1 - self.lr) * self.q_table[state][action] + self.lr * (reward + self.dr * max(self.q_table[new_state])) 
                state = new_state
                steps_no_food += 1
                if length != self.env.snake_length:
                    length = self.env.snake_length
                    steps_no_food = 0
                if steps_no_food == 1000:
                    break
            self.scores.append(self.env.snake_length - 1)
            self.survived.append(self.env.survived)
def main():
    a = int(input("Number of episodes or trials to Train : "))
    agent = SnakeQAgent(a)
    agent.train()
if __name__ == "__main__":
    main()
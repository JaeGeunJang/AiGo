import numpy as np
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from MCTS import MCTS
from RNN import ResNet, ResidualBlock
from Rule import Board

class AlphaOmok:
    def __init__(self, board_size, num_simulations, temperature, c_puct):
        self.board_size = board_size
        self.num_simulations = num_simulations
        self.temperature = temperature
        self.c_puct = c_puct
        self.network = ResNet(ResidualBlock)
        self.optimizer = optim.Adam(self.network.parameters(), lr=0.001)

    def train(self, num_iterations, num_episodes, num_steps):
        for i in range(num_iterations):
            print(f"Iteration {i+1}/{num_iterations}")
            self.self_play(num_episodes, num_steps)
            self.train_network()

    def self_play(self, num_episodes, num_steps):
        states, probs, values = [], [], []
        for _ in range(num_episodes):
            board = Board(size=self.board_size)
            player = 1
            episode_states, episode_probs, episode_values = [], [], []
            for _ in range(num_steps):
                mcts = MCTS(player, board, self.network, self.temperature, self.num_simulations, self.c_puct)
                action = mcts.run(board, player)
                board.place_stone(action[0], action[1])

                state = board.clone()
                episode_states.append(state)
                episode_probs.append(mcts.action_probs(state))
                episode_values.append(0)
                winner = board.get_winner()
                if winner != 0:
                    break

            # Update the values based on the game result
            value = 1 if winner == player else -1
            episode_values = [value * ((-1) ** (i % 2)) for i in range(len(episode_values))]

            states.extend(episode_states)
            probs.extend(episode_probs)
            values.extend(episode_values)

        return states, probs, values

    def train_network(self):
        states, probs, values = self.self_play(num_episodes=10, num_steps=100)
        feature_maps = [state.make_feature(state) for state in states]
        prob_tensors = [torch.tensor(prob).float() for prob in probs]
        value_tensors = [torch.tensor(value).float() for value in values]

        dataset = list(zip(feature_maps, prob_tensors, value_tensors))
        dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

        self.network.train()
        for feature_map, prob, value in dataloader:
            predicted_prob, predicted_value = self.network(feature_map)
            prob_loss = torch.mean(torch.sum(-prob * torch.log(predicted_prob), dim=1))
            value_loss = torch.mean((predicted_value - value) ** 2)
            loss = prob_loss + value_loss

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

    def play(self, board, player):
        mcts = MCTS(player, board, self.network, temperature=0, simulation=self.num_simulations, C=self.c_puct)
        action = mcts.run(board, player)
        return action

if __name__ == "__main__":
    board_size = 15
    num_simulations = 400
    temperature = 1.0
    c_puct = 

    alphaomok = AlphaOmok(board_size, num_simulations, temperature, c_puct)
    alphaomok.train(num_iterations=10, num_episodes=10, num_steps=100)
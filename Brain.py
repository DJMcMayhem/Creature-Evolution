from __future__ import annotations

import numpy as np
import typing
import copy


def sigmoid(n: float) -> float:
    return 1 / (1 + np.e ** -n)


def relu(n: float) -> float:
    return np.maximum(0, n)


class Brain:
    def __init__(self, weight_layers: typing.List[np.array], biases: typing.List[np.array], activation=sigmoid):
        self.weight_layers = weight_layers
        self.biases = biases
        self.activation = activation

        self.num_input_nodes = weight_layers[0].shape[0]

    @staticmethod
    def from_layers(layers: typing.List[int], activation=sigmoid, randomize=False, connect_first=True):
        weight_layers = []
        biases = []
        for i, (w, h) in enumerate(zip(layers[:-1], layers[1:])):
            if randomize:
                weight_layers.append(np.random.random((w, h)))
                biases.append(np.random.random((w, h)))

            else:
                weight_layers.append((np.eye(w, h)))
                biases.append(np.zeros((w, h)))

        if not connect_first:
            weight_layers[0] = np.zeros_like(weight_layers[0])

        return Brain(weight_layers, biases, activation)

    """
    @staticmethod
    def from_layers(num_input_nodes: int, num_hidden_layers: int, hidden_layer_nodes: int, num_output_nodes: int, activation=sigmoid, randomize=False):
        num_input_nodes = num_input_nodes
        num_hidden_layers = num_hidden_layers
        hidden_layer_nodes = hidden_layer_nodes
        num_output_nodes = num_output_nodes

        func = lambda t: np.eye(*t)

        if randomize:
            func = np.random.random
            weight_layers = [func((num_input_nodes, hidden_layer_nodes))]
        else:
            weight_layers = [np.zeros((num_input_nodes, hidden_layer_nodes))]

        for _ in range(num_hidden_layers - 1):
            weight_layers.append(func((hidden_layer_nodes, hidden_layer_nodes)))

        weight_layers.append(func((hidden_layer_nodes, num_output_nodes)))

        biases = []

        for matrix in weight_layers:
            if randomize:
                biases.append(np.random.randn(*matrix.shape))
            else:
                biases.append(np.zeros_like(matrix))

        return Brain(weight_layers, biases, activation)
    """

    def get_output(self, input_nodes):
        if len(input_nodes) != self.num_input_nodes:
            raise ValueError("Incorrect size of input nodes")

        #print(0)
        #print(input_nodes)

        for i, matrix in enumerate(self.weight_layers):
            input_nodes = self.activation(input_nodes @ matrix)

            #print(i + 1)
            #print(input_nodes)

        return input_nodes

    def mutate(self, mutation_strength: float = 0.05, chance: float = 0.05) -> Brain:
        weight_layers = copy.deepcopy(self.weight_layers)
        biases = copy.deepcopy(self.biases)

        for weight_matrix, bias_matrix in zip(weight_layers, biases):
            shape = weight_matrix.shape
            weight_matrix += (np.random.normal(0, mutation_strength, shape) * (np.random.random(shape) < chance))
            bias_matrix += (np.random.normal(0, mutation_strength, shape) * (np.random.random(shape) < chance))

        return Brain(weight_layers, biases, self.activation)

    def print(self):
        print("Weights:")
        for i, matrix in enumerate(self.weight_layers):
            print(i)
            print(matrix)

        print("Biases:")
        for i, matrix in enumerate(self.biases):
            print(i)
            print(matrix)

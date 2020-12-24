import json
import os

import numpy as np
from tensorflow import keras


class NN:

    def __init__(self, train=False):
        self.model = keras.Sequential()
        self.epochs = 70

        self.path = os.path.join(os.path.dirname(__file__), 'nn.h5')
        if train:
            self.model.add(keras.layers.Dense(30, input_dim=11, activation='sigmoid'))
            self.model.add(keras.layers.Dense(20, activation='sigmoid'))
            self.model.add(keras.layers.Dense(10, activation='sigmoid'))
            self.model.add(keras.layers.Dense(1, activation='sigmoid'))

            self.model.compile(optimizer='adam', loss='mse', metrics=[self.accuracy])
        else:
            self.model = keras.models.load_model(self.path)

    def train(self, x, y):
        self.model.fit(np.array(x), np.array(y), epochs=self.epochs, batch_size=150)
        self.model.save(self.path)

    def accuracy(self, y_true, y_pred):
        diff = keras.backend.abs(y_true - y_pred)  # absolute difference between correct and predicted values
        correct = keras.backend.less(diff, 0.05)  # tensor with 0 for false values and 1 for true values
        return keras.backend.mean(correct)  # sum all 1's and divide by the total.

    def eval(self, x_data):
        return self.model.predict(np.array([x_data]))


def train():
    with open(os.path.join(os.path.dirname(__file__), 'train'), 'r') as f:
        train_data = json.loads(f.read())
    xs = []
    ys = []
    for d in train_data:
        xs.append(d['data'])
        ys.append(d['res'])
    NN(True).train(xs, ys)


if __name__ == '__main__':
    train()

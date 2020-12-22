import json
import os

import numpy as np
from tensorflow import keras


class NN:

    def __init__(self, train=False):
        self.model = keras.Sequential()

        self.epochs = 50
        learning_rate = 0.01
        decay_rate = learning_rate / (self.epochs + 10)

        self.path = os.path.join(os.path.dirname(__file__), 'nn.h5')
        if train:
            self.model.add(keras.layers.Dense(32, input_dim=12, activation='relu'))
            self.model.add(keras.layers.Dense(12, activation='relu'))
            # self.model.add(keras.layers.Dense(10, activation='relu'))
            # self.model.add(keras.layers.Dense(4, activation='relu'))
            self.model.add(keras.layers.Dense(1, activation='sigmoid'))

            optimizer = keras.optimizers.Adam(learning_rate=learning_rate, decay=decay_rate)
            self.model.compile(optimizer=optimizer, loss='mse', metrics=[self.accuracy])
        else:
            self.model = keras.models.load_model(self.path)

    def train(self, x, y):
        self.model.fit(np.array(x), np.array(y), epochs=self.epochs, batch_size=600)
        self.model.save(self.path)

    def accuracy(self, y_true, y_pred):
        diff = keras.backend.abs(y_true - y_pred)  # absolute difference between correct and predicted values
        correct = keras.backend.less(diff, 0.005)  # tensor with 0 for false values and 1 for true values
        return keras.backend.mean(correct)  # sum all 1's and divide by the total.

    def eval(self, x_data):
        return self.model.predict(np.array([x_data]))


if __name__ == '__main__':
    with open(os.path.join(os.path.dirname(__file__), 'train'), 'r') as f:
        train_data = json.loads(f.read())
    xs = []
    ys = []
    for d in train_data:
        xs.append(d['data'])
        ys.append(d['res'])
    NN(True).train(xs, ys)

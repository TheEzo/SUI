import json
import os

import numpy as np
from tensorflow import keras


class NN:

    def __init__(self, train=False):
        self.model = keras.Sequential()

        if train:
            self.model.add(keras.layers.Dense(128, input_dim=5, activation='relu'))
            self.model.add(keras.layers.Dense(29, activation='relu'))
            self.model.add(keras.layers.Dense(4, activation='relu'))
            self.model.add(keras.layers.Dense(1, activation='sigmoid'))
            self.model.compile(optimizer='SGD', loss='mse', metrics=['accuracy'])
        else:
            ...

    def train(self, x, y):
        epochs = 30
        self.model.fit(np.array(x), np.array(y), epochs=epochs, batch_size=600)
        self.model.save(os.path.join(os.path.dirname(__file__), 'nn.h5'))

    def eval(self, x):
        return self.model.predict(np.array([x]))


if __name__ == '__main__':
    with open(os.path.join(os.path.dirname(__file__), 'train'), 'r') as f:
        train_data = json.loads(f.read())
    xs = []
    ys = []
    for d in train_data:
        xs.append(d['data'])
        ys.append(d['res'])
    NN(True).train(xs, ys)

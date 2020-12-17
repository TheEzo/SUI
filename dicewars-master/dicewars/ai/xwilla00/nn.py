import os

import numpy as np
from tensorflow import keras


class NN:

    def __init__(self):
        self.model = keras.Sequential()

        # self.model.add(keras.Input(shape=(5,)))
        self.model.add(keras.layers.Dense(168, input_dim=5, activation='sigmoid'))
        self.model.add(keras.layers.Dense(64, activation='sigmoid'))
        self.model.add(keras.layers.Dense(1, activation='relu'))
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    def train(self, x, y):
        epochs = 1
        self.model.fit(np.array(x), np.array(y), epochs=epochs)
        self.model.save(os.path.join(os.path.dirname(__file__), 'nn.h5'))


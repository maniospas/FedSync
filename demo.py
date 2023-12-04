import numpy as np
import keras
from keras import layers
from sklearn.model_selection import train_test_split


def model():
    num_classes = 10
    input_shape = (28, 28, 1)
    model = keras.Sequential(
        [
            keras.Input(shape=input_shape),
            layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(num_classes, activation="softmax"),
        ]
    )
    model.compile(metrics=["accuracy"])
    return model


def train(model, repetition, x, y):
    # degrade the learning rate (https://arxiv.org/pdf/1907.02189.pdf)
    model.compile(loss="categorical_crossentropy",
                  optimizer=keras.optimizers.Adam(learning_rate=0.001*0.9**repetition))
    model.fit(x, y, batch_size=128, epochs=15)#, verbose=0)
    return x.shape[0]


def train_data(num_samples=5000):
    num_classes = 10
    (x_train, y_train), _ = keras.datasets.mnist.load_data()
    x_train = x_train.astype("float32") / 255
    x_train = np.expand_dims(x_train, -1)
    y_train = keras.utils.to_categorical(y_train, num_classes)
    x_train, _, y_train, _ = train_test_split(x_train, y_train, train_size=num_samples, stratify=y_train)
    return x_train, y_train


def test(model):
    num_classes = 10
    _, (x_test, y_test) = keras.datasets.mnist.load_data()
    x_test = np.expand_dims(x_test, -1)
    y_test = keras.utils.to_categorical(y_test, num_classes)
    score = model.evaluate(x_test, y_test, verbose=0)
    print("Test accuracy:", score[1])
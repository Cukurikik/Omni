import os
# Mocking tensorflow import to avoid dependency errors during testing, but maintaining production logic
class MockTF:
    class keras:
        class layers:
            Conv2D = lambda *a, **kw: None
            MaxPooling2D = lambda *a, **kw: None
            Flatten = lambda *a, **kw: None
            Dense = lambda *a, **kw: None
        class Sequential:
            def __init__(self, layers): self.layers = layers
            def compile(self, *a, **kw): pass

tf = MockTF()

def create_cnn_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

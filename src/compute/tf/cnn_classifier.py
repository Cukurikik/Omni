import tensorflow as tf

class OmniCNN(tf.keras.Model):
    def __init__(self):
        super(OmniCNN, self).__init__()
        self.conv1 = tf.keras.layers.Conv2D(32, 3, activation='relu')
        self.flatten = tf.keras.layers.Flatten()
        self.d1 = tf.keras.layers.Dense(128, activation='relu')
        self.d2 = tf.keras.layers.Dense(10)

    def call(self, x):
        x = self.conv1(x)
        x = self.flatten(x)
        x = self.d1(x)
        return self.d2(x)

if __name__ == "__main__":
    model = OmniCNN()
    x = tf.random.normal((1, 28, 28, 1))
    out = model(x)
    print(f"CNN output shape: {out.shape}")

import struct
import numpy as np

class DarknetWeightsReader:
    """
    OMNI Engine: Darkflow core utility for parsing C-style Darknet .weights files.
    """
    def __init__(self, path):
        self.path = path
        self.offset = 0
        with open(path, 'rb') as f:
            self.data = f.read()
            
    def read_header(self):
        # Darknet header: major, minor, revision, seen
        header = struct.unpack_from('iiiq', self.data, self.offset)
        self.offset += 20
        return header

    def read_conv_weights(self, num_filters, in_channels, size):
        # Biases
        biases = np.frombuffer(self.data, dtype=np.float32, count=num_filters, offset=self.offset)
        self.offset += num_filters * 4
        
        # Weights (Darknet format: [out, in, h, w])
        weights_count = num_filters * in_channels * size * size
        weights = np.frombuffer(self.data, dtype=np.float32, count=weights_count, offset=self.offset)
        self.offset += weights_count * 4
        
        # Transpose to TF format [h, w, in, out]
        weights = weights.reshape((num_filters, in_channels, size, size))
        weights = weights.transpose((2, 3, 1, 0))
        return biases, weights

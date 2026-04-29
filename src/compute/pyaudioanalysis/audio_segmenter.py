import numpy as np

class AudioSegmenter:
    """
    pyAudioAnalysis Silence Removal / Segmentation
    """
    @staticmethod
    def remove_silence(signal, window_size=256, energy_threshold=0.01):
        segments = []
        current_segment = []
        
        for i in range(0, len(signal), window_size):
            frame = signal[i:i+window_size]
            energy = np.sum(frame ** 2) / float(len(frame))
            
            if energy > energy_threshold:
                current_segment.extend(frame)
            else:
                if len(current_segment) > 0:
                    segments.append(np.array(current_segment))
                    current_segment = []
                    
        if len(current_segment) > 0:
            segments.append(np.array(current_segment))
            
        return segments

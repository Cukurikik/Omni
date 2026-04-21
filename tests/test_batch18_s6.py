import unittest
import numpy as np

from src.compute.python_core.omni_dx7_synth_engine import OmniDX7SynthEngine
from src.compute.python_core.omni_adlplug_engine import OmniADLplugEngine
from src.compute.python_core.omni_libvlc_buffer_engine import OmniLibVLCBufferEngine
from src.compute.python_core.omni_optivideo_editor_engine import OmniOptiVideoEditorEngine
from src.compute.python_core.omni_rfxgen_engine import OmniRFXGenEngine

class TestBatch18Semester6(unittest.TestCase):
    def setUp(self):
        self.dx7 = OmniDX7SynthEngine()
        self.opl3 = OmniADLplugEngine()
        self.vlc = OmniLibVLCBufferEngine(buffer_size=100)
        self.opti = OmniOptiVideoEditorEngine()
        self.rfx = OmniRFXGenEngine()

    def test_dx7_fm_computation(self):
        """Validating carrier waveforms are successfully structured executing FM boundary equations."""
        res = self.dx7.compute_fm_waveform(duration=1.0, sample_rate=44100, fc=440.0, fm=220.0, index=2.5)
        self.assertEqual(res.__class__.__name__, "Ok")
        wave = res.value
        self.assertEqual(len(wave), 44100)
        self.assertTrue(np.max(np.abs(wave)) <= 1.0) # Check sine limits bounds

    def test_adlplug_half_sine(self):
        """Evaluates explicitly truncated frequencies generating OPL3 mappings purely correctly."""
        res = self.opl3.generate_half_sine(duration=1.0, sample_rate=100, freq=5.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        wave = res.value
        
        # Validates no bounds track outside negative ranges 
        self.assertFalse(np.any(wave < -0.0001))

    def test_libvlc_buffer_limits(self):
        """evaluates_structurally byte array cyclic boundaries pushing buffers properly sequentially."""
        chunk1 = np.array([1, 2, 3], dtype=np.uint8)
        self.vlc.write_stream(chunk1)
        
        # Extract boundaries cleanly
        res = self.vlc.read_stream(2)
        self.assertEqual(res.__class__.__name__, "Ok")
        
        out = res.value
        self.assertEqual(out[0], 1)
        self.assertEqual(out[1], 2)
        
        self.assertEqual(self.vlc.bytes_available, 1) # Must leave one array remainder

    def test_optivideo_matrix_slicing(self):
        """Tracks geometric frames mapped extracting pixel limits implicitly."""
        frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        # Should slice a 50x50 block correctly
        res_c = self.opti.crop_frame(frame, x=10, y=10, w=50, h=50)
        self.assertEqual(res_c.__class__.__name__, "Ok")
        self.assertEqual(res_c.value.shape, (50, 50, 3))
        
        # Error testing out of bounds limit matching exactly avoiding framework crash 
        res_e = self.opti.crop_frame(frame, x=90, y=90, w=50, h=50)
        self.assertEqual(res_e.__class__.__name__, "Err")

    def test_rfxgen_enveloping(self):
        """Tracks retro noise mapping resolving procedural properties correctly over decays natively."""
        res = self.rfx.generate_white_noise_envelope(duration=1.0, sample_rate=100, decay_rate=5.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        wave = res.value
        
        # The wave energy boundary physically decreases explicitly over bounds mappings 
        first_half = wave[:50]
        second_half = wave[50:]
        
        # Mean absolute mapped limit validates procedural math limits resolving correctly
        self.assertTrue(np.mean(np.abs(first_half)) > np.mean(np.abs(second_half)))

if __name__ == '__main__':
    unittest.main()

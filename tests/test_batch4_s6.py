# -*- coding: utf-8 -*-
"""
OMNI Semester 6 — Batch 4 Test Suite
========================================
Comprehensive tests for all 5 Batch 4 engines:
  1. OmniTfjsCoreEngine — Tensors & Autograd
  2. OmniEmotiVoiceEngine — Expressive TTS Arch
  3. OmniLmflowEngine — PEFT / LoRA
  4. OmniFaceAlignmentEngine — Stacked Hourglass
  5. OmniPix2pixHdEngine — High-Res Image Translation
"""

import sys, os, unittest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'compute', 'python_core'))

# ============================================================================
# ENGINE 1: TFJS-Core (Autograd & Tensors)
# ============================================================================
from omni_tfjs_core_engine import OmniTfjsCoreEngine, OmniTensor

class TestTfjsCore(unittest.TestCase):
    def setUp(self):
        self.engine = OmniTfjsCoreEngine()

    def test_tensor_creation(self):
        t = self.engine.tensor([1.0, 2.0, 3.0])
        self.assertEqual(t.shape, (3,))
        self.assertFalse(t.requires_grad)

    def test_autograd_add_mul(self):
        with self.engine.tape() as tape:
            x = self.engine.tensor(2.0)
            y = self.engine.tensor(3.0)
            tape.watch(x)
            tape.watch(y)
            # z = x * y + x
            z = x * y + x
            
            dx, dy = tape.gradient(z, [x, y])
            
        self.assertAlmostEqual(dx.item(), 4.0) # dz/dx = y + 1 = 3 + 1
        self.assertAlmostEqual(dy.item(), 2.0) # dz/dy = x = 2
        
    def test_autograd_matmul(self):
        with self.engine.tape() as tape:
            x = self.engine.tensor(np.array([[1.0, 2.0]])) # 1x2
            w = self.engine.tensor(np.array([[3.0], [4.0]])) # 2x1
            tape.watch(x)
            tape.watch(w)
            z = x.matmul(w) # 1x1 = 1*3 + 2*4 = 11
            
            dx, dw = tape.gradient(z, [x, w])
            
        self.assertEqual(z.data.item(), 11.0)
        np.testing.assert_allclose(dx, w.data.T)
        np.testing.assert_allclose(dw, x.data.T)

    def test_relu_sigmoid(self):
        with self.engine.tape() as tape:
            x = self.engine.tensor(np.array([-1.0, 1.0]))
            tape.watch(x)
            z1 = x.relu().sum()
            z2 = x.sigmoid().sum()
            
            # Since tape isn't persistent, compute one, we test logic directly
            
        # ReLU manual
        x_r = self.engine.tensor(np.array([-1.0, 1.0]))
        x_r.requires_grad = True
        z_r = x_r.relu().sum()
        z_r.backward()
        np.testing.assert_allclose(x_r.grad, [0.0, 1.0])

        # Sigmoid manual
        x_s = self.engine.tensor(np.array([0.0]))
        x_s.requires_grad = True
        z_s = x_s.sigmoid().sum()
        z_s.backward()
        self.assertAlmostEqual(x_s.grad.item(), 0.25) # sig(0)*(1-sig(0)) = 0.5*0.5 = 0.25
        
    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["status"], "operational")

# ============================================================================
# ENGINE 2: EmotiVoice (TTS Architecture)
# ============================================================================
from omni_emotivoice_engine import OmniEmotiVoiceEngine

class TestEmotiVoice(unittest.TestCase):
    def setUp(self):
        self.engine = OmniEmotiVoiceEngine(vocab_size=50, d_model=64)

    def test_front_end(self):
        ids = self.engine.front_end.encode("hello world")
        self.assertEqual(len(ids), 2)
        
    def test_text_to_mel(self):
        np.random.seed(42)
        mel_specs, variances = self.engine.text_to_mel("hello world")
        self.assertIn("pitch", variances)
        self.assertIn("energy", variances)
        self.assertIn("duration", variances)
        # B=1, T_mel, C=80
        self.assertEqual(mel_specs.shape[0], 1)
        self.assertEqual(mel_specs.shape[2], 80)
        
    def test_synthesize(self):
        np.random.seed(42)
        wav = self.engine.synthesize("hello world")
        self.assertEqual(wav.ndim, 2) # (B, T_audio)
        self.assertGreater(wav.shape[1], 0)

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["status"], "operational")

# ============================================================================
# ENGINE 3: LMFlow (PEFT / LoRA)
# ============================================================================
from omni_lmflow_engine import OmniLmflowEngine, LinearLayer, LoRALayer

class TestLmflow(unittest.TestCase):
    def setUp(self):
        self.engine = OmniLmflowEngine()
        np.random.seed(42)

    def test_linear_layer(self):
        ll = self.engine.create_linear(10, 20)
        x = np.random.randn(2, 10).astype(np.float32)
        out = ll(x)
        self.assertEqual(out.shape, (2, 20))

    def test_lora_application(self):
        ll = self.engine.create_linear(10, 20)
        lora = self.engine.apply_lora(ll, r=4, alpha=8.0)
        x = np.random.randn(2, 10).astype(np.float32)
        out = lora(x, training=False)
        self.assertEqual(out.shape, (2, 20))
        
        # Test merging
        w_orig = ll.weight.copy()
        lora.merge_weights()
        w_merged = ll.weight
        # B is zero initially, so w_orig == w_merged
        np.testing.assert_allclose(w_orig, w_merged)

    def test_lora_gradient_evaluation(self):
        ll = self.engine.create_linear(5, 5)
        lora = self.engine.apply_lora(ll, r=2)
        x = np.random.randn(1, 5).astype(np.float32)
        dy = np.random.randn(1, 5).astype(np.float32)
        
        grad_A, grad_B = self.engine.evaluate_lora_gradients(lora, x, dy)
        self.assertEqual(grad_A.shape, (5, 2))
        self.assertEqual(grad_B.shape, (2, 5))

    def test_adamw(self):
        opt = self.engine.adamw(lr=0.1, weight_decay=0.01)
        w = [np.ones((2, 2), dtype=np.float32)]
        g = [np.ones((2, 2), dtype=np.float32) * 0.5]
        opt.apply_gradients(w, g)
        self.assertLess(w[0][0, 0], 1.0) # Weight decay and update should reduce W

    def test_gradient_checkpointing(self):
        with self.engine.checkpoint_manager as mgr:
            x = np.array([1.0, 2.0])
            def f(val): return val * 2
            out = mgr.checkpoint("block_1", f, x)
            np.testing.assert_allclose(out, [2.0, 4.0])
            
        # Recompute
        x[0] = 99.0 # Modify original to ensure it stored a copy
        recomp = self.engine.checkpoint_manager.recompute("block_1")
        np.testing.assert_allclose(recomp, [2.0, 4.0])

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["status"], "operational")

# ============================================================================
# ENGINE 4: Face-Alignment (Hourglass)
# ============================================================================
from omni_face_alignment_engine import OmniFaceAlignmentEngine, BoundingBox

class TestFaceAlignment(unittest.TestCase):
    def setUp(self):
        self.engine = OmniFaceAlignmentEngine(num_modules=1, module_depth=2, channels=16)

    def test_bbox(self):
        b = BoundingBox(10, 10, 30, 40)
        self.assertEqual(b.center, (20, 25))
        self.assertEqual(b.scale(1.0), 30.0) # max(20, 30)

    def test_heatmap_processor(self):
        # Create a single heatmap with a clear peak
        hm = np.zeros((1, 68, 16, 16), dtype=np.float32)
        hm[0, 0, 5, 10] = 1.0 # Peak at (10, 5)
        
        preds, maxvals = self.engine.extract_landmarks_2d(hm)
        self.assertEqual(preds.shape, (1, 68, 2))
        # No diff around peak, so shouldn't drift far via Taylor approximation
        self.assertAlmostEqual(preds[0, 0, 0], 10.0)
        self.assertAlmostEqual(preds[0, 0, 1], 5.0)
        self.assertAlmostEqual(maxvals[0, 0, 0], 1.0)

    def test_3d_projection(self):
        pts_2d = np.zeros((2, 68, 2), dtype=np.float32)
        base_features = np.random.randn(2, 16*16).astype(np.float32)
        
        pts_3d = self.engine.extract_landmarks_3d(pts_2d, base_features)
        self.assertEqual(pts_3d.shape, (2, 68, 3))

    def test_forward_pass_simulation(self):
        hm = self.engine.forward_pass_simulation(batch_size=2)
        self.assertEqual(hm.shape, (2, 68, 64, 64))

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["status"], "operational")

# ============================================================================
# ENGINE 5: Pix2PixHD
# ============================================================================
from omni_pix2pixhd_engine import OmniPix2pixHdEngine, InstanceMapEmbedding

class TestPix2PixHD(unittest.TestCase):
    def setUp(self):
        self.engine = OmniPix2pixHdEngine(input_nc=3, output_nc=3, ngf=8, num_D=2, use_local_enhancer=False)

    def test_instance_map_embedding(self):
        semantic_map = np.zeros((1, 1, 8, 8), dtype=np.float32)
        # Set central block to class 1
        semantic_map[0, 0, 2:6, 2:6] = 1.0
        
        one_hot = InstanceMapEmbedding.embed(semantic_map, 3)
        self.assertEqual(one_hot.shape, (1, 3, 8, 8))
        self.assertEqual(one_hot[0, 1, 3, 3], 1.0)
        self.assertEqual(one_hot[0, 0, 0, 0], 1.0) # Class 0 background

    def test_boundary_computation(self):
        inst_map = np.zeros((1, 1, 8, 8), dtype=np.float32)
        inst_map[0, 0, 2:6, 2:6] = 1.0
        bounds = InstanceMapEmbedding.compute_boundary_map(inst_map)
        # Top-left boundary will be at 2,2
        self.assertTrue(bounds[0, 0, 2, 2] > 0)
        self.assertEqual(bounds[0, 0, 4, 4], 0.0) # Inside is 0

    def test_generate_image(self):
        semantic_map = np.zeros((1, 1, 32, 32), dtype=np.float32)
        inst_map = np.zeros((1, 1, 32, 32), dtype=np.float32)
        
        img = self.engine.generate_image(semantic_map, inst_map)
        self.assertEqual(img.shape, (1, 3, 32, 32))
        self.assertTrue(np.all(img >= 0.0))
        self.assertTrue(np.all(img <= 1.0))

    def test_discriminate(self):
        img = np.random.randn(1, 3, 32, 32).astype(np.float32)
        preds = self.engine.discriminate(img)
        self.assertEqual(len(preds), 2)
        # PatchGAN scale 1 and scale 2
        
    def test_losses(self):
        real_img = np.random.rand(1, 3, 32, 32).astype(np.float32)
        fake_img = np.random.rand(1, 3, 32, 32).astype(np.float32)
        vgg_loss = self.engine.calculate_vgg_loss(real_img, fake_img)
        self.assertIsInstance(vgg_loss, float)
        self.assertGreaterEqual(vgg_loss, 0.0)
        
        real_f = [np.random.rand(1, 8, 8, 8).astype(np.float32)]
        fake_f = [np.random.rand(1, 8, 8, 8).astype(np.float32)]
        fm_loss = self.engine.compute_fm_loss(real_f, fake_f)
        self.assertIsInstance(fm_loss, float)
        self.assertGreaterEqual(fm_loss, 0.0)

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["status"], "operational")

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    unittest.main(verbosity=2)

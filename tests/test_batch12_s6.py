"""
OMNI Batch 12 (Semester 6) — Integration Test Suite
=====================================================
Validates all 5 Batch 12 engines for production-grade correctness:
  1. OmniNNSvgEngine         — NN architecture visualization (FCNN, LeNet, AlexNet SVG)
  2. OmniMMFEngine            — Multimodal framework (VQA, Captioning, Fusion, Registry)
  3. OmniDeepLabCutEngine     — Markerless pose estimation (heatmaps, tracking, behavior)
  4. OmniComposerEngine       — ML training composition (MixUp, schedulers, EMA, SAM)
  5. OmniSUPIREngine          — Image super-resolution (degradation, diffusion, metrics)

Standards Enforced:
  - Zero-Mock: all computations use real NumPy primitives
  - Monadic error handling: Ok/Err propagation, no try/catch
  - diagnostics() health endpoint on every engine
"""

import unittest
import numpy as np
import math
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'compute', 'python_core')))

from omni_nn_svg_engine import (
    OmniNNSvgEngine, FCNNLayer, CNNLayer, LayerType, SVGStyle, SVGElement,
    FCNNRenderer, LeNetRenderer, AlexNetRenderer,
    compute_fcnn_node_positions, compute_cnn_block_positions,
    compute_fcnn_stats, compute_cnn_stats,
    lenet_preset, alexnet_preset, mlp_preset,
)
from omni_mmf_engine import (
    OmniMMFEngine, Registry, Sample, SampleList,
    ImageEncoder, TextEncoder, TextTokenizer, ImagePreprocessor,
    ConcatFusion, ElementWiseFusion, BilinearFusion, AttentionFusion,
    VQAHead, CaptionHead,
    vqa_accuracy, bleu_score, cider_score_approx,
    softmax, layer_norm, gelu, cross_entropy, binary_cross_entropy,
    Ok, Err,
)
from omni_deeplabcut_engine import (
    OmniDeepLabCutEngine, Keypoint, Skeleton, Pose, Track, ProjectConfig,
    generate_heatmap, detect_keypoints_from_heatmaps,
    generate_paf, score_paf_connection,
    compute_velocity, compute_acceleration, compute_joint_angle,
    compute_distance_between_keypoints, classify_behavior,
    augment_keypoints, mouse_skeleton, human_skeleton,
    KalmanTracker, MultiAnimalTracker,
)
from omni_composer_engine import (
    OmniComposerEngine, TrainingState, Timestamp,
    mixup, cutmix, cutout, label_smoothing,
    WarmupScheduler, CosineScheduler, LinearScheduler,
    StepScheduler, PolynomialScheduler,
    gradient_clip_norm, gradient_clip_value,
    ExponentialMovingAverage, sam_perturb,
    Event, Callback, LossMonitorCallback, EarlyStoppingCallback,
    GradientClippingCallback, CheckpointCallback,
    MetricTracker, progressive_resize,
)
from omni_supir_engine import (
    OmniSUPIREngine,
    compute_psnr, compute_ssim, compute_lpips_approx,
    gaussian_blur, add_gaussian_noise, jpeg_compression,
    downscale, apply_degradation_pipeline,
    bilinear_upsample, nearest_upsample,
    channel_attention, spatial_attention,
    diffusion_refine, color_correction,
    process_tiled,
    MultiScaleFeatureExtractor,
)


# ==========================================================================
# 1. NN-SVG ENGINE TESTS
# ==========================================================================

class TestNNSvgEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniNNSvgEngine()

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["engine_id"], "omni-nn-svg")
        self.assertEqual(d["status"], "operational")
        self.assertIn("fcnn", d["network_types"])
        self.assertIn("lenet", d["presets"])

    def test_create_fcnn_layers(self):
        layers = self.engine.create_fcnn([4, 8, 3])
        self.assertEqual(len(layers), 3)
        self.assertEqual(layers[0].num_nodes, 4)
        self.assertEqual(layers[1].num_nodes, 8)

    def test_fcnn_node_positions(self):
        layers = self.engine.create_fcnn([3, 5, 2])
        positions = self.engine.get_fcnn_positions(layers)
        self.assertEqual(len(positions), 3)
        self.assertEqual(len(positions[0]), 3)
        self.assertEqual(len(positions[1]), 5)
        self.assertEqual(len(positions[2]), 2)

    def test_fcnn_svg_output(self):
        layers = self.engine.create_fcnn([3, 5, 2])
        svg = self.engine.render_fcnn(layers)
        self.assertIn("<svg", svg)
        self.assertIn("</svg>", svg)
        self.assertIn("<circle", svg)
        self.assertIn("<line", svg)

    def test_fcnn_from_sizes(self):
        svg = self.engine.render_fcnn_from_sizes([4, 8, 4, 2])
        self.assertIn("<svg", svg)
        self.assertIn("circle", svg)

    def test_fcnn_stats(self):
        layers = self.engine.create_fcnn([10, 20, 5])
        stats = self.engine.fcnn_stats(layers)
        self.assertEqual(stats["num_layers"], 3)
        self.assertEqual(stats["total_neurons"], 35)
        # 10*20+20 + 20*5+5 = 220 + 105 = 325
        self.assertEqual(stats["total_parameters"], 325)
        self.assertEqual(stats["total_connections"], 10*20 + 20*5)

    def test_lenet_preset(self):
        layers = self.engine.preset_lenet()
        self.assertGreater(len(layers), 5)
        self.assertEqual(layers[0].label, "Input")
        self.assertEqual(layers[-1].label, "Output")

    def test_alexnet_preset(self):
        layers = self.engine.preset_alexnet()
        self.assertGreater(len(layers), 8)
        self.assertEqual(layers[0].depth, 3)  # Input RGB

    def test_mlp_preset(self):
        layers = self.engine.preset_mlp([784, 256, 128, 10])
        self.assertEqual(len(layers), 4)
        self.assertEqual(layers[0].num_nodes, 784)
        self.assertEqual(layers[0].label, "Input")
        self.assertEqual(layers[-1].label, "Output")

    def test_lenet_svg_output(self):
        layers = self.engine.preset_lenet()
        svg = self.engine.render_lenet(layers)
        self.assertIn("<svg", svg)
        self.assertIn("<rect", svg)

    def test_alexnet_svg_output(self):
        layers = self.engine.preset_alexnet()
        svg = self.engine.render_alexnet(layers)
        self.assertIn("<svg", svg)
        self.assertIn("<polygon", svg)

    def test_cnn_stats(self):
        layers = self.engine.preset_lenet()
        stats = self.engine.cnn_stats(layers)
        self.assertGreater(stats["total_parameters"], 0)
        self.assertEqual(stats["num_layers"], len(layers))

    def test_cnn_block_positions(self):
        layers = self.engine.preset_lenet()
        blocks = self.engine.get_cnn_block_positions(layers)
        self.assertEqual(len(blocks), len(layers))
        # X positions should be increasing
        for i in range(1, len(blocks)):
            self.assertGreater(blocks[i]["x"], blocks[i-1]["x"])

    def test_svg_element_rendering(self):
        elem = SVGElement("circle", {"cx": "10", "cy": "20", "r": "5"})
        rendered = elem.render()
        self.assertIn("circle", rendered)
        self.assertIn('cx="10"', rendered)

    def test_custom_style(self):
        style = SVGStyle(background_color="#000000", node_fill="#ff0000",
                         layer_spacing=200.0, show_labels=False)
        engine = OmniNNSvgEngine(style=style)
        layers = engine.create_fcnn([3, 3])
        svg = engine.render_fcnn(layers)
        self.assertIn("#000000", svg)

    def test_create_cnn_layer(self):
        layer = self.engine.create_cnn_layer("conv", depth=64, height=32,
                                              width=32, label="Conv1")
        self.assertEqual(layer.layer_type, LayerType.CONV)
        self.assertEqual(layer.depth, 64)


# ==========================================================================
# 2. MMF ENGINE TESTS
# ==========================================================================

class TestMMFEngine(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.engine = OmniMMFEngine(
            img_feat_dim=128,
            embed_dim=64,
            vocab_size=1000,
            num_answers=100,
            max_seq_len=32,
            num_regions=9,
            fusion_type="concat",
        )

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["engine_id"], "omni-mmf")
        self.assertEqual(d["status"], "operational")
        self.assertIn("vqa", d["tasks"])
        self.assertIn("captioning", d["tasks"])

    def test_registry_register_and_get(self):
        result = self.engine.register_component("model", "my_model", {"type": "test"})
        self.assertIsInstance(result, Ok)
        get_result = self.engine.get_component("model", "my_model")
        self.assertIsInstance(get_result, Ok)
        self.assertEqual(get_result.value["type"], "test")

    def test_registry_not_found(self):
        result = self.engine.get_component("model", "nonexistent")
        self.assertIsInstance(result, Err)

    def test_registry_invalid_category(self):
        result = self.engine.register_component("invalid_cat", "test", {})
        self.assertIsInstance(result, Err)

    def test_registry_list(self):
        self.engine.register_component("model", "m1", {})
        self.engine.register_component("model", "m2", {})
        models = self.engine.registry.list_registered("model")
        self.assertIn("m1", models)
        self.assertIn("m2", models)

    def test_image_encoder(self):
        features = np.random.randn(2, 9, 128).astype(np.float32)
        encoded = self.engine.encode_image(features)
        self.assertEqual(encoded.shape, (2, 64))

    def test_text_encoder(self):
        tokens = np.random.randint(0, 1000, (2, 32))
        encoded = self.engine.encode_text(tokens)
        self.assertEqual(encoded.shape, (2, 64))

    def test_text_tokenizer(self):
        tokens = self.engine.tokenizer.tokenize("hello world")
        self.assertEqual(len(tokens), 32)  # max_seq_len
        self.assertEqual(tokens[0], 2)  # BOS token

    def test_image_preprocessor(self):
        image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        normalized = self.engine.image_preprocessor.normalize(image)
        self.assertTrue(np.any(normalized < 0))  # Mean-subtracted

    def test_image_feature_extraction(self):
        image = np.random.randn(64, 64, 3).astype(np.float32)
        features = self.engine.image_preprocessor.extract_features(image)
        self.assertEqual(features.shape[0], 9)  # num_regions
        self.assertEqual(features.shape[1], 128)  # feat_dim

    def test_concat_fusion(self):
        img = np.random.randn(2, 64).astype(np.float32)
        txt = np.random.randn(2, 64).astype(np.float32)
        fused = ConcatFusion().fuse(img, txt)
        self.assertEqual(fused.shape, (2, 128))

    def test_element_wise_fusion(self):
        img = np.random.randn(2, 64).astype(np.float32)
        txt = np.random.randn(2, 64).astype(np.float32)
        fused = ElementWiseFusion(64).fuse(img, txt)
        self.assertEqual(fused.shape, (2, 64))

    def test_bilinear_fusion(self):
        img = np.random.randn(2, 64).astype(np.float32)
        txt = np.random.randn(2, 64).astype(np.float32)
        fused = BilinearFusion(64, 64, 64, rank=16).fuse(img, txt)
        self.assertEqual(fused.shape, (2, 64))

    def test_attention_fusion(self):
        query = np.random.randn(2, 4, 64).astype(np.float32)
        context = np.random.randn(2, 9, 64).astype(np.float32)
        fused = AttentionFusion(64, 8).fuse(query, context)
        self.assertEqual(fused.shape, (2, 4, 64))

    def test_vqa_head(self):
        features = np.random.randn(2, 128).astype(np.float32)
        head = VQAHead(128, 100)
        logits = head.forward(features)
        self.assertEqual(logits.shape, (2, 100))

    def test_caption_head(self):
        features = np.random.randn(2, 64).astype(np.float32)
        head = CaptionHead(64, 1000, max_caption_len=10)
        tokens = head.generate(features)
        self.assertEqual(tokens.shape, (2, 10))
        self.assertTrue(np.all(tokens >= 0))
        self.assertTrue(np.all(tokens < 1000))

    def test_vqa_pipeline(self):
        img_feat = np.random.randn(2, 9, 128).astype(np.float32)
        txt_tokens = np.random.randint(0, 1000, (2, 32))
        logits = self.engine.vqa_predict(img_feat, txt_tokens)
        self.assertEqual(logits.shape, (2, 100))

    def test_caption_pipeline(self):
        img_feat = np.random.randn(2, 9, 128).astype(np.float32)
        tokens = self.engine.caption_predict(img_feat)
        self.assertEqual(tokens.shape[0], 2)

    def test_vqa_accuracy_metric(self):
        preds = np.array([[0.1, 0.9, 0.0], [0.8, 0.1, 0.1]])
        targets = np.array([1, 0])
        acc = vqa_accuracy(preds, targets)
        self.assertEqual(acc, 1.0)

    def test_bleu_score(self):
        ref = np.array([1, 2, 3, 4, 5, 6])
        hyp = np.array([1, 2, 3, 4, 5, 6])
        score = bleu_score(ref, hyp)
        self.assertGreater(score, 0.5)

    def test_cider_score(self):
        ref = np.array([1, 2, 3, 4, 5, 6, 7, 8])
        hyp = np.array([1, 2, 3, 4, 5, 6, 7, 8])
        score = cider_score_approx(ref, hyp)
        self.assertGreater(score, 0.0)

    def test_sample_creation(self):
        image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        sample = self.engine.create_sample(image=image, text="test", sample_id="s1")
        self.assertTrue(sample.has_image())
        self.assertTrue(sample.has_text())
        self.assertEqual(sample.id, "s1")

    def test_sample_list(self):
        s1 = Sample(text_tokens=np.array([1, 2, 3]))
        s2 = Sample(text_tokens=np.array([4, 5, 6, 7]))
        sl = SampleList([s1, s2])
        self.assertEqual(sl.batch_size, 2)
        tokens = sl.get_text_tokens()
        self.assertEqual(tokens.shape, (2, 4))  # Padded to max

    def test_softmax_properties(self):
        x = np.random.randn(3, 10).astype(np.float32)
        p = softmax(x)
        np.testing.assert_allclose(np.sum(p, axis=-1), np.ones(3), atol=1e-5)

    def test_cross_entropy(self):
        logits = np.array([[2.0, 1.0, 0.1]], dtype=np.float32)
        targets = np.array([0])
        loss = cross_entropy(logits, targets)
        self.assertGreater(loss, 0.0)

    def test_binary_cross_entropy(self):
        logits = np.array([[0.0, 0.0]], dtype=np.float32)
        targets = np.array([[1.0, 0.0]], dtype=np.float32)
        loss = binary_cross_entropy(logits, targets)
        self.assertGreater(loss, 0.0)


# ==========================================================================
# 3. DEEPLABCUT ENGINE TESTS
# ==========================================================================

class TestDeepLabCutEngine(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.engine = OmniDeepLabCutEngine()

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["engine_id"], "omni-deeplabcut")
        self.assertEqual(d["status"], "operational")
        self.assertIn("mouse", d["presets"])

    def test_mouse_skeleton(self):
        skel = self.engine.preset_mouse()
        self.assertEqual(skel.name, "mouse")
        self.assertIn("snout", skel.keypoints)
        self.assertGreater(skel.num_joints, 10)
        self.assertGreater(skel.num_limbs, 5)

    def test_human_skeleton(self):
        skel = self.engine.preset_human()
        self.assertEqual(skel.name, "human_coco")
        self.assertEqual(skel.num_joints, 17)

    def test_custom_skeleton(self):
        skel = self.engine.create_skeleton(
            "ant", ["head", "thorax", "abdomen"],
            [("head", "thorax"), ("thorax", "abdomen")]
        )
        self.assertEqual(skel.num_joints, 3)
        self.assertEqual(skel.num_limbs, 2)

    def test_keypoint_properties(self):
        kp = Keypoint("nose", 10.5, 20.3, 0.95)
        self.assertEqual(kp.position, (10.5, 20.3))
        self.assertEqual(kp.name, "nose")

    def test_heatmap_generation(self):
        keypoints = [
            Keypoint("a", 16.0, 16.0, 1.0),
            Keypoint("b", 48.0, 48.0, 1.0),
        ]
        heatmaps = self.engine.generate_heatmaps(keypoints, height=64, width=64)
        self.assertEqual(heatmaps.shape, (2, 64, 64))
        # Peak should be near keypoint location
        peak_y, peak_x = np.unravel_index(np.argmax(heatmaps[0]), (64, 64))
        self.assertAlmostEqual(peak_y, 16, delta=2)
        self.assertAlmostEqual(peak_x, 16, delta=2)

    def test_keypoint_detection_from_heatmaps(self):
        keypoints = [Keypoint("nose", 30.0, 25.0, 1.0)]
        heatmaps = generate_heatmap(keypoints, 64, 64, sigma=5.0)
        detected = detect_keypoints_from_heatmaps(heatmaps, ["nose"], threshold=0.1)
        self.assertEqual(len(detected), 1)
        self.assertAlmostEqual(detected[0].x, 30.0, delta=3)
        self.assertAlmostEqual(detected[0].y, 25.0, delta=3)

    def test_paf_generation(self):
        kp_a = Keypoint("a", 10.0, 10.0, 1.0)
        kp_b = Keypoint("b", 50.0, 10.0, 1.0)
        pafs = generate_paf([(kp_a, kp_b)], 64, 64, sigma=5.0)
        self.assertEqual(pafs.shape[0], 2)  # x and y components
        # PAF along the limb should have positive x component
        self.assertGreater(np.max(pafs[0]), 0)

    def test_paf_scoring(self):
        kp_a = Keypoint("a", 10.0, 32.0, 1.0)
        kp_b = Keypoint("b", 50.0, 32.0, 1.0)
        pafs = generate_paf([(kp_a, kp_b)], 64, 64, sigma=5.0)
        score = score_paf_connection(pafs[0], pafs[1], kp_a, kp_b)
        self.assertGreater(score, 0)

    def test_pose_creation(self):
        pose = Pose(
            keypoints={
                "nose": Keypoint("nose", 10, 20, 0.9),
                "eye": Keypoint("eye", 15, 18, 0.8),
            },
            instance_id=0,
        )
        self.assertEqual(pose.num_detected, 2)
        self.assertIsNotNone(pose.get_keypoint("nose"))
        self.assertIsNone(pose.get_keypoint("tail"))

    def test_pose_to_array(self):
        pose = Pose(keypoints={
            "a": Keypoint("a", 10, 20, 0.9),
            "b": Keypoint("b", 30, 40, 0.8),
        })
        arr = pose.to_array(["a", "b", "c"])
        self.assertEqual(arr.shape, (3, 3))
        self.assertAlmostEqual(arr[0, 0], 10.0)
        self.assertAlmostEqual(arr[2, 2], 0.0)  # Missing keypoint

    def test_kalman_tracker(self):
        kf = KalmanTracker((10.0, 20.0))
        predicted = kf.predict()
        self.assertEqual(len(predicted), 2)
        updated = kf.update((12.0, 22.0))
        self.assertAlmostEqual(updated[0], 12.0, delta=5)

    def test_multi_animal_tracker(self):
        tracker = MultiAnimalTracker()

        # Frame 0: two animals
        poses_0 = [
            Pose(keypoints={"nose": Keypoint("nose", 10, 10, 0.9)}, instance_id=0),
            Pose(keypoints={"nose": Keypoint("nose", 50, 50, 0.9)}, instance_id=1),
        ]
        active = tracker.update(poses_0, 0)
        self.assertEqual(len(active), 2)

        # Frame 1: same animals moved slightly
        poses_1 = [
            Pose(keypoints={"nose": Keypoint("nose", 12, 11, 0.9)}),
            Pose(keypoints={"nose": Keypoint("nose", 52, 51, 0.9)}),
        ]
        active = tracker.update(poses_1, 1)
        self.assertEqual(len(active), 2)

    def test_velocity_computation(self):
        trajectory = np.array([[0, 0], [1, 0], [2, 0], [3, 0]], dtype=np.float32)
        vel = compute_velocity(trajectory, fps=1.0)
        self.assertEqual(len(vel), 3)
        np.testing.assert_allclose(vel, [1.0, 1.0, 1.0], atol=1e-5)

    def test_acceleration_computation(self):
        trajectory = np.array([[0, 0], [1, 0], [3, 0], [6, 0]], dtype=np.float32)
        acc = compute_acceleration(trajectory, fps=1.0)
        self.assertEqual(len(acc), 2)

    def test_joint_angle(self):
        # 90-degree angle
        kp_a = Keypoint("a", 0, 0, 1.0)
        kp_vertex = Keypoint("v", 0, 10, 1.0)
        kp_b = Keypoint("b", 10, 10, 1.0)
        angle = compute_joint_angle(kp_a, kp_vertex, kp_b)
        self.assertAlmostEqual(angle, 90.0, delta=1.0)

    def test_joint_angle_straight(self):
        kp_a = Keypoint("a", 0, 0, 1.0)
        kp_vertex = Keypoint("v", 5, 0, 1.0)
        kp_b = Keypoint("b", 10, 0, 1.0)
        angle = compute_joint_angle(kp_a, kp_vertex, kp_b)
        self.assertAlmostEqual(angle, 180.0, delta=1.0)

    def test_distance_between_keypoints(self):
        kp_a = Keypoint("a", 0, 0, 1.0)
        kp_b = Keypoint("b", 3, 4, 1.0)
        dist = compute_distance_between_keypoints(kp_a, kp_b)
        self.assertAlmostEqual(dist, 5.0, places=4)

    def test_behavior_classification(self):
        self.assertEqual(classify_behavior(0.5, 0.0), "resting")
        self.assertEqual(classify_behavior(8.0, 0.0), "walking")
        self.assertEqual(classify_behavior(30.0, 0.5), "running")
        self.assertEqual(classify_behavior(30.0, 50.0), "turning")

    def test_augment_keypoints_flip(self):
        keypoints = [Keypoint("a", 10, 20, 1.0)]
        augmented = augment_keypoints(keypoints, (256, 256), flip_horizontal=True)
        self.assertAlmostEqual(augmented[0].x, 246.0, delta=1.0)

    def test_augment_keypoints_scale(self):
        keypoints = [Keypoint("a", 128, 128, 1.0)]
        augmented = augment_keypoints(keypoints, (256, 256), scale=2.0)
        # Center point should stay at center
        self.assertAlmostEqual(augmented[0].x, 128.0, delta=1.0)

    def test_full_pipeline(self):
        skel = self.engine.preset_mouse()
        keypoints = [
            Keypoint(name, float(i * 5), float(i * 3), 0.9)
            for i, name in enumerate(skel.keypoints)
        ]
        heatmaps = self.engine.generate_heatmaps(keypoints, 64, 64)
        result = self.engine.predict_single_frame(heatmaps, frame_idx=0)
        self.assertIn("keypoints", result)
        self.assertIn("poses", result)

    def test_track_trajectory(self):
        pose = Pose(keypoints={"nose": Keypoint("nose", 10, 20, 0.9)})
        track = Track(track_id=0, poses=[(0, pose)])
        traj = track.trajectory("nose")
        self.assertEqual(traj.shape, (1, 2))


# ==========================================================================
# 4. COMPOSER ENGINE TESTS
# ==========================================================================

class TestComposerEngine(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.engine = OmniComposerEngine(
            base_lr=0.1, max_epochs=10, scheduler_type="cosine"
        )

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["engine_id"], "omni-composer")
        self.assertEqual(d["status"], "operational")
        self.assertIn("MixUp", d["algorithms"])
        self.assertIn("EMA", d["optimizations"])

    def test_mixup_shapes(self):
        images = np.random.randn(8, 32, 32, 3).astype(np.float32)
        labels = np.eye(10)[np.random.randint(0, 10, 8)]
        mixed_img, mixed_lbl = self.engine.apply_mixup(images, labels, alpha=0.2)
        self.assertEqual(mixed_img.shape, images.shape)
        self.assertEqual(mixed_lbl.shape, labels.shape)

    def test_mixup_interpolation(self):
        images = np.ones((2, 4, 4, 3), dtype=np.float32)
        labels = np.array([[1, 0], [0, 1]], dtype=np.float32)
        mixed_img, mixed_lbl = mixup(images, labels, alpha=0.2)
        # Mixed labels should sum to 1 per sample
        np.testing.assert_allclose(np.sum(mixed_lbl, axis=-1), np.ones(2), atol=1e-5)

    def test_cutmix_shapes(self):
        images = np.random.randn(4, 32, 32, 3).astype(np.float32)
        labels = np.eye(5)[np.random.randint(0, 5, 4)]
        cut_img, cut_lbl = self.engine.apply_cutmix(images, labels)
        self.assertEqual(cut_img.shape, images.shape)
        self.assertEqual(cut_lbl.shape, labels.shape)

    def test_cutout_creates_holes(self):
        images = np.ones((2, 32, 32, 3), dtype=np.float32)
        result = self.engine.apply_cutout(images, num_holes=1, hole_size=8)
        # Should have some zeros
        self.assertTrue(np.any(result == 0))

    def test_label_smoothing(self):
        labels = np.array([0, 1, 2])
        smoothed = self.engine.apply_label_smoothing(labels, num_classes=3, smoothing=0.1)
        self.assertEqual(smoothed.shape, (3, 3))
        # Max should be less than 1
        self.assertLess(np.max(smoothed), 1.0)
        # Each row should sum to ~1
        np.testing.assert_allclose(np.sum(smoothed, axis=-1), np.ones(3), atol=1e-5)

    def test_cosine_scheduler(self):
        sched = CosineScheduler(base_lr=0.1, min_lr=0.0)
        lr_start = sched.get_lr(0, 1000)
        lr_mid = sched.get_lr(500, 1000)
        lr_end = sched.get_lr(1000, 1000)
        self.assertAlmostEqual(lr_start, 0.1, places=3)
        self.assertLess(lr_mid, 0.1)
        self.assertAlmostEqual(lr_end, 0.0, delta=0.01)

    def test_warmup_scheduler(self):
        sched = WarmupScheduler(base_lr=0.1, warmup_steps=100)
        self.assertAlmostEqual(sched.get_lr(0, 1000), 0.0, places=5)
        self.assertAlmostEqual(sched.get_lr(50, 1000), 0.05, places=3)
        self.assertAlmostEqual(sched.get_lr(100, 1000), 0.1, places=3)

    def test_linear_scheduler(self):
        sched = LinearScheduler(base_lr=0.1, end_lr=0.01)
        self.assertAlmostEqual(sched.get_lr(0, 100), 0.1, places=3)
        self.assertAlmostEqual(sched.get_lr(100, 100), 0.01, places=3)

    def test_step_scheduler(self):
        sched = StepScheduler(base_lr=0.1, milestones=[30, 60], gamma=0.1)
        self.assertAlmostEqual(sched.get_lr(0, 100), 0.1)
        self.assertAlmostEqual(sched.get_lr(30, 100), 0.01)
        self.assertAlmostEqual(sched.get_lr(60, 100), 0.001)

    def test_polynomial_scheduler(self):
        sched = PolynomialScheduler(base_lr=0.1, power=2.0, end_lr=0.0)
        lr = sched.get_lr(50, 100)
        self.assertGreater(lr, 0)
        self.assertLess(lr, 0.1)

    def test_lr_schedule_generation(self):
        schedule = self.engine.create_lr_schedule(100)
        self.assertEqual(len(schedule), 100)
        self.assertGreater(schedule[0], schedule[-1])  # Cosine decays

    def test_gradient_clip_norm(self):
        grads = [np.ones((10, 10)) * 5.0]
        clipped, norm = self.engine.clip_gradients_norm(grads, max_norm=1.0)
        new_norm = math.sqrt(sum(float(np.sum(g**2)) for g in clipped))
        self.assertAlmostEqual(new_norm, 1.0, delta=0.1)

    def test_gradient_clip_value(self):
        grads = [np.ones((5,)) * 3.0]
        clipped = self.engine.clip_gradients_value(grads, clip_value=1.0)
        self.assertTrue(np.all(clipped[0] <= 1.0))

    def test_ema(self):
        params = {"w1": np.ones((3, 3)) * 10.0}
        self.engine.ema_register(params)
        new_params = {"w1": np.ones((3, 3)) * 20.0}
        self.engine.ema_update(new_params)
        ema_params = self.engine.ema_apply()
        # EMA should be between 10 and 20
        self.assertTrue(np.all(ema_params["w1"] > 10.0))
        self.assertTrue(np.all(ema_params["w1"] < 20.0))

    def test_sam_perturbation(self):
        params = [np.ones((4, 4))]
        grads = [np.ones((4, 4)) * 0.5]
        perturbed, eps = self.engine.sam_perturb(params, grads, rho=0.05)
        self.assertEqual(len(perturbed), 1)
        # Perturbed should differ from original
        self.assertFalse(np.allclose(perturbed[0], params[0]))

    def test_early_stopping_callback(self):
        cb = EarlyStoppingCallback(patience=2)
        state = TrainingState()
        state.eval_loss_history = [1.0]
        cb.on_epoch_end(state)
        self.assertFalse(state.stop_training)
        state.eval_loss_history.append(1.0)
        cb.on_epoch_end(state)
        state.eval_loss_history.append(1.0)
        cb.on_epoch_end(state)
        self.assertTrue(state.stop_training)

    def test_checkpoint_callback(self):
        cb = CheckpointCallback(save_interval=1)
        state = TrainingState()
        state.timestamp.epoch = 0
        state.train_loss_history = [0.5]
        result = cb.on_epoch_checkpoint(state)
        self.assertIsNotNone(result)
        self.assertEqual(len(cb.checkpoints), 1)

    def test_callback_system(self):
        self.engine.add_callback(LossMonitorCallback())
        self.engine.state.train_loss_history = [0.5]
        results = self.engine.fire_event(Event.BATCH_END)
        self.assertTrue(any(r is not None for r in results))

    def test_metric_tracker(self):
        tracker = MetricTracker()
        tracker.update("loss", 1.0)
        tracker.update("loss", 0.5)
        tracker.update("loss", 0.3)
        self.assertAlmostEqual(tracker.get_mean("loss"), 0.6, places=2)
        self.assertAlmostEqual(tracker.get_last("loss"), 0.3)
        self.assertAlmostEqual(tracker.get_min("loss"), 0.3)

    def test_metric_tracker_summary(self):
        tracker = MetricTracker()
        tracker.update("acc", 0.8)
        tracker.update("acc", 0.9)
        summary = tracker.summary()
        self.assertIn("acc", summary)
        self.assertEqual(summary["acc"]["count"], 2)

    def test_progressive_resize(self):
        images = np.random.randn(2, 224, 224, 3).astype(np.float32)
        # At epoch 0 with total 10, should give small size
        resized = progressive_resize(images, 0, 10, initial_size=64, final_size=224)
        self.assertEqual(resized.shape[1], 64)

    def test_train_step(self):
        images = np.random.randn(4, 8, 8, 3).astype(np.float32)
        labels = np.random.randn(4, 5).astype(np.float32)
        loss = self.engine.train_step(images, labels)
        self.assertGreater(loss, 0.0)
        self.assertEqual(len(self.engine.state.train_loss_history), 1)

    def test_run_epoch(self):
        train_data = [
            (np.random.randn(4, 8, 8, 3).astype(np.float32),
             np.random.randn(4, 5).astype(np.float32))
            for _ in range(3)
        ]
        result = self.engine.run_epoch(train_data)
        self.assertIn("train_loss", result)
        self.assertGreater(result["train_loss"], 0)

    def test_training_state(self):
        state = TrainingState(max_epochs=50)
        state.timestamp.epoch = 5
        state.timestamp.batch = 100
        self.assertEqual(state.current_epoch, 5)
        self.assertEqual(state.current_batch, 100)
        state.log_metric("acc", 0.95)
        self.assertIn("acc", state.metrics)


# ==========================================================================
# 5. SUPIR ENGINE TESTS
# ==========================================================================

class TestSUPIREngine(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        self.engine = OmniSUPIREngine(
            scale_factor=2, num_diffusion_steps=3, num_scales=2, tile_size=32
        )

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["engine_id"], "omni-supir")
        self.assertEqual(d["status"], "operational")
        self.assertIn("PSNR", d["metrics"])
        self.assertIn("gaussian_blur", d["degradations"])

    def test_psnr_perfect(self):
        img = np.random.randn(16, 16).astype(np.float32)
        psnr = self.engine.compute_psnr(img, img)
        self.assertGreater(psnr, 90.0)

    def test_psnr_noisy(self):
        img = np.random.randn(16, 16).astype(np.float32) * 0.5
        noisy = img + np.random.randn(16, 16).astype(np.float32) * 0.1
        psnr = self.engine.compute_psnr(img, noisy)
        self.assertGreater(psnr, 0.0)
        self.assertLess(psnr, 90.0)

    def test_ssim_perfect(self):
        img = np.random.rand(32, 32).astype(np.float32)
        ssim = self.engine.compute_ssim(img, img)
        self.assertGreater(ssim, 0.95)

    def test_ssim_different(self):
        img1 = np.random.rand(32, 32).astype(np.float32)
        img2 = np.random.rand(32, 32).astype(np.float32)
        ssim = self.engine.compute_ssim(img1, img2)
        self.assertLess(ssim, 0.5)

    def test_lpips_approx(self):
        img = np.random.rand(32, 32, 3).astype(np.float32)
        noisy = img + np.random.randn(32, 32, 3).astype(np.float32) * 0.1
        lpips = self.engine.compute_lpips(img, noisy)
        self.assertGreater(lpips, 0.0)

    def test_gaussian_blur(self):
        img = np.random.rand(32, 32, 3).astype(np.float32)
        blurred = self.engine.add_blur(img, sigma=2.0)
        self.assertEqual(blurred.shape, img.shape)
        # Blurred should be smoother (lower variance)
        self.assertLess(np.var(blurred), np.var(img))

    def test_add_noise(self):
        img = np.ones((16, 16, 3), dtype=np.float32) * 0.5
        noisy = self.engine.add_noise(img, sigma=0.1)
        self.assertEqual(noisy.shape, img.shape)
        self.assertFalse(np.allclose(noisy, img))
        self.assertTrue(np.all(noisy >= 0) and np.all(noisy <= 1))

    def test_jpeg_compression(self):
        img = np.random.rand(32, 32, 3).astype(np.float32)
        compressed = self.engine.add_jpeg_artifacts(img, quality=10)
        self.assertEqual(compressed.shape, img.shape)

    def test_downscale(self):
        img = np.random.rand(32, 32, 3).astype(np.float32)
        down = self.engine.downscale(img, factor=4)
        self.assertEqual(down.shape, (8, 8, 3))

    def test_full_degradation_pipeline(self):
        img = np.random.rand(32, 32, 3).astype(np.float32)
        degraded = self.engine.degrade(img)
        self.assertEqual(degraded.shape[0], 32 // self.engine.scale_factor)

    def test_bilinear_upsample(self):
        img = np.random.rand(8, 8, 3).astype(np.float32)
        up = self.engine.upsample_bilinear(img, scale=2)
        self.assertEqual(up.shape, (16, 16, 3))

    def test_nearest_upsample(self):
        img = np.random.rand(8, 8, 3).astype(np.float32)
        up = self.engine.upsample_nearest(img, scale=2)
        self.assertEqual(up.shape, (16, 16, 3))

    def test_bilinear_upsample_2d(self):
        img = np.random.rand(8, 8).astype(np.float32)
        up = bilinear_upsample(img, scale=2)
        self.assertEqual(up.shape, (16, 16))

    def test_channel_attention(self):
        features = np.random.randn(16, 16, 32).astype(np.float32)
        attended = self.engine.apply_channel_attention(features)
        self.assertEqual(attended.shape, features.shape)

    def test_spatial_attention(self):
        features = np.random.randn(16, 16, 32).astype(np.float32)
        attended = self.engine.apply_spatial_attention(features)
        self.assertEqual(attended.shape, features.shape)

    def test_feature_extraction(self):
        img = np.random.rand(32, 32, 3).astype(np.float32)
        features = self.engine.extract_features(img)
        self.assertEqual(len(features), 2)  # num_scales
        self.assertEqual(features[0].shape[:2], (32, 32))

    def test_diffusion_refinement(self):
        img = np.random.rand(16, 16, 3).astype(np.float32) * 0.5
        refined = self.engine.diffusion_refine(img, num_steps=3, noise_strength=0.05)
        self.assertEqual(refined.shape, img.shape)
        self.assertTrue(np.all(refined >= 0) and np.all(refined <= 1))

    def test_color_correction(self):
        restored = np.random.rand(16, 16, 3).astype(np.float32) * 0.3
        reference = np.random.rand(16, 16, 3).astype(np.float32) * 0.7 + 0.15
        corrected = self.engine.color_correct(restored, reference)
        self.assertEqual(corrected.shape, restored.shape)
        # Mean should be closer to reference
        ref_mean = np.mean(reference)
        corr_mean = np.mean(corrected)
        orig_mean = np.mean(restored)
        self.assertLess(abs(corr_mean - ref_mean), abs(orig_mean - ref_mean) + 0.1)

    def test_tone_mapping(self):
        hdr = np.random.rand(16, 16, 3).astype(np.float32) * 5.0
        ldr = self.engine.tone_map(hdr)
        self.assertTrue(np.all(ldr >= 0))
        self.assertTrue(np.all(ldr <= 1))

    def test_tiled_processing(self):
        img = np.random.rand(64, 64, 3).astype(np.float32)
        def identity_fn(tile):
            return tile
        result = self.engine.process_tiled(img, identity_fn)
        self.assertEqual(result.shape, img.shape)

    def test_full_super_resolution(self):
        lr = np.random.rand(8, 8, 3).astype(np.float32)
        sr = self.engine.super_resolve(lr, use_diffusion=True)
        # Should be upscaled
        self.assertGreaterEqual(sr.shape[0], 8 * self.engine.scale_factor - 1)
        self.assertTrue(np.all(sr >= 0) and np.all(sr <= 1))

    def test_evaluate_metrics(self):
        orig = np.random.rand(16, 16, 3).astype(np.float32)
        restored = orig + np.random.randn(16, 16, 3).astype(np.float32) * 0.05
        restored = np.clip(restored, 0, 1)
        metrics = self.engine.evaluate(orig, restored)
        self.assertIn("psnr", metrics)
        self.assertIn("ssim", metrics)
        self.assertIn("lpips", metrics)
        self.assertGreater(metrics["psnr"], 0)

    def test_downscale_2d(self):
        img = np.random.rand(32, 32).astype(np.float32)
        down = downscale(img, scale_factor=4)
        self.assertEqual(down.shape, (8, 8))

    def test_multiscale_feature_decode(self):
        img = np.random.rand(32, 32, 3).astype(np.float32)
        features = self.engine.extract_features(img)
        decoded = self.engine.decode_features(features)
        # Should have same spatial dims as first scale
        self.assertEqual(decoded.shape[0], features[0].shape[0])


if __name__ == '__main__':
    unittest.main()

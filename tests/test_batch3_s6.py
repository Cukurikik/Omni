# -*- coding: utf-8 -*-
"""
OMNI Semester 6 — Batch 3 Test Suite
========================================
Comprehensive tests for all 5 Batch 3 engines:
  1. OmniLayoutParserEngine — Document layout analysis
  2. OmniAiFinanceEngine — Quantitative finance
  3. OmniDaliPipelineEngine — Data augmentation pipeline
  4. OmniMlpackEngine — Classical ML algorithms
  5. OmniDallePytorchEngine — Text-to-image generation
"""

import sys, os, unittest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'compute', 'python_core'))

# ============================================================================
# ENGINE 1: Layout Parser
# ============================================================================
from omni_layout_parser_engine import (
    OmniLayoutParserEngine, Rectangle, Quadrilateral, TextBlock,
    Layout, BlockType, compute_iou, non_maximum_suppression,
)

class TestLayoutParser(unittest.TestCase):

    def setUp(self):
        self.engine = OmniLayoutParserEngine()

    def test_rectangle_properties(self):
        r = Rectangle(10, 20, 110, 120)
        self.assertAlmostEqual(r.width, 100)
        self.assertAlmostEqual(r.height, 100)
        self.assertAlmostEqual(r.area, 10000)
        self.assertEqual(r.center, (60, 70))

    def test_rectangle_intersect(self):
        a = Rectangle(0, 0, 100, 100)
        b = Rectangle(50, 50, 150, 150)
        inter = a.intersect(b)
        self.assertAlmostEqual(inter.area, 2500)

    def test_rectangle_union(self):
        a = Rectangle(0, 0, 50, 50)
        b = Rectangle(25, 25, 75, 75)
        u = a.union(b)
        self.assertEqual(u.coordinates, (0, 0, 75, 75))

    def test_iou_computation(self):
        a = Rectangle(0, 0, 100, 100)
        b = Rectangle(0, 0, 100, 100)
        self.assertAlmostEqual(compute_iou(a, b), 1.0)
        c = Rectangle(200, 200, 300, 300)
        self.assertAlmostEqual(compute_iou(a, c), 0.0)

    def test_iou_partial_overlap(self):
        a = Rectangle(0, 0, 100, 100)
        b = Rectangle(50, 0, 150, 100)
        iou = compute_iou(a, b)
        self.assertGreater(iou, 0.0)
        self.assertLess(iou, 1.0)

    def test_nms(self):
        blocks = [
            TextBlock(Rectangle(0, 0, 100, 100), BlockType.TEXT, 0.9, block_id=0),
            TextBlock(Rectangle(10, 10, 110, 110), BlockType.TEXT, 0.7, block_id=1),
            TextBlock(Rectangle(200, 200, 300, 300), BlockType.TEXT, 0.8, block_id=2),
        ]
        result = non_maximum_suppression(blocks, 0.3)
        self.assertEqual(len(result), 2)  # first two overlap, keep higher score

    def test_textblock_creation(self):
        tb = self.engine.create_textblock(0, 0, 100, 100, "title", 0.95, "Hello")
        self.assertEqual(tb.block_type, BlockType.TITLE)
        self.assertEqual(tb.text, "Hello")
        self.assertAlmostEqual(tb.score, 0.95)

    def test_layout_filter_by_type(self):
        layout = Layout([
            TextBlock(Rectangle(0, 0, 50, 50), BlockType.TEXT, 0.9, block_id=0),
            TextBlock(Rectangle(50, 50, 100, 100), BlockType.TITLE, 0.95, block_id=1),
            TextBlock(Rectangle(100, 100, 150, 150), BlockType.TEXT, 0.85, block_id=2),
        ])
        texts = layout.filter_by_type(BlockType.TEXT)
        self.assertEqual(len(texts), 2)

    def test_layout_sort_reading_order(self):
        layout = Layout([
            TextBlock(Rectangle(100, 0, 200, 50), BlockType.TEXT, 0.9, block_id=1),
            TextBlock(Rectangle(0, 0, 90, 50), BlockType.TEXT, 0.9, block_id=0),
            TextBlock(Rectangle(0, 60, 200, 110), BlockType.TEXT, 0.9, block_id=2),
        ])
        sorted_l = layout.sort_by_position("reading-order")
        ids = [b.block_id for b in sorted_l]
        self.assertEqual(ids, [0, 1, 2])

    def test_layout_export_json(self):
        layout = Layout([
            TextBlock(Rectangle(0, 0, 50, 50), BlockType.TEXT, 0.9, "test", 0),
        ])
        json_str = layout.to_json()
        recovered = Layout.from_json(json_str)
        self.assertEqual(len(recovered), 1)
        self.assertEqual(recovered[0].text, "test")

    def test_layout_export_coco(self):
        layout = Layout([
            TextBlock(Rectangle(10, 20, 110, 120), BlockType.TEXT, 0.9, block_id=0),
        ])
        coco = layout.to_coco(image_id=1, image_width=640, image_height=480)
        self.assertIn("annotations", coco)
        self.assertEqual(len(coco["annotations"]), 1)

    def test_detect_layout(self):
        img = np.random.randint(0, 255, (800, 600, 3), dtype=np.uint8)
        layout = self.engine.detect_layout(img)
        self.assertGreater(len(layout), 0)

    def test_document_analysis(self):
        img = np.random.randint(0, 255, (800, 600, 3), dtype=np.uint8)
        result = self.engine.analyze_document(img)
        self.assertIn("layout", result)
        self.assertIn("statistics", result)

    def test_quadrilateral(self):
        pts = np.array([[0,0],[100,0],[100,100],[0,100]], dtype=np.float64)
        q = Quadrilateral(pts)
        self.assertAlmostEqual(q.area, 10000.0)
        r = q.to_rectangle()
        self.assertAlmostEqual(r.area, 10000.0)

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["status"], "operational")


# ============================================================================
# ENGINE 2: AI Finance
# ============================================================================
from omni_ai_finance_engine import (
    OmniAiFinanceEngine, sma, ema, rsi, macd, bollinger_bands,
    sharpe_ratio, max_drawdown, value_at_risk, kelly_criterion,
    momentum_signal, mean_reversion_signal, Backtester, SignalType,
)

class TestAiFinance(unittest.TestCase):

    def setUp(self):
        self.engine = OmniAiFinanceEngine()
        np.random.seed(42)
        self.prices = 100 + np.cumsum(np.random.randn(252) * 0.5)

    def test_sma(self):
        result = sma(self.prices, 20)
        self.assertEqual(len(result), len(self.prices))
        self.assertFalse(np.isnan(result[-1]))
        self.assertTrue(np.isnan(result[0]))

    def test_ema(self):
        result = ema(self.prices, 12)
        self.assertEqual(len(result), len(self.prices))
        self.assertFalse(np.isnan(result[-1]))

    def test_rsi(self):
        result = rsi(self.prices, 14)
        valid = result[~np.isnan(result)]
        self.assertTrue(np.all(valid >= 0))
        self.assertTrue(np.all(valid <= 100))

    def test_macd(self):
        ml, sl, hist = macd(self.prices)
        self.assertEqual(len(ml), len(self.prices))

    def test_bollinger_bands(self):
        upper, mid, lower = bollinger_bands(self.prices, 20)
        valid_idx = ~np.isnan(upper)
        self.assertTrue(np.all(upper[valid_idx] >= mid[valid_idx]))
        self.assertTrue(np.all(lower[valid_idx] <= mid[valid_idx]))

    def test_sharpe_ratio(self):
        returns = np.diff(self.prices) / self.prices[:-1]
        sr = sharpe_ratio(returns)
        self.assertIsInstance(sr, float)

    def test_max_drawdown(self):
        mdd = max_drawdown(self.prices)
        self.assertLessEqual(mdd, 0)

    def test_var(self):
        returns = np.diff(self.prices) / self.prices[:-1]
        var = value_at_risk(returns, 0.95)
        self.assertIsInstance(var, float)

    def test_kelly_criterion(self):
        k = kelly_criterion(0.6, 2.0)
        self.assertGreater(k, 0)
        self.assertLessEqual(k, 1.0)

    def test_momentum_signals(self):
        signals = momentum_signal(self.prices, 20)
        self.assertGreater(len(signals), 0)
        self.assertIn(signals[0].signal, [SignalType.BUY, SignalType.SELL, SignalType.HOLD])

    def test_mean_reversion_signals(self):
        signals = mean_reversion_signal(self.prices, 20)
        self.assertGreater(len(signals), 0)

    def test_portfolio_equal_weight(self):
        w = self.engine.equal_weight(5)
        self.assertAlmostEqual(np.sum(w), 1.0)

    def test_min_variance(self):
        returns = np.random.randn(100, 3)
        cov = np.cov(returns.T)
        w = self.engine.min_variance(cov)
        self.assertAlmostEqual(np.sum(w), 1.0, places=1)

    def test_backtester(self):
        signals = momentum_signal(self.prices, 20)
        bt = Backtester(initial_capital=100000)
        result = bt.run(self.prices, signals)
        self.assertIsInstance(result.total_return, float)
        self.assertEqual(len(result.equity_curve), len(self.prices))

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["status"], "operational")


# ============================================================================
# ENGINE 3: DALI Pipeline
# ============================================================================
from omni_dali_pipeline_engine import (
    OmniDaliPipelineEngine, Pipeline, PipelineBuilder, DALIIterator,
    DALITensor, Resize, Normalize, HorizontalFlip, CenterCrop,
    DeviceType,
)

class TestDaliPipeline(unittest.TestCase):

    def setUp(self):
        self.engine = OmniDaliPipelineEngine()

    def test_pipeline_build_and_run(self):
        pipe = (PipelineBuilder(batch_size=4)
                .read(image_size=64)
                .resize(32, 32)
                .horizontal_flip()
                .normalize()
                .build())
        batch = pipe.run()
        self.assertEqual(batch.shape[0], 4)
        self.assertEqual(batch.shape[1], 32)
        self.assertEqual(batch.shape[2], 32)

    def test_resize_operator(self):
        images = np.random.randint(0, 255, (2, 64, 64, 3), dtype=np.uint8)
        tensor = DALITensor(images)
        op = Resize(32, 32)
        result = op(tensor)
        self.assertEqual(result.shape, (2, 32, 32, 3))

    def test_center_crop(self):
        images = np.random.randint(0, 255, (2, 64, 64, 3), dtype=np.uint8)
        tensor = DALITensor(images)
        op = CenterCrop(32, 32)
        result = op(tensor)
        self.assertEqual(result.shape, (2, 32, 32, 3))

    def test_normalize(self):
        images = np.random.randint(0, 255, (2, 32, 32, 3), dtype=np.uint8)
        tensor = DALITensor(images)
        op = Normalize()
        result = op(tensor)
        self.assertTrue(result.dtype == np.float32)

    def test_horizontal_flip(self):
        images = np.random.randint(0, 255, (4, 16, 16, 3), dtype=np.uint8)
        tensor = DALITensor(images)
        np.random.seed(0)
        op = HorizontalFlip(1.0)  # Always flip
        result = op(tensor)
        self.assertEqual(result.shape, images.shape)

    def test_layout_conversion_nhwc_nchw(self):
        data = np.random.randn(2, 32, 32, 3).astype(np.float32)
        nchw = self.engine.nhwc_to_nchw(data)
        self.assertEqual(nchw.shape, (2, 3, 32, 32))
        nhwc = self.engine.nchw_to_nhwc(nchw)
        self.assertEqual(nhwc.shape, (2, 32, 32, 3))

    def test_iterator(self):
        pipe = PipelineBuilder(batch_size=2).read(image_size=32).normalize().build()
        it = DALIIterator(pipe, num_batches=5)
        batches = list(it)
        self.assertEqual(len(batches), 5)
        self.assertEqual(batches[0].shape[0], 2)

    def test_pipeline_prefetch(self):
        pipe = Pipeline(batch_size=2, prefetch_depth=3)
        pipe.set_reader(__import__('omni_dali_pipeline_engine').FileReader(2, 16, 3))
        pipe.add_op(Normalize())
        pipe.build()
        self.assertEqual(len(pipe._prefetch_queue), 3)
        batch = pipe.run()
        self.assertEqual(len(pipe._prefetch_queue), 3)

    def test_augment_batch(self):
        images = np.random.randint(0, 255, (4, 32, 32, 3), dtype=np.uint8)
        result = self.engine.augment_batch(images, ["hflip", "normalize"])
        self.assertEqual(result.shape[0], 4)

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["status"], "operational")
        self.assertIn("Resize", d["operators"])


# ============================================================================
# ENGINE 4: mlpack
# ============================================================================
from omni_mlpack_engine import (
    OmniMlpackEngine, KNNClassifier, DecisionTreeClassifier,
    DecisionTreeRegressor, RandomForestClassifier, LinearRegression,
    GaussianNaiveBayes, KMeans, PCA,
)

class TestMlpack(unittest.TestCase):

    def setUp(self):
        self.engine = OmniMlpackEngine()
        np.random.seed(42)

    def test_knn_fit_predict(self):
        X = np.random.randn(50, 4)
        y = (X[:, 0] > 0).astype(int)
        knn = self.engine.knn(k=3)
        knn.fit(X, y)
        preds = knn.predict(X[:5])
        self.assertEqual(len(preds), 5)
        score = knn.score(X, y)
        self.assertGreater(score, 0.5)

    def test_knn_neighbors(self):
        X = np.random.randn(20, 3)
        y = np.zeros(20, dtype=int)
        knn = KNNClassifier(k=3).fit(X, y)
        dists, indices = knn.kneighbors(X[:2])
        self.assertEqual(dists.shape, (2, 3))
        self.assertEqual(indices.shape, (2, 3))

    def test_decision_tree_classifier(self):
        X = np.random.randn(100, 4)
        y = (X[:, 0] + X[:, 1] > 0).astype(int)
        dt = self.engine.decision_tree(max_depth=5)
        dt.fit(X, y)
        score = dt.score(X, y)
        self.assertGreater(score, 0.7)

    def test_decision_tree_entropy(self):
        X = np.random.randn(80, 3)
        y = (X[:, 0] > 0).astype(int)
        dt = DecisionTreeClassifier(max_depth=4, criterion="entropy")
        dt.fit(X, y)
        self.assertGreater(dt.score(X, y), 0.6)

    def test_decision_tree_regressor(self):
        X = np.random.randn(80, 3)
        y = X[:, 0] * 2 + X[:, 1] + np.random.randn(80) * 0.1
        reg = self.engine.decision_tree_regressor(max_depth=6)
        reg.fit(X, y)
        r2 = reg.score(X, y)
        self.assertGreater(r2, 0.5)

    def test_random_forest(self):
        X = np.random.randn(100, 5)
        y = (X[:, 0] + X[:, 1] > 0).astype(int)
        rf = self.engine.random_forest(n_estimators=5, max_depth=5)
        rf.fit(X, y)
        score = rf.score(X, y)
        self.assertGreater(score, 0.6)

    def test_linear_regression(self):
        X = np.random.randn(50, 3)
        y = X @ np.array([1.0, 2.0, 3.0]) + 0.5
        lr = self.engine.linear_regression()
        lr.fit(X, y)
        r2 = lr.score(X, y)
        self.assertGreater(r2, 0.99)

    def test_ridge_regression(self):
        X = np.random.randn(50, 3)
        y = X @ np.array([1.0, 2.0, 3.0]) + np.random.randn(50) * 0.1
        lr = self.engine.linear_regression(alpha=1.0)
        lr.fit(X, y)
        r2 = lr.score(X, y)
        self.assertGreater(r2, 0.9)

    def test_naive_bayes(self):
        X = np.random.randn(80, 4)
        y = (X[:, 0] > 0).astype(int)
        nb = self.engine.naive_bayes()
        nb.fit(X, y)
        score = nb.score(X, y)
        self.assertGreater(score, 0.6)

    def test_naive_bayes_proba(self):
        X = np.random.randn(30, 3)
        y = (X[:, 0] > 0).astype(int)
        nb = GaussianNaiveBayes().fit(X, y)
        proba = nb.predict_proba(X[:5])
        self.assertEqual(proba.shape[0], 5)
        np.testing.assert_allclose(proba.sum(axis=1), 1.0, atol=0.01)

    def test_kmeans(self):
        X = np.vstack([
            np.random.randn(30, 2) + [3, 3],
            np.random.randn(30, 2) + [-3, -3],
            np.random.randn(30, 2) + [3, -3],
        ])
        km = self.engine.kmeans(n_clusters=3)
        km.fit(X)
        self.assertEqual(len(np.unique(km.labels)), 3)
        self.assertGreater(km.inertia, 0)

    def test_pca(self):
        X = np.random.randn(50, 5)
        pca = self.engine.pca(n_components=2)
        pca.fit(X)
        X_reduced = pca.transform(X)
        self.assertEqual(X_reduced.shape, (50, 2))
        X_recon = pca.inverse_transform(X_reduced)
        self.assertEqual(X_recon.shape, (50, 5))

    def test_pca_variance_ratio(self):
        X = np.random.randn(100, 4)
        pca = PCA(n_components=3).fit(X)
        self.assertEqual(len(pca.explained_variance_ratio), 3)
        self.assertGreater(pca.explained_variance_ratio[0], 0)

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["status"], "operational")
        self.assertIn("KNN", d["algorithms"])


# ============================================================================
# ENGINE 5: DALLE-Pytorch
# ============================================================================
from omni_dalle_pytorch_engine import (
    OmniDallePytorchEngine, DiscreteVAE, Codebook,
    AutoregressiveTransformer, CLIPReranker,
    gumbel_sample, top_k_filter, softmax, layer_norm,
)

class TestDallePytorch(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)
        self.engine = OmniDallePytorchEngine(
            image_size=16, num_image_tokens=64,
            codebook_dim=32, num_text_tokens=64,
            text_seq_len=8, transformer_dim=64,
            transformer_depth=2, transformer_heads=4,
        )

    def test_codebook_encode_decode(self):
        cb = Codebook(num_tokens=64, codebook_dim=32)
        z = np.random.randn(2, 16, 32).astype(np.float32)
        indices = cb.encode(z)
        self.assertEqual(indices.shape, (2, 16))
        z_q = cb.decode(indices)
        self.assertEqual(z_q.shape, (2, 16, 32))

    def test_gumbel_quantize(self):
        cb = Codebook(num_tokens=64, codebook_dim=32)
        logits = np.random.randn(2, 16, 64).astype(np.float32)
        quantized, indices = cb.gumbel_quantize(logits, 1.0)
        self.assertEqual(quantized.shape, (2, 16, 32))
        self.assertEqual(indices.shape, (2, 16))

    def test_vae_encode_decode(self):
        vae = DiscreteVAE(image_size=16, num_tokens=64, codebook_dim=32, num_layers=2)
        images = np.random.randn(2, 3, 16, 16).astype(np.float32)
        indices = vae.encode(images)
        self.assertEqual(indices.shape[0], 2)
        recon = vae.decode(indices)
        self.assertEqual(recon.shape[0], 2)
        self.assertEqual(recon.shape[1], 3)

    def test_vae_reconstruction_loss(self):
        vae = DiscreteVAE(image_size=16, num_tokens=64, codebook_dim=32, num_layers=2)
        images = np.random.randn(2, 3, 16, 16).astype(np.float32)
        loss = vae.reconstruction_loss(images)
        self.assertIsInstance(loss, float)
        self.assertGreater(loss, 0)

    def test_softmax(self):
        x = np.array([[1, 2, 3], [1, 1, 1]], dtype=np.float32)
        result = softmax(x)
        np.testing.assert_allclose(result.sum(axis=1), [1.0, 1.0], atol=1e-5)

    def test_top_k_filter(self):
        logits = np.array([[0.1, 0.5, 0.3, 0.9, 0.2]], dtype=np.float32)
        filtered = top_k_filter(logits, 2)
        non_inf = filtered[filtered > -1e8]
        self.assertEqual(len(non_inf), 2)

    def test_layer_norm(self):
        x = np.random.randn(2, 5).astype(np.float32)
        normed = layer_norm(x)
        np.testing.assert_allclose(normed.mean(axis=-1), [0, 0], atol=1e-5)

    def test_transformer_forward(self):
        tf = AutoregressiveTransformer(
            dim=64, depth=2, n_heads=4,
            num_text_tokens=64, num_image_tokens=64,
            text_seq_len=8, image_seq_len=16,
        )
        text = np.random.randint(0, 64, (2, 8))
        logits = tf.forward(text)
        self.assertEqual(logits.shape, (2, 8, 128))

    def test_transformer_with_image(self):
        tf = AutoregressiveTransformer(
            dim=64, depth=2, n_heads=4,
            num_text_tokens=64, num_image_tokens=64,
            text_seq_len=8, image_seq_len=16,
        )
        text = np.random.randint(0, 64, (2, 8))
        img = np.random.randint(0, 64, (2, 16))
        logits = tf.forward(text, img)
        self.assertEqual(logits.shape, (2, 24, 128))

    def test_generate_image_tokens(self):
        text = np.random.randint(0, 64, (1, 8))
        tokens = self.engine.transformer.generate_image_tokens(text, temperature=1.0, top_k_val=32)
        self.assertEqual(tokens.shape[0], 1)
        self.assertEqual(tokens.shape[1], self.engine.vae.seq_len)

    def test_clip_reranker(self):
        reranker = CLIPReranker(text_dim=64, image_dim=64, latent_dim=32)
        text = np.random.randn(1, 64).astype(np.float32)
        images = np.random.randn(5, 64).astype(np.float32)
        ranking = reranker.rerank(text, images)
        self.assertEqual(len(ranking), 5)
        self.assertEqual(set(ranking.tolist()), {0, 1, 2, 3, 4})

    def test_full_generate(self):
        text = np.random.randint(0, 64, (1, 8))
        images = self.engine.generate(text, temperature=1.0, top_k=32)
        self.assertEqual(images.shape[0], 1)
        self.assertEqual(images.shape[1], 3)

    def test_compute_loss(self):
        text = np.random.randint(0, 64, (2, 8))
        img = np.random.randint(0, 64, (2, self.engine.vae.seq_len))
        loss = self.engine.compute_loss(text, img)
        self.assertIsInstance(loss, float)
        self.assertGreater(loss, 0)

    def test_diagnostics(self):
        d = self.engine.diagnostics()
        self.assertEqual(d["status"], "operational")
        self.assertIn("DiscreteVAE", d["components"])


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    unittest.main(verbosity=2)

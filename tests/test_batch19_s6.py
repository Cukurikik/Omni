import unittest
import numpy as np

from src.compute.python_core.omni_sports_cv_engine import OmniSportsCVEngine
from src.compute.python_core.omni_rl_qtable_engine import OmniRLQTableEngine
from src.compute.python_core.omni_muzic_transformer_engine import OmniMuzicTransformerEngine
from src.compute.python_core.omni_openprompt_engine import OmniOpenPromptEngine
from src.compute.python_core.omni_telegram_graph_engine import OmniTelegramGraphEngine

class TestBatch19Semester6(unittest.TestCase):
    def setUp(self):
        self.cv = OmniSportsCVEngine()
        self.rl = OmniRLQTableEngine(num_states=5, num_actions=2)
        self.muzic = OmniMuzicTransformerEngine()
        self.prompt = OmniOpenPromptEngine()
        self.graph = OmniTelegramGraphEngine(max_nodes=100)

    def test_sports_cv_tracking(self):
        """Validating Euclidean limits tracking object positions natively structurally perfectly."""
        # 3 frames, [x,y] points
        centroids = np.array([[0, 0], [3, 4], [3, 8]]) 
        res = self.cv.track_velocity(centroids, fps=30)
        
        self.assertEqual(res.__class__.__name__, "Ok")
        velocities = res.value
        
        # d1: sqrt(3^2 + 4^2) = 5 -> vel 150
        # d2: sqrt(0^2 + 4^2) = 4 -> vel 120
        self.assertEqual(len(velocities), 2)
        self.assertAlmostEqual(velocities[0], 150.0)
        self.assertAlmostEqual(velocities[1], 120.0)

    def test_rl_qtable_updates(self):
        """evaluates_structurally native RL arrays mapping correctly Bellman bounds updating correctly."""
        res = self.rl.update_q_value(state=0, action=1, reward=10.0, next_state=1)
        self.assertEqual(res.__class__.__name__, "Ok")
        
        # current=0, max_next=0, r=10. q = 0 + 0.1*(10 + 0) = 1.0
        self.assertAlmostEqual(res.value, 1.0)
        self.assertAlmostEqual(self.rl.q_table[0, 1], 1.0)

    def test_muzic_transformers(self):
        """Evaluates pure probability tracking modeling QKV targets explicitly correctly."""
        # sequence 2, dimension 4
        q = np.array([[1.0, 0.0, 1.0, 0.0], [0.0, 1.0, 0.0, 1.0]])
        k = np.array([[1.0, 0.0, 1.0, 0.0], [0.0, 1.0, 0.0, 1.0]])
        v = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]])
        
        res = self.muzic.compute_self_attention(q, k, v)
        self.assertEqual(res.__class__.__name__, "Ok")
        
        context = res.value
        self.assertEqual(context.shape, (2, 4))
        # Ensure it maintains probabilistic structural balances safely
        self.assertTrue(np.all(context >= 1.0))
        self.assertTrue(np.all(context <= 8.0))

    def test_openprompt_mapping(self):
        """Extracts text structures modeling symbolic token templates cleanly natively."""
        verbalizer = self.prompt.build_verbalizer({"positive": 0, "negative": 1})
        logit = np.array([0.1, 0.9]) # probability is higher for negative
        res = verbalizer.sequence_to_label(logit)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value, "negative")
        
        template = self.prompt.build_template('The sentiment is {"placeholder": "text_a"}.')
        res_t = template.process("positive")
        self.assertEqual(res_t.__class__.__name__, "Ok")
        self.assertEqual(res_t.value, 'The sentiment is positive.')

    def test_telegram_graph(self):
        """Validates static grid parameters simulating map geometries extracting tracking connections stably."""
        res_add1 = self.graph.add_connection(3, 10)
        res_add2 = self.graph.add_connection(3, 42)
        
        self.assertEqual(res_add1.__class__.__name__, "Ok")
        self.assertEqual(res_add2.__class__.__name__, "Ok")
        
        res_get = self.graph.get_contact_array(3)
        self.assertEqual(res_get.__class__.__name__, "Ok")
        
        contacts = res_get.value
        self.assertEqual(len(contacts), 2)
        self.assertTrue(10 in contacts)
        self.assertTrue(42 in contacts)

if __name__ == '__main__':
    unittest.main()

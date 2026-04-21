import unittest
import numpy as np

# Bindings to OMNI Batch 17 Engines
from src.compute.python_core.omni_sports_vision_engine import OmniSportsVisionEngine
from src.compute.python_core.omni_telegram_list_engine import OmniTelegramListEngine
from src.compute.python_core.omni_muzic_engine import OmniMuzicEngine
from src.compute.python_core.omni_deep_rl_engine import OmniDeepRLEngine
from src.compute.python_core.omni_openprompt_engine import OmniOpenPromptEngine

class TestBatch17Semester6(unittest.TestCase):
    
    def setUp(self):
        self.sports = OmniSportsVisionEngine()
        self.tele = OmniTelegramListEngine()
        self.muzic = OmniMuzicEngine()
        self.deeprl = OmniDeepRLEngine()
        self.prompt = OmniOpenPromptEngine()

    def test_sports_vision_homography(self):
        """Validate DLT mapping logic correctly scaling matrix offsets across 2D homogeneous limits"""
        # Formulate source mapping matching output
        src = np.array([[0,0], [10,0], [10,10], [0,10]])
        dst = np.array([[0,0], [20,0], [20,20], [0,20]])
        
        res_h = self.sports.get_homography_matrix(src, dst)
        self.assertEqual(res_h.__class__.__name__, "Ok")
        H = res_h.value
        
        # We expect a simple uniform scaling matrix for this test 2x modifier 
        self.assertAlmostEqual(H[0,0], 2.0, places=1)
        
        # Test point shifts
        test_pt = np.array([[5, 5]])
        res_proj = self.sports.project_points(test_pt, H)
        self.assertEqual(res_proj.__class__.__name__, "Ok")
        pt_out = res_proj.value
        
        # Coordinates should double mapping accurately
        self.assertTrue(np.allclose(pt_out[0], [10, 10]))

    def test_telegram_list_pagerank(self):
        """Validating undirected matrix probabilities cleanly mapped resolving PageRank without crashes"""
        graph = self.tele.get_network_graph(num_entities=3)
        graph.add_edge(0, 1)
        graph.add_edge(1, 2)
        graph.add_edge(2, 0)
        
        res_pr = graph.resolve_pagerank(iter_count=10)
        self.assertEqual(res_pr.__class__.__name__, "Ok")
        
        scores = res_pr.value
        self.assertEqual(len(scores), 3)
        # Verify sum property 1.0 limits representing probabilistic graph correctly
        self.assertAlmostEqual(np.sum(scores), 1.0, places=5)

    def test_muzic_engine_shifting(self):
        """Ensuring sequences shift within boundary limits perfectly."""
        mapper = self.muzic.get_sequence_mapper(vocab_base=128)
        
        seq = np.array([60, 62, 64]) # Basic C-D-E progression 
        res_q = mapper.sequence_quantization(seq, shift_steps=2)
        
        self.assertEqual(res_q.__class__.__name__, "Ok")
        out = res_q.value
        
        self.assertEqual(out[0], 62)
        
        # Grid timings calculations mapping sequence indices logically correctly
        events = np.array([0, 500, 1000]) # Event hits in MS
        res_a = mapper.align_sequence_grids(events, bpm=120)
        self.assertEqual(res_a.__class__.__name__, "Ok")

    def test_deep_rl_bellman_logic(self):
        """Validate dynamic policy iteration resolving state matrices strictly natively"""
        agent = self.deeprl.get_agent(state_space=2, action_space=2)
        
        # Forcing static reward loop checking matrices correctly map limits
        res_up = agent.update_policy(state=0, action=1, reward=10.0, next_state=1)
        self.assertEqual(res_up.__class__.__name__, "Ok")
        
        q_val = agent.q_table[0, 1]
        self.assertEqual(q_val, 1.0) # alpha * (10) since default alpha is 0.1 and initial q mapped at 0.0
        
        # Choosing actions exploits
        res_action = agent.choose_action(state=0, epsilon=0.0) # Force exploit
        self.assertEqual(res_action.__class__.__name__, "Ok")
        self.assertEqual(res_action.value, 1) # Must pick 1 since it evaluated highly previously!

    def test_openprompt_verbalizer(self):
        """Validating structural mapping templates parsing correctly natively"""
        # Testing templates 
        tmpl = self.prompt.build_template(template_string='Review: {"placeholder": "text_a"} {"mask"}')
        res_p = tmpl.process("It was good.")
        self.assertEqual(res_p.__class__.__name__, "Ok")
        self.assertEqual(res_p.value, 'Review: It was good. {"mask"}')
        
        # Testing logits
        classes = {"negative": 0, "positive": 1}
        verb = self.prompt.build_verbalizer(classes)
        
        resolved_logits = np.array([0.1, 0.9])
        res_v = verb.sequence_to_label(resolved_logits)
        self.assertEqual(res_v.__class__.__name__, "Ok")
        self.assertEqual(res_v.value, "positive")


if __name__ == '__main__':
    unittest.main()

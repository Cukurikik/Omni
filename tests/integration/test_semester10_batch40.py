"""
Integration Test Suite for OMNI Semester 10 Batch 40
Canonical migration from sem10_batch40_integration_tests.py
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import unittest
from src.compute.python_core.omni_regex_parser_engine import OmniRegexParserEngine
from src.compute.python_core.omni_blog_archive_engine import OmniBlogArchiveEngine
from src.compute.python_core.omni_swe_lecture_notes_engine import OmniSWELectureNotesEngine
from src.compute.python_core.omni_bus_ticket_reservation_engine import OmniBusTicketReservationEngine
from src.compute.python_core.omni_data_flow_diagram_engine import OmniDataFlowDiagramEngine

class TestBatch40Integration(unittest.TestCase):
    def test_regex_parser(self):
        engine = OmniRegexParserEngine()
        ast = [{"type": "LITERAL", "children": 0, "repetition": 1}, {"type": "KLEENE", "children": 2, "repetition": 1}]
        # i=0: type LITERAL (1.0). -> depth=1.0. comp += 1/1 = 1.0. 
        # i=1: type KLEENE (3.0), children=2(+1.0). -> depth=4.0. total_depth=5.0. comp += 9/2=4.5. total_comp=5.5.
        # overall = 5.0 * 10.0 = 50.0
        res = engine.compute_ast_topological_depth(ast)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["total_depth"], 4.0)
        self.assertEqual(res["value"]["complexity_index"], 5.5)
        self.assertEqual(res["value"]["recursive_cycles"], 1)
        self.assertEqual(res["value"]["overall_structural_index"], 26.0)

    def test_blog_archive(self):
        engine = OmniBlogArchiveEngine()
        entries = [{"length": 99.0, "links": 10.0, "media": 2.0}]
        # length_factor = log10(100.0) = 2.0
        # media_factor = 2 * 2.5 = 5.0
        # link_factor = 10 * 1.2 = 12.0
        # weight = 2+5+12 = 19.0.
        # cumulative = 19.0 * (1/(3.0)) = 6.3333... mean = 6.3333..
        res = engine.analyze_structural_entropy(entries)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["vector_density"], 19.0)
        self.assertAlmostEqual(res["value"]["mean_entropy"], 6.3333, places=3)

    def test_swe_lecture_notes(self):
        engine = OmniSWELectureNotesEngine()
        chapters = [{"theorems": 2.0, "examples": 10.0, "pages": 2.0}]
        # density = (4.0 + 5.0)/2.0 = 4.5.
        # cog_step = 4.5 * 1.0 = 4.5
        # d_factor = 1 + 0.45 = 1.45
        # int_matrix = 4.5 / 1.45 = 3.103448...
        res = engine.compute_learning_matrix_topology(chapters)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["cognitive_load_sum"], 4.5)
        self.assertEqual(res["value"]["structural_density"], 1.45)
        self.assertAlmostEqual(res["value"]["matrix_integral"], 3.1034, places=3)

    def test_bus_ticket(self):
        engine = OmniBusTicketReservationEngine()
        grid = [{"columns": 40.0, "occupied": 20.0, "grouping_distance": 2.0}]
        # occupied_mass = 20, capacity = 40. ratio = 0.5.
        # clustering = 400.0 / 2.0 = 200.0.
        # eff = 0.5 * 100 + 200.0 = 250.0
        res = engine.calculate_seat_packing_efficiency(grid)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["packing_ratio"], 0.5)
        self.assertEqual(res["value"]["clustering_factor"], 200.0)
        self.assertEqual(res["value"]["spatial_efficiency_index"], 250.0)

    def test_data_flow_diagram(self):
        engine = OmniDataFlowDiagramEngine()
        edges = [{"origin": "A", "dest": "B", "velocity": 10.0}, {"origin": "B", "dest": "C", "velocity": 5.0}]
        # weights: A: -10, B: 10-5 = 5. C: 5. max=5, min=-10. pressure=15. flux=15.
        res = engine.map_flow_structural_dimensions(edges)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["total_flux"], 15.0)
        self.assertEqual(res["value"]["max_sink_weight"], 5.0)
        self.assertEqual(res["value"]["min_source_weight"], -10.0)
        self.assertEqual(res["value"]["flow_pressure_index"], 15.0)


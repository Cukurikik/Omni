import pytest
from src.compute.python_core.omni_srabon_engine import OmniSrabonEngine
from src.compute.python_core.omni_hacker_system_engine import OmniHackerSystemEngine
from src.compute.python_core.omni_scaling_couscous_engine import OmniScalingCouscousEngine
from src.compute.python_core.omni_iron_oxidation_simulator_engine import OmniIronOxidationSimulatorEngine
from src.compute.python_core.omni_pcp_software_engine import OmniPcpSoftwareEngine
from src.compute.python_core.omni_candy_manager_engine import OmniCandyManagerEngine
from src.compute.python_core.omni_bytecore_engine import OmniBytecoreEngine
from src.compute.python_core.omni_psp_eclipse_engine import OmniPspEclipseEngine
from src.compute.python_core.omni_angular_adv_components_engine import OmniAngularAdvComponentsEngine
from src.compute.python_core.omni_virtual_dom_fiber_engine import OmniVirtualDomFiberEngine

class TestSemester11Batch32:
    
    # --- OmniSrabonEngine ---
    def test_srabon_registration(self):
        engine = OmniSrabonEngine()
        assert engine.register_user("u1").is_ok()
        assert not engine.register_user("u1").is_ok()

    def test_srabon_learn_item(self):
        engine = OmniSrabonEngine(base_interval=3)
        engine.register_user("u1")
        assert engine.learn_item("u1", "item_a", 10).is_ok()
        assert engine.user_states["u1"]["items"]["item_a"]["next_review"] == 13

    def test_srabon_review_success(self):
        engine = OmniSrabonEngine()
        engine.register_user("u1")
        engine.learn_item("u1", "i1", 0)
        res = engine.review_item("u1", "i1", 10, True)
        assert res.is_ok()
        assert res.unwrap() == 12 # 2 (interval 1 * 2.5) + 10 (curr time)

    def test_srabon_review_failure(self):
        engine = OmniSrabonEngine()
        engine.register_user("u1")
        engine.learn_item("u1", "i1", 0)
        engine.review_item("u1", "i1", 10, False)
        assert engine.user_states["u1"]["streaks"] == 0
        
    def test_srabon_due_items(self):
        engine = OmniSrabonEngine()
        engine.register_user("u1")
        engine.learn_item("u1", "i1", 0)
        engine.learn_item("u1", "i2", 10)
        due = engine.get_due_items("u1", 5).unwrap()
        assert due == ["i1"]

    # --- OmniHackerSystemEngine ---
    def test_hacker_create_node(self):
        engine = OmniHackerSystemEngine()
        assert engine.create_node("/bin", True, 755).is_ok()
        assert not engine.create_node("/bin", True, 999).is_ok()

    def test_hacker_attach_copyright(self):
        engine = OmniHackerSystemEngine()
        engine.create_node("/file.txt", False, 644)
        assert engine.attach_copyright("/file.txt", "url://copy").is_ok()

    def test_hacker_access_eval(self):
        engine = OmniHackerSystemEngine()
        engine.create_node("/file.txt", False, 644)
        assert engine.check_access("/file.txt", 4).unwrap() == True  # Read ok
        assert engine.check_access("/file.txt", 2).unwrap() == True  # Write ok
        assert engine.check_access("/file.txt", 1).unwrap() == False # Execute fail

    def test_hacker_missing_copyrights(self):
        engine = OmniHackerSystemEngine()
        engine.create_node("/a", False, 600)
        engine.create_node("/b", False, 600)
        engine.attach_copyright("/a", "yes")
        assert engine.find_missing_copyrights().unwrap() == ["/b"]

    def test_hacker_illegal_access(self):
        engine = OmniHackerSystemEngine()
        engine.create_node("/a", False, 600)
        assert not engine.check_access("/a", 3).is_ok()

    # --- OmniScalingCouscousEngine ---
    def test_couscous_register(self):
        engine = OmniScalingCouscousEngine(10)
        assert engine.register_node("n1").is_ok()

    def test_couscous_dispatch(self):
        engine = OmniScalingCouscousEngine(10)
        engine.register_node("n1")
        engine.register_node("n2")
        res = engine.dispatch_cart_load("c1", 5)
        assert res.unwrap() == "n1" # tie break sorted n1

    def test_couscous_overload(self):
        engine = OmniScalingCouscousEngine(10)
        engine.register_node("n1")
        engine.dispatch_cart_load("c1", 8)
        assert not engine.dispatch_cart_load("c2", 5).is_ok()

    def test_couscous_resolve(self):
        engine = OmniScalingCouscousEngine(10)
        engine.register_node("n1")
        engine.dispatch_cart_load("c1", 5)
        assert engine.resolve_transaction("n1", 5).is_ok()
        assert engine.nodes["n1"] == 0

    def test_couscous_variance(self):
        engine = OmniScalingCouscousEngine(10)
        engine.register_node("a")
        engine.register_node("b")
        engine.dispatch_cart_load("c1", 4)
        engine.dispatch_cart_load("c2", 2)
        var = engine.get_cluster_variance().unwrap()
        assert var == 1.0 # mean 3, abs(diffs) 1, 1^2=1, 1^2=1 => 2/2 = 1.0

    # --- OmniIronOxidationSimulatorEngine ---
    def test_ox_register(self):
        engine = OmniIronOxidationSimulatorEngine(0.1)
        assert engine.register_material("Fe", 100, 50).is_ok()

    def test_ox_step(self):
        engine = OmniIronOxidationSimulatorEngine(0.1)
        engine.register_material("Fe", 100, 10)
        # dM = 0.1 * 10 * 1.0 * 2 = 2.0
        rem = engine.simulate_step("Fe", 2.0, 1.0).unwrap()
        assert rem == 98.0

    def test_ox_ratio(self):
        engine = OmniIronOxidationSimulatorEngine(0.1)
        engine.register_material("Fe", 100, 10)
        engine.simulate_step("Fe", 2.0, 1.0)
        assert engine.get_oxidation_ratio("Fe").unwrap() == 0.02
        
    def test_ox_over_decay(self):
        engine = OmniIronOxidationSimulatorEngine(1.0)
        engine.register_material("Fe", 10, 100)
        res = engine.simulate_step("Fe", 10.0, 1.0).unwrap()
        assert res == 0.0 # Bounded at 0

    def test_ox_invalid_temp(self):
        engine = OmniIronOxidationSimulatorEngine(1.0)
        assert not engine.simulate_step("Fe", -5.0, 1.0).is_ok()

    # --- OmniPcpSoftwareEngine ---
    def test_pcp_ingest(self):
        engine = OmniPcpSoftwareEngine(5.0)
        assert engine.ingest_points([(1, 2, 3), (4, 5, 6)]).unwrap() == 2

    def test_pcp_centroid_empty(self):
        engine = OmniPcpSoftwareEngine(5.0)
        assert not engine.extract_centroid().is_ok()

    def test_pcp_centroid(self):
        engine = OmniPcpSoftwareEngine(5.0)
        engine.ingest_points([(0,0,0), (2,2,2)])
        assert engine.extract_centroid().unwrap() == (1.0, 1.0, 1.0)

    def test_pcp_reduction(self):
        engine = OmniPcpSoftwareEngine(2.0)
        # Centroid is (1,1,1). Distances to centroid:
        # p1: 0 (keep)
        # p2: sqrt(1+1+1) ~ 1.73 (keep)
        # p3: sqrt(9+9+9) ~ 5.19 (remove)
        engine.ingest_points([(1,1,1), (2,2,2), (4,4,4)])
        removed = engine.apply_spatial_reduction().unwrap()
        assert removed == 2
        assert len(engine.point_cloud) == 1

    def test_pcp_invalid_point(self):
        engine = OmniPcpSoftwareEngine(2.0)
        assert not engine.ingest_points([(1, 1)]).is_ok()

    # --- OmniCandyManagerEngine ---
    def test_candy_place(self):
        engine = OmniCandyManagerEngine(100)
        assert engine.place_order("o1", 50, 1).is_ok()

    def test_candy_overload(self):
        engine = OmniCandyManagerEngine(100)
        engine.place_order("o1", 50, 1)
        assert not engine.place_order("o2", 60, 1).is_ok()

    def test_candy_batch_process(self):
        engine = OmniCandyManagerEngine(100)
        engine.place_order("o1", 10, 1)
        engine.place_order("o2", 10, 5)
        # o2 has higher priority
        processed = engine.process_batch().unwrap()
        assert processed == ["o2", "o1"]

    def test_candy_priority_weighting(self):
        engine = OmniCandyManagerEngine(100)
        engine.place_order("o1", 10, 10)
        engine.place_order("o2", 10, 20)
        assert engine.compute_priority_weighting().unwrap() == 15.0

    def test_candy_process_empty(self):
        engine = OmniCandyManagerEngine(100)
        assert engine.process_batch().unwrap() == []

    # --- OmniBytecoreEngine ---
    def test_bytecore_load(self):
        engine = OmniBytecoreEngine()
        assert engine.load_program([0x01, 0xFF]).is_ok()

    def test_bytecore_overflow(self):
        engine = OmniBytecoreEngine()
        assert not engine.load_program([0] * 257).is_ok()

    def test_bytecore_halt(self):
        engine = OmniBytecoreEngine()
        engine.load_program([0x0F])
        assert engine.step().unwrap() == False

    def test_bytecore_addition(self):
        engine = OmniBytecoreEngine()
        # LOAD A 250 (0xFA), NOOP, ADD B (B is 10, so 260 -> mask 0xFF -> 4)
        engine.load_program([0x01, 250, 0x02, 0x0F])
        engine.registers["B"] = 10
        engine.run_till_halt()
        assert engine.registers["A"] == 4

    def test_bytecore_infinite_protector(self):
        engine = OmniBytecoreEngine()
        engine.load_program([0x00, 0x00]) # No halt
        assert not engine.run_till_halt(100).is_ok()

    # --- OmniPspEclipseEngine ---
    def test_psp_log_time(self):
        engine = OmniPspEclipseEngine()
        assert engine.log_time_entry("PLAN", 60).is_ok()
        assert not engine.log_time_entry("INVALID", 60).is_ok()

    def test_psp_log_defect(self):
        engine = OmniPspEclipseEngine()
        assert engine.log_defect("DESIGN", "CODE", 30).is_ok()
        
    def test_psp_defect_paradox(self):
        engine = OmniPspEclipseEngine()
        # Cannot inject in CODE and remove in DESIGN
        assert not engine.log_defect("CODE", "DESIGN", 30).is_ok()

    def test_psp_yield(self):
        engine = OmniPspEclipseEngine()
        engine.log_time_entry("CODE", 120)
        engine.log_defect("PLAN", "DESIGN", 15)
        res = engine.compute_yield_metrics().unwrap()
        assert res["total_time"] == 135.0
        assert res["phase_yield"] == 1.0 # 1 out of 1 pre-compile
        
    def test_psp_empty_yield(self):
        engine = OmniPspEclipseEngine()
        res = engine.compute_yield_metrics().unwrap()
        assert res["total_time"] == 0.0

    # --- OmniAngularAdvComponentsEngine ---
    def test_angular_define(self):
        engine = OmniAngularAdvComponentsEngine()
        assert engine.define_component("c1").is_ok()

    def test_angular_no_cycle(self):
        engine = OmniAngularAdvComponentsEngine()
        engine.define_component("c1", ["c2"])
        engine.define_component("c2", ["c3"])
        engine.define_component("c3")
        assert engine.trace_projection_cycles().unwrap() == False

    def test_angular_cycle_detect(self):
        engine = OmniAngularAdvComponentsEngine()
        engine.define_component("c1", ["c2"])
        engine.define_component("c2", ["c3"])
        engine.define_component("c3", ["c1"])
        assert not engine.trace_projection_cycles().is_ok()

    def test_angular_depth(self):
        engine = OmniAngularAdvComponentsEngine()
        engine.define_component("root", ["c1"])
        engine.define_component("c1", ["c2"])
        engine.define_component("c2", [])
        assert engine.calculate_tree_depth("root").unwrap() == 3

    def test_angular_depth_missing(self):
        engine = OmniAngularAdvComponentsEngine()
        assert not engine.calculate_tree_depth("ghost").is_ok()

    # --- OmniVirtualDomFiberEngine ---
    def test_vdom_mount(self):
        engine = OmniVirtualDomFiberEngine()
        assert engine.mount_root({"div": "hello"}).is_ok()

    def test_vdom_reconcile_mutations(self):
        engine = OmniVirtualDomFiberEngine()
        engine.mount_root({"div": "hello"})
        metrics = engine.reconcile({"div": "world"}).unwrap()
        assert metrics["mutations"] == 1
        assert engine.get_commit_frequency().unwrap() == 1

    def test_vdom_reconcile_add_del(self):
        engine = OmniVirtualDomFiberEngine()
        engine.mount_root({"a": 1})
        metrics = engine.reconcile({"b": 2}).unwrap()
        assert metrics["additions"] == 1
        assert metrics["deletions"] == 1

    def test_vdom_reconcile_nested(self):
        engine = OmniVirtualDomFiberEngine()
        engine.mount_root({"app": {"val": 1}})
        metrics = engine.reconcile({"app": {"val": 2}}).unwrap()
        assert metrics["mutations"] == 1
        
    def test_vdom_no_mount_fail(self):
        engine = OmniVirtualDomFiberEngine()
        assert not engine.reconcile({}).is_ok()


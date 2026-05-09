#=============================================================================
# OMNI COMPUTE LAYER — AIRFLOW DAG DEFINITIONS (PYTHON)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Declarative definitions of Airflow DAGs that map execution 
#              down to the Omni Rust DAG Engine.
#=============================================================================

from datetime import datetime, timedelta
from .airflow_bridge import OmniAirflowBridge

class OmniDAG:
    """
    Declarative DSL for defining pipelines.
    """
    def __init__(self, dag_id: str, schedule_interval: str):
        self.dag_id = dag_id
        self.schedule_interval = schedule_interval
        self.tasks = []

    def add_task(self, task_id: str, depends_on: list = None):
        self.tasks.append({
            "id": task_id,
            "dependencies": depends_on or []
        })

    def trigger(self, execution_date: datetime = None):
        date = execution_date or datetime.now()
        
        # Compile to Omni Graph format
        conf = { "nodes": self.tasks }
        
        # Send to Rust execution engine
        result = OmniAirflowBridge.trigger_omni_dag(self.dag_id, date, conf)
        return result


# --- Defined DAGs ---

def build_model_retraining_dag() -> OmniDAG:
    dag = OmniDAG("weekly_model_retrain", "@weekly")
    
    # 1. Ingest
    dag.add_task("ingest_latest_data")
    
    # 2. Preprocess (depends on ingest)
    dag.add_task("preprocess_data", depends_on=["ingest_latest_data"])
    
    # 3. Train Diff-Transformer
    dag.add_task("train_diff_transformer", depends_on=["preprocess_data"])
    
    # 4. Evaluate & Deploy
    dag.add_task("evaluate_model", depends_on=["train_diff_transformer"])
    dag.add_task("deploy_to_registry", depends_on=["evaluate_model"])
    
    return dag

# Instantiate standard pipelines
weekly_retrain = build_model_retraining_dag()

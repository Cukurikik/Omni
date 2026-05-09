#=============================================================================
# OMNI COMPUTE LAYER — AIRFLOW EVENT BRIDGE (PYTHON)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Bridges Apache Airflow execution triggers into the OMNI Event 
#              Loop and DAG Executor.
#=============================================================================

import json
from datetime import datetime
import omni_bridge.network.rpc as rpc
import omni_bridge.domain.error as err

class OmniAirflowBridge:
    """
    Acts as an Airflow Operator executing DAGs inside the Omni Rust engine.
    """
    
    @staticmethod
    def trigger_omni_dag(dag_id: str, execution_date: datetime, conf: dict) -> err.Result[str]:
        try:
            payload = {
                "dag_id": dag_id,
                "execution_date": execution_date.isoformat(),
                "configuration": conf
            }
            
            # Send synchronous RPC call to Rust DAG Executor
            response = rpc.call_sync("compute.pipelines.execute_dag", payload)
            
            if response.get("status") == "success":
                return err.Ok(response.get("run_id", "unknown_run"))
            else:
                return err.Err(f"Omni Engine DAG failure: {response.get('error')}")
                
        except Exception as e:
            return err.Err(f"Bridge communication error: {str(e)}")

    @staticmethod
    def poll_dag_status(run_id: str) -> str:
        """
        Polls the status of an ongoing Omni DAG execution.
        """
        response = rpc.call_sync("compute.pipelines.get_status", {"run_id": run_id})
        return response.get("status", "unknown")

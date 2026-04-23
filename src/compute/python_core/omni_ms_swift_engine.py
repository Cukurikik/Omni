"""OmniMsSwiftEngine.

Wrapper for ModelScope ms-swift (Scalable lightWeight Infrastructure for Fine-Tuning).
Provides programmatic entrypoints for PEFT tuning LLMs.
"""
from typing import Dict, Any
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniMsSwiftEngine:
    """OMNI Engine for modelscope/ms-swift."""

    def __init__(self, workspace_dir: str = "/tmp/swift_workspace"):
        """Initialize the ms-swift training orchestrator."""
        self.workspace_dir = workspace_dir

    def diagnostics(self) -> Dict[str, Any]:
        """Returns diagnostic metadata."""
        return {
            "engine": "OmniMsSwiftEngine",
            "status": "ready",
            "workspace": self.workspace_dir
        }

    def run_sft(self, model_id: str, dataset_id: str) -> Result[Dict[str, Any], Exception]:
        """Runs Supervised Fine Tuning (SFT) using ms-swift.
        
        Args:
            model_id: HuggingFace or ModelScope model ID.
            dataset_id: Dataset ID for training.
            
        Returns:
            Result wrapping training metadata output string.
        """
        try:
            from swift.llm import sft_main, SftArguments
            
            args = SftArguments(
                model=model_id,
                dataset=[dataset_id],
                output_dir=self.workspace_dir,
                sft_type="lora",
                max_length=2048
            )
            result = sft_main(args)
            return Ok({"status": "completed", "result": str(result)})
        except ImportError:
            return Err(Exception("ms-swift package is not installed. Run `pip install ms-swift`."))
        except Exception as e:
            return Err(e)

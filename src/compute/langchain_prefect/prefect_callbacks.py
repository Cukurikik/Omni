from langchain.callbacks.base import BaseCallbackHandler
from prefect import get_run_logger

class PrefectLangChainCallback(BaseCallbackHandler):
    def on_llm_start(self, serialized: dict, prompts: list, **kwargs):
        logger = get_run_logger()
        logger.info(f"LLM starting with prompts: {prompts}")
        
    def on_llm_end(self, response, **kwargs):
        logger = get_run_logger()
        logger.info("LLM finished successfully")

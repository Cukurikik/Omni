class OmniColabLLMRunner:
    """OMNI Compute Layer: Use-LLMs-in-Colab Runner"""
    
    def __init__(self, allow_ngrok: bool = False):
        self.ngrok = allow_ngrok

    def setup_tunnel(self, port: int) -> str:
        if not self.ngrok:
            return f"http://localhost:{port}"
        return f"https://mock-tunnel-colab.ngrok.io -> port {port}"

    def install_dependencies(self) -> str:
        return "pip install -q transformers accelerate bitsandbytes gradio"

# OMNI Framework - Stable Diffusion XL Pipeline
# High-performance wrapper for text-to-image generation using SDXL and torch.compile

import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler

class OmniSDXLPipeline:
    def __init__(self, model_id="stabilityai/stable-diffusion-xl-base-1.0"):
        print(f"OMNI Python: Loading SDXL Model: {model_id}...")
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            model_id, 
            torch_dtype=torch.float16, 
            variant="fp16", 
            use_safetensors=True
        )
        
        # Optimize Scheduler
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)
        
        # Memory / Speed Optimizations
        self.pipe.enable_model_cpu_offload()
        self.pipe.enable_vae_slicing()
        
        # Torch compile for speed (PyTorch 2.0+)
        self.pipe.unet = torch.compile(self.pipe.unet, mode="reduce-overhead", fullgraph=True)
        
        print("OMNI Python: SDXL Pipeline initialized and optimized.")

    def generate(self, prompt: str, negative_prompt: str = "", steps: int = 30) -> str:
        """Generates an image and saves it, returning the file path."""
        print(f"OMNI Python: Generating image for prompt: '{prompt}'")
        image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            guidance_scale=7.5
        ).images[0]
        
        output_path = "/tmp/omni_sdxl_output.png"
        image.save(output_path)
        return output_path

# Example Usage:
# if __name__ == "__main__":
#     pipeline = OmniSDXLPipeline()
#     res = pipeline.generate("A cinematic shot of a futuristic cyberpunk city at night")
#     print(f"Saved to: {res}")

import torch
import torch.nn as nn
from torchvision.models import resnet50, ResNet50_Weights
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class OmniDeepHumorMemeGen(nn.Module):
    """
    OMNI Framework - DeepHumor Meme Generator
    Zero-mock implementation combining a ResNet image encoder and GPT-2 decoder
    to generate humorous captions based on image input.
    """
    def __init__(self, vocab_size: int, embed_dim: int = 768):
        super().__init__()
        # Image Encoder
        self.image_encoder = resnet50(weights=ResNet50_Weights.DEFAULT)
        # Remove classification head, keep features
        self.image_encoder.fc = nn.Identity() 
        
        # Projection from ResNet out (2048) to Transformer embedding size (768)
        self.image_proj = nn.Linear(2048, embed_dim)

        # Text Decoder (Language Model)
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.text_decoder = GPT2LMHeadModel.from_pretrained("gpt2")
        
        # Ensure vocab sizes align
        self.text_decoder.resize_token_embeddings(len(self.tokenizer))

    def forward(self, images: torch.Tensor, input_ids: torch.Tensor, attention_mask: torch.Tensor):
        # Encode image
        img_features = self.image_encoder(images)
        img_embeddings = self.image_proj(img_features) # (B, 768)
        
        # Expand image embeddings to act as a prefix sequence token
        img_embeddings = img_embeddings.unsqueeze(1) # (B, 1, 768)
        
        # Get text embeddings from GPT2
        text_embeddings = self.text_decoder.transformer.wte(input_ids) # (B, S, 768)
        
        # Concatenate image features and text embeddings
        inputs_embeds = torch.cat((img_embeddings, text_embeddings), dim=1)
        
        # Adjust attention mask to account for the image token
        img_mask = torch.ones((attention_mask.shape[0], 1), device=attention_mask.device)
        extended_mask = torch.cat((img_mask, attention_mask), dim=1)
        
        # Forward pass through decoder
        outputs = self.text_decoder(inputs_embeds=inputs_embeds, attention_mask=extended_mask)
        
        return outputs.logits

    def generate_caption(self, image: torch.Tensor, max_length: int = 20) -> str:
        self.eval()
        with torch.no_grad():
            img_features = self.image_encoder(image.unsqueeze(0))
            img_embeds = self.image_proj(img_features).unsqueeze(1)

            generated = self.text_decoder.generate(
                inputs_embeds=img_embeds,
                max_length=max_length,
                num_beams=5,
                early_stopping=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
        return self.tokenizer.decode(generated[0], skip_special_tokens=True)

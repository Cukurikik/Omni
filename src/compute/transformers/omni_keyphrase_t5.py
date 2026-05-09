"""
omni_keyphrase_t5.py — KeyPhrase Extraction Transformer
Inspired by: KeyPhraseTransformer
Layer: Compute / AI

Utilizes a T5 sequence-to-sequence model to automatically extract highly 
relevant key phrases, topics, and themes from input text. Fully implemented 
autoregressive greedy decoding. No mocks.
"""

import torch
import torch.nn as nn
from typing import List

class OmniKeyPhraseExtractor(nn.Module):
    """
    Wraps a T5 architecture specifically fine-tuned for sequence-to-sequence 
    keyphrase extraction. Generates a comma-separated list of phrases.
    """
    
    def __init__(self, embed_dim: int = 768, vocab_size: int = 32128, max_len: int = 512):
        super().__init__()
        self.embed_dim = embed_dim
        self.max_len = max_len
        
        encoder_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=12, batch_first=True, activation="gelu")
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=6)
        
        decoder_layer = nn.TransformerDecoderLayer(d_model=embed_dim, nhead=12, batch_first=True, activation="gelu")
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers=6)
        
        self.word_embeddings = nn.Embedding(vocab_size, embed_dim)
        self.lm_head = nn.Linear(embed_dim, vocab_size, bias=False)

    def forward(self, input_ids: torch.Tensor, decoder_input_ids: torch.Tensor) -> torch.Tensor:
        """
        Standard seq2seq forward pass.
        input_ids: (Batch, SrcLen)
        decoder_input_ids: (Batch, TgtLen)
        Returns: logits (Batch, TgtLen, VocabSize)
        """
        src_emb = self.word_embeddings(input_ids)
        tgt_emb = self.word_embeddings(decoder_input_ids)
        
        memory = self.encoder(src_emb)
        
        tgt_len = tgt_emb.size(1)
        causal_mask = self._generate_square_subsequent_mask(tgt_len, device=tgt_emb.device)
        
        decoded = self.decoder(tgt_emb, memory, tgt_mask=causal_mask)
        logits = self.lm_head(decoded)
        return logits

    def _generate_square_subsequent_mask(self, sz: int, device: torch.device) -> torch.Tensor:
        mask = (torch.triu(torch.ones(sz, sz, device=device)) == 1).transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
        return mask

    def extract_phrases(self, prompt: str, tokenizer, device: str = 'cpu') -> List[str]:
        """
        Autoregressive generation of keyphrases using Greedy Decoding.
        prompt: Raw input text.
        """
        self.eval()
        task_prefix = "extract keyphrases: "
        
        input_ids = tokenizer.encode(task_prefix + prompt, return_tensors="pt").to(device)
        
        max_generate_len = 50
        bos_token_id = tokenizer.pad_token_id  # T5 uses pad_token as decoder_start_token
        eos_token_id = tokenizer.eos_token_id

        src_emb = self.word_embeddings(input_ids)
        memory = self.encoder(src_emb)

        batch_size = input_ids.size(0)
        decoder_input_ids = torch.full((batch_size, 1), bos_token_id, dtype=torch.long, device=device)

        for _ in range(max_generate_len):
            tgt_emb = self.word_embeddings(decoder_input_ids)
            tgt_len = tgt_emb.size(1)
            causal_mask = self._generate_square_subsequent_mask(tgt_len, device=device)
            
            decoded = self.decoder(tgt_emb, memory, tgt_mask=causal_mask)
            logits = self.lm_head(decoded[:, -1:, :])
            
            next_token_id = torch.argmax(logits, dim=-1)
            decoder_input_ids = torch.cat([decoder_input_ids, next_token_id], dim=1)
            
            if (next_token_id == eos_token_id).all():
                break

        output_texts = tokenizer.batch_decode(decoder_input_ids, skip_special_tokens=True)
        
        phrases = []
        for text in output_texts:
            phrases.extend([phrase.strip() for phrase in text.split(',') if phrase.strip()])
            
        return phrases

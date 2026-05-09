import torch
import torch.nn as nn

class OmniASRAttacker:
    """
    Projected Gradient Descent (PGD) Adversarial Attack on 
    Automatic Speech Recognition (ASR) systems (like Wav2Vec2).
    Generates subtle adversarial noise to fool the transcription model.
    """
    def __init__(self, asr_model, epsilon: float = 0.05, alpha: float = 0.005, iters: int = 20):
        self.asr_model = asr_model
        self.epsilon = epsilon
        self.alpha = alpha
        self.iters = iters
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.asr_model.to(self.device)
        self.asr_model.eval()

    def generate_attack(self, audio_tensor: torch.Tensor, target_transcription_ids: torch.Tensor) -> torch.Tensor:
        """
        audio_tensor: [1, Audio_Length]
        target_transcription_ids: [1, Target_Length]
        Returns adversarial audio tensor.
        """
        audio_tensor = audio_tensor.to(self.device).clone().detach()
        adv_audio = audio_tensor.clone().detach().requires_grad_(True)
        
        criterion = nn.CTCLoss(blank=self.asr_model.config.pad_token_id, zero_infinity=True)
        
        for i in range(self.iters):
            self.asr_model.zero_grad()
            
            # Forward pass
            outputs = self.asr_model(adv_audio)
            logits = outputs.logits
            
            # CTC loss expects [Sequence, Batch, Classes]
            log_probs = nn.functional.log_softmax(logits, dim=-1).transpose(0, 1)
            
            input_lengths = torch.full(size=(1,), fill_value=log_probs.shape[0], dtype=torch.long)
            target_lengths = torch.full(size=(1,), fill_value=target_transcription_ids.shape[1], dtype=torch.long)
            
            # We want to MINIMIZE the loss to the TARGET transcription
            loss = criterion(log_probs, target_transcription_ids, input_lengths, target_lengths)
            
            # Backward pass
            loss.backward()
            
            # PGD Step
            with torch.no_grad():
                adv_audio = adv_audio - self.alpha * adv_audio.grad.sign()
                
                # Projection to epsilon ball
                eta = torch.clamp(adv_audio - audio_tensor, min=-self.epsilon, max=self.epsilon)
                adv_audio = torch.clamp(audio_tensor + eta, min=-1.0, max=1.0).requires_grad_(True)
                
        return adv_audio.detach()

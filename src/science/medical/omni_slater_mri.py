import torch
import torch.nn as nn
import torch.fft

class OmniSLATER_MRI(nn.Module):
    """
    SLATER: Unsupervised MRI Reconstruction via Zero-Shot Learned Adversarial Transformers.
    Converts k-space (Fourier) undersampled data into high-resolution MRI images.
    """
    def __init__(self, img_size=256, patch_size=16, embed_dim=256, num_heads=8, depth=4):
        super().__init__()
        self.img_size = img_size
        self.patch_size = patch_size
        self.num_patches = (img_size // patch_size) ** 2
        
        self.patch_embed = nn.Conv2d(2, embed_dim, kernel_size=patch_size, stride=patch_size)
        self.pos_embed = nn.Parameter(torch.zeros(1, self.num_patches, embed_dim))
        
        encoder_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=num_heads, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=depth)
        
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(embed_dim, 64, kernel_size=patch_size, stride=patch_size),
            nn.ReLU(),
            nn.Conv2d(64, 2, kernel_size=3, padding=1) # output complex image (real, imag)
        )

    def forward(self, masked_k_space, mask):
        """
        masked_k_space: [B, 2, H, W] (real, imag components)
        mask: [B, 1, H, W] undersampling mask
        """
        # IFFT to image domain (aliased)
        k_complex = torch.complex(masked_k_space[:, 0], masked_k_space[:, 1])
        img_aliased = torch.fft.ifft2(k_complex, norm="ortho")
        img_aliased_real_imag = torch.stack([img_aliased.real, img_aliased.imag], dim=1)
        
        # Transformer representation
        B = img_aliased_real_imag.shape[0]
        x = self.patch_embed(img_aliased_real_imag) # [B, D, H/P, W/P]
        x = x.flatten(2).transpose(1, 2) # [B, N, D]
        x = x + self.pos_embed
        
        z = self.transformer(x)
        
        # Decode back to image
        H_p = self.img_size // self.patch_size
        z = z.transpose(1, 2).reshape(B, -1, H_p, H_p)
        img_recon = self.decoder(z)
        
        # Data Consistency step in k-space
        img_recon_complex = torch.complex(img_recon[:, 0], img_recon[:, 1])
        k_recon = torch.fft.fft2(img_recon_complex, norm="ortho")
        k_recon_real_imag = torch.stack([k_recon.real, k_recon.imag], dim=1)
        
        # Keep original sampled points, replace missing with reconstructed
        k_final = masked_k_space * mask + k_recon_real_imag * (1 - mask)
        
        # Final IFFT
        k_final_complex = torch.complex(k_final[:, 0], k_final[:, 1])
        img_final = torch.fft.ifft2(k_final_complex, norm="ortho")
        
        return torch.sqrt(img_final.real**2 + img_final.imag**2) # Magnitude image

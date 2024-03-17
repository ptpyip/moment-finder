import torch
from torch import nn

from collections import OrderedDict

from .modules import QuickGELU, LayerNorm

class TemporalTransformer(nn.Module):
    def __init__(self, 
        width: int, 
        layers: int, 
        heads: int,
        hidden_size: int,
        num_temporal_embeddings:int, 
    ):
        self.temporal_embeddings = nn.Embedding(
            num_temporal_embeddings, hidden_size
        )
        # self.transformer == nn.TransformerEncoder
        self.transformer = TransformerEncoder(width, layers, heads)
        
    def forward(self, x: torch.Tensor, attn_mask):
        seq_length = x.size(1)
        
        extended_attn_mask = (1.0 - attn_mask.unsqueeze(1)) * -1000000.0
        extended_attn_mask = extended_attn_mask.expand(-1, attn_mask.size(1), -1)
        
        temporal_ids = torch.arange(seq_length, dtype=torch.long, device=x.device)
        temporal_embeddings = self.temporal_embeddings(
            temporal_ids.unsqueeze(0).expand(x.size(0), -1)
        )
        
        temp = x + temporal_embeddings
        out = self.transformer(
            temp.permute(1, 0, 2),              # NLD -> LND
            extended_attn_mask
        ).permute(1, 0, 2)                      # LND -> NLD
        
        return out + x 

class ResidualAttentionBlock(nn.Module):
    def __init__(self, d_model: int, n_head: int):
        super().__init__()

        self.attn = nn.MultiheadAttention(d_model, n_head)
        self.ln_1 = LayerNorm(d_model)
        self.mlp = nn.Sequential(OrderedDict([
            ("c_fc", nn.Linear(d_model, d_model * 4)),
            ("gelu", QuickGELU()),
            ("c_proj", nn.Linear(d_model * 4, d_model))
        ]))
        self.ln_2 = LayerNorm(d_model)
        self.n_head = n_head

    def attention(self, x: torch.Tensor, attn_mask: torch.Tensor):
        attn_mask_ = attn_mask.repeat_interleave(self.n_head, dim=0)
        return self.attn(x, x, x, need_weights=False, attn_mask=attn_mask_)[0]

    def forward(self, para_tuple: tuple):
        # x: torch.Tensor, attn_mask: torch.Tensor
        # print(para_tuple)
        x, attn_mask = para_tuple
        x = x + self.attention(self.ln_1(x), attn_mask)
        x = x + self.mlp(self.ln_2(x))
        return (x, attn_mask)

class TransformerEncoder(nn.Module):
    def __init__(self, width: int, layers: int, heads: int):
        super().__init__()
        self.width = width
        self.layers = layers
        self.resblocks = nn.Sequential(*[ResidualAttentionBlock(width, heads) for _ in range(layers)])

    def forward(self, x: torch.Tensor, attn_mask: torch.Tensor):
        return self.resblocks((x, attn_mask))[0]
    

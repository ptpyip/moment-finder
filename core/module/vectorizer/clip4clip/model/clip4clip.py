import os
from enum import Enum
from typing import Optional

import torch
from torch import nn

from .modules import CrossEn
from .pretrained import PreTrainedClip
from .transfromer import TemporalTransformer

class TemporalMode(Enum):
    MEAN_POOLING = 0
    TRANSFORMER = 1
    # CrossTransformer = 2        # not used.

def build_model(state_dict: dict):
    """ build model from a given state dict
    if state_dict is {} => build from empty
    """
    
    
class CLIP4Clip(PreTrainedClip):
    CLIP_NAME = "ViT-B/32"
    def __init__(self,
        clip_name=CLIP_NAME,
        temporal_mode: TemporalMode = TemporalMode.MEAN_POOLING,
        hidden_size = 512,
        num_temporal_hidden_layers = 4,
        max_temporal_embeddings = 128,
    ) -> None:
        super(CLIP4Clip, self).__init__(clip_name)                                ## init clipa[0]
        self.input_resolution = self.clip.visual.input_resolution
        self.max_num_frame = self.clip.context_length
       
        self.temporal_mode = temporal_mode 
        self.hidden_size = hidden_size
        self.num_temporal_hidden_layers = num_temporal_hidden_layers
        
        self.temporal_trans: Optional[TemporalTransformer] = None
        if temporal_mode == TemporalMode.TRANSFORMER:
            self.temporal_trans = self._init_temporal_trans(max_temporal_embeddings)
            assert self.num_temporal_embeddings <= max_temporal_embeddings
        
        self.loss_fn = CrossEn()
        self.norm = lambda x: x / x.norm(dim=-1, keepdim=True)
    
        return

    def encode_text(self, text):
        """for inference"""
        text = text.view(-1, text.shape[-1]) 
        return self.forward_text(text)

    def encode_moments(self, moment: torch.Tensor, moment_mask=None):
        """
        encode one or more than one moments
        
        Attribute:
        - moment: torch.Tensor
        - moment_mask: a 2D array indicate moment_i has L frames. 
        
        """
        assert len(moment.shape) >= 4
        bs, L, _, H, W = moment.shape

        if moment_mask is None:
            moment_mask = torch.ones((bs, L))
        
        assert moment_mask.dim() == 2
        assert bs == moment_mask.shape[0]
        assert L == moment_mask.shape[1]
        
        moment = moment.view(-1, 3, H, W).float()   # batched frames in 4D Tensor
        return self.forward_visual(moment, moment_mask)

        
    # def encode_frames(self, frames):
    #     """for inference"""

    #     N, L, channel, h, w = frames.shape
    #     assert L <= self.max_num_frame
    #     frames = frames.view(-1, channel, h, w) 
    #     for moment in frames:
    #         moment_length = 
    #         video_mask[i][:v_length] = [1] * v_length
        
    #     return self.forward_text(frames)
   

    def forward(self, text, video, video_mask):
        text = text.view(-1, text.shape[-1])
        video_mask = video_mask.view(-1, video_mask.shape[-1])

        # T x 3 x H x W
        video = torch.as_tensor(video).float()
        b, pair, bs, ts, channel, h, w = video.shape
        video = video.view(b * pair * bs * ts, channel, h, w)
        
        text_feature = self.forward_text(text)
        video_feature = self.forward_visual(video, video_mask)

        ## assume training
        # if not self.training:
        #     return None
        
        loss = 0.
        sim_matrix, *_tmp = self.get_similarity_logits(
            text_feature, video_feature
        )
        
        sim_loss1 = self.loss_fn(sim_matrix)
        sim_loss2 = self.loss_fn(sim_matrix.T)
        sim_loss = (sim_loss1 + sim_loss2) / 2
        loss += sim_loss

        return loss

    def forward_text(self, text):
        bs = text.size(0)           # [batch_size, n_ctx, dim]
        
        text_feature = self.clip.encode_text(text).float()
        text_feature = text_feature.view(
            bs, -1, text_feature.size(-1)
        ).squeeze(1)
        
        return self.norm(text_feature) if self.training else text_feature
    
    
    def forward_visual(self, frames, video_mask):
        """
        here in og CLIP4Clip implementation they apply layernorm and projection to entire tans output.
        """
        bs = video_mask.size(0)
        frames = self.clip.encode_image(frames).float()
        frames = frames.view(
            bs, -1, frames.size(-1)
        )
        
        temporal_feature = self.forward_temporal(frames, video_mask)
        return self.norm(temporal_feature) if self.training else temporal_feature
    
    
    def forward_temporal(self, feature, video_mask):
        if self.temporal_mode is TemporalMode.TRANSFORMER:
            assert self.temporal_trans is not None
            feature = self.temporal_trans(feature, video_mask)
        
        return self.mean_pooling(feature, video_mask) 
    
    def mean_pooling(self, feature, video_mask):
        feature = self.norm(feature) if self.training else feature
        
        video_mask_un = video_mask.to(dtype=torch.float).unsqueeze(-1)
        feature = feature * video_mask_un
        
        video_mask_un_sum = torch.sum(video_mask_un, dim=1, dtype=torch.float)
        video_mask_un_sum[video_mask_un_sum == 0.] = 1.
        temporal_feature = torch.sum(feature, dim=1) / video_mask_un_sum
        
        return temporal_feature
    
    def get_similarity_logits(self, text_feature, video_feature, attention_mask, video_mask, shaped=False, loose_type=False):
        # if shaped is False:
        #     attention_mask = attention_mask.view(-1, attention_mask.shape[-1])
        #     video_mask = video_mask.view(-1, video_mask.shape[-1])

        logit_scale = self.clip.logit_scale.exp()
        retrieve_logits = logit_scale * torch.matmul(text_feature, video_feature.T)
        return retrieve_logits
    
    
    def _init_temporal_trans(self, max_temporal_embeddings) -> TemporalTransformer:          
        self.num_temporal_embeddings = self.positional_embedding.shape[0]
        self.transformer_width = self.clip.ln_final.weight.shape.shape[0]
        self.heads = self.transformer_width // 64
        
        assert self.num_temporal_embeddings <= max_temporal_embeddings
        
        temporal_trans = TemporalTransformer(
            width=self.transformer_width, 
            layers=self.num_temporal_hidden_layers,
            heads=self.transformer_heads, 
            hidden_size=self.hidden_size,
            num_temporal_embeddings=self.num_temporal_embeddings
        )   
       
        temporal_state_dict = {
            "temporal_embeddings.weight": self.clip.positional_embedding.clone()
        } 
        
        for key, val in self.clip.transformer.state_dict(prefix="transformer.").items():
            num_layer = int(key.split(".")[2]) 
            if num_layer >= self.num_temporal_hidden_layers:
                break
            
            temporal_state_dict[key] = val.clone() 
        
        temporal_trans.load_state_dict(temporal_state_dict)
        return temporal_trans
import math
import torch
import numpy as np
# import clip


from PIL.Image import Image
from typing import List
from torchvision.transforms import Compose

from . import clip4clip
from .base import BaseVectorizer
# CKPT_PATH = "/home/ptpyip/fyp/moment-finder/core/module/vectorizer/CLIP4Clip/ckpts"

class CLIP4ClipVectorizer(BaseVectorizer):
    model: clip4clip.CLIP4Clip
    def __init__(self, 
        model_path,
        model_name="meanP-ViT-B/32"
    ) -> None:
        self.model_path = model_path
        self.model_name = model_name
        super().__init__()
    
    def load_model(self, *args):
        self.model, self.transform = clip4clip.load(
            self.model_path, self.model_name, self.device
        )
        
    def vectorize_txt(self, txt:str):
        with torch.no_grad():
            text_features = self.model.encode_text(clip4clip.tokenize(txt).to(self.device))
            text_features /= text_features.norm(dim=-1, keepdim=True)
        
        return text_features
    
    def vectorize_moment(self, moment: List[Image]):
        # img_raw = Image.open(img_path)
        moment_tensor, moment_mask = self.preprocess([moment]) 
        
        with torch.no_grad():
            video_features =  self.model.encode_moments(
                moment_tensor.to(self.device),
                moment_mask.to(self.device) 
            )
            video_features /= video_features.norm(dim=-1, keepdim=True)
        
        return video_features 

    def preprocess(self, moments: List[List[Image]]):
        assert isinstance(moments, list)
        
        bs = len(moments)
        L = self.model.max_num_frame
        H = W = self.model.input_resolution
        
        moment_tensor = torch.zeros(bs, L, 3, H, W)
        moment_mask = torch.zeros(bs, L)
        for i, moment in enumerate(moments):
            moment_length = len(moment)
            
            if moment_length > L:
                print(f"Warning moment too large: {moment_length}, slicing is used")
                
                ## hard slice
                moment = moment[:L]
                moment_length = L

            moment_tensor[i][:moment_length] = np.stack(map(self.transform, moment))
            moment_mask[i][:moment_length] = [1] * moment_length
        
        return moment_tensor, moment_mask
import math
import torch
import numpy as np
# import clip
from clip.clip import _transform


from PIL.Image import Image
from typing import List
from torchvision.transforms import Compose
from transformers import CLIPTextModelWithProjection, CLIPVisionModelWithProjection, CLIPTokenizer

from . import clip4clip
from .base import BaseVectorizer
# CKPT_PATH = "/home/ptpyip/fyp/moment-finder/core/module/vectorizer/CLIP4Clip/ckpts"

class CLIP4ClipVectorizerV2(BaseVectorizer):
    model: clip4clip.CLIP4Clip
    def __init__(self, 
        model_path=None,
        model_name="Searchium-ai/clip4clip-webvid150k",
        input_reoulution=224
    ) -> None:
        self.model_path = model_path
        self.model_name = model_name
        self.input_reoulution = input_reoulution
        super().__init__()      # set device + call load_model() 
    
    def load_model(self, *args):
        self.txt_model = CLIPTextModelWithProjection.from_pretrained(self.model_name)
        self.txt_model.eval()
        self.txt_model.to(self.device)
        self.vis_model = CLIPVisionModelWithProjection.from_pretrained(self.model_name)
        self.vis_model.eval()
        self.vis_model.to(self.device)
        
        tokenizer = CLIPTokenizer.from_pretrained(self.model_name)
        self.tokenize = lambda txt: tokenizer(text=txt , return_tensors="pt")
        
        self.transform = _transform(self.input_reoulution)
        
    def vectorize_txt(self, txt:str) -> torch.Tensor:
        with torch.no_grad():
            inputs = self.tokenize(txt)
            outputs = self.txt_model(
                input_ids=inputs["input_ids"].to(self.device), 
                attention_mask=inputs["attention_mask"].to(self.device)
            )

            # Normalize embeddings for retrieval:
            text_features = outputs[0] / outputs[0].norm(dim=-1, keepdim=True)
            text_features = text_features.cpu().detach()
        
        return text_features
    
    def vectorize_moment(self, moment: List[Image]):
        moment_tensor = self.preprocess(moment) 
        
        with torch.no_grad():
            visual_output = self.vis_model(moment_tensor.to(self.device))

            # Normalizing the embeddings and calculating mean between all embeddings. 
            visual_output = visual_output["image_embeds"]
            visual_output = visual_output / visual_output.norm(dim=-1, keepdim=True)
            visual_output = torch.mean(visual_output, dim=0)
            visual_output = visual_output / visual_output.norm(dim=-1, keepdim=True)
        
        return visual_output        # batch_size = 1 
    
    def preprocess(self, moment: List[Image]):
    
        L = 77
        H = W = self.input_reoulution
        moment_tensor = torch.zeros(L, 3, H, W)
        
        moment_length = len(moment)
        if moment_length > L:
            print(f"Warning moment too large: {moment_length}, slicing is used")
            
            ## hard slice
            moment = moment[:L]
            moment_length = L

        moment_tensor[:moment_length] = torch.stack(
            [self.transform(frame) for frame in moment]
        )
        
        return moment_tensor[:moment_length] 
        
    # def preprocess(self, moments: List[List[Image]]):
    #     assert isinstance(moments, list)
        
    #     bs = len(moments)
    #     # L = self.model.max_num_frame
    #     L = 77
    #     # H = W = self.model.input_resolution
    #     H, W = self.input_reoulution
        
    #     moment_tensor = torch.zeros(bs, L, 3, H, W)
    #     # moment_mask = torch.zeros(bs, L)
    #     last_frame = 0
    #     for i, moment in enumerate(moments):
    #         moment_length = len(moment)
            
    #         if moment_length > L:
    #             print(f"Warning moment too large: {moment_length}, slicing is used")
                
    #             ## hard slice
    #             moment = moment[:L]
    #             moment_length = L

    #         moment_tensor[i][:moment_length] = torch.stack(
    #             [self.transform(frame) for frame in moment]
    #         )
    #         # moment_mask[i][:moment_length] += 1 
    #         last_frame = i
         
    #     return moment_tensor[: last_frame+1]
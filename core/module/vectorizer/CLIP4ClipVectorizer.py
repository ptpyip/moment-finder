import math
import torch
# import clip


from PIL import Image
from torchvision.transforms import Compose

from . import clip4clip
from .base import BaseVectorizer
# CKPT_PATH = "/home/ptpyip/fyp/moment-finder/core/module/vectorizer/CLIP4Clip/ckpts"

class CLIP4ClipVectorizer(BaseVectorizer):
    def __init__(self, 
        model_path,
        model_name="meanP-ViT-B/32"
    ) -> None:
        self.model_path = model_path
        self.model_name = model_name
        super().__init__()
    
    def load_model(self, *args):
        self.model, self.preprocess = clip4clip.load(
            self.model_path, self.model_name, self.device
        )
        
    def vectorize_txt(self, txt:str):
        with torch.no_grad():
            text_features = self.model.encode_text(clip4clip.tokenize(txt).to(self.device))
            text_features /= text_features.norm(dim=-1, keepdim=True)
        
        return text_features
    
    def vectorize_img(self, img_raw: Image):
        # img_raw = Image.open(img_path)
        img =  self.preprocess(img_raw) 
        
        with torch.no_grad():
            img_features =  self.model.encode_image(img.to(self.device))
            img_features /= img_features.norm(dim=-1, keepdim=True)
        
        return img_features 
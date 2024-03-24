import os
import torch
import clip
import numpy as np

from PIL import Image


from .base import BaseVectorizer
from . import clip4clip 

class CLIPVectorizer(BaseVectorizer): 
    def __init__(self, model_name="ViT-B/32") -> None:
        self.model_name = model_name
        
        super().__init__()
    
    def load_model(self, *args):
        if len(self.model_name.split('-')) == 3:
            """use CLIP4Clip's clip model"""
            clip4clip_model, self.transform = clip4clip.load(
                path=os.path.join(clip4clip.GPU_CKPTS_DIR, clip4clip.MODELS[self.model_name]),
                model_name=self.model_name,
                device="cuda"
            )
            
            self.model = clip4clip_model.clip
            return

        self.model, self.transform = clip.load(self.model_name, device=self.device)
        return
        
    def vectorize_txt(self, txt:str):
        with torch.no_grad():
            text_features = self.model.encode_text(clip.tokenize(txt).to(self.device))
            text_features /= text_features.norm(dim=-1, keepdim=True)
        
        return text_features
    
    def vectorize_img(self, img_raw: Image):
        # img_raw = Image.open(img_path)
        img =  self.transform(img_raw) 
        
        with torch.no_grad():
            img_features =  self.model.encode_image(img.to(self.device))
            img_features /= img_features.norm(dim=-1, keepdim=True)
        
        return img_features
    
    def vectorize_frames(self, frames):
        frames_tensor = self.preprocess(frames)
        
        with torch.no_grad():
            frame_features = self.model.encode_image(frames_tensor.to(self.device))
            frame_features /= frame_features.norm(dim=-1, keepdim=True)
        
        return frame_features 

    def preprocess(self, frames):
        if len(frames) > 0:
            return torch.tensor(np.stack(map(self.transform, frames)))
            # return self.transform(np.stack(frames))
        else:
            return torch.zeros(1)
        

    # def vectorize_img_tensor(self, img_tensor: torch.Tensor):
    #     assert isinstance(img_tensor, torch.Tensor)
        
    #     with torch.no_grad():
    #         img_features = self.model.encode_image(img_tensor.to(self.device))
    #         img_features /= img_features.norm(dim=-1, keepdim=True)
        
    #     return img_features
    
    # def vectorize_batched_img(self, images, batch_size):
    #     batches = math.ceil(len(images) / batch_size)

    #     # The encoded features will bs stored in video_features
    #     batched_img_features = torch.empty([0, 512], dtype=torch.float16).to(self.device)

    #     # Process each batch
    #     for i in range(batches):
    #         # print(f"Processing batch {i+1}/{batches}")

    #         # Get the relevant frames
    #         batch_frames = images[i*batch_size : (i+1)*batch_size]

    #         # Preprocess the images for the batch
    #         batch_preprocessed = torch.stack([
    #             self.preprocess(frame) for frame in batch_frames]
    #         ).to(self.devicedevice)

    #         # Encode with CLIP and normalize
    #         with torch.no_grad():
    #             batch_features = self.model.encode_image(batch_preprocessed)
    #             batch_features /= batch_features.norm(dim=-1, keepdim=True)

    #         # Append the batch to the list containing all features
    #         batched_img_features = torch.cat((batched_img_features, batch_features))

    #     # Print some stats
    #     # print(f"Features: {batched_img_features.shape}")
    #     return batched_img_features
        
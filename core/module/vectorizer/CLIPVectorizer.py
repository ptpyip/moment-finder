import math
import torch
import clip

from PIL import Image
from torchvision.transforms import Compose

from .base import BaseVectorizer

class CLIPVectorizer(BaseVectorizer): 
    def __init__(self, model_name="ViT-B/32") -> None:
        self.model_name = model_name
        super().__init__()
    
    def load_model(self, *args):
        self.model, self.preprocess = clip.load(self.model_name, device=self.device)
        
    def vectorize_txt(self, txt:str):
        with torch.no_grad():
            text_features = self.model.encode_text(clip.tokenize(txt).to(self.device))
            text_features /= text_features.norm(dim=-1, keepdim=True)
        
        return text_features
    
    def vectorize_img(self, img_raw: Image):
        # img_raw = Image.open(img_path)
        img =  self.preprocess(img_raw) 
        
        with torch.no_grad():
            img_features =  self.model.encode_image(img.to(self.device))
            img_features /= img_features.norm(dim=-1, keepdim=True)
        
        return img_features

    def vectorize_img_tensor(self, img_tensor: torch.Tensor):
        assert isinstance(img_tensor, torch.Tensor)
        
        with torch.no_grad():
            img_features = self.model.encode_image(img_tensor.to(self.device))
            img_features /= img_features.norm(dim=-1, keepdim=True)
        
        return img_features
    
    def vectorize_batched_img(self, images, batch_size):
        batches = math.ceil(len(images) / batch_size)

        # The encoded features will bs stored in video_features
        batched_img_features = torch.empty([0, 512], dtype=torch.float16).to(self.device)

        # Process each batch
        for i in range(batches):
            # print(f"Processing batch {i+1}/{batches}")

            # Get the relevant frames
            batch_frames = images[i*batch_size : (i+1)*batch_size]

            # Preprocess the images for the batch
            batch_preprocessed = torch.stack([
                self.preprocess(frame) for frame in batch_frames]
            ).to(self.devicedevice)

            # Encode with CLIP and normalize
            with torch.no_grad():
                batch_features = self.model.encode_image(batch_preprocessed)
                batch_features /= batch_features.norm(dim=-1, keepdim=True)

            # Append the batch to the list containing all features
            batched_img_features = torch.cat((batched_img_features, batch_features))

        # Print some stats
        # print(f"Features: {batched_img_features.shape}")
        return batched_img_features
        
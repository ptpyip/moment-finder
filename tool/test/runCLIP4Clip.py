import os

import sys

import clip
import torch
import numpy as np

sys.path.append("/homes/ptpyip/fyp/moment-finder")
from core.module.vectorizer import CLIP4ClipVectorizer

def main():
    clip_model = clip.load("ViT-B/16", "cuda")
    del clip_model
    vec = CLIP4ClipVectorizer(
        "/homes/ptpyip/downloads/ckpts/CLIP4Clip/meanP-ViT-B-16.bin.3",
        model_name="meanP-ViT-B/16"
    )
    
    t = np.zeros((5, 50))      # N, L
    for i in range(5):
        t[i][:(i+1)*10] = [1] * (i+1)*10
        
    T = np.zeros((5, 50, 3, 224, 224))
    T[t==1] = np.random.randn(3, 224, 224)
    tt = torch.tensor(T)
    out = vec.model.clip.encode_image(tt.view(-1, 3, 224, 224))
    print(out.view(tt.size(0), -1, out.size(-1)).shape)
    

    
if __name__ == "__main__":
    main()
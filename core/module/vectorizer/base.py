import torch

from abc import ABC, abstractmethod
from torchvision.transforms import Compose
from PIL import Image

class BaseVectorizer(ABC):
    model: torch.nn.Module
    preprocess: Compose
   
    def __init__(self) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_model()
    
    @abstractmethod
    def load_model(self, *args):
        raise NotImplementedError
    
    ### extend the base class later
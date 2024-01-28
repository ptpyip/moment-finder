import os.path
import torch

from dataclasses import dataclass

from ...momentGen import MomentProposalGenerator
from ...model import CLIPEncoder

from ..utils import VideoExtractor

from .encode import EncodingPipeline

# def upload(video_path):
#     # print(MomentProposalGenerator.__name__)
#     mpg = MomentProposalGenerator(PROPOSAL_OUT_DIR, use_adaptive=True)
#     mpg.generate(video_path)        # output mp4 files stored to PROPOSAL_OUT_DIR 
    
#     ### read from file
#     assert os.path.exists(PROPOSAL_OUT_DIR)
#     proposal_names = [name for name in os.listdir(PROPOSAL_OUT_DIR) if name.endswith(".mp4")]
#     # # print(proposal_names)
    
#     extractor = VideoExtractor()
#     encoder = CLIPEncoder()
    
#     moment_features = []
#     for name in proposal_names:
#         ## read video moments from file
#         proposal_path = os.path.join(PROPOSAL_OUT_DIR, name)
#         moment_tensor = extractor.process_video_data(proposal_path)     # extract to be tensor
        
#         moment_features.append(encoder.encode_img_tensor(moment_tensor))
#     # print(len(moment_features)) 

@dataclass  
class Momemnt:
    name: str
    id: int
    
class moment_feature:
    moment_id: int
    vector: torch.Tensor
    frame: list

# class UploadingPipeline:
#     MOMENT_OUT_DIR = "./proposal"
    
#     moment_generator = MomentProposalGenerator(MOMENT_OUT_DIR, use_adaptive=True) 
#     ep = EncodingPipeline()
    
#     def upload_video_file(self, video_path):
#         assert os.path.exists(video_path)
#         self.moment_generator.generate(video_path)
        
#         moment_features = []
#         for file_name in os.listdir(self.MOMENT_OUT_DIR):
#             if not file_name.endswith(".mp4"):
#                 continue
            
#             moment_path = os.path.join(self.MOMENT_OUT_DIR, file_name)
#             moment_features.append(
#                 self.ep.encode_file(moment_path, return_frames=True)
#             ) 
        
#         ## upload 
        
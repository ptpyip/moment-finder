# import os.path
# from ...momentGen import MomentProposalGenerator
# from ...model import CLIPEncoder

# from ..utils import VideoExtractor

# class EncodingPipeline():
#     extractor = VideoExtractor()
#     encoder = CLIPEncoder()
    
#     def encode_tensor(self, input_tensor):
#         return self.encoder.encode_img_tensor(input_tensor)
                   
#     def encode_file(self, video_path, return_frames=False):
#         assert os.path.exists(video_path)
        
#         input_tensor, frames = self.extractor.video2tensor(video_path, return_frames)
#         return self.encode_tensor(input_tensor), frames if return_frames else []

    
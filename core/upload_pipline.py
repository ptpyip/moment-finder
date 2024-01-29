import os.path

from .utils import video_processing
from .utils import VideoExtractor
from .module.segmenter import ShotDetectSegmenter
from .module.vectorizer import CLIPVectorizer

class UploadPipeline():
    MOMENT_OUT_DIR = "./proposal"
    
    segmenter = ShotDetectSegmenter(MOMENT_OUT_DIR, use_adaptive=True) 
    extractor = VideoExtractor()
    vectorizer = CLIPVectorizer()
      
    def vectorize_moments(self, moment_dir=None):
        if moment_dir is None:
            moment_dir = self.MOMENT_OUT_DIR
        else:
           assert os.path.exists(moment_dir) 
        
        moment_datas = []
        for file_name in os.listdir(moment_dir):
            if not file_name.endswith(".mp4"):
                continue
            
            moment_path = os.path.join(moment_dir, file_name)
            moment_frames = self.extract_frames(moment_path)
            moment_features = self.vectorize_frames(moment_frames)
            
            moment_datas.append({
                "name": file_name,
                "frames":  moment_frames,
                "features": moment_features
            })   
        
        return moment_datas
    
    
    def extract_frames(self, video_path):
        return self.extractor.get_frames(video_path)
    
    def vectorize_frames(self, frames:list):
        tensor = self.extractor.frames2tensor(frames)
        return self.vectorizer.vectorize_img_tensor(tensor)
                   
    def vectorize_file(self, video_path):
        assert os.path.exists(video_path)
        
        frames = self.extractor.get_frames(video_path) 
        tensor = self.extractor.frames2tensor(frames)
        
        return self.vectorizer.vectorize_img_tensor(tensor)
    
    
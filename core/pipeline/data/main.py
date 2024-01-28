import os.path

from ..utils import video_processing
from ..utils import VideoExtractor

from ...momentGen import MomentProposalGenerator
from ...model import CLIPEncoder
from ...vecDB import SupabaseDB


class DataPipeline:
    MOMENT_OUT_DIR = "./proposal"
    
    moment_generator = MomentProposalGenerator(MOMENT_OUT_DIR, use_adaptive=True) 
    extractor = VideoExtractor()
    encoder = CLIPEncoder()
    db = SupabaseDB()
    
    def upload_video_file(self, video_path):
        assert os.path.exists(video_path)
        self.moment_generator.generate(video_path)
        
        moment_datas = []
        for file_name in os.listdir(self.MOMENT_OUT_DIR):
            if not file_name.endswith(".mp4"):
                continue
            
            moment_path = os.path.join(self.MOMENT_OUT_DIR, file_name)
            moment_frames = self.extract_frames(moment_path)
            moment_features = self.encode_frames(moment_frames)
            
            moment_datas.append({
                "name": file_name,
                "frames":  moment_frames,
                "features": moment_features
            })
        
        ## upload 
        
        # create one moment
        # then upload vectors fro each frame for that moment
        for moment in moment_datas:
            
            res = self.db.insert(
                table_name=self.MOMENT_TABLE_NAME,
                data={"name": moment.get("name","")}
            )
                    
            moment_id = res.data[0]["id"]       # may need chane when new db is used?
            
            frames = moment.get("frames", [])
            features = moment.get("features", [])    
            for frame, feature in zip(frames, features):
                frame_base64 = video_processing.encode_img_to_base64(frame)
                
                res = self.db.insert(
                    self.MOMENT_FEATURE_TABLE_NAME,
                    data = {
                        "moment_id": moment_id,
                        "frame_base64": frame_base64.decode("utf-8"),           # need to turn byte to str, as JSON only accept str
                        "vector": feature.tolist()                              # jsn only support list
                    }
                )
         
    
    
    def extract_frames(self, video_path):
        return self.extractor.get_frames(video_path)
    
    
    def encode_frames(self, frames:list):
        tensor = self.extractor.frames2tensor(frames)
        return self.encode_tensor(tensor)
    
    def encode_tensor(self, input_tensor):
        return self.encoder.encode_img_tensor(input_tensor)
                   
    def encode_file(self, video_path):
        assert os.path.exists(video_path)
        
        frames = self.extractor.get_frames(video_path) 
        tensor = self.extractor.frames2tensor(frames)
        
        return self.encode_tensor(tensor)
    
    
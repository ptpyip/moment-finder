import os.path

from .vec_db import SupabaseDB
from .utils import video_processing
from .utils import VideoExtractor
from .module.segmenter import ShotDetectSegmenter
from .module.vectorizer import CLIPVectorizer

def clean_dir(dir):
    for filename in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, filename)):
            os.remove(os.path.join(dir, filename))
    
    return

class UploadPipeline():
    MOMENT_OUT_DIR = "/homes/ptpyip/dev/tmp/proposal"
    
    segmenter = ShotDetectSegmenter(MOMENT_OUT_DIR, use_adaptive=True) 
    extractor = VideoExtractor()
    vectorizer = CLIPVectorizer()
    db = SupabaseDB()
    
    def __init__(self, 
        moment_table_name=None, 
        vector_table_name=None
    ) -> None:
        if not os.path.exists(self.MOMENT_OUT_DIR):
            os.mkdir(self.MOMENT_OUT_DIR)
            
        self.moment_table_name = moment_table_name
        self.vector_table_name = vector_table_name
    
    def upload_video_file(self, video_path):
        assert os.path.exists(video_path)

        clean_dir(self.MOMENT_OUT_DIR)
        timestamp_list = self.segmenter.split(video_path)        ## Split to MOMENT_OUT_DIR
        
        moment_datas = self.vectorize_moments() 
                
        ## upload 
        
        # create one moment
        # then upload vectors fro each frame for that moment
        for moment, timestamp in zip(moment_datas, timestamp_list):
            
            res = self.db.insert(
                table_name=self.moment_table_name,
                data={
                    "name": moment.get("name",""),
                    "timestamp": list(timestamp)
                }        
            )
                    
            moment_id = res.data[0]["id"]       # may need chane when new db is used?
            
            frames = moment.get("frames", [])
            features = moment.get("features", [])    
            for frame, feature in zip(frames, features):
                frame_base64 = video_processing.encode_img_to_base64(frame)
                
                res = self.db.insert(
                    self.vector_table_name,
                    data = {
                        "moment_id": moment_id,
                        "frame_base64": frame_base64.decode("utf-8"),           # need to turn byte to str, as JSON only accept str
                        "vector": feature.tolist(),                              # jsn only support list
                    }
                )
        
        ## clean dir
        
        
      
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
    
    
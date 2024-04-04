import os.path
import tqdm 

from .vec_db import SupabaseDB
from .utils import video_processing
from .utils import VideoExtractor
from .module.segmenter import ShotDetectSegmenter
from .module.vectorizer import CLIPVectorizer, CLIP4ClipVectorizer

def clean_dir(dir):
    for filename in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, filename)):
            os.remove(os.path.join(dir, filename))
    
    return

class UploadPipeline():
    MOMENT_OUT_DIR = "/homes/ptpyip/dev/tmp/proposal"
    
    def __init__(self, 
        moment_table_name=None, 
        vector_table_name=None,
        use_moment_vector=False,
        upload_frame=True
    ) -> None:
        if not os.path.exists(self.MOMENT_OUT_DIR):
            os.mkdir(self.MOMENT_OUT_DIR)
            
        self.moment_table_name = moment_table_name
        self.vector_table_name = vector_table_name
        self.use_moment_vector = use_moment_vector
        
        self.segmenter = ShotDetectSegmenter(self.MOMENT_OUT_DIR, use_adaptive=True) 
        self.extractor = VideoExtractor()
        self.frame_vectorizer = CLIPVectorizer()
        self.moment_vectorizer = CLIP4ClipVectorizer(
           model_name="meanP-ViT-B/16",
           model_path="/csproject/dan3/downloads/ckpts/meanP-ViT-B-16.bin.3"
        ) if use_moment_vector else None
        self.db = SupabaseDB()
        
    def upload_moment_vector(self, video_path, insert_non_existed_moment=False):
        assert os.path.exists(video_path)

        clean_dir(self.MOMENT_OUT_DIR)
        timestamp_list = self.segmenter.split(video_path)        ## Split to MOMENT_OUT_DIR
        
        moment_datas = self.vectorize_moments()
                
        ## upload 
        
        # create one moment
        # then upload vectors fro each frame for that moment
        for moment, timestamp in zip(moment_datas, timestamp_list): 
            moment_id, count = (
                self.db.supabase_client.table(self.moment_table_name)
                    .select("id")
                    .eq("name", moment.get("name",""))
                    .excute()
            )
            
            if count == 0:
                if insert_non_existed_moment:
                    moment_id = self.db.insert(
                        table_name=self.moment_table_name,
                        data={
                            "name": moment.get("name",""),
                            "timestamp": list(timestamp)
                        }        
                    ).data[0]["id"]
                else: 
                    print("moment not found")
                    continue
                
            temporal_vector = moment["vector"]
            res = self.db.update_by_id(
                    self.moment_table_name, 
                    moment_id,
                    data = {
                        "vector": temporal_vector.tolist(),                     # json only support list
                    }
                ) 
        
    
    def upload_video_file(self, video_path):
        assert os.path.exists(video_path)

        clean_dir(self.MOMENT_OUT_DIR)
        timestamp_list = self.segmenter.split(video_path)        ## Split to MOMENT_OUT_DIR
        
        moment_datas = self.vectorize_moments() 
                
        ## upload 
        
        # create one moment
        # then upload vectors fro each frame for that moment
        for moment, timestamp in zip(moment_datas, timestamp_list):
            moment_data = {
                "name": moment.get("name",""),
                "timestamp": list(timestamp),
            } 
            
            if self.use_moment_vector:
                moment_data = moment_data | {"vector": moment.get("vector")}

            res = self.db.insert(
                table_name=self.moment_table_name,
                data=moment_data
                # data={
                #     "name": moment.get("name",""),
                #     "timestamp": list(timestamp),
                # } | {"vector": moment.get("vector")} if self.use_moment_vector else {}
            )
                    
            moment_id = res.data[0]["id"]       # may need chane when new db is used?
            
            frames = moment.get("frames", [])
            features = moment.get("frame_vectors", [])    
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
        for file_name in tqdm.tqdm(os.listdir(moment_dir)):
            if not file_name.endswith(".mp4"):
                continue
            
            moment_path = os.path.join(moment_dir, file_name)
            moment_frames = self.extract_frames(moment_path)
            
            ### vectorize moments
            moment_vector = self.moment_vectorizer.vectorize_moment(moment_frames) if self.use_moment_vector else None
            frame_vectors = self.frame_vectorizer.vectorize_frames(moment_frames)
            
            moment_datas.append({
                "name": file_name,
                "frames":  moment_frames,
                "frame_vectors": frame_vectors,
                "vector": moment_vector
            })   
        
        return moment_datas
    
    
    def extract_frames(self, video_path):
        return self.extractor.get_frames(video_path)
    
    def vectorize_frames(self, frames:list):
        raise NotImplementedError
        # tensor = self.extractor.frames2tensor(frames)
        # return self.vectorizer.vectorize_img_tensor(tensor)
                   
    def vectorize_file(self, video_path):
        assert os.path.exists(video_path)
        
        frames = self.extractor.get_frames(video_path) 
        # tensor = self.extractor.frames2tensor(frames)
        
        return self.vectorizer.vectorize_frames(frames)
    
## test
def test_upload():
    import argparse

    parser = argparse.ArgumentParser("Test Upload Pipeline")
    parser.add_argument("moment_table", type=str)
    parser.add_argument("vector_table", type=str)
    # parser.add_argument("use-moment-vector", action='store_true')
    parser.add_argument("video", type=str)
    args = parser.parse_args()
    
    up = UploadPipeline(args.moment_table,args.vector_table, use_moment_vector=True, upload_frame=False)
    up.upload_video_file(args.video)
    
    print("success")
    # up.upload_video_file(test_upload)
    
    
    
if __name__ == "__main__":
    test_upload()
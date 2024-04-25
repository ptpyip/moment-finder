import os.path
import tqdm 

from .vec_db import SupabaseDB
from .utils import video_processing
from .utils import VideoExtractor
from .module.segmenter import ShotDetectSegmenter
from .module.vectorizer import CLIPVectorizer, CLIP4ClipVectorizer, CLIP4ClipVectorizerV2

def clean_dir(dir):
    for filename in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, filename)):
            os.remove(os.path.join(dir, filename))
    
    return

class UploadPipeline():
    MOMENT_OUT_DIR = "/homes/ptpyip/dev/tmp/proposal"
    
    def __init__(self, 
        moment_table, 
        frame_table,
        clip_name="ViT-B/32",
        clip4clip_name="meanP-ViT-B/16",
        clip4clip_path="/csproject/dan3/downloads/ckpts/meanP-ViT-B-16.bin.3",
        use_moment_vector=False, store_frame=True
    ) -> None:
        if not os.path.exists(self.MOMENT_OUT_DIR):
            os.mkdir(self.MOMENT_OUT_DIR)
            
        self.moment_table = moment_table
        self.frame_table = frame_table
        self.use_moment_vector = use_moment_vector
        self.store_frame = store_frame 
        
        self.db = SupabaseDB()
        self.extractor = VideoExtractor()
        self.segmenter = ShotDetectSegmenter(self.MOMENT_OUT_DIR, use_adaptive=True) 


        clip_path = None
        if clip_name == clip4clip_name:
            """ use clip4clip's clip"""
            clip_path = clip4clip_path
        self.frame_vectorizer = CLIPVectorizer(clip_name, clip_path)
        self.moment_vectorizer = CLIP4ClipVectorizerV2() if use_moment_vector else None
        # self.moment_vectorizer = CLIP4ClipVectorizer(
        #    clip4clip_name, clip4clip_path
        # ) if use_moment_vector else None
               
        return    
    
    
    def upload_video_file(self, video_path):
        assert os.path.exists(video_path) 
        clean_dir(self.MOMENT_OUT_DIR)
        
        video_segments = self.segmenter.split(video_path)
        return self.upload_video_segments(video_segments)
         
    def upload_video_segments(self, segments: list[tuple[str, float, float]]):
        """
        1. extract frame from video splits
        2. vectorize moment
        3. insert moment to db
        4. insert frames to db
        """
        for segment_path, *timestamp in tqdm.tqdm(segments):

            frames = self.extract_frames(segment_path)
            
            ### vectorize moment
            moment_vector = self.moment_vectorizer.vectorize_moment(frames) if self.use_moment_vector else None
            frame_vectors = self.vectorize_frames(frames) 
            
            if moment_vector is not None:
                """TODO: 
                    - Additional logic to merge moments
                """
                pass
            
            ### insert moment
            res = self.db.insert(self.moment_table, {
                "name": segment_path.rsplit("/", 1)[-1].rsplit(".", 1)[0],       # output_dir/$VIDEO_NAME-Scene-$SCENE_NUMBER.mp4 -> $VIDEO_NAME-Scene-$SCENE_NUMBER
                "timestamp": list(timestamp),
                "vector": moment_vector.tolist() if self.use_moment_vector else None      # type: ignore
            })
            moment_id = res.data[0]["id"]  

            for i, vector in enumerate(frame_vectors):
                if self.store_frame:
                    frame = video_processing.encode_img_to_base64(frames[i]).decode("utf-8")
                else:
                    frame = None
                    
                res = self.db.insert(self.frame_table, {
                        "moment_id": moment_id,
                        "frame_base64": frame,           # need to turn byte to str, as JSON only accept str
                        "vector": vector.tolist(),                              # jsn only support list
                    }
                )
                
        return
    
    
    def extract_frames(self, video_path):
        return self.extractor.get_frames(video_path)
    
    
    def vectorize_frames(self, frames:list):
        """TODO: additional logic to filter frame_vector"""
        return self.frame_vectorizer.vectorize_frames(frames)
        
                   
    # def vectorize_file(self, video_path):
    #     assert os.path.exists(video_path)
        
    #     frames = self.extractor.get_frames(video_path) 
    #     # tensor = self.extractor.frames2tensor(frames)
        
    #     return self.vectorizer.vectorize_frames(frames)
    
    
    
        
    # def upload_moment_vector(self, video_path, insert_non_existed_moment=False):
        """ stand a lone upload NOT USED """
    #     assert os.path.exists(video_path)

    #     clean_dir(self.MOMENT_OUT_DIR)
    #     ## Split to MOMENT_OUT_DIR
    #     timestamp_list = self.segmenter.split(video_path)        
    #     moment_datas = self.vectorize_moments()
        
    #     for moment, timestamp in zip(moment_datas, timestamp_list): 
    #         moment_id, count = (self.db.supabase_client.table(self.moment_table)
    #                 .select("id")
    #                 .eq("name", moment.get("name",""))
    #                 .excute()
    #         )
            
    #         if count == 0:
    #             if insert_non_existed_moment:
    #                 moment_id = self.db.insert(
    #                     table=self.moment_table,
    #                     data={
    #                         "name": moment.get("name",""),
    #                         "timestamp": list(timestamp)
    #                     }        
    #                 ).data[0]["id"]
    #             else: 
    #                 print("moment not found")
    #                 continue
                
    #         temporal_vector = moment["vector"]
    #         res = self.db.update_by_id(
    #                 self.moment_table, 
    #                 moment_id,
    #                 data = {
    #                     "vector": temporal_vector.tolist(),                     # json only support list
    #                 }
    #             ) 
    
## test
def test_upload():
    import argparse

    parser = argparse.ArgumentParser("Test Upload Pipeline")
    parser.add_argument("--moment-table", type=str)
    parser.add_argument("--vector-table", type=str)
    parser.add_argument("--use-moment-vector", action='store_true')
    parser.add_argument("--video", type=str)
    args = parser.parse_args()
    
    up = UploadPipeline(args.moment_table,args.vector_table, use_moment_vector=True, upload_frame=False)
    up.upload_video_file(args.video)
    
    print("success")
    # up.upload_video_file(test_upload)
    
    
    
if __name__ == "__main__":
    test_upload()
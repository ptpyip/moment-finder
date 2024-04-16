"""
To compare the retrival time of our method and others, we conduct the following test
using QVHiglight.
1. Test naive clip
2. Test naive clip with Vector DB
3. Test ours 
4. Test SOTA ( MomentDETR, or even forzen ) 
"""
import os
import time
import tqdm
import clip
import torch
from sentence_transformers.util import cos_sim

# from core import UploadPipeline, RetrievalPipeline
from core.module.segmenter import ShotDetectSegmenter
from core.utils import VideoExtractor
from tool.utils import load_jsonl
from tool.eval.qvhighlight import retrieve_video_using_dataset_prompt

MOMENT_OUT_DIR = "test/proposal"

def test_naive_clip(
    data_dir="/home/ptpyip/fyp/datasets/qvhighlights", 
    video_dir="/data/qvhighlights/",
    number_of_query=0.1
):
    segmenter = ShotDetectSegmenter(MOMENT_OUT_DIR, use_adaptive=True) 
    extractor = VideoExtractor()
    vectorizer, _ = clip.load("ViT-B/16")

    video_dir = data_dir if video_dir is None else video_dir
    data_path = os.path.join(data_dir, "highlight_val_release.jsonl")
    assert os.path.exists(data_path)
    
    data_list = tuple(load_jsonl(data_path))
    if isinstance(number_of_query, float):
        # get the portion of val data set.
        number_of_query = int(len(data_list) * number_of_query)
        
    # print(number_of_query)
    data_list = data_list[:number_of_query]
    
    for data in data_list:
        # print(data)
        # # break
        vid = data.get("vid") 
        video_path = os.path.join(data_dir. video, f"{vid}.mp4")
        assert os.path.exists(video_path)
        
        query = data.get("query")
        query_vector = vectorizer.encode_text(query)
        
        ## 1. segment moment
        segmenter.clean_dir(MOMENT_OUT_DIR)
        timestamp_list = segmenter.split(video_path)        ## Split to MOMENT_OUT_DIR
        
        ## 2. extract frames from vid
        for segment_path, *timestamp in tqdm.tqdm(timestamp_list):
            frames = extractor.extract_frames(segment_path)
            
            ### vectorize moment
            frame_vectors = vectorizer.encode_image(frames) 
            cos_scores = cos_sim(query_vector, frame_vectors)[0]
            top_results = torch.topk(cos_scores, k=5)
                       
                
        return
    
def test_rp():
    start_time = time.time()
    print(start_time)
    retrieve_video_using_dataset_prompt("/home/ptpyip/fyp/datasets/qvhighlights/test_time.jsonl", eval=False, verbose = False,)
    end_time = time.time()
    print(end_time)

    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time:.6f} seconds")
    
    
        
if __name__ == "__main__":
    # test_naive_clip(number_of_query=15)
    # test_naive_clip(number_of_query=0.1)
    test_rp()
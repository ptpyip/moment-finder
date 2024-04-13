"""
To compare the retrival time of our method and others, we conduct the following test
using QVHiglight.
1. Test naive clip
2. Test naive clip with Vector DB
3. Test ours 
4. Test SOTA ( MomentDETR, or even forzen ) 
"""
import os
# from core import UploadPipeline, RetrievalPipeline
from core.module.segmenter import ShotDetectSegmenter
from core.utils import VideoExtractor
from tool.utils import load_jsonl

MOMENT_OUT_DIR = "test/proposal"

def test_naive_clip(
    data_dir="/home/ptpyip/fyp/datasets/qvhighlights", 
    video_dir="/data/qvhighlights/",
    number_of_query=0.1
):
    segmenter = ShotDetectSegmenter(MOMENT_OUT_DIR, use_adaptive=True) 
    extractor = VideoExtractor()
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
        
        ## 1. segment moment
        segmenter.clean_dir(MOMENT_OUT_DIR)
        timestamp_list = segmenter.split(video_path)        ## Split to MOMENT_OUT_DIR
        
        ## 2. extract frames from vid
        
if __name__ == "__main__":
    # test_naive_clip(number_of_query=15)
    test_naive_clip(number_of_query=0.1)
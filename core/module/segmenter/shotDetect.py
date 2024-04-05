"""
Method from Zero-shot Video Moment Retrieval With Off-the-Shelf Models (https://arxiv.org/abs/2211.02178)
@misc{diwan2022zeroshot,
      title={Zero-shot Video Moment Retrieval With Off-the-Shelf Models}, 
      author={Anuj Diwan and Puyuan Peng and Raymond J. Mooney},
      year={2022},
      eprint={2211.02178},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}
"""

import os

from typing import List, Tuple

import scenedetect
from scenedetect.detectors import AdaptiveDetector, ContentDetector
from scenedetect import video_splitter
from scenedetect import split_video_ffmpeg

from .base import BaseVideoSegmenter

class ShotDetectSegmenter(BaseVideoSegmenter):
    """
    Segment videos using  shot trainsition Detection
    """
    
    def __init__(self,
        output_dir,
        use_adaptive=False,
        content_threshold=53,
        adaptive_threshold=3,
        min_scene_len = 15
    ) -> None:
        assert video_splitter.is_ffmpeg_available()
        
        self.content_threshold = content_threshold
        
        self.output_file_template = f'{output_dir}/$VIDEO_NAME-Scene-$SCENE_NUMBER.mp4'  
          
        ### create detector for each split.
        self.use_adaptive = use_adaptive
        self.Detector = lambda self: AdaptiveDetector(
            adaptive_threshold, min_content_val=self.content_threshold
        ) if self.use_adaptive else ContentDetector(self.content_threshold)

        # self.detector = AdaptiveDetector(adaptive_threshold, min_content_val=content_threshold) if use_adaptive else ContentDetector(content_threshold)
        # self.detector = ContentDetector(content_threshold)
        
    def split(self, input_video_path, show_progress=True) -> List[Tuple[float, float]]:
        # output_dir = remove_suffix(output_dir,'/')
        # if not os.path.exists(output_dir):
        #     os.mkdir(output_dir)
        
        detector = self.Detector()      # create detector for each split.
        scene_list = scenedetect.detect(input_video_path, detector, show_progress=True)
        # print(scene_list)
        try:
            split_video_ffmpeg(input_video_path, scene_list, self.output_file_template, show_progress=show_progress)
        except AssertionError as err:
            print(err)
            return []
        return self.parse_scene_list(scene_list)
    
    def parse_scene_list(self, scene_list) -> List[Tuple[float, float]]:
        return [(scene[0].get_seconds(), scene[1].get_seconds()) for scene in scene_list]
       
    @staticmethod
    def parse_video_name(moment_dir) -> str:
        moment_file_name = moment_dir.split("/")[-1]
        moment_name = moment_file_name.rsplit(".mp4", 1)[0]
        video_name = moment_name.split("-Scene-", 1)[0]
        
        return video_name
        
        
### helper funcions
def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string
        
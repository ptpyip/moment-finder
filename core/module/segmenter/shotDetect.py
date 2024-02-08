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
        
        self.output_file_template = f'{output_dir}/$VIDEO_NAME-Scene-$SCENE_NUMBER.mp4'    
        self.detector = AdaptiveDetector(adaptive_threshold, min_content_val=content_threshold) if use_adaptive else ContentDetector(content_threshold)
        
    def split(self, input_video_path, show_progress=True) -> List[Tuple[float, float]]:
        # output_dir = remove_suffix(output_dir,'/')
        # if not os.path.exists(output_dir):
        #     os.mkdir(output_dir)
        scene_list = scenedetect.detect(input_video_path, self.detector)
        split_video_ffmpeg(input_video_path, scene_list, self.output_file_template, show_progress=show_progress)

        return self.parse_scene_list(scene_list)
    
    def parse_scene_list(scene_list) -> List[Tuple[float, float]]:
        return [(scene[0].get_seconds(), scene[1].get_seconds()) for scene in scene_list]
        
### helper funcions
def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string
        
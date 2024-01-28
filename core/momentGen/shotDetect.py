"""
use short trainsition Detection to split videos
"""

import os

import scenedetect
from scenedetect.detectors import AdaptiveDetector, ContentDetector
from scenedetect import video_splitter
from scenedetect import split_video_ffmpeg

class MomentProposalGenerator:
    
    def __init__(self,
        output_dir,
        use_adaptive=False,
        content_threshold=53,
        adaptive_threshold=3,
        min_scene_len = 15
    ) -> None:
        assert video_splitter.is_ffmpeg_available()
        
        output_dir = __remove_suffix(output_dir,'/')
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        
        self.output_file_template = f'{output_dir}/$VIDEO_NAME-Scene-$SCENE_NUMBER.mp4'    
        self.detector = AdaptiveDetector(adaptive_threshold, min_content_val=content_threshold) if use_adaptive else ContentDetector(content_threshold)
        
    def generate(self, input_video_path, show_progress=True):
        scene_list = scenedetect.detect(input_video_path, self.detector)
        split_video_ffmpeg(input_video_path, scene_list, self.output_file_template, show_progress=show_progress)
        
### helper funcions
def __remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string
        
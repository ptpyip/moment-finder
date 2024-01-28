
from PIL import Image
from dataclasses import dataclass

@dataclass
class Video:
    path: str
    fps: int
    frames: list
    frames_feature: list
    
    # def __init__(self, path_to_video, num_of_skip_frames=10) -> None:
    #     self.path = path_to_video
    #     self.frames, self.fps = get_frames(path_to_video)
    #     self.frames_feature = get_video_feature(self.frames)

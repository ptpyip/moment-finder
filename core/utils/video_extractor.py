import os
import cv2
import torch as th
import numpy as np

from PIL import Image
from einops import rearrange
from contextlib import contextmanager
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize

class RawVideoExtractorCV2():
    """
    Convert video data (.mp4) into tensors
    """
    def __init__(self, size=224, framerate=1, centercrop=False, max_num_frames=None):
        self.centercrop = centercrop
        self.size = size
        self.framerate = framerate                              # if frame_rate == video fps => encode all frame.
        self.transform = self._transform(self.size)
        self.max_num_frames = max_num_frames
        
    def video2tensor(self, video_path, start_time=None, end_time=None, sample_fps=0, return_frames=False):
        frames = self.get_frames(video_path, start_time, end_time, sample_fps)
                    
        return self.frames2tensor(frames), frames if return_frames else []
    
    def frames2tensor(self, frames: list):
        if len(frames) > 0:
            return th.tensor(np.stack(map(self.transform, frames)))
            # return self.transform(np.stack(frames))
        else:
            return th.zeros(1)

    def get_frames(self, video_path, start_time=None, end_time=None, sample_fps=0):
        ### validate input
        if start_time is not None or end_time is not None:
            assert isinstance(start_time, int) and isinstance(end_time, int) \
                   and start_time > -1 and end_time > start_time
                   

        if sample_fps == 0: sample_fps = self.framerate
        assert sample_fps > -1
        
        with self.open_video_file(video_path, sample_fps) as cap:
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            total_duration = (frame_count + fps - 1) // fps
            start_sec, end_sec = 0, total_duration

            if start_time is not None:
                start_sec, end_sec = start_time, end_time if end_time <= total_duration else total_duration
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(start_time * fps))

            interval = 1
            if sample_fps > 0:
                interval = fps // sample_fps
            else:
                sample_fps = fps
            if interval == 0: interval = 1

            inds = [ind for ind in np.arange(0, fps, interval)]
            assert len(inds) >= sample_fps
            inds = inds[:sample_fps]

            ret = True
            images, included = [], []

            for sec in np.arange(start_sec, end_sec + 1):
                if not ret: break
                sec_base = int(sec * fps)
                for ind in inds:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, sec_base + ind)
                    ret, frame = cap.read()
                    if not ret: break
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # images.append(self.transform(Image.fromarray(frame_rgb).convert("RGB")))
                    
                    images.append(Image.fromarray(frame_rgb).convert("RGB"))
                    
        return images # fix: get rgb img
 
        
    @contextmanager
    def open_video_file(self, video_path, sample_fps):
        assert os.path.exists(video_path)
            
        # Samples a frame sample_fps X frames.
        cap = cv2.VideoCapture(video_path)
        yield cap
        cap.release()
         

    def _transform(self, n_px):
        return Compose([
            Resize(n_px, interpolation=Image.BICUBIC),
            CenterCrop(n_px),
            lambda image: image.convert("RGB"),
            ToTensor(),
            Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
        ])

    def video_to_tensor(self, video_file, preprocess, sample_fp=0, start_time=None, end_time=None):
        if start_time is not None or end_time is not None:
            assert isinstance(start_time, int) and isinstance(end_time, int) \
                   and start_time > -1 and end_time > start_time
        assert sample_fp > -1

        # Samples a frame sample_fp X frames.
        cap = cv2.VideoCapture(video_file)
        frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        total_duration = (frameCount + fps - 1) // fps
        start_sec, end_sec = 0, total_duration

        if start_time is not None:
            start_sec, end_sec = start_time, end_time if end_time <= total_duration else total_duration
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(start_time * fps))

        interval = 1
        if sample_fp > 0:
            interval = fps // sample_fp
        else:
            sample_fp = fps
        if interval == 0: interval = 1

        inds = [ind for ind in np.arange(0, fps, interval)]
        assert len(inds) >= sample_fp
        inds = inds[:sample_fp]

        ret = True
        images, included = [], []

        for sec in np.arange(start_sec, end_sec + 1):
            if not ret: break
            sec_base = int(sec * fps)
            for ind in inds:
                cap.set(cv2.CAP_PROP_POS_FRAMES, sec_base + ind)
                ret, frame = cap.read()
                if not ret: break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                images.append(preprocess(Image.fromarray(frame_rgb).convert("RGB")))

        cap.release()

        if len(images) > 0:
            tensor_data = th.tensor(np.stack(images))
        else:
            tensor_data = th.zeros(1)
        return {'video': tensor_data}

    def get_video_data(self, video_path, start_time=None, end_time=None):
        image_input = self.video_to_tensor(video_path, self.transform, sample_fp=self.framerate, start_time=start_time, end_time=end_time)
        return image_input

    def process_raw_data(self, raw_video_data):
        tensor_size = raw_video_data.size()
        tensor = raw_video_data.view(-1, 1, tensor_size[-3], tensor_size[-2], tensor_size[-1])
        return tensor
    
    def process_video_data(self, video_path, start_time=None, end_time=None) -> th.Tensor:
        raw_video_data = self.get_video_data(video_path, start_time, end_time)["video"]     # returns dict
        tensor_size = raw_video_data.size()
        # tensor = raw_video_data.view(-1, 1, tensor_size[-3], tensor_size[-2], tensor_size[-1])      # L x T x 3 x H x W
       
        tensor = raw_video_data.view(-1, tensor_size[-3], tensor_size[-2], tensor_size[-1]) 
        return tensor  # L x 3 x H x W

    def process_frame_order(self, raw_video_data, frame_order=0):
        # 0: ordinary order; 1: reverse order; 2: random order.
        if frame_order == 0:
            pass
        elif frame_order == 1:
            reverse_order = np.arange(raw_video_data.size(0) - 1, -1, -1)
            raw_video_data = raw_video_data[reverse_order, ...]
        elif frame_order == 2:
            random_order = np.arange(raw_video_data.size(0))
            np.random.shuffle(random_order)
            raw_video_data = raw_video_data[random_order, ...]

        return raw_video_data

# An ordinary video frame extractor based CV2
# RawVideoExtractor = RawVideoExtractorCV2
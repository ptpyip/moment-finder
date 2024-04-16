import os
from abc import ABC

class BaseVideoSegmenter(ABC):
    """
    Segment a source video temporally into distinct moments
    """

    @staticmethod
    def clean_dir(dir):
        for filename in os.listdir(dir):
            if os.path.isfile(os.path.join(dir, filename)):
                os.remove(os.path.join(dir, filename))
        
        return
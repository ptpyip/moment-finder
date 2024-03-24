import os
from typing import Any, Union, List

import torch
from clip.simple_tokenizer import SimpleTokenizer as Tokenizer
from clip.clip import _transform

# from .model import build_model
from .model import CLIP4Clip

GPU_CKPTS_DIR = "/csproject/dan3/downloads/ckpts"
CPU_CKPTS_DIR = ""

MODELS = [
    "meanP-ViT-B/16","meanP-ViT-B/32",
    # "Trans-ViT-B/16","Trans-ViT-B/32"
]

# tokenizer = Tokenizer()

def load(path: str, model_name="meanP-ViT-B/16", device="cpu"):
    """Load a CLIP4Clip model for inference"""
    assert model_name in MODELS
    if not os.path.exists(path):
        raise RuntimeError(f"Model {model_name} not found with path: {path}")
        # return None
    
    state_dict = torch.load(path, map_location="cpu")
    
    clip_name = model_name.split("-", 1)[1]
    model = CLIP4Clip(clip_name)
    model.load_state_dict(state_dict)
    model.to(device).float().eval()
    
    return model, _transform(model.input_resolution)

# def preprocess(frames: list):
#     """convert list of frames into tensor + mask"""
#     # if frames
#     ...
    

# def _transform(n_px):
#     return Compose([
#         Resize(n_px, interpolation=BICUBIC),
#         CenterCrop(n_px),
#         _convert_image_to_rgb,
#         ToTensor(),
#         Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
#     ])

# def tokenize(
#     texts: Union[str, List[str]], 
#     context_length: int = 77, 
#     truncate: bool = False
# # ) -> Union[torch.IntTensor, torch.LongTensor]:
# ) -> torch.LongTensor:
#     """
#     Returns the tokenized representation of given input string(s)

#     Parameters
#     ----------
#     texts : Union[str, List[str]]
#         An input string or a list of input strings to tokenize

#     context_length : int
#         The context length to use; all CLIP models use 77 as the context length

#     truncate: bool
#         Whether to truncate the text in case its encoding is longer than the context length

#     Returns
#     -------
#     A two-dimensional tensor containing the resulting tokens, shape = [number of input strings, context_length].
#     We return LongTensor when torch version is <1.8.0, since older index_select requires indices to be long.
#     """
#     if isinstance(texts, str):
#         texts = [texts]

#     sot_token = tokenizer.encoder["<|startoftext|>"]
#     eot_token = tokenizer.encoder["<|endoftext|>"]
#     all_tokens = [[sot_token] + tokenizer.encode(text) + [eot_token] for text in texts]
    
#     result = torch.zeros(len(all_tokens), context_length, dtype=torch.long)
#     # if packaging.version.parse(torch.__version__) < packaging.version.parse("1.8.0"):
#     #     result = torch.zeros(len(all_tokens), context_length, dtype=torch.long)
#     # else:
#     #     result = torch.zeros(len(all_tokens), context_length, dtype=torch.int)

#     for i, tokens in enumerate(all_tokens):
#         if len(tokens) > context_length:
#             if truncate:
#                 tokens = tokens[:context_length]
#                 tokens[-1] = eot_token
#             else:
#                 raise RuntimeError(f"Input {texts[i]} is too long for context length {context_length}")
#         result[i, :len(tokens)] = torch.tensor(tokens)

#     return result
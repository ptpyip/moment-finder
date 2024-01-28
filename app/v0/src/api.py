from dataclasses import dataclass
from PIL.Image import Image

from .vecDB import WeaviateDB
from .CLIP import get_text_features

# vec_db = WeaviateDB()

def simple_video_search(vec_db, search_query, k=1) -> str:
    print(f"Search Query: {search_query}")
    
    query_vector = get_text_features(search_query)
    results = vec_db.fetch_frame_with_vec(query_vector, k)
    
    for i, result in enumerate(results):
        print(f"[{i}] ({result['certainty']}): {result['videoLoc']}")
        
    return None
    # print()




# @dataclass
# class Video:
#     ...

# def video_search_API(tgt_movie, search_query) -> list[Image]:
#     validate_inputs(search_query, tgt_movie) 
#     query = preprocess_query(search_query)
    
#     # with get_video_with_name(name=tgt_movie) as movie:
#     movie = get_video_with_name(name=tgt_movie)
#     result_frame_ids = retrieve_scene_from_video(movie, query)
    
#     result_frames: list[Image] = [
#         get_frame_from_video_with_id(movie, frame_id)
#         for frame_id in result_frame_ids
#     ]
        
#     return result_frames


# def validate_inputs(*inputs):
#     print(inputs)


# def preprocess_query(query: str) -> str:
#     print("Preprocessing ...")
#     # do sth
#     return query


# def get_video_with_name(name: str) -> Video:
#     print("Getting target video with name attribute ...")
#     return 
    

# def retrieve_scene_from_video(video: Video, query: str) -> [int]:
#     """return frame_id"""
#     print("Retrieving scene from video using Vector DB ...")
#     frame_ids = None
#     return frame_ids


# def get_frame_from_video_with_id(video: Video, frame_id: int) -> Image:
#     print("Getting frame with ID attribute ")
#     return 

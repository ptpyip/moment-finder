import argparse

from src.vecDB import WeaviateDB
from app import gradio_app
from src.CLIP import get_text_features

def get_args(description='Video Retrieve System'):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--vec_db", type=str, help='the database url')
    parser.add_argument("--test-import", 
        action='store_true', help='set the flag to test import.'
    )
    
    return parser.parse_args()


def simple_video_search(vec_db, search_query, k=1) -> str:
    print(f"Search Query: {search_query}")
    
    query_vector = get_text_features(search_query)
    results = vec_db.fetch_frame_with_vec(query_vector, k)
    
    for i, result in enumerate(results):
        print(f"[{i}] ({result['certainty']}): {result['videoLoc']}")
        
    return results[0]["videoLoc"]


def main():
    args = get_args()
    
    if args.test_import:
        """ Note: when calling sub-package, remember for parent package to use the . syntax"""
        print("success!")
        return

    vec_databases = {
        # "WebVid-2k-CLIP": WeaviateDB(host_url=args.vec_db),
        "MSVD-YouTubeClip-CLIP": WeaviateDB(host_url=args.vec_db)
    }
    app = gradio_app(vec_databases)
    app.launch(server_name="0.0.0.0", server_port=8080)
    
if __name__ == "__main__":
    main()

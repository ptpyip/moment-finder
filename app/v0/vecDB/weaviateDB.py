import torch
import weaviate

WEAVIATE_URL = "http://vml1wk132.cse.ust.hk:8080"
WEAVIATE_HEADERS = {'Content-Type': 'application/json'}

class WeaviateDB:
    def __init__(self, host_url=WEAVIATE_URL) -> None:
        self.client = weaviate.Client(host_url)

    def make_query(self, vector, k) -> dict:
        return self.client.query.get("Frame", 
            ["description", "videoLoc"]
        ).with_near_vector(
            {
                "vector":vector
            }
        ).with_additional(
            ["certainty", "vector"]
        ).with_limit(k).do()
    
    
    def fetch_frame_with_vec(self, quey_vector: torch.Tensor, k=3):
        # query_vector = get_text_features(input_query).tolist()[0]
        # res = make_query(query_vector)
        
        results = self.client.query.get("Frame", 
            ["description", "videoLoc"]
        ).with_near_vector(
            {
                "vector":quey_vector.tolist()[0]        # 1-dim list
            }
        ).with_additional(
            ["certainty", "vector"]
        ).with_limit(k).do()
        
        frames = []
        for frame in results["data"]["Get"]["Frame"]:
            frames.append({
                "description": frame["description"],
                "certainty": frame["_additional"]["certainty"],
                "videoLoc": frame["videoLoc"]
            })
            
        return frames
    
    
    def fetch_frame_with_txt(self, quey_txt, k=3):
        # res = make_query(query_vector)
        
        results = self.client.query.get("Frame", 
            ["description", "videoLoc"]
        ).with_near_text(
            {
                "content":quey_txt
            }
        ).with_additional(
            ["certainty", "vector"]
        ).with_limit(k).do()
        
        frames = []
        for frame in results["data"]["Get"]["Frame"]:
            frames.append({
                "description": frame["description"],
                "certainty": frame["_additional"]["certainty"],
                "videoLoc": frame["videoLoc"]
            })
            
        return frames
    
if __name__ == "__main__":
    
    import torch, clip
    # Load the open CLIP model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    def get_text_features(txt_query: str):
        with torch.no_grad():
            text_features = model.encode_text(clip.tokenize(txt_query).to(device))
            text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features

    input_query = input("Please enter your query:")
    query_vector = get_text_features(input_query)
    
    db = WeaviateDB()
    result = db.fetch_frame_with_vec(query_vector)
    print(result)
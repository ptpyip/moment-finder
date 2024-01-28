import math
import cv2
import clip
import torch

from PIL import Image

class Video:
    path: str
    fps: int
    frames: list
    frames_feature: list
    
    def __init__(self, path_to_video, num_of_skip_frames=10) -> None:
        self.path = path_to_video
        self.frames, self.fps = get_frames(path_to_video)
        self.frames_feature = get_video_feature(self.frames)

# Load the open CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def get_text_features(txt_query: str):
    with torch.no_grad():
        text_features = model.encode_text(clip.tokenize(txt_query).to(device))
        text_features /= text_features.norm(dim=-1, keepdim=True)
    
    return text_features
    
def get_img_features(img_raw: Image):
    # img_raw = Image.open(img_path)
    img =  preprocess(img_raw) 
    
    with torch.no_grad():
        img_features =  model.encode_image(img.to(device))
        img_features /= img_features.norm(dim=-1, keepdim=True)
    
    return img_features

def get_frames(path_to_video: str, num_of_skip_frames=10) -> tuple[list, int]:
    video_frames = []

    # Open the video file
    capture = cv2.VideoCapture(path_to_video)
    fps = capture.get(cv2.CAP_PROP_FPS)

    current_frame = 0
    while capture.isOpened():
        ret, frame = capture.read()

        # Convert it to a PIL image (required for CLIP) and store it
        if ret == True:
            video_frames.append(Image.fromarray(frame[:, :, ::-1]))
        else:
            break

    # Skip N frames
    current_frame += num_of_skip_frames
    capture.set(cv2.CAP_PROP_POS_FRAMES, current_frame)

    print(f"Frames extracted: {len(video_frames)}")
    return video_frames, fps

def get_video_feature(video_frames, batch_size):
    batches = math.ceil(len(video_frames) / batch_size)

    # The encoded features will bs stored in video_features
    video_features = torch.empty([0, 512], dtype=torch.float16).to(device)

    # Process each batch
    for i in range(batches):
        print(f"Processing batch {i+1}/{batches}")

        # Get the relevant frames
        batch_frames = video_frames[i*batch_size : (i+1)*batch_size]

        # Preprocess the images for the batch
        batch_preprocessed = torch.stack([preprocess(frame) for frame in batch_frames]).to(device)

        # Encode with CLIP and normalize
        with torch.no_grad():
            batch_features = model.encode_image(batch_preprocessed)
            batch_features /= batch_features.norm(dim=-1, keepdim=True)

        # Append the batch to the list containing all features
        video_features = torch.cat((video_features, batch_features))

    # Print some stats
    print(f"Features: {video_features.shape}")
    return video_features

def search_video(search_query, video: Video, k=3):

    # Encode and normalize the search query using CLIP
    text_features = get_text_features(search_query)

    # Compute the similarity between the search query and each frame using the Cosine similarity
    similarities = (100.0 * video.frames_feature @ text_features.T)
    values, best_photo_idx = similarities.topk(k, dim=0)
    
    return values, best_photo_idx

    # # Display the top 3 frames
    # for frame_id in best_photo_idx:
    #     display(video.frames[frame_id])

    #     # Find the timestamp in the video and display it10
    #     seconds = round(frame_id.cpu().numpy()[0] *  10 / fps)


def search_video(search_query, frame_features: torch.Tensor, k=3):

    # Encode and normalize the search query using CLIP
    text_features = get_text_features(search_query)

    # Compute the similarity between the search query and each frame using the Cosine similarity
    similarities = (100.0 * frame_features @ text_features.T)       # Tensor dot product
    values, best_photo_idx = similarities.topk(k, dim=0)
    
    return values, best_photo_idx

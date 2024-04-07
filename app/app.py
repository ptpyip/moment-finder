import gradio as gr
import base64
from PIL import Image
from io import BytesIO
from core import RetrievalPipeline

def base64_to_image(base64_str):
    decoded_image = base64.b64decode(base64_str)
    img = Image.open(BytesIO(decoded_image))
    return img


def video_search(search_query, k=3): 
    print(f"Search Query: {search_query}")

    pipeline = RetrievalPipeline()
    moments = pipeline.retrieve_moments(search_query, k)
    supabase_moments = pipeline.retrieve_base64_by_ids([moment[0] for moment in moments])

    images = []
    for s_moment in supabase_moments:
        img = base64_to_image(s_moment)
        print(img)
        images.append(img)
    
    distances = []
    for moment in moments:
        cos_dist = moment[3]
        print(cos_dist)
        distances.append(cos_dist)

    # return images and similarity scores
    return images[0], images[1], images[2], distances[0], distances[1], distances[2]

    # this is format of moments: [(18112, 'K5PTawokTA4_360.0_510.0-Scene-002.mp4', [0.934267, 21.4214], 0.679151737335596), (16138, 'smUAWKLhWnA_360.0_510.0-Scene-002.mp4', [0.633333, 13.2333], 0.679372013757325), ... ]
    # first element is moment_id
    # second element is video_name
    # third element is timestamp
    # fourth element is cosine distance
    # I want to reformat moment, such that:
    # 1. first element is moment_id
    # 2. second element is youtube_video_id (e.g for the first moment, it should be K5PTawokTA4)
    # 3. third element is timestamp but with modification (e.g for the first moment, it should be [360.0 + 0.934267, 360.0 + 21.4214])
    # 4. fourth element is cosine distance

    # reformat moments
    # reformatted_moments = []
    # moment_ids = []
    # for moment in moments:
    #     moment_id = moment[0]
    #     video_name = moment[1]
    #     youtube_video_id = video_name.split("_")[0]        
    #     youtube_start_time = float(video_name.split("_")[1])
    #     timestamp = moment[2]
    #     start_time = timestamp[0] + youtube_start_time
    #     end_time = timestamp[1] + youtube_start_time
    #     cos_dist = moment[3]

    #     reformatted_moments.append([moment_id, youtube_video_id, [start_time, end_time], cos_dist])

    # return reformatted_moments


def video_search_with_id(video_id, search_query, k=3):
    print(f"Search Query: {search_query}")
    print(f"Video ID: {video_id}")

    pipeline = RetrievalPipeline()
    moments = pipeline.retrieve_moments_by_video_id(video_id, search_query, k)
    supabase_moments = pipeline.retrieve_base64_by_ids([moment[0] for moment in moments])

    images = []
    for s_moment in supabase_moments:
        img = base64_to_image(s_moment)
        print(img)
        images.append(img)
    
    distances = []
    for moment in moments:
        cos_dist = moment[3]
        print(cos_dist)
        distances.append(cos_dist)
    
    return images[0], images[1], images[2], distances[0], distances[1], distances[2]
    

def gradio_app():
    with gr.Blocks() as app:
        gr.Markdown("## Moment Finder")
        with gr.Tab("Search Video"):
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        search_query = gr.Textbox(
                            label="Enter your prompt",
                            max_lines=1,
                            placeholder="Enter your prompt",
                            container=False,
                            scale=4
                        )
                        btn = gr.Button("Search a video", scale=1)
                
                with gr.Column():
                    image1_output = gr.Image(label="Image 1")
                    text1_output = gr.Textbox(label="Cosine Distance 1")
                    image2_output = gr.Image(label="Image 2")
                    text2_output = gr.Textbox(label="Cosine Distance 2")
                    image3_output = gr.Image(label="Image 3")
                    text3_output = gr.Textbox(label="Cosine Distance 3")
        
        with gr.Tab("Search Video with Video ID"):
            with gr.Row():
                with gr.Column():
                    video_id = gr.Textbox(
                        label="Enter the video ID",
                        max_lines=1,
                        placeholder="Enter the video ID",
                        container=False,
                    )
                    with gr.Row():
                        search_query_with_id = gr.Textbox(
                            label="Enter your prompt",
                            max_lines=1,
                            placeholder="Enter your prompt",
                            container=False,
                            scale=4
                        )
                        btn_with_id = gr.Button("Search a video", scale=1)

                with gr.Column():
                    image1_output_id = gr.Image(label="Image 1")
                    text1_output_id = gr.Textbox(label="Cosine Distance 1")
                    image2_output_id = gr.Image(label="Image 2")
                    text2_output_id = gr.Textbox(label="Cosine Distance 2")
                    image3_output_id = gr.Image(label="Image 3")
                    text3_output_id = gr.Textbox(label="Cosine Distance 3")

        # search video when button is clicked
        btn.click(
            video_search, 
            inputs=[search_query], 
            outputs=[image1_output, image2_output, image3_output, text1_output, text2_output, text3_output]
        )
        btn_with_id.click(
            video_search_with_id, 
            inputs=[video_id, search_query_with_id], 
            outputs=[image1_output_id, image2_output_id, image3_output_id, text1_output_id, text2_output_id, text3_output_id]
        )

    return app
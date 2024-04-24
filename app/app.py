import gradio as gr
import base64
from PIL import Image
from io import BytesIO
from core import RetrievalPipeline

# global state
moment_start_time_list = []
youtube_video_id = None

def get_moment_buttons(selected_id, num_of_moment=3, visible=True):
    variant="secondary"
    return tuple(   
        gr.Button(
            f"moment {idx+1}", scale=1, visible=visible, 
            variant="primary" if idx == selected_id else "secondary"
        )
        for idx in range(num_of_moment)
    )

def video_search_with_id(video_id, search_query_with_id, *args):
    
    # TODO: add some logic to get vid and moment's start time
    pipeline = RetrievalPipeline()
    moments = pipeline.retrieve_moments(search_query_with_id, 3, video_id)

    global moment_start_time_list
    global youtube_video_id
    youtube_video_id = video_id

    for moment in moments:
        video_name = moment[1]
        youtube_start_time = float(video_name.split("_")[1])
        timestamp = moment[2]
        start_time = timestamp[0] + youtube_start_time
        moment_start_time_list.append(start_time)

    
    # do not allow autoplay. Otherwise it will remember where you are watching.
    return (
        f'<iframe width="560" height="315"  src="https://www.youtube.com/embed/{video_id}?start=10" title="YouTube video player" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>',
        *get_moment_buttons(selected_id=-1, num_of_moment=3)
    )
    
def change_moment(idx, video_id):

    start_time = int(moment_start_time_list[idx]) 
    embed_html = f'<iframe width="560" height="315"  src="https://www.youtube.com/embed/{video_id}?start={start_time}" title="YouTube video player" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'

    updated_output = gr.HTML(embed_html)
    return updated_output, *get_moment_buttons(selected_id=idx, num_of_moment=3)


def gradio_app():
    with gr.Blocks() as app:
        gr.Markdown("## Moment Finder")
        
        with gr.Tab("Search Video with Video ID"):
            with gr.Column():
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
                    out = gr.HTML(scale=3)  # (rerender each time)
                    # buttons to control which moment
                    with gr.Row() as row:
                        change_video_button1 = gr.Button("moment 1", scale=1, visible=False)
                        change_video_button2 = gr.Button("moment 2", scale=1, visible=False)
                        change_video_button3 = gr.Button("moment 3", scale=1, visible=False)
                    # output2 =  video_component()


        # search video when button is clicked
        btn_with_id.click(
            video_search_with_id, 
            inputs=[video_id, search_query_with_id], 
            outputs=[out, change_video_button1, change_video_button2, change_video_button3]
        )
        
        # change which moment to display (rerender each time)
        change_video_button1.click(lambda: change_moment(0, youtube_video_id), outputs=[out, change_video_button1, change_video_button2, change_video_button3])
        change_video_button2.click(lambda: change_moment(1, youtube_video_id), outputs=[out, change_video_button1, change_video_button2, change_video_button3])
        change_video_button3.click(lambda: change_moment(2, youtube_video_id), outputs=[out, change_video_button1, change_video_button2, change_video_button3])

    return app
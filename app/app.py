import gradio as gr
from core import RetrievalPipeline

# def greet(name, intensity):
#     return "Hello, " + name + "!" * int(intensity)

# demo = gr.Interface(
#     fn=greet,
#     inputs=["text", "slider"],
#     outputs=["text"],
# )

# demo.launch()

def video_search(search_query, k=1): 
    print(f"Search Query: {search_query}")

    pipeline = RetrievalPipeline()
    moments = pipeline.retrieve_moments(search_query, k)
    return moments

def gradio_app():
    with gr.Blocks() as app:
        with gr.Column(variant="panel"):
            with gr.Row():
                search_query = gr.Textbox(
                    label="Enter your prompt",
                    max_lines=1,
                    placeholder="Enter your prompt",
                    container=False, 
                    scale=4
                )
                btn = gr.Button("Search a video", scale=1)
            
            gallery = gr.Video(format="mp4", autoplay=True)

        # search video when button is clicked
        btn.click(video_search, inputs=[search_query], outputs=[gallery])

    
    
    return app

import gradio as gr

from src.api import simple_video_search

def gradio_app(vec_databases):
    """ Modified from https://www.gradio.app/docs/gallery"""
    
    database_options = vec_databases.keys()

    def search_fn(db_name, search_query):
        # choocie the right vector db
        vec_db = vec_databases.get(db_name)
        
        if vec_db is not None:

            return simple_video_search(vec_db, search_query)
        
        return None 
    
    with gr.Blocks() as app:
        with gr.Column(variant="panel"):
            tgt_db = gr.Dropdown(database_options, label="Database")
            with gr.Row():
                search_query = gr.Textbox(
                    label="Enter your prompt",
                    max_lines=1,
                    placeholder="Enter your prompt",
                    container=False, 
                    scale=4
                )
                btn = gr.Button("Search a video", scale=1)

            # gallery = gr.Gallery(
            #     label="Generated images", show_label=False, elem_id="gallery"
            # , columns=[2], rows=[2], object_fit="contain", height="auto")
            
            gallery = gr.Video(format="mp4", autoplay=True)   
            # text = gr.gradio.Textbox()
            
            # with gr.Column():
            #     gallery = [
            #         gr.Video(format="mp4", autoplay=True) for _ in range(3)
            #     ]
                
        btn.click(search_fn,
            inputs=[tgt_db, search_query], outputs=gallery)      # position matters
        
    return app

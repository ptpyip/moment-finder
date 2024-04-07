from app.app import gradio_app

def main():
    # get pgvectorDB
    # vec_db = PgvectorDB()
    app = gradio_app()
    app.launch(server_name="0.0.0.0", server_port=8081, share=True)

if __name__ == "__main__":
    main()


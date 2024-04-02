from app.app import gradio_app
# from core.vec_db import PgvectorDB

def main():
    # get pgvectorDB
    # vec_db = PgvectorDB()
    app = gradio_app()
    app.launch(server_name="0.0.0.0", server_port=8081)

if __name__ == "__main__":
    main()


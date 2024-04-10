import os
import uvicorn

from fastapi import FastAPI, Request, Header
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from typing import Optional

from core import RetrievalPipeline

app = FastAPI()
dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = "/data/api/videos"
print(dir_path)

rp = RetrievalPipeline()

CONTENT_CHUNK_SIZE=100*1024
@app.get("/stream/{name}")
async def stream(name:str,range: Optional[str] = Header(None)):
    def get_file(name:str):
        filename = os.path.join(dir_path,"streamFiles", name)
        f = open(filename,'rb')
        return f, os.path.getsize(filename)
    
    def chunk_generator_from_stream(stream, chunk_size, start, size):
        bytes_read = 0
        stream.seek(start)
        while bytes_read < size:
            bytes_to_read = min(chunk_size,size - bytes_read)
            yield stream.read(bytes_to_read)
            bytes_read = bytes_read + bytes_to_read
        stream.close()

    asked = range or "bytes=0-"
    print(asked)
    stream,total_size=get_file(name)
    start_byte = int(asked.split("=")[-1].split('-')[0])

    return StreamingResponse(
        chunk_generator_from_stream(
            stream,
            start=start_byte,
            chunk_size=CONTENT_CHUNK_SIZE,
            size=total_size
        )
        ,headers={
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {start_byte}-{start_byte+CONTENT_CHUNK_SIZE}/{total_size}",
            "Content-Type": "video/mp4"
        },
        status_code=206)

@app.get("/moments")
async def retreive_moments(query: str, k=5):
    retrieval_result = rp.retrieve_moments(query, k)
    
    results = []
    for moment_id, video_name, timestamp, cos_dist in retrieval_result:
        vid = rp.get_video_id(video_name)
        
        results.append({
            "query": query,
            "vid":  vid,      
            "timestamp": timestamp,
            "sim_score": 1 - cos_dist 
        }) 
        
    return JSONResponse({
        "results": results
    })


@app.get("/moments/{video_name}")
async def retreive_moments_with_name(video_name: str, query: str, k=5):
    ## TODO: add video validate logic
    retrieval_result = rp.retrieve_moments(query, k, video_name)
    
    results = []
    for moment_id, video_name, timestamp, cos_dist in retrieval_result:
        vid = rp.get_video_id(video_name)
        
        results.append({
            "query": query,
            "vid":  vid,      
            "timestamp": timestamp,
            "sim_score": 1 - cos_dist 
        }) 
        
    return JSONResponse({
        "results": results
    })

# @app.get("/frames/")
# async def retreive_moments(query: str, k=5):
#     retrieval_result = rp.retrieve_moments(query, k)
    
#     results = []
#     for moment_id, video_name, timestamp, cos_dist in retrieval_result:
#         vid = rp.get_video_id(video_name)
        
#         results.append({
#             "query": query,
#             "vid":  vid,      
#             "timestamp": timestamp,
#             "sim_score": 1 - cos_dist 
#         }) 
        
#     return JSONResponse({
#         "results": results
#     })
            
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
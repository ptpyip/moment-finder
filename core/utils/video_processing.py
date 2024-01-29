import base64
from io import BytesIO
from PIL import Image

def encode_img_to_base64(img: Image) -> str: 
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue())
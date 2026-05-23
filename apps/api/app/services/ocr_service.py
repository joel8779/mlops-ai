from io import BytesIO

import pytesseract
from PIL import Image


class OCRService:
    def extract_text(self, payload: bytes) -> str:
        image = Image.open(BytesIO(payload))
        return pytesseract.image_to_string(image)

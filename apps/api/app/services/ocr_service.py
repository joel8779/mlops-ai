from io import BytesIO

from app.core.config import settings
from app.core.ocr_capabilities import check_binary


class OCRService:
    def extract_text(self, payload: bytes) -> str:
        if not settings.ocr_enabled:
            return ""
        if not check_binary("tesseract").available:
            return ""
        import pytesseract
        from PIL import Image

        image = Image.open(BytesIO(payload))
        return pytesseract.image_to_string(image, timeout=settings.ocr_timeout_seconds)

from fincontract.core.config import settings
from fincontract.core.errors import ToolError


class OCRClient:
    def extract_text(self, file_url: str) -> str:
        provider = settings.ocr_provider.lower()
        raise ToolError(f"OCR provider not configured: {provider}")

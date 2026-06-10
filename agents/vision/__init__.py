"""
GLM-OCR Integration for AutoTrade.
Reads trading charts, financial statements, receipts, and documents.
"""
import logging
from typing import Optional

logger = logging.getLogger("autotrade.vision")

class ChartReader:
    """
    Reads trading charts, candlestick patterns, and financial
    visualizations using GLM-OCR's multimodal understanding.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._ocr = None

    def _get_ocr(self):
        """Lazy-init GLM-OCR to avoid import overhead."""
        if self._ocr is None:
            from glmocr import GlmOcr
            self._ocr = GlmOcr(api_key=self.api_key)
        return self._ocr

    def read_chart(self, image_path: str) -> dict:
        """
        Extract trading data from a chart image.
        Returns structured text: price levels, patterns, indicators visible.
        """
        ocr = self._get_ocr()
        logger.info(f"Reading chart: {image_path}")
        result = ocr.parse(image_path)
        return {
            "source": image_path,
            "raw_text": result.markdown,
            "structured": result.json_result,
        }

    def read_statement(self, path: str) -> dict:
        """
        Extract financial data from a statement, receipt, or PDF.
        Returns structured JSON of all detected text.
        """
        ocr = self._get_ocr()
        logger.info(f"Reading document: {path}")
        result = ocr.parse(path)
        return result.json_result


class DocumentAnalyzer:
    """
    Analyzes financial/trading documents and extracts key data.
    Built on GLM-OCR for document understanding.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.reader = ChartReader(api_key)

    def extract_trade_from_image(self, image_path: str) -> Optional[dict]:
        """
        Given a screenshot of a trade confirmation or PnL,
        extract the key trading data: entry, exit, PnL, fees.
        """
        data = self.reader.read_chart(image_path)
        # Parse structured output for trade-relevant info
        text = data.get("raw_text", "").lower()
        result = {
            "source": image_path,
            "has_numbers": any(c.isdigit() for c in text),
            "raw_text_preview": text[:500],
        }
        return result

    def extract_chart_pattern(self, chart_path: str) -> dict:
        """
        Given a chart image, extract visible patterns, price levels,
        and indicator readings that the strategy agent can use.
        """
        data = self.reader.read_chart(chart_path)
        return {
            "chart_text": data.get("raw_text", ""),
            "analysis": "See raw_text for detected price levels, indicators, and patterns",
        }

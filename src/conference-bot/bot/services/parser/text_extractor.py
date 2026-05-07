import os
import pymupdf
import easyocr
import numpy as np
import logging


class PDFTextExtractor:
  """
    Класс для извлечения текста из PDF.
    Использует обычный текстовый слой и OCR (если PDF — скан).
  """
  _reader = None
  
  def __init__(self):
    if PDFTextExtractor._reader is None:
      logging.info("Инициализация OCR-модели...")
      PDFTextExtractor._reader = easyocr.Reader(['ru', 'en'], gpu=False, verbose=False)
    self.reader = PDFTextExtractor._reader
    
    
  def extract_text_smart(self, pdf_path, max_pages=10):
    """Извлекает текст из PDF. Если текста нет — использует OCR."""
    text = ""
    try:
      doc = pymupdf.open(pdf_path)

      for page_num in range(min(max_pages, doc.page_count)):
        page = doc.load_page(page_num)
        text += page.get_text("text").strip() + "\n"

      if len(text.strip()) < 150:
        logging.error(f"{os.path.basename(pdf_path)} определен как скан. Распознаю текст...")
        text = ""
        for page_num in range(min(max_pages, doc.page_count)):
          page = doc.load_page(page_num)
          pix = page.get_pixmap(dpi=150, alpha=False)
          img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
          result = self.reader.readtext(img_array, detail=0)
          text += " ".join(result) + "\n"

      doc.close()
    except Exception as e:
      logging.exception("Ошибка PDF")

    return text.encode("utf-8", "ignore").decode("utf-8")[:18000]

from .text_extractor import PDFTextExtractor
from .llm_service import OpenRouterProvider, GroqProvider, FallbackLLMParser
from bot.config import OPENROUTER_API_KEY, OPENROUTER_MODEL, GROQ_API_KEY, GROQ_MODEL


class ParserService:
  def __init__(self):
    self.extractor = PDFTextExtractor()

    providers = [
      OpenRouterProvider(OPENROUTER_API_KEY, OPENROUTER_MODEL),
      GroqProvider(GROQ_API_KEY, GROQ_MODEL),
    ]

    self.parser = FallbackLLMParser(providers)

  async def parse_pdf(self, file_path: str) -> dict | None:
    text = self.extractor.extract_text_smart(file_path)
    return await self.parser.parse(text)
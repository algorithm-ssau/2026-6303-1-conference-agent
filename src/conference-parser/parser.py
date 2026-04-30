import os
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, GROQ_API_KEY, GROQ_MODEL
from text_extractor import PDFTextExtractor
from llm_service import OpenRouterProvider, GroqProvider, FallbackLLMParser
from exporter import ExcelExporter
from tagger import assign_hashtags


class EventExtractionApp:
    def __init__(self, folder_path=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        if folder_path is None:
            folder_path = os.path.join(base_dir, "../pdfs")

        self.folder_path = os.path.abspath(folder_path)
        self.folder_path = folder_path
        self.extractor = PDFTextExtractor()

        providers = [
            OpenRouterProvider(OPENROUTER_API_KEY, OPENROUTER_MODEL),
            GroqProvider(GROQ_API_KEY, GROQ_MODEL),
        ]
        self.parser = FallbackLLMParser(providers)
        self.exporter = ExcelExporter()

    def run(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
            print(f"Создана папка '{self.folder_path}'. Положите туда файлы.")
            return

        pdf_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(".pdf")]
        all_results = []

        for filename in pdf_files:
            print(f"\nОбработка: {filename}...")
            pdf_path = os.path.join(self.folder_path, filename)

            raw_text = self.extractor.extract_text_smart(pdf_path)
            data = self.parser.parse(raw_text)

            if data:
                data = self.exporter.postprocess_for_excel(data)
                data["hashtags"] = assign_hashtags(
                    event_name=data.get("event_name", ""),
                    topics=data.get("topics", []),
                    raw_text=raw_text
                )
                data["source_file"] = filename
                all_results.append(data)
                print(f"Готово: {data.get('event_name', 'Без названия')}")

        if all_results:
            output_name = self.exporter.save(all_results)
            print(f"\nРезультаты в файле: {output_name}")
        else:
            print("\nНе удалось извлечь данные ни из одного файла.")


# if __name__ == "__main__":
#     app = EventExtractionApp()
#     app.run()

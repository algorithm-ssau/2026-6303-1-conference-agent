import pandas as pd
import os


class ExcelExporter:
    @staticmethod
    def postprocess_for_excel(data: dict) -> dict:
        """Постобработка данных перед записью в Excel."""
        if data.get('deadlines'):
            data['deadlines'] = "; ".join([f"{d['date']} ({d['description']})" for d in data['deadlines']])

        if data.get('links'):
            data['links'] = "; ".join([f"{l['url']} — {l['description']}" for l in data['links']])

        if isinstance(data.get('topics'), list):
            data['topics'] = ", ".join(data['topics'])

        return data

    @staticmethod
    def save(results, output_name="structured_events.xlsx"):

        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, "../files_parsed")

        os.makedirs(output_dir, exist_ok=True)  # на случай если папки нет

        full_path = os.path.join(output_dir, output_name)

        df = pd.DataFrame(results)
        df.insert(0, '№', range(1, len(df) + 1))
        df.to_excel(full_path, index=False)

        return full_path

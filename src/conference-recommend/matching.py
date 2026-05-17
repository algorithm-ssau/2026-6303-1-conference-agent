from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from config import MODEL_NAME, SIMILARITY_THRESHOLD, CONFERENCES, USER_INPUT


# Функция инициализации: загружает модель и создаёт индекс эмбеддингов
def initialize_model_and_index(conferences, model_name):

    model = SentenceTransformer(model_name)
    
    conference_index = {}
    for conf in conferences:
        embeddings = model.encode(conf["topics"])
        conference_index[conf["event_name"]] = {
            "topics": conf["topics"],
            "embeddings": embeddings
        }
    return model, conference_index


# Функция поиска совпадений: принимает строку, модель и индекс
def match_conferences(user_input_str, conference_index, model, threshold):

    user_topics = [topic.strip() for topic in user_input_str.split(",") if topic.strip()]
    if not user_topics:
        return []

    user_embeddings = model.encode(user_topics)
    results_with_scores = []

    # Сравнение с каждой конференцией
    for conf_name, conf_data in conference_index.items():
        similarity_scores = []
        for user_emb in user_embeddings:
            scores = cosine_similarity([user_emb], conf_data["embeddings"])[0]
            best_score = float(np.max(scores))
            if best_score >= threshold:
                similarity_scores.append(best_score)

        if similarity_scores:
            final_score = float(np.mean(similarity_scores))
            results_with_scores.append((conf_name, final_score))

    # Сортировка по релевантности и возврат только названий
    results_with_scores.sort(key=lambda x: x[1], reverse=True)
    return [name for name, _ in results_with_scores]


def result():
    model, conference_index = initialize_model_and_index(CONFERENCES, MODEL_NAME)
    matches = match_conferences(USER_INPUT, conference_index, model, SIMILARITY_THRESHOLD)

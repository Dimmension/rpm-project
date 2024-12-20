from sentence_transformers import SentenceTransformer
from config.settings import settings

model = SentenceTransformer(
    model_name_or_path=settings.EMBEDDER_MODEL,
)


def get_embeddings(sentence: str | None) -> list[float] | None:
    if sentence:
        return model.encode(sentence, normalize_embeddings=True)
    return None

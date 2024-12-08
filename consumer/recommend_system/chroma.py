import logging
import asyncio
import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from chromadb.config import Settings
from config.settings import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ChromaDBManager:
    def __init__(self, host: str, port: int, embedding_model: str):
        self.host = host
        self.port = port
        self.embedding_model = embedding_model
        self.client = None
        self.embedding_function = None
        self.collection = None
        self.initialize_embedding_function()

    def initialize_client(self):
        """Инициализация клиента ChromaDB."""
        try:
            self.client = chromadb.HttpClient(
                host=self.host,
                port=self.port,
                ssl=False,
                settings=Settings(
                    allow_reset=True,
                    anonymized_telemetry=False
                )
            )
            logging.info(f"ChromaDB client initialized on {self.host}:{self.port}.")
        except Exception as error:
            logging.error(f"Failed to initialize ChromaDB client: {error}")
            raise error

    def initialize_embedding_function(self) -> None:
        """Создание функции эмбеддингов."""
        try:
            self.embedding_function = SentenceTransformerEmbeddingFunction(model_name=self.embedding_model)
            logging.info(f"Embedding function created for model {self.embedding_model}.")
        except Exception as error:
            logging.error(f"Failed to create embedding function: {error}")
            raise error

    def create_or_get_collection(self, collection_name: str) -> None:
        """Создание или получение коллекции ChromaDB."""
        if not self.client:
            raise RuntimeError("ChromaDB client is not initialized. Call `initialize_client` first.")

        if not self.embedding_function:
            raise RuntimeError("Embedding function is not initialized. Call `initialize_embedding_function` first.")

        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logging.info(f'ChromaDB collection "{collection_name}" initialized.')
        except Exception as error:
            logging.error(f"Failed to create or get collection {collection_name}: {error}")
            raise error

    def add_to_collection(self, user_data: dict):
        """Добавление данных в коллекцию."""
        # {
        #  'event': 'user_form', 
        #  'action': 'send_form',
        #  'user_id': 970369969,
        #  'name': 'Vadim',
        #  'age': 19,
        #  'gender': 'Выберите ваш пол',
        #  'description': 'Ничего', 
        #  'filter_by_age': '19', 
        #  'filter_by_gender': 'Выберите пол того, кого вы ищете', 
        #  'filter_by_description': 'Ничего'
        # }
        metadata = {
            'name': user_data['name'],
            'age': user_data['age'],
            'gender': user_data['gender'],
            'description': user_data['description'],
            'filter_by_age': user_data['filter_by_age'],
            'filter_by_gender': user_data['filter_by_gender'],
            'filter_by_description': user_data['filter_by_description'],
        }

        if not self.collection:
            raise RuntimeError("ChromaDB collection is not initialized. Call `create_or_get_collection` first.")

        try:
            self.collection.add(
                documents=[user_data["description"]],
                metadatas=[metadata],
                ids=[str(user_data["user_id"])]
            )
            logging.info(f"Data for user {user_data['user_id']} added to collection.")
        except Exception as error:
            logging.error(f"Failed to add data to collection: {error}")
            raise error

    def get_recommends_by_id(self, user_data: dict):
        """
        Get embedding of user description and find similar descriptions.

        Args:
            user_data (dict): Contains user data including 'user_id'.

        Returns:    
            list[int]: List of recommended user IDs based on similarity.
        """
        try:
            print(f'ID: {str(user_data["user_id"])}')
            doc = self.collection.get(ids=[str(user_data["user_id"])], include=['embeddings'])
            logging.info(f"Fetched document: {doc}")

            if not doc or 'embeddings' not in doc or not doc['embeddings']:
                logging.warning("No embeddings found for the user.")
                return []

            embedding = doc['embeddings'][0]

            results = self.collection.query(
                query_embeddings=[embedding],
                include=['metadatas'],
                n_results=20
            )
            recommended_ids = [result for result in results['metadatas']]
            print(recommended_ids)
            return recommended_ids[0]

        except Exception as e:
            logging.error(f"Error in get_recommends_by_id: {e}")
            return []

    def close_client(self):
        """Закрытие соединения с клиентом."""
        if self.client:
            self.client.close()
            logging.info("ChromaDB client connection closed.")


chroma_manager = ChromaDBManager(
    **settings.CHROMA_SETTINGS
)
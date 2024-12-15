
import random
from faker import Faker
from recommend_system.chroma import chroma_manager
from consumer.schema.form import FormMessage

faker = Faker()

def handle_event_form(message: FormMessage):
    if message['action'] == 'send_form':
        for i in range(10):
            fake = {
                'event': 'user_form', 
                'action': 'send_form',
                'user_id': i,
                'name': faker.name(),
                'age': random.randint(18, 80),
                'gender': random.choice(['мужчина', 'женщина']),
                'description': faker.text(max_nb_chars=200),
                'filter_by_age': random.randint(18, 80),
                'filter_by_gender': faker.text(max_nb_chars=200),
                'filter_by_description': faker.text(max_nb_chars=200),
            }
            chroma_manager.add_to_collection(fake)
        chroma_manager.add_to_collection(message)


from prometheus_client import Counter

TOTAL_RECEIVED_MESSAGES = Counter(
    'received_messages',
    'Считает полученные сообщения',
)
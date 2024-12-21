from prometheus_client import Counter, Histogram

TOTAL_RECEIVED_MESSAGES = Counter(
    'received_messages',
    'Считает полученные сообщения',
)
from prometheus_client import Counter, Histogram
# sum(increase(counter_handler_total{handler="method_funcio..."}[1m]))
TOTAL_RECEIVED_MESSAGES = Counter(
    'received_messages',
    'Считает полученные сообщения',
)
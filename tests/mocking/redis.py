class MockRedis:
    def __init__(self) -> None:
        self.data = {}

    def set(self, key, value, ex: float | None = None) -> None:
        self.data[key] = value

    def get(self, key):
        return self.data[key]

from eventsourcing.encryption import ICryptoStore


class InMemCryptoStore(ICryptoStore):
    def __init__(self) -> None:
        self.store : dict[str, bytes] = {}

    def get_encryption_key(self, id: str) -> bytes | None:
        return self.store.get(id)

    def add(self, id: str, new_encryption_key: bytes) -> None:
        self.store[id] = new_encryption_key

    def remove(self, id: str) -> None:
        self.store[id] = None
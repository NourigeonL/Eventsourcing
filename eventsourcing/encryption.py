from functools import wraps
from cryptography.fernet import Fernet
import abc
from copy import deepcopy
from typing import Optional, List, Type, Callable
from eventsourcing.data import Data

class ICryptoStore(abc.ABC):
    """Abstract base class for crypto storage operations."""

    @abc.abstractmethod
    def get_encryption_key(self, id: str) -> Optional[bytes]:
        """Retrieve an encryption key by ID."""

    @abc.abstractmethod
    def add(self, id: str, new_encryption_key: bytes) -> None:
        """Add a new encryption key."""

    @abc.abstractmethod
    def remove(self, id: str) -> None:
        """Remove an encryption key by ID."""

class CryptoRepository:
    """Repository for managing encryption keys."""

    crypto_store: ICryptoStore

    @staticmethod
    def get_existing_or_new(id: str) -> bytes:
        """Get an existing key or generate a new one if not found."""
        key_stored = CryptoRepository.crypto_store.get_encryption_key(id=id)

        if key_stored is not None:
            return key_stored

        new_encryption_key = Fernet.generate_key()
        CryptoRepository.crypto_store.add(id=id, new_encryption_key=new_encryption_key)
        return new_encryption_key

    @staticmethod
    def get_existing_or_none(id: str) -> Optional[bytes]:
        """Get an existing key or return None if not found."""
        return CryptoRepository.crypto_store.get_encryption_key(id=id)

    @staticmethod
    def delete_encryption_key(id: str) -> None:
        """Delete an encryption key by ID."""
        CryptoRepository.crypto_store.remove(id=id)

def encrypted(subject_id: str, encrypted_members: List[str]) -> Callable:
    """
    Decorator for encrypting specified members of a Data class.
    
    Args:
        subject_id (str): The ID field used for encryption key lookup.
        encrypted_members (List[str]): List of member names to be encrypted.
    
    Returns:
        Callable: A decorator function.
    """
    def encrypt(cls: Type[Data]) -> Type[Data]:
        if not issubclass(cls, Data):
            raise TypeError("Class must inherit from Data")
        
        if subject_id not in cls.__dict__["__dataclass_fields__"]:
            raise AttributeError(f"{cls} does not have {subject_id} member")
        
        not_exist = [val for val in encrypted_members if val not in cls.__dict__["__dataclass_fields__"]]
        if not_exist:
            raise AttributeError(f"{cls} does not have {', '.join(not_exist)} member(s)")

        old_to_dict = cls.to_dict

        @wraps(old_to_dict)
        def new_to_dict(self: Data) -> dict:
            """Overridden to_dict method to encrypt specified members."""
            res = old_to_dict(self)
            encryption_key = CryptoRepository.get_existing_or_new(res[subject_id])
            fernet = Fernet(encryption_key)

            for member_name in encrypted_members:
                res[member_name] = "encrypted_" + fernet.encrypt(str(res[member_name]).encode('utf-8')).decode()
            return res

        cls.to_dict = new_to_dict

        old_from_dict = cls.from_dict

        @wraps(old_from_dict)
        def new_from_dict(dict_values: dict) -> Data:
            """Overridden from_dict method to decrypt specified members."""
            encryption_key = CryptoRepository.get_existing_or_none(dict_values[subject_id])

            if encryption_key is None:
                return old_from_dict(dict_values)

            fernet = Fernet(encryption_key)
            new_dict = deepcopy(dict_values)
            for member in encrypted_members:
                field_type = cls.__dict__["__dataclass_fields__"][member].type
                decrypted_value = fernet.decrypt(str(dict_values[member]).removeprefix("encrypted_")).decode('utf-8')
                new_dict[member] = field_type(decrypted_value)

            return old_from_dict(new_dict)

        cls.from_dict = new_from_dict

        return cls

    return encrypt

class InMemCryptoStore(ICryptoStore):
    def __init__(self) -> None:
        self.store : dict[str, bytes] = {}

    def get_encryption_key(self, id: str) -> bytes | None:
        return self.store.get(id)

    def add(self, id: str, new_encryption_key: bytes) -> None:
        self.store[id] = new_encryption_key

    def remove(self, id: str) -> None:
        self.store[id] = None
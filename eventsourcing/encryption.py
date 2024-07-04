from functools import wraps
from cryptography.fernet import Fernet
import abc
from copy import deepcopy
from eventsourcing.data import Data

class ICryptoStore(abc.ABC):

    @abc.abstractmethod
    def get_encryption_key(self, id :str) -> bytes | None: ...

    @abc.abstractmethod
    def add(self, id: str, new_encryption_key : bytes) -> None: ...

    @abc.abstractmethod
    def remove(self, id : str) -> None: ...

class CryptoRepository:
    crypto_store : ICryptoStore

    @staticmethod
    def get_existing_or_new(id : str) -> bytes:
        key_stored = CryptoRepository.crypto_store.get_encryption_key(id=id)

        if key_stored is not None:
            return key_stored

        new_encryption_key = Fernet.generate_key()
        CryptoRepository.crypto_store.add(id=id, new_encryption_key=new_encryption_key)
        return new_encryption_key

    @staticmethod
    def get_existing_or_none(id : str) -> bytes | None:
        return CryptoRepository.crypto_store.get_encryption_key(id=id)
    @staticmethod
    def delete_encryption_key(id: str) -> None:
        CryptoRepository.crypto_store.remove(id=id)

def encrypted(subject_id : str, encrypted_members : list[str]) -> callable:

    def encrypt(cls : type["Data"]) -> type["Data"]:
        if not issubclass(cls, Data):
            raise TypeError("class is not inherited from Data")
        if subject_id not in cls.__dict__["__dataclass_fields__"]:
            raise AttributeError(f"{cls} does not have {subject_id} member")
        not_exist = []
        for val in encrypted_members:
            if val not in cls.__dict__["__dataclass_fields__"]:
                not_exist.append(val)
        if len(not_exist) > 0:
            raise AttributeError(f"{cls} does not have {', '.join(not_exist)} member(s)")

        old_to_dict = cls.to_dict

        @wraps(old_to_dict)
        def new_to_dict(self : "Data") -> dict:
            res = old_to_dict(self)
            encryption_key = CryptoRepository.get_existing_or_new(res[subject_id])

            for member_name in encrypted_members:
                res[member_name] = Fernet(encryption_key).encrypt(bytes(str(res[member_name]), encoding='utf8'))
            return res
        cls.to_dict = new_to_dict

        old_from_dict = cls.from_dict

        @wraps(old_from_dict)
        def new_from_dict(dict_values : dict) -> dict:
            encryption_key = CryptoRepository.get_existing_or_none(dict_values[subject_id])

            if encryption_key is None:
                return old_from_dict(dict_values)

            f = Fernet(encryption_key)
            new_dict = deepcopy(dict_values)
            for member in encrypted_members:
                new_dict[member] = cls.__dict__["__dataclass_fields__"][member].type(str(f.decrypt(dict_values[member]), encoding='utf-8'))

            return old_from_dict(new_dict)

        cls.from_dict = new_from_dict

        return cls

    return encrypt
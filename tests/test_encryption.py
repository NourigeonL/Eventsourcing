import pytest
import unittest
from eventsourcing.encryption import encrypted, ICryptoStore, CryptoRepository
from dataclasses import dataclass
from eventsourcing.data import Data, to_dict
from cryptography.fernet import Fernet
from uuid import uuid4

class FakeCryptoStore(ICryptoStore):
    """
    A mock implementation of ICryptoStore for testing purposes.
    """
    def __init__(self):
        self.store : dict[str, bytes] = {}

    def get_encryption_key(self, id: str) -> bytes | None:
        return self.store.get(id)

    def add(self, id: str, new_encryption_key: bytes):
        self.store[id] = new_encryption_key

    def remove(self, id: str):
        self.store[id] = None

class CryptoRepositoryTest(unittest.TestCase):
    """
    Test suite for the CryptoRepository class.
    """
    def setUp(self):
        """
        Set up a FakeCryptoStore for each test.
        """
        self.key_store = FakeCryptoStore()
        CryptoRepository.crypto_store = self.key_store

    def test_get_existing_or_default(self):
        """
        Test retrieving a non-existent key returns None.
        """
        key = CryptoRepository.get_existing_or_none("123")
        assert key is None

    def test_get_existing_new_generate_new(self):
        """
        Test generating a new key when one doesn't exist.
        """
        key = CryptoRepository.get_existing_or_new("123")
        assert key is not None
        assert isinstance(key, bytes)
        assert self.key_store.store.get("123") is not None

    def test_get_existing_new_return_stored(self):
        """
        Test retrieving an existing key.
        """
        self.key_store.store["123"] = Fernet.generate_key()
        key = CryptoRepository.get_existing_or_new("123")
        assert key is not None
        assert key == self.key_store.store["123"]

    def test_delete_encryption_key(self):
        """
        Test deleting an encryption key.
        """
        self.key_store.store["321"] = Fernet.generate_key()
        assert self.key_store.store["321"] is not None
        CryptoRepository.delete_encryption_key("321")
        assert self.key_store.store["321"] is None

class EncryptionInitModelTest(unittest.TestCase):
    """
    Test suite for the encrypted decorator and its error handling.
    """
    def setUp(self):
        self.key_store = FakeCryptoStore()
        CryptoRepository.crypto_store = self.key_store

    def test_object_is_not_a_data(self):
        """
        Test that the decorator raises an error when applied to a non-Data class.
        """
        with pytest.raises(TypeError):
            @encrypted(subject_id="oh", encrypted_members=[])
            @dataclass
            class NotData:
                val : int


    def test_object_is_not_a_dataclass(self):
        """
        Test that the decorator raises an error when applied to a non-dataclass.
        """
        with pytest.raises(TypeError):
            @encrypted(subject_id="oh", encrypted_members=[])
            class NotData:
                val : int

    def test_argument_missing(self):
        """
        Test that the decorator raises an error when required arguments are missing.
        """
        with pytest.raises(TypeError):
            @encrypted(encrypted_members=[])
            @dataclass
            class NoSubject(Data):
                val : int

        with pytest.raises(TypeError):
            @encrypted(subject_id='fdf')
            @dataclass
            class NoSubject(Data):
                val : int

    def test_subject_id_does_not_exist(self):
        """
        Test that the decorator raises an error when the subject_id field doesn't exist.
        """
        with pytest.raises(AttributeError):
            @encrypted(subject_id="id", encrypted_members=[])
            @dataclass
            class NoSubject(Data):
                val : int

    def test_encrypted_members_do_not_exist(self):
        """
        Test that the decorator raises an error when specified encrypted members don't exist.
        """
        with pytest.raises(AttributeError):
            @encrypted(subject_id="id", encrypted_members=["val_one", "val_two"])
            @dataclass
            class NoMembers(Data):
                id : int

    def test_can_instanciate_class(self):
        """
        Test that a correctly decorated class can be instantiated.
        """
        @encrypted(subject_id="id", encrypted_members=["val_one", "val_two"])
        @dataclass
        class CorrectClass(Data):
            id : int
            val_one : str
            val_two : int
            val_three : float
        
        # Note: This test doesn't actually assert anything.
        # It implicitly checks that the class can be defined without raising an exception.

class EncryptionToDictTest(unittest.TestCase):
    """
    Test suite for testing the encryption and dictionary conversion functionalities.
    """
    def setUp(self):
        """
        Set up a FakeCryptoStore for each test.
        """
        self.key_store = FakeCryptoStore()
        CryptoRepository.crypto_store = self.key_store

    def test_dataclass_inside_dict_is_changed_to_dict(self):
        """
        Test that a dataclass inside a dictionary is converted to a dictionary.
        """
        @dataclass
        class NestedClass:
            id : int
            val_str : str
            val_int : int
            val_float : float

        my_dict : dict[str, NestedClass]= {"one" : NestedClass(id=1, val_str="two", val_int=3, val_float=4.4)}
        new_dict = to_dict(my_dict)

        # Check if the NestedClass instance is converted to a dictionary
        assert isinstance(new_dict["one"], dict)

    def test_class_changed_to_dict(self):
        """
        Test that a class with nested dataclass is correctly converted to a dictionary.
        """
        @dataclass
        class NestedClass:
            id : int
            val_str : str
            val_int : int
            val_float : float

        @dataclass
        class NesterClass(Data):
            id : int
            val_str : str
            val_int : int
            val_dataclass : NestedClass

        nester_id = str(uuid4())
        nested_id = str(uuid4())
        my_obj = NesterClass(id=nester_id, val_str="one", val_int=2, val_dataclass=NestedClass(id=nested_id, val_str="one one", val_int=22, val_float=3.3))
        my_dict = my_obj.to_dict()

        # Verify the structure and values of the resulting dictionary
        assert my_dict["id"] == nester_id
        assert my_dict["val_str"] == my_obj.val_str
        assert my_dict["val_int"] == my_obj.val_int
        assert isinstance(my_dict["val_dataclass"], dict)
        nested_dict = my_dict["val_dataclass"]
        assert nested_dict["id"] == nested_id
        assert nested_dict["val_str"] == my_obj.val_dataclass.val_str
        assert nested_dict["val_int"] == my_obj.val_dataclass.val_int
        assert nested_dict["val_float"] == my_obj.val_dataclass.val_float

    def test_new_key_is_generated(self):
        """
        Test that a new encryption key is generated when calling to_dict on a decorated class.
        """
        @encrypted(subject_id="id", encrypted_members=[])
        @dataclass
        class CorrectClass(Data):
            id : int
            val_one : str
            val_two : int
            val_three : float

        my_obj = CorrectClass(id="321456", val_one="one", val_two=2, val_three=3.3)
        my_obj.to_dict()

        # Check that a new encryption key is generated and stored
        assert self.key_store.store.get("321456") is not None

    def test_no_new_key_are_generated(self):
        """
        Test that no new encryption key is generated if one already exists.
        """
        @encrypted(subject_id="id", encrypted_members=[])
        @dataclass
        class CorrectClass(Data):
            id : int
            val_one : str
            val_two : int
            val_three : float

        key = Fernet.generate_key()
        self.key_store.store["321456"] = key
        my_obj = CorrectClass(id="321456", val_one="one", val_two=2, val_three=3.3)
        my_obj.to_dict()

        # Verify that the existing key is not changed
        assert self.key_store.store.get("321456") == key

    def test_one_member_is_encrypted(self):
        """
        Test that one specified member is encrypted when calling to_dict.
        """
        @encrypted(subject_id="id", encrypted_members=["val_one"])
        @dataclass
        class CorrectClass(Data):
            id : int
            val_one : str
            val_two : int
            val_three : float

        my_obj = CorrectClass(id="dfs456sdf", val_one="one", val_two=2, val_three=3.3)
        my_dict = my_obj.to_dict()

        key = self.key_store.store.get("dfs456sdf")
        f = Fernet(key)

        # Verify that the specified member is encrypted
        assert my_dict["id"] == "dfs456sdf"
        assert isinstance(my_dict["val_one"], bytes)
        assert str(f.decrypt(my_dict["val_one"]), encoding='utf-8') == "one"
        assert my_dict["val_two"] == 2
        assert my_dict["val_three"] == 3.3

    def test_all_member_are_encrypted(self):
        """
        Test that all specified members are encrypted when calling to_dict.
        """
        @encrypted(subject_id="id", encrypted_members=["val_one", "val_two", "val_three"])
        @dataclass
        class CorrectClass(Data):
            id : int
            val_one : str
            val_two : int
            val_three : float

        my_obj = CorrectClass(id="dfs456sdf", val_one="one", val_two=2, val_three=3.3)

        my_dict = my_obj.to_dict()

        key = self.key_store.store.get("dfs456sdf")
        f = Fernet(key)

        # Verify that all specified members are encrypted
        assert my_dict["id"] == "dfs456sdf"
        assert isinstance(my_dict["val_one"], bytes)
        assert str(f.decrypt(my_dict["val_one"]), encoding='utf-8') == "one"
        assert isinstance(my_dict["val_two"], bytes)
        assert int(str(f.decrypt(my_dict["val_two"]), encoding='utf-8')) == 2
        assert isinstance(my_dict["val_three"], bytes)
        assert float(str(f.decrypt(my_dict["val_three"]), encoding='utf-8')) == 3.3

    def test_nested_encrypted_class(self):
        """
        Test that nested encrypted classes are correctly handled when calling to_dict.
        """
        @encrypted(subject_id="id", encrypted_members=["val_one", "val_three"])
        @dataclass
        class NestedClass(Data):
            id : int
            val_one : str
            val_two : int
            val_three : float

        @encrypted(subject_id="id", encrypted_members=["val_two"])
        @dataclass
        class NesterClass(Data):
            id : int
            val_one : str
            val_two : int
            nested : NestedClass

        nester_id = str(uuid4())
        nested_id = str(uuid4())
        my_obj = NesterClass(id=nester_id, val_one="one", val_two=2, nested=NestedClass(id=nested_id, val_one="one one", val_two=22, val_three=3.3))
        my_dict = my_obj.to_dict()
        nester_key = self.key_store.store.get(nester_id)
        nested_key = self.key_store.store.get(nested_id)

        # Verify that the nested encrypted classes are correctly handled
        assert my_dict["id"] == nester_id
        assert my_dict["val_one"] == my_obj.val_one
        assert int(str(Fernet(nester_key).decrypt(my_dict["val_two"]), encoding='utf-8')) == my_obj.val_two
        assert isinstance(my_dict["nested"], dict)
        nested_dict = my_dict["nested"]
        assert nested_dict["id"] == nested_id
        assert str(Fernet(nested_key).decrypt(nested_dict["val_one"]), encoding='utf-8') == my_obj.nested.val_one
        assert nested_dict["val_two"] == my_obj.nested.val_two
        assert float(str(Fernet(nested_key).decrypt(nested_dict["val_three"]), encoding='utf-8')) == my_obj.nested.val_three

class EncryptionFromDictTest(unittest.TestCase):
    """
    Test suite for testing the decryption and object creation from dictionary functionalities.
    """
    def setUp(self):
        """
        Set up a FakeCryptoStore for each test.
        """
        self.key_store = FakeCryptoStore()
        CryptoRepository.crypto_store = self.key_store

    def test_no_key_are_generated(self):
        """
        Test that no encryption keys are generated when calling from_dict on a decorated class
        with an unencrypted dictionary.
        """
        @encrypted(subject_id="id", encrypted_members=[])
        @dataclass
        class CorrectClass(Data):
            id : int
            val_one : str
            val_two : int
            val_three : float

        my_dict = {"id":"321456", "val_one":"one", "val_two":2, "val_three":3.3}
        my_obj = CorrectClass.from_dict(my_dict)

        # Verify that no key is generated and values are correctly set
        assert self.key_store.store.get("321456") is None
        assert my_obj.val_one == "one"
        assert my_obj.val_two == 2
        assert my_obj.val_three == 3.3

    def test_members_are_decrypted(self):
        """
        Test that encrypted members are correctly decrypted when calling from_dict.
        """
        @encrypted(subject_id="id", encrypted_members=["val_one", "val_three"])
        @dataclass
        class CorrectClass(Data):
            id : int
            val_one : str
            val_two : int
            val_three : float

        key = Fernet.generate_key()
        id = "321456"
        self.key_store.store[id] = key

        # Create a dictionary with encrypted values
        my_dict = {
            "id":id, 
            "val_one":Fernet(key).encrypt(bytes(str("one"), encoding='utf-8')), 
            "val_two":2, 
            "val_three":Fernet(key).encrypt(bytes(str(3.3), encoding='utf-8'))
            }

        my_obj = CorrectClass.from_dict(my_dict)

        # Verify that encrypted values are correctly decrypted
        assert my_obj.val_one == "one"
        assert my_obj.val_two == 2
        assert my_obj.val_three == 3.3

    def test_nested_class_decrypted(self):
        """
        Test that nested encrypted classes are correctly decrypted when calling from_dict.
        """
        @encrypted(subject_id="id", encrypted_members=["val_one", "val_three"])
        @dataclass
        class NestedClass(Data):
            id : int
            val_one : str
            val_two : int
            val_three : float

        @encrypted(subject_id="id", encrypted_members=["val_two"])
        @dataclass
        class NesterClass(Data):
            id : int
            val_one : str
            val_two : int
            nested : NestedClass

        nested_key = Fernet.generate_key()
        nester_key = Fernet.generate_key()
        nested_id = str(uuid4())
        nester_id = str(uuid4())

        self.key_store.store[nested_id] = nested_key
        self.key_store.store[nester_id] = nester_key

        # Create a nested dictionary with encrypted values
        my_dict = {
            "id":nester_id, 
            "val_one":"one one", 
            "val_two":Fernet(nester_key).encrypt(bytes(str(22), encoding='utf-8')), 
            "nested":{
                "id":nested_id, 
                "val_one":Fernet(nested_key).encrypt(bytes(str("one"), encoding='utf-8')), 
                "val_two":2, 
                "val_three":Fernet(nested_key).encrypt(bytes(str(3.3), encoding='utf-8'))
                }
            }

        my_obj = NesterClass.from_dict(my_dict)

        # Verify that all values, including nested ones, are correctly decrypted
        assert my_obj.val_one == "one one"
        assert my_obj.val_two == 22
        assert my_obj.nested.val_one == "one"
        assert my_obj.nested.val_two == 2
        assert my_obj.nested.val_three == 3.3
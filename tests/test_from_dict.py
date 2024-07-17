from unittest import mock
from eventsourcing.data import from_dict, Data
from dataclasses import dataclass
import pytest

def test_convert_to_dict():
    """
    Test conversion of a dictionary to a dictionary.
    Ensures that from_dict correctly handles simple dictionary input.
    """
    dict_values = {"first_value" : 1, "second_value" : "two"}
    res = from_dict(dict, dict_values)

    # Check if the result is a dictionary and values are preserved
    assert isinstance(res, dict)
    assert res["first_value"] == 1
    assert res["second_value"] == "two"

def test_convert_to_simple_dataclass():
    """
    Test conversion of a dictionary to a simple dataclass.
    Verifies that from_dict can create a dataclass instance from a dictionary.
    """
    @dataclass
    class SimpleDataclass:
        first_value : int
        second_value : str

    dict_values = {"first_value" : 1, "second_value" : "two"}
    res = from_dict(SimpleDataclass, dict_values)

    # Ensure the result is of the correct type and has the expected values
    assert isinstance(res, SimpleDataclass)
    assert res.first_value == 1
    assert res.second_value == "two"

def test_convert_to_nested_dict():
    """
    Test conversion of a dictionary with nested dictionaries.
    Checks if from_dict correctly handles nested dictionary structures.
    """
    dict_values = {"first_value" : 1, "second_value" : "two", "nested":{"first_value" : 3, "second_value" : "four"}}
    res = from_dict(dict, dict_values)

    # Verify the structure and values of the nested dictionary
    assert isinstance(res, dict)
    assert res["first_value"] == 1
    assert res["second_value"] == "two"
    assert isinstance(res["nested"], dict)
    assert res["nested"]["first_value"] == 3
    assert res["nested"]["second_value"] == "four"

def test_convert_to_nested_dataclass():
    """
    Test conversion of a dictionary to a nested dataclass.
    Ensures that from_dict can handle complex nested dataclass structures.
    """
    @dataclass
    class NestedDataclass:
        first_value : int
        second_value : str

    @dataclass
    class NesterDataclass:
        first_value : int
        second_value : str
        nested : NestedDataclass

    dict_values = {"first_value" : 1, "second_value" : "two", "nested":{"first_value" : 3, "second_value" : "four"}}
    res = from_dict(NesterDataclass, dict_values)

    # Check if the nested structure is correctly created
    assert isinstance(res, NesterDataclass)
    assert res.first_value == 1
    assert res.second_value == "two"
    assert isinstance(res.nested, NestedDataclass)
    assert res.nested.first_value == 3
    assert res.nested.second_value == "four"

def test_convert_to_nested_dataclass_in_dict():
    """
    Test conversion of a dictionary with nested dataclasses.
    Verifies that from_dict can create a dictionary of dataclass instances.
    """
    @dataclass
    class SimpleDataclass:
        first_value : int
        second_value : str

    dict_values = {"uno" : {"first_value" : 1, "second_value" : "two"},"dos" : {"first_value" : 3, "second_value" : "four"}}
    res = from_dict(dict[str,SimpleDataclass], dict_values)

    # Ensure the result is a dictionary containing dataclass instances
    assert isinstance(res, dict)
    assert isinstance(res["uno"], SimpleDataclass)
    assert isinstance(res["dos"], SimpleDataclass)
    assert res["uno"].first_value == 1
    assert res["uno"].second_value == "two"
    assert res["dos"].first_value == 3
    assert res["dos"].second_value == "four"

def test_call_datas_from_dict_method():
    """
    Test calling Data's from_dict method.
    Checks if from_dict correctly uses custom from_dict methods when available.
    """
    @dataclass
    class MyData(Data):
        val : int

    @dataclass
    class MainClass:
        data_class : MyData

    my_dict = {"data_class":{"val":1}}
    res = from_dict(MainClass,my_dict)

    # Check initial conversion
    assert res.data_class.val == 1

    # Mock MyData's from_dict method and verify it's used
    MyData.from_dict = mock.MagicMock(return_value=MyData(val=3))
    res = from_dict(MainClass,my_dict)
    assert res.data_class.val == 3

def test_convert_to_nested_list_in_dict():
    """
    Test conversion of a dictionary with nested lists.
    Ensures that from_dict can handle dictionaries containing lists of dictionaries.
    """
    dict_values = {"nested":[{"first_value" : 1, "second_value" : "two"},{"first_value" : 3, "second_value" : "four"}]}
    res = from_dict(dict[str,list[dict]], dict_values)

    # Verify the structure and values of the nested list
    assert isinstance(res, dict)
    assert isinstance(res["nested"], list)
    assert len(res["nested"]) == 2
    assert res["nested"][0]["first_value"]== 1
    assert res["nested"][0]["second_value"] == "two"
    assert res["nested"][1]["first_value"]== 3
    assert res["nested"][1]["second_value"] == "four"

def test_convert_to_nested_list_of_dataclass_in_dict():
    """
    Test conversion of a dictionary with nested lists of dataclasses.
    Checks if from_dict can create a dictionary containing a list of dataclass instances.
    """
    @dataclass
    class SimpleDataclass:
        first_value : int
        second_value : str

    dict_values = {"nested":[{"first_value" : 1, "second_value" : "two"},{"first_value" : 3, "second_value" : "four"}]}
    res = from_dict(dict[str,list[SimpleDataclass]], dict_values)

    # Ensure the result is a dictionary containing a list of dataclass instances
    assert isinstance(res, dict)
    assert isinstance(res["nested"], list)
    assert len(res["nested"]) == 2
    assert isinstance(res["nested"][0], SimpleDataclass)
    assert isinstance(res["nested"][1], SimpleDataclass)
    assert res["nested"][0].first_value == 1
    assert res["nested"][0].second_value == "two"
    assert res["nested"][1].first_value == 3
    assert res["nested"][1].second_value == "four"

def test_convert_to_dataclass_with_list():
    """
    Test conversion of a dictionary to a dataclass with a list.
    Verifies that from_dict can handle dataclasses containing list attributes.
    """
    @dataclass
    class SimpleDataclass:
        first_value : int
        second_value : str
        lst : list[str]

    dict_values = {"first_value" : 1, "second_value" : "two", "lst":["three", "four"]}
    res = from_dict(SimpleDataclass, dict_values)

    # Check if the dataclass is correctly created with the list attribute
    assert isinstance(res, SimpleDataclass)
    assert res.first_value == 1
    assert res.second_value == "two"
    assert len(res.lst) == 2
    assert res.lst[0] == "three"
    assert res.lst[1] == "four"

def test_convert_to_dataclass_with_dict():
    """
    Test conversion of a dictionary to a dataclass with a dictionary.
    Verifies that from_dict can handle dataclasses containing dictionary attributes.
    """
    @dataclass
    class ChildDataclass(Data):
        value : int

    @dataclass
    class MotherDataclass(Data):
        first_value : int
        second_value : str
        childs : dict[str, ChildDataclass]

    dict_values = {"first_value" : 1, "second_value" : "two", "childs":{"one":{"value": 1}, "two":{"value":2}}}
    res = from_dict(MotherDataclass, dict_values)

    # Check if the dataclass is correctly created with the list attribute
    assert isinstance(res, MotherDataclass)
    assert res.first_value == 1
    assert res.second_value == "two"
    assert isinstance(res.childs, dict)
    assert isinstance(res.childs["one"], ChildDataclass)
    assert isinstance(res.childs["two"], ChildDataclass)
    assert res.childs["one"].value == 1
    assert res.childs["two"].value == 2

def test_should_skip_extra_member_of_Data_type_class():
    
    @dataclass
    class SimpleDataclass(Data):
        value_one : int

    dict_values = {"value_one":1, "extra_value":2}
    res = SimpleDataclass.from_dict(dict_values)
    assert isinstance(res, SimpleDataclass)
    assert res.value_one == 1

def test_should_skip_extra_member_of_dataclass():
    
    @dataclass
    class SimpleDataclass:
        value_one : int

    dict_values = {"value_one":1, "extra_value":2}
    res = from_dict(SimpleDataclass,dict_values)
    assert isinstance(res, SimpleDataclass)
    assert res.value_one == 1
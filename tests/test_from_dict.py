import unittest
from unittest import mock
from eventsourcing.data import from_dict, Data
from dataclasses import dataclass


class FromDictTest(unittest.TestCase):

    def test_convert_to_dict(self) -> None:

        dict_values = {"first_value" : 1, "second_value" : "two"}

        res = from_dict(dict, dict_values)

        assert isinstance(res, dict)

        assert res["first_value"] == 1
        assert res["second_value"] == "two"

    def test_convert_to_simple_dataclass(self) -> None:

        @dataclass
        class SimpleDataclass:
            first_value : int
            second_value : str

        dict_values = {"first_value" : 1, "second_value" : "two"}

        res = from_dict(SimpleDataclass, dict_values)

        assert isinstance(res, SimpleDataclass)

        assert res.first_value == 1
        assert res.second_value == "two"

    def test_convert_to_nested_dict(self) -> None:

        dict_values = {"first_value" : 1, "second_value" : "two", "nested":{"first_value" : 3, "second_value" : "four"}}

        res = from_dict(dict, dict_values)

        assert isinstance(res, dict)

        assert res["first_value"] == 1
        assert res["second_value"] == "two"
        assert isinstance(res["nested"], dict)
        assert res["nested"]["first_value"] == 3
        assert res["nested"]["second_value"] == "four"

    def test_convert_to_nested_dataclass(self) -> None:
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

        assert isinstance(res, NesterDataclass)

        assert res.first_value == 1
        assert res.second_value == "two"
        assert isinstance(res.nested, NestedDataclass)
        assert res.nested.first_value == 3
        assert res.nested.second_value == "four"

    def test_convert_to_nested_dataclass_in_dict(self) -> None:

        @dataclass
        class SimpleDataclass:
            first_value : int
            second_value : str

        dict_values = {"uno" : {"first_value" : 1, "second_value" : "two"},"dos" : {"first_value" : 3, "second_value" : "four"}}

        res = from_dict(dict[str,SimpleDataclass], dict_values)

        assert isinstance(res, dict)

        assert isinstance(res["uno"], SimpleDataclass)
        assert isinstance(res["dos"], SimpleDataclass)

        assert res["uno"].first_value == 1
        assert res["uno"].second_value == "two"
        assert res["dos"].first_value == 3
        assert res["dos"].second_value == "four"

    def test_call_datas_from_dict_methode(self) -> None:

        @dataclass
        class MyData(Data):
            val : int

        @dataclass
        class MainClass:
            data_class : MyData

        my_dict = {"data_class":{"val":1}}
        res = from_dict(MainClass,my_dict)

        assert res.data_class.val == 1

        MyData.from_dict = mock.MagicMock(return_value=MyData(val=3))
        res = from_dict(MainClass,my_dict)

        assert res.data_class.val == 3

    def test_convert_to_nested_list_in_dict(self) -> None:
        dict_values = {"nested":[{"first_value" : 1, "second_value" : "two"},{"first_value" : 3, "second_value" : "four"}]}

        res = from_dict(dict[str,list[dict]], dict_values)

        assert isinstance(res, dict)

        assert isinstance(res["nested"], list)
        assert len(res["nested"]) == 2

        assert res["nested"][0]["first_value"]== 1
        assert res["nested"][0]["second_value"] == "two"
        assert res["nested"][1]["first_value"]== 3
        assert res["nested"][1]["second_value"] == "four"

    def test_convert_to_nested_list_of_dataclass_in_dict(self) -> None:
        @dataclass
        class SimpleDataclass:
            first_value : int
            second_value : str

        dict_values = {"nested":[{"first_value" : 1, "second_value" : "two"},{"first_value" : 3, "second_value" : "four"}]}

        res = from_dict(dict[str,list[SimpleDataclass]], dict_values)

        assert isinstance(res, dict)

        assert isinstance(res["nested"], list)
        assert len(res["nested"]) == 2

        assert res["nested"][0].first_value == 1
        assert res["nested"][0].second_value == "two"
        assert res["nested"][1].first_value == 3
        assert res["nested"][1].second_value == "four"

    def test_convert_to_dataclass_with_list(self) -> None:
        @dataclass
        class SimpleDataclass:
            first_value : int
            second_value : str
            lst : list[str]

        dict_values = {"first_value" : 1, "second_value" : "two", "lst":["three", "four"]}

        res = from_dict(SimpleDataclass, dict_values)

        assert isinstance(res, SimpleDataclass)


        assert res.first_value == 1
        assert res.second_value == "two"
        assert len(res.lst) == 2
        assert res.lst[0] == "three"
        assert res.lst[1] == "four"

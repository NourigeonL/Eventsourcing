import unittest
from unittest import mock
from eventsourcing.data import to_dict, Data
from dataclasses import dataclass

class ToDictTest(unittest.TestCase):

    def test_convert_simple_dataclass_to_dict(self) -> None:
        @dataclass
        class SimpleDataclass:
            val_one : int
            val_two : str

        my_obj = SimpleDataclass(val_one=1, val_two="two")
        res = to_dict(my_obj)

        assert "val_one" in res
        assert "val_two" in res
        assert res["val_one"] == 1
        assert res["val_two"] == "two"

    def test_convert_nested_dataclass_to_dict(self) -> None:

        @dataclass
        class NestedDataclass:
            val_three : int
            val_four : str

        @dataclass
        class NesterDataclass:
            val_one : int
            val_two : str
            nested : NestedDataclass

        my_obj = NesterDataclass(val_one=1, val_two="two", nested=NestedDataclass(val_three=3, val_four="four"))
        res = to_dict(my_obj)

        assert "val_one" in res
        assert "val_two" in res
        assert "nested" in res
        assert "val_three" in res["nested"]
        assert "val_four" in res["nested"]
        assert res["val_one"] == 1
        assert res["val_two"] == "two"
        assert res["nested"]["val_three"] == 3
        assert res["nested"]["val_four"] == "four"

    def test_convert_nested_list_dataclass_to_dict(self) -> None:
        @dataclass
        class NestedDataclass:
            first_val : int
            second_val : str

        @dataclass
        class ListNesterDataclass:
            val_one : int
            val_two : str
            nested_list : list[NestedDataclass]


        my_obj = ListNesterDataclass(val_one=1, val_two="two", nested_list=[NestedDataclass(first_val=3, second_val="four"), NestedDataclass(first_val=5, second_val="six")])
        res = to_dict(my_obj)
        assert "val_one" in res
        assert "val_two" in res
        assert "nested_list" in res
        assert len(res["nested_list"]) == 2
        assert res["nested_list"][0]["first_val"] == 3
        assert res["nested_list"][0]["second_val"] == "four"
        assert res["nested_list"][1]["first_val"] == 5
        assert res["nested_list"][1]["second_val"] == "six"

    def test_call_datas_to_dict_methode(self) -> None:

        @dataclass
        class MyData(Data):
            val : int

        @dataclass
        class MainClass:
            data_class : MyData

        my_data_obj = MyData(val=1)
        my_obj = MainClass(data_class=my_data_obj)

        res = to_dict(my_obj)

        assert res["data_class"]["val"] == 1

        my_data_obj.to_dict = mock.MagicMock(return_value={"val" : 3})



        res = to_dict(my_obj)

        assert res["data_class"]["val"] == 3

    def test_convert_nested_list_dict_to_dict(self) -> None:

        my_obj = {"val_one":1, "val_two":"two", "nested_list":[{"first_val":3, "second_val":"four"}, {"first_val":5, "second_val":"six"}]}
        res = to_dict(my_obj)
        assert "val_one" in res
        assert "val_two" in res
        assert "nested_list" in res
        assert len(res["nested_list"]) == 2
        assert res["nested_list"][0]["first_val"] == 3
        assert res["nested_list"][0]["second_val"] == "four"
        assert res["nested_list"][1]["first_val"] == 5
        assert res["nested_list"][1]["second_val"] == "six"
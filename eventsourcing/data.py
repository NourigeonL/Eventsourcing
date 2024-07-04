from dataclasses import dataclass, is_dataclass
from typing import get_args, get_origin, TypeVar

def __get_subclass(cls : type, args : tuple, origin : type, key : str, value : any) -> type:
    if is_dataclass(cls):
        sub_cls = cls.__dict__["__dataclass_fields__"][key].type
    elif origin == dict:
        sub_cls = args[1]
    else:
        sub_cls = type(value)
    return sub_cls

T = TypeVar("T")
def to_dict(obj : object) -> dict | object:
        try:
            res = {}
            items_dict = {}
            if isinstance(obj, dict):
                items_dict = obj
            elif is_dataclass(obj):
                items_dict = vars(obj)
            else:
                return obj
            for key, value in items_dict.items():
                if isinstance(value, Data):
                    res[key] = value.to_dict()
                elif is_dataclass(value) or isinstance(value, dict):
                    res[key] = to_dict(value)
                elif isinstance(value, list):
                    new_list = []
                    for val in value:
                        new_list.append(to_dict(val))
                    res[key] = new_list
                else:
                    res[key] = value
            return res
        except Exception as e:
            raise e

def from_dict(cls : type[T], values : any) -> T:
    try:
        if not isinstance(values, dict):
            return cls(values)
        new_dict = {}
        args = get_args(cls)
        origin = get_origin(cls)
        for key, value in values.items():
            if isinstance(value, dict):
                sub_cls = __get_subclass(cls, args, origin, key, value)
                if issubclass(sub_cls, Data):
                    new_dict[key] = sub_cls.from_dict(value)
                else:
                    new_dict[key] = from_dict(sub_cls, value)
            elif isinstance(value, list):
                sub_cls = __get_subclass(cls, args, origin, key, value)
                sub_arg = get_args(sub_cls)
                new_list = []
                for val in value:
                    new_list.append(from_dict(sub_arg[0], val))
                new_dict[key] = new_list
            else:
                new_dict[key] = value
        return cls(**new_dict)
    except Exception as e:
        raise e


@dataclass
class Data:
    def to_dict(self) -> dict:
        return to_dict(self)

    @classmethod
    def from_dict(cls : type[T], dict_values : dict) -> T:
        return from_dict(cls, dict_values)
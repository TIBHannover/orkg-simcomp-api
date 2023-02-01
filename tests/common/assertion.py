from typing import Dict, Type, Any


def assert_keys_in_dict(obj: Dict[str, Any], keys_types: Dict[str, Type], exact=True):
    """
    assert whether obj includes the keys and their types.

    :param obj: object to assert.
    :param keys_types: key names and their types.
    :param exact: indicates whether the inclusion is exact. Defaults to True.
    """

    if exact:
        assert obj.keys() == keys_types.keys()

    for key, key_type in keys_types.items():

        if not exact:
            assert key in obj

        assert isinstance(obj[key], key_type)

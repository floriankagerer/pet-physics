"""Helper functions for serialization and deserialization of data model objects."""


def to_dict(data_object: object) -> dict:
    """Convert a dataclass instance to a dictionary.

    Args:
        data_object: The dataclass instance to convert.

    Returns:
        Dictionary representation of the data object.
    """
    return data_object.to_dict()


def from_dict(dictionary: dict, cls: type) -> object:
    """Convert a dictionary to a data object.

    Args:
        dictionary: The dictionary representation of the data object.
        cls: The class of the data object to convert to.

    Returns:
        Instance of dataclass cls created from the dictionary.
    """
    return cls.from_dict(dictionary)

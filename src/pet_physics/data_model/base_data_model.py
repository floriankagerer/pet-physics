"""Base class for the data models."""

from abc import ABC
from dataclasses import dataclass, fields
from typing import Self


@dataclass
class BaseDataModel(ABC):
    """Base class for data model that deserializes instances by prefering a defined `alias`."""

    @classmethod
    def from_dict(cls, serialized: dict) -> Self:
        """Deserialize dictionary into dataclass instance, prefering defined `alias`."""
        init_kwargs = {}

        for f in fields(cls):
            alias = f.metadata.get("alias", None)
            field_name = f.name

            if alias is not None and alias in serialized:
                init_kwargs[field_name] = serialized[alias]
            elif field_name in serialized:
                init_kwargs[field_name] = serialized[field_name]

        return cls(**init_kwargs)

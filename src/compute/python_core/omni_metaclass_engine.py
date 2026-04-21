"""
OMNI Metaclass Engine
=====================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from __future__ import annotations

ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI METACLASS ENGINE (SEMESTER 3 — BATCH 38.6)
# ===========================================================================
# Absorbed From  : Django ORM metaclass + SQLAlchemy declarative + attrs + pydantic
# Logic Inherited: Python / Compute Layer (Metaclass-Driven ORM & Validation)
# ===========================================================================
#
# By studying Django's ModelBase metaclass and pydantic's ModelMetaclass,
# Mother learned Python metaclass patterns:
#   1. __init_subclass__ intercepts class creation
#   2. __set_name__ captures the attribute name from the owner class
#   3. Descriptors (__get__/__set__) enable lazy/validated fields
#   4. __annotations__ introspection for type-driven code generation
#   5. Registry pattern: metaclass auto-registers all subclasses

import datetime
import re
from typing import (
    Any, Callable, ClassVar, Dict, List, Optional, Set, Tuple, Type, TypeVar, get_type_hints
)

T = TypeVar("T")


# ============================================================
# PART 1: Field Descriptors
# ============================================================

class Field:
    """Descriptor-based field with validation, default, and metadata."""

    __slots__ = (
        "name", "field_type", "default", "default_factory",
        "required", "validator", "min_val", "max_val",
        "min_length", "max_length", "pattern", "choices",
        "primary_key", "unique", "index", "column_name",
        "_total_gets", "_total_sets", "_total_validations",
    )

    def __init__(
        self,
        field_type: Type = Any,
        *,
        default: Any = None,
        default_factory: Optional[Callable] = None,
        required: bool = True,
        validator: Optional[Callable] = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        choices: Optional[Set] = None,
        primary_key: bool = False,
        unique: bool = False,
        index: bool = False,
        column_name: Optional[str] = None,
    ):
        """Initialize Field."""
        self.field_type = field_type
        self.default = default
        self.default_factory = default_factory
        self.required = required
        self.validator = validator
        self.min_val = min_val
        self.max_val = max_val
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.choices = choices
        self.primary_key = primary_key
        self.unique = unique
        self.index = index
        self.column_name = column_name
        self.name = ""
        self._total_gets = 0
        self._total_sets = 0
        self._total_validations = 0

    def __set_name__(self, owner: Type, name: str) -> None:
        """Called when the descriptor is assigned to a class attribute."""
        self.name = name
        if self.column_name is None:
            self.column_name = name

    def __get__(self, obj: Any, objtype: Type = None) -> Any:
        if obj is None:
            return self
        self._total_gets += 1
        return obj.__dict__.get(self.name, self._get_default())

    def __set__(self, obj: Any, value: Any) -> None:
        self._total_sets += 1
        validated = self.validate(value)
        obj.__dict__[self.name] = validated

    def _get_default(self) -> Any:
        if self.default_factory is not None:
            return self.default_factory()
        return self.default

    def validate(self, value: Any) -> Any:
        """Full validation chain."""
        self._total_validations += 1

        # Required check
        if value is None:
            if self.required:
                raise ValueError(f"Field '{self.name}' is required")
            return value

        # Type check
        if self.field_type is not Any and not isinstance(value, self.field_type):
            try:
                value = self.field_type(value)
            except (TypeError, ValueError) as e:
                raise TypeError(
                    f"Field '{self.name}': expected {self.field_type.__name__}, "
                    f"got {type(value).__name__}"
                ) from e

        # Numeric range
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f"Field '{self.name}': {value} < min({self.min_val})")
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f"Field '{self.name}': {value} > max({self.max_val})")

        # String length
        if isinstance(value, str):
            if self.min_length is not None and len(value) < self.min_length:
                raise ValueError(
                    f"Field '{self.name}': length {len(value)} < min_length({self.min_length})"
                )
            if self.max_length is not None and len(value) > self.max_length:
                raise ValueError(
                    f"Field '{self.name}': length {len(value)} > max_length({self.max_length})"
                )

        # Regex pattern
        if self.pattern is not None and isinstance(value, str):
            if not re.match(self.pattern, value):
                raise ValueError(
                    f"Field '{self.name}': '{value}' doesn't match pattern '{self.pattern}'"
                )

        # Choices (enum-like)
        if self.choices is not None and value not in self.choices:
            raise ValueError(
                f"Field '{self.name}': '{value}' not in {self.choices}"
            )

        # Custom validator
        if self.validator is not None:
            if not self.validator(value):
                raise ValueError(f"Field '{self.name}': custom validation failed")

        return value


# ============================================================
# PART 2: Model Metaclass
# ============================================================

_MODEL_REGISTRY: Dict[str, Type] = {}


class ModelMeta(type):
    """Metaclass that auto-discovers Field descriptors and builds schema."""

    def __new__(mcs, name: str, bases: Tuple[Type, ...], namespace: Dict[str, Any]):
        cls = super().__new__(mcs, name, bases, namespace)

        if name == "Model":
            return cls

        # Collect fields from all bases + current class
        fields: Dict[str, Field] = {}
        for base in reversed(cls.__mro__):
            for attr_name, attr_val in vars(base).items():
                if isinstance(attr_val, Field):
                    fields[attr_name] = attr_val

        cls._fields = fields
        cls._table_name = namespace.get("__tablename__", name.lower() + "s")
        cls._primary_key = None

        for fname, field in fields.items():
            if field.primary_key:
                cls._primary_key = fname

        # Auto-register in global registry
        _MODEL_REGISTRY[name] = cls

        return cls


# ============================================================
# PART 3: Base Model
# ============================================================

class Model(metaclass=ModelMeta):
    """Base model with metaclass-driven field discovery, validation, and serialization."""

    _fields: ClassVar[Dict[str, Field]] = {}
    _table_name: ClassVar[str] = ""
    _primary_key: ClassVar[Optional[str]] = None

    def __init__(self, **kwargs: Any):
        """Initialize Model."""
        for name, field in self._fields.items():
            if name in kwargs:
                setattr(self, name, kwargs[name])
            elif not field.required:
                setattr(self, name, field._get_default())
            elif field.default is not None or field.default_factory is not None:
                setattr(self, name, field._get_default())
            # If required and no default, it will be validated on access

    def validate_all(self) -> List[str]:
        """Validate all fields, return list of errors."""
        errors = []
        for name, field in self._fields.items():
            try:
                value = self.__dict__.get(name)
                field.validate(value)
            except (ValueError, TypeError) as e:
                errors.append(str(e))
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        result = {}
        for name in self._fields:
            value = self.__dict__.get(name)
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            elif isinstance(value, Model):
                value = value.to_dict()
            result[name] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Model":
        """Deserialize from dictionary."""
        return cls(**data)

    @classmethod
    def schema(cls) -> Dict[str, Dict[str, Any]]:
        """Return JSON-schema-like description."""
        result = {}
        for name, field in cls._fields.items():
            result[name] = {
                "type": field.field_type.__name__ if field.field_type is not Any else "any",
                "required": field.required,
                "primary_key": field.primary_key,
                "unique": field.unique,
                "index": field.index,
                "column": field.column_name,
            }
        return result

    def __repr__(self) -> str:
        fields = ", ".join(
            f"{k}={self.__dict__.get(k)!r}" for k in self._fields
        )
        return f"{self.__class__.__name__}({fields})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.to_dict() == other.to_dict()


# ============================================================
# PART 4: Query Builder (Fluent Interface)
# ============================================================

class QueryBuilder:
    """Chainable query builder for Model classes."""

    def __init__(self, model_cls: Type[Model]):
        """Initialize QueryBuilder."""
        self._model = model_cls
        self._filters: List[Callable] = []
        self._order_key: Optional[str] = None
        self._order_reverse: bool = False
        self._limit_val: Optional[int] = None
        self._offset_val: int = 0
        self._data: List[Model] = []

    def set_data(self, data: List[Model]) -> "QueryBuilder":
        """Set data for QueryBuilder."""
        self._data = data
        return self

    def filter(self, predicate: Callable[[Model], bool]) -> "QueryBuilder":
        """Execute filter operation for QueryBuilder."""
        self._filters.append(predicate)
        return self

    def where(self, **kwargs: Any) -> "QueryBuilder":
        """Execute where operation for QueryBuilder."""
        def pred(obj: Model) -> bool:
            return all(
                getattr(obj, k, None) == v for k, v in kwargs.items()
            )
        self._filters.append(pred)
        return self

    def order_by(self, key: str, reverse: bool = False) -> "QueryBuilder":
        """Execute order by operation for QueryBuilder."""
        self._order_key = key
        self._order_reverse = reverse
        return self

    def limit(self, n: int) -> "QueryBuilder":
        """Execute limit operation for QueryBuilder."""
        self._limit_val = n
        return self

    def offset(self, n: int) -> "QueryBuilder":
        """Execute offset operation for QueryBuilder."""
        self._offset_val = n
        return self

    def execute(self) -> List[Model]:
        """Execute execute operation for QueryBuilder."""
        result = list(self._data)

        for f in self._filters:
            result = [obj for obj in result if f(obj)]

        if self._order_key:
            result.sort(
                key=lambda obj: getattr(obj, self._order_key, None) or 0,
                reverse=self._order_reverse,
            )

        result = result[self._offset_val:]
        if self._limit_val is not None:
            result = result[:self._limit_val]

        return result

    def first(self) -> Optional[Model]:
        """Execute first operation for QueryBuilder."""
        results = self.limit(1).execute()
        return results[0] if results else None

    def count(self) -> int:
        """Execute count operation for QueryBuilder."""
        return len(self.execute())


# ============================================================
# Diagnostics
# ============================================================

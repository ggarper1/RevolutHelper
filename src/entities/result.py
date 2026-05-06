from typing import Generic, TypeVar, Optional
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    data: Optional[T] = None
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    @classmethod
    def success(cls, data: T) -> "Result[T]":
        return cls(data=data)

    @classmethod
    def failure(cls, error: str) -> "Result[T]":
        return cls(error=error)

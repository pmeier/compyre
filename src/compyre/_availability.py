import functools
import importlib.metadata
from typing import Any, Callable

import packaging.requirements

__all__ = ["available_if", "is_available"]

packages_distributions = functools.cache(importlib.metadata.packages_distributions)


class _Requirement:
    def __init__(self, requirement_string: str) -> None:
        self._requirement = packaging.requirements.Requirement(requirement_string)

    @functools.cached_property
    def is_available(self) -> bool:
        try:
            distribution = importlib.metadata.distribution(self._requirement.name)
        except importlib.metadata.PackageNotFoundError:
            return False

        if (
            self._requirement.specifier
            and distribution.version not in self._requirement.specifier
        ):
            return False

        for module_name in {  # pragma: no cover
            module_name
            for module_name, distribution_names in packages_distributions().items()
            if distribution.name in distribution_names
        }:
            try:
                importlib.import_module(module_name)
            except Exception:
                return False

        return True

    def __str__(self) -> str:  # pragma: no cover
        return str(self._requirement)

    def __repr__(self) -> str:  # pragma: no cover
        return f"{type(self).__module__}.{type(self).__name__}({self!s})"


def available_if(*requirement_strings: str) -> Callable:
    requirements = [_Requirement(s) for s in requirement_strings]

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not_met := [r for r in requirements if not r.is_available]:
                parts = [f"The following requirements for {fn.__name__} are not met:\n"]
                parts.extend(f"- {r}" for r in not_met)
                raise RuntimeError("\n".join(parts))

            return fn(*args, **kwargs)

        setattr(wrapper, "__requirements__", requirements)

        return wrapper

    return decorator


def is_available(obj: Any) -> bool:
    requirements: list[_Requirement] | None = getattr(obj, "__requirements__", None)
    if requirements is None:
        return True

    return all(r.is_available for r in requirements)

from typing import Protocol, Any, Dict, Type


class LLM(Protocol):
    def model(self) -> Any: ...

class ModelFactory:
    _registry: Dict[str, Type[LLM]] = {}

    @classmethod
    def register(cls, name: str, impl: Type[LLM]) -> None:
        cls._registry[name.lower()] = impl

    @classmethod
    def create(cls, name: str, **kwargs) -> LLM:
        try:
            impl = cls._registry[name.lower()]
        except KeyError:
            valid = ", ".join(sorted(cls._registry))
            raise ValueError(f"Unknown model '{name}'. Valid: {valid}")
        return impl(**kwargs)

        

    

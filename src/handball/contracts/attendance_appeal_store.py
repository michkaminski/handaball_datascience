from typing import Protocol

from maf.artifacts import ModelArtifact


class ModeleMafReadStore(Protocol):
    def latest(self, key: str) -> ModelArtifact | None: ...

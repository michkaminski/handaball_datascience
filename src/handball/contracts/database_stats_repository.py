from typing import Protocol

from handball.domain.database_stats import SnapshotStatystykBazy


class StatystykiBazyReadRepository(Protocol):
    def pobierz_snapshot(self) -> SnapshotStatystykBazy: ...

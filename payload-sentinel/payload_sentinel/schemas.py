"""Schémas de données (analyse SQL vs payload JSON)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SqlColumn:
    """Colonne extraite d'une requête SELECT."""

    table: str
    column: str
    wildcard: bool = False

    @property
    def leaf_name(self) -> str:
        return self.column if not self.wildcard else "*"


@dataclass(frozen=True)
class SqlCapture:
    """Une requête SQL et ses colonnes lues."""

    sql: str
    columns: tuple[SqlColumn, ...]


@dataclass(frozen=True)
class SensitiveHit:
    """Champ sensible trouvé dans la réponse JSON."""

    field_path: str
    matched_pattern: str


@dataclass
class PayloadAnalysisReport:
    """Rapport comparant colonnes SQL et champs JSON renvoyés."""

    sql_columns_fetched: list[str] = field(default_factory=list)
    response_field_paths: list[str] = field(default_factory=list)
    unused_columns: list[str] = field(default_factory=list)
    used_columns: list[str] = field(default_factory=list)
    overfetch_ratio: float = 0.0
    overfetch_detected: bool = False
    sensitive_hits: list[SensitiveHit] = field(default_factory=list)
    sensitive_leak_detected: bool = False
    response_parsed: bool = False


@dataclass(frozen=True)
class PayloadSentinelConfig:
    """Configuration résolue."""

    enabled: bool = True
    sensitive_fields: tuple[str, ...] = ()
    overfetch_threshold: float = 0.85
    block_sensitive_leak: bool = True
    debug_headers: bool = True
    structlog_enabled: bool = True
    log_overfetch: bool = True
    strict_in_tests: bool = False

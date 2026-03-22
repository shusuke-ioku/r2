"""Data models for the skills engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class SkillRecord:
    """A parsed skill from SKILL.md."""

    name: str
    description: str
    body: str
    file_path: Path
    content_hash: str = ""
    last_indexed: datetime | None = None

    def to_document(self) -> str:
        """Serialize skill to a single document string for indexing."""
        return (
            f"Skill: {self.name}\n"
            f"Description: {self.description}\n\n"
            f"{self.body}"
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "body_preview": self.body[:500] + ("..." if len(self.body) > 500 else ""),
            "file_path": str(self.file_path),
            "content_hash": self.content_hash,
            "last_indexed": self.last_indexed.isoformat() if self.last_indexed else None,
        }


@dataclass
class DispatchResult:
    """A skill recommendation from semantic dispatch."""

    skill_name: str
    confidence: float
    reason: str
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "confidence": round(self.confidence, 3),
            "reason": self.reason,
            "description": self.description,
        }


@dataclass
class UsageEvent:
    """A recorded skill usage event."""

    skill_name: str
    query: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "query": self.query,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SkillRelationship:
    """A discovered relationship between skills."""

    source: str
    target: str
    relationship: str
    weight: float = 1.0

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "relationship": self.relationship,
            "weight": round(self.weight, 3),
        }

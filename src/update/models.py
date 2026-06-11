# -*- coding: utf-8 -*-
"""
Update system data models
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from src.core.version import SemanticVersion


@dataclass
class VersionInfo:
    """Version information from GitHub release"""
    version: SemanticVersion
    minimum_supported_version: SemanticVersion
    download_url: str
    sha256: str
    mandatory: bool = False
    release_notes: List[str] = field(default_factory=list)
    published_at: Optional[datetime] = None
    file_size: int = 0
    
    @classmethod
    def from_json(cls, data: dict) -> 'VersionInfo':
        """Create from JSON data"""
        return cls(
            version=SemanticVersion(data['version']),
            minimum_supported_version=SemanticVersion(data['minimum_supported_version']),
            download_url=data['download_url'],
            sha256=data['sha256'],
            mandatory=data.get('mandatory', False),
            release_notes=data.get('release_notes', []),
            published_at=datetime.fromisoformat(data['published_at']) if data.get('published_at') else None,
            file_size=data.get('file_size', 0),
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'version': str(self.version),
            'minimum_supported_version': str(self.minimum_supported_version),
            'download_url': self.download_url,
            'sha256': self.sha256,
            'mandatory': self.mandatory,
            'release_notes': self.release_notes,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'file_size': self.file_size,
        }


@dataclass
class UpdateResult:
    """Result of update check"""
    update_available: bool = False
    version_info: Optional[VersionInfo] = None
    error: Optional[str] = None
    is_online: bool = False
    
    @property
    def is_mandatory(self) -> bool:
        """Check if update is mandatory"""
        return self.version_info and self.version_info.mandatory
    
    @property
    def current_version_str(self) -> str:
        """Get current version string"""
        from src.core.version import APP_VERSION
        return str(APP_VERSION)
    
    @property
    def latest_version_str(self) -> str:
        """Get latest version string"""
        return str(self.version_info.version) if self.version_info else "Unknown"

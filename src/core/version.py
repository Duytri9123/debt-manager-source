# -*- coding: utf-8 -*-
"""
Version management with Semantic Versioning
"""
import re
from typing import Tuple


class SemanticVersion:
    """Semantic version parser and comparator"""
    
    VERSION_PATTERN = re.compile(
        r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)'
        r'(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
        r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
        r'(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    )
    
    def __init__(self, version_str: str):
        """Parse semantic version string"""
        self.version_str = version_str.strip()
        
        match = self.VERSION_PATTERN.match(self.version_str)
        if not match:
            raise ValueError(f"Invalid semantic version: {version_str}")
        
        self.major = int(match.group('major'))
        self.minor = int(match.group('minor'))
        self.patch = int(match.group('patch'))
        self.prerelease = match.group('prerelease')
        self.build_metadata = match.group('buildmetadata')
        
    def __str__(self) -> str:
        """Return version string"""
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build_metadata:
            version += f"+{self.build_metadata}"
        return version
    
    def __repr__(self) -> str:
        return f"SemanticVersion('{self}')"
    
    def _compare_tuple(self) -> Tuple[int, int, int]:
        """Return tuple for comparison"""
        return (self.major, self.minor, self.patch)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, SemanticVersion):
            return False
        return self._compare_tuple() == other._compare_tuple()
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self._compare_tuple() < other._compare_tuple()
    
    def __le__(self, other) -> bool:
        return self.__eq__(other) or self.__lt__(other)
    
    def __gt__(self, other) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self._compare_tuple() > other._compare_tuple()
    
    def __ge__(self, other) -> bool:
        return self.__eq__(other) or self.__gt__(other)
    
    def is_major_update(self, other: 'SemanticVersion') -> bool:
        """Check if other version is a major update"""
        return other.major > self.major
    
    def is_minor_update(self, other: 'SemanticVersion') -> bool:
        """Check if other version is a minor update"""
        return other.major == self.major and other.minor > self.minor
    
    def is_patch_update(self, other: 'SemanticVersion') -> bool:
        """Check if other version is a patch update"""
        return (other.major == self.major and 
                other.minor == self.minor and 
                other.patch > self.patch)


# Current application version
APP_VERSION = SemanticVersion("1.0.0")
APP_NAME = "Quản lý B2B"
APP_COMPANY = "B2B Management"
APP_ID = "com.b2bmanagement.quanlyb2b"

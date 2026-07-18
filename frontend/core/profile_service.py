"""
Profile Service.

Manages user profile data using QSettings.
"""

from dataclasses import dataclass
from datetime import datetime
import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, Signal, QSettings

@dataclass
class UserProfile:
    name: str = ""
    resume_path: str = ""
    onboarding_version: int = 0
    created_at: str = ""
    updated_at: str = ""

class ProfileService(QObject):
    profile_updated = Signal(UserProfile)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = QSettings("TellMe", "AppProfile")
        self._profile = self._load()

    def _load(self) -> UserProfile:
        try:
            data = self._settings.value("profile", "{}")
            if isinstance(data, str):
                parsed = json.loads(data)
                return UserProfile(
                    name=parsed.get("name", ""),
                    resume_path=parsed.get("resume_path", ""),
                    onboarding_version=parsed.get("onboarding_version", 0),
                    created_at=parsed.get("created_at", ""),
                    updated_at=parsed.get("updated_at", "")
                )
        except Exception:
            pass
        return UserProfile()

    def _save(self):
        try:
            data = {
                "name": self._profile.name,
                "resume_path": self._profile.resume_path,
                "onboarding_version": self._profile.onboarding_version,
                "created_at": self._profile.created_at,
                "updated_at": self._profile.updated_at
            }
            self._settings.setValue("profile", json.dumps(data))
            self._settings.sync()
            self.profile_updated.emit(self._profile)
        except Exception:
            pass

    @property
    def current_profile(self) -> UserProfile:
        return self._profile

    @property
    def requires_onboarding(self) -> bool:
        """Returns True if the user has not completed onboarding."""
        return not bool(self._profile.name.strip())

    def verify_resume(self) -> bool:
        """Checks if the stored resume still exists."""
        if not self._profile.resume_path:
            return True # Not having a resume is valid
        if not os.path.exists(self._profile.resume_path):
            # Clear it if it's missing
            self.update_profile(resume_path="")
            return False
        return True

    def _get_resumes_dir(self) -> Path:
        from backend.config.settings import get_settings
        base_dir = (get_settings().runtime_path / "resumes").resolve()
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir

    def update_profile(self, name: Optional[str] = None, resume_path: Optional[str] = None):
        """Update parts of the profile and save."""
        now = datetime.now().isoformat()
        if not self._profile.created_at:
            self._profile.created_at = now
        self._profile.updated_at = now
        
        if name is not None:
            self._profile.name = name.strip()
        
        if resume_path is not None:
            raw_path = resume_path.strip()
            if raw_path and os.path.exists(raw_path):
                # If it's a new file (not already in our managed directory)
                resumes_dir = self._get_resumes_dir()
                if not str(resumes_dir) in os.path.abspath(raw_path):
                    # Clean up old managed resume if it exists
                    if self._profile.resume_path and os.path.exists(self._profile.resume_path):
                        if str(resumes_dir) in os.path.abspath(self._profile.resume_path):
                            try:
                                os.remove(self._profile.resume_path)
                            except Exception:
                                pass
                    
                    # Copy the new one
                    new_filename = os.path.basename(raw_path)
                    new_path = resumes_dir / new_filename
                    shutil.copy2(raw_path, new_path)
                    self._profile.resume_path = str(new_path)
            elif not raw_path:
                # User cleared the resume
                if self._profile.resume_path and os.path.exists(self._profile.resume_path):
                    resumes_dir = self._get_resumes_dir()
                    if str(resumes_dir) in os.path.abspath(self._profile.resume_path):
                        try:
                            os.remove(self._profile.resume_path)
                        except Exception:
                            pass
                self._profile.resume_path = ""

        # Mark onboarding as completed by bumping version
        if self._profile.name:
            self._profile.onboarding_version = 1

        self._save()

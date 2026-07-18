"""
QSSHydrator — hydrates QSS templates with token values.
"""
import re
from pathlib import Path
from frontend.engine.token_resolver import TokenResolver
from backend.core.logging import get_logger

_logger = get_logger(__name__)

# Matches {colors.accent}, {typography.size_base}, etc.
_TOKEN_REGEX = re.compile(r"\{([\w\.]+)\}")

class QSSHydrator:
    """
    Loads QSS template files and replaces {TOKEN_PATH} with resolved values.
    """
    def __init__(self, resolver: TokenResolver):
        self._resolver = resolver

    def hydrate(self, qss_path: Path) -> str:
        """Read a QSS file and return hydrated content."""
        if not qss_path.exists():
            _logger.error(f"QSS template not found: {qss_path}")
            return ""
        
        with open(qss_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        return self.hydrate_string(template)

    def hydrate_string(self, template: str) -> str:
        """Replace {TOKEN_PATH} with actual values in a string."""
        def repl(match):
            path = match.group(1)
            # QSS units: we let QSS handle px if the template includes it (e.g. {radius.lg}px)
            # We just dump the raw resolved value.
            val = self._resolver.resolve_str(path)
            if val == "":
                _logger.warning(f"QSSHydrator: Unresolved token '{path}'")
                return match.group(0) # leave untouched if not found
            return val

        hydrated = _TOKEN_REGEX.sub(repl, template)
        return hydrated

    def validate(self, template: str) -> list[str]:
        """Return a list of unresolved token paths in the template."""
        unresolved = []
        for match in _TOKEN_REGEX.finditer(template):
            path = match.group(1)
            val = self._resolver.resolve_str(path)
            if val == "":
                unresolved.append(path)
        return unresolved

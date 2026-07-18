"""
GGUF Metadata Extractor.

Reads binary GGUF file headers to extract model architecture,
parameter counts, context lengths, and other metadata without
loading the full model weights into memory.

GGUF Format Reference:
    https://github.com/ggerganov/ggml/blob/master/docs/gguf.md

Design:
    This module performs read-only binary parsing of the GGUF header.
    It never assumes a specific model family. All architecture information
    is read directly from the file's metadata key-value store.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

from backend.config.constants import GGUF_MAGIC, GGUF_MIN_VERSION
from backend.core.exceptions import ModelValidationError
from backend.core.logging import get_logger
from backend.shared.enums.model import ModelArchitecture

_logger = get_logger(__name__)

# Known GGUF metadata keys (vendor-agnostic)
_KEY_ARCHITECTURE = "general.architecture"
_KEY_CONTEXT_LENGTH = "llama.context_length"  # architecture-prefixed in real files
_KEY_PARAM_COUNT = "general.parameter_count"
_KEY_NAME = "general.name"
_KEY_QUANTIZATION = "general.quantization_version"


@dataclass
class GGUFMetadata:
    """
    Structured metadata extracted from a GGUF file header.

    Attributes:
        gguf_version: The GGUF format version (must be >= GGUF_MIN_VERSION).
        architecture: Detected neural network architecture family.
        model_name: Model display name from the file's metadata, if present.
        parameter_count: Total parameter count (e.g., 7_000_000_000 for 7B).
        context_length: Maximum supported context window in tokens.
        quantization: Quantization scheme string (e.g., 'Q4_K_M').
        raw: All raw key-value pairs extracted from the header.
    """

    gguf_version: int
    architecture: ModelArchitecture = ModelArchitecture.UNKNOWN
    model_name: str | None = None
    parameter_count: int | None = None
    context_length: int | None = None
    quantization: str | None = None
    raw: dict = field(default_factory=dict)


class GGUFMetadataExtractor:
    """
    Extracts metadata from GGUF model files by reading binary headers.

    This class reads the minimum required bytes from the file to extract
    architecture and configuration information. It does NOT load model
    weights. Only the file header is scanned.

    Usage:
        extractor = GGUFMetadataExtractor()
        metadata = extractor.extract(Path("/path/to/model.gguf"))
    """

    def extract(self, model_path: Path) -> GGUFMetadata:
        """
        Read and parse the GGUF header from a model file.

        Args:
            model_path: Absolute path to the GGUF file.

        Returns:
            A populated GGUFMetadata instance.

        Raises:
            ModelValidationError: If the file cannot be read or is not a
                                  valid GGUF file.
        """
        if not model_path.is_file():
            raise ModelValidationError(
                f"Model file not found: {model_path}",
                context={"path": str(model_path)},
            )

        _logger.info("Extracting GGUF metadata from: {}", model_path.name)

        try:
            with model_path.open("rb") as f:
                magic = f.read(4)
                if magic != GGUF_MAGIC:
                    raise ModelValidationError(
                        f"Invalid GGUF magic bytes in '{model_path.name}'. "
                        "File may be corrupt or not a GGUF model.",
                        context={"path": str(model_path), "magic": magic.hex()},
                    )

                version = struct.unpack("<I", f.read(4))[0]
                if version < GGUF_MIN_VERSION:
                    raise ModelValidationError(
                        f"Unsupported GGUF version {version} "
                        f"(minimum required: {GGUF_MIN_VERSION})",
                        context={"version": version},
                    )

                tensor_count = struct.unpack("<Q", f.read(8))[0]
                kv_count = struct.unpack("<Q", f.read(8))[0]
                
                metadata_raw = {}
                
                def read_string(file) -> str:
                    length = struct.unpack("<Q", file.read(8))[0]
                    return file.read(length).decode("utf-8")
                
                def read_value(file, val_type: int) -> int | float | str | bool | list | None:
                    if val_type == 0: return struct.unpack("<B", file.read(1))[0]  # UINT8
                    if val_type == 1: return struct.unpack("<b", file.read(1))[0]  # INT8
                    if val_type == 2: return struct.unpack("<H", file.read(2))[0]  # UINT16
                    if val_type == 3: return struct.unpack("<h", file.read(2))[0]  # INT16
                    if val_type == 4: return struct.unpack("<I", file.read(4))[0]  # UINT32
                    if val_type == 5: return struct.unpack("<i", file.read(4))[0]  # INT32
                    if val_type == 6: return struct.unpack("<f", file.read(4))[0]  # FLOAT32
                    if val_type == 7: return bool(struct.unpack("<?", file.read(1))[0])  # BOOL
                    if val_type == 8: return read_string(file)  # STRING
                    if val_type == 9:  # ARRAY
                        arr_type = struct.unpack("<I", file.read(4))[0]
                        arr_len = struct.unpack("<Q", file.read(8))[0]
                        return [read_value(file, arr_type) for _ in range(arr_len)]
                    if val_type == 10: return struct.unpack("<Q", file.read(8))[0] # UINT64
                    if val_type == 11: return struct.unpack("<q", file.read(8))[0] # INT64
                    if val_type == 12: return struct.unpack("<d", file.read(8))[0] # FLOAT64
                    # Unknown type, just skip or return None (not fully implemented for all types)
                    return None

                for _ in range(kv_count):
                    key = read_string(f)
                    vtype = struct.unpack("<I", f.read(4))[0]
                    value = read_value(f, vtype)
                    metadata_raw[key] = value

                _logger.info("GGUF header parsed. Version={}, KV_count={}", version, kv_count)

                arch_str = metadata_raw.get(_KEY_ARCHITECTURE)
                architecture = ModelArchitecture.UNKNOWN
                if isinstance(arch_str, str):
                    try:
                        # Ensure we map string to Enum if it exists, otherwise leave as UNKNOWN
                        architecture = ModelArchitecture(arch_str.lower())
                    except ValueError:
                        pass
                
                # Context length might be architecture-specific (e.g. llama.context_length)
                ctx_len = metadata_raw.get(f"{arch_str}.context_length") if arch_str else None
                if ctx_len is None:
                    ctx_len = metadata_raw.get(_KEY_CONTEXT_LENGTH)

                model_name = metadata_raw.get(_KEY_NAME)
                param_count = metadata_raw.get(_KEY_PARAM_COUNT)
                quantization = metadata_raw.get("general.file_type")

                return GGUFMetadata(
                    gguf_version=version,
                    architecture=architecture,
                    model_name=str(model_name) if model_name is not None else None,
                    parameter_count=int(param_count) if isinstance(param_count, (int, float)) else None,
                    context_length=int(ctx_len) if isinstance(ctx_len, (int, float)) else None,
                    quantization=str(quantization) if quantization is not None else None,
                    raw=metadata_raw,
                )

        except (OSError, struct.error) as exc:
            raise ModelValidationError(
                f"Failed to read GGUF header from '{model_path.name}': {exc}",
                context={"path": str(model_path)},
            ) from exc

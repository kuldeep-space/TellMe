"""
Core Service: Metadata Extractor.

Responsible purely for inspecting model files and populating a ModelDescriptor.
Supports GGUF format natively (via header parsing).
Leaves unknown fields as "unknown" rather than guessing.
"""
import os
import struct
import logging
from backend.domain.models import ModelDescriptor, ModelCapabilities, ModelFormat

logger = logging.getLogger(__name__)


# GGUF magic bytes: GGUF
_GGUF_MAGIC = b"GGUF"

# Known GGUF key names for metadata
_KEY_GENERAL_ARCHITECTURE = b"general.architecture"
_KEY_GENERAL_NAME         = b"general.name"
_KEY_CONTEXT_LENGTH_SUFFIX = b".context_length"
_KEY_QUANTIZATION_VERSION  = b"general.quantization_version"


def _read_gguf_string(f) -> str:
    """Read a GGUF length-prefixed UTF-8 string."""
    length = struct.unpack("<Q", f.read(8))[0]
    return f.read(length).decode("utf-8", errors="replace")


def _skip_gguf_value(f, value_type: int):
    """Skip over a GGUF metadata value without fully decoding it."""
    if value_type == 0:   # UINT8
        f.read(1)
    elif value_type == 1: # INT8
        f.read(1)
    elif value_type == 2: # UINT16
        f.read(2)
    elif value_type == 3: # INT16
        f.read(2)
    elif value_type == 4: # UINT32
        f.read(4)
    elif value_type == 5: # INT32
        f.read(4)
    elif value_type == 6: # FLOAT32
        f.read(4)
    elif value_type == 7: # BOOL
        f.read(1)
    elif value_type == 8: # STRING
        _read_gguf_string(f)
    elif value_type == 9: # ARRAY
        elem_type = struct.unpack("<I", f.read(4))[0]
        count = struct.unpack("<Q", f.read(8))[0]
        for _ in range(count):
            _skip_gguf_value(f, elem_type)
    elif value_type == 10: # UINT64
        f.read(8)
    elif value_type == 11: # INT64
        f.read(8)
    elif value_type == 12: # FLOAT64
        f.read(8)


def _read_gguf_value(f, value_type: int):
    """Read and return a GGUF metadata value."""
    if value_type == 4:   return struct.unpack("<I", f.read(4))[0]   # UINT32
    if value_type == 5:   return struct.unpack("<i", f.read(4))[0]   # INT32
    if value_type == 10:  return struct.unpack("<Q", f.read(8))[0]   # UINT64
    if value_type == 11:  return struct.unpack("<q", f.read(8))[0]   # INT64
    if value_type == 8:   return _read_gguf_string(f)                # STRING
    _skip_gguf_value(f, value_type)
    return None


def _extract_gguf_metadata(filepath: str) -> dict:
    """
    Parse the GGUF file header and extract key metadata fields.
    Returns a dict with whatever could be read; empty on failure.
    """
    meta = {}
    try:
        with open(filepath, "rb") as f:
            magic = f.read(4)
            if magic != _GGUF_MAGIC:
                return meta

            _version = struct.unpack("<I", f.read(4))[0]  # noqa: F841
            _tensor_count = struct.unpack("<Q", f.read(8))[0]
            metadata_kv_count = struct.unpack("<Q", f.read(8))[0]

            for _ in range(metadata_kv_count):
                key = _read_gguf_string(f).encode()
                value_type = struct.unpack("<I", f.read(4))[0]
                value = _read_gguf_value(f, value_type)

                if key == _KEY_GENERAL_ARCHITECTURE:
                    meta["architecture"] = value
                elif key == _KEY_GENERAL_NAME:
                    meta["name"] = value
                elif value_type == 4 and key.endswith(_KEY_CONTEXT_LENGTH_SUFFIX):
                    meta["context_length"] = value
                elif value_type == 10 and key.endswith(_KEY_CONTEXT_LENGTH_SUFFIX):
                    meta["context_length"] = value

    except Exception as e:
        logger.warning(f"MetadataExtractor: Could not fully parse GGUF header for {filepath}: {e}")

    return meta


def _parse_filename_metadata(filename: str) -> dict:
    """
    Parse common naming conventions from a filename.
    Example: Meta-Llama-3-8B-Instruct.Q4_K_M.gguf
    """
    meta = {}
    stem = os.path.splitext(filename)[0]
    parts = stem.split(".")

    # Last part is often quantization (e.g., Q4_K_M)
    if len(parts) >= 2:
        quant_candidate = parts[-1].upper()
        known_quants = ["Q2_K", "Q3_K_S", "Q3_K_M", "Q3_K_L", "Q4_0", "Q4_K_S",
                        "Q4_K_M", "Q5_0", "Q5_K_S", "Q5_K_M", "Q6_K", "Q8_0",
                        "F16", "F32", "BF16", "IQ2_XS", "IQ3_M"]
        if any(q in quant_candidate for q in known_quants):
            meta["quantization"] = quant_candidate

    # Look for common parameter size patterns (7B, 13B, 8x7B, etc.)
    import re
    param_match = re.search(r"(\d+x\d+|\d+(\.\d+)?)[Bb]", stem)
    if param_match:
        meta["parameter_size"] = param_match.group(0).upper()

    # Attempt to infer family from beginning of stem
    stem_lower = stem.lower()
    for family in ["llama", "mistral", "mixtral", "phi", "gemma", "qwen", "deepseek",
                   "falcon", "mpt", "gpt2", "codellama", "vicuna", "wizard", "orca"]:
        if family in stem_lower:
            meta["family"] = family
            break

    return meta


def extract_metadata(filepath: str) -> ModelDescriptor:
    """
    Main entry point. Given a model file path, produce a fully populated
    ModelDescriptor, leaving unknown fields as "unknown" or defaults.
    """
    import uuid
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower().lstrip(".")

    # Determine format
    format_map = {
        "gguf": ModelFormat.GGUF,
        "ggml": ModelFormat.GGML,
        "safetensors": ModelFormat.SAFETENSORS,
        "onnx": ModelFormat.ONNX,
    }
    model_format = format_map.get(ext, ModelFormat.UNKNOWN)

    # Start with filename-based heuristics
    file_meta = _parse_filename_metadata(filename)

    # Augment with format-specific header parsing
    header_meta = {}
    if model_format == ModelFormat.GGUF:
        header_meta = _extract_gguf_metadata(filepath)

    # Merge: header > filename > defaults
    architecture = str(header_meta.get("architecture") or file_meta.get("family") or "unknown")
    family = str(file_meta.get("family") or architecture or "unknown")
    quantization = str(file_meta.get("quantization") or "unknown")
    parameter_size = str(file_meta.get("parameter_size") or "unknown")
    context_length = int(header_meta.get("context_length") or 4096)

    # Display name: prefer the GGUF name key, else clean up filename
    raw_name = str(header_meta.get("name") or os.path.splitext(filename)[0].replace("-", " ").replace("_", " ").title())

    caps = ModelCapabilities(
        context_length=context_length,
        supports_streaming=True,
        supports_system_prompts=True,
    )

    return ModelDescriptor(
        id=str(uuid.uuid4()),
        display_name=raw_name,
        path=filepath,
        format=model_format,
        family=family,
        quantization=quantization,
        parameter_size=parameter_size,
        architecture=architecture,
        size_bytes=os.path.getsize(filepath) if os.path.exists(filepath) else 0,
        capabilities=caps,
    )

#!/usr/bin/env python3
"""Encode, decode, and structurally validate DiamondFire code templates."""

from __future__ import annotations

import argparse
import base64
import binascii
import gzip
import json
import sys
from pathlib import Path
from typing import Any


KNOWN_BLOCKS = {
    "call_func",
    "control",
    "else",
    "entity_action",
    "entity_event",
    "event",
    "func",
    "game_action",
    "game_event",
    "if_entity",
    "if_game",
    "if_player",
    "if_var",
    "player_action",
    "process",
    "repeat",
    "select_obj",
    "set_var",
    "start_process",
}
DATA_BLOCKS = {"func", "call_func", "process", "start_process"}
KNOWN_ITEMS = {
    "bl_tag",
    "bucket_var",
    "comp",
    "g_val",
    "hint",
    "item",
    "loc",
    "num",
    "part",
    "pn_el",
    "pot",
    "snd",
    "txt",
    "var",
    "vec",
}
LEGACY_ITEMS = {"Bitem", "Bloc"}
VARIABLE_SCOPES = {"saved", "unsaved", "local", "line"}
TARGETS = {
    "",
    "AllPlayers",
    "Victim",
    "Shooter",
    "Damager",
    "Killer",
    "Default",
    "Selection",
    "Projectile",
    "LastEntity",
}


class TemplateError(Exception):
    """An expected input or file error."""


def _read_source(source: str | None) -> str:
    if source is None or source == "-":
        return sys.stdin.read()

    try:
        path = Path(source)
        if path.is_file():
            return path.read_text(encoding="utf-8")
    except OSError:
        # A long JSON/base64 positional argument may not be a valid filesystem path.
        pass
    return source


def _parse_json(text: str, description: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise TemplateError(f"{description} is not valid JSON: {exc}") from exc


def decode_template(encoded_input: str) -> Any:
    """Decode raw base64 or the code field from a template-item JSON object."""
    stripped = encoded_input.strip()
    if not stripped:
        raise TemplateError("Template input is empty")

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        encoded = stripped
    else:
        if isinstance(parsed, str):
            encoded = parsed
        elif isinstance(parsed, dict) and isinstance(parsed.get("code"), str):
            encoded = parsed["code"]
        else:
            raise TemplateError(
                "JSON template input must be a base64 string or an object with a code field"
            )

    encoded = "".join(encoded.split())
    try:
        compressed = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise TemplateError(f"Template code is not valid base64: {exc}") from exc
    try:
        decoded_bytes = gzip.decompress(compressed)
    except (OSError, EOFError) as exc:
        raise TemplateError(f"Template code is not valid gzip data: {exc}") from exc
    try:
        decoded_text = decoded_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TemplateError("Decoded template is not UTF-8 text") from exc
    return _parse_json(decoded_text, "Decoded template")


def encode_template(template: Any) -> str:
    """Serialize JSON compactly, gzip it deterministically, and return base64."""
    try:
        raw = json.dumps(
            template, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise TemplateError(f"Template cannot be serialized as JSON: {exc}") from exc
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    return base64.b64encode(compressed).decode("ascii")


def _issue(issues: list[dict[str, str]], path: str, message: str) -> None:
    issues.append({"path": path, "message": message})


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _require_object(
    value: Any, path: str, errors: list[dict[str, str]]
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        _issue(errors, path, "must be an object")
        return None
    return value


def _require_string_field(
    value: dict[str, Any], field: str, path: str, errors: list[dict[str, str]]
) -> None:
    if not isinstance(value.get(field), str):
        _issue(errors, f"{path}.{field}", "must be a string")


def _require_number_field(
    value: dict[str, Any], field: str, path: str, errors: list[dict[str, str]]
) -> None:
    if not _is_number(value.get(field)):
        _issue(errors, f"{path}.{field}", "must be a number")


def _validate_item(
    item: Any,
    path: str,
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    item_object = _require_object(item, path, errors)
    if item_object is None:
        return

    item_id = item_object.get("id")
    if not isinstance(item_id, str) or not item_id:
        _issue(errors, f"{path}.id", "must be a non-empty string")
        return
    if item_id in LEGACY_ITEMS:
        _issue(warnings, f"{path}.id", f"uses legacy item type {item_id!r}")
        return
    if item_id not in KNOWN_ITEMS:
        _issue(warnings, f"{path}.id", f"unknown item type {item_id!r}")
        return

    data = _require_object(item_object.get("data"), f"{path}.data", errors)
    if data is None:
        return

    if item_id in {"num", "txt", "comp"}:
        _require_string_field(data, "name", f"{path}.data", errors)
    elif item_id == "var":
        _require_string_field(data, "name", f"{path}.data", errors)
        if data.get("scope") not in VARIABLE_SCOPES:
            _issue(
                errors,
                f"{path}.data.scope",
                f"must be one of {sorted(VARIABLE_SCOPES)}",
            )
    elif item_id == "loc":
        if not isinstance(data.get("isBlock"), bool):
            _issue(errors, f"{path}.data.isBlock", "must be a boolean")
        location = _require_object(data.get("loc"), f"{path}.data.loc", errors)
        if location is not None:
            for field in ("x", "y", "z", "pitch", "yaw"):
                _require_number_field(location, field, f"{path}.data.loc", errors)
    elif item_id == "vec":
        for field in ("x", "y", "z"):
            _require_number_field(data, field, f"{path}.data", errors)
    elif item_id == "pot":
        _require_string_field(data, "pot", f"{path}.data", errors)
        _require_number_field(data, "dur", f"{path}.data", errors)
        _require_number_field(data, "amp", f"{path}.data", errors)
    elif item_id == "snd":
        _require_string_field(data, "sound", f"{path}.data", errors)
        _require_number_field(data, "pitch", f"{path}.data", errors)
        _require_number_field(data, "vol", f"{path}.data", errors)
        if "variant" in data and not isinstance(data["variant"], str):
            _issue(errors, f"{path}.data.variant", "must be a string")
    elif item_id == "g_val":
        _require_string_field(data, "type", f"{path}.data", errors)
        _require_string_field(data, "target", f"{path}.data", errors)
        if isinstance(data.get("target"), str) and data["target"] not in TARGETS:
            _issue(
                warnings,
                f"{path}.data.target",
                f"unknown target {data['target']!r}",
            )
    elif item_id == "part":
        _require_string_field(data, "particle", f"{path}.data", errors)
        cluster = _require_object(data.get("cluster"), f"{path}.data.cluster", errors)
        if cluster is not None:
            for field in ("amount", "horizontal", "vertical"):
                _require_number_field(cluster, field, f"{path}.data.cluster", errors)
        _require_object(data.get("data"), f"{path}.data.data", errors)
    elif item_id == "item":
        _require_string_field(data, "item", f"{path}.data", errors)
    elif item_id == "bl_tag":
        for field in ("option", "tag", "action", "block"):
            _require_string_field(data, field, f"{path}.data", errors)
        if "variable" in data:
            _validate_item(data["variable"], f"{path}.data.variable", errors, warnings)
    elif item_id == "bucket_var":
        for field in ("name", "key", "namespace_type", "namespace_alias"):
            _require_string_field(data, field, f"{path}.data", errors)
        if data.get("namespace_type") not in {"DEFAULT", "ALIAS"}:
            _issue(
                errors,
                f"{path}.data.namespace_type",
                "must be DEFAULT or ALIAS",
            )
    elif item_id == "hint":
        _require_string_field(data, "id", f"{path}.data", errors)
    elif item_id == "pn_el":
        _require_string_field(data, "name", f"{path}.data", errors)
        _require_string_field(data, "type", f"{path}.data", errors)
        for field in ("plural", "optional"):
            if field in data and not isinstance(data[field], bool):
                _issue(errors, f"{path}.data.{field}", "must be a boolean")
        if "default" in data:
            _validate_item(data["default"], f"{path}.data.default", errors, warnings)


def _validate_args(
    args: Any,
    path: str,
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> int:
    args_object = _require_object(args, path, errors)
    if args_object is None:
        return 0
    items = args_object.get("items")
    if not isinstance(items, list):
        _issue(errors, f"{path}.items", "must be an array")
        return 0

    seen_slots: set[int] = set()
    for index, argument in enumerate(items):
        argument_path = f"{path}.items[{index}]"
        argument_object = _require_object(argument, argument_path, errors)
        if argument_object is None:
            continue
        slot = argument_object.get("slot")
        if not isinstance(slot, int) or isinstance(slot, bool) or slot < 0:
            _issue(errors, f"{argument_path}.slot", "must be a non-negative integer")
        elif slot in seen_slots:
            _issue(errors, f"{argument_path}.slot", f"duplicates slot {slot}")
        else:
            seen_slots.add(slot)
        _validate_item(argument_object.get("item"), f"{argument_path}.item", errors, warnings)
    return len(items)


def validate_template(template: Any) -> dict[str, Any]:
    """Validate documented template structure while warning on future types."""
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    item_count = 0

    root = _require_object(template, "$", errors)
    if root is None:
        return {
            "valid": False,
            "summary": {"blockCount": 0, "itemCount": 0},
            "errors": errors,
            "warnings": warnings,
        }

    blocks = root.get("blocks")
    if not isinstance(blocks, list):
        _issue(errors, "$.blocks", "must be an array")
        blocks = []

    for index, block in enumerate(blocks):
        path = f"$.blocks[{index}]"
        block_object = _require_object(block, path, errors)
        if block_object is None:
            continue
        entry_id = block_object.get("id")
        if entry_id == "bracket":
            if block_object.get("direct") not in {"open", "close"}:
                _issue(errors, f"{path}.direct", "must be open or close")
            if block_object.get("type") not in {"norm", "repeat"}:
                _issue(errors, f"{path}.type", "must be norm or repeat")
            continue
        if entry_id != "block":
            _issue(errors, f"{path}.id", "must be block or bracket")
            continue

        block_type = block_object.get("block")
        if not isinstance(block_type, str) or not block_type:
            _issue(errors, f"{path}.block", "must be a non-empty string")
            continue
        if block_type not in KNOWN_BLOCKS:
            _issue(warnings, f"{path}.block", f"unknown block type {block_type!r}")
            if "args" in block_object:
                item_count += _validate_args(
                    block_object["args"], f"{path}.args", errors, warnings
                )
            continue
        if block_type == "else":
            continue
        if block_type in DATA_BLOCKS:
            _require_string_field(block_object, "data", path, errors)
        else:
            _require_string_field(block_object, "action", path, errors)

        item_count += _validate_args(
            block_object.get("args"), f"{path}.args", errors, warnings
        )
        if "attribute" in block_object and block_object["attribute"] not in {
            "",
            "LS-CANCEL",
            "NOT",
        }:
            _issue(
                errors,
                f"{path}.attribute",
                "must be an empty string, LS-CANCEL, or NOT",
            )
        if "attribute" not in block_object and "inverted" in block_object:
            _issue(warnings, f"{path}.inverted", "uses the legacy inverted field")
        if "target" in block_object:
            if not isinstance(block_object["target"], str):
                _issue(errors, f"{path}.target", "must be a string")
            elif block_object["target"] not in TARGETS:
                _issue(
                    warnings,
                    f"{path}.target",
                    f"unknown target {block_object['target']!r}",
                )
        if "subAction" in block_object and not isinstance(
            block_object["subAction"], str
        ):
            _issue(errors, f"{path}.subAction", "must be a string")

    return {
        "valid": not errors,
        "summary": {"blockCount": len(blocks), "itemCount": item_count},
        "errors": errors,
        "warnings": warnings,
    }


def _decoded_input(text: str) -> Any:
    """Accept decoded JSON, an encoded string, or a template-item wrapper."""
    stripped = text.strip()
    if not stripped:
        raise TemplateError("Template input is empty")
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return decode_template(stripped)

    if isinstance(parsed, dict) and "blocks" in parsed:
        return parsed
    if isinstance(parsed, (str, dict)):
        return decode_template(stripped)
    return parsed


def _write_output(text: str, output: Path | None) -> None:
    if output is None:
        print(text)
        return
    try:
        output.write_text(text + "\n", encoding="utf-8")
    except OSError as exc:
        raise TemplateError(f"Could not write {output}: {exc}") from exc


def _json_text(value: Any, compact: bool) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=None if compact else 2,
        separators=(",", ":") if compact else None,
    )


def _add_io_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "input",
        nargs="?",
        help="input file or literal value; omit or use - to read stdin",
    )
    parser.add_argument("--output", type=Path, help="write output to this file")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Encode, decode, and validate DiamondFire code templates."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    decode_parser = subparsers.add_parser(
        "decode", help="decode base64/gzip template code into JSON"
    )
    _add_io_arguments(decode_parser)
    decode_parser.add_argument(
        "--compact", action="store_true", help="emit single-line JSON"
    )

    encode_parser = subparsers.add_parser(
        "encode", help="encode decoded template JSON as base64/gzip"
    )
    _add_io_arguments(encode_parser)

    validate_parser = subparsers.add_parser(
        "validate", help="validate decoded or encoded template structure"
    )
    _add_io_arguments(validate_parser)
    validate_parser.add_argument(
        "--compact", action="store_true", help="emit single-line JSON"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text = _read_source(args.input)
        if args.command == "decode":
            output = _json_text(decode_template(text), args.compact)
            exit_code = 0
        elif args.command == "encode":
            output = encode_template(_parse_json(text, "Template input"))
            exit_code = 0
        else:
            result = validate_template(_decoded_input(text))
            output = _json_text(result, args.compact)
            exit_code = 0 if result["valid"] else 1
        _write_output(output, args.output)
        return exit_code
    except TemplateError as exc:
        print(
            json.dumps({"error": str(exc)}, ensure_ascii=False, separators=(",", ":")),
            file=sys.stderr,
        )
        return 2
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

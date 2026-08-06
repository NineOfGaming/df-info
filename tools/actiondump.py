#!/usr/bin/env python3
"""Query DiamondFire actiondump files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

DEFAULT_DUMP = (
    Path(__file__).resolve().parents[1]
    / "actiondump"
    / "actiondump_minimessage.json"
)

# Fields useful for identifying a record manually or from a code template. Query
# searches these by default; --all-fields also searches descriptions and metadata.
IDENTITY_FIELDS: dict[str, tuple[str, ...]] = {
    "codeblocks": ("name", "identifier", "item.name"),
    "actions": ("name", "codeblockName", "subAction", "aliases", "icon.name"),
    "gameValueCategories": ("identifier", "icon.name"),
    "gameValues": ("icon.name", "aliases", "category"),
    "particleCategories": ("identifier", "icon.name"),
    "particles": ("particle", "particleId", "icon.name", "category"),
    "soundCategories": ("identifier", "icon.name"),
    "sounds": ("sound", "soundId", "icon.name"),
    "potions": ("potion", "potionId", "icon.name"),
    "cosmetics": ("id", "name", "icon.name"),
    "shops": ("id", "name", "icon.name"),
}


class ActiondumpError(Exception):
    """An expected error suitable for structured CLI output."""

    def __init__(self, message: str, *, details: Any = None, exit_code: int = 2):
        super().__init__(message)
        self.details = details
        self.exit_code = exit_code


def load_actiondump(path: Path) -> dict[str, list[Any]]:
    """Load an actiondump and check the top-level shape used by this CLI."""
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise ActiondumpError(f"Actiondump file not found: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ActiondumpError(f"Could not read actiondump {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ActiondumpError("Actiondump root must be a JSON object")

    invalid = [name for name, records in data.items() if not isinstance(records, list)]
    if invalid:
        raise ActiondumpError(
            "Every actiondump collection must be an array",
            details={"invalidCollections": invalid},
        )
    return data


def _value_at_path(value: Any, dotted_path: str) -> Any:
    for component in dotted_path.split("."):
        if not isinstance(value, dict) or component not in value:
            return None
        value = value[component]
    return value


def _string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for child in value:
            yield from _string_values(child)


def _all_string_fields(value: Any, path: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            yield from _all_string_fields(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _all_string_fields(child, f"{path}[{index}]")


def _identity_fields(collection: str, record: Any) -> list[tuple[str, str]]:
    if not isinstance(record, dict):
        return []

    paths = IDENTITY_FIELDS.get(
        collection,
        ("id", "name", "identifier", "aliases", "icon.name"),
    )
    fields: list[tuple[str, str]] = []
    for path in paths:
        for value in _string_values(_value_at_path(record, path)):
            fields.append((path, value))
    return fields


def _identity_summary(collection: str, record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        return {"value": record}

    summary: dict[str, Any] = {}
    for path in IDENTITY_FIELDS.get(
        collection,
        ("id", "name", "identifier", "aliases", "icon.name"),
    ):
        value = _value_at_path(record, path)
        if value not in (None, "", []):
            summary[path] = value
    return summary


def _matches(candidate: str, needle: str, exact: bool) -> bool:
    candidate_folded = candidate.casefold()
    needle_folded = needle.casefold()
    return candidate_folded == needle_folded if exact else needle_folded in candidate_folded


def _match_score(candidate: str, needle: str) -> int:
    candidate_folded = candidate.casefold()
    needle_folded = needle.casefold()
    if candidate_folded == needle_folded:
        return 0
    if candidate_folded.startswith(needle_folded):
        return 1
    return 2


def _selected_collections(
    actiondump: dict[str, list[Any]], requested: list[str] | None
) -> list[str]:
    if not requested:
        return list(actiondump)

    unknown = [name for name in requested if name not in actiondump]
    if unknown:
        raise ActiondumpError(
            "Unknown actiondump collection",
            details={"unknown": unknown, "available": list(actiondump)},
        )
    # Keep the caller's order, but do not search a repeated collection twice.
    return list(dict.fromkeys(requested))


def query_actiondump(
    actiondump: dict[str, list[Any]],
    term: str,
    *,
    collections: list[str] | None = None,
    exact: bool = False,
    all_fields: bool = False,
    full: bool = False,
    limit: int = 20,
) -> dict[str, Any]:
    """Return compact, ranked matches from one or more collections."""
    if not term:
        raise ActiondumpError("Query must not be empty")

    selected = _selected_collections(actiondump, collections)
    ranked: list[tuple[int, int, int, dict[str, Any]]] = []

    for collection_order, collection in enumerate(selected):
        for index, record in enumerate(actiondump[collection]):
            fields = (
                list(_all_string_fields(record))
                if all_fields
                else _identity_fields(collection, record)
            )
            matching = [
                (path, value)
                for path, value in fields
                if _matches(value, term, exact)
            ]
            if not matching:
                continue

            result: dict[str, Any] = {
                "collection": collection,
                "index": index,
                "identity": _identity_summary(collection, record),
                "matchedFields": list(dict.fromkeys(path for path, _ in matching))[:20],
            }
            if full:
                result["record"] = record
            score = min(_match_score(value, term) for _, value in matching)
            ranked.append((score, collection_order, index, result))

    ranked.sort(key=lambda item: item[:3])
    total = len(ranked)
    matches = [item[3] for item in ranked[:limit]]
    return {
        "query": term,
        "match": "exact" if exact else "substring",
        "searchedCollections": selected,
        "total": total,
        "returned": len(matches),
        "truncated": total > len(matches),
        "matches": matches,
    }


def inspect_record(
    actiondump: dict[str, list[Any]],
    collection: str,
    *,
    key: str | None = None,
    index: int | None = None,
    codeblock: str | None = None,
) -> dict[str, Any]:
    """Return one complete record, selected by collection index or exact identity."""
    _selected_collections(actiondump, [collection])
    records = actiondump[collection]

    if (key is None) == (index is None):
        raise ActiondumpError("Provide exactly one of KEY or --index")

    if index is not None:
        if index < 0 or index >= len(records):
            raise ActiondumpError(
                f"Index {index} is outside collection {collection}",
                details={"minimum": 0, "maximum": len(records) - 1},
                exit_code=3,
            )
        matches = [(index, records[index])]
    else:
        assert key is not None
        matches = [
            (record_index, record)
            for record_index, record in enumerate(records)
            if any(
                _matches(value, key, exact=True)
                for _, value in _identity_fields(collection, record)
            )
        ]

    if codeblock is not None:
        matches = [
            (record_index, record)
            for record_index, record in matches
            if isinstance(record, dict)
            and isinstance(record.get("codeblockName"), str)
            and record["codeblockName"].casefold() == codeblock.casefold()
        ]

    if not matches:
        raise ActiondumpError(
            "No matching actiondump record",
            details={"collection": collection, "key": key, "codeblock": codeblock},
            exit_code=3,
        )
    if len(matches) > 1:
        candidates = [
            {
                "index": record_index,
                "identity": _identity_summary(collection, record),
            }
            for record_index, record in matches[:20]
        ]
        raise ActiondumpError(
            "More than one record matched; use --index or a more specific --codeblock",
            details={
                "collection": collection,
                "matchCount": len(matches),
                "candidates": candidates,
            },
            exit_code=3,
        )

    record_index, record = matches[0]
    return {"collection": collection, "index": record_index, "record": record}


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def _add_output_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--dump",
        type=Path,
        default=DEFAULT_DUMP,
        help=f"actiondump JSON file (default: {DEFAULT_DUMP})",
    )
    parser.add_argument(
        "--compact", action="store_true", help="emit single-line JSON"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Query and inspect DiamondFire actiondump JSON files."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    collections_parser = subparsers.add_parser(
        "collections", help="list available collections and record counts"
    )
    _add_output_arguments(collections_parser)

    query_parser = subparsers.add_parser(
        "query", help="search record names, IDs, aliases, and display names"
    )
    query_parser.add_argument("term", help="case-insensitive search term")
    query_parser.add_argument(
        "--collection",
        dest="collections",
        action="append",
        help="collection to search; repeat to select more than one",
    )
    query_parser.add_argument(
        "--exact", action="store_true", help="require a complete field match"
    )
    query_parser.add_argument(
        "--all-fields",
        action="store_true",
        help="also search descriptions and nested metadata",
    )
    query_parser.add_argument(
        "--full", action="store_true", help="include complete records in results"
    )
    query_parser.add_argument(
        "--limit", type=_positive_int, default=20, help="maximum returned matches"
    )
    _add_output_arguments(query_parser)

    inspect_parser = subparsers.add_parser(
        "inspect", help="return one complete record by exact identity or index"
    )
    inspect_parser.add_argument("collection", help="collection containing the record")
    inspect_parser.add_argument(
        "key", nargs="?", help="exact name, ID, alias, or display name"
    )
    inspect_parser.add_argument("--index", type=int, help="zero-based collection index")
    inspect_parser.add_argument(
        "--codeblock",
        help="filter duplicate actions by codeblockName (for example PLAYER ACTION)",
    )
    _add_output_arguments(inspect_parser)
    return parser


def _emit(value: Any, *, compact: bool, stream: Any = sys.stdout) -> None:
    indent = None if compact else 2
    separators = (",", ":") if compact else None
    print(
        json.dumps(value, ensure_ascii=False, indent=indent, separators=separators),
        file=stream,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        actiondump = load_actiondump(args.dump)
        if args.command == "collections":
            output = {
                "file": str(args.dump),
                "collections": [
                    {"name": name, "count": len(records)}
                    for name, records in actiondump.items()
                ],
            }
        elif args.command == "query":
            output = query_actiondump(
                actiondump,
                args.term,
                collections=args.collections,
                exact=args.exact,
                all_fields=args.all_fields,
                full=args.full,
                limit=args.limit,
            )
        else:
            output = inspect_record(
                actiondump,
                args.collection,
                key=args.key,
                index=args.index,
                codeblock=args.codeblock,
            )
        _emit(output, compact=args.compact)
        return 0
    except ActiondumpError as exc:
        error: dict[str, Any] = {"error": str(exc)}
        if exc.details is not None:
            error["details"] = exc.details
        _emit(error, compact=True, stream=sys.stderr)
        return exc.exit_code
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

# df-info

This repository collects reference information and exported metadata for
[DiamondFire](https://mcdiamondfire.com/).

> [!IMPORTANT]
> **This branch archives DiamondFire 8.12 and is not the current documentation.**  
> Use the repository's [default branch](https://github.com/NineOfGaming/df-info) for information about the current DiamondFire patch.
>
> This branch preserves the information recorded while 8.12 was current.  
> Newly discovered or previously undocumented details are not added retroactively, even when they describe behavior that already existed in 8.12.  
> Changes introduced in later DiamondFire patches are likewise not added here.

## Repository contents

- [`actiondump/`](actiondump/) contains the DiamondFire actiondump as JSON.  
  The four files contain the same data, but use plain text, ampersand codes,  
  MiniMessage tags, or section-sign codes for formatted text.  
  See the [actiondump guide](docs/actiondump/actiondump.md) for the data structure and  
  details about each variant.
- [`docs/actiondump/`](docs/actiondump/) documents actiondump entries such as  
  actions, codeblocks, icons, arguments, and return values.
- [`docs/templates/`](docs/templates/) explains DiamondFire code-template  
  encoding and the decoded block and item formats.
- [`docs/useful-info/`](docs/useful-info/) contains practical notes about  
  variables, selections, percent expressions, limits, entity references, and coding  
  quirks.

## Command-line tools

The [`tools/`](tools/) directory includes Python scripts for exploring the actiondump and working with code templates.  
They have no third-party dependencies; Python 3.10 or newer is recommended.

### Search the actiondump:

```sh
python tools/actiondump.py collections
python tools/actiondump.py query Teleport --collection actions
python tools/actiondump.py inspect actions Teleport --codeblock "PLAYER ACTION"
python tools/actiondump.py query "Movement Key Change" --collection actions --inspect
```

Queries search names, IDs, aliases, and display names by default.  
Add `--all-fields` to include descriptions and nested metadata,  
`--full` to include complete matching records, or `--compact` for single-line JSON.  
Add `--inspect` to return the complete record directly when exactly one query result matches.  
The `inspect` command always returns a complete record and accepts `--full` as an optional no-op for consistency.  
It also accepts the collection index returned by a query, for example `inspect actions --index 1070`.

The MiniMessage actiondump is used by default.  
Pass `--dump` to any subcommand to select another file, for example:

```sh
python tools/actiondump.py query Teleport --dump actiondump/actiondump_plain.json
```

### Decode, validate, and re-encode code templates:

```sh
python tools/template.py decode encoded-template.txt --output template.json
python tools/template.py validate template.json
python tools/template.py encode template.json --output encoded-template.txt
```

Template commands accept a filename, a literal value,  
or standard input when the input is omitted or `-` is used.  
`decode` and `validate` also accept a full template-item object  
containing `author`, `name`, `version`, and `code`.

# Actiondump

The actiondump is a JSON collection of metadata exported from DiamondFire.  
It describes codeblocks, actions, game values, particles, sounds, potions, cosmetics, and shops.

## Files in this repository

Each file contains the same top-level data.  
Only the representation of formatted text differs.

| File | Text formatting |
| --- | --- |
| [`actiondump_plain.json`](../../actiondump/actiondump_plain.json) | Formatting removed |
| [`actiondump_ampersand.json`](../../actiondump/actiondump_ampersand.json) | Ampersand (`&`) codes |
| [`actiondump_minimessage.json`](../../actiondump/actiondump_minimessage.json) | MiniMessage tags |
| [`actiondump_section.json`](../../actiondump/actiondump_section.json) | Section-sign (`§`) codes |

## Getting an actiondump

### Help Bot

In the DiamondFire Discord, go to [`#bot-cmds`](https://discord.com/channels/180793115223916544/423321409918599169) and run `?actiondump`.  
Check the footer of `?info`, because the bot's copy may be older than DiamondFire's current data.

### Manually

Development-like nodes may expose the hidden command:

```text
/dumpactioninfo [-c]
```

The `-c` flag emits colors as ampersand codes.  
While the dump is being sent, other server communication can pause and the client may disconnect.  
The messages can be copied from the client log and their chat prefixes removed.

### Mods

Mods such as [Flint](https://modrinth.com/mod/flint) or [CodeClient](https://modrinth.com/mod/codeclient) can also export actiondump data.  
Each mod provides its own command or workflow for creating the export.

The actiondump files in this repository were exported using Flint.

## Versions

The `versions` object describes the DiamondFire patch, the current code-item versions, and the current Minecraft-ID mappings:

```ts
{
  patch: string;
  particle_mapping: number;
  potion_mapping: number;
  sound_mapping: number;
  bucket_var: number;
  var: number;
  num: number;
  txt: number;
  comp: number;
  loc: number;
  r_loc: number;
  vec: number;
  part: number;
  snd: number;
  pot: number;
  item: number;
  g_val: number;
  bl_tag: number;
  pn_el: number;
  hint: number;
}
```

- `patch` is the DiamondFire patch associated with the dump.
- `particle_mapping`, `potion_mapping`, and `sound_mapping` identify the current mappings for Minecraft IDs. Code items store the applicable value in their `data.mappingVersion` field so renamed IDs can be migrated.
- The remaining keys are code-item IDs. Their values are the current format version for that item type. See [Items and arguments](../templates/items.md#item) for the serialized item format.

In the current format, `part`, `snd`, and `pot` are version `1`; the other listed item types are version `0`.

## Top-level data

Besides `versions`, an actiondump contains these arrays:

| Collection | Contents |
| --- | --- |
| `codeblocks` | Codeblock display names, template identifiers, and [icons](icons.md) |
| `actions` | [Actions](actions.md), tags, aliases, argument metadata, and return metadata |
| `gameValueCategories` | Game-value category identifiers, menu slots, and icons |
| `gameValues` | Game-value aliases, categories, icons, and return metadata |
| `particleCategories` | Particle category identifiers, menu slots, and icons |
| `particles` | Particle names, IDs, categories, editable fields, and icons |
| `soundCategories` | Sound category identifiers, subcategory flags, and icons |
| `sounds` | Sound names, IDs, variants, and icons |
| `potions` | Potion names, IDs, and icons |
| `cosmetics` | Cosmetic IDs, names, categories, and icons |
| `shops` | Shop layouts and purchasable-item metadata |

See [Codeblocks](codeblocks.md) for the mapping represented by the `codeblocks` collection.

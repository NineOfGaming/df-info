# Items and arguments

Items supplied to a codeblock are stored in its `args` field:

```ts
{
  items: Argument[];
}
```

An argument associates an item with its chest slot.  
Array order is not significant.

```ts
{
  item: Item;
  slot: number;
}
```

## Item

Each item contains its format version, a type identifier, and type-specific data:

```ts
{
  version: number;
  id:
    | "bl_tag"
    | "bucket_var"
    | "comp"
    | "g_val"
    | "hint"
    | "item"
    | "loc"
    | "num"
    | "part"
    | "pn_el"
    | "pot"
    | "snd"
    | "txt"
    | "var"
    | "vec";
  data: unknown;
}
```

The version is specific to the item type rather than to the template as a whole.  
When `version` is omitted, DiamondFire treats the item as version `0`.  
Currently, sounds, potions, and particles use version `1`; the other documented item types use version `0`.  
New versions can change the meaning or structure of one item type without changing the others.  
The actiondump's [`versions` object](../actiondump/actiondump.md#versions) records the current version of each type.

Some older templates may use legacy identifiers such as `Bitem` and `Bloc`.

## Named values

Numbers, Strings, and Text values share a `name` field.  
Numbers use a string because they can include percent expressions.

```ts
{
  version: 0;
  id: "num" | "txt" | "comp";
  data: {
    name: string;
  };
}
```

### Styled text

`comp` is DiamondFire's Styled Text value.  
Its `name` is formatted using [MiniMessage](https://docs.papermc.io/adventure/minimessage/format/).  
`txt` is an ordinary String value and does not use MiniMessage.  

### Variables

```ts
{
  version: 0;
  id: "var";
  data: {
    name: string;
    scope: "saved" | "unsaved" | "local" | "line";
  };
}
```

`unsaved` is the in-game `GAME` scope.

### Parameters

`pn_el` is short for pattern element.  
Each entry corresponds to a parameter shown in an action's chest.

```ts
{
  version: 0;
  id: "pn_el";
  data: {
    name: string;
    type:
      | "txt"
      | "comp"
      | "num"
      | "loc"
      | "vec"
      | "snd"
      | "part"
      | "pot"
      | "item"
      | "any"
      | "var"
      | "list"
      | "dict";
    plural?: boolean;
    optional?: boolean;
    note?: string;
    description?: string;
    default?: Item;
  };
}
```

A `var` parameter cannot be plural.  
Parameters with default values are not plural.  
Defaults must match the selected type and have historically not been available for `var`, `list`, or `dict`.

## Location

```ts
{
  version: 0;
  id: "loc";
  data: {
    isBlock: boolean;
    loc: {
      x: number;
      y: number;
      z: number;
      pitch: number;
      yaw: number;
    };
  };
}
```

When `isBlock` is true, pitch and yaw are hidden.  
`isBlock` exists for legacy support.

## Vector

```ts
{
  version: 0;
  id: "vec";
  data: {
    x: number;
    y: number;
    z: number;
  };
}
```

## Potion

```ts
{
  version: 1;
  id: "pot";
  data: {
    mappingVersion: number;
    pot: string;
    dur: number;
    amp: number;
  };
}
```

In version `1`, `pot` is the namespaced Minecraft potion ID, such as `minecraft:speed`.  
Version `0` potion items used DiamondFire's display name instead.

`dur` is measured in ticks.  
`amp` is the effect strength and is normally limited to the range -255 through 255.  
Durations of `1,000,000` ticks or greater are displayed in-game as `Infinite`.

## Sound

```ts
{
  version: 1;
  id: "snd";
  data: {
    mappingVersion: number;
    sound: string;
    pitch: number;
    vol: number;
    variant?: string;
  };
}
```

In version `1`, `sound` is the namespaced Minecraft sound ID, such as `minecraft:block.note_block.pling`.  
Version `0` sound items used DiamondFire's display name instead.

`pitch` is normally in the range 0 through 2.  
During playback, Minecraft treats values below 0.5 as 0.5, so lower values do not reduce the pitch further.

When a specific sound variant is selected, `variant` contains its ID from the actiondump sound's `variants` array.

## Game value

```ts
{
  version: 0;
  id: "g_val";
  data: {
    type: string;
    target:
      | "Selection"
      | "Default"
      | "Victim"
      | "Killer"
      | "Damager"
      | "Shooter"
      | "Projectile"
      | "LastEntity";
  };
}
```

The target is hidden and has no effect for plot or event values.

## Particle

Particle types expose different optional fields inside `data.data`:

```ts
{
  version: 1;
  id: "part";
  data: {
    mappingVersion: number;
    particle: string;
    cluster: {
      amount: number;
      horizontal: number;
      vertical: number;
    };
    data: {
      motionVariation?: number;
      x?: number;
      y?: number;
      z?: number;
      colorVariation?: number;
      rgb?: number;
      sizeVariation?: number;
      size?: number;
      material?: string;
    };
  };
}
```

In version `1`, `particle` is the namespaced Minecraft particle ID, such as `minecraft:cloud`.  
Version `0` particle items used DiamondFire's display name instead.

For sounds, potions, and particles, `mappingVersion` identifies the Minecraft-ID mapping used when the item was created.  
DiamondFire can use it to migrate IDs that Minecraft renames; the actiondump publishes the current [`sound_mapping`, `potion_mapping`, and `particle_mapping`](../actiondump/actiondump.md#versions) values.

`rgb` is a base-10 integer representation of a hexadecimal RGB color.

## Minecraft item

```ts
{
  version: 0;
  id: "item";
  data: {
    item: string;
  };
}
```

`item` contains Minecraft NBT serialized as a string. NBT is not JSON.

## Block tag

Block tags occupy slots at the bottom right side of an action chest:

```ts
{
  version: 0;
  id: "bl_tag";
  data: {
    option: string;
    tag: string;
    action: string;
    block:
      | "call_func"
      | "control"
      | "else"
      | "entity_action"
      | "entity_event"
      | "event"
      | "func"
      | "game_action"
      | "game_event"
      | "if_entity"
      | "if_game"
      | "if_player"
      | "if_var"
      | "player_action"
      | "process"
      | "repeat"
      | "select_obj"
      | "set_var"
      | "start_process";
    variable?: {
      version: 0;
      id: "var";
      data: {
        name: string;
        scope: "saved" | "unsaved" | "local" | "line";
      };
    };
  };
}
```

When `variable` is present, the tag selects its option at runtime using that variable's value.  
The value is matched case-insensitively against the tag's option names.  
If no option matches, the tag uses its [default option](../actiondump/actions.md#tags).

The serialized `block` field can use identifiers for blocks that do not expose an action chest, including events and Else.  
Their presence in the format does not mean those blocks expose usable block tags in-game.

## Bucket variables

Bucket-variable items identify an individual variable inside a bucket and namespace:

```ts
{
  version: 0;
  id: "bucket_var";
  data: {
    name: string;
    key: string;
    namespace_type: "DEFAULT" | "ALIAS";
    namespace_alias: string;
  };
}
```

- `name` is the bucket variable's name.
- `key` is the key of the bucket containing the variable.
- `namespace_type` selects either the default namespace or a namespace alias.
- `namespace_alias` contains the alias when `namespace_type` is `ALIAS`; it is an empty string when `namespace_type` is `DEFAULT`.

## Hint

```ts
{
  version: 0;
  id: "hint";
  data: {
    id: "function";
  };
}
```

Other values can be selected but produce an error.

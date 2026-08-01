# Icons

Icons provide a shared representation for actions, menu entries, and inventory items.  
Not every field is meaningful in every context, and some icon types add specialized fields.

```ts
{
  material: string;
  name: string;
  deprecatedNote: string[];
  description: string[];
  example: string[];
  worksWith: string[];
  additionalInfo: string[][];
  requiredRank: string;
  requireTokens: boolean;
  requireSparks: boolean;
  requireRankAndTokens: boolean;
  advanced: boolean;
  worldExclusive: boolean;
  loadedItem: string;

  color?: {
    red: number;
    green: number;
    blue: number;
  };
  head?: string;
  cancellable?: boolean;
  cancelledAutomatically?: boolean;
  tags?: number;
  arguments?: (ArgumentMetadata | { text: string })[];
  returnValues?: (ReturnMetadata | { text: string })[];
  returnType?: string;
  returnDescription?: string[];
}
```

- `material` is an uppercase Minecraft material name without the `minecraft:` namespace, such as `STONE`.
- `loadedItem` is the material loaded into a crossbow, using the same material naming scheme.
- `head` contains base64-encoded player-head texture data.
- `cancellable` and `cancelledAutomatically` describe event cancellation behavior.
- `tags` is the number of block tags exposed by an action.
- `arguments` and `returnValues` are primarily present on action icons.
- `returnType` and `returnDescription` describe the value produced by a game value.

## Arguments

Argument metadata describes the values accepted by an action:

```ts
type ArgumentMetadata = {
  type: string;
  plural: boolean;
  optional: boolean;
  description: string[];
  notes: string[][];
};
```

Some actions include separator entries such as `{ text: "OR" }` in their argument arrays.

Each inner `notes` array contains the lines of one note.  
`additionalInfo` uses the same nested line-group structure.

## Return values

Return-value metadata describes values produced by an action:

```ts
type ReturnMetadata = {
  type: string;
  description: string[];
};
```

Return-value arrays can also contain separator entries such as `{ text: "OR" }`.

# Codeblocks

The `codeblocks` collection maps each codeblock's top-line display name to the identifier used inside code templates.

```ts
{
  name: string;       // For example: "PLAYER EVENT"
  identifier: string; // For example: "event"
  item: Icon;
}
```

`item` contains the [icon metadata](icons.md) for the block placed from the player's inventory.

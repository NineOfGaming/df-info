# Actions

Actions describe the operations available on DiamondFire codeblocks.  
Legacy actions remain in the dump for compatibility and may have little or no display metadata.

## Action

An action has the following general shape:

```ts
{
  name: string;
  codeblockName: string;
  tags: Tag[];
  aliases: string[];
  subAction: string;
  icon: Icon;
  legacyReplacement?: {
    text: string[];
    action: string;
  };
  subActionBlocks?: (
    | "if_player"
    | "if_entity"
    | "if_game"
    | "if_var"
  )[];
}
```

- `name` is the action's internal name.
- `codeblockName` is the top-line display name, such as `PLAYER ACTION`; it is not the internal codeblock identifier.
- `aliases` contains alternate names, primarily for search and help tools.
- `subAction` identifies the condition used by sub-action blocks when applicable.
- `legacyReplacement` points to the action that replaces a legacy action.
- `subActionBlocks` lists the condition-block types accepted by actions such as repeat-while and conditional selection.

`if_game` and `if_var` conditions are generally available wherever a sub-action condition is accepted.  
Entity filters cannot use `if_player`, while player filters cannot use `if_entity`; repeat-while conditions can use both.

## Tags

Tags represent the block-tag items at the right side of an action chest:

```ts
{
  name: string;
  options: Option[];
  defaultOption: string;
  slot: number;
}
```

### Option

```ts
{
  name: string;
  icon: Icon;
  aliases: string[];
}
```

`defaultOption` is the name of the option selected by default, and `slot` is the chest slot occupied by the tag.

## Arguments

Action argument metadata is stored in the action's [icon](icons.md#arguments).  
The actual values supplied to a codeblock are documented under [Items and arguments](../templates/items.md).

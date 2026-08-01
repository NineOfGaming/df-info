# Blocks

Every entry in a decoded template's `blocks` array is either a codeblock or a bracket:

```ts
{
  id: "block" | "bracket";
}
```

Each kind adds its own fields.

## Brackets

```ts
{
  id: "bracket";
  direct: "open" | "close";
  type: "norm" | "repeat";
}
```

- `direct` determines whether the piston faces right (`open`) or left (`close`).
- `type` determines whether the bracket is normal or sticky.

## Codeblocks

All codeblocks begin with:

```ts
{
  id: "block";
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
}
```

Values DiamondFire does not validate may be imported even when they would be impossible to enter in-game.  
Such strings can contain section-sign (`§`) color codes.

### Else

Else blocks contain no dynamic values:

```ts
{
  id: "block";
  block: "else";
}
```

### Action blocks

Blocks that execute an action have the following common shape:

```ts
{
  id: "block";
  block: string;
  action: string;
  attribute: "" | "LS-CANCEL" | "NOT";
  args: Args;
}
```

- `action` is the action's internal name. DiamondFire may not validate this value when importing.
- `attribute` stores either condition inversion (`NOT`) or an event's automatic cancellation state (`LS-CANCEL`).
- `args` contains the block's [argument items](items.md).

Older templates may use an `inverted` field. `attribute` supersedes it.

#### Selection blocks

Selection-style blocks also store a target:

```ts
{
  id: "block";
  block:
    | "event"
    | "player_action"
    | "entity_event"
    | "entity_action"
    | "set_var"
    | "game_action"
    | "repeat"
    | "control"
    | "select_obj";
  action: string;
  target:
    | ""
    | "AllPlayers"
    | "Victim"
    | "Shooter"
    | "Damager"
    | "Killer"
    | "Default"
    | "Selection"
    | "Projectile"
    | "LastEntity";
  attribute: "" | "LS-CANCEL" | "NOT";
  args: Args;
}
```

Not every block in this group exposes target selection or inversion in-game.

#### Sub-action blocks

Conditional selection blocks and repeat-while blocks can store a condition in `subAction`:

```ts
{
  id: "block";
  block: "if_entity" | "if_game" | "if_player" | "if_var";
  action: string;
  subAction: string;
  attribute: "" | "LS-CANCEL" | "NOT";
  args: Args;
}
```

When condition types clash, `if_player` has been observed to take priority.

### Data blocks

Function and process blocks store the user-entered function or process name in `data`:

```ts
{
  id: "block";
  block: "func" | "call_func" | "process" | "start_process";
  data: string;
  args: Args;
}
```

The `data` field can contain color codes, unusually long strings, and characters that cannot normally be entered through the in-game interface.

Call Function and Start Process names can contain [percent codes](../useful-info/percent-codes.md#dynamic-function-and-process-names) that resolve the target code line at runtime.

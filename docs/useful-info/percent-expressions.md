# Percent expressions 

Percent expressions are placeholders that DiamondFire evaluates while code is running.  
They can retrieve values, perform small calculations, or insert a target from the current code context.

There are two common forms:

- Expressions use arguments inside parentheses, such as `%var(score)` or `%math(2+3)`.
- Target expressions have no arguments, such as `%default` or `%victim`.

Percent expressions can be nested inside one another.

## Expressions

| Expression | Result |
| --- | --- |
| `%random(min,max)` | A random integer between `min` and `max` |
| `%round(number)` | `number` rounded down to an integer |
| `%index(list,index)` | The value at `index` in `list` |
| `%entry(dictionary,key)` | The value stored at `key` in `dictionary` |
| `%var(variable)` | The value of the variable with the given name |
| `%math(expression)` | The result of a mathematical expression |

DiamondFire lists are 1-indexed, so the first value is at index `1`.

`%math` does not use the usual mathematical order of operations.  
For example, `%math(1+5*3)` evaluates to `18`, not `16`, because the operations are applied from left to right.  

Use a nested `%math` expression when part of the calculation must be evaluated first:

```text
%math(1+%math(5*3))
```

The inner expression produces `15`, so the outer expression produces `16`.  
Normal grouping parentheses do not work, so `%math(1+(5*3))` is invalid.

`%math` is supported by Number values.  
Other percent expressions can be nested inside it when they resolve to numbers:

```text
%math(%var(score)+5)
```

## Target expressions

Target expressions depend on the current event, target, or selection:

| Expressions | Result |
| --- | --- |
| `%default` | The name of the Default player or entity |
| `%defaultuuid` | The UUID of the Default player or entity |
| `%selected` | The target currently being processed, or the Default target when no selection is active |
| `%uuid` | The UUID of the target currently being processed, or the Default target when no selection is active |
| `%damager` | The damager in a damage event |
| `%damageruuid` | The UUID of the damager in a damage event |
| `%killer` | The killer in a death event |
| `%killeruuid` | The UUID of the killer in a death event |
| `%victim` | The victim in a damage, death, or applicable click event |
| `%victimuuid` | The UUID of the victim in a damage, death, or applicable click event |
| `%shooter` | The shooter in a projectile event |
| `%shooteruuid` | The UUID of the shooter in a projectile event |
| `%projectile` | The projectile in a projectile event |
| `%projectileuuid` | The UUID of the projectile in a projectile event |

Event-specific expressions only work when that target exists.  
Expressions that require Default may also fail or produce an unexpected result in a [selectionless thread](selections.md#selection-states).

`%default` and `%defaultuuid` always refer to Default.  
`%selected` and `%uuid` instead follow selection-based execution, resolving the current target's name and UUID respectively, and fall back to Default when no selection is active.

## Nesting

DiamondFire resolves nested percent expressions as part of the surrounding expression.

For example, a list and its index can both come from variables:

```text
%index(%var(rewards),%var(level))
```

A dictionary entry can be retrieved in the same way:

```text
%entry(%var(profile),rank)
```

Keep deeply nested expressions readable.  
An intermediate variable is usually better when the expression is difficult to inspect or reuse.

## Dynamic variable names

Percent expressions can appear inside variable names:

```text
%default.opponent
```

The name is evaluated when the variable is used, allowing one placed variable item to address different data for different players.

`%var` can also read a dynamically named variable:

```text
%var(%default.opponent).health
```

Use a UUID expression rather than a name expression for persistent player data because usernames can change.

## Dynamic function and process names

Both Call Function and Start Process accept percent expressions in their names.  
DiamondFire evaluates the name when the block runs, then calls the function or process whose name matches the result.

This allows one placed block to choose between multiple code lines without a separate call block for every possible name.

For example:

```text
Function weapon.bow
Function weapon.sword

Set weapon_type = bow
Call Function weapon.%var(weapon_type)
```

The expression resolves the call name to `weapon.bow`.  
If `weapon_type` contains `sword` instead, the same block calls `weapon.sword`.

Start Process resolves names in the same way:

```text
Process match.lobby
Process match.playing

Start Process match.%var(match_state)
```

The resolved name must exactly match an existing function or process.  
Functions reached through one dynamic Call Function block should also use compatible parameters because of its [signature-caching behavior](code-practices-and-quirks.md#dynamic-function-call-signatures).

## Where percent expressions are evaluated

Percent expressions are commonly used in String and Text values, Number expressions, variable names, and dynamic function or process names.  
The exact behavior depends on the value type and the action consuming it; not every text-bearing field evaluates percent expressions.

Percent expressions are separate from MiniMessage formatting.  
MiniMessage controls presentation, while percent expressions insert or calculate values.  

Percent expressions cannot be used directly inside a [Styled Text value's MiniMessage tags](../templates/items.md#styled-text).  
For example, a percent expression cannot dynamically provide a tag name or argument.

To generate dynamic MiniMessage tags, put the MiniMessage expression in a String so its percent expressions can be evaluated, then convert it with Set Variable: Parse MiniMessage Expression:

```text
<color:%var(color)>Hello</color>
```

# Variables and values

## Choose the narrowest useful scope

Variable scope controls lifetime and visibility:

| Scope | Lifetime and visibility | Common use |
| --- | --- | --- |
| Game | Shared plot state; cleared after everyone leaves | Active matches, caches, temporary player state |
| Save | Persistent across sessions | Progress, settings, long-term player data |
| Local | Limited to one event thread and shared with called functions | Temporary calculations used across a call chain |
| Line | Limited to the current code line or function invocation | Scratch values and function parameters |

Line variables do not cross a function boundary, which makes them safer for temporary names reused by multiple functions.  
See [Functions and processes](code-practices-and-quirks.md#functions-and-processes) for Local-variable inheritance when starting a process.

Game and Save variables share a namespace.  
If a Save variable already exists, attempting to set a Game variable with the same name can modify the persistent value instead, so avoid ambiguous names across these two scopes.

## Purge temporary player state

Game variables containing player-specific runtime state should be removed when the player leaves the plot.

Without cleanup, stale values can leak into later sessions, consume the variable limit, and make certain behavior inconsistent.

## Build names from stored identifiers

If code only needs an identifier, building a variable name from stored data is often safer than changing the selection.

For example, a duel system could store an opponent:

```text
%default.opponent
```

The stored identifier can then be used in another variable name:

```text
%var(%default.opponent).health
```

Use a stable identifier for persistent data.  
UUIDs are generally safer than usernames because usernames can change.

## Use percent codes for simple intermediate values

Percent codes such as `%math`, `%index`, `%entry`, and `%var` can replace Set Variable actions whose only purpose is to calculate or retrieve a value used once.

This can reduce code size and unnecessary actions, but compactness is not the only goal.  
Use an intermediate variable when it makes a complicated expression easier to inspect, reuse, or debug.

Avoiding an extra Set Variable block also avoids parsing and executing that block and its arguments, slightly reducing CPU overhead.  
The difference is usually minimal, so readability should remain the deciding factor.

See [Percent codes and expressions](percent-codes.md) for syntax, built-in expressions, target codes, and nesting.

## Number precision

DiamondFire numbers use signed 64-bit fixed-point storage with three decimal places.  
Values are rounded to increments of `0.001`, and the approximate representable range is:

```text
-9,223,372,036,854,775.808
to
 9,223,372,036,854,775.807
```

Repeated calculations can accumulate rounding error, especially when they use very small changes.

When additional decimal precision is required, store a scaled integer and divide only when presenting or consuming the result:

```text
1.23456 → store 123456 with a scale of 100000
```

Keep the scale consistent throughout the system.  
Vectors use a different numeric representation and can be useful when calculations naturally fit vector operations, but they should not be used merely to disguise ordinary number logic.

## Save variables versus bucket variables

Use ordinary Save variables when the data comfortably fits on one plot and does not need cross-plot access.  
Bucket variables are intended for larger persistent storage or data shared between plots.

Bucket variables require an explicit lifecycle:

1. Load or create the bucket.
2. Read and modify its variables.
3. Save periodically when data must survive a failure.
4. Save and unload when the data is no longer in use.

A loaded bucket is locked, preventing another plot from loading it at the same time.  
Operations can also fail or be throttled, so use their result variables and retry recoverable failures after a delay rather than placing load/save operations in fast loops.

Per-player storage commonly uses one bucket key per UUID.  
Ensure quit handling and cleanup logic unload buckets even when a player leaves during unusual plot states.

See [DiamondFire limits](limits.md#bucket-variable-limits) for bucket quotas and the approximate operation rate.  
See [Items and arguments](../templates/items.md#bucket-variables) for the template representation of a bucket-variable item.

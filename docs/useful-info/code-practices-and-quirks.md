# Code practices and quirks

## Abstract repeated behavior, not every detail

Functions and data structures can replace duplicated code and make a system easier to update.  
For example, checking a mined block against one editable list is usually easier to maintain than creating a separate condition for every permitted block.

Abstraction has a cost: more indirection, setup, and state to understand.  
Do not turn a small fixed system into a complex data-driven framework unless it improves maintainability, reuse, or performance in practice.

A useful test is whether a future change can be made in one obvious place without making the current code harder to follow.

## Functions and processes

A function pauses its caller, runs on the same thread, and returns when it finishes.  
A process starts separate execution while the original line continues.

Use a function when:

- the caller needs the result before continuing;
- the work belongs to the same logical operation;
- Local variables should naturally remain in the same call chain.

Use a process when:

- work should continue independently or in parallel;
- waits should not pause the original line;
- the new thread needs different selection or Local-variable behavior.

Start Process can omit, copy, or share the caller's Local variables.  
Its [target mode](selections.md#start-process-target-modes) separately controls how the new thread receives selections and event targets.

Copying Local variables creates an independent snapshot.  
Sharing them allows changes in the process to affect the caller's Local variables, which is powerful but can make concurrent code difficult to reason about.

## Sticky multi-type parameters

Some action parameters accept more than one value type.  
The first type used by a particular placed codeblock during a plot session can become fixed for that block, causing later executions with another accepted type to fail until the plot restarts.

If a block may receive several types, normalize the input to one type or use separate placed blocks for each type.

## Dynamic function-call signatures

A Call Function block whose name contains [percent expressions](percent-expressions.md#dynamic-function-and-process-names) can call different functions dynamically.  
The placed call block can remember the parameter signature of the first function it calls during a session, including parameter names, and reuse that signature for later calls.

All functions reachable from one dynamic Call Function block should therefore use compatible parameters.  
If their signatures differ, use separate call blocks or a wrapper function with one stable interface.

## Player death and respawn quirks

Player death events are usually adequate for simple games, but the normal death and respawn sequence can reset or invalidate more player and plot state than expected.  
Complex games should not assume that state survives this sequence unchanged.

Known issues include:

- During the death or respawn transition, the player can briefly be moved far outside the plot.  
This can temporarily unload plot chunks, cause entities in those chunks to despawn, and remove client-side ghost blocks for that player.
- Player-specific settings, including the world border, can be reset.
- While a player remains on the death screen with Keep Inventory enabled, actions that get or set their inventory do not work reliably.

This is not an exhaustive list; other state and behavior may also be affected.

### Restoring state after a normal death

Treat affected state as invalid after every death.  
Once the player respawns, reapply anything that may have been reset or removed, or check and restore individual pieces of state when they can be inspected reliably.  
This can include recreating despawned entities, resending ghost blocks, and reapplying settings such as the world border.

Inventory handling requires additional care.  
Before the inventory becomes unavailable, copy it into temporary per-player state that lasts until respawn.  
While the player is dead, treat the cached inventory as authoritative:

- Read from the cached inventory instead of the player's inventory.
- Apply inventory changes to the cached inventory.
- If the player leaves from the death screen, save the cached inventory instead of reading their unavailable inventory.
- After the player respawns, overwrite their inventory with the cached version if it was modified and remove the temporary state.

Enable Instant Respawn unless the game intentionally uses the death screen.  
Avoiding the screen mitigates some of the issues and shortens the time in which inventory cannot be accessed, but it does not prevent every death-related issue.

### Replacing the death system

Alternatively, cancel each relevant player death event and implement a custom death and respawn system.  
This requires more code, but gives the game explicit control over which state changes and when the player is considered dead or respawned.

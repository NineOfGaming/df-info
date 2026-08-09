# Selections and execution

A selection is the player-or-entity list carried by a code thread.  
It affects action and condition execution, while structural blocks usually carry the same selection into the code they invoke or contain.

## Selection states

| State | Meaning |
| --- | --- |
| Default selection | No Select Object override is active, so the event's Default target is used |
| Explicit selection | Select Object has produced a player or entity list containing at least one target |
| Empty selection | An explicit selection exists, but its size is zero |
| Selectionless thread | No selection exists, normally because Start Process used its no-targets mode |

A selection contains players or entities, not both.  
Select Object: Reset removes an explicit selection and restores the thread's default behavior.

## Behavior by codeblock

This table describes blocks using their normal Current Selection target.  
Player, Entity, and related condition blocks can bypass the selection when their target setting is changed to an event or special target.

| Block | Default selection | Non-empty explicit selection | Empty selection | Selectionless thread |
| --- | --- | --- | --- | --- |
| Player Action / Entity Action | Runs once for the Default target | Runs once for every selected target | Does not run | Does not run |
| Set Variable | Runs once | Runs once for every selected target | Does not run | Runs once |
| If Player / If Entity | Tests the Default target | Tests all selected targets and passes if at least one matches | Does not pass | Does not pass |
| Select Object | Creates a selection | Replaces, changes, or resets the selection | Replaces, changes, or resets the selection | Creates a selection |
| Call Function | Runs once and passes on the default selection | Runs once and passes on the selection | Runs once and passes on the empty selection | Runs once and passes on the selectionless state |
| Start Process | Uses its configured target mode | Uses its configured target mode | With Current or No Targets can run once; For Each starts none | With Current or No Targets can run once; For Each starts none |
| Game Action / If Variable / If Game / Repeat / Control / Else | Runs once | Runs once | Runs once | Runs once |
| Events / Function / Process | Starts or defines a code line | Starts or defines a code line | Starts or defines a code line | Starts or defines a code line |

An empty selection does not stop the whole code line.  
It makes selection-driven actions run zero times and prevents Current Selection player or entity conditions from finding a match, while blocks that execute once continue normally.

## Start Process target modes

| Target mode | Targets passed to the process | Processes started | Process lifetime |
| --- | --- | --- | --- |
| With Current Targets | The current event targets, but not the explicit selection | One if a Default target exists; otherwise none | Runs only while its Default target exists |
| With Current Selection | The explicit selection, but no event targets | One, even if the selection is empty | Continues even if its selected targets cease to exist or the selection is reset |
| No Targets | No selection or event targets | One | Continues without a target |
| For Each in Selection | One selected target as the process's Default | One per selected target; none if the selection is empty | Runs only while its Default target exists |

Processes started With Current Targets or For Each in Selection are tied to their Default target.  
If that player leaves the plot or that entity ceases to exist, its process stops as well.

## Conditions do not filter the selection

If Player or If Entity passes for one selected target, the branch runs with the original selection.  
The targets that failed are not automatically removed.

For example:

```text
Select Player1 and Player2
If Player: Is Sneaking
    Send "You are sneaking" to Current Selection
```

If only Player1 is sneaking, the If block passes, but Current Selection still contains Player1 and Player2.  
The message will therefore be sent to both players.

Use Select Object: Select by Condition when later actions should affect only the matching targets.  
Use Start Process: For Each in Selection when every target needs a separate thread with that as the Default target.

## Set Variable multiplication

Set Variable runs once per selected entry even when the operation itself has no player or entity target.

This makes bulk updates possible:

```text
Select all players
Set %selected.score to 0
```

It can also multiply a shared modification.  
Incrementing one shared variable while five targets are selected performs five increments, while the same block performs none when the selection is empty.

## Target overrides and fallbacks

Changing a Player Action, Entity Action, If Player, or If Entity target from Current Selection to an event or special target allows it to run independently of the active selection.  
This is useful for accessing a victim, damager, shooter, or another event-specific target.

Game Values also have a target setting that chooses the player or entity from which their value is read.  
Current Selection is the normal target described earlier on this page, so the tables below list only event and special targets.

### Event targets

| Target | Meaning |
| --- | --- |
| Default | The player or entity that triggered the event |
| Killer | The player or entity that killed the Victim |
| Damager | The player or entity that harmed the Victim |
| Victim | The player or entity that was harmed or killed |
| Shooter | The player or entity that fired the Projectile |
| Projectile | The projectile involved in the event |

An event target is only available when the current event provides it.

### Special targets

| Target | Meaning |
| --- | --- |
| All Players | Every player currently on the plot |
| Last Entity | The most recently spawned entity |
| Current Selection | The currently selected targets |

Select Object provides separate actions for selecting all players or the last-spawned entity.  
Select All Entities and Select All Mobs are also Select Object actions, not additional target settings.

The Current Selection target uses the active explicit selection.  
When none is active, it falls back to the event's Default target.  
This is the same fallback used by [`%selected` and `%uuid`](percent-codes.md#target-codes).  
A selectionless thread has no Default target to fall back to.

Some Entity Actions can fall back to a victim or the last spawned entity when no applicable Default target exists.  
Because fallback behavior depends on the event and action, test the exact combination before relying on it.

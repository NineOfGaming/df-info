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

A Call Function block whose name contains [percent codes](percent-codes.md#dynamic-function-and-process-names) can call different functions dynamically.  
The placed call block can remember the parameter signature of the first function it calls during a session, including parameter names, and reuse that signature for later calls.

All functions reachable from one dynamic Call Function block should therefore use compatible parameters.  
If their signatures differ, use separate call blocks or a wrapper function with one stable interface.

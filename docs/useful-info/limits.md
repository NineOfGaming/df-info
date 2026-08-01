# DiamondFire limits

These tables collect plot, entity, variable, value, codespace, and bucket-variable limits.

Limits may change over time, so verify values that a plot depends on critically.

## Plot dimensions

| Type | Basic | Large | Massive | Mega | World |
| --- | ---: | ---: | ---: | ---: | ---: |
| Plot size | 51 × 51 | 101 × 101 | 301 × 301 | 1,001 × 1,001 | 5,999,968 × 5,999,968 |
| Codespace area | 51 × 20 | 101 × 20 | 301 × 20 | 301 × 301 | 301 x 301 |

Codespace area is the full available area, not the length consumed by one template line.  

## Physical code length

Code elements do not all occupy the same amount of physical space when placed in a codespace.  
Length is measured along the code line:

| Element | Physical length |
| --- | ---: |
| Most codeblocks | 2 blocks |
| `repeat` | 1 block |
| `if_entity`, `if_game`, `if_player`, and `if_var` | 1 block |
| `else` | 1 block |
| Opening bracket | 1 block |
| Closing bracket | 2 blocks |

Although `repeat`, all `if_*` codeblocks, and `else` are only one block long themselves, their template structure always includes a separate opening and closing bracket.  
The bracket pair therefore adds three blocks of physical length in addition to the initiating codeblock for a total of four blocks.

## Entity limits

| Entity type | Basic | Large | Massive | Mega / World |
| --- | ---: | ---: | ---: | ---: |
| Mobs | 50 | 100 | 150 | 300 |
| Ender Dragons | 30 | 30 | 30 | 30 |
| Withers | 10 | 10 | 10 | 10 |
| Projectiles | 100 | 200 | 300 | 500 |
| Item drops | 150 | 300 | 450 | 600 |
| Armor stands | 1,000 | 1,000 | 1,000 | 2,000 |
| Falling blocks | 200 | 400 | 600 | 1,000 |
| Decoration entities | 150 | 300 | 450 | 5,000 |
| Map-making entities | 4,000 | 4,000 | 4,000 | 5,000 |
| General entities | 100 | 200 | 300 | 500 |

Decoration entities are item frames and paintings.  
Map-making entities are display and interaction entities.  
General entities are all remaining types, such as evoker fangs, potion clouds, and end crystals.

## Variable and value limits

| Type | Limit |
| --- | ---: |
| Loaded Game and Save variables | 500,000 combined |
| Local variables | 50,000 per thread |
| Line variables | 50,000 per line |
| Save-variable storage | Approximately 4-7 MB compressed; 10 MB uncompressed |
| List length | 10,000 values |
| Dictionary size | 10,000 counted values; up to 5,000 simple key-value pairs |
| String or Text length | 10,000 characters |
| Item tags | 500 |

Nested lists and dictionaries contribute their contained values to these limits.  
Code actions that get or compare a list or dictionary's length only count its top-level entries.  
A nested list or dictionary therefore counts as one entry to those actions even though all of its contents count toward the storage limit.  
Dictionary keys also count, which is why 5,000 simple key-value pairs consume the 10,000-value allowance.

## Codespace and plot-wide limits

| Type | Limit |
| --- | ---: |
| Regular codespaces | 40 |
| Underground codespaces | 9 |
| Total codespaces | 49, or 50 including the base |
| Build limit | 256 blocks |
| Render distance | 7 chunks |
| Plot-name length | 128 characters total; 32 non-MiniMessage/text-code characters |
| Special characters in a plot name | 19, regardless of rank |

## Bucket-variable limits

| Type | Limit | Can be increased? |
| --- | ---: | :---: |
| Namespaces per player | 4 | Yes |
| Data per namespace | 100 MB | Yes |
| Buckets per namespace | 100,000 | Yes |
| Data per bucket | 64 KB | No |
| Bucket name length | 1-256 characters | No |
| Namespace name length | 4-256 characters | No |
| Namespace alias length | 1-128 characters | No |

Load, Save, and Unload operations are rate-limited and may be throttled.  
They average approximately one operation per second, support bursts, and are queued internally; the limit increases for very high player counts.

See the [official bucket-variable limits](https://www.mcdiamondfire.com/docs/bucket-variables/limits/) for current values and information about requesting an increase.

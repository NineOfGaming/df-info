# Projectile and entity references

Some arguments use an item to identify a projectile or entity type.  
The expected argument type determines how the item is interpreted, and some references also depend on the item's stack size.

## Projectile references

| Reference item | Projectile type |
| --- | --- |
| Snowball | Snowball |
| Egg | Egg |
| Ender Pearl | Ender Pearl |
| Trident | Trident |
| Arrow | Arrow |
| Spectral Arrow | Spectral Arrow |
| Tipped Arrow | Tipped Arrow |
| Splash Potion | Splash Potion |
| Lingering Potion | Splash Potion |
| Milk Bucket | Llama Spit |
| Fire Charge | Small Fireball |
| 2 x Fire Charge | Fireball |
| Dragon's Breath | Dragon Fireball |
| Wither Skeleton Skull | Wither Skull |
| 2 x Wither Skeleton Skull | Charged Wither Skull |
| Bottle o' Enchanting | Bottle o' Enchanting |
| Wind Charge | Wind Charge |

## Entity references

| Reference item | Entity type |
| --- | --- |
| Armor Stand | Armor Stand |
| Carrot on a Stick | Interaction |
| Diamond Pickaxe | Item Display |
| End Crystal | End Crystal |
| Eye of Ender | Eye of Ender |
| Bottle o' Enchanting | Experience Orb |
| Firework Rocket | Firework Rocket |
| Fishing Rod | Fishing Bobber |
| Lingering Potion | Area Effect Cloud |
| Name Tag | Text Display |
| Bricks | Block Display |
| Gravel or Sand | Falling Block |
| TNT | Primed TNT |
| Tripwire Hook | Evoker Fangs |
| Any spawn egg | The corresponding mob |

An item's meaning is specific to the expected reference type.  
For example, Bottle o' Enchanting represents its thrown projectile in a projectile argument but an Experience Orb in an entity argument.

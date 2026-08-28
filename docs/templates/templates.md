# Code templates

## Template items in Minecraft

DiamondFire-created template items store a stringified JSON object in `PublicBukkitValues["hypercube:codetemplatedata"]`.  
Hold a template item and run `/i nbt` to inspect it on the server.

The stored object has this general shape:

```ts
{
  author: string;
  name: string;
  version: number;
  code: string;
}
```

- `author` is the player who picked up the code line or template.
- `name` is generated dynamically from the beginning of the code line.
- `version` is the template-encoding version; I've only seen `1`.
- `code` contains the encoded block data.

## Encoding

The raw code data is JSON.  
DiamondFire compresses the JSON with gzip and then encodes the compressed bytes as base64:

```text
JSON → gzip → base64
```

Encoded template data commonly begins with `H4sIAAAAAAAA`.  
Tooling should decode base64 and decompress gzip together instead of exposing raw gzip bytes, which can contain null characters.

## Decoded data

Throughout these docs, fields marked with `?` are optional.  
Every other field is required and must not be omitted, even when it has no value; DiamondFire cannot parse a template with a missing required field.

The decoded JSON object contains a `blocks` array:

```ts
{
  blocks: Block[];
}
```

See [Blocks](blocks.md) for the values in this array and [Items and arguments](items.md) for the values stored in block argument slots.

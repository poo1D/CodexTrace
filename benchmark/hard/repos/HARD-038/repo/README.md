# source-map-ranges

`mapRange(map, start, end)` maps a generated source range back
to original source positions.

The map has a `mappings` array. Each mapping contains:

- `generated`: `{ line, column }`
- `original`: `{ source, line, column }`

Lines are one-based and columns are zero-based. For a generated
position, use the nearest preceding mapping segment on the same
generated line. Ranges may span more than one generated line.
Malformed mapping entries should raise `SourceMapError` with a
message that helps locate the bad entry.

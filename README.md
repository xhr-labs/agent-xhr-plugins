# Release anchor

Release tags of this marketplace point at this tiny orphan commit instead of
the heavy payload snapshots on `main`. Reason: `codex plugin marketplace
upgrade` performs a FULL git clone with a hard 30s timeout, and tags that pin
old payload snapshots (each carrying native binaries) made the clone exceed
it. Release assets stay attached to the releases themselves; nothing
references payload history, so clones stay small.

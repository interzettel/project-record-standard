# Retained exporter branch review

Observed 2026-10-22. Local source: `refs/heads/proof-export` at `c1a49a97af2c514ecae099ad3255beef6276225e`, one commit ahead of main `03782b5739f26041dbe109f3d9426412dcf77fba`. Commit title: Start proof exporter. Source author: Fixture author. Accountable review owner: Sam.

The complete added file, `proof.py`, is:

```python
def export_proof():
    raise NotImplementedError("Proof export needs layout and physical inspection")
```

This establishes unfinished implementation intent, not a usable exporter or a hosted PR. It maps to **LG-003**, once, in LG-WP2 and LG-M2. Sam should review/resume this branch after LG-001 and LG-002. The branch was preserved; no merge, reset, deletion or archive was performed. Its age was not a cleanup criterion.

To inspect the authoritative local source:

```sh
git show c1a49a97af2c514ecae099ad3255beef6276225e:proof.py
git diff 03782b5739f26041dbe109f3d9426412dcf77fba...c1a49a97af2c514ecae099ad3255beef6276225e -- proof.py
```

Physical acceptance and the print requirements still belong to Sam. Hosted PR links and status are unknown because no remote is configured.

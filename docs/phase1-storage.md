# Phase 1 DUAT storage handoff

Status: the reviewed storage campaign completed. New source/build/proof work remains local; historical inactive data is recoverable from the iPad.

TESTED:40 exact candidates were backed up, fully restored and compared by the original DUAT offload path before guarded local retirement. `records/phase1-blockers/storage-20261014-v1/verified-campaign-v1.json` additionally joins every local/iPad item receipt to its tagged snapshot and original path; all predicates passed. `verification-scope-v1/result.jsonl` records exit0. Original/quarantine/verification-scratch absence predicates passed at retirement. Nine historical roots intentionally contain only rehydrated exact compact metadata and an ARCHIVED marker. `owned-quiescence-after-storage-v1.json` confirms recorded own jobs/attributed services settled.

MEASURED: initial preflight free bytes were12023783424. After cache cleanup and verified offloads, the campaign readback reported86296772608 free bytes. Filesystem readings can also change with other workloads; archive size is not represented as measured reclaimed space. Native restic cleanup removed only the precisely inventoried inactive default cache and preserved the production vault cache/repository. The stuck pre-existing backup was stopped under explicit human permission; its signal/context-cancelled failure is retained, not called successful.

Recovery index: `records/phase1-blockers/storage-20261014-v1/cold-item-index-v1.tsv`. It retains each exact original path, item ID, snapshot ID and content-manifest hash locally. Sibling `.ipad.json` locators and historical ARCHIVED markers also retain the recovery identity. Producing commits remain UNVERIFIED where original provenance is absent; exact archival recovery does not invent a rebuild recipe.

Use a fresh local destination, especially for intentionally regrown metadata roots:

```bash
project-vault get 2163b160104243bda9a7930ab66ac65d --to /home/sicarii/Work/worldline-recovered-journal
project-vault find worldline-revalidation
```

Retrieve exact historical bytes when needed; never rebuild them as a substitute for original evidence. The iPad must be online with the configured vault identity. After offload it is the single physical archive copy. This campaign's snapshot joins do not add a whole-repository data scrub or independent acceptance.

Active obj/bin/lib, current source/frame/build inputs and private proof templates are pinned. D26–D28 record authorization, archive comparisons and native cache bootstrap; D30 registers this campaign's owned scheduling window; D32 requires preflight/periodic capacity observations and reviewed completed-output offload between heavy runs. Release only the owned coordination record when foreground work yields; leave all other windows and pins intact.

## Final-v5 selected evidence backup

TESTED: six exact settled report/proof/runtime directories completed backup-only `project-vault put`, including full restored-content/metadata and unchanged-source comparison. All original directories remain local. Exact item IDs, snapshots, content-manifest hashes, commands and raw output references are retained in `records/phase1-blockers/storage-20261015-final-v1/verified-backup-readback.json`. This batch does not cover all other final actor/control payloads, proof objects, source/tool pins or the whole project, and it retires no local data. The earlier forty verified offloads remain a separate campaign. No full-repository recovery or fresh scrub is inferred.

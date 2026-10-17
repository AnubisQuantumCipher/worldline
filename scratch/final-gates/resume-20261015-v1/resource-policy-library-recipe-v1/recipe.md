# Fresh original production library and resource-policy module recipe

MEASURED metadata supports the original project's `--subdirs` route. No private source frame or altered project is needed for this candidate. Actual build/test success remains UNVERIFIED.

The retained `gprbuild --help` says `--subdirs` suffixes object, library and executable directories. The read-only-root `gprinspect` invocation on the original `core/worldline_core.gpr` resolves the aggregate library and its ALIs to `lib/phase1-resource-policy-candidate-v1/`, and compiled objects to the matching suffix beneath `obj/core-library`, `obj/core`, `obj/attest-sha256` and `obj/full-physical`. `gprls -U -s` retains the complete original selected compilation-source roster. Neither listing compiled or ran code.

The physical project closure remains the aggregate, `worldline_core_sources.gpr`, `attest_sha256.gpr`, `protected-canonical/full_physical_sources.gpr`, `worldline_sparklib_link.gpr`, and the existing private `sparklib.gpr` / `sparklib_common.gpr`. Full/private-prebuilt SPARK uses its existing original source, objects, ALIs and static archive; metadata leaves those directories unsuffixed because it is externally built. This is the established build dependency policy, not a proof exclusion. Original WORLDLINE checks compilation retains `-gnata`.

The exact proposed argv and environment are in `recipe.json`. Build payload:

```text
gprbuild -p -P core/worldline_core.gpr -j2 --subdirs=phase1-resource-policy-candidate-v1 -XWORLDLINE_BUILD=checks -XSPARKLIB_MODE=full -XSPARKLIB_BUILD=Production -XSPARKLIB_LIBRARY_TYPE=static -XSPARKLIB_INSTALLED=True -XWORLDLINE_PRIVATE_SPARKLIB_PREBUILT=True -cargs:Ada -fPIC
```

Keep the root and private dependency read-only in the build carrier. Precreate only the fresh suffixed output directories and the owned result/tmp directory, then bind only those writable. This prevents an unexpected unsuffixed write from altering the pinned library/object/ALI files. Use the existing shared-lock, memory-admission, 8G/swap0, storage-guarded launcher. The retained original full-build deadline is 45m. This preparation selects no new test deadline; the coordinator must record its bounded test launch without changing acceptance deadlines.

After actual successful build, run the entire unchanged module in a fresh Python process:

```text
WORLDLINE_CORE_LIB=<worktree>/lib/phase1-resource-policy-candidate-v1/libworldline_core.so
PYTHONPATH=<worktree>/runtime
PYTHONDONTWRITEBYTECODE=1
TMPDIR=<fresh owned result directory>/tmp
python3 -B -m unittest discover -s tests -p test_resource_policy.py -v
```

`ResourcePolicyTests.setUpClass` passes that environment value as an explicit Path to `Core`. `Core` resolves and loads the explicit file; missing/load failure raises rather than falling back. Existing ledger fixtures put the same actual core instance into `Core._shared`. Preserve the original unavailable-API negative control and original observer/liveness fixtures; do not add mocks or alter a decision. The complete original method roster is in the JSON, with no skip decorators observed. This is ordinary finite real-library evidence, not authentic protected execution or a full-domain proof.

Before launch, validate the reviewed integration/source identity and the original private SPARK source/project/object/ALI/archive receipt. Refuse existing or symlinked output paths. Retain hashes of every old pinned root and private artifact; compare after both jobs. Require new suffixed library and ALIs, assertion options in those new ALIs, complete module execution, zero skips and exit0 for its finite claim. Keep every failure and output. Do not claim metadata demonstrates a successful build, exact loaded instructions, proof, or acceptance.

No product, project, pin, dependency, fixture or original artifact was changed. Only version/help/project-listing work ran, inside the owned preparation directory with a read-only-root carrier for project metadata.

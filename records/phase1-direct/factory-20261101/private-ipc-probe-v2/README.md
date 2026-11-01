# Private IPC probe v2 — diagnostic-only successor

The actual v1 nominal probe failed before semaphore creation with `private shm
mount mismatch`; its archived report contains no selected mount records or maps.
The failing member of the mountpoint/rw/tmpfs conjunction is UNKNOWN. A covered
mount-row selection issue is a hypothesis, not an observed topology diagnosis.

This source keeps mount_record and every existing mount predicate unchanged.
It publishes the four selected parsed records and UID/GID maps before predicates,
then includes bounded exact /dev/shm covering candidate rows, the old selected
mount ID, tie counts and the already-open IPC descriptor's fdinfo/mnt_id.
The first-longest/first-tie policy is preserved. No topology repair is included.

All relevant candidate rows must fit the new bounded evidence envelope, otherwise
the diagnostic fails before IPC with explicit incomplete/omitted counts and a
hash of the LF-joined candidate row contents. That hash is not a full mountinfo
file hash. Oversized stdout remains FAILED under the original8192-byte cap;
its fallback preserves bounded candidate evidence and explicitly marks discarded
mandatory fields/unknown cleanup. An incomplete or overflow result cannot qualify.

source_tests.py and boundary_tests.py use deterministic synthetic mount/maps/fdinfo
records and mocked reads. They execute only the diagnostic observation/selection/
rendering path, never open_context, main, semaphore, cleanup, socket, namespace,
mount, guard, compiler or proof. Own source/receipt file I/O is real. Synthetic
IDs3/6 and every fixture mount field are NOT observations from the actual run.

V1 source, collector, six guards, topology, caps, API/ownership cleanup and earlier
runs remain untouched. Root owns any collector/guard successor and must obtain
independent exact-source review before a separately admitted actual diagnostic.
No mechanism qualification or proof/PhaseOne acceptance follows from this proposal.

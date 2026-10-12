#!/usr/bin/env python3
"""Selected ENTRY; execute only through the retained approved-source loader."""
import sys
_loader = sys.modules.get('_worldline_approved_source_loader')
if type(_loader) is not type(sys):
    raise RuntimeError('CUSTODY_PROVISION_EARLY_SOURCE_REQUIRED')
_lease = _loader.current()
if type(_lease) is not _loader.ApprovedSourceLease:
    raise RuntimeError('CUSTODY_PROVISION_REAL_SOURCE_LEASE_REQUIRED')
_lease.check()
from pathlib import Path
_runtime = Path(__file__).parent.parent / 'runtime'
_lease.directory_or_absent(str(_runtime))
sys.path.append(str(_runtime))
from worldline.custody_v2_provision_entry import main
main()

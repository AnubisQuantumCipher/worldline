"""Exact source-selected original control requester child entry."""
import sys
_approved=sys.modules.get('_worldline_approved_source_loader')
if _approved is None:raise SystemExit('RESOURCE_CONTROL_EARLY_SOURCE_REQUIRED')
_source=_approved.current()
if type(_source) is not _approved.ApprovedSourceLease:
    raise SystemExit('RESOURCE_CONTROL_ACTUAL_SOURCE_REQUIRED')
_source.check()
import argparse
from pathlib import Path
# Original isolated loader does not add the ENTRY's script directory.
_runtime = str(Path(__file__).parents[2] / 'runtime')
_source.directory_or_absent(_runtime)
sys.path.insert(0, _runtime)
from worldline.owner_resource_control import OwnerResourceControl

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--peer-child',action='store_true',required=True)
    parser.add_argument('--plan',type=Path,required=True)
    args=parser.parse_args()
    _source.file(str(Path(__file__).absolute()),('ENTRY','SOURCE'))
    OwnerResourceControl.peer_child(args.plan)

if __name__=='__main__':main()

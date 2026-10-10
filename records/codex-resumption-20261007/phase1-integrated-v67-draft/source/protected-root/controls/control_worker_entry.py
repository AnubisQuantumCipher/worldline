"""Qualified observer ENTRY around the unchanged original exec worker entry.

The native helper still appends its sole real custody descriptor; no argument,
request, owner, observation, handler or native decision is substituted here.
"""
import sys
_approved = sys.modules.get('_worldline_approved_source_loader')
if _approved is None:
    raise SystemExit('CONTROL_WORKER_EARLY_APPROVED_SOURCE_REQUIRED')
_lease = _approved.current()
_lease.check()
from pathlib import Path
import types


def main():
    for directory in (Path(__file__).parent.parent.parent / 'runtime',
                      Path(__file__).parent, Path(__file__).parent.parent):
        _lease.directory_or_absent(str(directory))
        sys.path.append(str(directory))
    from worldline.custody_control_registration import register_from_source, source_observers, publish_source_observers
    register_from_source(str(Path(__file__).with_suffix('.observer.json')))
    duplex = Path(__file__).with_suffix('.duplex.json')
    if str(duplex) in _lease.files:
        from duplex_original_control import configure_from_source, exercise
        from worldline.custody_control_registration import register_worker_control
        configure_from_source(str(duplex))
        register_worker_control(exercise)
    original = Path(__file__).parent.parent / 'worker_entry.py'
    _lease.file(str(original), ('SOURCE',))
    module = types.ModuleType('worldline_original_custody_worker_entry')
    module.__file__ = str(original)
    code = _lease.compile_source(str(original), module.__name__)
    # The selected original module itself checks the real early source lease.
    exec(code, module.__dict__)
    _lease.check()
    try:
        return module.main()
    finally:
        primary = sys.exc_info()[1]
        errors = []
        try:
            from observed_controls import assert_recorders
            assert_recorders(source_observers(), (), (), ())
            if str(duplex) in _lease.files:
                from duplex_original_control import require_exercised
                require_exercised()
        except BaseException as error:
            errors.append(error)
        try:
            publish_source_observers()
        except BaseException as error:
            errors.append(error)
        try:
            _lease.check()
        except BaseException as error:
            errors.append(error)
        if errors:
            if primary is None:
                raise errors[0]
            for error in errors:
                primary.add_note('Actual control observation publication failed: ' + repr(error))


if __name__ == '__main__':
    main()

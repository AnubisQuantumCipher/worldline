"""Check all actual process-role captures without manufacturing native output."""
import hashlib
import json
from pathlib import Path
from custody_runtime_controls_v35 import KINDS, CONTROLS, SCHEMA
from observed_controls import SUBJECT_CASES


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def actual_manifests(paths, *, publication_errors=None):
    """Prefer complete publications; retain interrupted write/read evidence."""
    import os
    import stat
    selected = []
    errors = publication_errors if publication_errors is not None else []

    def complete(path, predecessor=None):
        raw = None
        try:
            info = path.lstat()
            require(stat.S_ISREG(info.st_mode) and info.st_uid == 0
                    and not stat.S_IMODE(info.st_mode) & 0o077,
                    'COVERAGE_PUBLICATION_PRIVATE_REGULAR_FILE_REQUIRED')
            raw = path.read_bytes()
            manifest = json.loads(raw)
            if (not isinstance(manifest, dict) or manifest.get('schema') != SCHEMA
                    or not manifest.get('original_commands')
                    or not manifest.get('producer_source_sha256')
                    or not isinstance(manifest.get('cases'), list) or not manifest['cases']):
                raise ValueError('COVERAGE_PUBLICATION_INCOMPLETE_MANIFEST')
            if predecessor is not None:
                require(manifest['producer_source_sha256'] == predecessor['producer_source_sha256']
                        and manifest['original_commands'] == predecessor['original_commands']
                        and len(manifest['cases']) == 1, 'COVERAGE_ACTUAL_OUTCOME_MANIFEST_SPLIT')
                old, new = predecessor['cases'][0], manifest['cases'][0]
                for key in ('name', 'kind', 'operation', 'input', 'delta', 'context',
                            'before_load', 'expected_status', 'expected_position'):
                    require(old.get(key) == new.get(key), 'COVERAGE_ACTUAL_OUTCOME_DECISION_SPLIT_' + key)
            for row in manifest['cases']:
                for slot in ('input', 'delta', 'before_load', 'after_load', 'context', 'uncertainty'):
                    if slot not in row:
                        continue
                    record = row[slot]
                    relative = Path(record['path'])
                    require(not relative.is_absolute() and '..' not in relative.parts,
                            'COVERAGE_CAPTURE_ARTIFACT_ESCAPES_OUTPUT')
                    artifact = path.parent / relative
                    info = artifact.lstat()
                    require(stat.S_ISREG(info.st_mode) and info.st_uid == 0
                            and not stat.S_IMODE(info.st_mode) & 0o077,
                            'COVERAGE_ARTIFACT_PRIVATE_REGULAR_FILE_REQUIRED')
                    if hashlib.sha256(artifact.read_bytes()).hexdigest() != record['sha256']:
                        raise ValueError('COVERAGE_PUBLICATION_INCOMPLETE_ARTIFACT_BYTES')
                if not all(slot in row for slot in ('input', 'before_load', 'context')):
                    raise ValueError('COVERAGE_PUBLICATION_INCOMPLETE_NATIVE_INPUT')
            return manifest
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append({'path': str(path), 'sha256': None if raw is None else hashlib.sha256(raw).hexdigest(),
                           'raw_hex': None if raw is None else raw.hex(),
                           'error': {'type': type(error).__name__, 'message': str(error),
                                     'errno': getattr(error, 'errno', None)}})
            return None

    for wanted in paths:
        wanted = Path(wanted)
        info = wanted.parent.lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid == 0
                and not stat.S_IMODE(info.st_mode) & 0o077,
                'COVERAGE_ACTUAL_PRIVATE_CAPTURE_DIRECTORY_REQUIRED')
        if os.path.lexists(wanted) and complete(wanted) is not None:
            selected.append(wanted)
            continue
        fragments = sorted(wanted.parent.glob('case-*.native-decision.json'))
        require(fragments, 'COVERAGE_CRASH_WITHOUT_ACTUAL_DURABLE_NATIVE_DECISION')
        completed_start = len(selected)
        for decision in fragments:
            before = complete(decision)
            if before is None:
                continue
            require(len(before['cases']) == 1, 'COVERAGE_ACTUAL_SINGLE_NATIVE_DECISION_REQUIRED')
            outcome = decision.with_name(decision.name.removesuffix('.native-decision.json') + '.actual-outcome.json')
            if os.path.lexists(outcome) and complete(outcome, before) is not None:
                selected.append(outcome)
            else:
                selected.append(decision)
        require(len(selected) > completed_start, 'COVERAGE_CRASH_WITHOUT_ACTUAL_COMPLETE_NATIVE_DECISION')
    require(len(set(selected)) == len(selected), 'COVERAGE_ACTUAL_CAPTURE_ALIAS')
    return tuple(selected)


def check(paths, required_kinds, required_controls, required_subject_cases):
    from worldline.root_worker_codec import scoped_restore_archive
    kinds = set()
    subjects = set()
    controls = set()
    evidence = []
    publication_errors = []
    for path in actual_manifests(paths, publication_errors=publication_errors):
        path = Path(path)
        manifest_raw = path.read_bytes()
        manifest = json.loads(manifest_raw)
        require(manifest['schema'] == SCHEMA, 'COVERAGE_ACTUAL_CAPTURE_SCHEMA')
        import custody_runtime_controls_v35 as exporter
        expected_source = hashlib.sha256(Path(exporter.__file__).read_bytes()).hexdigest()
        require(manifest['producer_source_sha256'] == expected_source, 'COVERAGE_ORIGINAL_EXPORTER_SOURCE_SPLIT')
        require(manifest['original_commands'], 'COVERAGE_ACTUAL_ORIGINAL_COMMAND_REQUIRED')
        for row in manifest['cases']:
            values = {}
            for slot in ('input', 'delta', 'before_load', 'after_load', 'context', 'uncertainty'):
                if slot not in row:
                    continue
                record = row[slot]
                relative = Path(record['path'])
                require(not relative.is_absolute() and '..' not in relative.parts,
                        'COVERAGE_CAPTURE_ARTIFACT_ESCAPES_OUTPUT')
                raw = (path.parent / relative).read_bytes()
                require(hashlib.sha256(raw).hexdigest() == record['sha256'],
                        'COVERAGE_ACTUAL_CAPTURE_BYTES_CHANGED')
                values[slot] = raw
            candidate = scoped_restore_archive(values['input'])['candidate']
            require(candidate['kind'] == row['kind'] and candidate['operation'] == row['operation'],
                    'COVERAGE_ORIGINAL_CANDIDATE_SPLIT')
            ready = row['expected_status'] == 0 and 'delta' in values and 'context' in values
            if ready:
                kinds.add(row['kind'])
                if row['kind'] in SUBJECT_CASES:
                    expected = 'REQUEST' if row['kind'].startswith('REQUEST_') else 'DESCRIPTOR'
                    require(candidate['subject_kind'] == expected, 'COVERAGE_ORIGINAL_SUBJECT_CLASS_SPLIT')
                    subjects.add(row['kind'])
            require(set(row['controls']) <= CONTROLS, 'COVERAGE_UNENROLLED_CONTROL_TAG')
            if 'uncertain' in row['controls']:
                from worldline.root_worker_codec import raw_restore_archive
                require('uncertainty' in values, 'COVERAGE_GENUINE_UNCERTAINTY_CAPSULE_MISSING')
                capsule = raw_restore_archive(values['uncertainty'])
                require(capsule['input'] == values['input'] and capsule['candidate'] == candidate['record']
                        and capsule['native_status'] == row['expected_status']
                        and capsule['native_position'] == row['expected_position'],
                        'COVERAGE_ACTUAL_UNCERTAIN_NATIVE_INPUT_SPLIT')
            controls.update(row['controls'])
        evidence.append({'capture': str(path), 'sha256': hashlib.sha256(manifest_raw).hexdigest(),
                         'actual_original_commands': manifest['original_commands']})
    require(set(required_kinds) <= KINDS and set(required_kinds) <= kinds,
            'COVERAGE_REQUIRED_GENUINE_NATIVE_KIND_MISSING')
    require(set(required_controls) <= CONTROLS and set(required_controls) <= controls,
            'COVERAGE_REQUIRED_REAL_CONTROL_NOT_EXERCISED')
    require(set(required_subject_cases) <= SUBJECT_CASES and set(required_subject_cases) <= subjects,
            'COVERAGE_FULL_ORIGINAL_SUBJECT_CLASS_MISSING')
    return {'actual_positive_kinds': sorted(kinds), 'actual_controls': sorted(controls),
            'actual_subject_cases': sorted(subjects), 'captures': evidence,
            'publication_errors': publication_errors,
            'native_reexecution_and_outer_admission_still_required': True}

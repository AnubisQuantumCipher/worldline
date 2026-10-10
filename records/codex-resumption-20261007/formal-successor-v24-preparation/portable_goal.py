"""Read-only current-controller observation guard; original window lineage is separate.

No goal/RPC call, mutation, actor, service, admission, target or acceptance occurs here.
Historical observations bind identity/objective only, never current activity/freshness.
"""
from pathlib import Path
import datetime
import hashlib
import json
import stat

MODEL = 'openai-codex/gpt-6.1-sol:max'
AUTHOR = 'SolPhaseOneIntegration'
HOLDER = '01a1149d-db62-74b0-a5f7-b0239f285c44'
REVIEW_DISPOSITION = 'QUALIFIED_EXACT_CURRENT_CONTROLLER_OBSERVATION_SURFACE_FOR_ORIGINAL_FORMAL_GOAL'
STAGES = frozenset(('preparation', 'ready', 'reserve', 'dispatch', 'collect'))
MAX_AGE = datetime.timedelta(minutes=30)


def load(path):
    return json.loads(Path(path).read_text())


def pin(path):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    after = path.lstat()
    fields = lambda row: (row.st_dev, row.st_ino, row.st_mode, row.st_size,
                          row.st_mtime_ns, row.st_ctime_ns)
    assert fields(before) == fields(after), ('Changed during read', str(path))
    return {'path': str(path), 'sha256': digest, 'bytes': after.st_size,
            'mode': stat.S_IMODE(after.st_mode)}


def matched(row):
    assert set(row) == {'path', 'sha256', 'bytes', 'mode'}
    path = Path(row['path'])
    assert path.is_absolute() and pin(path) == row, str(path)
    return path


def content_identity(row):
    return {name: row[name] for name in ('sha256', 'bytes', 'mode')}


def native_goal(record):
    assert record['observer'] == 'Main'
    assert record['source_tool'] == 'functions.goal' and record['arguments'] == {'op': 'get'}
    details = record['actual_response']['details']
    assert details['op'] == 'get'
    goal = details['goal']
    assert isinstance(goal['id'], str) and goal['id'] and 'threadId' not in goal
    assert record['required_window_holder'] == HOLDER and record['no_phase_acceptance'] is True
    return goal


def check_profile(root):
    root = Path(root)
    binding = load(root / 'source-bindings.json')
    profile_row = binding['pins']['current_controller_binding']
    assert matched(profile_row) == root / 'current-controller-binding.json'
    profile = load(profile_row['path'])
    assert profile['schema'] == 'worldline-current-controller-original-lineage-binding-v1'
    assert profile['candidate'] == str(root) and profile['required_window_holder'] == HOLDER
    assert profile['author'] == AUTHOR and profile['author_model'] == MODEL
    assert profile['approval'] is False and profile['phase_acceptance'] is False
    review = load(matched(binding['pins']['portable_goal_guard_review']))
    assert review['actual_model_selection'] == MODEL and review['author'] == AUTHOR
    assert isinstance(review['reviewer'], str) and review['reviewer'].strip() and review['reviewer'] != AUTHOR
    assert review['disposition'] == REVIEW_DISPOSITION and review['blocking_findings'] == []
    assert review['target_execution'] is False and review['phase_acceptance'] is False
    for row in review['artifacts'].values():
        matched(row)
    for name, path in (('portable_goal.py', root / 'portable_goal.py'),
                       ('current-controller-binding.json', root / 'current-controller-binding.json'),
                       ('prepare_successor.py', root / 'prepare_successor.py'),
                       ('authorization.py', root / 'authorization.py')):
        assert content_identity(pin(path)) == content_identity(review['artifacts'][name]), name
    assert matched(binding['pins']['portable_goal_module']) == root / 'portable_goal.py'
    for row in profile['provenance'].values():
        matched(row)
    original_record = load(profile['provenance']['original_paused_goal_observation']['path'])
    assert original_record['interface'] == 'supported finite codex app-server --stdio thread/goal/get'
    assert [row['method'] for row in original_record['actual_requests']] == ['initialize', 'initialized', 'thread/goal/get']
    assert original_record['actual_requests'][2]['params'] == {'threadId': HOLDER}
    original = original_record['actual_response']['result']['goal']
    assert original['threadId'] == HOLDER and original['status'] == 'paused'
    assert original_record['no_original_goal_mutation'] is True and original_record['no_thread_resume_or_turn_start'] is True
    assert original['objective'] == profile['original_goal_objective']
    seed = native_goal(load(profile['provenance']['admitted_native_goal_observation']['path']))
    assert seed['status'] == 'active' and seed['id'] != HOLDER
    assert {name: seed[name] for name in ('id', 'objective', 'createdAt')} == profile['current_controller']
    return profile


def check_observation(root, stage, observation):
    """Consume a separately retained actual Main-native get plus the original clock field."""
    assert __debug__ and stage in STAGES
    root = Path(root)
    profile = check_profile(root)
    assert observation['schema'] == 'worldline-current-controller-stage-observation-v1'
    assert observation['stage'] == stage and observation['candidate'] == str(root)
    assert observation['required_window_holder'] == HOLDER
    assert 'goalToolObservation' not in observation, 'Never relabel a native id as a legacy thread observation'
    row = observation['nativeGoalToolObservation']
    path = matched(row)
    assert path.is_relative_to(root), 'Current stage observation must be retained by this exact candidate'
    assert '..' not in path.relative_to(root).parts
    assert path.resolve(strict=True).is_relative_to(root.resolve(strict=True)), 'Fresh receipt resolves outside its actual candidate'
    for component in path.relative_to(root).parts:
        assert component not in ('source', 'private-sparklib'), 'Fresh observations are not target inputs'
    record = load(path)
    assert record['candidate'] == str(root) and record['stage'] == stage
    goal = native_goal(record)
    assert goal['status'] == 'active', 'The actually observed current controller must be active'
    assert {name: goal[name] for name in ('id', 'objective', 'createdAt')} == profile['current_controller']
    clock = datetime.datetime.strptime(observation['clockToolObservation']['current_time'], '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=datetime.timezone.utc)
    recorded = datetime.datetime.fromisoformat(record['recorded_at'].replace('Z', '+00:00'))
    assert recorded.tzinfo is not None and recorded.utcoffset() == datetime.timedelta(0)
    now = datetime.datetime.now(datetime.timezone.utc)
    assert datetime.timedelta(0) <= now - clock <= MAX_AGE, 'Original fresh clock gate failed'
    assert datetime.timedelta(0) <= now - recorded <= MAX_AGE, 'Actual native get is stale or future-dated'
    assert abs(clock - recorded) <= MAX_AGE, 'Native read and clock do not belong to the fresh stage'
    return {'stage': stage, 'candidate': str(root), 'native_goal_id': goal['id'],
            'required_window_holder': HOLDER, 'native_observation': row,
            'clockToolObservation': observation['clockToolObservation'],
            'legacy_goal_status_is_historical': 'paused', 'goal_mutation': False,
            'target_execution': False, 'phase_acceptance': False}

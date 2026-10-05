LABEL = ('ENGINEERING_ONLY: scratch result on a throwaway copy; never proof, review, admission, ordinary, '
         'source-qualification or Phase One acceptance evidence. Original guarantees OPEN_UNCHANGED.')
REVIEW_PROFILE = {'schema': 'claude-scratch-frame-review-v5', 'different_from_author': True,
                  'actual_model_selection': 'gpt-6.1-sol', 'author': 'Claude Code lead claude-opus-5-5',
                  'disposition': 'QUALIFIED_ENGINEERING_SCRATCH_FRAME', 'blocking_findings': [],
                  'execution_authority': 'NONE_FRESH_LEAD_ADOPTION_AND_ORIGINAL_GATES_REQUIRED',
                  'scratch_results_as_evidence': False, 'proof_acceptance': False, 'phase_acceptance': False,
                  'source_acceptance': False, 'target_execution': False}
O_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
# ... (unchanged lines 105-686 omitted) ...
def rollout_join(events_path, argv_path):
    """Actual codex-exec review joined to its recorded rollout: roster, model, cwd, provider, final message and its
    timestamp, argv. All reads anchored."""
    mismatches = []

    def need(condition, what):
        if not condition:
            mismatches.append(what)
    review = Dir.anchor(REVIEW)
    try:
        freeze_record = json.loads(review.read_bytes('review-freeze.json'))
        need(set(freeze_record.get('files', {})) == FRAME_REVIEW_ROSTER, 'review freeze roster')
        for name in sorted(FRAME_REVIEW_ROSTER & set(freeze_record.get('files', {}))):
            row = freeze_record['files'][name]
            need(review.ident(name) == {k: row[k] for k in ('sha256', 'bytes', 'mode')}, 'freeze member ' + name)
        need(freeze_record.get('actual_model_selection') == 'gpt-6.1-sol' and freeze_record.get('different_from_author') is True,
             'freeze model/author profile')
        reported_names = {name: review.ident(name)['sha256'] for name in ('review.json', 'REVIEW.md', 'review-freeze.json')}
    finally:
        review.close()
    events_bytes, events_pin = pinned(events_path)
    events = [json.loads(line) for line in events_bytes.decode().splitlines() if line.strip().startswith('{')]
    threads = sorted({e['thread_id'] for e in events if e.get('type') == 'thread.started'})
    need(len(threads) == 1, 'exactly one thread in the event stream')
    thread = threads[0] if threads else ''
    finals = [e['item']['text'] for e in events
              if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'agent_message']
    rollouts = sorted(glob.glob('/home/sicarii/.codex/sessions/*/*/*/rollout-*' + thread + '.jsonl')) if thread else []
    need(len(rollouts) == 1, 'exactly one rollout for thread')
    contexts, providers, rollout_final, rollout_final_at, rollout_pin = [], [], None, None, None
    if len(rollouts) == 1:
        rollout_bytes, rollout_pin = pinned(rollouts[0])
        for line in rollout_bytes.decode().splitlines():
            row = json.loads(line)
            payload = row.get('payload') if isinstance(row.get('payload'), dict) else {}
            if row.get('type') == 'turn_context':
                contexts.append({k: payload.get(k) for k in ('model', 'effort', 'cwd', 'approval_policy', 'sandbox_policy')})
            if row.get('type') == 'session_meta':
                providers.append(payload.get('model_provider'))
            if row.get('type') == 'event_msg' and payload.get('type') == 'task_complete':
                rollout_final, rollout_final_at = payload.get('last_agent_message'), row.get('timestamp')
    need(bool(contexts) and all(c['model'] == 'gpt-6.1-sol' for c in contexts), 'rollout model gpt-6.1-sol')
    need(bool(contexts) and all(c['cwd'] == str(REVIEW) for c in contexts), 'rollout cwd is the review directory')
    need(bool(providers) and all(p in ('openai', 'openai-review') for p in providers), 'rollout provider is the ChatGPT backend')
    need(bool(finals) and rollout_final is not None and finals[-1] == rollout_final, 'event final message equals rollout final')
    need(isinstance(rollout_final_at, str), 'rollout completion timestamp')
    reported = set(re.findall(r'\b[0-9a-f]{64}\b', rollout_final or ''))
    for name, digest in reported_names.items():
        need(digest in reported, 'rollout final message reports ' + name)
    argv_bytes, argv_pin = pinned(argv_path)
    argv = json.loads(argv_bytes)
    need(isinstance(argv, list) and len(argv) > 4 and argv[0] == '/usr/lib/chatgpt/resources/codex' and argv[1] == 'exec'
         and '-m' in argv and argv[argv.index('-m') + 1] == 'gpt-6.1-sol' and 'model_reasoning_effort=max' in argv,
         'recorded exec argv is an actual gpt-6.1-sol max-effort codex exec')
    provenance = {'reviewer_thread': thread, 'rollout': rollout_pin, 'turn_contexts': contexts, 'session_providers': providers,
                  'exec_argv': argv, 'exec_argv_record': argv_pin, 'event_stream': events_pin,
                  'rollout_final_message_sha256': hashlib.sha256((rollout_final or '').encode()).hexdigest(),
                  'rollout_final_timestamp': rollout_final_at}
    return mismatches, provenance


def review_profile_problems(review, lead_id, inventory_sha):
    problems = [key for key, value in REVIEW_PROFILE.items() if review.get(key) != value]
    if review.get('candidate') != str(FRAME):
        problems.append('candidate')
    if review.get('lead_id') != lead_id:
        problems.append('lead_id')
    if review.get('frame_inventory_sha256') != inventory_sha:
        problems.append('frame_inventory_sha256')
    if review.get('report_sha256') != sha(REVIEW / 'REVIEW.md'):
        problems.append('report_sha256')
    for key, name in (('checks', 'checks.json'), ('complete_bound_inputs', 'bound-inputs.json'), ('tool_topology', 'tool-topology.json')):
        if (review.get(key) or {}) != pin(REVIEW / name):
            problems.append('sidecar ' + key)
    return problems


def validate_adoption_observation(claude_lead, observation, adoption_at, provenance):
    """The retained adoption observation: complete schema, stage, candidate, identity and authority profile, joined to
    the exact append-only transcript prefix it observed, and ordered after the review's completion and before the
    adoption record (v3 B4). The later-goal list must be derived from the observed goal commands (v4 N06)."""
    require(observation.get('schema') == claude_lead.OBSERVATION_SCHEMA and observation.get('stage') == 'scratch-adopt'
            and observation.get('candidate') == str(FRAME), 'adoption observation schema/stage/candidate')
    require(observation.get('sourcePreparationOnly') is False and observation.get('targetExecution') is False
            and observation.get('admission') is False and observation.get('reservation') is False,
            'adoption observation authority profile')
    observed = observation.get('leadObservation') or {}
    expected = {'leadId': claude_lead.LEAD_ID, 'harness': 'claude-code', 'sessionId': claude_lead.SESSION_ID,
                'transcript': str(claude_lead.TRANSCRIPT), 'goalRecord': claude_lead.GOAL_RECORD,
                'goalSetRecord': claude_lead.GOAL_SET_RECORD, 'objectiveSha256': claude_lead.OBJECTIVE_SHA256,
                'startInstruction': claude_lead.START_INSTRUCTION, 'laterGoalCommandIndexes': [],
                'liveWithinSeconds': claude_lead.MAX_LEAD_SILENCE_SECONDS, 'transcriptLive': True, 'status': 'active'}
    wrong = sorted(key for key, value in expected.items() if observed.get(key) != value)
    require(not wrong, 'adoption observation identity/profile: ' + repr(wrong))
    start = pin(claude_lead.START_INSTRUCTION['path'])
    require(start['sha256'] == claude_lead.START_INSTRUCTION['sha256'] and start['bytes'] == claude_lead.START_INSTRUCTION['bytes'],
            'start instruction identity')
    size = observed.get('transcriptBytesObserved')
    require(isinstance(size, int) and not isinstance(size, bool) and size > 0, 'observed transcript size')
    transcript_dir = Dir.anchor(Path(claude_lead.TRANSCRIPT).parent)
    try:
        prefix = transcript_dir.read_prefix(existing_name(Path(claude_lead.TRANSCRIPT).name), size)
    finally:
        transcript_dir.close()
    require(hashlib.sha256(prefix).hexdigest() == observed.get('transcriptSha256Observed'),
            'adoption observation is not a prefix of the append-only transcript')
    lines = prefix.split(b'\n')
    if lines and lines[-1] == b'':
        lines.pop()
    for key in ('goalRecord', 'goalSetRecord'):
        row = observed[key]
        require(row['index'] < len(lines) and hashlib.sha256(lines[row['index']]).hexdigest() == row['sha256'],
                'goal record in the observed prefix: ' + key)
    commands = claude_lead._goal_command_indexes(lines)
    require(commands == observed.get('goalCommandIndexesObserved'), 'goal commands in observed prefix')
    require([index for index in commands if index > claude_lead.GOAL_RECORD['index']] == observed.get('laterGoalCommandIndexes') == [],
            'later goal commands derived from the observed goal commands')
    last = claude_lead._last_timestamp(lines)
    require(last is not None and last == observed.get('lastTranscriptTimestamp'), 'last transcript timestamp in observed prefix')
    observed_at = parse_time(observation['clockObservation']['current_time'])
    silence = (observed_at - parse_time(last)).total_seconds()
    recorded_silence = observed.get('transcriptSilenceSeconds')
    require(isinstance(recorded_silence, (int, float)) and abs(silence - recorded_silence) <= 1.0
            and 0 <= silence <= claude_lead.MAX_LEAD_SILENCE_SECONDS, 'adoption observation liveness')
    require(isinstance(provenance.get('rollout_final_timestamp'), str)
            and parse_time(provenance['rollout_final_timestamp']) <= observed_at <= parse_time(adoption_at),
            'adoption observation must follow the review completion and precede the adoption record')


def adopt(events_path, argv_path):
    claude_lead = lead()
    inventory = frame_inventory()
    review_dir = Dir.anchor(FRAME / 'review')
    try:
        require(not review_dir.has('lead-adoption.json'), 'adoption already recorded')
        review = load_json(REVIEW / 'review.json')
        mismatches, provenance = rollout_join(events_path, argv_path)
        mismatches += ['review profile: ' + p for p in review_profile_problems(review, claude_lead.LEAD_ID, inventory['__pin__']['sha256'])]
        observation = claude_lead.observe('scratch-adopt', str(FRAME))
        claude_lead.check_observation(observation, 'scratch-adopt', str(FRAME))
        require(not mismatches, 'adoption mismatches: ' + repr(mismatches))
        at = now()
        validate_adoption_observation(claude_lead, observation, at, provenance)
        record = review_dir.write_json('lead-adoption.json', {
            'schema': 'claude-scratch-frame-lead-adoption-v5', 'at': at, 'frame': str(FRAME), 'lead_id': claude_lead.LEAD_ID,
            'frame_inventory_sha256': inventory['__pin__']['sha256'], 'review_sha256': sha(REVIEW / 'review.json'),
            'review_freeze_sha256': sha(REVIEW / 'review-freeze.json'), 'review_report_sha256': sha(REVIEW / 'REVIEW.md'),
            'mismatches': [], **provenance, 'lead_observation': observation, 'truth_boundary': LABEL})
    finally:
        review_dir.close()
    print(json.dumps({'adoption': record}))


def frame_admitted():
    """Complete frame, review profile, adoption profile, re-joined rollout provenance and the validated retained
    adoption observation; refuses otherwise. Returns the frozen inventory."""
    claude_lead = lead()
    inventory = frame_inventory()
    inventory_sha = inventory['__pin__']['sha256']
    review = load_json(REVIEW / 'review.json')
    problems = review_profile_problems(review, claude_lead.LEAD_ID, inventory_sha)
    require(not problems, 'review profile: ' + repr(problems))
    adoption = load_json(ADOPTION)
    require(adoption.get('schema') == 'claude-scratch-frame-lead-adoption-v5' and adoption.get('frame') == str(FRAME), 'adoption profile')
    require(adoption['lead_id'] == claude_lead.LEAD_ID and adoption['mismatches'] == [], 'adoption lead/mismatches')
    require(adoption['frame_inventory_sha256'] == inventory_sha, 'adoption frame inventory')
    require(adoption['review_sha256'] == sha(REVIEW / 'review.json'), 'adoption review pin')
    require(adoption['review_freeze_sha256'] == sha(REVIEW / 'review-freeze.json'), 'adoption review-freeze pin')
    require(adoption['review_report_sha256'] == sha(REVIEW / 'REVIEW.md'), 'adoption review report pin')
    for key in ('rollout', 'exec_argv_record', 'event_stream'):
        require(adoption[key] is not None and pin(adoption[key]['path']) == adoption[key], 'adoption provenance pin changed: ' + key)
    mismatches, provenance = rollout_join(adoption['event_stream']['path'], adoption['exec_argv_record']['path'])
    require(not mismatches, 'rollout join no longer holds: ' + repr(mismatches))
    for key in ('reviewer_thread', 'rollout_final_message_sha256', 'rollout_final_timestamp'):
        require(provenance[key] == adoption[key], 'rollout identity changed: ' + key)
    validate_adoption_observation(claude_lead, adoption['lead_observation'], adoption['at'], provenance)
    return inventory

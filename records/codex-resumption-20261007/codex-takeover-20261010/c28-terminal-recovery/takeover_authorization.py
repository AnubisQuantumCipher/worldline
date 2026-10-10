"""Terminal-only Codex takeover; historical qualification stays exact."""
from pathlib import Path
import datetime
import json
import sys
sys.path.insert(0, '/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/records/codex-resumption-20261007/formal-successor-v28-preparation')
import successor_support as support
import portable_goal
import sys
sys.dont_write_bytecode = True

D = Path('/home/sicarii/Documents/Codex/2026-10-03/read-the-two-files-and-follow/work/claude-lead-isolation-v1/wt-1/records/codex-resumption-20261007/formal-successor-v28-preparation')
T = Path(__file__).resolve().parent
GOAL = '01a1149d-db62-74b0-a5f7-b0239f285c44'
MODE = 'full-strict-formal-diagnostic'
WINDOW = Path('/home/sicarii/Documents/Codex/2026-09-30/how-do-u-feel-about-the/work/worldline-build-proof-window.json')


def pin(path):
    return support.pinned(path)


def matched(row):
    return support.matched(row)


def check():
    assert __debug__
    custody = check_takeover()
    portable_goal.check_profile(D)
    adoption = support.load(D / 'review/root-adoption-v1/adoption.json')
    assert adoption['schema'] == 'root-full-formal-diagnostic-adoption-v1'
    assert adoption['candidate'] == str(D) and adoption['holder_task'] == GOAL
    assert adoption['permitted_action_modes'] == [MODE]
    assert adoption['diagnostic_only'] is True and adoption['phase_acceptance'] is False
    assert adoption['proof_acceptance'] is False and adoption['required_entrypoint'] == str(D / 'outer_capture.py')
    assert matched(adoption['frame_freeze']) == D / 'author-freeze.json'
    freeze = support.load(D / 'author-freeze.json')
    assert freeze['author'] == support.AUTHOR and freeze['author_model'] == support.MODEL
    for name, row in freeze['files'].items():
        assert pin(D / name) == {'path': str(D / name), **row}, name
    review = support.load(matched(adoption['independent_review']))
    support.independent(review, 'QUALIFIED_EXACT_FULL_STRICT_FORMAL_DIAGNOSTIC_PREPARATION', freeze['author'])
    for key, path in [('inputs_sha256', D / 'inputs.json'),
                      ('proposal_sha256', D / 'reviewed-launch-proposal.json'),
                      ('gate_sha256', D / 'review/root-live-lane-v1/inputs.json'),
                      ('final_source_inventory_sha256', D / 'final-source-inventory.json')]:
        assert review[key] == pin(path)['sha256'], key
    assert review['frame_freeze'] == adoption['frame_freeze']
    assert review['private_dependency_inventory'] == pin(D / 'dependency-inventory.json')
    current = support.load(matched(adoption['current_source_review']))
    support.independent(current, 'QUALIFIED_EXACT_EMITTED_CURRENT_SOURCE_FOR_FULL_STRICT_FORMAL_DIAGNOSTIC_ONLY')
    assert current['source_inventory_sha256'] == pin(D / 'final-source-inventory.json')['sha256']
    assert current['complete_source_entries'] == pin(D / 'selected-source-entries.json')
    assert current['private_dependency_inventory'] == pin(D / 'dependency-inventory.json')
    assert current['strict_proof'] is False and current['phase_acceptance'] is False
    binding = support.load(D / 'source-bindings.json')
    support.source_review(binding['pins']['source_review'], binding['pins']['source_selection'], binding['pins']['source_inventory'])
    current_closure_review = support.check_closure_review(D)
    if current_closure_review is not None:
        closure_binding = support.load(D / 'current-closure-review-binding.json')
        assert closure_binding['independent_review'] == current_closure_review
        assert closure_binding['current_closure_binding'] == binding['current_closure_binding']['binding']
        assert closure_binding['historical_drift_acknowledgement'] == binding['pins']['historical_drift_acknowledgement']
        assert closure_binding['acknowledgement_expanded'] is False and closure_binding['target_execution'] is False
    return {**adoption, '_takeover_custody': custody}

def check_takeover():
    # A recovery authority is distinct from the historical execution owner.
    assert pin(D / 'authorization.py')['sha256'] == '45b805b6843264b410d9648a9009387577c42f406b74ee58d109a7039385aeca'
    assert pin(D / 'review/root-terminal-v1/collect_terminal.py')['sha256'] == '13ae18a8104ece2d681be6ab8f9c2e0a2069ef88127bcbd9a9ddade6fb3ff5a9'
    assert len(sys.argv) == 3 and sys.argv[1] == '--inputs-sha256'
    inputs_pin = pin(T / 'recovery-inputs.json')
    assert inputs_pin['sha256'] == sys.argv[2]
    inputs = support.load(matched(inputs_pin))
    assert set(inputs) == {'goal', 'clock', 'takeover', 'review'}
    for key, expected in (
        ('goal', T / 'current-goal.json'),
        ('clock', T / 'current-clock.json'),
        ('takeover', T.parent / 'takeover.json'),
        ('review', T / 'independent-review.json'),
    ):
        assert matched(inputs[key]) == expected
    review = support.load(matched(inputs['review']))
    assert review['author'] == 'codex-root-01a12665'
    assert isinstance(review['reviewer'], str) and review['reviewer'].strip()
    assert review['reviewer'] != review['author']
    assert review['actual_model'] == 'gpt-6.1-sol'
    assert review['reasoning_effort'] == 'max'
    assert review['scope'] == 'TERMINAL_CUSTODY_ONLY'
    assert review['verdict'] == 'QUALIFIED' and review['blocking_findings'] == []
    assert set(review['source_pins']) == {'takeover_authorization.py', 'collect_terminal.py'}
    for name, sha in review['source_pins'].items():
        assert pin(T / name)['sha256'] == sha
    observation = support.load(matched(inputs['goal']))
    clock = support.load(matched(inputs['clock']))
    assert observation['source_tool'] == 'functions.get_goal'
    assert observation['arguments'] == {}
    goal = observation['actual_response']['goal']
    assert goal['threadId'] == '01a12665-43dd-7732-be5f-b7c5bec8be96'
    assert goal['status'] == 'active'
    assert goal['objective'] == 'Referenced pasted text files:\n- pasted text file: /home/sicarii/.codex/attachments/39a29ba1-214f-4c74-92f3-c4460b067e33/pasted-text-1.txt. Read this file before continuing.'
    attachment = Path('/home/sicarii/.codex/attachments/39a29ba1-214f-4c74-92f3-c4460b067e33/pasted-text-1.txt')
    assert pin(attachment)['sha256'] == '53588423cea5771a70ecc572f3789041a4a422c39442c6750a68a3700f64ecff'
    observed = datetime.datetime.strptime(clock['current_time'], '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=datetime.timezone.utc)
    recorded = datetime.datetime.strptime(observation['recorded_at'], '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=datetime.timezone.utc)
    current = datetime.datetime.now(datetime.timezone.utc)
    assert observed <= current <= observed + datetime.timedelta(minutes=30)
    assert recorded <= current <= recorded + datetime.timedelta(minutes=30)
    assert abs(observed - recorded) <= datetime.timedelta(minutes=30)
    takeover = support.load(matched(inputs['takeover']))
    assert takeover['current_controller'] == goal['threadId']
    assert takeover['operator_instruction'] == 'shut that down ans then you do this'
    assert takeover['shutdown']['pid'] == 672100 and takeover['shutdown']['starttime'] == '32265401'
    for pid in (672100, 776436):
        assert not (Path('/proc') / str(pid)).exists(), 'Prior controller or broker identity unresolved'
    assert pin(WINDOW)['sha256'] == '54f164db0f7996533fcf69339332a9cbfb9143bf44f1319dae4da0a6f37dc4cb'
    coord = support.load(WINDOW)
    assert coord['status'] == 'reserved' and coord['holder_task'] == GOAL and coord['candidate'] == str(D)
    return {'current_controller': goal['threadId'], 'historical_execution_holder': GOAL,
            'target_execution_authorized': False, 'inputs': inputs_pin, **inputs}

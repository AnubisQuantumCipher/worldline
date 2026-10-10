"""Current-model different-author formal-only adoption; no observations invented."""
from pathlib import Path
import datetime
import json
import successor_support as support
import portable_goal

D = Path(__file__).resolve().parent
GOAL = '01a1149d-db62-74b0-a5f7-b0239f285c44'
MODE = 'full-strict-formal-diagnostic'
WINDOW = Path('/home/sicarii/Documents/Codex/2026-09-30/how-do-u-feel-about-the/work/worldline-build-proof-window.json')


def pin(path):
    return support.pinned(path)


def matched(row):
    return support.matched(row)


def check(stage):
    assert __debug__ and stage in ('ready', 'reserve', 'dispatch', 'collect')
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
    observation = support.load(matched(adoption['fresh_goal_observations'][stage]))
    assert observation['stage'] == stage and observation['candidate'] == str(D)
    portable_goal.check_observation(D, stage, observation)
    if stage == 'dispatch':
        window = json.loads(WINDOW.read_text())
        assert window['status'] == 'reserved' and window['holder_task'] == GOAL and window['candidate'] == str(D)
    return adoption

"""Main-native observation eligibility; never call/resume/mutate a goal/window."""
from __future__ import annotations

import datetime
import json
from pathlib import Path
import shlex

import observation_support as s


def profile_input():
    custody, original = s.inherited()
    old = custody.check_controller_profile(original["pins"]["native_controller_eligibility_review"])
    candidate_profile = {
        "schema": "worldline-N67-inner-observation-current-controller-binding-v1",
        "candidate": str(s.F), "author": s.AUTHOR, "execution_owner": "Main",
        "required_window_holder": old["required_window_holder"],
        "current_controller": old["current_controller"],
        "original_goal_objective": old["original_goal_objective"],
        "original_complete_profile": old,
        "original_complete_profile_sha256": s.digest(old),
        "original_controller_review": original["pins"]["native_controller_eligibility_review"],
        "clock_command": custody.CONTROLLER_CLOCK_COMMAND,
        "maximum_age_seconds": int(custody.CONTROLLER_MAX_AGE.total_seconds()),
        "stages": sorted(s.STAGES), "main_observation_root": str(s.J),
        "Main_model": "openai-codex/gpt-6.1-sol:max",
        "Main_builtin_advisor": {"enabled": True, "mechanism": "OMP built-in /advisor",
            "configured_model": "openai-codex/gpt-6-astra:medium", "sync_backlog": "off",
            "guidance_only": True, "independent_review": False},
        "human_routing_supersession": s.INPUTS["current_Main_routing_supersession"],
        "review_model": s.MODEL, "historical_identity_is_not_current_freshness": True,
        "goal_mutation": False, "target_execution": False, "phase_acceptance": False}
    return candidate_profile


def profile(capture_row, controller_review_row):
    candidate_profile = profile_input()
    artifacts = {name: s.pin(s.P / name) for name in ("controller.py", "observation_support.py", "Main_wait.py", "inputs.json", "author-provenance.json", "review-contracts.json")}
    s.reviewed(controller_review_row, "controller", artifacts,
               {"original_capture": capture_row, "profile_digest_sha256": s.digest(candidate_profile)})
    return candidate_profile


def check(stage, observation_row, capture_row, controller_review_row):
    assert __debug__ and stage in s.STAGES
    p = profile(capture_row, controller_review_row)
    observation = s.read(s.external(observation_row))
    assert set(observation) == {"schema", "stage", "candidate", "required_window_holder",
        "nativeGoalToolObservation", "clockToolObservation", "MainRoutingObservation", "no_goal_mutation", "no_phase_acceptance"}
    assert observation["schema"] == "worldline-N67-inner-observation-stage-observation-v1"
    assert observation["stage"] == stage and observation["candidate"] == str(s.F)
    assert observation["required_window_holder"] == p["required_window_holder"]
    assert observation["no_goal_mutation"] is True and observation["no_phase_acceptance"] is True
    native = s.read(s.external(observation["nativeGoalToolObservation"]))
    assert set(native) == {"observer", "source_tool", "arguments", "actual_response",
        "required_window_holder", "no_phase_acceptance", "recorded_at", "candidate", "stage"}
    assert native["observer"] == "Main" and native["source_tool"] == "functions.goal" and native["arguments"] == {"op": "get"}
    assert native["stage"] == stage and native["candidate"] == str(s.F)
    assert native["required_window_holder"] == p["required_window_holder"] and native["no_phase_acceptance"] is True
    response = native["actual_response"]
    assert isinstance(response["text"], str) and response["details"]["op"] == "get"
    goal = response["details"]["goal"]
    assert "threadId" not in goal and goal["status"] == "active"
    assert {key: goal[key] for key in ("id", "objective", "createdAt")} == p["current_controller"]
    clock = observation["clockToolObservation"]
    assert set(clock) == {"current_time", "source_tool", "actual_command", "actual_returncode", "wall_seconds", "actual_response_pin", "Main_actual_wait_capture", "actual_wrapper_argv", "actual_Main_tool_invocation"}
    assert clock["source_tool"] == "functions.bash" and clock["actual_command"] == p["clock_command"]
    assert type(clock["actual_returncode"]) is int and clock["actual_returncode"] == 0
    assert type(clock["wall_seconds"]) in (int, float) and clock["wall_seconds"] >= 0
    actual = s.read(s.external(clock["actual_response_pin"]))
    assert isinstance(actual["details"], dict) and actual["text"].splitlines()[0].strip() == clock["current_time"]
    wait = s.read(s.external(clock["Main_actual_wait_capture"]))
    assert wait["schema"] == "worldline-N67-inner-observation-Main-actual-child-wait-v1"
    assert wait["observer"] == "Main" and wait["mode"] == "clock"
    expected_wrapper = ["/usr/bin/python3", "-B", str(s.P / "Main_wait.py"), "clock", clock["Main_actual_wait_capture"]["path"]]
    assert wait["actual_wrapper_argv"] == clock["actual_wrapper_argv"] == expected_wrapper
    assert wait["actual_wrapper_source"] == s.pin(s.P / "Main_wait.py")
    assert wait["actual_child_argv"] == ["/usr/bin/date", "-u", "+%Y-%m-%d %H:%M:%S UTC"]
    assert wait["actual_clock_command"] == p["clock_command"]
    assert wait["original_Main_tool_timeout_seconds"] == 30
    assert wait["actual_Popen_wait_observed"] is True and wait["actual_returncode"] == clock["actual_returncode"]
    assert wait["retention_complete"] is True and wait["timed_out"] is False and not wait["errors"]
    assert wait["provider_numeric_exit_inferred"] is False and wait["actual_elapsed_seconds"] <= 30
    invocation = clock["actual_Main_tool_invocation"]
    assert invocation["source_tool"] == "functions.bash"
    assert invocation["arguments"]["command"] == shlex.join(expected_wrapper) and invocation["arguments"]["timeout"] == 30
    stdout_path = s.external(wait["raw_streams"]["stdout"])
    stderr_path = s.external(wait["raw_streams"]["stderr"])
    assert stdout_path.read_bytes() == (clock["current_time"] + "\n").encode() and stderr_path.read_bytes() == b""
    clock_time = datetime.datetime.strptime(clock["current_time"], "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=datetime.timezone.utc)
    recorded = datetime.datetime.fromisoformat(native["recorded_at"].replace("Z", "+00:00"))
    current = datetime.datetime.now(datetime.timezone.utc)
    maximum = datetime.timedelta(seconds=p["maximum_age_seconds"])
    assert recorded.tzinfo is not None and recorded.utcoffset() == datetime.timedelta(0)
    assert datetime.timedelta(0) <= current - clock_time <= maximum
    assert datetime.timedelta(0) <= current - recorded <= maximum and abs(recorded - clock_time) <= maximum
    routing = s.read(s.external(observation["MainRoutingObservation"]))
    assert routing["schema"] == "worldline-N67-inner-observation-live-Main-routing-v1"
    assert routing["observer"] == "Main" and routing["stage"] == stage and routing["candidate"] == str(s.F)
    assert routing["actual_model_selection"] == p["Main_model"]
    assert routing["thinking_level"] == "max" and routing["resolved_model_is_fallback"] is False
    assert routing["service_tier"] == "default" and routing["advisor_enabled"] is True
    assert routing["actual_session_observation"] and routing["actual_reply_observation"]
    assert routing["human_routing_supersession"] == p["human_routing_supersession"]
    directive = s.read(s.external(routing["human_routing_supersession"]))
    guidance = p["Main_builtin_advisor"]
    assert directive["schema"] == "Main-live-human-routing-supersession-v1"
    assert directive["requested_lead"] == p["Main_model"] and directive["requested_independent_and_delegated"] == p["review_model"]
    assert directive["original_goal_and_profile_identity_retained_not_rewritten"] is True
    assert directive["historical_model_observations_not_relabelled"] is True
    assert directive["no_gate_or_acceptance_relaxation"] is True
    assert directive["advisor_enabled"] is True and directive["requested_guidance_mechanism"] == guidance["mechanism"]
    assert directive["requested_guidance_model"] == guidance["configured_model"]
    assert directive["advisor_guidance_only"] is True and directive["advisor_is_not_independent_review"] is True
    assert directive["catch_up"] == "off / nonblocking"
    assert directive["fallback_forbidden"] is True and directive["standard_speed_required"] is True
    advisor_session = directive["actual_advisor_session_and_provider_observations"][0]
    assert advisor_session["type"] == "session" and advisor_session["id"]
    advisor_reply = directive["actual_advisor_session_and_provider_observations"][-1]["message"]
    assert advisor_reply["provider"] == "openai-codex" and advisor_reply["model"] == "gpt-6-astra"
    assert advisor_reply["serviceTier"] == "default" and advisor_reply["errorMessage"] is None
    roles_text = directive["actual_saved_model_role_observation"]["text"].splitlines()[0]
    assert roles_text.startswith("modelRoles: ")
    assert json.loads(roles_text.removeprefix("modelRoles: "))["advisor"] == guidance["configured_model"]
    assert directive["actual_catch_up_observation"]["text"].splitlines()[0] == 'advisor.syncBacklog: "off"'
    # Session /advisor on does not mutate saved advisor.enabled. No forced
    # settings/restart or missing response effort is fabricated by this gate.
    assert routing["phase_acceptance"] is False
    routed_at = datetime.datetime.fromisoformat(routing["recorded_at"].replace("Z", "+00:00"))
    assert routed_at.utcoffset() == datetime.timedelta(0) and datetime.timedelta(0) <= current - routed_at <= maximum
    s.external(observation_row)
    return {"stage": stage, "candidate": str(s.F), "current_controller": p["current_controller"],
            "required_window_holder": p["required_window_holder"], "observation": observation_row,
            "profile_digest_sha256": s.digest(p), "target_execution": False, "phase_acceptance": False}


if __name__ == "__main__":
    import json
    import sys
    assert __debug__
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == "profile-input":
        output = Path(args[1])
        assert output.parent == s.J and not output.exists() and not output.is_symlink()
        value = profile_input()
        s.save_new(output, {"schema": "worldline-N67-controller-exact-source-only-review-input-v1",
                           "observer": "Main", "profile": value, "profile_digest_sha256": s.digest(value),
                           "qualification": False, "target_execution": False, "phase_acceptance": False})
        print(json.dumps({"controller_review_input": s.pin(output), "target_execution": False}, sort_keys=True))
    elif len(args) == 6 and args[0] == "stage":
        output = Path(args[5])
        assert output.parent == s.J and not output.exists() and not output.is_symlink()
        value = check(args[1], s.pin(Path(args[4])), s.pin(Path(args[2])), s.pin(Path(args[3])))
        s.save_new(output, value)
        print(json.dumps({"actual_consumed_preaction_guard": s.pin(output), "target_execution": False}, sort_keys=True))
    else:
        raise SystemExit("profile-input OUTPUT; stage STAGE CAPTURE CONTROLLER_REVIEW OBSERVATION OUTPUT")

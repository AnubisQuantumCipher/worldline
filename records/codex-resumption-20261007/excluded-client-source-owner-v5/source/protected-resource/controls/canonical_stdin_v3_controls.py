"""UNRUN genuine protected controls; no mock/native/fixture fallback.

The outside campaign must construct actual owner-provisioned principals under
original complete admission and selected early source/native/runtime custody.
This code never constructs a grant, fake slot, READY flag or synthetic wait.
"""
from pathlib import Path
from worldline.protected_startup import require
from worldline.canonical_actor_stdin import retained_input


async def full_delivery(principal,slot,capture_id,*,expected_stdout,expected_stderr,expected_exit):
    material=retained_input(principal,slot,capture_id)
    before=principal.resources.current_snapshot()
    answer=await principal.pump_original_workload(slot,capture_id)
    require(Path(answer['raw_stdout_path']).read_bytes()==expected_stdout
        and Path(answer['raw_stderr_path']).read_bytes()==expected_stderr,
        'CONTROL_FULL_ORIGINAL_RAW_OUTPUT_CHANGED')
    require(answer['raw_main_exit_code']==expected_exit and answer['closed']==slot.closed
        and slot.closed is not None and slot.closed_event is not None,
        'CONTROL_ACTUAL_RAW_FAILURE_OR_OWNED_CLOSURE_CHANGED')
    from worldline import resource_scoped_run_ledger as S
    principal.resources.observations.load()
    complete=S.restore(answer['stdin_event']['payload'])
    require(complete['payload']==material['stdin_raw']
        and complete['written']==len(material['stdin_raw']) and complete['EOF_close_returned'] is True,
        'CONTROL_FULL_ORIGINAL_INPUT_OR_EOF_CHANGED')
    after=principal.resources.current_snapshot()
    require(before.rows==after.rows,
        'CONTROL_TRANSPORT_MUST_NOT_RELEASE_OR_CHARGE_RESOURCE_ROWS')
    return answer


async def required_refusal(action,expected_reason):
    from worldline.protected_resource_runtime import ResourceProducerRefusal
    try:await action()
    except ResourceProducerRefusal as actual:
        require(actual.args and actual.args[0]==expected_reason,
            'CONTROL_WRONG_REFUSAL_CANNOT_PASS')
        return actual
    raise AssertionError('required genuine refusal absent')


async def full_preflight_cleanup(principal,slot,capture_id,*,expected_reason,
                                expected_stdout,expected_stderr):
    """Actual post-GO isolated fixture; no manufactured principal/slot/ACK."""
    from worldline.canonical_actor_stdin import owned_slot
    from worldline.protected_startup import StartupRefusal
    from worldline.protected_resource_runtime import ResourceProducerRefusal
    from worldline import resource_scoped_run_ledger as S
    import asyncio
    owned_slot(principal,slot)
    require(slot.started and slot.credential_committed is not None
        and slot.credential_ack_event is not None,'CONTROL_GENUINE_GO_NATIVE_ACK_FIXTURE_REQUIRED')
    before=principal.resources.current_snapshot()
    try:await principal.pump_original_workload(slot,capture_id)
    except (StartupRefusal,ResourceProducerRefusal) as actual:
        require(actual.args and actual.args[0]==expected_reason,
            'CONTROL_WRONG_PREFLIGHT_REFUSAL_CANNOT_PASS')
    else:raise AssertionError('required genuine preflight refusal absent')
    cleanup=getattr(slot,'failure_cleanup_task',None)
    require(cleanup is not None,'CONTROL_OWNED_PREFLIGHT_CLEANUP_TASK_ABSENT')
    await asyncio.shield(cleanup)
    record=slot.failure_capture
    require(record['primary_text']==expected_reason and record['resource_release_or_charge'] is False
        and record['held']==slot.held_event and record['dispatch']==slot.dispatch,
        'CONTROL_FULL_PRIMARY_ORIGINAL_OWNERSHIP_CHANGED')
    principal.resources.observations.load();events=principal.resources.observations.events
    selected=[]
    for event in events:
        if event['reservation']!=slot.row.bound.reservation.hex():continue
        if event['cause'] not in ('ACTOR_TRANSPORT_OUTPUT_READ','ACTOR_TRANSPORT_FAILURE_OUTPUT'):continue
        payload=S.restore(event['payload'])
        require(payload['held']==slot.held_event and payload['dispatch']==slot.dispatch,
            'CONTROL_ACTUAL_FAILURE_OUTPUT_CUSTODY_CHANGED')
        selected.append(payload)
    require(b''.join(item['bytes'] for item in selected if item['stream']=='stdout')==expected_stdout
        and b''.join(item['bytes'] for item in selected if item['stream']=='stderr')==expected_stderr,
        'CONTROL_COMPLETE_ACTUAL_PREFLIGHT_FAILURE_OUTPUT_CHANGED')
    require(principal.resources.current_snapshot().rows==before.rows,
        'CONTROL_PREFLIGHT_FAILURE_MUST_RETAIN_RESOURCE_ROWS')
    result_event=getattr(slot,'failure_result_event',None)
    if record['status']=='OWNED_CLOSED_RAW_FAILURE_RETAINED':
        require(result_event is not None and result_event in events
            and result_event['cause']=='ACTOR_TRANSPORT_FAILURE_RESULT'
            and result_event['reservation']==slot.row.bound.reservation.hex()
            and S.restore(result_event['payload'])==record,
            'CONTROL_FULL_AUTHENTIC_FINAL_FAILURE_RESULT_REQUIRED')
        require(slot.closed is not None and slot.closed_event is not None
            and record['closed']==slot.closed and record['closed_event']==slot.closed_event,
            'CONTROL_GENUINE_PREFLIGHT_CLOSURE_CHANGED')
    else:
        require(record['status']=='UNKNOWN' and slot.principal.slots.get(slot.row.bound.reservation.hex()) is slot,
            'CONTROL_UNKNOWN_MUST_RETAIN_ACTUAL_OWNED_SLOT')
    return record

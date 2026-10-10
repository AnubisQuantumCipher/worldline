"""Actual retained original workload -> owned V3 input/output transport.

A genuine full-domain child dispatcher supplies its native-authorized slot,
original operation ancestry and selected full adapter/SandboxSpec. This module
creates no grant/use/reservation/dispatch or successful canonical outcome.
"""
from __future__ import annotations
import asyncio,os,shutil
from .protected_startup import require
from .operation_capture import restore_archive
from .protected_operations import identity


def owned_slot(principal,slot):
    """Retained actual ownership precedes cleanup; caller data grants nothing.

    No client artifact, supplied PID/path, current eligibility flag or copied
    ACK can select another workload for root cleanup. stop_owned_transport
    independently rechecks the actual selected manager InvocationID/ControlGroup.
    """
    from .protected_operations import CanonicalOperationPrincipal
    from .protected_scoped_supervisor_v3 import OwnedSupervisorV3
    from .protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
    require(type(principal) is CanonicalOperationPrincipal and type(slot) is OwnedSupervisorV3
        and type(principal.resources) is ProtectedScopedResourcePrincipal
        and slot.principal is principal.resources and principal.resources.operation_principal is principal
        and principal.resources.lease is principal.lease and principal.resources.gate is principal.gate
        and principal.resources.slots.get(slot.row.bound.reservation.hex()) is slot
        and slot.held is not None,
        'OPERATION_V3_ACTUAL_OWNED_SLOT_REQUIRED')
    return slot


def retained_input(principal,slot,capture_id):
    owned_slot(principal,slot)
    principal.intact();principal.journal.load()
    operation=principal._operation_key(slot.row.bound.operation);row=principal.journal.rows[operation]
    values=[]
    for boundary in row['boundaries']:
        if boundary['name']!='ORIGINAL_WORKLOAD_CAPTURE':continue
        material=restore_archive(bytes.fromhex(boundary['material']))
        if identity(material).hex()==capture_id:values.append(material)
    require(len(values)==1,'OPERATION_V3_EXACT_AUTHENTIC_WORKLOAD_CAPTURE_REQUIRED')
    material=values[0]
    require(material['schema']=='worldline.protected-original-workload-material-v1'
        and material['operation']==operation and material['original_request']==row['capture']['request']
        and material['original_native_use']==principal._original_native_use(row)
        and material['stdin_close_required'] is True,
        'OPERATION_V3_ORIGINAL_WORKLOAD_CUSTODY_CHANGED')
    mode=material['adapter']['mission_via_stdin']
    require(type(mode) is bool and type(material['mission_raw']) is bytes
        and material['actual_mission_file']==material['mission_raw']
        and material['stdin_raw']==(material['mission_raw'] if mode else b''),
        'OPERATION_V3_COMPLETE_ORIGINAL_STDIN_OR_EOF_CHANGED')
    plan=slot.dispatch['payload']['plan']
    require(tuple(plan['argv'])==material['sandbox_argv'],
        'OPERATION_V3_ORIGINAL_SANDBOX_DISPATCH_CROSSWALK_REQUIRED')
    witness=slot._input_commit()
    require(witness['authority']['original_request']==material['original_request']
        and witness['authority']['plan']==plan,
        'OPERATION_V3_FULL_NATIVE_WORKLOAD_EXECUTION_JOIN_CHANGED')
    # World.record is the original dataclass dictionary, not camel-case wire DTO.
    world=principal.store.world(material['world']['instance_id'])
    require(world.record()==material['world'],'OPERATION_V3_ORIGINAL_WORLD_CHANGED')
    return material


async def pump_original(principal,slot,capture_id):
    """All post-owned-launch preflight is inside the genuine cleanup boundary."""
    # This authentic retained slot anchor alone permits its own cleanup; stale
    # capture/path/native/current-world facts below cannot bypass that cleanup.
    # An unowned arbitrary slot never obtains root stop authority.
    owned_slot(principal,slot)
    streams={};outputs={};tasks=[];input_task=None;wait_task=None
    try:
        material=retained_input(principal,slot,capture_id)
        instance=material['world']['instance_id'];runner=principal.controller.runner
        raw_path=runner.paths.logs/(instance+'.agent.jsonl')
        stderr_path=runner.paths.logs/(instance+'.agent.stderr')
        for path in (raw_path,stderr_path):
            require(path.parent==runner.paths.logs and not os.path.lexists(path),
                'OPERATION_V3_ORIGINAL_RAW_OUTPUT_PATH_ALREADY_PRESENT')
        await slot.attach_output()
        for name,path in (('stdout',raw_path),('stderr',stderr_path)):
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
            streams[name]=os.fdopen(fd,'wb',buffering=0)
        slot.original_output_reads={}
        async def drain(name):
            reader=getattr(slot,name);sink=streams[name];occurrence=0
            while True:
                chunk=await reader.read(shutil.COPY_BUFSIZE)
                observed={'stream':name,'occurrence':occurrence,'bytes':chunk,
                    'EOF_observed':chunk==b'','held':slot.held_event,
                    'dispatch':slot.dispatch,'written_to_raw_file':0}
                slot.original_output_reads[name]=observed
                # Retain the entire actual read before writing its raw file.
                # A short/failed file write cannot drop its unpersisted tail.
                principal.resources.observations.append('ACTOR_TRANSPORT_OUTPUT_READ',
                    slot.row.bound.reservation.hex(),observed)
                occurrence+=1
                if not chunk:break
                view=memoryview(chunk);offset=0
                while offset<len(view):
                    try:
                        written=sink.write(view[offset:])
                        require(type(written) is int and written>0,'OPERATION_V3_FULL_RAW_WRITE_NO_PROGRESS')
                        offset+=written;observed['written_to_raw_file']=offset
                    except InterruptedError:continue
            os.fsync(sink.fileno())
        outputs={name:asyncio.create_task(drain(name)) for name in ('stdout','stderr')}
        # Both real drainers are scheduled before the sole full input writer.
        input_task=asyncio.create_task(slot.write_input(material['stdin_raw']))
        wait_task=asyncio.create_task(slot.wait());tasks=[*outputs.values(),input_task,wait_task]
        done,_pending=await asyncio.wait(tasks,return_when=asyncio.FIRST_EXCEPTION)
        faults=[task.exception() for task in done if not task.cancelled() and task.exception() is not None]
        if faults:raise faults[0]
        answers=await asyncio.gather(*tasks,return_exceptions=True)
        errors=[value for value in answers if isinstance(value,BaseException)]
        if errors:
            primary=errors[0]
            for error in errors[1:]:primary.add_note('other full transport failure: '+repr(error))
            raise primary
        return {'material':material,'stdin_event':answers[-2],
            'raw_main_exit_code':answers[-1],'closed':slot.closed,'closed_event':slot.closed_event,
            'raw_stdout_path':str(raw_path),'raw_stderr_path':str(stderr_path)}
    except BaseException as primary:
        # Protect the actual owner's cleanup from a second caller cancellation.
        # The task remains explicitly owned by this real slot until it returns;
        # cancellation is never turned into EOF, native terminal or release.
        cleanup=asyncio.create_task(slot.capture_owned_failure(primary,
            output_tasks=outputs,input_task=input_task,wait_task=wait_task))
        slot.failure_cleanup_task=cleanup
        def retained_cleanup_completion(task,original=primary):
            # Consume the actual completion even when the caller was cancelled
            # again. The full task/error remains owned by this actual slot.
            try:task.result()
            except BaseException as error:
                slot.failure_cleanup_error=error
                original.add_note('owned cleanup completion UNKNOWN: '+repr(error))
        cleanup.add_done_callback(retained_cleanup_completion)
        try:await asyncio.shield(cleanup)
        except BaseException as cleanup_error:
            primary.add_note('actual owned cleanup remains UNKNOWN or pending: '+repr(cleanup_error))
        raise
    finally:
        # A shielded pending cleanup may still own these exact sinks. It closes
        # them on actual task completion; no live writer gets a closed handle.
        cleanup=getattr(slot,'failure_cleanup_task',None)
        if cleanup is not None and not cleanup.done():
            def close_after_owned_cleanup(_task):
                for stream in streams.values():stream.close()
            cleanup.add_done_callback(close_after_owned_cleanup)
        else:
            for stream in streams.values():stream.close()

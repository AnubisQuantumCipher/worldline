"""Lossless actual original workload preparation; no plan-as-authority shortcut.

This is the original runner/adapter/SandboxSpec producer seam. The separately
declared scoped task dispatcher must reserve a distinct full native child hold,
join the complete original grant/use/request and this actual plan, capture real
Running/actor state, commit its closed native conjunction before credential ACK,
and stream the retained mission only through the owned sixth input descriptor.
This producer itself never launches, selects a permission, or releases a hold.
"""
from dataclasses import fields
from pathlib import Path,PosixPath
import os
from .protected_startup import require
from .operation_capture import archive
from .protected_operations import current_scope,OperationScope,clone,identity
from .agents.base import AgentContext
from .agents import CodexAdapter,ClaudeAdapter,GenericAdapter,OmpAdapter,PiAdapter
from .linux.namespaces import SandboxSpec,OverlayRoot,CredentialProjection
from .project import ProjectConfig,GeneratedClassifier,CheckSpec,ServiceSpec
from .runner import AgentRunner

_RECORDS=(AgentContext,SandboxSpec,OverlayRoot,CredentialProjection,
          GeneratedClassifier,CheckSpec,ServiceSpec)
_ADAPTERS=(CodexAdapter,ClaudeAdapter,GenericAdapter,OmpAdapter,PiAdapter)


def factual(value):
    """Full explicit data encoding, never an import/eval/default decoder."""
    kind=type(value)
    if kind in _RECORDS:
        return {'record':[kind.__module__,kind.__name__],
            'fields':[[field.name,factual(getattr(value,field.name))] for field in fields(kind)]}
    if kind is PosixPath:return {'path_raw':os.fsencode(value)}
    if kind is dict:return {key:factual(item) for key,item in value.items()}
    if kind is tuple:return tuple(factual(item) for item in value)
    if kind is list:return [factual(item) for item in value]
    require(value is None or kind in (bytes,str,bool,int,float),'OPERATION_WORKLOAD_COMPLETE_DATA_TYPE_REQUIRED')
    return value


def capture_workload(p,runner,world,adapter,mission,context,project,spec,
                     sandbox_argv,*,low_priority,timeout):
    # Exactly the original concrete producer objects, not a socket-supplied
    # SandboxSpec or a root path/UID masquerading as requester authority.
    scope=current_scope()
    require(type(scope) is OperationScope and scope.principal is p and scope.peer is not None
        and type(runner) is AgentRunner and runner is p.controller.runner
        and runner.store is p.store and runner.core is p.core
        and type(adapter) in _ADAPTERS and type(context) is AgentContext
        and type(project) is ProjectConfig and type(spec) is SandboxSpec,
        'OPERATION_WORKLOAD_ACTUAL_ORIGINAL_PRODUCER_REQUIRED')
    p.intact();operation=scope.operation;row=p.journal.rows[operation];captured=row['capture']
    require(scope.peer is p.active_peers.get(operation) and scope.peer.observation()==captured['request']
        and p.store.world(world.instance_id).record()==world.record()
        and spec.instance_id==world.instance_id and type(mission) is str,
        'OPERATION_WORKLOAD_ORIGINAL_PEER_WORLD_JOIN_CHANGED')
    argv=tuple(sandbox_argv)
    require(tuple(adapter.build_argv(context,mission))==spec.argv
        and tuple(runner.sandbox.build_argv(spec))==argv,
        'OPERATION_WORKLOAD_FAITHFUL_SELECTED_ARGV_CHANGED')
    require(type(adapter.mission_via_stdin) is bool,
        'OPERATION_WORKLOAD_ORIGINAL_STDIN_MODE_REQUIRED')
    mission_raw=mission.encode('utf-8','strict')
    # Exactly original semantics: no added newline, size cap, normalization,
    # shell quoting or default mission. Non-stdin adapters still require EOF.
    stdin_raw=mission_raw if adapter.mission_via_stdin else b''
    mission_path=spec.runtime/'mission.txt';world_path=spec.runtime/'world.json'
    require(mission_path.read_bytes()==mission_raw,
        'OPERATION_WORKLOAD_ACTUAL_MISSION_SOURCE_CHANGED')
    actual_files={}
    for path in (Path(adapter.executable),Path(runner.sandbox.executable)):
        raw=p.lease.source_lease.file(str(path),('SOURCE','INTERPRETER','EXTENSION','DATA'))
        actual_files[os.fsencode(path)]={'raw':raw,'source_role_selection':'exact early lease'}
    credentials=[]
    for projection in spec.credential_mounts:
        require(type(projection) is CredentialProjection,
            'OPERATION_WORKLOAD_ORIGINAL_CREDENTIAL_RECORD_REQUIRED')
        credentials.append({'projection':factual(projection),
            'actual_bytes':projection.source.read_bytes()})
    project_source=None if project.source_path is None else Path(project.source_path).read_bytes()
    current_scope_record,current_epoch,uhead,lhead,current_source=p.resources.current_context()
    from .resource_run_ledger import dto_record
    material={'schema':'worldline.protected-original-workload-material-v1',
        'operation':operation,'original_request':scope.peer.observation(),
        'original_capture':archive(captured).hex(),'original_native_use':p._original_native_use(row),
        'world':clone(world.record()),'adapter':{'type':[type(adapter).__module__,type(adapter).__name__],
            'name':adapter.name,'executable_raw':os.fsencode(adapter.executable),
            'extra_argv':tuple(adapter.extra_argv),'mission_via_stdin':adapter.mission_via_stdin},
        'context':factual(context),'sandbox_spec':factual(spec),'sandbox_argv':argv,
        'mission_raw':mission_raw,'stdin_raw':stdin_raw,'stdin_close_required':True,
        'actual_mission_file':mission_path.read_bytes(),'actual_world_file':world_path.read_bytes(),
        'credential_projections':credentials,'selected_executable_files':actual_files,
        'project':{'generated':factual(project.generated),'checks':factual(project.checks),
            'services':factual(project.services),'protected':factual(project.protected),
            'source_sha256':project.source_sha256,'source_path':project.source_path,'source_raw':project_source},
        'global_config':clone(runner.config.value),'low_priority':low_priority,'timeout':timeout,
        'original_resource_policy':clone(runner.gate.policy.canonical()),
        'current_scope':dto_record(current_scope_record),'current_resource_epoch':current_epoch,
        'current_universe_head':uhead,'current_ledger_head':lhead,'complete_current_source':current_source,
        'actual_native_mapping':p.intact()}
    # Root-private durable factual intent precedes child reservation/dispatch.
    # Original result/use/chain state stays unchanged by this observation ACK.
    boundary={'name':'ORIGINAL_WORKLOAD_CAPTURE','material':archive(material).hex()}
    p.journal.append(operation,'ACK',captured,snapshot=row['snapshot'],native=row['native'],
        boundaries=row['boundaries']+[boundary])
    return {'material':material,'capture_id':identity(material).hex(),
        'event_id':p.journal.rows[operation]['event']}

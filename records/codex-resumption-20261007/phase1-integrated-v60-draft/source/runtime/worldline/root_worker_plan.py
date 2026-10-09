"""Exact owner-selected registered-handler command, not an actor mission.

The complete original request and workload stay in their original typed capture.
This plan selects only the privileged coordinator exec; the real handler consumes
that original request after current native/custody admission. No caller argv or
mission is substituted, and ordinary resource_launch_material remains intact.
"""
from pathlib import Path
from .protected_startup import require,private_bytes,digest
from .admission import ResourcePolicy
from .resource_run_ledger import dto_record

def handler_plan(owner,bound):
    from .protected_root_worker import RootWorkerFront,RootWorkerProcess
    require(type(owner) in (RootWorkerFront,RootWorkerProcess),
            'ROOT_PLAN_ACTUAL_FRONT_OR_WORKER_REQUIRED')
    source=owner.source_lease;source.check();plan=owner.plan
    components=plan['native_components']
    require(type(components) is dict and set(components)=={'systemctl','systemd_run','approved_loader'},
            'ROOT_PLAN_COMPLETE_EXECUTABLE_COMPONENTS_REQUIRED')
    interpreter=owner.spec['runtime']['interpreter']
    policy=ResourcePolicy.from_mapping(plan['worker_policy'])
    require(policy.enforcement=='cgroup2','ROOT_PLAN_ORIGINAL_ENFORCED_POLICY_REQUIRED')
    selected={}
    for path,role in ((interpreter,'INTERPRETER'),(components['approved_loader'],'SOURCE'),
                      (plan['entry'],'SOURCE'),(plan['helper'],'EXECUTABLE'),
                      (components['systemctl'],'EXECUTABLE'),(components['systemd_run'],'EXECUTABLE')):
        raw=source.file(path,(role,));require(raw==private_bytes(path),'ROOT_PLAN_SELECTED_EXECUTABLE_CHANGED')
        selected[path]=digest(raw)
    # The C helper appends only its sole real custody FD. That FD is not a
    # request, operation, workload or an authority value.
    argv=[interpreter,'-I','-S','-B',components['approved_loader'],
          '--bootstrap-envelope',plan['early_envelope'],'--entry',plan['entry'],
          str(owner.lease.descriptor_path)]
    source.file(plan['early_envelope'],('DATA',))
    return {'bound':dto_record(bound),'argv':argv,'cwd':owner.spec['paths']['state'],
            'environment':{},'systemd_properties':policy.unit_properties(),
            'policy':policy.canonical(),'executables':selected}

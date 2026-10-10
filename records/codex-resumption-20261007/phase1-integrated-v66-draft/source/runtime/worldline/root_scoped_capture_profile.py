"""Original full scoped inputs and factual raw projection preimages.

Nothing here classifies or authorizes. Native source projection joins these
actual full bytes/records to every original input and redecides each classifier.
"""
from .protected_startup import require

DOMAIN='worldline.complete-scoped-capture-source-v1'


def current_projection(producer,before,current,source,catalogue,root_value,root_json,catalogue_json):
    from . import resource_scoped_run_ledger as S
    from .protected_resource_runtime import canonical
    from .scoped_capture_history_source import capture_history_owner
    from .protected_scoped_resource_service import snapshot_record
    return {'schema':DOMAIN,'before':before,'before_json':canonical(snapshot_record(before)),
        'before_values':{name:getattr(before,name) for name in before.__dataclass_fields__},
        'current':current,'source':source,
        'source_scoped':S.record(source),'source_json':canonical(S.record(source)),
        'root_value':root_value,'root_json':root_json,'catalogue':catalogue,
        'catalogue_json':catalogue_json,'catalogue_encoded':producer.scoped_service.cfg['catalogue'],
        'gate_config':producer.gate.config,'binding':producer.binding,
        'binding_json':canonical(producer.binding),'resource_config':producer.cfg,
        'history_owner':capture_history_owner(producer)}


def capture_profile(producer,packet,sources,classifications,materials,roster=None):
    from . import resource_scoped_run_ledger as S
    require(type(packet) is S.ScopedPacket and len(packet.rows)==len(packet.facts)==len(packet.observed)
        ==len(sources)==len(classifications)==len(materials),'SCOPED_RAW_FULL_ROW_CORRESPONDENCE_REQUIRED')
    projection=producer.scoped_projection
    require(projection['current']==packet.current,'SCOPED_RAW_ACTUAL_CURRENT_SOURCE_CHANGED')
    return {'schema':DOMAIN,'packet':packet,'scoped_projection':projection,
        'rows':tuple({'row':row,'physical':fact,'observed':observed,'source':source,
            'native_classification':native,'classification_material':material}
            for row,fact,observed,source,native,material in zip(packet.rows,packet.facts,packet.observed,
                sources,classifications,materials)),
        'inventory':None if roster is None else roster.intact()}


def capture_retained_scoped(owner,seed,*,custody_connection=None,owner_state=None):
    """Read escrow after target owners close; never reopen semantic owners.

    The actual complete raw owner SQL capture accompanies the original retained
    context. The native owner/current/source relation must join it, rather than
    credit Python equality or infer a current context from recorded LIVE facts.
    """
    from .root_owned_descriptor_roster import OwnedDescriptorRoster
    from .root_worker_current_state import capture_startup_owner_state
    from . import resource_scoped_run_ledger as S
    roster=owner.custody.owned_roster if getattr(owner,'custody',None) is not None else seed['roster']
    require(type(roster) is OwnedDescriptorRoster and type(seed['packet']) is S.ScopedPacket,
        'SCOPED_RAW_GENUINE_RETAINED_DESCRIPTOR_OWNER_REQUIRED')
    state=owner_state if owner_state is not None else capture_startup_owner_state(
        owner,custody_connection=custody_connection)
    from .scoped_capture_owner_projection import selected_owner_files
    if 'selected_files' not in state:state['selected_files']=selected_owner_files(owner)
    packet,captured=roster.recapture(owner,seed['packet'],state)
    source=owner.source_lease.check()
    from .scoped_capture_history_source import capture_receiver_history_owner
    from .scoped_capture_owner_projection import capture_retained_owner_sql_projection
    projection=dict(seed['scoped_projection'])
    projection['history_owner']=capture_receiver_history_owner(owner,state,roster)
    projection['owner_sql_source']=capture_retained_owner_sql_projection(owner,projection,state)
    captured['scoped_projection']=projection;captured['owner_state']=state
    from .protected_root_worker import RootWorkerIntake
    core=owner.core if type(owner) is RootWorkerIntake else owner.principal.core
    return {'material':packet,'observation':S.ScopedRunLedgerKernel(core).validate(packet),
        'source':source,'scoped_source':projection['source'],
        'physical':tuple(row['source'] for row in captured['rows']),
        'classification':tuple(row['native_classification'] for row in captured['rows']),
        'classification_material':tuple(row['classification_material'] for row in captured['rows']),
        'owned_descriptor_roster':captured,'owner_state':state}

def capture_for_owner(owner,*,custody_connection=None,owner_state=None):
    from .protected_root_observation import RootControllerCapture
    capture=getattr(owner,'_root_capture',None)
    require(type(capture) is RootControllerCapture and capture.owner is owner
        and capture.material is not None and capture.provenance is not None,
        'SCOPED_RAW_LATEST_ACTUAL_ROOT_CAPTURE_REQUIRED')
    return capture_retained_scoped(owner,{'packet':capture.material['packet'],
        'scoped_projection':capture.provenance['owned_descriptor_roster']['scoped_projection'],
        'roster':capture.owned_roster},custody_connection=custody_connection,owner_state=owner_state)

def capture_for_intake(owner,*,custody_connection=None,owner_state=None):
    from .protected_root_worker import RootWorkerIntake
    require(type(owner) is RootWorkerIntake and owner.custody.frame is owner.frame,
        'SCOPED_RAW_ACTUAL_CONSTRUCTOR_FREE_INTAKE_REQUIRED')
    seed=owner.custody.frame['root_native']
    return capture_retained_scoped(owner,{'packet':seed['material']['packet'],
        'scoped_projection':seed['provenance']['owned_descriptor_roster']['scoped_projection'],
        'roster':owner.custody.owned_roster},custody_connection=custody_connection,owner_state=owner_state)


def bind_owner_source(producer,profile,owner_state):
    from .scoped_capture_owner_projection import capture_owner_sql_projection
    projection=dict(profile['scoped_projection'])
    projection['owner_sql_source']=capture_owner_sql_projection(producer,owner_state)
    profile['scoped_projection']=projection;profile['owner_state']=owner_state
    return profile


def capture_live_scoped(producer,packet,sources,decisions,materials,owner,*,custody_connection=None,owner_state=None):
    from .protected_root_worker import RootWorkerFront,RootWorkerProcess
    from .root_owned_descriptor_roster import OwnedDescriptorRoster
    from .root_worker_current_state import capture_startup_owner_state
    from . import resource_scoped_run_ledger as S
    require(type(owner) in (RootWorkerFront,RootWorkerProcess) and owner.principal.resources is producer,
        'SCOPED_RAW_ACTUAL_LIVE_OWNER_REQUIRED')
    state=owner_state if owner_state is not None else capture_startup_owner_state(
        owner,custody_connection=custody_connection)
    from .scoped_capture_owner_projection import selected_owner_files
    if 'selected_files' not in state:state['selected_files']=selected_owner_files(owner)
    retained=(getattr(owner,'_root_capture',None) if type(owner) is RootWorkerFront else None)
    retained=None if retained is None else retained.owned_roster
    if retained is None and type(owner) is RootWorkerProcess:retained=owner.custody.owned_roster
    roster=(OwnedDescriptorRoster.capture(owner,packet,sources) if retained is None else
        OwnedDescriptorRoster.refresh(owner,packet,sources,retained))
    try:
        current,captured=roster.recapture(owner,packet,state)
        captured['scoped_projection']=producer.scoped_projection
        bind_owner_source(producer,captured,state)
        return {'material':current,'observation':producer.scoped_kernel.validate(current),
            'source':owner.source_lease.check(),'scoped_source':captured['scoped_projection']['source'],
            'physical':tuple(item['source'] for item in captured['rows']),
            'classification':tuple(item['native_classification'] for item in captured['rows']),
            'classification_material':tuple(item['classification_material'] for item in captured['rows']),
            'complete_scoped_capture':captured,'owner_state':state,'roster':roster}
    except BaseException:
        roster.close()
        raise

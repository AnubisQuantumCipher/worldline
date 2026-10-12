"""Exec-only selected entry; no ordinary imports before the approved loader."""
import sys
_source=sys.modules.get('_worldline_approved_source_loader')
if _source is None:
    raise RuntimeError('ROOT_WORKER_EARLY_SOURCE_LEASE_REQUIRED')
_source.current().check()

def main():
    import asyncio,os,socket
    from pathlib import Path
    from worldline.protected_startup import StartupLease,require
    from worldline.protected_root_worker import RootWorkerIntake,RootWorkerProcess
    from worldline.root_worker_custody import CustodyReceipt
    from worldline.protected_operations import CanonicalOperationPrincipal
    from worldline.protected_scoped_resource_runtime import ProtectedScopedResourcePrincipal
    from worldline.daemon import WorldlineDaemon
    from worldline.status import StatusPublisher
    require(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
        and len(sys.argv)==3 and os.geteuid()==0,'ROOT_WORKER_EXACT_OPERATOR_ENTRY_REQUIRED')
    descriptor=Path(sys.argv[1]);word=sys.argv[2]
    require(word.isascii() and word.isdigit() and str(int(word))==word,
            'ROOT_WORKER_ACTUAL_CUSTODY_DESCRIPTOR_REQUIRED')
    channel=socket.socket(fileno=int(word))
    intake=RootWorkerIntake(descriptor)
    custody=CustodyReceipt.receive(channel,intake.authority)
    lease=StartupLease(descriptor,custody=custody)
    lease.construct()
    resources=lease.resource_principal
    require(type(resources) is ProtectedScopedResourcePrincipal and resources.lease is lease,
            'ROOT_WORKER_ACTUAL_FULL_SCOPED_STARTUP_ATTACHMENT_REQUIRED')
    principal=lease.canonical_operation_principal
    require(type(principal) is CanonicalOperationPrincipal and principal.lease is lease
        and principal.resources is resources,'ROOT_WORKER_ORIGINAL_STARTUP_PRINCIPAL_REQUIRED')
    daemon=WorldlineDaemon(lease.controller.paths,lease.store,StatusPublisher(lease.controller.paths,lease.store))
    lease.controller.register(daemon)
    worker=RootWorkerProcess(custody,lease,principal,daemon)
    # Before ACK, actual source/native/grant/use/current/OFD and physical worker
    # join is redecided. An ACK transports custody, not an effect verdict.
    material=worker.capture_root_material(custody.frame,channel,custody.peer)
    native=worker.authority.decide(material)
    custody.bind_live_owner(worker,material,native)
    async def progress(event,data):
        request_id=worker.initial_request_admission['peer'].observation()['requestId']
        output=await worker.publish_initial_output('PROGRESS_BYTES',{'id':request_id,'event':event,'data':data})
        await worker._channel_method('send_original_progress',{'event':event,'data':data},worker_output=output)
    async def original():
        try:await worker.result_channel.commit_custody(material,native)
        except BaseException as error:
            await worker._retain_failed_operation(worker.operation,error)
            raise
        return await worker.run_original(progress)
    asyncio.run(original())
    # Collector owns full namespace ECHILD/outer wait and native historical
    # final resource settlement. No close in this entry invents that terminal.
    try:worker.relinquish_owners()
    except BaseException as error:
        asyncio.run(worker._retain_failed_operation(worker.operation,error))
        raise
    custody.close();channel.close()

if __name__=='__main__':main()

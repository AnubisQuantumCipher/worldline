"""Full original root roster staging; legacy one-mission fixture untouched.

Uses original Manifest capture/materialize, including its symlink/metadata/ACL
and repository semantics. Every registered root and original logical byte path
is retained; no private-evaluator tree/depth/byte cap is imported here.
Root custody, current writer quiescence and complete native correspondence are
required separately. Nothing creates a missing historical state or Genesis.
"""
import os,stat,hmac,hashlib,uuid
from pathlib import Path
from .manifest import Manifest
from .operation_capture import archive
from .protected_startup import private_bytes,protected,exact_json,canonical,require
from .protected_operations import clone,identity

DOMAIN=b'worldline-full-canonical-store-v1\0'
class FullCanonicalStore:
    def __init__(self,principal):
        self.p=principal;self.root=Path(principal.lease.spec['paths']['authority_root'])/'canonical'
        self.state_path=self.root/'full-domain-state.json';self.policy_path=self.root/'full-domain-policy.json'
        self.policy_raw=private_bytes(self.policy_path);self.policy=exact_json(self.policy_raw)
        require(set(self.policy)=={'schema','installation','store_genesis','universe_genesis','genesis','source_inventory','data','transactions','staging'}
            and self.policy['schema']=='worldline.full-canonical-policy-v1'
            and self.policy['installation']==principal.lease.spec['installation_id']
            and self.policy['store_genesis']==principal.store.get_meta('protectedStoreGenesis')
            and self.policy['universe_genesis']==principal.gate.universe.genesis_sha256,
            'FULL_CANONICAL_OWNER_CROSSWALK_CHANGED')
        self.data=self.root/'full-data';self.transactions=self.root/'full-transactions';self.staging=self.root/'full-staging'
        require(all(self.policy[name]==str(getattr(self,name)) for name in ('data','transactions','staging')),
            'FULL_CANONICAL_SELECTED_DIRECTORY_SPLIT')
        for path in (self.root,self.data,self.transactions,self.staging):protected(path,directory=True)
        self.raw=private_bytes(self.state_path);self.load()
    def mac(self,body):return hmac.new(self.p.gate.issuer.key,DOMAIN+canonical(body),'sha256').hexdigest()
    def load(self):
        env=exact_json(self.raw);require(set(env)=={'body','mac'} and hmac.compare_digest(env['mac'],self.mac(env['body'])),
            'FULL_CANONICAL_COMPLETE_STATE_AUTHENTICATION')
        body=env['body'];require(set(body)=={'schema','installation','genesis','worldline_store','universe_genesis','history'}
            and body['schema']=='worldline.full-canonical-state-v1'
            and body['installation']==self.policy['installation'] and body['genesis']==self.policy['genesis']
            and body['worldline_store']==self.policy['store_genesis']
            and body['universe_genesis']==self.policy['universe_genesis']
            and type(body['history']) is list and body['history'], 'FULL_CANONICAL_RETAINED_HISTORY_REQUIRED')
        # Full state history has a provisioned independent head requirement;
        # HMAC alone does not defeat privileged historical rollback.
        self.body=body
    def intact(self):
        self.p.intact();require(private_bytes(self.policy_path)==self.policy_raw
            and private_bytes(self.state_path)==self.raw,'FULL_CANONICAL_PROTECTED_PRIOR_CHANGED')
        for path in (self.root,self.data,self.transactions,self.staging):protected(path,directory=True)
    def _manifest(self,path,root):
        return self.p.controller.transactions._capture_payload(
            source=os.fsencode(path),logical=bytes(root['path']),root=root)
    def capture(self,mapping):
        self.intact();roots=self.p.store.roots();protected(mapping,directory=True)
        names={os.fsencode(name) for name in os.listdir(mapping)}
        expected={os.fsencode(root['root_key']) for root in roots}
        # Marker is carried as an independent complete byte input, never root
        # mapping/payload authority. Typed marker absence remains separate.
        marker=Path(mapping)/'.worldline-generation.json'
        if os.path.lexists(marker):names.remove(b'.worldline-generation.json')
        require(names==expected,'FULL_CANONICAL_COMPLETE_ROOT_ROSTER_CHANGED')
        manifests=[];mappings=[]
        for root in roots:
            slot=Path(mapping)/root['root_key'];info=slot.lstat()
            require(stat.S_ISLNK(info.st_mode),'FULL_CANONICAL_SLOT_NOT_SYMLINK')
            target=os.readlink(os.fsencode(slot));require(target.startswith(os.fsencode(self.root)+b'/'),
                'FULL_CANONICAL_SLOT_OUTSIDE_PROTECTED_ROOT')
            require(Path(os.fsdecode(target)).resolve().is_relative_to(self.root.resolve()),
                'FULL_CANONICAL_RESOLVED_SLOT_OUTSIDE_PROTECTED_ROOT')
            captured=self._manifest(target,root)
            manifests.append(captured);mappings.append({'root':clone(root),'link':target,
                'slot_stat':{'device':info.st_dev,'inode':info.st_ino,'mode':info.st_mode},
                'manifest':{'value':captured.value,'canonical':captured.canonical,'root_hash':captured.root_hash}})
        info=Path(mapping).stat()
        return {'mapping':{'device':info.st_dev,'inode':info.st_ino,'mode':info.st_mode},
            'roots':mappings,'root_set':Manifest.root_set_hash(manifests,self.p.core),
            'marker':None if not os.path.lexists(marker) else private_bytes(marker)}
    def stage(self,transaction):
        self.intact();tx=transaction['transactionId']
        require(uuid.UUID(hex=tx).hex==tx,
            'FULL_CANONICAL_TRANSACTION_ID_INVALID')
        original=self.p.controller.transactions._load_record(tx)
        require(archive(original)==archive(transaction),'FULL_CANONICAL_ACTUAL_TRANSACTION_CHANGED')
        source=self.p.controller.paths.transactions/tx/'payload'
        require(source==Path(transaction['stagingPayload']),'FULL_CANONICAL_SOURCE_PATH_SPLIT')
        destination=self.staging/tx;directory=self.transactions/tx;mapping=directory/'mapping'
        require(not os.path.lexists(destination) and not os.path.lexists(directory),
            'FULL_CANONICAL_PRIOR_STAGE_REQUIRES_RETAINED_INTENT_RECONCILIATION')
        roots=self.p.store.roots();require({p.name for p in source.iterdir()}=={r['root_key'] for r in roots},
            'FULL_CANONICAL_SOURCE_ROOT_ROSTER_CHANGED')
        # Caller persists complete STAGING_INTENT in its independent head CAS
        # before invoking stage. Partial directories remain for diagnosis.
        destination.mkdir(mode=0o700);directory.mkdir(mode=0o700);mapping.mkdir(mode=0o700)
        for root in roots:
            selected=source/root['root_key'];manifest=self.p.controller.transactions._capture_payload(
                source=os.fsencode(selected),logical=bytes(root['path']),root=root)
            Manifest.materialize(manifest,selected,destination/root['root_key'],core=self.p.core)
            os.symlink(os.fsencode(destination/root['root_key']),os.fsencode(mapping/root['root_key']))
        self.p.controller.transactions._fsync_payload_tree(destination)
        marker=canonical({'schemaVersion':1,'transactionId':tx})
        fd=os.open(mapping/'.worldline-generation.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        with os.fdopen(fd,'wb') as output:output.write(marker);output.flush();os.fsync(output.fileno())
        for selected in (mapping,directory,self.transactions,self.staging):
            fd=os.open(selected,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
            try:os.fsync(fd)
            finally:os.close(fd)
        result=self.capture(mapping)
        require(result['root_set']==transaction['stagedRoot'], 'FULL_CANONICAL_STAGED_ROOT_NATIVE_MISMATCH')
        return result

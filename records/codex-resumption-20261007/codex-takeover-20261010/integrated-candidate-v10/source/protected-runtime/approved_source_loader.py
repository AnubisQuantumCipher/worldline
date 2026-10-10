"""Early approved-source import lease for explicit protected operator entries.

Only built-in/frozen bootstrap imports precede install. The protected outer
launcher must bind their actual interpreter image, flags, entry/helper bytes and
pre-main file/cache immutability BEFORE Python starts. This module validates that
declared closure and controls future imports; it cannot retrospectively prove
the custody of initial execution, mapped ELF dependencies or native ctypes loads.
No descriptor, filename, successful import or lease is a protected authority.
"""
import sys
import builtins
import posix
import _io
import _stat
import _imp
import marshal
import _frozen_importlib as _boot
import _frozen_importlib_external as _external

_COMPILE=builtins.compile
_IMPORT=builtins.__import__
_EXEC=builtins.exec
_CODE=type((lambda:None).__code__)
_ACTIVE=None
_HEADER=b'WORLDLINE-APPROVED-SOURCE-ENVELOPE-V1\n'
_INITIAL_BOUNDARY='OUTER_PROTECTED_PRELAUNCH_INTERPRETER_BOOTSTRAP_AND_IMMUTABILITY_REQUIRED_NOT_ESTABLISHED_BY_THIS_LEASE'

class Refusal(RuntimeError):pass
def require(condition,reason):
    if not condition:raise Refusal(reason)
def _path(path):
    require(type(path) is str and path.startswith('/') and '\x00' not in path,'APPROVED_PATH_INVALID')
    require(path=='/' or all(part and part not in ('.','..') for part in path.split('/')[1:]),'APPROVED_PATH_NONCANONICAL')
    return path
def _parents(path):
    result=['/'];current=''
    for part in path.split('/')[1:-1]:
        current+='/'+part;result.append(current)
    return result
def _protected(path,*,directory=False,private=False):
    path=_path(path)
    for parent in _parents(path):
        info=posix.lstat(parent)
        require(_stat.S_ISDIR(info.st_mode) and info.st_uid==0 and not info.st_mode&0o022,'APPROVED_PARENT_UNPROTECTED')
    info=posix.lstat(path)
    require(info.st_uid==0 and not info.st_mode&0o022 and not _stat.S_ISLNK(info.st_mode),'APPROVED_PATH_UNPROTECTED')
    require(_stat.S_ISDIR(info.st_mode) if directory else _stat.S_ISREG(info.st_mode),'APPROVED_PATH_KIND')
    if private:require(not info.st_mode&0o077,'APPROVED_ENVELOPE_NOT_PRIVATE')
    return info
def _file_identity(info):
    return {'device':info.st_dev,'inode':info.st_ino,'mode':info.st_mode,
            'uid':info.st_uid,'gid':info.st_gid,'nlink':info.st_nlink,
            'size':info.st_size,'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns}
def _read(path,*,private=False,capture=None):
    named_before=_protected(path,private=private);named=named_before
    descriptor=posix.open(path,posix.O_RDONLY|posix.O_CLOEXEC|posix.O_NOFOLLOW)
    try:
        before=posix.fstat(descriptor)
        require(_stat.S_ISREG(before.st_mode) and before.st_uid==0 and before.st_nlink==1 and not before.st_mode&0o022,'APPROVED_OPEN_FILE_CUSTODY')
        require((named.st_dev,named.st_ino)==(before.st_dev,before.st_ino),'APPROVED_OPEN_FILE_REPLACED')
        with _io.FileIO(descriptor,'rb',closefd=False) as stream:raw=stream.readall()
        after=posix.fstat(descriptor);named=posix.lstat(path)
        require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns,before.st_mode)==
                (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns,after.st_mode),'APPROVED_FILE_CHANGED')
        require((named.st_dev,named.st_ino)==(after.st_dev,after.st_ino),'APPROVED_FILE_REPLACED')
        if capture is not None:
            capture[path]={'path':path,'raw_hex':raw.hex(),'private':private,
                           'named_before':_file_identity(named_before),
                           'held_before':_file_identity(before),'held_after':_file_identity(after),
                           'named_after':_file_identity(named)}
        return raw,_stat.S_IMODE(after.st_mode)
    finally:posix.close(descriptor)
def _unhex(raw):
    value=bytes.fromhex(raw.decode('ascii'))
    require(value.hex().encode('ascii')==raw,'APPROVED_NONCANONICAL_HEX');return value
def _text(raw):
    value=_unhex(raw).decode('utf-8');require(value.encode('utf-8')==_unhex(raw),'APPROVED_TEXT_ENCODING');return value
def _mode(raw):
    value=int(raw,8);require(format(value,'o').encode('ascii')==raw,'APPROVED_MODE_SPELLING');return value
def _same_constant(left,right):
    if type(left) is not type(right):return False
    if type(left) is _CODE:return _same_code(left,right)
    if type(left) is tuple:return len(left)==len(right) and all(_same_constant(a,b) for a,b in zip(left,right))
    # Constants come from compile/marshal, never eval or a caller object.
    if type(left) is frozenset:
        if len(left)!=len(right):return False
        remaining=list(right)
        for member in left:
            for index,candidate in enumerate(remaining):
                if _same_constant(member,candidate):remaining.pop(index);break
            else:return False
        return not remaining
    if type(left) in (float,complex):return marshal.dumps(left)==marshal.dumps(right)
    return left==right
def _same_code(left,right):
    if type(left) is not _CODE or type(right) is not _CODE:return False
    names=('co_argcount','co_posonlyargcount','co_kwonlyargcount','co_nlocals','co_stacksize','co_flags',
           'co_code','co_names','co_varnames','co_filename','co_name','co_qualname','co_firstlineno',
           'co_linetable','co_exceptiontable','co_freevars','co_cellvars')
    return all(getattr(left,n)==getattr(right,n) for n in names) and _same_constant(left.co_consts,right.co_consts)

def _held_bytes(descriptor):
    before=posix.fstat(descriptor)
    require(_stat.S_ISREG(before.st_mode),'APPROVED_PROJECTION_REGULAR_REQUIRED')
    with _io.FileIO(posix.dup(descriptor),'rb') as stream:
        stream.seek(0);raw=stream.readall()
    require(_file_identity(before)==_file_identity(posix.fstat(descriptor)) and
            len(raw)==before.st_size,'APPROVED_PROJECTION_CHANGED')
    return raw

def _proc_bytes(path):
    with _io.FileIO(path,'rb') as stream:return stream.readall()

def descriptor_facts(descriptor):
    info=posix.fstat(descriptor)
    return {'fd':descriptor,'device':info.st_dev,'inode':info.st_ino,'mode':info.st_mode,
            'uid':info.st_uid,'gid':info.st_gid,'size':info.st_size,
            'fdinfo_hex':_proc_bytes('/proc/self/fdinfo/'+str(descriptor)).hex()}

def held_projection_facts(descriptor,seals):
    before=descriptor_facts(descriptor);initial=seals()
    raw=_held_bytes(descriptor);after=descriptor_facts(descriptor)
    readback=_held_bytes(descriptor);final=descriptor_facts(descriptor)
    return {'fd':descriptor,'before':before,'after':after,'final':final,
            'raw_hex':raw.hex(),'readback_hex':readback.hex(),
            'seals_before':initial,'seals_after':seals()}

def process_facts(pid=None):
    """Actual proc observations, not enrolled RootWorker or principal claims."""
    pid=posix.getpid() if pid is None else pid
    require(type(pid) is int and pid>0,'APPROVED_ACTUAL_PROCESS_REQUIRED')
    base='/proc/'+str(pid)
    raw=_proc_bytes(base+'/stat');tail=raw[raw.rfind(b')')+2:].split()
    status=_proc_bytes(base+'/status')
    columns={parts[0]:[int(value) for value in parts[1:]]
             for line in status.splitlines() if (parts:=line.split()) and parts[0] in (b'Uid:',b'Gid:',b'Groups:')}
    namespaces={}
    for name in sorted(posix.listdir(base+'/ns')):
        path=base+'/ns/'+name;info=posix.stat(path)
        namespaces[name]={'link':posix.readlink(path),'device':info.st_dev,
                          'inode':info.st_ino,'mode':info.st_mode}
    return {'pid':pid,'start_tick':int(tail[19]),'stat_hex':raw.hex(),
            'boot_hex':_proc_bytes('/proc/sys/kernel/random/boot_id').hex(),
            'status_hex':status.hex(),'kernel_uid':columns[b'Uid:'],'kernel_gid':columns[b'Gid:'],
            'uid_map_hex':_proc_bytes(base+'/uid_map').hex(),
            'gid_map_hex':_proc_bytes(base+'/gid_map').hex(),
            'cmdline_hex':_proc_bytes(base+'/cmdline').hex(),
            'maps_hex':_proc_bytes(base+'/maps').hex(),
            'groups':posix.getgroups() if pid==posix.getpid() else columns[b'Groups:'],
            'real_uid':posix.getuid() if pid==posix.getpid() else columns[b'Uid:'][0],
            'real_gid':posix.getgid() if pid==posix.getpid() else columns[b'Gid:'][0],
            'resuid':list(posix.getresuid()) if pid==posix.getpid() else columns[b'Uid:'][:3],
            'resgid':list(posix.getresgid()) if pid==posix.getpid() else columns[b'Gid:'][:3],
            'exe':posix.readlink(base+'/exe'),'namespaces':namespaces}

class _SourceOwnerChannel:
    """One fixed acquisition/completion protocol; no path or read RPC."""
    def __init__(self,lease,descriptor,projection,endpoint_parent,deadline):
        # These imports execute under the actor's own freshly installed lease,
        # before delegation and before the irreversible credential drop.
        import socket,json,struct,array,fcntl,time
        self.socket,self.json,self.struct,self.array,self.fcntl,self.time=socket,json,struct,array,fcntl,time
        self.lease=lease;self.projection=projection;self.endpoint_parent=endpoint_parent
        self.deadline=deadline;self.sequence=0;self.stage='BOOTSTRAP';self.finished=False
        self.channel=socket.socket(fileno=descriptor)
        require(self.channel.family==socket.AF_UNIX and
                self.channel.getsockopt(socket.SOL_SOCKET,socket.SO_TYPE)==socket.SOCK_STREAM,
                'APPROVED_SOURCE_OWNER_CHANNEL_KIND')
        self.channel.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
        self.seals=fcntl.F_SEAL_SEAL|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_GROW|fcntl.F_SEAL_WRITE
        require(posix.fstat(projection).st_uid==0 and
                fcntl.fcntl(projection,fcntl.F_GET_SEALS)&self.seals==self.seals,
                'APPROVED_ROOT_SEALED_PROJECTION_REQUIRED')
        self.carrier_peer=self.channel.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('@iII')).hex()
        self.owner=None
        self.target=None;self._target_pending=None
    def _timeout(self):
        remaining=self.deadline-self.time.monotonic()
        require(remaining>0,'APPROVED_SOURCE_OWNER_ORIGINAL_DEADLINE')
        self.channel.settimeout(remaining)
    def _send(self,body):
        raw=self.json.dumps(body,ensure_ascii=True,separators=(',',':'),allow_nan=False).encode('ascii')
        fd=posix.memfd_create('worldline-selected-actor-observation',posix.MFD_CLOEXEC|posix.MFD_ALLOW_SEALING)
        try:
            with _io.FileIO(posix.dup(fd),'wb') as stream:
                require(stream.write(raw)==len(raw),'APPROVED_ACTOR_CAPTURE_WRITE_UNKNOWN')
            self.fcntl.fcntl(fd,self.fcntl.F_ADD_SEALS,self.seals)
            self._timeout()
            sent=self.channel.sendmsg([b'F'],[
                (self.socket.SOL_SOCKET,self.socket.SCM_RIGHTS,self.array.array('i',[fd])),
                (self.socket.SOL_SOCKET,self.socket.SCM_CREDENTIALS,
                 self.struct.pack('@iII',posix.getpid(),posix.getuid(),posix.getgid()))],
                self.socket.MSG_NOSIGNAL)
            require(sent==1,'APPROVED_ACTOR_CAPTURE_SEND_UNKNOWN')
        finally:posix.close(fd)
    def _receive(self):
        self._timeout();descriptors=[]
        try:
            body,controls,flags,_=self.channel.recvmsg(1,
                self.socket.CMSG_SPACE(self.array.array('i').itemsize)+
                self.socket.CMSG_SPACE(self.struct.calcsize('@iII')),self.socket.MSG_CMSG_CLOEXEC)
            credentials=[];malformed=False
            for level,kind,raw in controls:
                if (level,kind)==(self.socket.SOL_SOCKET,self.socket.SCM_RIGHTS):
                    rights=self.array.array('i');whole=len(raw)-len(raw)%rights.itemsize
                    rights.frombytes(raw[:whole]);descriptors.extend(rights);malformed|=whole!=len(raw)
                elif (level,kind)==(self.socket.SOL_SOCKET,self.socket.SCM_CREDENTIALS):
                    credentials.append(raw)
                else:malformed=True
            require(body==b'F' and not malformed and not flags&(self.socket.MSG_TRUNC|self.socket.MSG_CTRUNC)
                    and len(descriptors)==1 and len(credentials)==1
                    and len(credentials[0])==self.struct.calcsize('@iII'),'APPROVED_OWNER_REPLY_MALFORMED')
            fd=descriptors[0]
            require(posix.fstat(fd).st_uid==0 and
                    self.fcntl.fcntl(fd,self.fcntl.F_GET_SEALS)&self.seals==self.seals,
                    'APPROVED_OWNER_REPLY_NOT_ROOT_SEALED')
            raw=_held_bytes(fd);reply=self.json.loads(raw)
            require(set(reply)=={'schema','sequence','projection_hex','owner','native_action'}
                    and reply['schema']=='worldline.fixed-source-owner-reply-v1'
                    and reply['sequence']==self.sequence
                    and bytes.fromhex(reply['projection_hex'])==self.lease.envelope
                    and reply['native_action'] in (1,2),'APPROVED_OWNER_REPLY_SCOPE_CHANGED')
            owner=reply['owner'];pid,uid,gid=self.struct.unpack('@iII',credentials[0])
            # Carrier peer authenticates the unchanged creator/OWNER only;
            # actual dropped actor identity comes from each kernel SCM record.
            require((pid,uid,gid)==self.struct.unpack('@iII',bytes.fromhex(self.carrier_peer))
                    and pid==owner['pid'] and owner['pid']!=posix.getpid()
                    and uid==owner['real_uid'] and gid==owner['real_gid'],
                    'APPROVED_OWNER_REPLY_KERNEL_IDENTITY')
            require(self.owner is None or self.owner==owner,'APPROVED_SOURCE_OWNER_REPLACED')
            self.owner=owner
            return reply
        finally:
            for fd in descriptors:posix.close(fd)
    def acquire(self,source=None):
        require(not self.finished,'APPROVED_SOURCE_OWNER_ALREADY_COMPLETED')
        self.sequence+=1
        self._send({'schema':'worldline.fixed-source-actor-message-v1',
                    'sequence':self.sequence,'stage':self.stage,'kind':'ACQUIRE',
                    'source':self.lease.snapshot() if source is None else source,
                    'actor':process_facts(),'resuid':list(posix.getresuid()),
                    'resgid':list(posix.getresgid()),'groups':posix.getgroups(),
                    'channel':descriptor_facts(self.channel.fileno()),
                    'projection':descriptor_facts(self.projection),
                    'endpoint_parent':descriptor_facts(self.endpoint_parent),
                    'target':self.target,
                    'carrier_peer_hex':self.carrier_peer,'terminal':None})
        if self._target_pending is not None:
            descriptor=self._target_pending;self._target_pending=None;self._timeout()
            sent=self.channel.sendmsg([b'F'],[
                (self.socket.SOL_SOCKET,self.socket.SCM_RIGHTS,self.array.array('i',[descriptor])),
                (self.socket.SOL_SOCKET,self.socket.SCM_CREDENTIALS,
                 self.struct.pack('@iII',posix.getpid(),posix.getuid(),posix.getgid()))],
                self.socket.MSG_NOSIGNAL)
            require(sent==1,'APPROVED_ACTUAL_TARGET_DESCRIPTOR_SEND_UNKNOWN')
        return self._receive()
    def ready(self):
        self.stage='ACTOR';self.lease.check()
    def finish(self,terminal):
        self.sequence+=1
        self._send({'schema':'worldline.fixed-source-actor-message-v1',
                    'sequence':self.sequence,'stage':self.stage,'kind':'COMPLETE',
                    'source':self.lease.snapshot(),'actor':process_facts(),
                    'resuid':list(posix.getresuid()),'resgid':list(posix.getresgid()),
                    'groups':posix.getgroups(),'channel':descriptor_facts(self.channel.fileno()),
                    'projection':descriptor_facts(self.projection),
                    'endpoint_parent':descriptor_facts(self.endpoint_parent),
                    'target':self.target,
                    'carrier_peer_hex':self.carrier_peer,'terminal':terminal})
        self._receive();self.finished=True
    def endpoint(self,original):
        # A directory capability bypasses inaccessible *ancestors*, not this
        # selected directory's execute or the original socket's connect rights.
        require(_stat.S_ISDIR(posix.fstat(self.endpoint_parent).st_mode),'APPROVED_ENDPOINT_DIRECTORY_REQUIRED')
        return '/proc/self/fd/'+str(self.endpoint_parent)+'/'+original.rsplit('/',1)[1]
    def observe_target(self,channel,original):
        require(self.stage=='ACTOR' and self.target is None,'APPROVED_POST_DROP_TARGET_ONLY')
        self.target={'original':_path(original),'connected_path':self.endpoint(original),
                     'descriptor':descriptor_facts(channel.fileno()),
                     'domain':channel.getsockopt(self.socket.SOL_SOCKET,self.socket.SO_DOMAIN),
                     'type':channel.getsockopt(self.socket.SOL_SOCKET,self.socket.SO_TYPE),
                     'server_credentials_hex':channel.getsockopt(self.socket.SOL_SOCKET,self.socket.SO_PEERCRED,
                                                               self.struct.calcsize('@iII')).hex(),
                     'peername':channel.getpeername(),'actor':process_facts(),
                     'resuid':list(posix.getresuid()),'resgid':list(posix.getresgid()),
                     'groups':posix.getgroups()}
        self._target_pending=channel.fileno();self.lease.check()

class ApprovedSourceLease:
    """Process-local executed-code observation/control, never native authority."""
    def __init__(self,envelope_path,helper_path,*,projection_fd=None):
        require(posix.geteuid()==0 and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,'APPROVED_ROOT_I_S_B_REQUIRED')
        self.envelope_path=_path(envelope_path);self.helper_path=_path(helper_path)
        self._projection_fd=projection_fd;self._owner=None;self._completion=None
        self._readbacks={}
        self.envelope=(_read(self.envelope_path,private=True,capture=self._readbacks)[0] if projection_fd is None
                       else _held_bytes(projection_fd))
        require(self.envelope.startswith(_HEADER) and self.envelope.endswith(b'\n'),'APPROVED_ENVELOPE_HEADER')
        self.files={};self.absent=set();self.directories={};self.builtins=set();self.frozen=set();self.flags={};self.events=[];self.refusals=[]
        for raw in self.envelope[len(_HEADER):].splitlines():
            parts=raw.split(b'\t');kind=parts[0]
            if kind==b'FILE':
                require(len(parts)==5,'APPROVED_FILE_RECORD');role=parts[1].decode('ascii');path=_path(_text(parts[2]))
                require(role in ('HELPER','ENTRY','INTERPRETER','EXECUTABLE','SOURCE','EXTENSION','CACHE','DATA') and path not in self.files and path not in self.absent,'APPROVED_DUPLICATE_FILE')
                self.files[path]=(role,_mode(parts[3]),_unhex(parts[4]))
                require(role!='EXECUTABLE' or self.files[path][1]&0o111,
                        'APPROVED_NATIVE_EXECUTABLE_MODE_REQUIRED')
            elif kind==b'ABSENT':
                require(len(parts)==2,'APPROVED_ABSENCE_RECORD');path=_path(_text(parts[1]))
                require(path not in self.files and path not in self.absent,'APPROVED_DUPLICATE_ABSENCE');self.absent.add(path)
            elif kind==b'DIRECTORY':
                require(len(parts)==3,'APPROVED_DIRECTORY_RECORD');path=_path(_text(parts[1]))
                require(path not in self.directories,'APPROVED_DUPLICATE_DIRECTORY');self.directories[path]=_mode(parts[2])
            elif kind in (b'BUILTIN',b'FROZEN'):
                require(len(parts)==2,'APPROVED_IMAGE_RECORD');name=_text(parts[1]);roster=self.builtins if kind==b'BUILTIN' else self.frozen
                require(name and name not in roster,'APPROVED_DUPLICATE_IMAGE_MEMBER');roster.add(name)
            elif kind==b'FLAG':
                require(len(parts)==3,'APPROVED_FLAG_RECORD');name=parts[1].decode('ascii')
                value=_text(parts[2])
                require(name not in self.flags,'APPROVED_DUPLICATE_FLAG');self.flags[name]=value
            else:raise Refusal('APPROVED_UNKNOWN_RECORD')
        require(set(self.flags)=={'optimize','cache_tag','magic','version'},'APPROVED_FLAGS_REQUIRED')
        require(self.flags=={'optimize':str(sys.flags.optimize),'cache_tag':sys.implementation.cache_tag,'magic':_external.MAGIC_NUMBER.hex(),'version':sys.version},'APPROVED_INTERPRETER_FLAGS_CHANGED')
        require([path for path,spec in self.files.items() if spec[0]=='HELPER']==[self.helper_path],'APPROVED_HELPER_SELECTION')
        self.interpreter=_path(posix.readlink('/proc/self/exe'))
        require([path for path,spec in self.files.items() if spec[0]=='INTERPRETER']==[self.interpreter],'APPROVED_INTERPRETER_SELECTION')
        self._source_type=_external.SourceFileLoader;self._extension_type=_external.ExtensionFileLoader
        self._file_finder_type=_external.FileFinder;self._path_finder=_external.PathFinder
        self._source_get_code=self._source_type.get_code;self._source_exec=self._source_type.exec_module
        self._extension_create=self._extension_type.create_module;self._extension_exec=self._extension_type.exec_module
        self._path_find=self._path_finder.find_spec.__func__
        self._file_find=self._file_finder_type.find_spec
        self._builtin_find=_boot.BuiltinImporter.find_spec.__func__;self._frozen_find=_boot.FrozenImporter.find_spec.__func__
        self._builtin_exec=_boot.BuiltinImporter.exec_module;self._frozen_exec=_boot.FrozenImporter.exec_module
        self._builtin_create=_boot.BuiltinImporter.create_module;self._frozen_create=_boot.FrozenImporter.create_module
        self._initial_modules=dict(sys.modules)
        self.check_files()
        self._initial_roster()
        lease=self
        def source_code(loader,fullname):
            lease.check_hooks();require(type(loader) is lease._source_type,'APPROVED_SOURCE_LOADER_TYPE')
            raw=lease.file(loader.path,('SOURCE','ENTRY','HELPER'))
            code=_COMPILE(raw,loader.path,'exec',dont_inherit=True,optimize=sys.flags.optimize)
            lease.events.append({'kind':'SOURCE_COMPILED_BEFORE_EXEC','module':fullname,'path':loader.path,'source_bytes_hex':raw.hex(),'cache_used':False})
            return code
        def extension_create(loader,spec):
            lease.check_hooks();require(type(loader) is lease._extension_type,'APPROVED_EXTENSION_LOADER_TYPE')
            raw=lease.file(loader.path,('EXTENSION',))
            lease.events.append({'kind':'EXTENSION_BEFORE_CREATE','module':spec.name,'path':loader.path,'bytes_hex':raw.hex(),'actual_mapping_custody':'OUTER_REQUIRED'})
            return lease._extension_create(loader,spec)
        def extension_exec(loader,module):
            lease.check_hooks();lease.file(loader.path,('EXTENSION',));return lease._extension_exec(loader,module)
        class Finder:
            def find_spec(self,fullname,path=None,target=None):
                lease.check_hooks()
                spec=_boot.BuiltinImporter.find_spec(fullname,path,target)
                if spec is not None:
                    require(fullname in lease.builtins,'APPROVED_BUILTIN_UNBOUND');return spec
                spec=_boot.FrozenImporter.find_spec(fullname,path,target)
                if spec is not None:
                    require(fullname in lease.frozen,'APPROVED_FROZEN_UNBOUND');return spec
                locations=list(sys.path if path is None else path)
                for location in locations:lease.directory_or_absent(location)
                spec=lease._path_finder.find_spec(fullname,path,target)
                if spec is None:return None
                if spec.loader is None:
                    require(spec.submodule_search_locations is not None,'APPROVED_SPEC_ABSENT')
                    for location in spec.submodule_search_locations:lease.directory_or_absent(location)
                    return spec
                require(type(spec.loader) in (lease._source_type,lease._extension_type),'APPROVED_UNSUPPORTED_EXECUTABLE_LOADER')
                require(spec.origin==spec.loader.path,'APPROVED_LOADER_ORIGIN_SPLIT')
                lease.file(spec.origin,('SOURCE',) if type(spec.loader) is lease._source_type else ('EXTENSION',))
                return spec
        self._new_source_code=source_code;self._new_extension_create=extension_create;self._new_extension_exec=extension_exec
        self._finder=Finder()
        self._path_hook=self._file_finder_type.path_hook((self._source_type,_external.SOURCE_SUFFIXES),(self._extension_type,_external.EXTENSION_SUFFIXES))
        self._source_type.get_code=source_code;self._extension_type.create_module=extension_create;self._extension_type.exec_module=extension_exec
        sys.meta_path[:]=[self._finder];sys.path_hooks[:]=[self._path_hook];sys.path_importer_cache.clear()
        def guarded_import(name,globals=None,locals=None,fromlist=(),level=0):
            lease.check_hooks();return _IMPORT(name,globals,locals,fromlist,level)
        self._guarded_import=guarded_import;builtins.__import__=guarded_import
        self.check_hooks()
    def file(self,path,roles):
        path=_path(path);require(path in self.files and self.files[path][0] in roles,'APPROVED_FILE_UNBOUND')
        role,mode,expected=self.files[path]
        if self._owner is not None:
            self._owner.acquire();return expected
        raw,actual_mode=_read(path,capture=self._readbacks)
        require(raw==expected and actual_mode==mode,'APPROVED_FILE_BYTES_OR_MODE_CHANGED');return raw
    def directory_or_absent(self,path):
        path=_path(path)
        if path in self.absent:
            self._absence(path);return
        require(path in self.directories,'APPROVED_IMPORT_DIRECTORY_UNBOUND')
        if self._owner is not None:
            self._owner.acquire();return
        require(_stat.S_IMODE(_protected(path,directory=True).st_mode)==self.directories[path],'APPROVED_DIRECTORY_MODE_CHANGED')
    def _absence(self,path):
        if self._owner is not None:
            require(path in self.absent,'APPROVED_ABSENCE_UNBOUND');self._owner.acquire();return
        for part in (*_parents(path),path):
            try:posix.lstat(part)
            except FileNotFoundError:return
            if part!=path:_protected(part,directory=True)
        raise Refusal('APPROVED_EXPECTED_ABSENCE_CHANGED')
    def check_files(self):
        if self._owner is not None:
            self._owner.acquire();return
        require((_read(self.envelope_path,private=True,capture=self._readbacks)[0] if self._projection_fd is None
                 else _held_bytes(self._projection_fd))==self.envelope,'APPROVED_ENVELOPE_CHANGED')
        for path,spec in self.files.items():self.file(path,(spec[0],))
        for path in self.absent:self._absence(path)
        for path in self.directories:self.directory_or_absent(path)
    def _cache_faithful(self,path,source_path,source):
        if path in self.absent:
            self._absence(path);return {'path':path,'present':False}
        raw=self.file(path,('CACHE',))
        _external._classify_pyc(raw,source_path,{'path':path})
        # CPython 3.14 _bootstrap_external documents the header as 16 bytes.
        # _compile_bytecode performs CPython's filename repair before comparison.
        cached=_external._compile_bytecode(memoryview(raw)[16:],name=source_path,bytecode_path=path,source_path=source_path)
        fresh=_COMPILE(source,source_path,'exec',dont_inherit=True,optimize=sys.flags.optimize)
        require(_same_code(cached,fresh),'APPROVED_INITIAL_CACHE_NOT_FAITHFUL')
        return {'path':path,'present':True,'bytes_hex':raw.hex(),'faithful_to_complete_source':True}
    def _initial_roster(self):
        for name,module in self._initial_modules.items():
            require(module is not None,'APPROVED_INITIAL_MODULE_NONE');spec=getattr(module,'__spec__',None)
            if module is sys.modules.get('__main__'):
                require(getattr(module,'__file__',None)==self.helper_path,'APPROVED_INITIAL_MAIN_UNBOUND')
                self.events.append({'kind':'INITIAL_HELPER_SOURCE','module':name,'path':self.helper_path,'bytes_hex':self.file(self.helper_path,('HELPER',)).hex(),'initial_execution_custody':_INITIAL_BOUNDARY});continue
            require(spec is not None,'APPROVED_INITIAL_SPEC_ABSENT')
            if spec.origin=='built-in':
                require(spec.name in self.builtins and spec.loader is _boot.BuiltinImporter,'APPROVED_INITIAL_BUILTIN_UNBOUND')
                self.events.append({'kind':'INITIAL_BUILTIN','module':name,'image_member':spec.name});continue
            if spec.origin=='frozen':
                require(spec.name in self.frozen and spec.loader is _boot.FrozenImporter,'APPROVED_INITIAL_FROZEN_UNBOUND')
                self.events.append({'kind':'INITIAL_FROZEN','module':name,'image_member':spec.name});continue
            require(type(spec.loader) is self._source_type and spec.origin==spec.loader.path and getattr(module,'__file__',None)==spec.origin,'APPROVED_INITIAL_SOURCE_LOADER_REQUIRED')
            raw=self.file(spec.origin,('SOURCE',))
            cache=_external.cache_from_source(spec.origin)
            require(getattr(module,'__cached__',None)==cache,'APPROVED_INITIAL_CACHE_PATH_SPLIT')
            candidates=[self._cache_faithful(cache,spec.origin,raw),self._cache_faithful(spec.origin[:-3]+'.pyc',spec.origin,raw)]
            self.events.append({'kind':'INITIAL_SOURCE_CANDIDATES','module':name,'path':spec.origin,'source_bytes_hex':raw.hex(),'cache_candidates':candidates,'initial_execution_custody':_INITIAL_BOUNDARY})
    def check_hooks(self):
        require(builtins.compile is _COMPILE and builtins.exec is _EXEC and builtins.__import__ is self._guarded_import,'APPROVED_BUILTINS_CHANGED')
        require(sys.meta_path==[self._finder] and sys.path_hooks==[self._path_hook],'APPROVED_IMPORT_HOOKS_CHANGED')
        require(self._source_type.get_code is self._new_source_code and self._source_type.exec_module is self._source_exec,'APPROVED_SOURCE_LOADER_CHANGED')
        require(self._extension_type.create_module is self._new_extension_create and self._extension_type.exec_module is self._new_extension_exec,'APPROVED_EXTENSION_LOADER_CHANGED')
        require(self._path_finder.find_spec.__func__ is self._path_find and _boot.BuiltinImporter.find_spec.__func__ is self._builtin_find and _boot.FrozenImporter.find_spec.__func__ is self._frozen_find,'APPROVED_FINDERS_CHANGED')
        require(self._file_finder_type.find_spec is self._file_find,'APPROVED_FILE_FINDER_CHANGED')
        require(_boot.BuiltinImporter.create_module is self._builtin_create and _boot.BuiltinImporter.exec_module is self._builtin_exec and _boot.FrozenImporter.create_module is self._frozen_create and _boot.FrozenImporter.exec_module is self._frozen_exec,'APPROVED_IMAGE_LOADERS_CHANGED')
        for finder in sys.path_importer_cache.values():require(finder is None or type(finder) is self._file_finder_type,'APPROVED_PATH_FINDER_CHANGED')
    def check(self):
        self.check_hooks();self.check_files()
        for location in sys.path:self.directory_or_absent(location)
        for name,module in tuple(sys.modules.items()):
            if module is None:continue
            if module in self._initial_modules.values():continue
            if module is sys.modules.get('__main__') or module is sys.modules.get('_worldline_approved_source_loader'):continue
            spec=getattr(module,'__spec__',None);require(spec is not None,'APPROVED_FINAL_SPEC_ABSENT')
            if spec.origin=='built-in':require(spec.name in self.builtins and spec.loader is _boot.BuiltinImporter,'APPROVED_FINAL_BUILTIN_UNBOUND')
            elif spec.origin=='frozen':require(spec.name in self.frozen and spec.loader is _boot.FrozenImporter,'APPROVED_FINAL_FROZEN_UNBOUND')
            elif spec.origin is None and (spec.loader is None or type(spec.loader) is _external.NamespaceLoader):
                require(spec.submodule_search_locations is not None,'APPROVED_FINAL_NAMESPACE_ABSENT')
                for location in spec.submodule_search_locations:self.directory_or_absent(location)
            else:
                require(type(spec.loader) in (self._source_type,self._extension_type) and spec.origin==spec.loader.path and getattr(module,'__file__',None)==spec.origin,'APPROVED_FINAL_SOURCE_SPLIT')
                self.file(spec.origin,('SOURCE',) if type(spec.loader) is self._source_type else ('EXTENSION',))
                require(any(event.get('module')==spec.name and event.get('path')==spec.origin for event in self.events),'APPROVED_EXECUTED_MODULE_RECORD_ABSENT')
        return self.snapshot()
    def compile_source(self,path,logical_name):
        self.check_hooks();raw=self.file(path,('SOURCE','ENTRY'))
        code=_COMPILE(raw,path,'exec',dont_inherit=True,optimize=sys.flags.optimize)
        self.events.append({'kind':'EXPLICIT_SOURCE_COMPILED_BEFORE_EXEC','module':logical_name,'path':path,'source_bytes_hex':raw.hex(),'cache_used':False})
        return code
    def snapshot(self):
        # Full bytes are retained, not merely a digest or __file__ claim.
        return {'schema':'worldline.approved-executed-code-observation-v1','envelope_path':self.envelope_path,'envelope_bytes_hex':self.envelope.hex(),'helper':self.helper_path,'interpreter':self.interpreter,'interpreter_flags':dict(self.flags),'bootstrap_flags':{'isolated':bool(sys.flags.isolated),'no_site':bool(sys.flags.no_site),'dont_write_bytecode':bool(sys.dont_write_bytecode)},'events':[dict(event) for event in self.events],'file_readbacks':[dict(row) for row in self._readbacks.values()],'projection_readback':None if self._projection_fd is None or self._owner is None else held_projection_facts(self._projection_fd,lambda:self._owner.fcntl.fcntl(self._projection_fd,self._owner.fcntl.F_GET_SEALS)),'initial_execution_custody':_INITIAL_BOUNDARY,'actual_mapping_custody':'OUTER_REQUIRED','authority_or_phase_acceptance':False}
    def excluded_actor_ready(self):
        require(self._owner is not None,'APPROVED_EXCLUDED_ACTOR_OWNER_REQUIRED')
        self._owner.ready()
    def excluded_endpoint(self,original):
        require(self._owner is not None,'APPROVED_EXCLUDED_ACTOR_OWNER_REQUIRED')
        return self._owner.endpoint(_path(original))
    def excluded_target(self,channel,original):
        require(self._owner is not None,'APPROVED_EXCLUDED_ACTOR_OWNER_REQUIRED')
        self._owner.observe_target(channel,original)
    def excluded_actor(self):
        return self._owner is not None
    def owner_completion(self,completion):
        require(self._owner is None and self._completion is None and callable(completion),
                'APPROVED_SINGLE_ROOT_OWNER_COMPLETION_REQUIRED')
        self._completion=completion
    def run_entry(self,path,arguments):
        global _ACTIVE
        raw=self.file(path,('ENTRY',));self.check();code=_COMPILE(raw,path,'exec',dont_inherit=True,optimize=sys.flags.optimize)
        self.events.append({'kind':'ENTRY_COMPILED_BEFORE_EXEC','module':'__main__','path':path,'source_bytes_hex':raw.hex(),'cache_used':False})
        helper=sys.modules['__main__'];sys.modules['_worldline_approved_source_loader']=helper
        module=type(sys)('__main__');module.__file__=path;module.__builtins__=builtins.__dict__;sys.modules['__main__']=module
        sys.argv=[path,*arguments]
        try:_EXEC(code,module.__dict__)
        finally:
            try:self.check()
            except BaseException as error:
                if self._completion is not None:self._completion(None,error)
                if self._owner is not None:
                    try:self._owner.finish({'final_check':False,'exception':type(error).__name__,'message':str(error)})
                    except BaseException as transport:error.add_note('actor completion failed: '+repr(transport))
                raise
            if self._owner is not None:
                error=sys.exception()
                status=(0 if error is None else
                        (error.code if type(error) is SystemExit and type(error.code) is int else 1))
                self._owner.finish({'final_check':True,'exit_status':status,
                                    'exception':None if error is None or type(error) is SystemExit else type(error).__name__,
                                    'message':None if error is None or type(error) is SystemExit else str(error)})
            if self._completion is not None:self._completion(self.snapshot(),sys.exception())

def install(envelope_path,*,helper_path):
    global _ACTIVE
    require(_ACTIVE is None,'APPROVED_LEASE_ALREADY_INSTALLED')
    _ACTIVE=ApprovedSourceLease(envelope_path,helper_path);return _ACTIVE
def current():
    require(type(_ACTIVE) is ApprovedSourceLease,'APPROVED_EARLY_LEASE_REQUIRED');_ACTIVE.check_hooks();return _ACTIVE
def main(arguments):
    if arguments and arguments[0]=='--actor-source-owner':
        global _ACTIVE
        require(len(arguments)>=10 and arguments[4]=='--deadline' and arguments[6]=='--entry','APPROVED_ACTOR_LAUNCH_ARGUMENTS')
        descriptor,projection,endpoint_parent=map(int,arguments[1:4])
        require(arguments[5] and arguments[7],'APPROVED_ACTOR_LAUNCH_ARGUMENTS')
        require(_ACTIVE is None,'APPROVED_LEASE_ALREADY_INSTALLED')
        lease=ApprovedSourceLease('/proc/self/fd/'+str(projection),__file__,projection_fd=projection)
        _ACTIVE=lease
        owner=_SourceOwnerChannel(lease,descriptor,projection,endpoint_parent,float(arguments[5]))
        lease._owner=owner
        lease.run_entry(arguments[7],arguments[8:])
        return
    require(len(arguments)>=4 and arguments[0]=='--bootstrap-envelope' and arguments[2]=='--entry','APPROVED_LAUNCH_ARGUMENTS')
    lease=install(arguments[1],helper_path=__file__);lease.run_entry(arguments[3],arguments[4:])
if __name__=='__main__':
    try:main(sys.argv[1:])
    except Refusal as exc:
        print('APPROVED_SOURCE_REFUSED:'+str(exc),file=sys.stderr);raise SystemExit(1)

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
def _read(path,*,private=False):
    named=_protected(path,private=private)
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

class ApprovedSourceLease:
    """Process-local executed-code observation/control, never native authority."""
    def __init__(self,envelope_path,helper_path):
        require(posix.geteuid()==0 and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,'APPROVED_ROOT_I_S_B_REQUIRED')
        self.envelope_path=_path(envelope_path);self.helper_path=_path(helper_path)
        self.envelope,_=_read(self.envelope_path,private=True)
        require(self.envelope.startswith(_HEADER) and self.envelope.endswith(b'\n'),'APPROVED_ENVELOPE_HEADER')
        self.files={};self.absent=set();self.directories={};self.builtins=set();self.frozen=set();self.flags={};self.events=[];self.refusals=[]
        for raw in self.envelope[len(_HEADER):].splitlines():
            parts=raw.split(b'\t');kind=parts[0]
            if kind==b'FILE':
                require(len(parts)==5,'APPROVED_FILE_RECORD');role=parts[1].decode('ascii');path=_path(_text(parts[2]))
                require(role in ('HELPER','ENTRY','INTERPRETER','SOURCE','EXTENSION','CACHE','DATA') and path not in self.files and path not in self.absent,'APPROVED_DUPLICATE_FILE')
                self.files[path]=(role,_mode(parts[3]),_unhex(parts[4]))
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
        role,mode,expected=self.files[path];raw,actual_mode=_read(path)
        require(raw==expected and actual_mode==mode,'APPROVED_FILE_BYTES_OR_MODE_CHANGED');return raw
    def directory_or_absent(self,path):
        path=_path(path)
        if path in self.absent:
            self._absence(path);return
        require(path in self.directories,'APPROVED_IMPORT_DIRECTORY_UNBOUND')
        require(_stat.S_IMODE(_protected(path,directory=True).st_mode)==self.directories[path],'APPROVED_DIRECTORY_MODE_CHANGED')
    def _absence(self,path):
        for part in (*_parents(path),path):
            try:posix.lstat(part)
            except FileNotFoundError:return
            if part!=path:_protected(part,directory=True)
        raise Refusal('APPROVED_EXPECTED_ABSENCE_CHANGED')
    def check_files(self):
        require(_read(self.envelope_path,private=True)[0]==self.envelope,'APPROVED_ENVELOPE_CHANGED')
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
        return {'schema':'worldline.approved-executed-code-observation-v1','envelope_path':self.envelope_path,'envelope_bytes_hex':self.envelope.hex(),'interpreter':self.interpreter,'interpreter_flags':dict(self.flags),'events':[dict(event) for event in self.events],'initial_execution_custody':_INITIAL_BOUNDARY,'actual_mapping_custody':'OUTER_REQUIRED','authority_or_phase_acceptance':False}
    def run_entry(self,path,arguments):
        global _ACTIVE
        raw=self.file(path,('ENTRY',));self.check();code=_COMPILE(raw,path,'exec',dont_inherit=True,optimize=sys.flags.optimize)
        self.events.append({'kind':'ENTRY_COMPILED_BEFORE_EXEC','module':'__main__','path':path,'source_bytes_hex':raw.hex(),'cache_used':False})
        helper=sys.modules['__main__'];sys.modules['_worldline_approved_source_loader']=helper
        module=type(sys)('__main__');module.__file__=path;module.__builtins__=builtins.__dict__;sys.modules['__main__']=module
        sys.argv=[path,*arguments]
        try:_EXEC(code,module.__dict__)
        finally:self.check()

def install(envelope_path,*,helper_path):
    global _ACTIVE
    require(_ACTIVE is None,'APPROVED_LEASE_ALREADY_INSTALLED')
    _ACTIVE=ApprovedSourceLease(envelope_path,helper_path);return _ACTIVE
def current():
    require(type(_ACTIVE) is ApprovedSourceLease,'APPROVED_EARLY_LEASE_REQUIRED');_ACTIVE.check_hooks();return _ACTIVE
def main(arguments):
    require(len(arguments)>=4 and arguments[0]=='--bootstrap-envelope' and arguments[2]=='--entry','APPROVED_LAUNCH_ARGUMENTS')
    lease=install(arguments[1],helper_path=__file__);lease.run_entry(arguments[3],arguments[4:])
if __name__=='__main__':
    try:main(sys.argv[1:])
    except Refusal as exc:
        print('APPROVED_SOURCE_REFUSED:'+str(exc),file=sys.stderr);raise SystemExit(1)

with Worldline.Custody_V2_Load_Input;

--  Original protected_startup._installation, independently of operation heads
--  or a present startup journal. All observations are freshly acquired facts.
package Worldline.Startup_Installation with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   package V renames L.V;
   package S renames V.S;
   package E renames L.E;

   function Path_Bytes_Equivalent (Left, Right : E.Bytes) return Boolean
     with Global => null;
   function Path_Equivalent
     (Data : E.Bytes; Left, Right : E.Span) return Boolean
     with Global => null;
   function Joined_Path
     (Data : E.Bytes; Word, Base : E.Span; Suffix : String) return Boolean
     with Global => null;

   --  Roster is the original actual owner roster, not an operation principal.
   --  Roster.installation is the original spec; Roster.source is the genuine
   --  current ApprovedSourceLease.check() observation. Profile is the complete
   --  startup_admission profile in either runtime OwnedLoad or offline archive.
   --
   --  Profile.installation_inventory (scoped root_worker_codec archive):
   --    trees: list [{selector: original spec.trees key, path: actual Path(key),
   --                   identity: root lstat, entries: ALL fresh rglob entries}]
   --    files: list [regular entry + selector: original spec.files key]
   --    components: list [named directory entries for EVERY ancestor and root]
   --    interpreter: {path: actual readlink('/proc/self/exe')}
   --    interpreter_flags: {isolated: int, no_site: int,
   --                        dont_write_bytecode: bool}
   --    helper: source_lease.helper_path; helper_module: source_module.__file__;
   --    startup_module: protected_startup.__file__; environment_keys: sequence;
   --    tool_resolutions: dict [command -> actual strict-resolved which or None].
   --  Entry: {path, kind: 'DIRECTORY'|'REGULAR'|'SYMLINK'|'OTHER', identity,
   --          raw: bytes for REGULAR / None otherwise, link_target: str/None};
   --  tree entries additionally have relative: actual relative_to(root).as_posix.
   --  REGULAR entries additionally have held_identity, after_identity,
   --  named_after_identity, acquired from one O_NOFOLLOW descriptor read.
   --  Identity: {dev,inode,uid,gid,mode,nlink,size,mtime_ns,ctime_ns}, mode is
   --  actual full st_mode, never an asserted permission status. Installed files
   --  need not have nlink=1 or private mode: original inventory permits both.
   --  Empty directories, including __pycache__, are intentionally permitted.
   --  Source FILE envelope uses FULL path hex and FULL raw file hex; no digest
   --  substitutes for these bytes. selector stays raw while path is normalized.
   function Corresponds
     (Data : E.Bytes; Roster, Profile : E.Span) return Boolean
     with Global => null;

   --  Call Corresponds on both full snapshots before Stable. Directory
   --  timestamps/size may change during authorized journal creation, but their
   --  dev/inode/uid/gid/mode/nlink remain authority. Every installed regular
   --  file's complete raw bytes and all named/held identities remain fixed.
   function Stable
     (Before_Data, After_Data : E.Bytes;
      Before_Profile, After_Profile : E.Span) return Boolean
     with Global => null;
end Worldline.Startup_Installation;

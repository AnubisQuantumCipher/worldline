with SPARK.Big_Integers;
with Worldline.Custody_V2_Load_Input;
with Worldline.Custody_V2_Event_Joins;
with Worldline.Root_Custody_Phase_Values;
with Worldline.Custody_V2_Operation_Journal;
package Worldline.Custody_V2_Root_Evidence with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   package D renames Worldline.Custody_V2_Event_Joins.D;
   package M renames D.M;
   package Q renames D.Q;
   package P renames Worldline.Root_Custody_Phase_Values;
   use type L.Decode_Status;
   type Join_Status is (Evidence_Refused, Evidence_Joined);
   package E renames L.E;
   --  Total exact original signed integer projection; malformed is -1.
   --  Consumers MUST separately check V.Is_Integer before using equality.
   function Number (Data : E.Bytes; Item : E.Span)
      return SPARK.Big_Integers.Valid_Big_Integer with Global => null;
   function Cause_Class_Of (Value : L.Parsed_Input; Index : Q.Byte_Count)
      return M.Cause_Class with Global => null;
   --  Raw original fdinfo/stat parsers, with -1 for missing/ambiguous data.
   --  No liveness or ownership authority follows from parsing an integer.
   function Pidfd_Pid (Data : E.Bytes; Item : E.Span)
      return SPARK.Big_Integers.Valid_Big_Integer with Global => null;
   function Stat_Field (Data : E.Bytes; Item : E.Span; Field : Positive)
      return SPARK.Big_Integers.Valid_Big_Integer with Global => null;
   --  NEW source-only producer contract, not a claim about existing captures.
   --  x5.root_evidence is BYTES(raw_archive(full profile)); its decoded owned
   --  ORIGINAL image has schema "worldline.custody-root-raw-v1".
   --  x5.native_observations is likewise BYTES(raw_archive(full native tuple)).
   --  Load_Input owns both decoded images. Never use outer BYTES offsets as
   --  observation spans or reinterpret byte-key dictionaries as scoped DTOs.
   --  Common: source (full source_lease.check()), actor (full actor_identity),
   --  request (original RequestPeer.observation()), use (full original native
   --  use), captures (role, provenance pairs matching native_observations),
   --  operation_journal_envelope (full original decoded body/mac envelope),
   --  owner_before/owner_current (complete capture_owner_state), locks (below).
   --  Every native role retains the actual full material/observation/provenance.
   --  Provenance is the complete owned_descriptor_roster or direct complete
   --  scoped capture: packet, rows, scoped_projection, inventory, owner_state.
   --  Scoped_Capture_Projection conjoins complete original native root/scoped
   --  material, current source, owner SQL and every physical/history/absence row.
   --  Running/settlement committed operands also retain this actual provenance.
   --  Every retained reference below is TEXT event_id strictly before Index.
   --  Root events bind their own operation/generation. ECR consumers bind the
   --  root Before.Operation/Generation, independently of subject own operations.
   --
   --  Syscall receipt: {call,args,result,errno,source}; args is a full dict of
   --  original arguments, result/errno signed native integers. Local receipts
   --  bind common source; receiver OFD receipts bind the independently matched
   --  actual sender broker source/actor/host worker PIDFD. No allowed/Ready/
   --  closed/gone/verdict Boolean is authority.
   --  Identity: complete original identity(fd), including fdinfo. Named inode
   --  matches use device/inode/mode/uid/gid; OFD matches require kcmp syscall
   --  (KCMP_FILE=0, result=0) and LOCK_EX|LOCK_NB flock (operation=6,result=0).
   --  locks is the complete ordered tuple {path,origin,current,named,ofd,flock,
   --  open,current_acquisition,named_open,named_close,duplicates,receiver_ofd,
   --  sender_role_roster}. current_acquisition retains the genuine fresh
   --  constructor dup from the original escrow FD with its full at-time proof.
   --  Every owner_before.held_locks row joins; named inode probes are distinct
   --  from held acquisitions. Full raw transfer.roster joins authenticated
   --  TRANSFER_SENT.frame.subject_custody.roles, transfer.roles and broker.
   --  root_roles. Unchanged request original.socket_roster is not this roster.
   --  The scoped/ subset separately joins inventory.frame.original_roles,
   --  inventory.roles and broker.roles. ALL raw streams, rights and controls
   --  join actual send/receive receipts; listener errors remain raw observations,
   --  never silently reinterpreted as connected RequestPeer socket failures.
   --  Namespace-source native SCM projection binds host/namespace credentials,
   --  the actual original root frame and authenticated EXECUTION_NATIVE record.
   --  Fresh ECR retains authentic old open -> offer dup -> current escrow FD:
   --  TRANSFER_SENT.transfer.duplicates has {receipt,ofd}; each dup retains its
   --  full before-FD inventory, actual readbacks and positive at-time KCMP_FILE.
   --  Root closes do not license an invented post-close OFD measurement.
   --
   --  Per-event operands:
   --  prepared: {reserved,intent} full original op-journal events.
   --  held: full original HELD record; machine: actual original machine
   --  admission native tuple; running: committed full scoped resource event.
   --  HELD also retains helper_pidfd_origin=identity(actual original helper
   --  pidfd), independently joined by Closed_Outer with the selected manager.
   --  execution: {material,observation,provenance,before_exec}; original
   --  measured/process/request bind before_exec exactly. ack retains
   --  execution_event/request/ticket/peer/frame/measured_frame/witness_raw/
   --  witness/send/receive. The original committed event id and measurement
   --  bytes bind the actual prior native execution. Receive retains the raw
   --  WL-ROOT-WORKER-ACK-RECEIPT-v1 transport plus actual SCM credentials,
   --  original worker PIDFD and live host process context; actor and receiver
   --  need not inhabit the same PID namespace.
   --  Execution additionally retains worker_pidfd_origin=identity(actual
   --  original worker pidfd); ECR must join that retained descriptor inode.
   --  handoff: full original custody frame; quiescence: {background,
   --  acquisitions}, complete lists; acquisition rows retain active intervals.
   --  owners_closed: complete ordered {owner,close} roster, not a closed flag.
   --  seed: complete original post-close owner snapshot plus prefix event ids.
   --  transfer: complete actual frame/actual_send and descriptor/send receipts;
   --  roster: complete actual received identities plus kcmp/flock receipts.
   --  Its Front writer retains receiver_report={report,event,raw,transport};
   --  report.original carries complete_received_roster/sender_transcript/
   --  sender_role_roster; report.evidence/native bind the actual receiver
   --  observations and whole original event. SCM sender host PID is joined to
   --  broker.worker_host_pid and original PIDFD fdinfo, not namespace PID.
   --  abort: {launch_journal,classification,release}, full original records.
   --  report: {event,raw,sender_credentials,worker,request,use,channel,receive},
   --  event is original immutable result/progress/terminal, not child result.
   --  terminal: original owner_state/native_event/original_native_use/value.
   --  DISTINCT failed closed witness: failure_schema is exactly
   --  worldline.failed-root-physical-closure-v1. Its actual failure_event is
   --  HANDOFF_ABORT or FRONT_RETAINED_ESCROW; execution_event and handoff_intent
   --  are authenticated same-generation prior native events. No Custody_ACK,
   --  ORIGINAL_RESULT or HANDLER_TERMINAL may exist in that root interval.
   --  failure_owner_state is the authenticated failure raw owner_current;
   --  original_request/use/root_native come from that actual HANDOFF_INTENT.
   --  The original complete CLOSED_NS/OUTER/RAW, full REAPED/validate captures
   --  and Closed_State.Matches remain mandatory. A Python failure flag, stop
   --  return, socket EOF or unknown partial send cannot admit this branch.
   --  relinquish: {owners_closed,native_event,owner_state}.
   --  reattach: {hello,challenge,proof,ready,worker,channel,peer};
   --  each message {body,mac}; body is original scoped dict carrying operation,
   --  generation, nonce_f/nonce_w and epochs; MAC covers exact original archive
   --  bytes under worldline.root-worker-reattach-v1 + NUL, original owner key.
   --  No key is retained inside root_evidence.
   --
   --  ecr: {regime,held_event,execution_event,worker,namespace_init,locks}.
   --  regime "front-live": each process {recorded,origin,current,poll}; origin
   --  is the held original pidfd identity; current exact same inode; poll args
   --  {fd,events=25,timeout=0}, result=1, revents in {1,16,17}, errno=0.
   --  Known-live cleanup uses successful empty poll (result=0,revents=0) of
   --  that same retained inode and fdinfo PID, never NOT(worker_gone).
   --  regime "front-restart": each process {recorded,current_boot,pidfd_open,
   --  pidfd_info,stat,poll}; recorded is {boot,pid,start_tick}. Absence is ONLY
   --  different boot, pidfd_open(pid,0)=-1/ESRCH(3), or fdinfo/stat pid match
   --  plus different start_tick while the fresh pidfd poll remains live.
   --  Namespace init also admits original init_exited_at_held with actual
   --  HELD poll terminal. Restart additionally needs actual exclusive flock on
   --  EVERY original transferred lock, authentic acquisition/escrow lineage,
   --  and separately captured named open/fstat/close identity.
   --
   --  Worker self liveness retains namespace_context={actor,host_proc,
   --  host_proc_fd,execution_event,execution,reads}; reads binds exact host-mount
   --  openat paths, read chunks through EOF and close for pidfd_info and stat.
   --  Fresh self pidfd_open uses actual namespace PID; authenticated EXEC binds
   --  host PID/start tick independently; the actual pidfd_close also joins.
   --  closed_ns: {held_event,frame,namespace_wait,ack}; original CLOSED/ECHILD
   --  exact ticket/init/wait-status frame, terminal same held namespace pidfd,
   --  actual successful send(b"A"). closed_outer: {namespace_event,
   --  helper_wait,launcher_wait,manager,namespace_wait}; raw manager stdout
   --  must contain the selected unit, invocation/cgroup and MainPID=0.
   --  closed_raw: {streams,result}; streams contains stdout AND stderr,
   --  each {stream,bytes,raw,identity,path,eof,fsync}, complete raw immutable
   --  bytes and actual read result zero/fsync result zero.
   --  witness: full original closed proof packet/classification_input/native/
   --  consistent/physical/original_row/terminal/terminal_transport/owned_closed/
   --  outer_wait/complete_raw/original_use/original_request/complete history.
   --  witness.actual_state_correspondence={before,current}: before is the
   --  authenticated full HANDLER_TERMINAL.record.value.owner_state, current the
   --  actual unchanged fresh owner state. Cached Join invokes Closed_State.
   --  Matches once over both full raw states, complete Source_Input prefix and
   --  held actual Value.Key. Both original v1 chains retain all fourteen kinds;
   --  complete v1/v2 native history/HMAC/state joins are independently redecided.
   --  No key is copied into evidence. The read-only Closed_Proof_Reference used
   --  before reconstruction imposes no phase/Legal prerequisite.
   --  settlement: original committed scoped Record_Terminal then Release_Hold
   --  or Charge_Budget events; historical: original U operation event/result.
   --  reconstruction: fresh complete StartupLease owner capture and escrow
   --  claim receipts; front_owned: old_end/new_owner complete capture.
   --
   --  cause is primitive_inputs.unknown_cause, complete scoped dictionary:
   --  {class,operation,generation,source,raw}. CChannel raw is failed transport
   --  receipt; CDeadline raw is {clock,deadline,channel,worker}; CAppend raw is
   --  {append,failed_event,record}: append is BYTES of the full original
   --  capture_uncertainty(), record is actual scoped stored-wrapper bytes.
   --  append_uncertainty in this raw profile is the complete decoded original
   --  capture: before/input/candidate/actor/native_delta/attempted_event/
   --  applied_rows and complete actual exception including args/notes and
   --  nullable errno/SQLite metadata. No manufactured OS errno or status DTO.
   --  failed_event is the full original replay tuple plus exact record digest.
   --  A remote Worker CAppend retains worker_report={event,raw,transport,worker,
   --  worker_actor,worker_pidfd,execution_event}; original wire event/raw/sealed
   --  received memfd/SCM/host worker PIDFD/native EXEC measurements all join.
   --  A queued report may outlive the Worker: actual live OR terminal poll is
   --  retained, not transformed into cleanup permission. Failed subject op/gen
   --  remain the actual attempted event's; root Before.Operation stays starter.
   --  CEvidence raw is {expected,actual} unequal retained native operands.
   --  reconciled: {cause,route,reattach_event,ecr,failed_event,retry};
   --  route only "reattach"/"append-persisted"/"append-retry"/"custody-returned"/
   --  "corroborated"; no EOF/deadline settlement. Fold owns before_unknown,
   --  legal original-phase-owner retry and replay/alternative/CAS relations.
   --  append-retry redecides the full actual saved native attempt; retry.
   --  original_owner is the complete actual candidate.x5.actor_identity image,
   --  not a copied phase/owner role label. Saved input is structurally nested
   --  within complete immutable Value.Source_Input, not selected Before Input;
   --  this is actual byte-image descent, never an accepted-domain cap.
   --  Owned ORIGINAL tuple replay, full material and actual source/owner roster
   --  correspondence. Operation identity is deliberately checked by the caller:
   --  a subject request and its root starter have independent operations.
   function Native_Capture_Joined
     (Data : E.Bytes; Observation, Material, Provenance : E.Span; Role : String)
      return Boolean with Global => null;
   function Native_Capture_Joined
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Role : String)
      return Boolean with Global => null;
   function Worker_Gone
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State)
      return Boolean with Global => null,
       Post => (if Worker_Gone'Result then Index in Value.Events'Range);
   type Worker_Liveness is (Known_Live, Known_Gone, Uncertain);
   function Worker_Liveness_Of
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State)
      return Worker_Liveness with Global => null;
   --  Event-specific raw evidence only. Authentication of the full prefix,
   --  phase/actor/alternative/history legality and Next belong to the fold.
   --  References are resolved strictly before Index, never against future rows.
   function Join
     (Value : L.Parsed_Input; Index : Q.Byte_Count;
      Before : M.Root_State; Subjects : M.Subject_State_Array;
      Subject : P.Optional_Subject) return Join_Status
     with Global => null,
       Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 4),
       Post => (if Join'Result = Evidence_Joined then
          Value.Status = L.Parsed and then Index in Value.Events'Range);
   -- The full actual current-owner/journal replay is established once by Fold.
   -- An invalid/default or foreign-arena proof never admits any event.
   function Join
     (Value : L.Parsed_Input; Index : Q.Byte_Count;
      Before : M.Root_State; Subjects : M.Subject_State_Array;
      Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof) return Join_Status
     with Global => null,
       Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 3),
       Post => (if Join'Result = Evidence_Joined then
          Value.Status = L.Parsed and then Index in Value.Events'Range and then
          Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Index, Proof));
   type Closed_State_References is record
      Status : Join_Status := Evidence_Refused;
      Terminal_Owner_State : E.Span := (1, 0);
      Current_Owner_State : E.Span := (1, 0);
   end record;
   --  Full authenticated CLOSED_WITNESS evidence and two-side state relation,
   --  without Legal/Next. Returned spans refer to owned unchanged original
   --  material in Value.Arena; cached Join performs Closed_State.Matches once.
   function Closed_Proof_Reference
     (Value : L.Parsed_Input; Index : Q.Byte_Count;
      Before : M.Root_State; Subjects : M.Subject_State_Array;
      Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof)
      return Closed_State_References
     with Global => null,
       Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 4),
       Post => (if Closed_Proof_Reference'Result.Status = Evidence_Joined then
          Value.Status = L.Parsed and then Index in Value.Events'Range and then
          Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Index, Proof));
end Worldline.Custody_V2_Root_Evidence;

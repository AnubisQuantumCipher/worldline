with Worldline.Custody_V2_Load_Input;
with Worldline.Custody_V2_Operation_Journal;
package Worldline.Custody_V2_Subject_Evidence with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   package D renames L.N.D;
   package M renames D.M;
   package P renames L.N.P;
   package Q renames D.Q;
   use type L.Decode_Status;
   use type M.Subject_Kind;
   type Join_Status is (Evidence_Refused, Evidence_Joined);
   type Cleanup_Kind is (No_Event, Request_Lost, Drain_Reclaimed, Retain_Unknown);
   -- Complete ordered descriptor-role relation, independent of operation,
   -- subject and event domain. Receiver fstat/socket/flock receipts use Source;
   -- actual front-broker KCMP_FILE receipts use distinct KCMP_Source. Transport
   -- rights/frame/carrier evidence must be joined separately by the caller.
   function Roles_Joined
     (Data : L.E.Bytes; Actual, Original, Source, KCMP_Source : L.E.Span;
      Received : Boolean) return Boolean with Global => null;
   -- The input is the SAME complete staged mutation envelope with actual X5
   -- root E-CR, original subject payload and native-selected predecessor heads.
   -- The proposed family kind is not authority. This selector redecides the
   -- original no-work clauses before requiring E-CR for a loss consequence.
   -- Known live is no work; ambiguous material is retained, never reclaimed.
   -- A later append still requires the complete Legal/Next decision.
   function Cleanup_Kind_Of
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof)
      return Cleanup_Kind with Global => null,
        Post => (if Cleanup_Kind_Of'Result in Request_Lost | Drain_Reclaimed then
          Value.Status = L.Parsed and then Index in Value.Events'Range and then Subject.Present);
   -- Ephemeral pre-effect query on the same full envelope. The proposed
   -- REQUEST_RESPONDED header selects the request family but is never appended
   -- by this query; no response/blob or future write is asserted. Actual
   -- subject_evidence.serving_gate carries the current raw FRESH reread or
   -- signed WLRY gate pair and complete endpoint transcript.
   function Serving_Reference
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject)
      return Boolean with Global => null;
   function Serving_Join
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof)
      return Join_Status with Global => null,
        Post => (Serving_Join'Result = Evidence_Joined) =
          (Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Index, Proof)
           and then Serving_Reference (Value, Index, Before, Subjects, Subject));
   -- Factual output-allocation context, not a serving or append grant. Both
   -- actual Front and Worker producers are admitted by their complete current
   -- source/actor and original request joins, without a Request_From clause
   -- or a response-kind phase prerequisite. Detached production after a
   -- committed response remains in domain. The allocator independently joins
   -- x5.emitter.records/candidate original images to all authenticated original
   -- REQUEST_OUTPUT boundaries and derives the production-order quantity.
   function Output_Reference
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof)
      return Boolean with Global => null,
        Post => (if Output_Reference'Result then
          Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Index, Proof)
          and then Subject.Present and then Subject.Value.Kind = M.Request);
   -- Shared authentic factual context for allocator and channel evidence.
   -- Current observer and historical producer/writer are distinct: this join
   -- does not impose an emitter candidate, admission kind, phase or RootReady.
   function Output_Context_Reference
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof)
      return Boolean with Global => null,
        Post => (if Output_Context_Reference'Result then
          Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Index, Proof)
          and then Subject.Present and then Subject.Value.Kind = M.Request);
   -- NEW capture grammar; existing v1 producers do not emit it. Source UNRUN.
   -- x5.subject_evidence.schema = "worldline.custody-subject-raw-v1".
   -- binding {generation,operation,subject,subgeneration,root_head,
   -- subject_head,source,actor,original} compares complete original payload,
   -- native source/actor captures and prior TEXT event references. Quantity
   -- binding fields have the exact original SQL BLOB archive representation.
   -- request is the full original RequestPeer observation, never asserted UID.
   -- front_socket/worker_socket use Custody_V2_Requester_Join's raw grammar.
   -- Each socket also carries source; every syscall receipt source equals it.
   --
   -- transfer {mode,frame,sender,received_sender,send,receive,roles,
   -- worker_document,origin_user_ns,reader_user_ns,origin_pid_ns,reader_pid_ns,
   -- held_pid_ns,host_cookie,reader_cookie}. send/receive contain fd, result,
   -- errno, frame, rights, flags, source. roles is the FULL original ordered
   -- socket descriptor roster; each row {role,origin,current,front_fd,
   -- worker_fd,kcmp,flock}. No fixed participant count or missing alias default.
   -- current_inventory is BYTES of the whole actual adopted subject inventory.
   -- x5.subject_evidence_raw carries the WHOLE unchanged original profile,
   -- decoded once by Load_Input into its owned arena and included in private
   -- Journal_Proof identity. Whole scoped/raw profile and transfer equality are
   -- mandatory before using any raw span. FRESH intake/serving preserves every
   -- ordered original role and requires same-capture provenance.subject_capture,
   -- native packet/source/OFD-alias linkage, ordered inventory-image equality
   -- and the genuine cross-arena Evolution.Subject_Roles_Match. Retired aliases
   -- remain actual closed/EBADF facts, never copied current KCMP success.
   -- A FRESH intent needs the actual original front socket and complete roles;
   -- intake additionally needs the successful actual send/receive and worker
   -- raw peer reread. RELAY intent/intake joins the retained transfer head,
   -- reattach epoch, real custody channel and front reread; no serving gate
   -- may be authorized before committed INTAKE.
   --
   -- serving_gate carries FRESH correspondence or a full signed WLRY pair,
   -- both actual endpoints, four raw syscall streams and complete prior gate
   -- history. Frames are WLRY / uint32be length / original archive(body) /
   -- HMAC under worldline.root-worker-relay-v1+NUL and the original owner key.
   -- Bodies bind gen/sg/epoch, own operation/request, gate, sequence, nonce
   -- and committed intake head. Responses echo bindings and original reread
   -- observation/error. Gate sequence starts one; output sequence permits zero.
   --
   -- descriptor {role,fd,identity,roster}: roster is the FULL original LIVE
   -- front roster, exactly equal to original.live_roster. Every member identity
   -- and role is retained; duplicate roles/fds fail rather than disappear.
   -- spool {direction,records,raw,fd,identity,fsync,position}: raw is the whole
   -- actual spool file, identity the actual original fstat/readback, records
   -- ALL ordered {kind,owner,position,length,data,sha256,write,fsync}.
   -- ARMED/CHUNK/DISARMED and WRITE_ARMED/W_DONE fold every open interval;
   -- every CHUNK joins actual write/pwrite offset/result/bytes and file slice.
   -- STOP requires an open interval; FREEZE requires a durable closed interval.
   -- Primitive Position is rederived from complete raw bytes, never EOF.
   --
   -- ofd.worker_report holds the unchanged original archive image, with owned
   -- actor/source/native tuple companions. Original worker kcmp receipts are
   -- retained separately from real front-broker KCMP_FILE operands and locks.
   -- Both actual descriptor and /spool worker fd roles join the original report.
   -- Released close {fd,result,errno,source,readback}; close returns zero,
   -- readback fstat on that same active fd returns -1/EBADF. Retained copies
   -- are distinct roles, not implicitly closed; last-writer EOF is untouched.
   -- Lost/Reclaimed call the SAME full authentic root Worker_Gone E-CR join.
   --
   -- response {bytes,sha256,blob,original,relay,relay_body,gates,out_seq}: digest
   -- blob SQL bytes all join; original is the exact original response archive.
   -- RELAY contains the full RESPONSE_BYTES frame, prior intake head and exact
   -- bytes reserved for the later front write. Responded does not claim that
   -- a future write already happened. Front native original gates are replayed.
   -- Request abandon rejoins retained transfer operands; descriptor abandon
   -- joins the original role/identity and exact successor subgeneration.
   -- Fold independently decides all actor/from/root/alternative clauses.
   -- Every nullable operand is explicit NoneType; missing fields never stand
   -- for absent participants. Arbitrary nested original data remains unchanged.
   function Primitive_Reference
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject)
      return Boolean with Global => null,
       Post => (if Primitive_Reference'Result then Index in Value.Events'Range);
   -- Primitive evidence only; root/subject Legal and RawNext remain in Fold.
   -- Every predecessor lookup is restricted to the authenticated prior prefix.
   function Join
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject)
      return Join_Status with Global => null,
       Post => (if Join'Result = Evidence_Joined then
         Primitive_Reference (Value, Index, Before, Subjects, Subject));
   function Join
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof)
      return Join_Status with Global => null,
       Post => (Join'Result = Evidence_Joined) =
         (Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Index, Proof)
          and then Primitive_Reference (Value, Index, Before, Subjects, Subject));
end Worldline.Custody_V2_Subject_Evidence;

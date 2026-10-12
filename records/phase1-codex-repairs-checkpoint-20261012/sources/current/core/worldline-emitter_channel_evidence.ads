with Worldline.Custody_V2_Subject_Evidence;
with Worldline.Custody_V2_Operation_Journal;
package Worldline.Emitter_Channel_Evidence with SPARK_Mode is
   package SE renames Worldline.Custody_V2_Subject_Evidence;
   package I renames SE.L;
   package E renames I.E;
   package Q renames E.Q;
   package M renames SE.M;
   package P renames SE.P;
   package J renames Worldline.Custody_V2_Operation_Journal;
   -- Borrowed ORIGINAL operation archives. The private full journal proof and
   -- complete native source/current/history correspondence are prerequisites;
   -- neither an ordinal nor a journal-status field establishes an origin.
   -- These joins do not allocate, fold written order, or grant serving/append.
   -- The root output policy owns the complete production/written prefix.
   -- Baseline requester/current source/native joins use the authentic shared
   -- SE.Output_Context_Reference; saved sender/writer joins are separate.
   -- Frame_Reference also authenticates the literal seven-field PEER_STATUS
   -- candidate {request,admission_head,type,source,scope,relay,written}. Its
   -- signed payload next_out_seq is evidence to compare with the root policy's
   -- rederived complete written prefix, never a counter or write permission.
   -- Source-only producer profile: sealed OUTPUT_SOURCE retains its complete
   -- worker_channel/document, actor, worker_origin, send and native tuple;
   -- replay retains those exact companions as worker_* relay fields.
   -- OUTPUT_WRITTEN_REPORT retains the real Front native tuple and actor.
   -- Status relay retains both channel documents, PEER_HELD/PEER_STATUS frames,
   -- actual streams, writer_native raw original bytes and unchanged sealed
   -- PEER_STATUS_REPORT body/frame/native/actor/source/channel/document/written.
   -- PEER_HELD carries {written: actual Worker ACK tuple}; authentication of
   -- that original payload is separate from the root's ordered OJ replay.
   -- Front-owned prefix ACKs retain sealed OUTPUT_SOURCE and genuine saved
   -- Front writer/native/write/send facts, not a fictitious Worker receive.
   -- Actual serving dup/KCMP receipts and retained service-registry alias
   -- chains bind live descriptors to enrolled socket/OFD identities.
   -- ACK/status relay_namespace_source binds actual report SCM credentials
   -- through the measured original Root EXEC, host-proc/NSpid/PIDFD/namespaces,
   -- never a generic PID0 or socket-creator credential exception.
   -- Both written and status relays retain worker_native BYTES of the actual
   -- complete Worker tuple observed before the original send. Historical
   -- endpoint/source joins redecide it rather than substituting current X5.
   -- Historical epochs are at most Before.Reattach_Epoch; only the exact
   -- current emitter candidate image requires equality to the current epoch.
   -- OUTPUT_PREFIX is an unsigned pure observation before PEER_STATUS signing:
   -- exact {request,admission_head,type,source,scope,written}. This helper
   -- authenticates only its current context and the original tuple carrier;
   -- the root policy must authenticate/replay every ACK and derive the prefix.
   function Prefix_Reference
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : J.Journal_Proof; Candidate_Data : E.Bytes; Candidate : E.Span)
      return Boolean with Global => null;
   function Frame_Reference
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : J.Journal_Proof; Candidate_Data : E.Bytes; Candidate : E.Span)
      return Boolean with Global => null;
   -- Source is the actual writer, not necessarily the current query observer.
   -- Production scope retains its original epoch. A signed PEER_STATUS is not
   -- a written acknowledgement: the original front report, sockets, native
   -- origin and all frame syscall streams remain necessary.
   function Acknowledgement_Reference
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : J.Journal_Proof; Acknowledgement_Data, Produced_Data : E.Bytes;
      Acknowledgement, Produced : E.Span)
      return Boolean with Global => null;
end Worldline.Emitter_Channel_Evidence;

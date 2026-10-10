with Worldline.Custody_V2_Values;
with Worldline.Custody_V2_Archive_Chain;
package Worldline.Custody_V2_Requester_Join with SPARK_Mode is
   package V renames Worldline.Custody_V2_Values;
   package S renames V.S;
   package E renames V.E;
   package Q renames V.Q;
   package C renames Worldline.Custody_V2_Archive_Chain;
   -- All scalar checks decode the original integer's entire magnitude.
   -- Linux syscall constants constrain kernel operands, not archived quantities.
   function Integer_Is (Data : E.Bytes; Item : E.Span; Number : Long_Long_Integer)
      return Boolean with Global => null;
   function Unsigned_Is (Data : E.Bytes; Item : E.Span; Number : Q.Byte_Count)
      return Boolean with Global => null;
   function Same (Data : E.Bytes; Left, Right : E.Span) return Boolean
      with Global => null;
   function Same_Bytes (Data : E.Bytes; Left, Right : E.Span) return Boolean
      with Global => null;
   function Digest_Matches (Data : E.Bytes; Raw, Hex : E.Span) return Boolean
      with Global => null;
   -- Authenticate the exact borrowed frame excluding its final 32-byte MAC.
   -- Key and frame remain in separate original arenas: no concatenation cap.
   function Frame_Mac_Matches
     (Key_Data, Frame_Data : E.Bytes; Key, Frame : E.Span; Domain : String)
      return Boolean with Global => null;
   function Ucred_Matches (Data : E.Bytes; Raw : E.Span; Peer : E.Span)
      return Boolean with Global => null;
   -- Per-message SCM_CREDENTIALS, deliberately not SO_PEERCRED. The caller
   -- separately binds the genuine receive receipt and owned channel lineage.
   function SCM_Credentials_Match
     (Data : E.Bytes; Raw, Pid, Uid, Gid : E.Span) return Boolean
     with Global => null;
   function Signed_32_Matches
     (Data : E.Bytes; Raw, Value : E.Span) return Boolean with Global => null;
   -- Cross the two ORIGINAL encoders without a reconstructed/flattened DTO.
   -- Document is S.record(RequestPeer.observation()); Archive is the original
   -- operation_capture.archive capture['request'] subtree, in borrowed storage.
   function Request_Archive_Matches
     (Document_Data, Archive_Data : E.Bytes; Document, Archive : E.Span)
      return Boolean with Global => null;
   -- Socket is a factual transcript of calls on one owned descriptor:
   -- {fd,fstat,peercred,domain,type,peername}. fstat is
   -- {fd,result,errno,identity}; identity is the complete original identity(fd).
   -- getsockopt calls are {fd,level,option,requested,result,errno,raw:bytes};
   -- peername is {fd,result,errno,raw:bytes}. Socket identity and ucred are
   -- rederived, not accepted from document pid/uid/gid or a success verdict.
   function Socket_Matches (Data : E.Bytes; Socket, Document : E.Span)
      return Boolean with Global => null;
   function Fresh_Matches
     (Data : E.Bytes; Document, Front_Socket, Worker_Socket, Transfer : E.Span)
      return Boolean with Global => null;
   -- Optional cookie/namespace operands require an explicit NoneType. Missing
   -- fields are malformed, never an absent-participant default. When both
   -- optional operands exist they join; PID namespaces are not equated.
end Worldline.Custody_V2_Requester_Join;

with Worldline.Custody_V2_Load_Input;
with Worldline.Retained_Evidence_Replay;
with Worldline.Custody_V2_Owner_Canonical;
with Worldline.Custody_V2_K4_Resource_Ack;
with Interfaces;
package Worldline.Custody_V2_Operation_Journal with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   package E renames L.E;
   package Q renames L.Q;
   package R renames Worldline.Retained_Evidence_Replay;
   package A renames R.A;
   package O renames Worldline.Custody_V2_Owner_Canonical;
   package K renames Worldline.Custody_V2_K4_Resource_Ack;
   use type L.Decode_Status;
   type Journal_State is (Absent, Reserved, Effect_Intent, Effect_Observed,
      Settled, Released, Quarantined, Resolved_Effect, Resolved_No_Effect);
   -- This is the original chronological table, including repeated quarantine.
   -- Historical completion is a DISTINCT native result, never an A.Decision cast.
   function Transition_Allowed
     (Before, After : Journal_State; Command : A.Command;
      Decision : A.Decision; Historical : R.H.Decision;
      Historical_Entry : Boolean := False) return Boolean
     with Global => null;
   -- Authenticating one original JSON envelope is necessary, not sufficient:
   -- the complete current owner files/head and all-operation history are joined
   -- separately by Authenticated. No key or authorization bit comes from X5.
   function Envelope_Authenticated
     (Key_Data, JSON_Data : E.Bytes; Key, Envelope : E.Span;
      Domain : String) return Boolean
     with Global => null;
   type Head_Disposition is (Refused, Stable, Finalize_Surviving_Next);
   type Journal_Proof is private;
   -- Constructed only by full original source/native/current-history replay.
   -- Invalid default; no producer authorization scalar can construct it.
   procedure Establish (Value : L.Parsed_Input; Proof : out Journal_Proof)
      with Global => null, Always_Terminates;
   -- A complete native frame may lend its already established factual histories.
   -- Exact source correspondence and all typed owner/current/history joins are
   -- still checked here. The contexts never escape into Journal_Proof.
   procedure Establish
     (Value : L.Parsed_Input; Owner_Context : O.Prepared_History;
      Resource_Context : K.Prepared_History; Proof : out Journal_Proof)
      with Global => null, Always_Terminates;
   function Established (Value : L.Parsed_Input; Proof : Journal_Proof) return Boolean
      with Global => null,
        Post => (if Established'Result then Value.Status = L.Parsed);
   procedure Startup_Decide
     (Value : L.Parsed_Input; Proof : Journal_Proof; Current_Matches : out Boolean;
      Head : out Head_Disposition; Preparations_Done : out Boolean)
      with Global => null, Always_Terminates,
        Post => (if not Current_Matches then Head = Refused and then not Preparations_Done)
          and then (if Head /= Refused or else Preparations_Done then
             Current_Matches and then Value.Status = L.Parsed);
   function Authenticated (Value : L.Parsed_Input; Index : Q.Byte_Count;
                           Proof : Journal_Proof) return Boolean
      with Global => null,
        Post => (if Authenticated'Result then
          Value.Status = L.Parsed and then Index in Value.Events'Range);
   function Current_Authenticated (Value : L.Parsed_Input) return Boolean
      with Global => null,
        Post => (if Current_Authenticated'Result then Value.Status = L.Parsed);
   -- Recognition/finalization of the EXISTING independent operation head is
   -- not permission to expose a fresh endpoint or dispatch any operation.
   function Head_Action (Value : L.Parsed_Input) return Head_Disposition
      with Global => null,
        Post => (if Head_Action'Result /= Refused then Value.Status = L.Parsed);
   -- One genuine context/native/history redecision serves all three outputs.
   procedure Startup_Decide
     (Value : L.Parsed_Input; Current_Matches : out Boolean;
      Head : out Head_Disposition; Preparations_Done : out Boolean)
      with Global => null, Always_Terminates,
        Post => (if not Current_Matches then Head = Refused and then not Preparations_Done)
          and then (if Head /= Refused or else Preparations_Done then
             Current_Matches and then Value.Status = L.Parsed);
   function Preparations_Complete (Value : L.Parsed_Input) return Boolean
      with Global => null,
        Post => (if Preparations_Complete'Result then Value.Status = L.Parsed);
   -- Exact original reconcile_before_endpoint route, derived from the latest
   -- full authenticated ordinary row. It selects an original recovery producer;
   -- it is not that producer's success, a new use or effect authorization.
   -- Each consequential recovery step still consumes its complete actual
   -- native packet and fresh physical/owner context before the original effect.
   -- RELEASED was an original no-action branch, not an unresolved operation.
   type Recovery_Action is (Recovery_Refused, No_Recovery, Retain_Unresolved,
      Recover_Committed, Recover_Owner_Resolution, Recover_Full_Broker, Recover_K4);
   function Recovery_Decide
     (Value : L.Parsed_Input; Operation : E.Span; Proof : Journal_Proof)
      return Recovery_Action
      with Global => null,
        Post => (if Recovery_Decide'Result /= Recovery_Refused then Value.Status = L.Parsed);
   function Recovery_Decide
     (Value : L.Parsed_Input; Operation : E.Span) return Recovery_Action
      with Global => null,
        Post => (if Recovery_Decide'Result /= Recovery_Refused then Value.Status = L.Parsed);
   -- Candidate is separate from all genuine BEFORE files/rows. Complete
   -- original chronology/chain replay precedes the writer's first head CAS.
   function Append_Allowed (Value : L.Parsed_Input; Candidate : E.Span)
      return Boolean with Global => null,
        Post => (if Append_Allowed'Result then Value.Status = L.Parsed);
   function Authenticated (Value : L.Parsed_Input; Index : Q.Byte_Count)
      return Boolean
     with Global => null,
       Post => (if Authenticated'Result then
          Value.Status = L.Parsed and then Index in Value.Events'Range);
   -- The original offline utility is a separate owner boundary. The transport
   -- supplies actual getpid/geteuid values, never values from the input record.
   -- The full immutable input contains original sources and real syscall/OFD
   -- observations; no custody-v2 root or canonical principal is fabricated.
   type Bootstrap_Action is (Bootstrap_Refused, Create_Fresh, Reuse_Authentic);
   type Bootstrap_Decision is record
      Status : Bootstrap_Action := Bootstrap_Refused;
      Position : E.Count := 0;
   end record;
   function Bootstrap_Decide
     (Data : aliased E.Bytes; Envelope : E.Span;
      Caller_PID, Caller_EUID : Interfaces.Unsigned_32) return Bootstrap_Decision
      with Global => null;
private
   type Proof_State is (Not_Established, Original_Current_Replayed);
   type Preparation_State is (Pending, Complete);
   type Journal_Proof is record
      State : Proof_State := Not_Established;
      Arena_Count, Arena_Used, Decoded_Events, Events, Heads, Roots, Subjects,
        Alternatives, Blobs : E.Count := 0;
      Owner_Roster, Input, Source_Input, Key, Genesis_File, Genesis_Row, Genesis_Message,
        Genesis_Mac : E.Span := (1, 0);
      Arena_Digest, Operand_Digest : Worldline.Hash := Worldline.Zero_Hash;
      Head : Head_Disposition := Refused;
      Preparations : Preparation_State := Pending;
   end record;
end Worldline.Custody_V2_Operation_Journal;

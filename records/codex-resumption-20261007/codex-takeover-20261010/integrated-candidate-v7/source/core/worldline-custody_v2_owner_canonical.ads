with Worldline.Custody_V2_Load_Input;
package Worldline.Custody_V2_Owner_Canonical with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   package E renames L.E;
   use type L.Decode_Status;
   -- Lexical observer of immutable actual scoped bytes and the separately
   -- decoded original operation-list capsule arena. Neither borrow may escape
   -- the enclosing native call. A default object has no authenticated history.
   type Prepared_History
     (Data, Facts_Data : access constant E.Bytes;
      Parsed_Data : access constant L.Parsed_Input) is limited private;
   -- Factual decoder only: no installation, source or issuer admission.
   function Extract_Replay_Capsules
     (Data : E.Bytes; Owner_Roster : E.Span) return E.Bytes
     with Global => null;
   -- One-shot complete original owner9 current authentication and native
   -- RESERVED/SETTLED adoption replay on the same borrowed actual sources.
   procedure Establish_History
     (Context : in out Prepared_History; Roster : E.Span)
     with Global => null, Always_Terminates;
   -- Factual relation only. Bootstrap MUST additionally conjoin the actual
   -- full Startup_Installation, Source_Custody and Issuer_Source predicates on
   -- this same Data; this getter is not a standalone startup admission.
   function Current_Matches (Context : Prepared_History) return Boolean
     with Global => null;
   -- Exact factual source/coordinate relation at the frame handoff, not an
   -- admission predicate or a hash/pointer comparison repeated per witness.
   function Source_Matches
     (Context : Prepared_History; Data : E.Bytes; Roster : E.Span)
      return Boolean
     with Global => null,
       Post => (if Source_Matches'Result then Current_Matches (Context));
   function Authenticated
     (Context : Prepared_History; Capture_Data : E.Bytes; Witness : E.Span)
      return Boolean
     with Global => null,
       Post => (if Authenticated'Result then Current_Matches (Context));
   -- Original operation_capture.archive bytes and original scoped load arena
   -- are distinct. No span from either arena is applied to the other.
   function Authenticated
     (Value : L.Parsed_Input; Capture_Data : E.Bytes; Witness : E.Span)
      return Boolean
     with Global => null,
       Post => (if Authenticated'Result then Value.Status = L.Parsed);
   -- Full current protected owner issuer/genesis/bootstrap/head/lifecycle,
   -- including every original RESERVED and SETTLED ADOPT_REQUIREMENT replay.
   function Current_History_Authenticated (Value : L.Parsed_Input)
      return Boolean
     with Global => null,
       Post => (if Current_History_Authenticated'Result then
          Value.Status = L.Parsed);
   -- Original full evaluation producer/classifier collection, then the native
   -- owner rule. Facts_Data is the separate actual operation archive of parser
   -- capsules; no scalar/identity offset in Data is applied to that arena.
   -- FAIL history is retained, never replaced by selected evidence.
   function Reserved_Redecided
     (Data : E.Bytes; Record_Value : E.Span; Facts_Data : E.Bytes; Capsules : E.Span)
      return Boolean with Global => null;
   -- The consumed adoption receipt is reconstructed from actual event hashes
   -- and exact original collapse packet, never a copied native disposition.
   function Adopt_Settled_Redecided
     (Data : E.Bytes; Record_Value : E.Span; Event_Digest, Facts_Data : E.Bytes;
      Capsules : E.Span)
      return Boolean with Global => null;
private
   type History_State is (Unestablished, Rejected, Verified);
   type Current_View is record
      State : History_State := Unestablished;
      Roster, Key_Field, Policy_Field, Binding, Journal_Field : E.Span := (1, 0);
      Event_Count : Natural := 0;
   end record;
   type Prepared_History
     (Data, Facts_Data : access constant E.Bytes;
      Parsed_Data : access constant L.Parsed_Input) is limited record
      View : Current_View;
   end record;
end Worldline.Custody_V2_Owner_Canonical;

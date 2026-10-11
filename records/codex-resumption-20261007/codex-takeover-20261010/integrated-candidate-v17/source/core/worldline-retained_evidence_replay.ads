with Worldline.Collapse_Wire;
with Worldline.Scoped_Archive;
with Worldline.Native_Execution_Views;
with Worldline.Operation_Authority;
with Resource_Scoped_Run_Ledger;
with Worldline.Resource_Child_Execution;
with Worldline.Canonical_Owner_Completion;
with Worldline.Canonical_Exchange;
with Interfaces;
package Worldline.Retained_Evidence_Replay with SPARK_Mode is
   package E renames Worldline.Scoped_Archive.E;
   package V renames Worldline.Native_Execution_Views;
   package A renames Worldline.Operation_Authority;
   package J renames Worldline.Resource_Child_Execution;
   package S renames Resource_Scoped_Run_Ledger;
   package H renames Worldline.Canonical_Owner_Completion;
   package CEX renames Worldline.Canonical_Exchange;
   type Replay_State is (Decode_Refused, Native_Redecided, Output_Conflict);
   type Root_Replay_Result is record
      State : Replay_State := Decode_Refused;
      Native_Status : J.Status := J.Status'First;
      Mode : J.Admission_Mode := J.Admission_Mode'First;
      Action : A.Operation := A.Operation'First;
      Id : A.Identities := (others => (Present => False, Value => (others => 0)));
   end record;
   type Scoped_Entry is (Check_Entry, Validate_Entry, Classify_Entry);
   type Scoped_Replay_Result is record
      State : Replay_State := Decode_Refused;
      Roster_Entry : Scoped_Entry := Check_Entry;
      Native_Status : Interfaces.Unsigned_32 := 0;
      Action : S.Action := S.Action'First;
      Original_Command : J.L.Operation := J.L.Operation'First;
   end record;
   type Operation_Entry is (Authority_Entry, Historical_Completion_Entry);
   type Operation_Replay_Result is record
      State : Replay_State := Decode_Refused;
      Roster_Entry : Operation_Entry := Authority_Entry;
      Historical_Status : H.Decision := H.Refused;
      Command : A.Command := A.Command'First;
      Native_Status : A.Decision := A.Decision'First;
      Action : A.Operation := A.Operation'First;
      Id : A.Identities := (others => (Present => False, Value => (others => 0)));
   end record;
   type Exchange_Replay_Result is record
      State : Replay_State := Decode_Refused;
      Native_Status : CEX.Decision := CEX.Refused;
      Action : A.Operation := A.Operation'First;
      Id : A.Identities := (others => (Present => False, Value => (others => 0)));
   end record;
   -- Complete retained material is owned and natively redecided before any
   -- output comparison. These functions establish value evidence, not source
   -- authenticity, an SQL row's provenance, event custody or a dispatch grant.
   function Reestablish_Root_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Root_Replay_Result
     with Global => null;
   function Reestablish_Scoped_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Scoped_Replay_Result
     with Global => null;
   function Reestablish_Operation_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Operation_Replay_Result
     with Global => null;
   -- Lossless resource IDs are arbitrary length. Compare their owned decoded
   -- bytes directly to the authenticated custody value without imposing a
   -- digest-size restriction or returning arena-relative native spans.
   function Scoped_Identity_Matches
     (Data : E.Bytes; Observation_Archive : E.Span; Expected : E.Bytes;
      Reservation : Boolean := False) return Boolean with Global => null;
   -- Exact native-input versus complete authentic material correspondence;
   -- these joins must accompany, never replace, successful redecision and the
   -- caller's protected event/source/prior-state custody joins.
   function Root_Material_Matches
     (Data : E.Bytes; Observation_Archive, Material_Archive : E.Span)
      return Boolean with Global => null;
   function Scoped_Material_Matches
     (Data : E.Bytes; Observation_Archive, Material_Archive : E.Span)
      return Boolean with Global => null;
   function Operation_Material_Matches
     (Data : E.Bytes; Observation_Archive, Material_Archive : E.Span)
      return Boolean with Global => null;
   function Reestablish_Exchange_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Exchange_Replay_Result
     with Global => null;
   function Exchange_Material_Matches
     (Data : E.Bytes; Observation_Archive, Arguments_Archive : E.Span)
      return Boolean with Global => null;
   function Root_Capture_Matches
     (Data : E.Bytes; Observation_Archive, Provenance_Archive : E.Span)
      return Boolean with Global => null;
   -- Original exact ten-member current and eight-member intake provenance remain
   -- valid. The sole additive subject_capture member is accepted only when the
   -- complete same-event subject/native/descriptor relation validates it.
   function Operation_Capture_Matches
     (Data : E.Bytes; Observation_Archive, Material_Archive, Event_Archive : E.Span)
      return Boolean with Global => null;
   function Archive_Field
     (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
      with Global => null;
   -- Transport-only native values: Present is decode success, NEVER admission.
   -- Callers must derive every source/whole-roster/owner fact independently.
   type Collapse_Values_Result (Present : Boolean := False) is record
      case Present is
         when True => Raw : Worldline.Collapse_Wire.Raw_Request;
         when False => null;
      end case;
   end record;
   function Decode_Collapse_Values (Data : E.Bytes; Values : E.Span)
      return Collapse_Values_Result with Global => null;
   function Reestablish_Reservation_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Operation_Replay_Result
      with Global => null;
   function Reservation_Material_Matches
     (Data : E.Bytes; Observation_Archive, Material_Archive : E.Span)
      return Boolean with Global => null;
   function Archive_Text_Is (Data : E.Bytes; Item : E.Span; Text : String) return Boolean
     with Global => null;
   function Archive_Boolean_Is (Data : E.Bytes; Item : E.Span; Value : Boolean) return Boolean
     with Global => null;
   function Archive_Bytes_Valid (Data : E.Bytes; Item : E.Span) return Boolean
     with Global => null;
   function Archive_Bytes (Data : E.Bytes; Item : E.Span) return E.Bytes
     with Global => null, Pre => Archive_Bytes_Valid (Data, Item);
   function Archive_Integer_Valid (Data : E.Bytes; Item : E.Span) return Boolean
     with Global => null;
   function Archive_Integer_Negative (Data : E.Bytes; Item : E.Span) return Boolean
     with Global => null, Pre => Archive_Integer_Valid (Data, Item);
   function Archive_Integer_Magnitude (Data : E.Bytes; Item : E.Span) return E.Bytes
     with Global => null, Pre => Archive_Integer_Valid (Data, Item);
   function Archive_Is_None (Data : E.Bytes; Item : E.Span) return Boolean
     with Global => null;
   function Archive_Length (Data : E.Bytes; Item : E.Span) return E.Count
     with Global => null;
   function Archive_Index (Data : E.Bytes; Item : E.Span; Index : E.Count) return E.Span
     with Global => null;
   function Archive_Record_Is (Data : E.Bytes; Item : E.Span; Name : String) return Boolean
     with Global => null;
   function Archive_Is_Sequence (Data : E.Bytes; Item : E.Span) return Boolean with Global => null;
   function Archive_Equal (Data : E.Bytes; Left, Right : E.Span) return Boolean with Global => null;
   -- Image is a bytes carrier; all three codec flags are explicit.
   -- Literal dictionaries never select a different carrier codec by shape.
   function Archive_Image_Matches
     (Data : E.Bytes; Image, Value : E.Span;
      Image_Scoped, Value_Scoped : Boolean := False;
      Carrier_Scoped : Boolean := False) return Boolean
     with Global => null;
   function Decode_Recovery_Collapse_Values (Data : E.Bytes; Values : E.Span)
      return Collapse_Values_Result with Global => null;
   function Actor_Material_Matches
     (Data : E.Bytes; Observation_Archive, Material_Archive : E.Span)
      return Boolean with Global => null;
   function Root_Scoped_Material_Matches
     (Data : E.Bytes; Observation_Archive, Packet_Archive : E.Span) return Boolean
      with Global => null;
end Worldline.Retained_Evidence_Replay;

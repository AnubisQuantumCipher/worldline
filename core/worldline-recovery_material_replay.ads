with Worldline.Scoped_Archive;
with Evaluation_History;
package Worldline.Recovery_Material_Replay with SPARK_Mode is
   package E renames Worldline.Scoped_Archive.E;
   package H renames Evaluation_History;
   -- Complete JSONlike archive projection; byte capture mode is exactly the
   -- original evaluation_producer.capture optional_bytes encoding.
   function JSON
     (Data : E.Bytes; Item : E.Span; At_Layer : E.Layer := E.Recovery;
      Ensure_ASCII : Boolean := False; Preserve_Bytes : Boolean := False)
      return String with Global => null;
   function JSON_Valid
     (Data : E.Bytes; Item : E.Span; At_Layer : E.Layer := E.Recovery;
      Ensure_ASCII : Boolean := False; Preserve_Bytes : Boolean := False)
      return Boolean with Global => null;
   type Replay_Result is record
      Valid, Promotion : Boolean := False;
      Reference : H.Record_Reference := H.No_Record;
      Context, Capture, Typed_Rows, Retained_Stream, Observed : E.Span := (1, 0);
   end record;
   --  Pure factual request extraction over every original archive subtree.
   --  Retained payload bytes are decoded with the existing Terminal/Finalization
   --  codec. No history selection, custody or permission is decided here.
   function Syntax_Inputs
     (Data : E.Bytes; Whole : E.Span; At_Layer : E.Layer := E.Recovery)
      return String with Global => null;
   function Rebuild
     (Data : E.Bytes; Saved, Subject, Current_Requirement, Prepared : E.Span;
      Facts_Data : E.Bytes; Capsules : E.Span)
      return Replay_Result with Global => null;
   function Bind
     (Data : E.Bytes; Saved, Values, Subject, Candidate,
      Authoritative_Requirement, Resulting_Requirement, Roots, Agent,
      Agent_Record, Prepared : E.Span; Staged : Boolean;
      Facts_Data : E.Bytes; Capsules : E.Span) return Boolean
     with Global => null;
   function Agent_Matches
     (Data : E.Bytes; Subject, Agent, Agent_Record : E.Span;
      Required : Boolean; Facts_Data : E.Bytes;
      Capsules : E.Span) return Boolean with Global => null;
   function Agent_Admitted (Data : E.Bytes; Agent : E.Span)
      return Boolean with Global => null;
   function Row_Count
     (Data : E.Bytes; Material : E.Span; At_Layer : E.Layer := E.Recovery)
      return E.Count
     with Global => null;
   --  Zero denotes an unrepresentable extent. Otherwise this includes Data
   --  plus exactly the independently derived native declaration/measurement
   --  suffix; it guarantees Data'First + Result - 1 is representable.
   function Arena_Length
     (Data : E.Bytes; Material : E.Span; At_Layer : E.Layer := E.Recovery)
      return E.Count
     with Global => null;
   --  Decoded identity/epoch bytes stay at their original encoded first
   --  position. Arena must start at Data'First and have at least Arena_Length
   --  bytes. The suffix is private native policy/measurement storage; returned
   --  history identities and cursors remain original Data coordinates.
   procedure Classify_All
     (Data : E.Bytes; Material, World, Requirement : E.Span;
      Arena : in out E.Bytes; Rows : out H.History;
      Finalization : out H.Optional_Record; Current : out H.Optional_Cursor;
      Valid : out Boolean; At_Layer : E.Layer := E.Recovery;
      Facts_Data : E.Bytes; Capsules : E.Span)
     with Global => null;
   function Owner_Selected
     (Data : E.Bytes; Saved, Owner : E.Span; Facts_Data : E.Bytes;
      Capsules : E.Span)
      return Replay_Result with Global => null;
   function Owner_Promotion
     (Data : E.Bytes; Owner : E.Span; Facts_Data : E.Bytes;
      Capsules : E.Span)
      return Boolean with Global => null;
end Worldline.Recovery_Material_Replay;

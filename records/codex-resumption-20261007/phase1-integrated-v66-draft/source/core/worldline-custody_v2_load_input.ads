with Worldline.Custody_V2_Values;
with Worldline.Custody_V2_Raw_Next;
package Worldline.Custody_V2_Load_Input with SPARK_Mode is
   package V renames Worldline.Custody_V2_Values;
   package E renames V.E;
   package C renames Worldline.Custody_V2_Raw_Next.C;
   package F renames Worldline.Custody_V2_Raw_Next.D.F;
   package A renames Worldline.Custody_V2_Raw_Next.D.A;
   package N renames Worldline.Custody_V2_Raw_Next;
   package S renames F.S;
   package Q renames V.Q;
   use type E.Count;
   type Decode_Status is (Malformed, Storage_Extent, Parsed);
   type Sizes is record
      Status : Decode_Status := Malformed;
      Arena, Events, Heads, Roots, Subjects, Alternatives, Blobs : E.Count := 0;
   end record;
   type SQL_Rows is array (Q.Byte_Index range <>, Positive range <>) of S.SQL_Cell;
   type Span_Array is array (Q.Byte_Index range <>) of E.Span;
   type Original_Format is (No_Original, Scoped_Original, Operation_Original);
   -- Format is derived by native grammar inspection, never supplied by the
   -- producer. Unrecognized byte images retain their complete payload with
   -- No_Original; decode alone does not admit their evidence.
   type Event_Extra is record
      Reattach_Epoch, Position, Next_Subgeneration, Transfer_Mode,
        Abort_Class, Unknown_Cause : S.SQL_Cell;
      Cause_Archive : E.Span := (1, 0);
      Original_Payload : E.Span := (1, 0);
      Original_Encoding : Original_Format := No_Original;
      Root_Evidence_Payload, Native_Observations_Payload, Subject_Evidence_Payload : E.Span := (1, 0);
      Root_Evidence_Encoding, Native_Observations_Encoding,
        Subject_Evidence_Encoding : Original_Format := No_Original;
   end record;
   type Event_Extras is array (Q.Byte_Index range <>) of Event_Extra;
   -- The unchanged input prefix owns every original encoded span. Decoded bytes
   -- follow it exactly once; symbols share this same stack-owned arena.
   -- Whole-owner observers borrow this by-reference object, never its
   -- constrained array component and never a copied arena. Tagging provides
   -- aliased formal views; limitedness prevents accidental owner copies.
   type Parsed_Input
     (Arena_Count, Event_Count, Head_Count, Root_Count, Subject_Count,
      Alternative_Count, Blob_Count : E.Count) is tagged limited record
      Status : Decode_Status := Malformed;
      Decoded_Event_Count, Arena_Used : E.Count := 0;
      Arena : aliased E.Bytes (1 .. Arena_Count);
      Input, Key, Genesis_File, Genesis_Row, Genesis_Message, Genesis_Mac,
        Owner_Roster : E.Span := (1, 0);
      -- Complete immutable decoder source prefix, distinct from the selected
      -- load envelope. Staged evidence may reside outside Input, never outside
      -- Source_Input; recursive native trials decrease this authentic extent.
      Source_Input : E.Span := (1, 0);
      -- Full factual original capture shared by native packet/source/SQL joins.
      -- Bytes are owned once; no producer status or permission constructs it.
      Startup_Capture_Payload : E.Span := (1, 0);
      Startup_Capture_Encoding : Original_Format := No_Original;
      Events : C.Event_Rows (1 .. Event_Count);
      Extras : Event_Extras (1 .. Event_Count);
      Heads : C.Head_Rows (1 .. Head_Count);
      Roots : S.Root_Rows (1 .. Root_Count);
      Subjects : S.Subject_Rows (1 .. Subject_Count);
      Alternatives : A.Alternative_Rows (1 .. Alternative_Count);
      Event_SQL : SQL_Rows (1 .. Event_Count, 1 .. 13);
      Head_SQL : SQL_Rows (1 .. Head_Count, 1 .. 5);
      Root_SQL : SQL_Rows (1 .. Root_Count, 1 .. 16);
      Subject_SQL : SQL_Rows (1 .. Subject_Count, 1 .. 9);
      Alternative_SQL : SQL_Rows (1 .. Alternative_Count, 1 .. 7);
      Blob_SQL : SQL_Rows (1 .. Blob_Count, 1 .. 3);
      Event_Encoded : Span_Array (1 .. Event_Count);
      Head_Encoded : Span_Array (1 .. Head_Count);
      Root_Encoded : Span_Array (1 .. Root_Count);
      Subject_Encoded : Span_Array (1 .. Subject_Count);
      Alternative_Encoded : Span_Array (1 .. Alternative_Count);
      Blob_Encoded : Span_Array (1 .. Blob_Count);
      Symbols : N.Symbols;
   end record;
   function Counts (Data : E.Bytes) return Sizes with Global => null;
   function Counts (Data : E.Bytes; Envelope : E.Span) return Sizes
     with Global => null;
   function Parsed_Spans_Valid (Value : Parsed_Input) return Boolean
     with Global => null;
   procedure Decode (Data : E.Bytes; Value : out Parsed_Input)
     with Global => null, Always_Terminates,
       Post => (if Value.Status = Parsed then
          Parsed_Spans_Valid (Value) and then N.Valid (Value.Arena, Value.Symbols));
   procedure Decode (Data : E.Bytes; Envelope : E.Span; Value : out Parsed_Input)
     with Global => null, Always_Terminates,
       Post => (if Value.Status = Parsed then
          Parsed_Spans_Valid (Value) and then N.Valid (Value.Arena, Value.Symbols));
   procedure Decode_Grown
     (Data : E.Bytes; Envelope : E.Span; Value : out Parsed_Input; Used : out E.Count)
     with Global => null, Always_Terminates,
       Post => (if Value.Status = Parsed then
          Parsed_Spans_Valid (Value) and then N.Valid (Value.Arena, Value.Symbols) and then
          Used = Value.Arena_Used and then
          Value.Decoded_Event_Count < Value.Event_Count and then
          Value.Event_Count - Value.Decoded_Event_Count = 1);
   function SQL_Byte_Count (Data : E.Bytes; Encoded : E.Span) return E.Count
     with Global => null;
   procedure Append_SQL_Cell
     (Data : in out E.Bytes; Encoded : E.Span; Used : in out E.Count;
      Cell : out S.SQL_Cell; Status : out Decode_Status)
     with Global => null, Always_Terminates;
   function Event_Extra_Byte_Count (Data : E.Bytes; Record_Archive : E.Span)
      return E.Count with Global => null;
   procedure Append_Event_Extras
     (Data : in out E.Bytes; Record_Archive : E.Span; Used : in out E.Count;
      Extras : out Event_Extra; Status : out Decode_Status)
     with Global => null, Always_Terminates;
   -- A selected envelope remains a view into the unchanged complete parent
   -- input prefix. Its span is rebased to the arena, not extracted or recopied.
   -- SQL operands/codec correspondence only. Parsed is never Ready or an
   -- authentication, fold, owner-custody or startup permission decision.
end Worldline.Custody_V2_Load_Input;

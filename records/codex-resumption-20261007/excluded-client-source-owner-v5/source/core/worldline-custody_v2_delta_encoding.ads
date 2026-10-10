with Worldline.Custody_V2_Archive_Chain;
with Worldline.Root_Custody_Row_Schema;
-- Encoding only. No validity, digest or output flag confers custody authority.
package Worldline.Custody_V2_Delta_Encoding with SPARK_Mode is
   package C renames Worldline.Custody_V2_Archive_Chain;
   package E renames C.E;
   package Q renames E.Q;
   package SQL renames Worldline.Root_Custody_Row_Schema;
   use type E.Count;
   use type C.SHA.Digest;
   type Raw_Cell is record
      Kind : SQL.SQL_Class := SQL.SQL_Null;
      Negative : Boolean := False;
      Payload : E.Span := (1, 0);
   end record;
   type Cells is array (Q.Byte_Index range <>) of Raw_Cell;
   subtype Event_Columns is Cells (1 .. 12);
   subtype Head_Columns is Cells (1 .. 5);
   -- Tables are flattened in SQL column order; no count or magnitude cap.
   type Length_Result is record
      Valid : Boolean := False;
      Needed : E.Count := 0;
   end record;
   function Delta_Length
     (Data : E.Bytes; Event : Event_Columns; Roots, Subjects, Alternatives,
      Blobs : Cells; Head : Head_Columns; Head_Message : E.Span)
      return Length_Result with Global => null;
   procedure Encode_Delta
     (Data : E.Bytes; Event : Event_Columns; Roots, Subjects, Alternatives,
      Blobs : Cells; Head : Head_Columns; Head_Message : E.Span;
      Output : out E.Bytes; Length : out Length_Result; Complete : out Boolean)
   with Global => null, Always_Terminates,
     Post => Length = Delta_Length
       (Data, Event, Roots, Subjects, Alternatives, Blobs, Head, Head_Message)
       and then Complete = (Length.Valid and then Length.Needed <= Output'Length);

   type Node_Kind is (Copy_Archive, Text_Node, Bytes_Node, Null_Node);
   type Node is record
      Kind : Node_Kind := Null_Node;
      Payload : E.Span := (1, 0);
   end record;
   type Member is record
      Name : E.Span;
      Value : Node;
   end record;
   type Members is array (Q.Byte_Index range <>) of Member;
   -- Names are raw UTF8/surrogatepass bytes; copied nodes are independently
   -- rooted ORIGINAL scoped archive subtrees, not decoded/projected values.
   function Dictionary_Length (Data : E.Bytes; Fields : Members)
      return Length_Result with Global => null;
   procedure Encode_Dictionary
     (Data : E.Bytes; Fields : Members; Output : out E.Bytes;
      Length : out Length_Result; Complete : out Boolean)
   with Global => null, Always_Terminates,
     Post => Length = Dictionary_Length (Data, Fields) and then
       Complete = (Length.Valid and then Length.Needed <= Output'Length);
   function Base_Length (Data : E.Bytes; Row : C.Event_Row)
      return Length_Result with Global => null;
   procedure Encode_Base
     (Data : E.Bytes; Row : C.Event_Row; Output : out E.Bytes;
      Length : out Length_Result; Complete : out Boolean)
   with Global => null, Always_Terminates,
     Post => Length = Base_Length (Data, Row) and then
       Complete = (Length.Valid and then Length.Needed <= Output'Length);
   function Head_Length (Data : E.Bytes; Event_Id, Genesis_Row : E.Span)
      return Length_Result with Global => null;
   procedure Encode_Event_Head
     (Data : E.Bytes; Event_Id, Genesis_Row : E.Span; Output : out E.Bytes;
      Length : out Length_Result; Complete : out Boolean)
   with Global => null, Always_Terminates,
     Post => Length = Head_Length (Data, Event_Id, Genesis_Row) and then
       Complete = (Length.Valid and then Length.Needed <= Output'Length);
   -- Single-object construction: sources must lie in the occupied prefix.
   -- Used is a byte count relative to Arena'First, not an absolute index.
   -- Insufficient capacity or invalid source geometry leaves Arena/Used intact.
   function Base_In_Prefix
     (Arena : E.Bytes; Row : C.Event_Row; Used : E.Count) return Boolean
     with Global => null;
   function Head_In_Prefix
     (Arena : E.Bytes; Event_Id, Genesis_Row : E.Span; Used : E.Count)
      return Boolean with Global => null;
   procedure Append_Base
     (Arena : in out E.Bytes; Row : C.Event_Row; Used : in out E.Count;
      Length : out Length_Result; Complete : out Boolean)
   with Global => null, Always_Terminates,
     Post => Length =
       (if Base_In_Prefix (Arena, Row, Used'Old) then Base_Length (Arena, Row)
        else Length_Result'(False, 0))
       and then Complete =
         (Used'Old <= Arena'Length and then Length.Valid and then
          Length.Needed <= Arena'Length - Used'Old)
       and then Used =
         (if Complete then Used'Old + Length.Needed else Used'Old)
       and then (for all I in Arena'Range =>
         (if I - Arena'First < Used'Old or else I - Arena'First >= Used then
            Arena (I) = Arena'Old (I)));
   procedure Append_Event_Head
     (Arena : in out E.Bytes; Event_Id, Genesis_Row : E.Span;
      Used : in out E.Count; Length : out Length_Result; Complete : out Boolean)
   with Global => null, Always_Terminates,
     Post => Length =
       (if Head_In_Prefix (Arena, Event_Id, Genesis_Row, Used'Old) then
          Head_Length (Arena, Event_Id, Genesis_Row)
        else Length_Result'(False, 0))
       and then Complete =
         (Used'Old <= Arena'Length and then Length.Valid and then
          Length.Needed <= Arena'Length - Used'Old)
       and then Used =
         (if Complete then Used'Old + Length.Needed else Used'Old)
       and then (for all I in Arena'Range =>
         (if I - Arena'First < Used'Old or else I - Arena'First >= Used then
            Arena (I) = Arena'Old (I)));
   type Event_Digest_Result (Present : Boolean := False) is record
      case Present is
         when True => Event_Id, Mac : C.SHA.Digest;
         when False => null;
      end case;
   end record;
   -- Actual original whole-base hash and domain-separated whole-key MAC.
   -- This constructs cryptographic bytes, not X4/X5 validation or Legal.
   function Event_Digests (Data : E.Bytes; Key, Base_Archive : E.Span)
      return Event_Digest_Result
   with Global => null,
     Post => Event_Digests'Result.Present =
       (E.C.P.Valid (Data, Key) and then E.C.P.Valid (Data, Base_Archive))
       and then (if Event_Digests'Result.Present then
         Event_Digests'Result.Event_Id = C.G.Hash (Data, Base_Archive) and then
         Event_Digests'Result.Mac = C.G.Mac (Data, Key, Base_Archive));
   -- Length-only Output(1 .. 0) is admitted. Short buffers receive a prefix;
   -- only Complete marks a complete encoding, never a legal/authentic event.
   -- Needed=0/Valid=False means invalid spans/widths or host extent overflow,
   -- not a numeric-domain refusal. Inputs are never numerically converted.
end Worldline.Custody_V2_Delta_Encoding;

with Worldline.Custody_V2_Empty_Seed;
with Worldline.Root_Custody_Row_Schema;
-- Complete retained row bytes, not caller-supplied decoded permission flags.
-- Final positive status excludes JSON genesis correspondence and X5 Legal/fold.
package Worldline.Custody_V2_Archive_Chain with SPARK_Mode is
   package G renames Worldline.Custody_V2_Empty_Seed;
   package S renames G.S;
   package E renames G.E;
   package SHA renames G.SHA;
   package RS renames Worldline.Root_Custody_Row_Schema;
   use type E.Count;
   use type SHA.Digest;
   type Event_Row is record
      Event_Id, Previous, Generation, Operation, Subject_Kind, Subject,
      Subgeneration, Kind, Actor, Record_Archive, Base_Archive, Mac : E.Span;
   end record;
   type Event_Rows is array (E.Q.Byte_Index range <>) of Event_Row;
   type Optional_Span (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : E.Span;
      end case;
   end record;
   type Head_Row is record
      Name, Kind, Mac, Message : E.Span;
      Event_Id, Origin : Optional_Span;
   end record;
   type Head_Rows is array (E.Q.Byte_Index range <>) of Head_Row;
   type Status is (Invalid_Operands, Genesis_Mismatch, Genesis_Mac,
      Row_Malformed, Row_Link, Row_Id, Row_Duplicate, Row_Mac,
      Head_Kind, Head_Value, Head_Mac,
      Archive_Chain_Matches_Genesis_JSON_And_Fold_Open);
   type Result is record
      State : Status := Invalid_Operands;
      Failing_Row : E.Count := 0;
      Origin, Head : SHA.Digest := (others => 0);
   end record;
   function Base_Matches (Data : E.Bytes; Row : Event_Row) return Boolean
      with Global => null;
   function Verify
     (Data : E.Bytes; Key, Genesis_Row, Genesis_Message, Genesis_Mac_Text : E.Span;
      Rows : Event_Rows; Heads : Head_Rows) return Result
     with Global => null,
       Post => (if Verify'Result.State = Archive_Chain_Matches_Genesis_JSON_And_Fold_Open then
         Verify'Result.Failing_Row = 0 and then Heads'Length = 1 and then
         E.C.P.Valid (Data, Genesis_Row) and then
         Verify'Result.Origin = G.Hash (Data, Genesis_Row) and then
         (for all Row of Rows => Base_Matches (Data, Row)));

   -- X5 handoff preserves all raw ordered events and stored columns, no projection
   -- to selected/current generation. This record is INPUT only, not a fold result.
   type Fold_Operands (Event_Count, Root_Count, Subject_Count : E.Count) is record
      Events : Event_Rows (1 .. Event_Count);
      Roots : RS.Root_Rows (1 .. Root_Count);
      Subjects : RS.Subject_Rows (1 .. Subject_Count);
   end record;
end Worldline.Custody_V2_Archive_Chain;

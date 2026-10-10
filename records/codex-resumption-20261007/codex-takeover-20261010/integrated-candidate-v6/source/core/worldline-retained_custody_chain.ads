with Attest.Custody_SHA256;
with Worldline.Root_Custody_Archive_Join;

-- Original v1 retention relation only. Never v2 X4 Ready or effect permission.
package Worldline.Retained_Custody_Chain with SPARK_Mode is
   package J renames Worldline.Root_Custody_Archive_Join;
   package S renames J.S;
   package E renames S.E;
   package SHA renames Attest.Custody_SHA256;
   use type E.Count;
   type Event_Row is record
      Event_Id, Previous, Operation, Kind, Record_Archive, Mac : E.Span;
      -- Computed encoding supplied as bytes, checked against every row column.
      Base_Archive : E.Span;
   end record;
   type Event_Rows is array (E.Q.Byte_Index range <>) of Event_Row;
   type Genesis_Row is record
      Name, Value : E.Span;
   end record;
   type Genesis_Rows is array (E.Q.Byte_Index range <>) of Genesis_Row;
   type Head_Row is record
      Name, Event_Id, Mac : E.Span;
   end record;
   type Head_Rows is array (E.Q.Byte_Index range <>) of Head_Row;
   type Status is
     (Retained_Chain_Matches, Malformed_Input, Genesis_Mismatch,
      Row_Malformed, Row_Link, Row_Id, Row_Duplicate, Row_Mac,
      Head_Mismatch, Head_Archive_Mismatch, Head_Mac);
   type Result is record
      State : Status := Malformed_Input;
      -- Original array index on row failure; zero for non-row outcomes.
      Failing_Row : E.Count := 0;
      Origin, Head : SHA.Digest := (others => 0);
   end record;
   -- Genesis_Archive is the original archive(owner-bound parsed genesis), not
   -- raw JSON. Its provenance, SQL types/schema, transaction completeness and
   -- lock ownership must be established by the authentic producer separately.
   -- Empty row arrays are admitted only with exact original genesis/head joins.
   function Verify
     (Data : E.Bytes; Key, Genesis_Archive, Head_Archive : E.Span;
      Genesis : Genesis_Rows; Rows : Event_Rows; Heads : Head_Rows)
      return Result with Global => null,
        Post =>
          (if Verify'Result.State in Row_Malformed | Row_Link | Row_Id |
               Row_Duplicate | Row_Mac
           then Verify'Result.Failing_Row in Rows'Range
           else Verify'Result.Failing_Row = 0);
end Worldline.Retained_Custody_Chain;

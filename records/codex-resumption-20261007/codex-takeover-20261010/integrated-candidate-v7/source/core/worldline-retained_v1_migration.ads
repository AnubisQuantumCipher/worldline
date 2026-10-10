with Worldline.Retained_Custody_Chain;
with Worldline.Custody_V2_Empty_Seed;
package Worldline.Retained_V1_Migration with SPARK_Mode is
   package C renames Worldline.Retained_Custody_Chain;
   package E renames C.E;
   package G renames Worldline.Custody_V2_Empty_Seed;
   use type E.Count;
   use type E.Q.Byte;
   use type C.Status;
   function Literal (Data : E.Bytes; Item : E.Span; Value : String) return Boolean is
     (E.C.P.Valid (Data, Item) and then Item.Length = Value'Length and then
      (for all I in Value'Range => Data (Item.First + E.Count (I - Value'First)) = Character'Pos (Value (I))))
     with Global => null;
   function Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (E.C.P.Valid (Data, Left) and then E.C.P.Valid (Data, Right) and then
      Left.Length = Right.Length and then
      (if Left.Length > 0 then
        (for all I in E.Count range 0 .. Left.Length - 1 => Data (Left.First + I) = Data (Right.First + I))))
     with Global => null;
   function Terminal (Data : E.Bytes; Row : C.Event_Row) return Boolean is
     (Literal (Data, Row.Kind, "HISTORICAL_SETTLEMENT") or else
      Literal (Data, Row.Kind, "FRONT_RECONSTRUCTION")) with Global => null;
   function Last_For_Operation
     (Data : E.Bytes; Rows : C.Event_Rows; Position : E.Q.Byte_Index) return Boolean is
     (for all I in Rows'Range =>
        (if I > Position then not Same (Data, Rows (Position).Operation, Rows (I).Operation)))
     with Global => null, Pre => Position in Rows'Range;
   function Closed_Operations (Data : E.Bytes; Rows : C.Event_Rows) return Boolean is
     ((for all Row of Rows => E.C.P.Valid (Data, Row.Operation) and then E.C.P.Valid (Data, Row.Kind)) and then
      (for all I in Rows'Range =>
        (if Last_For_Operation (Data, Rows, I) then Terminal (Data, Rows (I)))))
     with Global => null;

   type Artifact is (Descriptor, Plan, Genesis_File, Journal_File, Issuer_Key);
   type Artifact_Input is record
      Raw, Actual_Path, Retained_Path, Retained_SHA256 : E.Span;
   end record;
   type Context_Inputs is array (Artifact) of Artifact_Input;
   -- Retained paths/digests/head are raw operands selected from prior context,
   -- not authenticity flags. The producer must bind them to genuine v2 DATA.
   function Context_Matches
     (Data : E.Bytes; Context : Context_Inputs; Genesis_Archive, Installation : E.Span)
      return Boolean with Global => null;
   type Status is (Retained_Chain_Refused, Prior_Context_Differs,
                   Operation_Not_Closed, Closed_V1_Value_Source_Join_Open);
   type Decision is record
      State : Status;
      Position : E.Count;
      Chain : C.Result;
   end record;
   function Decide
     (Data : E.Bytes; Context : Context_Inputs; Installation, Genesis_Archive,
      Head_Archive, Retained_Head : E.Span; Genesis : C.Genesis_Rows;
      Rows : C.Event_Rows; Heads : C.Head_Rows) return Decision
     with Global => null,
       Post =>
         (Decide'Result.State = Closed_V1_Value_Source_Join_Open) =
           (C.Verify (Data, Context (Issuer_Key).Raw, Genesis_Archive, Head_Archive,
                      Genesis, Rows, Heads).State = C.Retained_Chain_Matches and then
            Context_Matches (Data, Context, Genesis_Archive, Installation) and then
            Heads'Length = 1 and then Same (Data, Heads (Heads'First).Event_Id, Retained_Head)
            and then Closed_Operations (Data, Rows));
end Worldline.Retained_V1_Migration;

with Worldline.Root_Custody_Row_Schema;
-- Final full-row equality subrelation of X5, not a producer of legal fold rows.
-- All historical generations and inactive SQL fields remain in the comparison.
package Worldline.Custody_V2_Fold_Rows with SPARK_Mode is
   package S renames Worldline.Root_Custody_Row_Schema;
   package Q renames S.Q;
   use type Q.Byte_Count;
   function Root_Key_Same (Data : Q.Byte_Array; L, R : S.Root_Columns) return Boolean is
     (S.Same_Cell (Data, L.Generation, R.Generation)) with Global => null;
   function Subject_Key_Same (Data : Q.Byte_Array; L, R : S.Subject_Columns) return Boolean is
     (S.Same_Cell (Data, L.Generation, R.Generation) and then
      S.Same_Cell (Data, L.Kind_Of_Subject, R.Kind_Of_Subject) and then
      S.Same_Cell (Data, L.Subject, R.Subject)) with Global => null;
   function Roots_Valid (Data : Q.Byte_Array; Rows : S.Root_Rows) return Boolean is
     ((for all Row of Rows => Row.Present and then S.Root_Column_Shapes (Data, Row.Columns)) and then
      (for all I in Rows'Range =>
       (for all J in Rows'Range =>
        (if I /= J then not Root_Key_Same (Data, Rows (I).Columns, Rows (J).Columns)))))
     with Global => null;
   function Subjects_Valid (Data : Q.Byte_Array; Rows : S.Subject_Rows) return Boolean is
     ((for all Row of Rows => Row.Present and then S.Subject_Column_Shapes (Data, Row.Columns)) and then
      (for all I in Rows'Range =>
       (for all J in Rows'Range =>
        (if I /= J then not Subject_Key_Same (Data, Rows (I).Columns, Rows (J).Columns)))))
     with Global => null;
   function Root_Rows_Equal (Data : Q.Byte_Array; Expected, Stored : S.Root_Rows) return Boolean is
     (Roots_Valid (Data, Expected) and then Roots_Valid (Data, Stored) and then
      Expected'Length = Stored'Length and then
      (for all Row of Expected =>
       (for some Other of Stored => S.Same_Root_Columns (Data, Row.Columns, Other.Columns))))
     with Global => null;
   function Subject_Rows_Equal (Data : Q.Byte_Array; Expected, Stored : S.Subject_Rows) return Boolean is
     (Subjects_Valid (Data, Expected) and then Subjects_Valid (Data, Stored) and then
      Expected'Length = Stored'Length and then
      (for all Row of Expected =>
       (for some Other of Stored => S.Same_Subject_Columns (Data, Row.Columns, Other.Columns))))
     with Global => null;
   type Status is (Malformed_Expected_Roster, Malformed_Stored_Roster,
      Root_Count_Differs, Subject_Count_Differs, Root_Row_Differs,
      Subject_Row_Differs, Complete_Rows_Equal_Not_A_Fold_Claim);
   type Result is record
      State : Status;
      Position : Q.Byte_Count;
   end record;
   function Compare
     (Data : Q.Byte_Array; Expected_Roots, Stored_Roots : S.Root_Rows;
      Expected_Subjects, Stored_Subjects : S.Subject_Rows) return Result
     with Global => null,
       Post =>
         (Compare'Result.State = Complete_Rows_Equal_Not_A_Fold_Claim) =
          (Root_Rows_Equal (Data, Expected_Roots, Stored_Roots) and then
           Subject_Rows_Equal (Data, Expected_Subjects, Stored_Subjects));
end Worldline.Custody_V2_Fold_Rows;

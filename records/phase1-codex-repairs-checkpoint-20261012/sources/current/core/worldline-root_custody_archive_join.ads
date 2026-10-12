with Worldline.Scoped_Archive;
--  Native correspondence to ORIGINAL v1 _load's complete base construction.
--  This is the retained-v1 operand join needed by V5-J.4, not v2 X4 Ready.
package Worldline.Root_Custody_Archive_Join with SPARK_Mode is
   package S renames Worldline.Scoped_Archive;
   package E renames S.E;
   use type E.Count;
   function V1_Base_Matches
     (Data : E.Bytes; Base, Previous, Operation, Kind, Record_Archive : E.Span)
      return Boolean is
     (S.Valid (Data, Base) and then S.Member_Count (Data, Base) = 4 and then
      S.Member_Name_Is (Data, Base, 0, "previous") and then
      S.Member_Name_Is (Data, Base, 1, "operation") and then
      S.Member_Name_Is (Data, Base, 2, "kind") and then
      S.Member_Name_Is (Data, Base, 3, "record") and then
      S.Text_Matches (Data, S.Field (Data, Base, "previous"), Previous) and then
      S.Text_Matches (Data, S.Field (Data, Base, "operation"), Operation) and then
      S.Text_Matches (Data, S.Field (Data, Base, "kind"), Kind) and then
      S.Valid (Data, Record_Archive) and then
      S.A.Same_Encoding (Data, S.Field (Data, Base, "record"), Record_Archive))
   with Global => null;
end Worldline.Root_Custody_Archive_Join;

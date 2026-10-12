package body Worldline.Custody_V2_Fold_Rows with SPARK_Mode is
   function Compare
     (Data : Q.Byte_Array; Expected_Roots, Stored_Roots : S.Root_Rows;
      Expected_Subjects, Stored_Subjects : S.Subject_Rows) return Result is
   begin
      if not Roots_Valid (Data, Expected_Roots) or else not Subjects_Valid (Data, Expected_Subjects) then
         return (Malformed_Expected_Roster, 0);
      end if;
      if not Roots_Valid (Data, Stored_Roots) or else not Subjects_Valid (Data, Stored_Subjects) then
         return (Malformed_Stored_Roster, 0);
      end if;
      if Expected_Roots'Length /= Stored_Roots'Length then return (Root_Count_Differs, 0); end if;
      if Expected_Subjects'Length /= Stored_Subjects'Length then return (Subject_Count_Differs, 0); end if;
      for I in Expected_Roots'Range loop
         pragma Loop_Invariant
           (for all J in Expected_Roots'First .. I - 1 =>
            (for some Other of Stored_Roots =>
             S.Same_Root_Columns (Data, Expected_Roots (J).Columns, Other.Columns)));
         if not (for some Other of Stored_Roots =>
           S.Same_Root_Columns (Data, Expected_Roots (I).Columns, Other.Columns)) then
            return (Root_Row_Differs, I);
         end if;
      end loop;
      for I in Expected_Subjects'Range loop
         pragma Loop_Invariant
           (for all J in Expected_Subjects'First .. I - 1 =>
            (for some Other of Stored_Subjects =>
             S.Same_Subject_Columns (Data, Expected_Subjects (J).Columns, Other.Columns)));
         if not (for some Other of Stored_Subjects =>
           S.Same_Subject_Columns (Data, Expected_Subjects (I).Columns, Other.Columns)) then
            return (Subject_Row_Differs, I);
         end if;
      end loop;
      return (Complete_Rows_Equal_Not_A_Fold_Claim, 0);
   end Compare;
end Worldline.Custody_V2_Fold_Rows;

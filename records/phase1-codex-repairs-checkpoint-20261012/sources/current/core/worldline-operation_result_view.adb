with Worldline.Operation_Result_Relations;
package body Worldline.Operation_Result_View with SPARK_Mode is
   package M renames Worldline.Operation_Result_Relations;
   use type V.T.A.C.Chain_Row;
   function Expected (Raw : V.T.Raw_Input; Data : V.Q.Byte_Array;
     Grants : V.Raw_Grant_Array; Uses : V.Raw_Use_Array;
     Receipts, Events : V.Raw_Chain_Array) return V.Result is
      package T renames V.T;
      R : T.A.C.Retained_Rows (Receipts'Range);
      E : T.A.C.Retained_Rows (Events'Range);
   begin
      if not T.Well_Formed (Raw) or else not T.Recovery_Well_Formed (Data, Raw.Facts)
        or else not (for all I in Grants'Range => T.Well_Formed (Grants (I)))
        or else not (for all I in Uses'Range => T.Well_Formed (Uses (I)))
        or else not (for all I in Receipts'Range => T.C.Well_Formed (Receipts (I)))
        or else not (for all I in Events'Range => T.C.Well_Formed (Events (I)))
      then return V.Rejected; end if;
      for I in R'Range loop
         R (I) := T.C.Decode (Receipts (I));
         pragma Loop_Invariant (for all K in R'First .. I => R (K) = T.C.Decode (Receipts (K)));
      end loop;
      for I in E'Range loop
         E (I) := T.C.Decode (Events (I));
         pragma Loop_Invariant (for all K in E'First .. I => E (K) = T.C.Decode (Events (K)));
      end loop;
      return (Well_Formed => True, Status => M.Reason'Pos
        (M.Assess (Data, T.Decode (Raw.Bound), T.Decode (Data, Raw.Facts), R, E)));
   end Expected;
   function Check (Raw : V.T.Raw_Input; Data : V.Q.Byte_Array;
     Grants : V.Raw_Grant_Array; Uses : V.Raw_Use_Array;
     Receipts, Events : V.Raw_Chain_Array) return V.Result is
      package T renames V.T;
      R : T.A.C.Retained_Rows (Receipts'Range);
      E : T.A.C.Retained_Rows (Events'Range);
   begin
      if not T.Well_Formed (Raw) or else not T.Recovery_Well_Formed (Data, Raw.Facts)
        or else not (for all I in Grants'Range => T.Well_Formed (Grants (I)))
        or else not (for all I in Uses'Range => T.Well_Formed (Uses (I)))
        or else not (for all I in Receipts'Range => T.C.Well_Formed (Receipts (I)))
        or else not (for all I in Events'Range => T.C.Well_Formed (Events (I)))
      then return V.Rejected; end if;
      for I in R'Range loop
         R (I) := T.C.Decode (Receipts (I));
         pragma Loop_Invariant (for all K in R'First .. I => R (K) = T.C.Decode (Receipts (K)));
      end loop;
      for I in E'Range loop
         E (I) := T.C.Decode (Events (I));
         pragma Loop_Invariant (for all K in E'First .. I => E (K) = T.C.Decode (Events (K)));
      end loop;
      return (Well_Formed => True, Status => M.Reason'Pos
        (M.Assess (Data, T.Decode (Raw.Bound), T.Decode (Data, Raw.Facts), R, E)));
   end Check;
end Worldline.Operation_Result_View;

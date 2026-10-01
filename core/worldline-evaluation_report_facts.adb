package body Worldline.Evaluation_Report_Facts with SPARK_Mode is
   function Report_Integrity_Of
     (Report_Based : Boolean;
      Value        : Classified_Value;
      Facts        : Report_Facts) return E.Report_Integrity
   is
   begin
      if not Report_Based then
         return E.Not_Applicable;
      end if;
      if Value.Execution /= E.Completed
        or else Value.Bundle /= Bundle_Verified
      then
         return E.Untrusted_Report;
      end if;
      if not All_Facts (Facts) then
         return E.Untrusted_Report;
      end if;
      return E.Verified_Report;
   end Report_Integrity_Of;

   function Confined_Report_Integrity_Of
     (Report_Based : Boolean;
      Value        : Classified_Value;
      Facts        : Report_Facts;
      Confinement  : Confinement_Observation) return E.Report_Integrity
   is
      Integrity : constant E.Report_Integrity :=
        Report_Integrity_Of (Report_Based, Value, Facts);
   begin
      if Integrity = E.Verified_Report
        and then Confinement /= Confinement_Established
      then
         return E.Untrusted_Report;
      end if;
      return Integrity;
   end Confined_Report_Integrity_Of;
end Worldline.Evaluation_Report_Facts;

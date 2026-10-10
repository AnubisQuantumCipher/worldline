with Worldline.Evaluation;

--  The D26 report-integrity dependency, strengthened by the v6 requirement
--  that an audit observation never substitutes for established confinement.
--  This unit consumes observations; it does not authenticate their producers.
package Worldline.Evaluation_Report_Facts with SPARK_Mode is
   package E renames Worldline.Evaluation;
   use type E.Execution_State;
   use type E.Report_Integrity;

   --  Preserve the full planned bundle domain without changing the legacy
   --  Evaluation ABI before its complete, separately reviewed migration.
   type Bundle_Observation is
     (Bundle_Not_Covered, Bundle_Verified, Bundle_Compromised,
      Bundle_Unknown, Bundle_Unbound);

   type Classified_Value is record
      Execution : E.Execution_State;
      Result    : E.Outcome;
      Bundle    : Bundle_Observation;
   end record;

   type Report_Facts is record
      Private_Profile          : Boolean;
      Exit_Integer_Nonnegative : Boolean;
      Records_Present          : Boolean;
      Channel_Daemon_Accepted   : Boolean;
      Supervision_Clean        : Boolean;
      Boundary_Consistent      : Boolean;
      Report_Mount_Exclusive   : Boolean;
      Collected_Privately      : Boolean;
      Identities_Match         : Boolean;
      Digest_Matches           : Boolean;
      Examiner_Observed        : Boolean;
      Workers_Separated        : Boolean;
      Status_Rederived          : Boolean;
      Examiner_Audit_Clean      : Boolean;
   end record;

   --  Absence of measurement and an observed negative are distinct. This is
   --  still a supplied observation, not proof of custody or confinement.
   type Confinement_Observation is
     (Confinement_Unmeasured, Confinement_Not_Established,
      Confinement_Established);

   function All_Facts (Facts : Report_Facts) return Boolean is
     (Facts.Private_Profile
      and then Facts.Exit_Integer_Nonnegative
      and then Facts.Records_Present
      and then Facts.Channel_Daemon_Accepted
      and then Facts.Supervision_Clean
      and then Facts.Boundary_Consistent
      and then Facts.Report_Mount_Exclusive
      and then Facts.Collected_Privately
      and then Facts.Identities_Match
      and then Facts.Digest_Matches
      and then Facts.Examiner_Observed
      and then Facts.Workers_Separated
      and then Facts.Status_Rederived
      and then Facts.Examiner_Audit_Clean)
     with Global => null;

   --  A closed, independent semantic equation. D26 intentionally accepts the
   --  complete classification product, including every Result value; report
   --  integrity does not manufacture or replace the evaluation verdict.
   function Expected_Integrity
     (Report_Based : Boolean;
      Value        : Classified_Value;
      Facts        : Report_Facts) return E.Report_Integrity is
     (if not Report_Based then E.Not_Applicable
      elsif Value.Execution = E.Completed
        and then Value.Bundle = Bundle_Verified
        and then All_Facts (Facts)
      then E.Verified_Report
      else E.Untrusted_Report)
     with Global => null;

   function Report_Integrity_Of
     (Report_Based : Boolean;
      Value        : Classified_Value;
      Facts        : Report_Facts) return E.Report_Integrity
     with Global => null,
          Post =>
            Report_Integrity_Of'Result =
              Expected_Integrity (Report_Based, Value, Facts)
            and then
              ((Report_Integrity_Of'Result = E.Not_Applicable) =
                 (not Report_Based))
            and then
              (if Report_Integrity_Of'Result = E.Verified_Report then
                 Report_Based
                 and then Value.Execution = E.Completed
                 and then Value.Bundle = Bundle_Verified
                 and then All_Facts (Facts));

   --  The original D26 equation remains exact above. A consumer making the
   --  stronger v6 confinement claim must additionally use this closed gate;
   --  the syntactic audit fact alone cannot satisfy it.
   function Expected_Confined_Integrity
     (Report_Based : Boolean;
      Value        : Classified_Value;
      Facts        : Report_Facts;
      Confinement  : Confinement_Observation) return E.Report_Integrity is
     (if Expected_Integrity (Report_Based, Value, Facts) = E.Verified_Report
        and then Confinement /= Confinement_Established
      then E.Untrusted_Report
      else Expected_Integrity (Report_Based, Value, Facts))
     with Global => null;

   function Confined_Report_Integrity_Of
     (Report_Based : Boolean;
      Value        : Classified_Value;
      Facts        : Report_Facts;
      Confinement  : Confinement_Observation) return E.Report_Integrity
     with Global => null,
          Post =>
            Confined_Report_Integrity_Of'Result =
              Expected_Confined_Integrity
                (Report_Based, Value, Facts, Confinement)
            and then
              (if Confined_Report_Integrity_Of'Result = E.Verified_Report then
                 Report_Integrity_Of (Report_Based, Value, Facts) =
                   E.Verified_Report
                 and then Confinement = Confinement_Established);
end Worldline.Evaluation_Report_Facts;

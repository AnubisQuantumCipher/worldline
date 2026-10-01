package body Worldline.Evaluation_V2 with SPARK_Mode is

   function Transition_Allowed
     (From_State, To_State : Execution_State) return Boolean is
   begin
      case From_State is
         when Not_Attempted =>
            return To_State = Prepared;
         when Prepared =>
            return To_State in Started | Interrupted | Error_Before_Examiner |
              Incomplete_Unknown | Unclassified;
         when Started =>
            return To_State in Completed | Interrupted | Incomplete_Unknown |
              Evaluator_Incomplete | Unclassified;
         when Terminal_State =>
            return False;
      end case;
   end Transition_Allowed;

   procedure Advance
     (State : in out Execution_State; Requested : Execution_State) is
   begin
      if Transition_Allowed (State, Requested) then
         State := Requested;
      end if;
   end Advance;

   function Classify (Facts : Observations) return Classification is
      Answer : Classification :=
        (Execution => Unclassified, Result => No_Outcome,
         Bundle => Bundle_Of (Facts));
   begin
      if Facts.Channel = Malformed_Channel then
         null;
      elsif Facts.Source = Engine then
         if Facts.Status in Pass_Status | Fail_Status
           and not Facts.Exit_Present
           and Facts.Channel in Absent_Channel | Empty_Channel
           and not Facts.Bundle_Present
         then
            Answer.Execution := Completed;
         end if;
      elsif Facts.Source = Agent then
         if Facts.Supervisor = Supervised
           and not Facts.Supervisor_Stopped
           and Facts.Exit_Integer
           and Facts.Status in Pass_Status | Fail_Status
         then
            Answer.Execution := Completed;
         elsif Facts.Supervisor in No_Supervision | Stopped
           or Facts.Supervisor_Stopped
         then
            Answer.Execution := Interrupted;
         else
            Answer.Execution := Incomplete_Unknown;
         end if;
      elsif Facts.Status = Unassessed_Status
        or (Facts.Status = Absent_Status
            and not Facts.Exit_Present
            and Facts.Channel in Absent_Channel | Empty_Channel)
      then
         Answer.Execution := Not_Attempted;
      elsif Facts.Channel = Rejected_Channel then
         case Facts.Stage is
            when Never_Started =>
               Answer.Execution := Error_Before_Examiner;
            when Manager_Stopped | Harness_Signalled =>
               Answer.Execution := Interrupted;
            when others => Answer.Execution := Incomplete_Unknown;
         end case;
      elsif Facts.Channel = Accepted_Channel
        and Facts.Exit_Integer
        and Facts.Status in Pass_Status | Fail_Status
      then
         if Facts.Supervisor = Stopped or Facts.Supervisor_Stopped then
            Answer.Execution := Interrupted;
         elsif Facts.Supervisor /= Supervised then
            Answer.Execution := Incomplete_Unknown;
         elsif Facts.Isolation = Shared_Process then
            Answer.Execution := Evaluator_Incomplete;
         else
            Answer.Execution := Completed;
         end if;
      elsif not Facts.Exit_Present
        and (Facts.Bundle_Present or Facts.Status /= Absent_Status)
      then
         Answer.Execution := Incomplete_Unknown;
      end if;

      --  A failure from an examiner whose staged bundle cannot satisfy its own
      --  module-level imports is not a verdict on the candidate.
      if Answer.Execution = Completed
        and Facts.Unsatisfied_Imports
        and (Facts.Status = Fail_Status
          or (Facts.Source = External and Facts.Status = Pass_Status))
      then
         Answer.Execution := Evaluator_Incomplete;
      end if;

      if Answer.Execution = Completed then
         Answer.Result :=
           (if Facts.Status = Pass_Status then Passed else Failed);
      end if;

      return Answer;
   end Classify;

   function Admissible
     (Value    : Classification;
      Report   : Report_Integrity;
      Presence : Evidence_Presence) return Boolean is
   begin
      return Value.Execution = Completed
        and Value.Result = Passed
        and Value.Bundle in Not_Covered | Verified
        and Report in Not_Applicable | Verified_Report
        and Evidence_Complete (Presence);
   end Admissible;

   function Report_Integrity_Of
     (Report_Based : Boolean; Value : Classification; Facts : Report_Facts)
      return Report_Integrity is
   begin
      if not Report_Based then return Not_Applicable; end if;
      if Value.Execution = Completed and Value.Bundle = Verified
        and All_Facts (Facts) then return Verified_Report; end if;
      return Untrusted_Report;
   end Report_Integrity_Of;

   function Confined_Report_Integrity_Of
     (Report_Based : Boolean; Value : Classification; Facts : Report_Facts;
      Confinement : Confinement_Observation) return Report_Integrity
   is
      Report : constant Report_Integrity := Report_Integrity_Of (Report_Based, Value, Facts);
   begin
      if Report = Verified_Report and Confinement /= F.Confinement_Established then
         return Untrusted_Report;
      end if;
      return Report;
   end Confined_Report_Integrity_Of;

   function Roster_Complete
     (Admitted : Admissions; Empty_Declared, Completion_Admitted : Boolean)
      return Boolean is
   begin
      if not Completion_Admitted then return False; end if;
      if Admitted'Length = 0 then return Empty_Declared; end if;
      for I in Admitted'Range loop
         if not Admitted (I) then return False; end if;
         pragma Loop_Invariant (for all J in Admitted'First .. I => Admitted (J));
      end loop;
      return True;
   end Roster_Complete;
end Worldline.Evaluation_V2;

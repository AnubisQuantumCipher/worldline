package body Worldline.Evaluation with SPARK_Mode is

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
         when others =>
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
         Bundle => Not_Covered);
   begin
      if not Facts.Bundle_Present then
         Answer.Bundle := Not_Covered;
      elsif not Facts.Bundle_Is_Mapping then
         Answer.Bundle := Unknown_Integrity;
      elsif Facts.Bundle_Stable and not Facts.Bundle_Changed then
         Answer.Bundle := Verified;
      else
         Answer.Bundle := Compromised;
      end if;

      if Facts.Channel = Malformed_Channel then
         null;
      elsif Facts.Source = Engine then
         if Facts.Status in Pass_Status | Fail_Status
           and not Facts.Exit_Present
           and Facts.Channel in Absent_Channel | Empty_Channel
           and not Facts.Bundle_Present
         then
            Answer.Execution := Completed;
            Answer.Result :=
              (if Facts.Status = Pass_Status then Passed else Failed);
         end if;
      elsif Facts.Source = Agent then
         if Facts.Supervisor = Supervised
           and not Facts.Supervisor_Stopped
           and Facts.Exit_Integer
           and Facts.Status in Pass_Status | Fail_Status
         then
            Answer.Execution := Completed;
            Answer.Result :=
              (if Facts.Status = Pass_Status then Passed else Failed);
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
         if Facts.Unsatisfied_Imports and Facts.Status /= Pass_Status then
            Answer.Execution := Evaluator_Incomplete;
         else
            Answer.Execution := Completed;
            Answer.Result :=
              (if Facts.Status = Pass_Status then Passed else Failed);
         end if;
      elsif not Facts.Exit_Present
        and (Facts.Bundle_Present or Facts.Status /= Absent_Status)
      then
         Answer.Execution := Incomplete_Unknown;
      end if;

      return Answer;
   end Classify;

   function Admissible
     (Value : Classification;
      Report : Report_Integrity;
      Evidence_Complete : Boolean) return Boolean is
   begin
      return Value.Execution = Completed
        and Value.Result = Passed
        and Value.Bundle in Not_Covered | Verified
        and Report in Not_Applicable | Verified_Report
        and Evidence_Complete;
   end Admissible;

end Worldline.Evaluation;

package Worldline.Evaluation with SPARK_Mode is

   --  A new attempt requires a new evaluation identity. Terminal states never
   --  transition back into a live attempt under the same identity.
   type Execution_State is
     (Not_Attempted, Prepared, Started, Interrupted,
      Error_Before_Examiner, Incomplete_Unknown,
      Evaluator_Incomplete, Unclassified, Completed);

   type Outcome is (No_Outcome, Passed, Failed);
   type Bundle_Integrity is
     (Not_Covered, Verified, Compromised, Unknown_Integrity);
   type Report_Integrity is
     (Not_Applicable, Verified_Report, Untrusted_Report);

   function Transition_Allowed
     (From_State, To_State : Execution_State) return Boolean
     with Global => null,
          Post =>
            (if From_State in Interrupted | Error_Before_Examiner |
                 Incomplete_Unknown | Evaluator_Incomplete |
                 Unclassified | Completed
             then not Transition_Allowed'Result);

   procedure Advance
     (State : in out Execution_State; Requested : Execution_State)
     with Post =>
       State =
         (if Transition_Allowed (State'Old, Requested)
          then Requested else State'Old);

   --  C/Python translates observable categories into this finite record. That
   --  translation and the provenance of each observation remain outside proof.
   type Origin is (Engine, Agent, External);
   type Raw_Status is (Absent_Status, Pass_Status, Fail_Status,
                       Unassessed_Status, Other_Status);
   type Channel_State is
     (Absent_Channel, Empty_Channel, Accepted_Channel,
      Rejected_Channel, Other_Channel, Malformed_Channel);
   type Rejection_Stage is
     (No_Stage, Never_Started, Manager_Stopped, Harness_Signalled,
      Other_Stage);
   type Supervision_State is
     (No_Supervision, Supervised, Stopped, Other_Supervision);

   type Observations is record
      Source              : Origin;
      Status              : Raw_Status;
      Channel             : Channel_State;
      Stage               : Rejection_Stage;
      Exit_Present        : Boolean;
      Exit_Integer        : Boolean;
      Supervisor          : Supervision_State;
      Supervisor_Stopped  : Boolean;
      Bundle_Present      : Boolean;
      Bundle_Is_Mapping   : Boolean;
      Bundle_Stable       : Boolean;
      Bundle_Changed      : Boolean;
      Unsatisfied_Imports : Boolean;
   end record;

   type Classification is record
      Execution : Execution_State;
      Result    : Outcome;
      Bundle    : Bundle_Integrity;
   end record;

   function Classify (Facts : Observations) return Classification
     with Global => null,
          Post =>
            (Classify'Result.Execution = Completed) =
              (Classify'Result.Result /= No_Outcome);

   --  This is the sole per-check promotion predicate. Evidence_Complete is a
   --  separate roster fact supplied by the caller; the kernel never infers it
   --  from a missing result or a default value.
   function Admissible
     (Value : Classification;
      Report : Report_Integrity;
      Evidence_Complete : Boolean) return Boolean
     with Global => null,
          Post =>
            Admissible'Result =
              (Value.Execution = Completed
               and Value.Result = Passed
               and Value.Bundle in Not_Covered | Verified
               and Report in Not_Applicable | Verified_Report
               and Evidence_Complete);

end Worldline.Evaluation;

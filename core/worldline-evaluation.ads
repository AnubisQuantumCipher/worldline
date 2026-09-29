package Worldline.Evaluation with SPARK_Mode is

   --  A new attempt requires a new evaluation identity. Terminal states never
   --  transition back into a live attempt under the same identity.
   type Execution_State is
     (Not_Attempted, Prepared, Started, Interrupted,
      Error_Before_Examiner, Incomplete_Unknown,
      Evaluator_Incomplete, Unclassified, Completed);

   subtype Terminal_State is Execution_State range Interrupted .. Completed;

   type Outcome is (No_Outcome, Passed, Failed);
   type Bundle_Integrity is
     (Not_Covered, Verified, Compromised, Unknown_Integrity);
   type Report_Integrity is
     (Not_Applicable, Verified_Report, Untrusted_Report);

   --  The whole lifecycle relation, stated as the contract rather than left
   --  in the body: Completed is reachable only from Started, an examiner can
   --  only be reached from Prepared, and every terminal state is final.
   function Transition_Allowed
     (From_State, To_State : Execution_State) return Boolean
     with Global => null,
          Post =>
            Transition_Allowed'Result =
              (case From_State is
                 when Not_Attempted => To_State = Prepared,
                 when Prepared =>
                   To_State in Started | Interrupted |
                     Error_Before_Examiner | Incomplete_Unknown |
                     Unclassified,
                 when Started =>
                   To_State in Completed | Interrupted |
                     Incomplete_Unknown | Evaluator_Incomplete |
                     Unclassified,
                 when Terminal_State => False);

   procedure Advance
     (State : in out Execution_State; Requested : Execution_State)
     with Global => null,
          Post =>
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

   --  What the bundle observations mean, independent of execution.
   function Bundle_Of (Facts : Observations) return Bundle_Integrity is
     (if not Facts.Bundle_Present then Not_Covered
      elsif not Facts.Bundle_Is_Mapping then Unknown_Integrity
      elsif Facts.Bundle_Stable and not Facts.Bundle_Changed then Verified
      else Compromised)
     with Global => null;

   --  The observations that can support a completed evaluation at all. Every
   --  Completed classification satisfies this; it is necessary, not
   --  sufficient. A FAIL from an examiner whose staged bundle cannot satisfy
   --  its own module-level imports is not a verdict on the candidate. A PASS
   --  with such a gap is: the import resolved, and the analysis cannot tell a
   --  missing helper from the module under test, which a test imports.
   function Completion_Possible (Facts : Observations) return Boolean is
     (Facts.Channel /= Malformed_Channel
      and Facts.Status in Pass_Status | Fail_Status
      and not (Facts.Unsatisfied_Imports and Facts.Status = Fail_Status)
      and (case Facts.Source is
             when Engine =>
               not Facts.Exit_Present
               and Facts.Channel in Absent_Channel | Empty_Channel
               and not Facts.Bundle_Present,
             when Agent =>
               Facts.Supervisor = Supervised
               and not Facts.Supervisor_Stopped
               and Facts.Exit_Integer,
             when External =>
               Facts.Channel = Accepted_Channel and Facts.Exit_Integer))
     with Global => null;

   function Classify (Facts : Observations) return Classification
     with Global => null,
          Post =>
            --  An outcome exists exactly when the evaluation completed, and
            --  it is the recorded verdict, never a default.
            (Classify'Result.Execution = Completed) =
              (Classify'Result.Result /= No_Outcome)
            and (if Classify'Result.Execution = Completed then
                   Completion_Possible (Facts)
                   and ((Classify'Result.Result = Passed) =
                          (Facts.Status = Pass_Status)))
            --  Bundle integrity is a pure function of the bundle facts.
            and Classify'Result.Bundle = Bundle_Of (Facts)
            --  A classification never claims an attempt is still in flight.
            and Classify'Result.Execution not in Prepared | Started
            --  Named refusals (spec section 4).
            and (if Facts.Channel = Malformed_Channel then
                   Classify'Result.Execution = Unclassified)
            and (if Facts.Unsatisfied_Imports and Facts.Status = Fail_Status
                 then Classify'Result.Execution /= Completed)
            and (if Facts.Source = Agent
                   and Facts.Channel /= Malformed_Channel
                   and (Facts.Supervisor_Stopped
                        or Facts.Supervisor in No_Supervision | Stopped)
                 then Classify'Result.Execution = Interrupted)
            and (if Facts.Source = External
                   and Facts.Channel /= Malformed_Channel
                   and Facts.Status = Unassessed_Status
                 then Classify'Result.Execution = Not_Attempted)
            and (if Facts.Source = External
                   and Facts.Status = Absent_Status
                   and not Facts.Exit_Present
                   and Facts.Channel in Absent_Channel | Empty_Channel
                 then Classify'Result.Execution = Not_Attempted)
            and (if Facts.Source = External
                   and Facts.Status /= Unassessed_Status
                   and Facts.Channel = Rejected_Channel
                   and Facts.Stage = Never_Started
                 then Classify'Result.Execution = Error_Before_Examiner);

   --  Per-check evidence presence, stated as typed facts rather than inferred
   --  from whether a record happens to be non-empty.
   type Evidence_Presence is record
      Record_Identified   : Boolean;  --  the record names its check
      Verdict_Recorded    : Boolean;  --  a verdict field is present
      Binding_Established : Boolean;  --  provenance of the examiner holds
      Declaration_Matches : Boolean;  --  format/profile are the declared ones
      Bundle_Identified   : Boolean;  --  a declared bundle names what ran
   end record;

   function Evidence_Complete (Presence : Evidence_Presence) return Boolean is
     (Presence.Record_Identified
      and Presence.Verdict_Recorded
      and Presence.Binding_Established
      and Presence.Declaration_Matches
      and Presence.Bundle_Identified)
     with Global => null;

   --  This is the sole per-check promotion predicate.
   function Admissible
     (Value    : Classification;
      Report   : Report_Integrity;
      Presence : Evidence_Presence) return Boolean
     with Global => null,
          Post =>
            Admissible'Result =
              (Value.Execution = Completed
               and Value.Result = Passed
               and Value.Bundle in Not_Covered | Verified
               and Report in Not_Applicable | Verified_Report
               and Evidence_Complete (Presence));

   --  The roster: one admission verdict per required check, in policy order.
   --  An empty roster is complete only when the policy explicitly declared
   --  that nothing is required; a loop over nothing never manufactures a pass.
   subtype Roster_Index is Positive range 1 .. 4096;
   type Admissions is array (Roster_Index range <>) of Boolean;

   function Roster_Complete
     (Admitted       : Admissions;
      Empty_Declared : Boolean) return Boolean
     with Global => null,
          Post =>
            Roster_Complete'Result =
              (if Admitted'Length = 0 then Empty_Declared
               else (for all I in Admitted'Range => Admitted (I)));

end Worldline.Evaluation;

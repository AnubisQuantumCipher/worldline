with Interfaces;
with Worldline.Identities;
with Worldline.Transitions;

package Worldline.Collapse with SPARK_Mode is
   use Worldline.Identities;
   use type Interfaces.Unsigned_64;
   use type Transitions.World_State;

   --  Which question is being asked. Commit is 0, so a zeroed request asks the
   --  strict one: at Prepare the staged tree has one observation (the merge's
   --  own capture); the equality with a second, independent capture is the
   --  commit's obligation.
   type Phase is (Commit, Prepare);

   --  A measurement the runtime made, or could not make. Unmeasured never
   --  satisfies a requirement; Found refuses; only None_Found passes.
   type Measurement is (Unmeasured, None_Found, Found);

   --  Which evidence speaks for the bytes that would become live.
   --  Candidate_Evaluation: the candidate's own evaluation, fresh against the
   --  current requirement, with a complete roster and the declared verifiers
   --  executed. Checkpoint_Return: a previous reality WORLDLINE itself made
   --  live, which carries a lineage witness instead of an evaluation.
   type Evaluation_Mode is (Candidate_Evaluation, Checkpoint_Return);

   --  Every identity pair is produced from two different sources; the comment
   --  on each names them. Two absent values are never the same (Same).
   type Collapse_Request is record
      Candidate_State : Transitions.World_State;
      Request_Phase   : Phase;
      Mode            : Evaluation_Mode;
      --  Measured by the merge (conflicts) and by comparing a fresh capture of
      --  live PRIME with the PRIME record's components (foreign writes).
      Conflicts       : Measurement;
      Foreign_Writes  : Measurement;
      --  The kernel's roster verdicts (Evaluation.Roster_Complete plus the
      --  agent's exit) for the primary evaluation and, when one ran, for the
      --  evaluation of the staged merge result.
      Roster_Complete        : Boolean;
      Staged_Roster_Complete : Boolean;
      --  Store's record of the parent's content / the candidate row's claim.
      Expected_Parent, Candidate_Parent   : Optional_Content_Id;
      --  The world the promotion is about / the world the speaking evidence
      --  (or the return vehicle) was bound to.
      Expected_Subject, Evidence_Subject  : Optional_Subject_Id;
      --  The candidate row's base claim / a capture of its base payload.
      Expected_Base, Candidate_Base       : Optional_State_Root;
      --  The candidate row's delta claim / the delta recomputed now.
      Expected_Delta, Candidate_Delta     : Optional_Delta_Id;
      --  The registered root set / the candidate row's root set.
      Expected_Root_Set, Candidate_Root_Set : Optional_Root_Set_Id;
      --  The merge's capture of the staged tree / a recapture (Commit only).
      Expected_Staged_Root, Actual_Staged_Root : Optional_State_Root;
      --  Content root of the staged tree that would become live, and of the
      --  bytes the primary evaluation examined.
      Staged_Content_Root, Tested_Root    : Optional_Content_Root;
      --  The current PRIME's requirement / the one the evidence was bound to.
      Current_Requirement, Evaluated_Requirement : Optional_Requirement_Id;
      --  The policy's declared verifier roster / what the runner executed.
      Declared_Verifiers, Executed_Verifiers : Optional_Verifier_Set_Id;
      --  The staged-merge evaluation, when one ran.
      Staged_Evaluated_Requirement : Optional_Requirement_Id;
      Staged_Executed_Verifiers    : Optional_Verifier_Set_Id;
      Staged_Examined_Root         : Optional_Content_Root;
      --  The subject's own content identity / the one a DIFFERENT record states
      --  for it (its lineage child, or the PRIME register).
      Expected_Checkpoint, Witnessed_Checkpoint : Optional_Content_Id;
      --  The registered roots / the roots the PRIME watcher actually watches.
      Registered_Watch_Set, Watched_Set : Optional_Watch_Set_Id;
      --  The watcher's generation before the requirement read / just before
      --  the decision.
      Generation_Before, Generation_After : Optional_Generation;
   end record;

   type Decision is
     (Authorized,
      Invalid_Candidate,
      Parent_Mismatch,
      --  Retired in 1.9.0 and never returned (see Decide's Post): the owner
      --  pair had one producer. The evidence-subject binding replaces it, and
      --  "owner" is reserved for requester capabilities.
      Owner_Mismatch,
      Base_Mismatch,
      Delta_Mismatch,
      Root_Set_Mismatch,
      Staged_Root_Mismatch,
      Conflict,
      Foreign_Managed_Write,
      Validation_Context_Mismatch,
      Staged_Untested,
      Execution_Evidence_Incomplete,
      Verifier_Execution_Identity_Mismatch,
      Checkpoint_Unwitnessed,
      --  Appended for 1.9.0; existing ordinals are unchanged.
      Identity_Absent,
      Measurement_Absent,
      Prime_Changed,
      Watch_Incomplete,
      Checkpoint_Mismatch,
      Evidence_Subject_Mismatch);

   --  Both sides present and different: the only situation a *_Mismatch code
   --  may report.
   function Differ (L, R : Optional_Content_Id) return Boolean is
     (L.Present and then R.Present and then L.Value /= R.Value) with Global => null;
   function Differ (L, R : Optional_Subject_Id) return Boolean is
     (L.Present and then R.Present and then L.Value /= R.Value) with Global => null;
   function Differ (L, R : Optional_State_Root) return Boolean is
     (L.Present and then R.Present and then L.Value /= R.Value) with Global => null;
   function Differ (L, R : Optional_Delta_Id) return Boolean is
     (L.Present and then R.Present and then L.Value /= R.Value) with Global => null;
   function Differ (L, R : Optional_Root_Set_Id) return Boolean is
     (L.Present and then R.Present and then L.Value /= R.Value) with Global => null;
   function Differ (L, R : Optional_Requirement_Id) return Boolean is
     (L.Present and then R.Present and then L.Value /= R.Value) with Global => null;
   function Differ (L, R : Optional_Verifier_Set_Id) return Boolean is
     (L.Present and then R.Present and then L.Value /= R.Value) with Global => null;
   function Differ (L, R : Optional_Watch_Set_Id) return Boolean is
     (L.Present and then R.Present and then L.Value /= R.Value) with Global => null;
   function Differ (L, R : Optional_Generation) return Boolean is
     (L.Present and then R.Present and then L.Value /= R.Value) with Global => null;

   --  Every measurement was made.
   function Measured (R : Collapse_Request) return Boolean is
     (R.Conflicts /= Unmeasured
      and then R.Foreign_Writes /= Unmeasured
      and then R.Generation_Before.Present and then R.Generation_After.Present
      and then R.Registered_Watch_Set.Present and then R.Watched_Set.Present)
     with Global => null;

   --  Every identity the question depends on is present. Tested_Root and the
   --  witnessed checkpoint are not here: their absence has its own answer
   --  (Staged_Untested, Checkpoint_Unwitnessed).
   function Required_Present (R : Collapse_Request) return Boolean is
     (R.Expected_Parent.Present and then R.Candidate_Parent.Present
      and then R.Expected_Subject.Present and then R.Evidence_Subject.Present
      and then R.Expected_Base.Present and then R.Candidate_Base.Present
      and then R.Expected_Delta.Present and then R.Candidate_Delta.Present
      and then R.Expected_Root_Set.Present and then R.Candidate_Root_Set.Present
      and then R.Staged_Content_Root.Present
      and then R.Expected_Staged_Root.Present
      and then (R.Request_Phase = Prepare or else R.Actual_Staged_Root.Present)
      and then (case R.Mode is
                  when Candidate_Evaluation =>
                    R.Current_Requirement.Present
                    and then R.Evaluated_Requirement.Present
                    and then R.Declared_Verifiers.Present
                    and then R.Executed_Verifiers.Present,
                  when Checkpoint_Return =>
                    R.Expected_Checkpoint.Present))
     with Global => null;

   --  The staged tree: one observation at Prepare, two equal ones at Commit.
   function Staged_Root_Holds (R : Collapse_Request) return Boolean is
     (case R.Request_Phase is
        when Commit  => Same (R.Expected_Staged_Root, R.Actual_Staged_Root),
        when Prepare => R.Expected_Staged_Root.Present)
     with Global => null;

   --  The primary evaluation examined exactly the bytes that would go live.
   function Primary_Covers (R : Collapse_Request) return Boolean is
     (Same (R.Tested_Root, R.Staged_Content_Root))
     with Global => null;

   --  A staged-merge evaluation examined exactly the staged bytes, against the
   --  current requirement, with a complete roster and the declared verifiers.
   function Staged_Covers (R : Collapse_Request) return Boolean is
     (Same (R.Current_Requirement, R.Staged_Evaluated_Requirement)
      and then R.Staged_Roster_Complete
      and then Same (R.Declared_Verifiers, R.Staged_Executed_Verifiers)
      and then Same (R.Staged_Examined_Root, R.Staged_Content_Root))
     with Global => null;

   function Covered (R : Collapse_Request) return Boolean is
     (Primary_Covers (R) or else Staged_Covers (R))
     with Global => null;

   --  The evidence obligation of the request's mode.
   function Evidence_Holds (R : Collapse_Request) return Boolean is
     ((case R.Mode is
         when Candidate_Evaluation =>
           Same (R.Current_Requirement, R.Evaluated_Requirement)
           and then R.Roster_Complete
           and then Same (R.Declared_Verifiers, R.Executed_Verifiers),
         when Checkpoint_Return =>
           Same (R.Expected_Checkpoint, R.Witnessed_Checkpoint))
      and then Covered (R))
     with Global => null;

   --  The whole rule.
   function All_Hold (R : Collapse_Request) return Boolean is
     (R.Candidate_State = Transitions.Valid
      and then R.Conflicts = None_Found
      and then R.Foreign_Writes = None_Found
      and then Same (R.Registered_Watch_Set, R.Watched_Set)
      and then Same (R.Generation_Before, R.Generation_After)
      and then Same (R.Expected_Parent, R.Candidate_Parent)
      and then Same (R.Expected_Subject, R.Evidence_Subject)
      and then Same (R.Expected_Base, R.Candidate_Base)
      and then Same (R.Expected_Delta, R.Candidate_Delta)
      and then Same (R.Expected_Root_Set, R.Candidate_Root_Set)
      and then Staged_Root_Holds (R)
      and then Evidence_Holds (R))
     with Global => null;

   function Decide (Request : Collapse_Request) return Decision
     with Global => null,
          Post =>
            --  Authorized exactly when every obligation holds.
            (Decide'Result = Authorized) = All_Hold (Request)
            --  Nothing absent or unmeasured is ever authorized.
            and then (if not Required_Present (Request) or else not Measured (Request)
                      then Decide'Result /= Authorized)
            --  Retired.
            and then Decide'Result /= Owner_Mismatch
            --  Each refusal names something that is actually the case.
            and then (if Decide'Result = Invalid_Candidate then
                        Request.Candidate_State /= Transitions.Valid)
            and then (if Decide'Result = Conflict then Request.Conflicts = Found)
            and then (if Decide'Result = Foreign_Managed_Write then
                        Request.Foreign_Writes = Found)
            and then (if Decide'Result = Measurement_Absent then
                        not Measured (Request))
            and then (if Decide'Result = Identity_Absent then
                        not Required_Present (Request))
            and then (if Decide'Result = Watch_Incomplete then
                        Differ (Request.Registered_Watch_Set, Request.Watched_Set))
            and then (if Decide'Result = Prime_Changed then
                        Differ (Request.Generation_Before, Request.Generation_After))
            and then (if Decide'Result = Parent_Mismatch then
                        Differ (Request.Expected_Parent, Request.Candidate_Parent))
            and then (if Decide'Result = Evidence_Subject_Mismatch then
                        Differ (Request.Expected_Subject, Request.Evidence_Subject))
            and then (if Decide'Result = Base_Mismatch then
                        Differ (Request.Expected_Base, Request.Candidate_Base))
            and then (if Decide'Result = Delta_Mismatch then
                        Differ (Request.Expected_Delta, Request.Candidate_Delta))
            and then (if Decide'Result = Root_Set_Mismatch then
                        Differ (Request.Expected_Root_Set, Request.Candidate_Root_Set))
            and then (if Decide'Result = Staged_Root_Mismatch then
                        Request.Request_Phase = Commit
                        and then Differ (Request.Expected_Staged_Root,
                                         Request.Actual_Staged_Root))
            and then (if Decide'Result = Execution_Evidence_Incomplete then
                        Request.Mode = Candidate_Evaluation
                        and then not Request.Roster_Complete)
            and then (if Decide'Result = Validation_Context_Mismatch then
                        Request.Mode = Candidate_Evaluation
                        and then Differ (Request.Current_Requirement,
                                         Request.Evaluated_Requirement))
            and then (if Decide'Result = Verifier_Execution_Identity_Mismatch then
                        Request.Mode = Candidate_Evaluation
                        and then Differ (Request.Declared_Verifiers,
                                         Request.Executed_Verifiers))
            and then (if Decide'Result = Checkpoint_Unwitnessed then
                        Request.Mode = Checkpoint_Return
                        and then not Request.Witnessed_Checkpoint.Present)
            and then (if Decide'Result = Checkpoint_Mismatch then
                        Request.Mode = Checkpoint_Return
                        and then Differ (Request.Expected_Checkpoint,
                                         Request.Witnessed_Checkpoint))
            and then (if Decide'Result = Staged_Untested then
                        not Covered (Request));

end Worldline.Collapse;

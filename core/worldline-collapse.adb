package body Worldline.Collapse with SPARK_Mode is

   --  The order below chooses which reason is reported when several hold; the
   --  postcondition does not depend on it. Conflicts come before absence
   --  because a conflicted merge legitimately has no staged tree to compare.
   function Decide (Request : Collapse_Request) return Decision is
   begin
      if Request.Candidate_State /= Transitions.Valid then
         return Invalid_Candidate;
      elsif Request.Conflicts = Found then
         return Conflict;
      elsif Request.Foreign_Writes = Found then
         return Foreign_Managed_Write;
      elsif not Measured (Request) then
         return Measurement_Absent;
      elsif not Same (Request.Registered_Watch_Set, Request.Watched_Set) then
         return Watch_Incomplete;
      elsif not Same (Request.Generation_Before, Request.Generation_After) then
         return Prime_Changed;
      elsif Request.Mode = Candidate_Evaluation
        and then not Request.Roster_Complete
      then
         return Execution_Evidence_Incomplete;
      elsif not Required_Present (Request) then
         return Identity_Absent;
      elsif not Same (Request.Expected_Parent, Request.Candidate_Parent) then
         return Parent_Mismatch;
      elsif not Same (Request.Expected_Subject, Request.Evidence_Subject) then
         return Evidence_Subject_Mismatch;
      elsif not Same (Request.Expected_Base, Request.Candidate_Base) then
         return Base_Mismatch;
      elsif not Same (Request.Expected_Delta, Request.Candidate_Delta) then
         return Delta_Mismatch;
      elsif not Same (Request.Expected_Root_Set, Request.Candidate_Root_Set) then
         return Root_Set_Mismatch;
      elsif Request.Request_Phase = Commit
        and then not Same (Request.Expected_Staged_Root,
                           Request.Actual_Staged_Root)
      then
         return Staged_Root_Mismatch;
      elsif Request.Mode = Candidate_Evaluation
        and then not Same (Request.Current_Requirement,
                           Request.Evaluated_Requirement)
      then
         return Validation_Context_Mismatch;
      elsif Request.Mode = Candidate_Evaluation
        and then not Same (Request.Declared_Verifiers,
                           Request.Executed_Verifiers)
      then
         return Verifier_Execution_Identity_Mismatch;
      elsif Request.Mode = Checkpoint_Return
        and then not Request.Witnessed_Checkpoint.Present
      then
         return Checkpoint_Unwitnessed;
      elsif Request.Mode = Checkpoint_Return
        and then not Same (Request.Expected_Checkpoint,
                           Request.Witnessed_Checkpoint)
      then
         return Checkpoint_Mismatch;
      elsif not Covered (Request) then
         return Staged_Untested;
      else
         return Authorized;
      end if;
   end Decide;

end Worldline.Collapse;

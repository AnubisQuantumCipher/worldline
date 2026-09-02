with Worldline.Transitions;

package Worldline.Collapse with SPARK_Mode is
   use type Hash;
   use type Transitions.World_State;


   type Collapse_Request is record
      Candidate_State            : Transitions.World_State;
      Has_Conflicts              : Boolean;
      Has_Foreign_Managed_Writes : Boolean;
      Expected_Parent            : Hash;
      Candidate_Parent           : Hash;
      Expected_Owner             : Hash;
      Candidate_Owner            : Hash;
      Expected_Base              : Hash;
      Candidate_Base             : Hash;
      Expected_Delta             : Hash;
      Candidate_Delta            : Hash;
      Expected_Root_Set          : Hash;
      Candidate_Root_Set         : Hash;
      Expected_Staged_Root       : Hash;
      Actual_Staged_Root         : Hash;
   end record;

   type Decision is
     (Authorized,
      Invalid_Candidate,
      Parent_Mismatch,
      Owner_Mismatch,
      Base_Mismatch,
      Delta_Mismatch,
      Root_Set_Mismatch,
      Staged_Root_Mismatch,
      Conflict,
      Foreign_Managed_Write);

   function Decide (Request : Collapse_Request) return Decision
     with Global => null,
          Post =>
            (Decide'Result = Authorized) =
              (Request.Candidate_State = Transitions.Valid
               and Request.Expected_Parent = Request.Candidate_Parent
               and Request.Expected_Owner = Request.Candidate_Owner
               and Request.Expected_Base = Request.Candidate_Base
               and Request.Expected_Delta = Request.Candidate_Delta
               and Request.Expected_Root_Set = Request.Candidate_Root_Set
               and Request.Expected_Staged_Root = Request.Actual_Staged_Root
               and not Request.Has_Conflicts
               and not Request.Has_Foreign_Managed_Writes);

end Worldline.Collapse;

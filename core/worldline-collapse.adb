package body Worldline.Collapse with SPARK_Mode is

   function Decide (Request : Collapse_Request) return Decision is
   begin
      if Request.Candidate_State /= Transitions.Valid then
         return Invalid_Candidate;
      elsif Request.Expected_Parent /= Request.Candidate_Parent then
         return Parent_Mismatch;
      elsif Request.Expected_Owner /= Request.Candidate_Owner then
         return Owner_Mismatch;
      elsif Request.Expected_Base /= Request.Candidate_Base then
         return Base_Mismatch;
      elsif Request.Expected_Delta /= Request.Candidate_Delta then
         return Delta_Mismatch;
      elsif Request.Expected_Root_Set /= Request.Candidate_Root_Set then
         return Root_Set_Mismatch;
      elsif Request.Expected_Staged_Root /= Request.Actual_Staged_Root then
         return Staged_Root_Mismatch;
      elsif Request.Has_Conflicts then
         return Conflict;
      elsif Request.Has_Foreign_Managed_Writes then
         return Foreign_Managed_Write;
      else
         return Authorized;
      end if;
   end Decide;

end Worldline.Collapse;

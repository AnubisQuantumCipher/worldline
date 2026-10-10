package body Cosmogony.Genesis with SPARK_Mode => On is

   function Valid_Genesis (U : Universe_State) return Boolean is
   begin
      if U.Universe_Id = Zero_Digest
        or else U.Mission_Id = Zero_Digest
        or else U.Policy_Id = Zero_Digest
        or else U.Policy_Owner_Mission /= U.Mission_Id
        or else U.Worldline_Instance_Id = Zero_Digest
        or else U.Root_Set_Id = Zero_Digest
        or else U.Prime_Id = Zero_Digest
        or else U.Policy_Epoch = 0
        or else U.Budget.Worlds_Reserved > U.Budget.World_Limit
        or else U.Budget.Evaluations_Reserved > U.Budget.Evaluation_Limit
        or else U.Roster_Count = 0
      then
         return False;
      end if;

      for I in U.Roster'Range loop
         if Natural (I) <= Natural (U.Roster_Count) then
            if not U.Roster (I).Enabled
              or else U.Roster (I).Identity = Zero_Digest
              or else U.Roster (I).Identity = U.Mission_Id
            then
               return False;
            end if;
            for J in U.Roster'Range loop
               if J < I and then U.Roster (J).Identity = U.Roster (I).Identity
               then
                  return False;
               end if;
            end loop;
         elsif U.Roster (I).Enabled
           or else U.Roster (I).Identity /= Zero_Digest
         then
            return False;
         end if;
      end loop;
      return True;
   end Valid_Genesis;

   function Role_Allows
     (U : Universe_State; Actor : Digest; Action : Operation) return Boolean
   is
   begin
      for I in U.Roster'Range loop
         if Natural (I) <= Natural (U.Roster_Count)
           and then U.Roster (I).Enabled
           and then U.Roster (I).Identity = Actor
         then
            case U.Roster (I).Role is
               when Builder | Synthesizer =>
                  return Action in Observe | Propose | Create_World |
                    Evaluate_World | Request_Promotion;
               when Adversary =>
                  return Action in Observe | Propose | Create_World |
                    Evaluate_World;
               when Reviewer | Held_Out_Evaluator =>
                  return Action in Observe | Evaluate_World;
               when Observer =>
                  return Action = Observe;
            end case;
         end if;
      end loop;
      return False;
   end Role_Allows;

   function Has_Capacity
     (U : Universe_State; Action : Operation) return Boolean is
   begin
      case Action is
         when Create_World =>
            return U.Budget.Worlds_Reserved < U.Budget.World_Limit;
         when Evaluate_World =>
            return U.Budget.Evaluations_Reserved < U.Budget.Evaluation_Limit;
         when others =>
            return True;
      end case;
   end Has_Capacity;

   function Decide (U : Universe_State; R : Request) return Decision is
   begin
      if not Valid_Genesis (U) then
         return (Denied, Invalid_Genesis);
      elsif R.Request_Id = Zero_Digest then
         return (Denied, Missing_Request_Identity);
      elsif R.Universe_Id /= U.Universe_Id then
         return (Denied, Foreign_Universe);
      elsif R.Mission_Id /= U.Mission_Id then
         return (Denied, Foreign_Mission);
      elsif R.Policy_Id /= U.Policy_Id then
         return (Denied, Foreign_Policy);
      elsif R.Policy_Epoch /= U.Policy_Epoch then
         return (Denied, Stale_Epoch);
      elsif R.Worldline_Instance_Id /= U.Worldline_Instance_Id then
         return (Denied, Foreign_Instance);
      elsif R.Root_Set_Id /= U.Root_Set_Id then
         return (Denied, Foreign_Root_Set);
      elsif R.Prime_Id /= U.Prime_Id then
         return (Denied, Stale_Prime);
      elsif Is_Privileged (R.Action) then
         return (Denied, Privileged_Action);
      elsif not Role_Allows (U, R.Actor_Id, R.Action) then
         return (Denied, Unknown_Or_Disallowed_Agent);
      elsif not Has_Capacity (U, R.Action) then
         return (Denied, Resource_Exhausted);
      elsif Is_Forwardable (R.Action) then
         return (Forward_Worldline, Worldline_Request_Eligible);
      else
         return (Allowed_Local, Local_Request_Allowed);
      end if;
   end Decide;
end Cosmogony.Genesis;

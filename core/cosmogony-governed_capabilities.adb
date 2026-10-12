package body Cosmogony.Governed_Capabilities with SPARK_Mode => On is

   function Derive
     (U : Cosmogony.Universes.Universe_Record;
      G : Cosmogony.Genesis.Universe_State;
      Caller_Id : Cosmogony.Genesis.Digest;
      Parent : Cosmogony.Capabilities.Capability;
      Proposal : Cosmogony.Capabilities.Grant_Proposal;
      Now_Tick : Interfaces.Unsigned_64)
      return Cosmogony.Capabilities.Grant_Decision
   is
   begin
      if not Cosmogony.Universes.Valid (U)
        or else U.Life /= Cosmogony.Universes.Active
        or else U.Parent_Id /= Cosmogony.Genesis.Zero_Digest
      then
         return (False, Cosmogony.Capabilities.Invalid_Universe,
                 Cosmogony.Capabilities.Null_Capability);
      elsif not Cosmogony.Universes.Genesis_Binds (U, G) then
         return (False, Cosmogony.Capabilities.Invalid_Parent,
                 Cosmogony.Capabilities.Null_Capability);
      else
         return Cosmogony.Capabilities.Derive
           (G, U.Policy.Authority_Id, Caller_Id, Parent, Proposal, Now_Tick);
      end if;
   end Derive;

   function Check_Request
     (U : Cosmogony.Universes.Universe_Record;
      G : Cosmogony.Genesis.Universe_State;
      C : Cosmogony.Capabilities.Capability;
      Q : Cosmogony.Capabilities.Scoped_Request;
      Usage : Cosmogony.Capabilities.Resource_Usage;
      Now_Tick : Interfaces.Unsigned_64)
      return Cosmogony.Capabilities.Check_Decision
   is
   begin
      if not Cosmogony.Universes.Valid (U)
        or else U.Life /= Cosmogony.Universes.Active
        or else U.Parent_Id /= Cosmogony.Genesis.Zero_Digest
      then
         return (Cosmogony.Capabilities.Refused,
                 Cosmogony.Capabilities.Invalid_Universe_State);
      elsif not Cosmogony.Universes.Genesis_Binds (U, G) then
         return (Cosmogony.Capabilities.Refused,
                 Cosmogony.Capabilities.Foreign_Capability_Binding);
      else
         return Cosmogony.Capabilities.Check_Request
           (G, U.Policy.Authority_Id, C, Q, Usage, Now_Tick);
      end if;
   end Check_Request;
end Cosmogony.Governed_Capabilities;

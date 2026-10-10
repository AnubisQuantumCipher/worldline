package body Cosmogony.Revocable_Capabilities with SPARK_Mode => On is

   function Derive
     (U : Cosmogony.Universes.Universe_Record;
      G : Universe_State; Caller_Id : Digest;
      Links : Lineage; Count : Link_Count;
      Proposal : Grant_Proposal;
      Now_Tick : Interfaces.Unsigned_64) return Grant_Decision
   is
   begin
      if not Cosmogony.Universes.Valid (U)
        or else U.Life /= Cosmogony.Universes.Active
        or else U.Parent_Id /= Zero_Digest
      then
         return (False, Invalid_Universe, Null_Capability);
      elsif not Cosmogony.Universes.Genesis_Binds (U, G) then
         return (False, Stale_Grant_Lifecycle, Null_Capability);
      elsif Count = 0 then
         return (False, Invalid_Grant_Ancestry, Null_Capability);
      elsif (for some I in 1 .. Count => Links (I).Revoked) then
         return (False, Revoked_Ancestor, Null_Capability);
      elsif not Ancestry_Valid
        (G, U.Policy.Authority_Id, Links, Count, Now_Tick)
      then
         return (False, Invalid_Grant_Ancestry, Null_Capability);
      else
         return Cosmogony.Capabilities.Derive
           (G, U.Policy.Authority_Id, Caller_Id,
            Links (Count).Grant, Proposal, Now_Tick);
      end if;
   end Derive;

   function Check_Request
     (U : Cosmogony.Universes.Universe_Record;
      G : Universe_State;
      Links : Lineage; Count : Link_Count;
      Q : Scoped_Request; Usage : Resource_Usage;
      Now_Tick : Interfaces.Unsigned_64) return Check_Decision
   is
   begin
      if not Cosmogony.Universes.Valid (U)
        or else U.Life /= Cosmogony.Universes.Active
        or else U.Parent_Id /= Zero_Digest
      then
         return (Refused, Invalid_Universe_State);
      elsif not Cosmogony.Universes.Genesis_Binds (U, G) then
         return (Refused, Stale_Lifecycle_Epoch);
      elsif Count = 0 then
         return (Refused, Invalid_Ancestry);
      elsif (for some I in 1 .. Count => Links (I).Revoked) then
         return (Refused, Revoked_Ancestry);
      elsif not Ancestry_Valid
        (G, U.Policy.Authority_Id, Links, Count, Now_Tick)
      then
         return (Refused, Invalid_Ancestry);
      else
         return Cosmogony.Capabilities.Check_Request
           (G, U.Policy.Authority_Id, Links (Count).Grant,
            Q, Usage, Now_Tick);
      end if;
   end Check_Request;
end Cosmogony.Revocable_Capabilities;

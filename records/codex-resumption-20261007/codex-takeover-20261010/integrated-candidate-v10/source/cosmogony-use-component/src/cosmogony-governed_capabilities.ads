with Interfaces;
with Cosmogony.Genesis;
with Cosmogony.Capabilities;
with Cosmogony.Universes;

package Cosmogony.Governed_Capabilities with SPARK_Mode => On is
   use type Cosmogony.Universes.Lifecycle_State;
   use type Cosmogony.Capabilities.Check_Kind;
   use type Cosmogony.Capabilities.Capability;
   use type Cosmogony.Genesis.Digest;

   --  Both records must come from the protected canonical Universe store.
   --  This is a value predicate; it does not authenticate the records.
   function Gate_Open
     (U : Cosmogony.Universes.Universe_Record;
      G : Cosmogony.Genesis.Universe_State) return Boolean is
     (Cosmogony.Universes.Valid (U)
      and then U.Life = Cosmogony.Universes.Active
      and then U.Parent_Id = Cosmogony.Genesis.Zero_Digest
      and then Cosmogony.Universes.Genesis_Binds (U, G));

   function Can_Derive
     (U : Cosmogony.Universes.Universe_Record;
      G : Cosmogony.Genesis.Universe_State;
      Caller_Id : Cosmogony.Genesis.Digest;
      Parent : Cosmogony.Capabilities.Capability;
      Proposal : Cosmogony.Capabilities.Grant_Proposal;
      Now_Tick : Interfaces.Unsigned_64) return Boolean is
     (Gate_Open (U, G)
      and then Cosmogony.Capabilities.Can_Derive
        (G, U.Policy.Authority_Id, Caller_Id, Parent, Proposal, Now_Tick));

   function Derive
     (U : Cosmogony.Universes.Universe_Record;
      G : Cosmogony.Genesis.Universe_State;
      Caller_Id : Cosmogony.Genesis.Digest;
      Parent : Cosmogony.Capabilities.Capability;
      Proposal : Cosmogony.Capabilities.Grant_Proposal;
      Now_Tick : Interfaces.Unsigned_64)
      return Cosmogony.Capabilities.Grant_Decision
   with Post =>
     Derive'Result.Granted =
       Can_Derive (U, G, Caller_Id, Parent, Proposal, Now_Tick)
     and then
       (if Derive'Result.Granted then
          Cosmogony.Capabilities.Attenuates
            (Parent, Derive'Result.Child)
        else Derive'Result.Child =
          Cosmogony.Capabilities.Null_Capability);

   function Eligible
     (U : Cosmogony.Universes.Universe_Record;
      G : Cosmogony.Genesis.Universe_State;
      C : Cosmogony.Capabilities.Capability;
      Q : Cosmogony.Capabilities.Scoped_Request;
      Usage : Cosmogony.Capabilities.Resource_Usage;
      Now_Tick : Interfaces.Unsigned_64) return Boolean is
     (Gate_Open (U, G)
      and then Cosmogony.Capabilities.Eligible
        (G, U.Policy.Authority_Id, C, Q, Usage, Now_Tick));

   function Check_Request
     (U : Cosmogony.Universes.Universe_Record;
      G : Cosmogony.Genesis.Universe_State;
      C : Cosmogony.Capabilities.Capability;
      Q : Cosmogony.Capabilities.Scoped_Request;
      Usage : Cosmogony.Capabilities.Resource_Usage;
      Now_Tick : Interfaces.Unsigned_64)
      return Cosmogony.Capabilities.Check_Decision
   with Post =>
     ((Check_Request'Result.Kind =
         Cosmogony.Capabilities.Eligible_Worldline) =
        (Eligible (U, G, C, Q, Usage, Now_Tick)
         and Cosmogony.Genesis.Is_Forwardable (Q.Ask.Action)))
     and then
     ((Check_Request'Result.Kind = Cosmogony.Capabilities.Eligible_Local) =
        (Eligible (U, G, C, Q, Usage, Now_Tick)
         and not Cosmogony.Genesis.Is_Forwardable (Q.Ask.Action)))
     and then
       (if U.Life /= Cosmogony.Universes.Active then
          Check_Request'Result.Kind = Cosmogony.Capabilities.Refused);
end Cosmogony.Governed_Capabilities;

with Interfaces;
with Cosmogony.Genesis;
with Cosmogony.Capabilities;
with Cosmogony.Universes;
with Cosmogony.Governed_Capabilities;

package Cosmogony.Revocable_Capabilities with SPARK_Mode => On is
   use Cosmogony.Genesis;
   use Cosmogony.Capabilities;
   use type Interfaces.Unsigned_64;
   use type Cosmogony.Universes.Lifecycle_State;

   --  A bounded value snapshot. The caller must obtain it from a protected,
   --  canonical issuer/store; these values do not authenticate themselves.
   subtype Link_Index is Positive range 1 .. 8;
   type Link is record
      Grant : Capability;
      Revoked : Boolean;
   end record;
   type Lineage is array (Link_Index) of Link;
   subtype Link_Count is Natural range 0 .. Link_Index'Last;

   function Current_Link
     (G : Universe_State; Authority_Id : Digest; Item : Link;
      Now_Tick : Interfaces.Unsigned_64) return Boolean is
     (Well_Formed (Item.Grant)
      and then not Item.Revoked
      and then not Item.Grant.Terminal
      and then Bound_To (G, Authority_Id, Item.Grant)
      and then Role_Bounds_Grant
        (G, Item.Grant.Subject_Id, Item.Grant.Granted)
      and then Item.Grant.Issued_At <= Now_Tick
      and then Now_Tick < Item.Grant.Expires_At);

   function Distinct_Ids
     (Links : Lineage; Count : Link_Count) return Boolean is
     (for all I in 1 .. Count =>
       (for all J in 1 .. Count =>
         (if J < I then
           Links (I).Grant.Capability_Id /= Links (J).Grant.Capability_Id)));

   function Ancestry_Valid
     (G : Universe_State; Authority_Id : Digest;
      Links : Lineage; Count : Link_Count;
      Now_Tick : Interfaces.Unsigned_64) return Boolean is
     (Count > 0
      and then Links (1).Grant.Parent_Id = Zero_Digest
      and then Distinct_Ids (Links, Count)
      and then (for all I in 1 .. Count =>
        Current_Link (G, Authority_Id, Links (I), Now_Tick)
        and then (if I > 1 then
          Attenuates (Links (I - 1).Grant, Links (I).Grant))));

   function Gate_Open
     (U : Cosmogony.Universes.Universe_Record;
      G : Universe_State) return Boolean renames
        Cosmogony.Governed_Capabilities.Gate_Open;

   function Can_Derive
     (U : Cosmogony.Universes.Universe_Record;
      G : Universe_State; Caller_Id : Digest;
      Links : Lineage; Count : Link_Count;
      Proposal : Grant_Proposal;
      Now_Tick : Interfaces.Unsigned_64) return Boolean is
     (Gate_Open (U, G)
      and then Ancestry_Valid
        (G, U.Policy.Authority_Id, Links, Count, Now_Tick)
      and then (for all I in 1 .. Count =>
        Proposal.Capability_Id /= Links (I).Grant.Capability_Id)
      and then Cosmogony.Capabilities.Can_Derive
        (G, U.Policy.Authority_Id, Caller_Id,
         Links (Count).Grant, Proposal, Now_Tick));

   function Derive
     (U : Cosmogony.Universes.Universe_Record;
      G : Universe_State; Caller_Id : Digest;
      Links : Lineage; Count : Link_Count;
      Proposal : Grant_Proposal;
      Now_Tick : Interfaces.Unsigned_64) return Grant_Decision
   with Post =>
     Derive'Result.Granted =
       Can_Derive (U, G, Caller_Id, Links, Count, Proposal, Now_Tick)
     and then (if Derive'Result.Granted then
       Attenuates (Links (Count).Grant, Derive'Result.Child)
       else Derive'Result.Child = Null_Capability);

   function Eligible
     (U : Cosmogony.Universes.Universe_Record;
      G : Universe_State;
      Links : Lineage; Count : Link_Count;
      Q : Scoped_Request; Usage : Resource_Usage;
      Now_Tick : Interfaces.Unsigned_64) return Boolean is
     (Gate_Open (U, G)
      and then Ancestry_Valid
        (G, U.Policy.Authority_Id, Links, Count, Now_Tick)
      and then Cosmogony.Capabilities.Eligible
        (G, U.Policy.Authority_Id, Links (Count).Grant,
         Q, Usage, Now_Tick));

   function Check_Request
     (U : Cosmogony.Universes.Universe_Record;
      G : Universe_State;
      Links : Lineage; Count : Link_Count;
      Q : Scoped_Request; Usage : Resource_Usage;
      Now_Tick : Interfaces.Unsigned_64) return Check_Decision
   with Post =>
     ((Check_Request'Result.Kind = Eligible_Worldline) =
       (Eligible (U, G, Links, Count, Q, Usage, Now_Tick)
        and Is_Forwardable (Q.Ask.Action)))
     and then
     ((Check_Request'Result.Kind = Eligible_Local) =
       (Eligible (U, G, Links, Count, Q, Usage, Now_Tick)
        and not Is_Forwardable (Q.Ask.Action)))
     and then (if not Gate_Open (U, G)
       or else not Ancestry_Valid
         (G, U.Policy.Authority_Id, Links, Count, Now_Tick)
       then Check_Request'Result.Kind = Refused);
end Cosmogony.Revocable_Capabilities;

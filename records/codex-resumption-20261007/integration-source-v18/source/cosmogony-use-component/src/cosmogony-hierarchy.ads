with Interfaces;
with Cosmogony.Genesis;
with Cosmogony.Universes;
with Cosmogony.Capabilities;

package Cosmogony.Hierarchy with SPARK_Mode => On is
   use type Interfaces.Unsigned_32;
   use type Interfaces.Unsigned_64;
   use type Cosmogony.Genesis.Digest;
   use type Cosmogony.Universes.Universe_Record;
   use type Cosmogony.Universes.Lifecycle_State;
   use type Cosmogony.Capabilities.Capability;
   use type Cosmogony.Capabilities.Scope_Kind;
   use type Cosmogony.Capabilities.Scope;
   use type Cosmogony.Capabilities.Check_Kind;

   subtype Digest is Cosmogony.Genesis.Digest;
   Zero_Digest : Digest renames Cosmogony.Genesis.Zero_Digest;

   --  The four dimensions are policy units. Authenticating actual host use
   --  and mapping these units to OS limits are separate boundary obligations.
   type Resources is record
      Worlds : Interfaces.Unsigned_32;
      Evaluations : Interfaces.Unsigned_32;
      Memory_MiB : Interfaces.Unsigned_32;
      Threads : Interfaces.Unsigned_32;
   end record;
   Zero_Resources : constant Resources := (0, 0, 0, 0);

   type Child_Index is range 1 .. 8;
   type Child_Count is range 0 .. 8;
   type Child_Allocation is record
      Child_Id : Digest;
      Grant : Resources;
   end record;
   Empty_Allocation : constant Child_Allocation :=
     (Child_Id => Zero_Digest, Grant => Zero_Resources);
   type Allocation_Table is array (Child_Index) of Child_Allocation;

   type Hierarchy_State is record
      Universe : Cosmogony.Universes.Universe_Record;
      Limit : Resources;
      Local_Reserved : Resources;
      Child_Allocated : Resources;
      Count : Child_Count;
      Allocations : Allocation_Table;
   end record;

   type Create_Result is record
      Created : Boolean;
      Parent_State : Hierarchy_State;
      Child_State : Hierarchy_State;
      Child_Capability : Cosmogony.Capabilities.Capability;
   end record;

   function Fits (Value, Limit : Resources) return Boolean is
     (Value.Worlds <= Limit.Worlds
      and then Value.Evaluations <= Limit.Evaluations
      and then Value.Memory_MiB <= Limit.Memory_MiB
      and then Value.Threads <= Limit.Threads);

   function Can_Add
     (Used, Extra, Limit : Resources) return Boolean is
     (Fits (Used, Limit)
      and then Extra.Worlds <= Limit.Worlds - Used.Worlds
      and then Extra.Evaluations <= Limit.Evaluations - Used.Evaluations
      and then Extra.Memory_MiB <= Limit.Memory_MiB - Used.Memory_MiB
      and then Extra.Threads <= Limit.Threads - Used.Threads);

   function Plus
     (Used, Extra, Limit : Resources) return Resources
   with Pre => Can_Add (Used, Extra, Limit),
        Post =>
          Plus'Result.Worlds = Used.Worlds + Extra.Worlds
          and then Plus'Result.Evaluations =
            Used.Evaluations + Extra.Evaluations
          and then Plus'Result.Memory_MiB =
            Used.Memory_MiB + Extra.Memory_MiB
          and then Plus'Result.Threads = Used.Threads + Extra.Threads
          and then Fits (Plus'Result, Limit);

   function Ledger_Consistent (H : Hierarchy_State) return Boolean;
   function Valid (H : Hierarchy_State) return Boolean is
     (Cosmogony.Universes.Valid (H.Universe)
      and then Ledger_Consistent (H)
      and then Can_Add
        (H.Child_Allocated, H.Local_Reserved, H.Limit));

   function Distinct_Domains
     (Parent, Child : Cosmogony.Universes.Universe_Record)
      return Boolean is
     (Child.Universe_Id /= Parent.Universe_Id
      and then Child.Parent_Id = Parent.Universe_Id
      and then Child.Policy.Mission_Id /= Parent.Policy.Mission_Id
      and then Child.Policy.Authority_Id /= Parent.Policy.Authority_Id
      and then Child.Policy.Resource_Id /= Parent.Policy.Resource_Id
      and then Child.Policy.Network_Id /= Parent.Policy.Network_Id
      and then Child.Policy.Provider_Id /= Parent.Policy.Provider_Id
      and then Child.Policy.Evaluator_Id /= Parent.Policy.Evaluator_Id
      and then Child.Policy.Evidence_Id /= Parent.Policy.Evidence_Id
      and then Child.Policy.Root_Set_Id /= Parent.Policy.Root_Set_Id
      and then Child.Policy.Roster_Id /= Parent.Policy.Roster_Id
      and then Child.Policy.Worldline_Set_Id /= Parent.Policy.Worldline_Set_Id
      and then Child.Prime_Worldline_Id /= Parent.Prime_Worldline_Id
      and then Child.Prime_Id /= Parent.Prime_Id
      and then Child.Receipt_Head_Id /= Parent.Receipt_Head_Id);

   --  This lifecycle prerequisite is shared with the complete creation gate.
   --  It does not establish resource or capability authority on its own.
   function Parent_Ready
     (Parent : Cosmogony.Universes.Universe_Record) return Boolean is
     (Cosmogony.Universes.Valid (Parent)
      and then Parent.Life = Cosmogony.Universes.Active);

   function Cross_Universe_Attenuates
     (Parent_U, Child_U : Cosmogony.Universes.Universe_Record;
      Parent_G, Child_G : Cosmogony.Genesis.Universe_State;
      Parent_Cap, Child_Cap : Cosmogony.Capabilities.Capability;
      Grant : Resources; Now_Tick : Interfaces.Unsigned_64)
      return Boolean is
     (Cosmogony.Universes.Genesis_Binds (Parent_U, Parent_G)
      and then Cosmogony.Universes.Genesis_Binds (Child_U, Child_G)
      and then Cosmogony.Genesis.Valid_Genesis (Parent_G)
      and then Cosmogony.Genesis.Valid_Genesis (Child_G)
      and then Cosmogony.Capabilities.Well_Formed (Parent_Cap)
      and then Cosmogony.Capabilities.Well_Formed (Child_Cap)
      and then not Parent_Cap.Terminal
      and then not Child_Cap.Terminal
      and then Cosmogony.Capabilities.Bound_To
        (Parent_G, Parent_U.Policy.Authority_Id, Parent_Cap)
      and then Cosmogony.Capabilities.Bound_To
        (Child_G, Child_U.Policy.Authority_Id, Child_Cap)
      and then Parent_Cap.Applies_To.Kind =
        Cosmogony.Capabilities.Universe_Scope
      and then Child_Cap.Applies_To =
        Cosmogony.Capabilities.Entire_Universe
      and then Child_Cap.Parent_Id = Parent_Cap.Capability_Id
      and then Child_Cap.Capability_Id /= Parent_Cap.Capability_Id
      and then Child_Cap.Issuer_Id = Child_U.Policy.Authority_Id
      and then Child_Cap.Subject_Id /= Child_U.Policy.Mission_Id
      and then Cosmogony.Capabilities.Rights_Within
        (Child_Cap.Granted, Parent_Cap.Granted)
      and then Cosmogony.Capabilities.Role_Bounds_Grant
        (Parent_G, Parent_Cap.Subject_Id, Parent_Cap.Granted)
      and then Cosmogony.Capabilities.Role_Bounds_Grant
        (Child_G, Child_Cap.Subject_Id, Child_Cap.Granted)
      and then Child_Cap.Ceiling.Worlds <= Parent_Cap.Ceiling.Worlds
      and then Child_Cap.Ceiling.Evaluations <=
        Parent_Cap.Ceiling.Evaluations
      and then Grant.Worlds <= Parent_Cap.Ceiling.Worlds
      and then Grant.Evaluations <= Parent_Cap.Ceiling.Evaluations
      and then Child_Cap.Ceiling.Worlds <= Grant.Worlds
      and then Child_Cap.Ceiling.Evaluations <= Grant.Evaluations
      and then Parent_Cap.Issued_At <= Now_Tick
      and then Now_Tick < Parent_Cap.Expires_At
      and then Child_Cap.Issued_At >= Parent_Cap.Issued_At
      and then Child_Cap.Issued_At <= Now_Tick
      and then Now_Tick < Child_Cap.Expires_At
      and then Child_Cap.Expires_At <= Parent_Cap.Expires_At);

   function Can_Create
     (H : Hierarchy_State;
      Parent_G : Cosmogony.Genesis.Universe_State;
      Child_U : Cosmogony.Universes.Universe_Record;
      Child_G : Cosmogony.Genesis.Universe_State;
      Parent_Cap, Child_Cap : Cosmogony.Capabilities.Capability;
      Grant : Resources; Caller_Id : Digest;
      Now_Tick : Interfaces.Unsigned_64) return Boolean is
     (Valid (H)
      and then Parent_Ready (H.Universe)
      and then Caller_Id = H.Universe.Policy.Mission_Id
      and then H.Limit.Worlds <= Parent_G.Budget.World_Limit
      and then H.Limit.Evaluations <=
        Parent_G.Budget.Evaluation_Limit
      and then H.Count < Child_Count'Last
      and then Cosmogony.Universes.Valid (Child_U)
      and then Child_U.Life = Cosmogony.Universes.Genesis
      and then Distinct_Domains (H.Universe, Child_U)
      and then Grant /= Zero_Resources
      and then Child_G.Budget.World_Limit = Grant.Worlds
      and then Child_G.Budget.Evaluation_Limit = Grant.Evaluations
      and then Child_G.Budget.Worlds_Reserved = 0
      and then Child_G.Budget.Evaluations_Reserved = 0
      and then Can_Add (H.Child_Allocated, Grant, H.Limit)
      and then Can_Add
        (Plus (H.Child_Allocated, Grant, H.Limit),
         H.Local_Reserved, H.Limit)
      and then Cross_Universe_Attenuates
        (H.Universe, Child_U, Parent_G, Child_G,
         Parent_Cap, Child_Cap, Grant, Now_Tick)
      and then (for all I in H.Allocations'Range =>
                  (if Natural (I) <= Natural (H.Count) then
                     H.Allocations (I).Child_Id /= Child_U.Universe_Id)));

   function Create_Child
     (H : Hierarchy_State;
      Parent_G : Cosmogony.Genesis.Universe_State;
      Child_U : Cosmogony.Universes.Universe_Record;
      Child_G : Cosmogony.Genesis.Universe_State;
      Parent_Cap, Child_Cap : Cosmogony.Capabilities.Capability;
      Grant : Resources; Caller_Id : Digest;
      Now_Tick : Interfaces.Unsigned_64) return Create_Result
   with Post =>
       (if Create_Child'Result.Created then
          Can_Create (H, Parent_G, Child_U, Child_G,
                      Parent_Cap, Child_Cap, Grant,
                      Caller_Id, Now_Tick)
          and then Valid (Create_Child'Result.Parent_State)
          and then Valid (Create_Child'Result.Child_State)
          and then Create_Child'Result.Parent_State.Universe = H.Universe
          and then Create_Child'Result.Parent_State.Limit = H.Limit
          and then Create_Child'Result.Parent_State.Local_Reserved =
            H.Local_Reserved
          and then Create_Child'Result.Parent_State.Count = H.Count + 1
          and then Create_Child'Result.Child_State.Universe = Child_U
          and then Create_Child'Result.Child_State.Limit = Grant
          and then Create_Child'Result.Child_Capability = Child_Cap
        else Create_Child'Result.Parent_State = H
          and then Create_Child'Result.Child_State = H
          and then Create_Child'Result.Child_Capability =
            Cosmogony.Capabilities.Null_Capability);

   function Allocation_Exists
     (Parent_H : Hierarchy_State; Child_Id : Digest; Grant : Resources)
      return Boolean is
     (for some I in Parent_H.Allocations'Range =>
        Natural (I) <= Natural (Parent_H.Count)
        and then Parent_H.Allocations (I).Child_Id = Child_Id
        and then Parent_H.Allocations (I).Grant = Grant);

   function Child_Eligible
     (Parent_H, Child_H : Hierarchy_State;
      Parent_G, Child_G : Cosmogony.Genesis.Universe_State;
      Parent_Cap, Child_Cap : Cosmogony.Capabilities.Capability;
      Q : Cosmogony.Capabilities.Scoped_Request;
      Usage : Cosmogony.Capabilities.Resource_Usage;
      Now_Tick : Interfaces.Unsigned_64) return Boolean is
     (Valid (Parent_H) and then Valid (Child_H)
      and then Parent_H.Universe.Life = Cosmogony.Universes.Active
      and then Child_H.Universe.Life = Cosmogony.Universes.Active
      and then Parent_H.Limit.Worlds <= Parent_G.Budget.World_Limit
      and then Parent_H.Limit.Evaluations <=
        Parent_G.Budget.Evaluation_Limit
      and then Child_H.Limit.Worlds = Child_G.Budget.World_Limit
      and then Child_H.Limit.Evaluations =
        Child_G.Budget.Evaluation_Limit
      and then Distinct_Domains
        (Parent_H.Universe, Child_H.Universe)
      and then Allocation_Exists
        (Parent_H, Child_H.Universe.Universe_Id, Child_H.Limit)
      and then Cross_Universe_Attenuates
        (Parent_H.Universe, Child_H.Universe,
         Parent_G, Child_G, Parent_Cap, Child_Cap,
         Child_H.Limit, Now_Tick)
      and then Cosmogony.Capabilities.Eligible
        (Child_G, Child_H.Universe.Policy.Authority_Id,
         Child_Cap, Q, Usage, Now_Tick));

   function Check_Child_Request
     (Parent_H, Child_H : Hierarchy_State;
      Parent_G, Child_G : Cosmogony.Genesis.Universe_State;
      Parent_Cap, Child_Cap : Cosmogony.Capabilities.Capability;
      Q : Cosmogony.Capabilities.Scoped_Request;
      Usage : Cosmogony.Capabilities.Resource_Usage;
      Now_Tick : Interfaces.Unsigned_64)
      return Cosmogony.Capabilities.Check_Decision
   with Post =>
     ((Check_Child_Request'Result.Kind =
         Cosmogony.Capabilities.Eligible_Worldline) =
        (Child_Eligible
           (Parent_H, Child_H, Parent_G, Child_G,
            Parent_Cap, Child_Cap, Q, Usage, Now_Tick)
         and Cosmogony.Genesis.Is_Forwardable (Q.Ask.Action)))
     and then
     ((Check_Child_Request'Result.Kind =
         Cosmogony.Capabilities.Eligible_Local) =
        (Child_Eligible
           (Parent_H, Child_H, Parent_G, Child_G,
            Parent_Cap, Child_Cap, Q, Usage, Now_Tick)
         and not Cosmogony.Genesis.Is_Forwardable (Q.Ask.Action)))
     and then
       (if Q.Ask.Universe_Id = Parent_H.Universe.Universe_Id
        then Check_Child_Request'Result.Kind =
          Cosmogony.Capabilities.Refused);
end Cosmogony.Hierarchy;

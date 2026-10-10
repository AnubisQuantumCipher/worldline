package body Cosmogony.Hierarchy with SPARK_Mode => On is

   function Plus
     (Used, Extra, Limit : Resources) return Resources is
      Result : constant Resources :=
        (Worlds => Used.Worlds + Extra.Worlds,
         Evaluations => Used.Evaluations + Extra.Evaluations,
         Memory_MiB => Used.Memory_MiB + Extra.Memory_MiB,
         Threads => Used.Threads + Extra.Threads);
   begin
      return Result;
   end Plus;

   function Ledger_Consistent (H : Hierarchy_State) return Boolean is
      Accumulated : Resources := Zero_Resources;
   begin
      for I in H.Allocations'Range loop
         if Natural (I) <= Natural (H.Count) then
            if H.Allocations (I).Child_Id = Zero_Digest
              or else H.Allocations (I).Grant = Zero_Resources
              or else not Can_Add
                (Accumulated, H.Allocations (I).Grant, H.Limit)
            then
               return False;
            end if;
            for J in H.Allocations'Range loop
               if J < I
                 and then H.Allocations (J).Child_Id =
                   H.Allocations (I).Child_Id
               then
                  return False;
               end if;
            end loop;
            Accumulated := Plus
              (Accumulated, H.Allocations (I).Grant, H.Limit);
         elsif H.Allocations (I) /= Empty_Allocation then
            return False;
         end if;
      end loop;
      return Accumulated = H.Child_Allocated;
   end Ledger_Consistent;

   function Create_Child
     (H : Hierarchy_State;
      Parent_G : Cosmogony.Genesis.Universe_State;
      Child_U : Cosmogony.Universes.Universe_Record;
      Child_G : Cosmogony.Genesis.Universe_State;
      Parent_Cap, Child_Cap : Cosmogony.Capabilities.Capability;
      Grant : Resources; Caller_Id : Digest;
      Now_Tick : Interfaces.Unsigned_64) return Create_Result
   is
      Parent_State : Hierarchy_State := H;
      Child_State : Hierarchy_State;
   begin
      if not Can_Create
        (H, Parent_G, Child_U, Child_G,
         Parent_Cap, Child_Cap, Grant, Caller_Id, Now_Tick)
      then
         return
           (Created => False, Parent_State => H, Child_State => H,
            Child_Capability => Cosmogony.Capabilities.Null_Capability);
      end if;

      Parent_State.Count := H.Count + 1;
      Parent_State.Allocations (Child_Index (Parent_State.Count)) :=
        (Child_Id => Child_U.Universe_Id, Grant => Grant);
      Parent_State.Child_Allocated :=
        Plus (H.Child_Allocated, Grant, H.Limit);
      Child_State :=
        (Universe => Child_U,
         Limit => Grant,
         Local_Reserved => Zero_Resources,
         Child_Allocated => Zero_Resources,
         Count => 0,
         Allocations => (others => Empty_Allocation));
      if not Valid (Parent_State) or else not Valid (Child_State) then
         return
           (Created => False, Parent_State => H, Child_State => H,
            Child_Capability => Cosmogony.Capabilities.Null_Capability);
      end if;
      return
        (Created => True, Parent_State => Parent_State,
         Child_State => Child_State, Child_Capability => Child_Cap);
   end Create_Child;

   function Check_Child_Request
     (Parent_H, Child_H : Hierarchy_State;
      Parent_G, Child_G : Cosmogony.Genesis.Universe_State;
      Parent_Cap, Child_Cap : Cosmogony.Capabilities.Capability;
      Q : Cosmogony.Capabilities.Scoped_Request;
      Usage : Cosmogony.Capabilities.Resource_Usage;
      Now_Tick : Interfaces.Unsigned_64)
      return Cosmogony.Capabilities.Check_Decision
   is
   begin
      if not Valid (Parent_H) or else not Valid (Child_H)
        or else Parent_H.Universe.Life /= Cosmogony.Universes.Active
        or else Child_H.Universe.Life /= Cosmogony.Universes.Active
        or else Parent_H.Limit.Worlds > Parent_G.Budget.World_Limit
        or else Parent_H.Limit.Evaluations >
          Parent_G.Budget.Evaluation_Limit
        or else Child_H.Limit.Worlds /= Child_G.Budget.World_Limit
        or else Child_H.Limit.Evaluations /=
          Child_G.Budget.Evaluation_Limit
      then
         return (Cosmogony.Capabilities.Refused,
                 Cosmogony.Capabilities.Invalid_Universe_State);
      elsif not Distinct_Domains
        (Parent_H.Universe, Child_H.Universe)
        or else not Allocation_Exists
          (Parent_H, Child_H.Universe.Universe_Id, Child_H.Limit)
        or else not Cross_Universe_Attenuates
          (Parent_H.Universe, Child_H.Universe,
           Parent_G, Child_G, Parent_Cap, Child_Cap,
           Child_H.Limit, Now_Tick)
      then
         return (Cosmogony.Capabilities.Refused,
                 Cosmogony.Capabilities.Foreign_Capability_Binding);
      else
         return Cosmogony.Capabilities.Check_Request
           (Child_G, Child_H.Universe.Policy.Authority_Id,
            Child_Cap, Q, Usage, Now_Tick);
      end if;
   end Check_Child_Request;
end Cosmogony.Hierarchy;

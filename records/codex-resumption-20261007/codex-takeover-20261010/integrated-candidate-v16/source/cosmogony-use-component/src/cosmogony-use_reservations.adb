package body Cosmogony.Use_Reservations with SPARK_Mode => On is
   function Count_Reference
     (Data : Rows; Prefix : Natural; Grant_Id : Digest; Purpose : Operation;
      Exclude_Operation : Digest; Base : Interfaces.Unsigned_32) return Counter is
   begin
      if Prefix = 0 then return (True, Base); end if;
      return Step (Count_Reference (Data, Prefix - 1, Grant_Id, Purpose, Exclude_Operation, Base),
                   Charges (Data (Prefix), Grant_Id, Purpose, Exclude_Operation));
   end Count_Reference;
   function Count
     (Data : Rows; Grant_Id : Digest; Purpose : Operation;
      Exclude_Operation : Digest; Base : Interfaces.Unsigned_32) return Counter
   is
      Result : Counter := (True, Base);
   begin
      for I in Data'Range loop
         pragma Loop_Invariant (Result = Count_Reference
           (Data, I - 1, Grant_Id, Purpose, Exclude_Operation, Base));
         Result := Step (Result, Charges (Data (I), Grant_Id, Purpose, Exclude_Operation));
      end loop;
      return Result;
   end Count;
   function Existing (Data : Rows; Operation_Id : Digest) return Natural is
   begin
      for I in Data'Range loop
         pragma Loop_Invariant
           (for all J in Data'First .. I - 1 => Data (J).Bound.Operation_Id /= Operation_Id);
         if Data (I).Bound.Operation_Id = Operation_Id then return I; end if;
      end loop;
      return 0;
   end Existing;
   function Capacity
     (Data : Rows; Links : R.Lineage; Link_Count : R.Link_Count;
      Exclude_Operation : Digest; Base : C.Resource_Usage; Action : Operation)
      return Boolean
   is
      Worlds, Evaluations : Counter;
   begin
      if Link_Count = 0 then return False; end if;
      for I in 1 .. Link_Count loop
         Worlds := Count (Data, Links (I).Grant.Capability_Id, Create_World, Exclude_Operation, Base.Worlds);
         Evaluations := Count (Data, Links (I).Grant.Capability_Id, Evaluate_World, Exclude_Operation, Base.Evaluations);
         if not Worlds.Valid or else not Evaluations.Valid
           or else not C.Usage_Valid (Links (I).Grant, (Worlds.Value, Evaluations.Value))
           or else not C.Has_Grant_Capacity (Links (I).Grant, (Worlds.Value, Evaluations.Value), Action)
         then return False; end if;
         pragma Loop_Invariant
           (for all J in 1 .. I =>
              Count_Reference (Data, Data'Length, Links (J).Grant.Capability_Id,
                Create_World, Exclude_Operation, Base.Worlds).Valid
              and then Count_Reference (Data, Data'Length, Links (J).Grant.Capability_Id,
                Evaluate_World, Exclude_Operation, Base.Evaluations).Valid
              and then C.Usage_Valid (Links (J).Grant,
                (Count_Reference (Data, Data'Length, Links (J).Grant.Capability_Id,
                   Create_World, Exclude_Operation, Base.Worlds).Value,
                 Count_Reference (Data, Data'Length, Links (J).Grant.Capability_Id,
                   Evaluate_World, Exclude_Operation, Base.Evaluations).Value))
              and then C.Has_Grant_Capacity (Links (J).Grant,
                (Count_Reference (Data, Data'Length, Links (J).Grant.Capability_Id,
                   Create_World, Exclude_Operation, Base.Worlds).Value,
                 Count_Reference (Data, Data'Length, Links (J).Grant.Capability_Id,
                   Evaluate_World, Exclude_Operation, Base.Evaluations).Value), Action));
      end loop;
      return True;
   end Capacity;
   function Fresh_Eligible
     (Data : Rows; U : Cosmogony.Universes.Universe_Record; G : Universe_State;
      Links : R.Lineage; Link_Count : R.Link_Count; Q : C.Scoped_Request;
      Base : C.Resource_Usage; Now_Tick : Interfaces.Unsigned_64; Bound : Binding)
      return Boolean
   is
      Worlds, Evaluations : Counter;
   begin
      if not Roster_Valid (Data) or else not Complete (Bound) or else Link_Count = 0
        or else Bound.Capability_Id /= Links (Link_Count).Grant.Capability_Id
        or else Bound.Operation_Id /= Q.Ask.Request_Id
        or else Bound.Requester_Id /= Q.Ask.Actor_Id
        or else Bound.Policy_Epoch /= Q.Ask.Policy_Epoch
        or else Bound.Action /= Q.Ask.Action
        or else not Capacity (Data, Links, Link_Count, Bound.Operation_Id, Base, Q.Ask.Action)
      then return False; end if;
      Worlds := Count (Data, Bound.Capability_Id, Create_World, Bound.Operation_Id, Base.Worlds);
      Evaluations := Count (Data, Bound.Capability_Id, Evaluate_World, Bound.Operation_Id, Base.Evaluations);
      return R.Check_Request (U, G, Links, Link_Count, Q,
        (Worlds.Value, Evaluations.Value), Now_Tick).Kind /= C.Refused;
   end Fresh_Eligible;
   function Check
     (Data : Rows; Grants : Grant_Rows; U : Cosmogony.Universes.Universe_Record; G : Universe_State;
      Links : R.Lineage; Link_Count : R.Link_Count; Q : C.Scoped_Request;
      Base : C.Resource_Usage; Now_Tick : Interfaces.Unsigned_64;
      Bound : Binding; Mode : Command) return Status
   is
      Index : Natural;
   begin
      if not Roster_Valid (Data) or else not Complete (Bound)
        or else not Canonical_Roster (Data, Grants, Links, Link_Count) then return Refused; end if;
      Index := Existing (Data, Bound.Operation_Id);
      if Index /= 0 and then
        (Data (Index).Kind /= Bound_Reservation or else Data (Index).Bound /= Bound)
      then return Refused; end if;
      if Mode = Reserve_Use then
         if Index /= 0 and then Data (Index).State /= Reserved then return Refused; end if;
         if not Capacity (Data, Links, Link_Count, Bound.Operation_Id, Base, Q.Ask.Action)
           or else not Fresh_Eligible (Data, U, G, Links, Link_Count, Q, Base, Now_Tick, Bound)
         then return Refused; end if;
         if Index = 0 then return Reserved_New; else return Reserved_Replay; end if;
      elsif Mode = Consume_Use then
         if Index = 0 or else Data (Index).State = Released then return Refused; end if;
         if Data (Index).State = Reserved then return Consumed_New; else return Consumed_Replay; end if;
      else
         if Index = 0 or else Data (Index).State = Consumed then return Refused; end if;
         if Data (Index).State = Reserved then return Released_New; else return Released_Replay; end if;
      end if;
   end Check;
end Cosmogony.Use_Reservations;

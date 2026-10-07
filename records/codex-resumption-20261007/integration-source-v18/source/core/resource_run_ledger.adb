package body Resource_Run_Ledger with SPARK_Mode is
   function Same_Epoch (Data : Q.Byte_Array; Left, Right : Epoch) return Boolean is
     (T.Epoch_Valid (Data, Left) and then T.Epoch_Valid (Data, Right)
      and then Q.Compare (Data, Left.Value, Right.Value) = Q.Equal);
   function Same_Row (Data : Q.Byte_Array; Left, Right : Row) return Boolean is
     (Row_Valid (Data, Left) and then Row_Valid (Data, Right)
      and then Same_Context (Data, Left.Scope, Right.Scope)
      and then Same_Binding (Data, Left.Bound, Right.Bound)
      and then Optional_Same (Data, Left.Parent, Right.Parent)
      and then Left.Kind = Right.Kind and then Left.State = Right.State
      and then Q.Compare (Data, Left.Amount, Right.Amount) = Q.Equal
      and then Left.Observed_Usage.Present = Right.Observed_Usage.Present
      and then (if Left.Observed_Usage.Present then
        Q.Compare (Data, Left.Observed_Usage.Value, Right.Observed_Usage.Value) = Q.Equal)
      and then Optional_Same (Data, Left.Planned_Unit, Right.Planned_Unit)
      and then Optional_Same (Data, Left.Actual_Unit, Right.Actual_Unit)
      and then Optional_Same (Data, Left.Cgroup, Right.Cgroup)
      and then Optional_Same (Data, Left.Invocation, Right.Invocation));
   function Exact_Value (Data : Q.Byte_Array; Item : Q.Quantity) return Valid_Big_Integer is
      Count : Q.Byte_Count := 0;
      Value : Valid_Big_Integer := To_Big_Integer (0);
      Place : Valid_Big_Integer := To_Big_Integer (1);
   begin
      if not Q.Span_Valid (Data, Item) then return To_Big_Integer (0); end if;
      while Count < Item.Length loop
         pragma Loop_Invariant (Count <= Item.Length);
         pragma Loop_Invariant (Value = Q.Prefix_Reference (Data, Item, Count));
         pragma Loop_Invariant (Place = Q.Power_Reference (Count));
         pragma Loop_Variant (Decreases => Item.Length - Count);
         Value := Value + To_Big_Integer (Q.Digit (Data, Item, Count)) * Place;
         Place := Place * To_Big_Integer (256);
         Count := Count + 1;
      end loop;
      return (if Item.Negative then -Value else Value);
   end Exact_Value;
   function Amount (Data : Q.Byte_Array; Item : Row) return Valid_Big_Integer is
      Reserved : constant Valid_Big_Integer := Exact_Value (Data, Item.Amount);
   begin
      if not Counted (Item) then return To_Big_Integer (0); end if;
      if Item.Kind = Held_Capacity and then Item.Observed_Usage.Present then
         declare
            Used : constant Valid_Big_Integer := Exact_Value (Data, Item.Observed_Usage.Value);
         begin
            if Used > Reserved then return Used; end if;
         end;
      end if;
      return Reserved;
   end Amount;
   function Sum (Data : Q.Byte_Array; Rows : Row_Array; Parent : Identity;
                 Kind : Charge_Kind) return Valid_Big_Integer is
      Count : Q.Byte_Count := 0;
      Result : Valid_Big_Integer := To_Big_Integer (0);
   begin
      while Count < Rows'Length loop
         pragma Loop_Invariant (Count <= Rows'Length);
         pragma Loop_Invariant (Result = Sum_Reference (Data, Rows, Count, Parent, Kind));
         pragma Loop_Variant (Decreases => Q.Byte_Count (Rows'Length) - Count);
         if Included (Data, Rows (Rows'First + Count), Parent, Kind) then
            Result := Result + Amount (Data, Rows (Rows'First + Count));
         end if;
         Count := Count + 1;
      end loop;
      return Result;
   end Sum;
   function Conserved (Data : Q.Byte_Array; State : Ledger_State; Rows : Row_Array)
      return Boolean is
     (Shape (Data, State, Rows)
      and then Exact_Value (Data, State.Held_Total) = Sum (Data, Rows, (Present => False), Held_Capacity)
      and then Exact_Value (Data, State.Charged_Total) = Sum (Data, Rows, (Present => False), Irreversible_Budget));
   function Contained (Data : Q.Byte_Array; Rows : Row_Array) return Boolean is
   begin
      for I in Rows'Range loop
         pragma Loop_Invariant (for all K in Rows'Range => (if K < I then
           (if Rows (K).Parent.Present then (for some J in Rows'Range => J < K
             and then Parent_Supports (Data, Rows (J), Rows (K))))));
         if Rows (I).Parent.Present and then not
           (for some J in Rows'Range => J < I and then Parent_Supports (Data, Rows (J), Rows (I)))
         then return False; end if;
      end loop;
      for I in Rows'Range loop
         pragma Loop_Invariant (for all K in Rows'Range => (if K < I then
           Sum_Reference (Data, Rows, Rows'Length, Rows (K).Bound.Reservation, Held_Capacity)
           + Sum_Reference (Data, Rows, Rows'Length, Rows (K).Bound.Reservation, Irreversible_Budget)
           <= Q.Value (Data, Rows (K).Amount)));
         if Sum (Data, Rows, Rows (I).Bound.Reservation, Held_Capacity)
           + Sum (Data, Rows, Rows (I).Bound.Reservation, Irreversible_Budget) > Exact_Value (Data, Rows (I).Amount)
         then return False; end if;
      end loop;
      return True;
   end Contained;
   function Same_Run_Metadata (Data : Q.Byte_Array; Before, Proposed : Row) return Boolean is
   begin
      return Optional_Same (Data, Before.Planned_Unit, Proposed.Planned_Unit)
        and then Optional_Same (Data, Before.Actual_Unit, Proposed.Actual_Unit)
        and then Optional_Same (Data, Before.Cgroup, Proposed.Cgroup)
        and then Optional_Same (Data, Before.Invocation, Proposed.Invocation);
   end Same_Run_Metadata;
   procedure Changed_Row_Composition_Equality
     (Data : Q.Byte_Array; Before, Proposed : Row;
      Observed : Native_Row; R : Request) is
   begin
      pragma Assert (Changed_Row_Allowed (Data, Before, Proposed, Observed, R) =
         (Same_Context (Data, Before.Scope, Proposed.Scope)
      and then Same_Binding (Data, Before.Bound, Proposed.Bound)
      and then Optional_Same (Data, Before.Parent, Proposed.Parent)
      and then Before.Kind = Proposed.Kind
      and then Q.Compare (Data, Before.Amount, Proposed.Amount) = Q.Equal
      and then Before.Observed_Usage.Present = Proposed.Observed_Usage.Present
      and then (if Before.Observed_Usage.Present then
        Q.Compare (Data, Before.Observed_Usage.Value, Proposed.Observed_Usage.Value) = Q.Equal)
      and then (case R.Kind is
        when Unknown_Operation | Reserve => False,
        when Record_Launch_Intent => Before.State = Reserved and then Proposed.State = Launch_Intent
          and then Id_Valid (Data, Proposed.Planned_Unit)
          and then not Proposed.Actual_Unit.Present and then not Proposed.Cgroup.Present
          and then not Proposed.Invocation.Present,
        when Record_Running => Before.State in Launch_Intent | Settlement_Unknown
          and then not Has_Effect (Before) and then Proposed.State = Running
          and then Observed.Observed = Live
          and then Same (Data, Before.Planned_Unit, Proposed.Actual_Unit)
          and then Same (Data, Before.Planned_Unit, Proposed.Planned_Unit)
          and then Same (Data, Proposed.Actual_Unit, Observed.Actual_Unit)
          and then Same (Data, Proposed.Cgroup, Observed.Cgroup)
          and then Same (Data, Proposed.Invocation, Observed.Invocation),
        when others => Optional_Same (Data, Before.Planned_Unit, Proposed.Planned_Unit)
          and then Optional_Same (Data, Before.Actual_Unit, Proposed.Actual_Unit)
          and then Optional_Same (Data, Before.Cgroup, Proposed.Cgroup)
          and then Optional_Same (Data, Before.Invocation, Proposed.Invocation)
          and then Original_Run_State_Equation (Before, Proposed, Observed, R))));
   end Changed_Row_Composition_Equality;

   function Check
     (Data : Q.Byte_Array; Before : Ledger_State; Before_Rows : Row_Array;
      Proposed : Ledger_State; Proposed_Rows : Row_Array;
      Observed : Native_Array; R : Request) return Status is
     (if R.Kind = Unknown_Operation then Unknown_Kind
      elsif not Shape (Data, Before, Before_Rows) then Invalid_Before
      elsif not Shape (Data, Proposed, Proposed_Rows) then Invalid_Proposed
      elsif not Native_Valid (Data, Before, Before_Rows, Observed) then Native_Roster_Invalid
      elsif not Context_Valid (Data, R.Scope) or else not T.Epoch_Valid (Data, R.Expected_Epoch)
        or else not Id_Valid (Data, R.Expected_Ledger_Head) or else not Id_Valid (Data, R.Request_Id)
        or else not Id_Valid (Data, R.Reservation) or else not Id_Valid (Data, R.Operation_Id)
        or else not Id_Valid (Data, R.Requester)
        or else not Binding_Valid (Data, R.Bound)
        or else not Same (Data, R.Bound.Reservation, R.Reservation)
        or else not Same (Data, R.Bound.Operation, R.Operation_Id)
        or else not Same (Data, R.Bound.Owner, R.Requester) then Request_Invalid
      elsif not Same_Epoch (Data, Before.Resource_Epoch, R.Expected_Epoch) then Stale_Epoch
      elsif not Same (Data, Before.Ledger_Head, R.Expected_Ledger_Head) then Ledger_Head_Mismatch
      elsif not Same_Context (Data, Before.Scope, Proposed.Scope)
        or else not Same_Context (Data, Before.Scope, R.Scope)
        or else not Same (Data, Before.Universe_Head, Proposed.Universe_Head)
        or else Q.Compare (Data, Before.Capacity, Proposed.Capacity) /= Q.Equal then Context_Changed
      elsif not T.Is_Successor (Data, Before.Resource_Epoch.Value, Proposed.Resource_Epoch.Value)
        then Epoch_Not_Successor
      elsif Same (Data, Before.Ledger_Head, Proposed.Ledger_Head) then Ledger_Head_Mismatch
      elsif not Conserved (Data, Before, Before_Rows)
        or else not Conserved (Data, Proposed, Proposed_Rows) then Conservation_Mismatch
      elsif not Contained (Data, Before_Rows)
        or else not Contained (Data, Proposed_Rows) then Parent_Invalid
      elsif Exact_Value (Data, Proposed.Held_Total) + Exact_Value (Data, Proposed.Charged_Total) >
          Exact_Value (Data, Proposed.Capacity) then Capacity_Exceeded
      elsif R.Kind = Reserve then
        (if Before_Rows'Length = Q.Byte_Count'Last or else
             Proposed_Rows'Length /= Before_Rows'Length + 1 then Historical_Row_Removed
         elsif not (for all I in Before_Rows'Range => Same_Row
           (Data, Before_Rows (I), Proposed_Rows (Proposed_Rows'First + (I - Before_Rows'First))))
           then Historical_Row_Changed
         elsif not Same_Row (Data, R.New_Row, Proposed_Rows (Proposed_Rows'Last))
           or else not Same_Binding (Data, R.Bound, R.New_Row.Bound)
           or else R.New_Row.State /= Reserved
           or else not Same (Data, R.New_Row.Bound.Reservation, R.Reservation)
           or else not Same (Data, R.New_Row.Bound.Operation, R.Operation_Id)
           or else not Same_Epoch (Data, R.New_Row.Bound.Resource_Epoch, Before.Resource_Epoch)
           or else not Same (Data, R.New_Row.Bound.Universe_Head, Before.Universe_Head)
           then Request_Invalid
         elsif not Same (Data, R.Requester, R.New_Row.Bound.Owner) then Wrong_Owner
         else Ready)
      elsif Proposed_Rows'Length /= Before_Rows'Length then Historical_Row_Removed
      elsif not (for some I in Before_Rows'Range => Same
          (Data, Before_Rows (I).Bound.Reservation, R.Reservation)) then Request_Invalid
      elsif not (for all I in Before_Rows'Range =>
        (if Same (Data, Before_Rows (I).Bound.Reservation, R.Reservation) then
          Same (Data, Before_Rows (I).Bound.Owner, R.Requester))) then Wrong_Owner
      elsif not (for all I in Before_Rows'Range =>
        (if Same (Data, Before_Rows (I).Bound.Reservation, R.Reservation) then
          Same (Data, Before_Rows (I).Bound.Operation, R.Operation_Id)
          and then Same_Binding (Data, Before_Rows (I).Bound, R.Bound))) then Operation_Mismatch
      elsif not (for all I in Before_Rows'Range =>
        (if not Same (Data, Before_Rows (I).Bound.Reservation, R.Reservation) then
          Same_Row (Data, Before_Rows (I), Proposed_Rows (Proposed_Rows'First + (I - Before_Rows'First)))))
        then Historical_Row_Changed
      elsif not (for all I in Before_Rows'Range =>
        (if Same (Data, Before_Rows (I).Bound.Reservation, R.Reservation) then
          Changed_Row_Allowed (Data, Before_Rows (I),
             Proposed_Rows (Proposed_Rows'First + (I - Before_Rows'First)),
             Observed (Observed'First + (I - Before_Rows'First)), R))) then Illegal_Lifecycle
      else Ready);
end Resource_Run_Ledger;

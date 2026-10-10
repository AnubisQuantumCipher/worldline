with Resource_Quantities;
with Resource_Reservation_Transition;
with SPARK.Big_Integers;
package Resource_Run_Ledger with SPARK_Mode is
   package Q renames Resource_Quantities;
   package T renames Resource_Reservation_Transition;
   use SPARK.Big_Integers;
   use type Q.Byte_Count;
   use type Q.Byte;
   use type Q.Ordering;
   subtype Identity is T.Optional_Identity;
   subtype Epoch is Q.Optional_Quantity;
   type Context is record
      Universe : Identity;
      Policy : Identity;
      Resource : Identity;
      Unit : Identity;
      Instance : Identity;
      Host : Identity;
      Boot : Identity;
      Authority : Identity;
      Policy_Epoch : Epoch;
   end record;
   type Binding is record
      Reservation : Identity;
      Operation : Identity;
      Owner : Identity;
      Workload : Identity;
      Universe_Head : Identity;
      Capability : Identity;
      Grant_Use : Identity;
      Payload : Identity;
      Provenance : Identity;
      Resource_Epoch : Epoch;
   end record;
   type Charge_Kind is (Held_Capacity, Irreversible_Budget);
   type Phase is (Reserved, Launch_Intent, Running, Terminating,
                  Terminal, Settlement_Unknown, Released, Charged);
   type Row is record
      Scope : Context;
      Bound : Binding;
      Parent : Identity;
      Kind : Charge_Kind;
      State : Phase;
      Amount : Q.Quantity;
      Observed_Usage : Q.Optional_Quantity;
      Planned_Unit, Actual_Unit, Cgroup, Invocation : Identity;
   end record;
   type Row_Array is array (Q.Byte_Index range <>) of Row;
   type Ledger_State is record
      Scope : Context;
      Resource_Epoch : Epoch;
      Universe_Head, Ledger_Head : Identity;
      Capacity, Held_Total, Charged_Total : Q.Quantity;
   end record;
   type Liveness is (Unknown, Live, Reaped, Never_Launched);
   type Native_Row is record
      Scope : Context;
      Resource_Epoch : Epoch;
      Bound : Binding;
      Actual_Unit : Identity;
      Cgroup : Identity;
      Invocation : Identity;
      Observation_Head : Identity;
      Observed : Liveness;
   end record;
   type Native_Array is array (Q.Byte_Index range <>) of Native_Row;
   type Operation is (Unknown_Operation, Reserve, Record_Launch_Intent,
                      Record_Running, Record_Terminating, Record_Terminal,
                      Retain_Uncertain, Release_Hold, Charge_Budget);
   type Request is record
      Kind : Operation;
      Scope : Context;
      Expected_Epoch : Epoch;
      Expected_Ledger_Head, Request_Id : Identity;
      Reservation, Operation_Id, Requester : Identity;
      Bound : Binding;
      New_Row : Row;
   end record;
   type Status is (Ready, Unknown_Kind, Invalid_Before, Invalid_Proposed,
                   Native_Roster_Invalid, Request_Invalid, Stale_Epoch,
                   Ledger_Head_Mismatch, Context_Changed, Epoch_Not_Successor,
                   Historical_Row_Removed, Historical_Row_Changed,
                   Duplicate_Reservation, Wrong_Owner, Operation_Mismatch,
                   Illegal_Lifecycle, Native_Not_Established, Parent_Invalid,
                   Conservation_Mismatch, Capacity_Exceeded);
   function Id_Valid (Data : Q.Byte_Array; Item : Identity) return Boolean is
     (T.Present_Identity_Valid (Data, Item)) with Global => null;
   function Same (Data : Q.Byte_Array; Left, Right : Identity) return Boolean is
     (T.Same_Identity (Data, Left, Right)) with Global => null;
   function Optional_Same (Data : Q.Byte_Array; Left, Right : Identity)
      return Boolean is
     ((not Left.Present and then not Right.Present) or else Same (Data, Left, Right))
   with Global => null;
   function Same_Epoch (Data : Q.Byte_Array; Left, Right : Epoch) return Boolean
   with Global => null,
     Post => Same_Epoch'Result = (T.Epoch_Valid (Data, Left)
       and then T.Epoch_Valid (Data, Right)
       and then Q.Value (Data, Left.Value) = Q.Value (Data, Right.Value));
   function Context_Valid (Data : Q.Byte_Array; Scope : Context) return Boolean is
     (Id_Valid (Data, Scope.Universe)
      and then Id_Valid (Data, Scope.Policy)
      and then Id_Valid (Data, Scope.Resource)
      and then Id_Valid (Data, Scope.Unit)
      and then Id_Valid (Data, Scope.Instance)
      and then Id_Valid (Data, Scope.Host)
      and then Id_Valid (Data, Scope.Boot)
      and then Id_Valid (Data, Scope.Authority)
      and then T.Epoch_Valid (Data, Scope.Policy_Epoch)) with Global => null;
   function Same_Context (Data : Q.Byte_Array; Left, Right : Context) return Boolean is
     (Same (Data, Left.Universe, Right.Universe)
      and then Same (Data, Left.Policy, Right.Policy)
      and then Same (Data, Left.Resource, Right.Resource)
      and then Same (Data, Left.Unit, Right.Unit)
      and then Same (Data, Left.Instance, Right.Instance)
      and then Same (Data, Left.Host, Right.Host)
      and then Same (Data, Left.Boot, Right.Boot)
      and then Same (Data, Left.Authority, Right.Authority)
      and then Same_Epoch (Data, Left.Policy_Epoch, Right.Policy_Epoch))
   with Global => null;
   function Binding_Valid (Data : Q.Byte_Array; B : Binding) return Boolean is
     (Id_Valid (Data, B.Reservation)
      and then Id_Valid (Data, B.Operation)
      and then Id_Valid (Data, B.Owner)
      and then Id_Valid (Data, B.Workload)
      and then Id_Valid (Data, B.Universe_Head)
      and then Id_Valid (Data, B.Capability)
      and then Id_Valid (Data, B.Grant_Use)
      and then Id_Valid (Data, B.Payload)
      and then Id_Valid (Data, B.Provenance)
      and then T.Epoch_Valid (Data, B.Resource_Epoch)) with Global => null;
   function Same_Binding (Data : Q.Byte_Array; Left, Right : Binding) return Boolean is
     (Same (Data, Left.Reservation, Right.Reservation)
      and then Same (Data, Left.Operation, Right.Operation)
      and then Same (Data, Left.Owner, Right.Owner)
      and then Same (Data, Left.Workload, Right.Workload)
      and then Same (Data, Left.Universe_Head, Right.Universe_Head)
      and then Same (Data, Left.Capability, Right.Capability)
      and then Same (Data, Left.Grant_Use, Right.Grant_Use)
      and then Same (Data, Left.Payload, Right.Payload)
      and then Same (Data, Left.Provenance, Right.Provenance)
      and then Same_Epoch (Data, Left.Resource_Epoch, Right.Resource_Epoch))
   with Global => null;
   function Has_Effect (Item : Row) return Boolean is (Item.Actual_Unit.Present)
   with Global => null;
   function Counted (Item : Row) return Boolean is (Item.State /= Released)
     with Global => null;
   function Row_Valid (Data : Q.Byte_Array; Item : Row) return Boolean is
     (Context_Valid (Data, Item.Scope) and then Binding_Valid (Data, Item.Bound)
      and then (if Item.Parent.Present then Id_Valid (Data, Item.Parent))
      and then T.Nonnegative_Valid (Data, Item.Amount)
      and then (if Item.Observed_Usage.Present then
                  T.Nonnegative_Valid (Data, Item.Observed_Usage.Value))
      and then (if Item.State = Charged then Item.Kind = Irreversible_Budget)
      and then (if Item.State = Released then Item.Kind = Held_Capacity)
      and then (if Item.Planned_Unit.Present then Id_Valid (Data, Item.Planned_Unit))
      and then (if Item.State in Launch_Intent | Running | Terminating | Terminal | Settlement_Unknown | Charged
        then Id_Valid (Data, Item.Planned_Unit))
      and then (if Item.State in Running | Terminating | Terminal | Charged then Has_Effect (Item))
      and then (if Item.State in Reserved | Launch_Intent then
        not Item.Actual_Unit.Present and then not Item.Cgroup.Present and then not Item.Invocation.Present)
      and then (if Item.State = Reserved then not Item.Planned_Unit.Present)
      and then Item.Actual_Unit.Present = Item.Cgroup.Present
      and then Item.Actual_Unit.Present = Item.Invocation.Present
      and then (if Has_Effect (Item) then
        Id_Valid (Data, Item.Actual_Unit) and then Id_Valid (Data, Item.Cgroup)
        and then Id_Valid (Data, Item.Invocation)
        and then Same (Data, Item.Planned_Unit, Item.Actual_Unit)))
   with Global => null;
   function Same_Row (Data : Q.Byte_Array; Left, Right : Row) return Boolean
   with Global => null,
     Post => Same_Row'Result = (Row_Valid (Data, Left) and then Row_Valid (Data, Right)
       and then Same_Context (Data, Left.Scope, Right.Scope)
       and then Same_Binding (Data, Left.Bound, Right.Bound)
       and then Optional_Same (Data, Left.Parent, Right.Parent)
       and then Left.Kind = Right.Kind and then Left.State = Right.State
       and then Q.Value (Data, Left.Amount) = Q.Value (Data, Right.Amount)
       and then Left.Observed_Usage.Present = Right.Observed_Usage.Present
       and then (if Left.Observed_Usage.Present then
         Q.Value (Data, Left.Observed_Usage.Value) = Q.Value (Data, Right.Observed_Usage.Value))
       and then Optional_Same (Data, Left.Planned_Unit, Right.Planned_Unit)
       and then Optional_Same (Data, Left.Actual_Unit, Right.Actual_Unit)
       and then Optional_Same (Data, Left.Cgroup, Right.Cgroup)
       and then Optional_Same (Data, Left.Invocation, Right.Invocation));
   function Exact_Value (Data : Q.Byte_Array; Item : Q.Quantity) return Valid_Big_Integer
   with Global => null, Post => Exact_Value'Result = Q.Value (Data, Item);
   function Amount_Reference (Data : Q.Byte_Array; Item : Row) return Valid_Big_Integer is
     (if not Counted (Item) then To_Big_Integer (0)
      elsif Item.Kind = Held_Capacity and then Item.Observed_Usage.Present
        and then Q.Value (Data, Item.Observed_Usage.Value) > Q.Value (Data, Item.Amount)
      then Q.Value (Data, Item.Observed_Usage.Value) else Q.Value (Data, Item.Amount))
   with Ghost, Global => null;
   function Amount (Data : Q.Byte_Array; Item : Row) return Valid_Big_Integer
   with Global => null, Post => Amount'Result = Amount_Reference (Data, Item);
   function Included (Data : Q.Byte_Array; Item : Row; Parent : Identity;
                      Kind : Charge_Kind) return Boolean is
     (Item.Kind = Kind and then Counted (Item)
      and then (if Parent.Present then Same (Data, Item.Parent, Parent)
                else not Item.Parent.Present)) with Global => null;
   function Sum_Reference (Data : Q.Byte_Array; Rows : Row_Array;
                           Count : Q.Byte_Count; Parent : Identity;
                           Kind : Charge_Kind) return Valid_Big_Integer is
     (if Count = 0 then To_Big_Integer (0)
      else Sum_Reference (Data, Rows, Count - 1, Parent, Kind) +
        (if Count <= Rows'Length and then Included
             (Data, Rows (Rows'First + (Count - 1)), Parent, Kind)
         then Amount_Reference (Data, Rows (Rows'First + (Count - 1)))
         else To_Big_Integer (0)))
   with Ghost, Global => null, Subprogram_Variant => (Decreases => Count);
   function Sum (Data : Q.Byte_Array; Rows : Row_Array; Parent : Identity;
                 Kind : Charge_Kind) return Valid_Big_Integer
   with Global => null,
     Post => Sum'Result = Sum_Reference (Data, Rows, Rows'Length, Parent, Kind);
   function Cgroup_Inside (Data : Q.Byte_Array; Parent, Child : Identity) return Boolean is
     (Id_Valid (Data, Parent) and then Id_Valid (Data, Child)
      and then Parent.Value.Length > 0
      and then Parent.Value.Length <= Child.Value.Length
      and then (for all Offset in Q.Byte_Count range 0 .. Parent.Value.Length - 1 =>
        Data (Parent.Value.First + Offset) = Data (Child.Value.First + Offset))
      and then (Parent.Value.Length = Child.Value.Length or else
        Data (Child.Value.First + Parent.Value.Length) = Q.Byte (Character'Pos ('/'))))
   with Global => null;
   function Shape (Data : Q.Byte_Array; State : Ledger_State; Rows : Row_Array) return Boolean is
     (Context_Valid (Data, State.Scope) and then T.Epoch_Valid (Data, State.Resource_Epoch)
      and then Id_Valid (Data, State.Universe_Head) and then Id_Valid (Data, State.Ledger_Head)
      and then T.Nonnegative_Valid (Data, State.Capacity)
      and then T.Nonnegative_Valid (Data, State.Held_Total)
      and then T.Nonnegative_Valid (Data, State.Charged_Total)
      and then (for all I in Rows'Range => Row_Valid (Data, Rows (I))
        and then Same_Context (Data, State.Scope, Rows (I).Scope)
        and then Q.Compare (Data, Rows (I).Bound.Resource_Epoch.Value,
                              State.Resource_Epoch.Value) in Q.Less | Q.Equal)
      and then (for all I in Rows'Range => (for all J in Rows'Range =>
        (if I < J then not Same (Data, Rows (I).Bound.Reservation, Rows (J).Bound.Reservation)
         and then not Same (Data, Rows (I).Bound.Operation, Rows (J).Bound.Operation))))) with Global => null;
   function Conserved_Reference (Data : Q.Byte_Array; State : Ledger_State;
                                 Rows : Row_Array) return Boolean is
     (Shape (Data, State, Rows)
      and then Q.Value (Data, State.Held_Total) = Sum_Reference
        (Data, Rows, Rows'Length, (Present => False), Held_Capacity)
      and then Q.Value (Data, State.Charged_Total) = Sum_Reference
        (Data, Rows, Rows'Length, (Present => False), Irreversible_Budget))
   with Ghost, Global => null;
   function Conserved (Data : Q.Byte_Array; State : Ledger_State; Rows : Row_Array)
      return Boolean with Global => null,
     Post => Conserved'Result = Conserved_Reference (Data, State, Rows);
   function Parent_Supports (Data : Q.Byte_Array; Parent, Child : Row) return Boolean is
     (Same (Data, Child.Parent, Parent.Bound.Reservation)
      and then Parent.Kind = Child.Kind
      and then (if Counted (Child) then Counted (Parent))
      and then (if Parent.State = Charged and then Counted (Child) then Child.State = Charged)
      and then (if Has_Effect (Child) and then Counted (Child) then
        Has_Effect (Parent) and then Cgroup_Inside (Data, Parent.Cgroup, Child.Cgroup)))
   with Global => null;
   function Contained_Reference (Data : Q.Byte_Array; Rows : Row_Array) return Boolean is
     ((for all I in Rows'Range =>
        (if Rows (I).Parent.Present then
          (for some J in Rows'Range => J < I and then Parent_Supports (Data, Rows (J), Rows (I)))))
      and then (for all I in Rows'Range =>
        Sum_Reference (Data, Rows, Rows'Length, Rows (I).Bound.Reservation, Held_Capacity)
        + Sum_Reference (Data, Rows, Rows'Length, Rows (I).Bound.Reservation, Irreversible_Budget)
        <= Q.Value (Data, Rows (I).Amount)))
   with Ghost, Global => null;
   function Contained (Data : Q.Byte_Array; Rows : Row_Array) return Boolean
   with Global => null, Post => Contained'Result = Contained_Reference (Data, Rows);
   function Native_Valid (Data : Q.Byte_Array; State : Ledger_State;
                          Rows : Row_Array; Observed : Native_Array) return Boolean is
     (Observed'Length = Rows'Length and then
      (for all I in Rows'Range =>
       Same_Context (Data, State.Scope, Observed (Observed'First + (I - Rows'First)).Scope)
       and then Same_Epoch (Data, State.Resource_Epoch,
                             Observed (Observed'First + (I - Rows'First)).Resource_Epoch)
       and then Same_Binding (Data, Rows (I).Bound,
                              Observed (Observed'First + (I - Rows'First)).Bound)
       and then Id_Valid (Data, Observed (Observed'First + (I - Rows'First)).Observation_Head)
       and then (if Has_Effect (Rows (I)) then
         Same (Data, Rows (I).Actual_Unit, Observed (Observed'First + (I - Rows'First)).Actual_Unit)
         and then Same (Data, Rows (I).Cgroup, Observed (Observed'First + (I - Rows'First)).Cgroup)
         and then Same (Data, Rows (I).Invocation, Observed (Observed'First + (I - Rows'First)).Invocation))
       and then (if Observed (Observed'First + (I - Rows'First)).Observed = Never_Launched then
         Rows (I).State in Reserved | Launch_Intent | Settlement_Unknown
         and then not Has_Effect (Rows (I))))) with Global => null;
   function Same_Run_Metadata (Data : Q.Byte_Array; Before, Proposed : Row) return Boolean
     with Global => null,
       Post => Same_Run_Metadata'Result =
         (Optional_Same (Data, Before.Planned_Unit, Proposed.Planned_Unit)
          and then Optional_Same (Data, Before.Actual_Unit, Proposed.Actual_Unit)
          and then Optional_Same (Data, Before.Cgroup, Proposed.Cgroup)
          and then Optional_Same (Data, Before.Invocation, Proposed.Invocation));
   function Changed_Row_Allowed (Data : Q.Byte_Array; Before, Proposed : Row;
                                 Observed : Native_Row; R : Request) return Boolean is
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
        when Record_Terminating => Same_Run_Metadata (Data, Before, Proposed)
          and then Before.State = Running and then Proposed.State = Terminating,
        when Record_Terminal => Same_Run_Metadata (Data, Before, Proposed)
          and then Before.State in Running | Terminating | Settlement_Unknown
          and then Proposed.State = Terminal and then Observed.Observed = Reaped,
        when Retain_Uncertain => Same_Run_Metadata (Data, Before, Proposed)
          and then Before.State in Launch_Intent | Running | Terminating | Settlement_Unknown
          and then Proposed.State = Settlement_Unknown and then Observed.Observed = Unknown,
        when Release_Hold => Same_Run_Metadata (Data, Before, Proposed)
          and then Before.Kind = Held_Capacity and then Proposed.State = Released
          and then ((Before.State = Terminal and then Observed.Observed = Reaped)
            or else (Before.State in Reserved | Launch_Intent | Settlement_Unknown
              and then not Has_Effect (Before) and then Observed.Observed = Never_Launched)),
        when Charge_Budget => Same_Run_Metadata (Data, Before, Proposed)
          and then Before.Kind = Irreversible_Budget and then Before.State = Terminal
          and then Proposed.State = Charged and then Observed.Observed = Reaped)) with Global => null;
   --  Original inner state equation, total over the unchanged Request domain.
   --  Kept outside the outer case so every original branch remains analyzable.
   function Original_Run_State_Equation
     (Before, Proposed : Row; Observed : Native_Row; R : Request)
      return Boolean is
     (case R.Kind is
            when Record_Terminating => Before.State = Running and then Proposed.State = Terminating,
            when Record_Terminal => Before.State in Running | Terminating | Settlement_Unknown
              and then Proposed.State = Terminal and then Observed.Observed = Reaped,
            when Retain_Uncertain => Before.State in Launch_Intent | Running | Terminating | Settlement_Unknown
              and then Proposed.State = Settlement_Unknown and then Observed.Observed = Unknown,
            when Release_Hold => Before.Kind = Held_Capacity and then Proposed.State = Released
              and then ((Before.State = Terminal and then Observed.Observed = Reaped)
                or else (Before.State in Reserved | Launch_Intent | Settlement_Unknown
                  and then not Has_Effect (Before) and then Observed.Observed = Never_Launched)),
            when Charge_Budget => Before.Kind = Irreversible_Budget and then Before.State = Terminal
              and then Proposed.State = Charged and then Observed.Observed = Reaped,
            when others => False)
   with Ghost, Global => null;

   --  Retains the complete old nested-case equation as a checked theorem.
   --  All Request variants and all arbitrary row/observation inputs remain.
   procedure Changed_Row_Composition_Equality
     (Data : Q.Byte_Array; Before, Proposed : Row;
      Observed : Native_Row; R : Request)
     with Ghost, Global => null, Always_Terminates,
       Post => Changed_Row_Allowed (Data, Before, Proposed, Observed, R) =
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
          and then Original_Run_State_Equation (Before, Proposed, Observed, R)));

   function Decision_Reference
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
      elsif not Conserved_Reference (Data, Before, Before_Rows)
        or else not Conserved_Reference (Data, Proposed, Proposed_Rows) then Conservation_Mismatch
      elsif not Contained_Reference (Data, Before_Rows)
        or else not Contained_Reference (Data, Proposed_Rows) then Parent_Invalid
      elsif Q.Value (Data, Proposed.Held_Total) + Q.Value (Data, Proposed.Charged_Total) >
          Q.Value (Data, Proposed.Capacity) then Capacity_Exceeded
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
      else Ready)
   with Ghost, Global => null;
   function Check
     (Data : Q.Byte_Array; Before : Ledger_State; Before_Rows : Row_Array;
      Proposed : Ledger_State; Proposed_Rows : Row_Array;
      Observed : Native_Array; R : Request) return Status
   with Global => null,
     Post => Check'Result = Decision_Reference
       (Data, Before, Before_Rows, Proposed, Proposed_Rows, Observed, R)
       and then (if Check'Result = Ready then
         Conserved_Reference (Data, Proposed, Proposed_Rows)
         and then Contained_Reference (Data, Proposed_Rows)
         and then Proposed_Rows'Length >= Before_Rows'Length
         and then Q.Value (Data, Proposed.Resource_Epoch.Value) =
                  Q.Value (Data, Before.Resource_Epoch.Value) + 1);
end Resource_Run_Ledger;

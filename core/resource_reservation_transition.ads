with Resource_Quantities;
with SPARK.Big_Integers;

package Resource_Reservation_Transition with SPARK_Mode is
   use Resource_Quantities;
   use SPARK.Big_Integers;
   use type Resource_Quantities.Byte;

   --  This unit checks one selected persistent budget reservation against an
   --  explicitly supplied remainder for every other reservation. It does not
   --  authenticate that remainder, the selected row, or a protected observation.
   --  All identities are full bytes. Bounds are storage extents, not value caps.
   type Identity is record
      First  : Byte_Index;
      Length : Byte_Count;
   end record;
   type Optional_Identity (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True  => Value : Identity;
      end case;
   end record;
   type Context is record
      Universe : Optional_Identity;
      Policy   : Optional_Identity;
      Resource : Optional_Identity;
   end record;
   type Reservation_Binding is record
      Reservation : Optional_Identity;
      Operation   : Optional_Identity;
      Owner       : Optional_Identity;
      Universe    : Optional_Identity;
      Head        : Optional_Identity;
      Candidate   : Optional_Identity;
   end record;
   type Reservation_Record is record
      Binding : Reservation_Binding;
      Amount  : Quantity;
   end record;
   type Reservation_Phase is (Active, Consumed, Released);
   type Optional_Reservation (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True =>
            Value : Reservation_Record;
            Phase : Reservation_Phase;
      end case;
   end record;
   type Ledger_State is record
      Scope : Context;
      Epoch : Optional_Quantity;
      Total : Quantity;
      Other_Reservations : Quantity;
      Selected : Optional_Reservation;
   end record;
   type High_Water_Observation is record
      Scope : Context;
      Epoch : Optional_Quantity;
   end record;
   type Operation_Kind is (Unknown_Operation, Reserve, Consume, Release);
   type Request (Kind : Operation_Kind := Unknown_Operation) is record
      Requester : Optional_Identity;
      case Kind is
         when Unknown_Operation => null;
         when Reserve =>
            Expected_Epoch : Optional_Quantity;
            New_Reservation : Reservation_Record;
            Ceiling : Quantity;
         when Consume | Release =>
            Reservation : Optional_Identity;
            Operation   : Optional_Identity;
      end case;
   end record;
   type Result_Status is
     (Ready, Unknown_Kind, Invalid_Before, Invalid_Proposed,
      Observation_Absent, Observation_Invalid, Observation_Scope_Mismatch,
      High_Water_Mismatch, Request_Invalid, Stale_Reserve_Epoch,
      Slot_Already_Exists, Reservation_Absent, Wrong_Owner,
      Reservation_Mismatch, Operation_Mismatch, Already_Released,
      Already_Consumed, Before_Conservation_Mismatch, Context_Changed,
      Remainder_Changed, Proposed_Row_Mismatch, Epoch_Not_Successor,
      Proposed_Conservation_Mismatch, Transition_Conservation_Mismatch,
      Limit_Exceeded);

   function Identity_Valid (Data : Byte_Array; Id : Identity) return Boolean is
     (Id.Length = 0 or else
        (Id.First in Data'Range and then Id.Length - 1 <= Data'Last - Id.First))
   with Global => null;
   function Present_Identity_Valid
     (Data : Byte_Array; Id : Optional_Identity) return Boolean is
     (Id.Present and then Identity_Valid (Data, Id.Value))
   with Global => null;
   function Same_Identity
     (Data : Byte_Array; Left, Right : Optional_Identity) return Boolean is
     (Present_Identity_Valid (Data, Left) and then
      Present_Identity_Valid (Data, Right) and then
      Left.Value.Length = Right.Value.Length and then
      (Left.Value.Length = 0 or else
       (for all Offset in Byte_Count range 0 .. Left.Value.Length - 1 =>
          Data (Left.Value.First + Offset) = Data (Right.Value.First + Offset))))
   with Global => null;
   function Context_Valid (Data : Byte_Array; C : Context) return Boolean is
     (Present_Identity_Valid (Data, C.Universe) and then
      Present_Identity_Valid (Data, C.Policy) and then
      Present_Identity_Valid (Data, C.Resource))
   with Global => null;
   function Same_Context (Data : Byte_Array; Left, Right : Context)
      return Boolean is
     (Same_Identity (Data, Left.Universe, Right.Universe) and then
      Same_Identity (Data, Left.Policy, Right.Policy) and then
      Same_Identity (Data, Left.Resource, Right.Resource))
   with Global => null;
   function Binding_Valid (Data : Byte_Array; B : Reservation_Binding)
      return Boolean is
     (Present_Identity_Valid (Data, B.Reservation) and then
      Present_Identity_Valid (Data, B.Operation) and then
      Present_Identity_Valid (Data, B.Owner) and then
      Present_Identity_Valid (Data, B.Universe) and then
      Present_Identity_Valid (Data, B.Head) and then
      Present_Identity_Valid (Data, B.Candidate))
   with Global => null;
   function Same_Binding
     (Data : Byte_Array; Left, Right : Reservation_Binding) return Boolean is
     (Same_Identity (Data, Left.Reservation, Right.Reservation) and then
      Same_Identity (Data, Left.Operation, Right.Operation) and then
      Same_Identity (Data, Left.Owner, Right.Owner) and then
      Same_Identity (Data, Left.Universe, Right.Universe) and then
      Same_Identity (Data, Left.Head, Right.Head) and then
      Same_Identity (Data, Left.Candidate, Right.Candidate))
   with Global => null;

   --  Negative zero and arbitrary leading padding are accepted. A persistent
   --  reservation amount/epoch is nonnegative; signed observations/ceilings
   --  remain represented in full and are never truncated to a machine word.
   function Nonnegative_Valid (Data : Byte_Array; Q : Quantity) return Boolean
   with Global => null,
     Post => Nonnegative_Valid'Result =
       (Span_Valid (Data, Q) and then Value (Data, Q) >= 0);
   function Epoch_Valid (Data : Byte_Array; E : Optional_Quantity)
      return Boolean is
     (E.Present and then Nonnegative_Valid (Data, E.Value))
   with Global => null;
   function State_Shape (Data : Byte_Array; S : Ledger_State) return Boolean is
     (Context_Valid (Data, S.Scope) and then Epoch_Valid (Data, S.Epoch) and then
      Nonnegative_Valid (Data, S.Total) and then
      Nonnegative_Valid (Data, S.Other_Reservations) and then
      (if S.Selected.Present then
         Binding_Valid (Data, S.Selected.Value.Binding) and then
         Nonnegative_Valid (Data, S.Selected.Value.Amount) and then
         Same_Identity (Data, S.Scope.Universe,
                        S.Selected.Value.Binding.Universe)))
   with Global => null;

   function Magnitude_Sum_Equals
     (Data : Byte_Array; Left, Right, Sum : Quantity) return Boolean
   with Global => null,
     Post => Magnitude_Sum_Equals'Result =
       (Span_Valid (Data, Left) and then Span_Valid (Data, Right) and then
        Span_Valid (Data, Sum) and then Magnitude (Data, Sum) =
          Magnitude (Data, Left) + Magnitude (Data, Right));
   function Signed_Sum_Equals
     (Data : Byte_Array; Left, Right, Sum : Quantity) return Boolean
   with Global => null,
     Post => Signed_Sum_Equals'Result =
       (Span_Valid (Data, Left) and then Span_Valid (Data, Right) and then
        Span_Valid (Data, Sum) and then
        Value (Data, Sum) = Value (Data, Left) + Value (Data, Right));
   function Is_Successor
     (Data : Byte_Array; Before, After : Quantity) return Boolean
   with Global => null,
     Post => Is_Successor'Result =
       (Span_Valid (Data, Before) and then Span_Valid (Data, After) and then
        Value (Data, Before) >= 0 and then Value (Data, After) >= 0 and then
        Value (Data, After) = Value (Data, Before) + 1);

   function Counted_Amount (Data : Byte_Array; S : Ledger_State)
      return Valid_Big_Integer is
     (if S.Selected.Present and then S.Selected.Phase /= Released
      then Value (Data, S.Selected.Value.Amount) else To_Big_Integer (0))
   with Ghost, Global => null;
   function Conserved_Reference (Data : Byte_Array; S : Ledger_State)
      return Boolean is
     (State_Shape (Data, S) and then Value (Data, S.Total) =
        Value (Data, S.Other_Reservations) + Counted_Amount (Data, S))
   with Ghost, Global => null;
   function Conserved (Data : Byte_Array; S : Ledger_State) return Boolean
   with Global => null,
     Post => Conserved'Result = Conserved_Reference (Data, S);

   function Same_Reservation_Reference
     (Data : Byte_Array; Left, Right : Reservation_Record) return Boolean is
     (Same_Binding (Data, Left.Binding, Right.Binding) and then
      Span_Valid (Data, Left.Amount) and then Span_Valid (Data, Right.Amount)
      and then Value (Data, Left.Amount) = Value (Data, Right.Amount))
   with Ghost, Global => null;
   function Same_Reservation
     (Data : Byte_Array; Left, Right : Reservation_Record) return Boolean
   with Global => null,
     Post => Same_Reservation'Result =
       Same_Reservation_Reference (Data, Left, Right);
   function Proposed_Row_Reference
     (Data : Byte_Array; Before, Proposed : Ledger_State; R : Request)
      return Boolean is
     (case R.Kind is
        when Unknown_Operation => False,
        when Reserve => Proposed.Selected.Present and then
          Proposed.Selected.Phase = Active and then
          Same_Reservation_Reference
            (Data, Proposed.Selected.Value, R.New_Reservation),
        when Consume | Release => Before.Selected.Present and then
          Proposed.Selected.Present and then
          Proposed.Selected.Phase = (if R.Kind = Consume then Consumed else Released)
          and then Same_Reservation_Reference
            (Data, Before.Selected.Value, Proposed.Selected.Value))
   with Ghost, Global => null;
   function Proposed_Row
     (Data : Byte_Array; Before, Proposed : Ledger_State; R : Request)
      return Boolean
   with Global => null,
     Post => Proposed_Row'Result = Proposed_Row_Reference (Data, Before, Proposed, R);
   function Change_Reference
     (Data : Byte_Array; Before, Proposed : Ledger_State; R : Request)
      return Boolean is
     (Span_Valid (Data, Before.Total) and then Span_Valid (Data, Proposed.Total)
      and then
      (if R.Kind = Unknown_Operation then False
       elsif R.Kind = Reserve then Span_Valid (Data, R.New_Reservation.Amount) and then
           Value (Data, Proposed.Total) = Value (Data, Before.Total) +
             Value (Data, R.New_Reservation.Amount)
       elsif R.Kind = Consume then Value (Data, Proposed.Total) = Value (Data, Before.Total)
       else Before.Selected.Present and then
           Span_Valid (Data, Before.Selected.Value.Amount) and then
           Value (Data, Before.Total) = Value (Data, Proposed.Total) +
             Value (Data, Before.Selected.Value.Amount)))
   with Ghost, Global => null;
   function Change_Conserved
     (Data : Byte_Array; Before, Proposed : Ledger_State; R : Request)
      return Boolean
   with Global => null,
     Post => Change_Conserved'Result = Change_Reference (Data, Before, Proposed, R);

   function Request_Shape
     (Data : Byte_Array; Before : Ledger_State; R : Request) return Boolean is
     (Present_Identity_Valid (Data, R.Requester) and then
      (case R.Kind is
         when Unknown_Operation => False,
         when Reserve => Epoch_Valid (Data, R.Expected_Epoch) and then
           Binding_Valid (Data, R.New_Reservation.Binding) and then
           Nonnegative_Valid (Data, R.New_Reservation.Amount) and then
           Span_Valid (Data, R.Ceiling) and then
           Same_Identity (Data, R.Requester, R.New_Reservation.Binding.Owner)
           and then Same_Identity
             (Data, Before.Scope.Universe, R.New_Reservation.Binding.Universe),
         when Consume | Release =>
           Present_Identity_Valid (Data, R.Reservation) and then
           Present_Identity_Valid (Data, R.Operation)))
   with Global => null;

   --  Complete closed first-refusal equation, independent of Check/Apply and
   --  their desired theorem. Mathematical equality is not a trusted admission
   --  Boolean. All selectors are guarded over the complete variant domain.
   function Decision_Reference
     (Data : Byte_Array; Before, Proposed : Ledger_State;
      High_Water : High_Water_Observation; R : Request) return Result_Status is
     (if R.Kind = Unknown_Operation then Unknown_Kind
      elsif not State_Shape (Data, Before) then Invalid_Before
      elsif not State_Shape (Data, Proposed) then Invalid_Proposed
      elsif not High_Water.Epoch.Present then Observation_Absent
      elsif not Context_Valid (Data, High_Water.Scope) or else
        not Epoch_Valid (Data, High_Water.Epoch) then Observation_Invalid
      elsif not Same_Context (Data, Before.Scope, High_Water.Scope)
        then Observation_Scope_Mismatch
      elsif Value (Data, Before.Epoch.Value) /= Value (Data, High_Water.Epoch.Value)
        then High_Water_Mismatch
      elsif not Request_Shape (Data, Before, R) then Request_Invalid
      elsif R.Kind = Reserve and then
        Value (Data, R.Expected_Epoch.Value) /= Value (Data, Before.Epoch.Value)
        then Stale_Reserve_Epoch
      elsif R.Kind = Reserve and then Before.Selected.Present then Slot_Already_Exists
      elsif R.Kind in Consume | Release and then not Before.Selected.Present
        then Reservation_Absent
      elsif R.Kind in Consume | Release and then not Same_Identity
        (Data, R.Requester, Before.Selected.Value.Binding.Owner) then Wrong_Owner
      elsif R.Kind in Consume | Release and then not Same_Identity
        (Data, R.Reservation, Before.Selected.Value.Binding.Reservation)
        then Reservation_Mismatch
      elsif R.Kind in Consume | Release and then not Same_Identity
        (Data, R.Operation, Before.Selected.Value.Binding.Operation)
        then Operation_Mismatch
      elsif R.Kind in Consume | Release and then Before.Selected.Phase = Released
        then Already_Released
      elsif R.Kind in Consume | Release and then Before.Selected.Phase = Consumed
        then Already_Consumed
      elsif not Conserved_Reference (Data, Before) then Before_Conservation_Mismatch
      elsif not Same_Context (Data, Before.Scope, Proposed.Scope) then Context_Changed
      elsif Value (Data, Before.Other_Reservations) /=
        Value (Data, Proposed.Other_Reservations) then Remainder_Changed
      elsif not Proposed_Row_Reference (Data, Before, Proposed, R)
        then Proposed_Row_Mismatch
      elsif Value (Data, Proposed.Epoch.Value) /= Value (Data, Before.Epoch.Value) + 1
        then Epoch_Not_Successor
      elsif not Conserved_Reference (Data, Proposed) then Proposed_Conservation_Mismatch
      elsif not Change_Reference (Data, Before, Proposed, R)
        then Transition_Conservation_Mismatch
      elsif R.Kind = Reserve and then
        Value (Data, Proposed.Total) > Value (Data, R.Ceiling) then Limit_Exceeded
      else Ready)
   with Ghost, Global => null;
   function Check
     (Data : Byte_Array; Before, Proposed : Ledger_State;
      High_Water : High_Water_Observation; R : Request) return Result_Status
   with Global => null,
     Post => Check'Result = Decision_Reference (Data, Before, Proposed, High_Water, R)
       and then (if Check'Result = Ready then
         Before.Epoch.Present and then Proposed.Epoch.Present and then
         Value (Data, Proposed.Epoch.Value) = Value (Data, Before.Epoch.Value) + 1
         and then Conserved_Reference (Data, Before)
         and then Conserved_Reference (Data, Proposed)
         and then Change_Reference (Data, Before, Proposed, R));
   procedure Apply
     (Data : Byte_Array; State : in out Ledger_State; Proposed : Ledger_State;
      High_Water : High_Water_Observation; R : Request; Status : out Result_Status)
   with Global => null, Always_Terminates,
     Post => Status = Decision_Reference (Data, State'Old, Proposed, High_Water, R)
       and then (if Status = Ready then State = Proposed else State = State'Old)
       and then (if Status = Ready then
          Conserved_Reference (Data, State) and then
          Change_Reference (Data, State'Old, State, R));
end Resource_Reservation_Transition;

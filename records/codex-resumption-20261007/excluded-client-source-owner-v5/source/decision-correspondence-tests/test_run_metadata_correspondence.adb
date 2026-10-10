with Resource_Run_Ledger;
procedure Test_Run_Metadata_Correspondence is
   package L renames Resource_Run_Ledger;
   package Q renames L.Q;
   A : constant Q.Byte_Array (1 .. 1) := (others => 0);
   Id : constant L.Identity := (True, (1, 0));
   Other_Id : constant L.Identity := (True, (1, 1));
   None : constant L.Identity := (Present => False);
   Zero : constant Q.Quantity := (False, 1, 0);
   Scope : constant L.Context := (Id, Id, Id, Id, Id, Id, Id, Id, (True, Zero));
   Bound : constant L.Binding := (Id, Id, Id, Id, Id, Id, Id, Id, Id, (True, Zero));
   Before : L.Row := (Scope, Bound, None, L.Held_Capacity, L.Reserved,
     Zero, (Present => False), None, None, None, None);
   Proposed : L.Row := Before;
   Observed : L.Native_Row := (Scope, (True, Zero), Bound,
     Id, Id, Id, Id, L.Unknown);
   R : L.Request := (L.Unknown_Operation, Scope, (True, Zero),
     Id, Id, Id, Id, Id, Bound, Before);
   procedure Require (Name : String; Actual, Expected : Boolean) is
   begin
      if Actual /= Expected then raise Program_Error with Name; end if;
   end Require;
   procedure Equation is
   begin
      L.Changed_Row_Composition_Equality (A, Before, Proposed, Observed, R);
   end Equation;
begin
   Require ("all_absent_metadata_preserved", L.Same_Run_Metadata (A, Before, Proposed), True);
   Proposed.Cgroup := Other_Id;
   Require ("typed_absence_not_present_identifier", L.Same_Run_Metadata (A, Before, Proposed), False);
   Proposed := Before;
   for Kind in L.Operation loop
      R.Kind := Kind;
      Equation;
   end loop;
   R.Kind := L.Unknown_Operation;
   Require ("unknown_always_refuses", L.Changed_Row_Allowed (A, Before, Proposed, Observed, R), False);
   R.Kind := L.Reserve;
   Require ("reserve_uses_separate_additive_relation", L.Changed_Row_Allowed (A, Before, Proposed, Observed, R), False);
   R.Kind := L.Record_Launch_Intent;
   Proposed.State := L.Launch_Intent;
   Proposed.Planned_Unit := Id;
   Equation;
   Require ("original_launch_intent_positive", L.Changed_Row_Allowed (A, Before, Proposed, Observed, R), True);
   Before := Proposed;
   R.Kind := L.Record_Running;
   Proposed.State := L.Running;
   Proposed.Actual_Unit := Id; Proposed.Cgroup := Id; Proposed.Invocation := Id;
   Observed.Observed := L.Live;
   Equation;
   Require ("original_running_positive", L.Changed_Row_Allowed (A, Before, Proposed, Observed, R), True);
   Before := Proposed;
   R.Kind := L.Record_Terminating; Proposed.State := L.Terminating;
   Equation;
   Require ("original_terminating_positive", L.Changed_Row_Allowed (A, Before, Proposed, Observed, R), True);
   R.Kind := L.Record_Terminal; Proposed.State := L.Terminal; Observed.Observed := L.Reaped;
   Equation;
   Require ("original_terminal_positive", L.Changed_Row_Allowed (A, Before, Proposed, Observed, R), True);
   Before := Proposed; R.Kind := L.Release_Hold; Proposed.State := L.Released;
   Equation;
   Require ("original_release_positive", L.Changed_Row_Allowed (A, Before, Proposed, Observed, R), True);
   Proposed.Cgroup := Other_Id;
   Equation;
   Require ("release_metadata_change_refuses", L.Changed_Row_Allowed (A, Before, Proposed, Observed, R), False);
   Proposed := Before; Before.Kind := L.Irreversible_Budget; Proposed.Kind := Before.Kind;
   R.Kind := L.Charge_Budget; Proposed.State := L.Charged;
   Equation;
   Require ("original_charge_positive", L.Changed_Row_Allowed (A, Before, Proposed, Observed, R), True);
   Before.Kind := L.Held_Capacity; Before.State := L.Launch_Intent;
   Before.Actual_Unit := None; Before.Cgroup := None; Before.Invocation := None;
   Proposed := Before; Proposed.State := L.Settlement_Unknown;
   R.Kind := L.Retain_Uncertain; Observed.Observed := L.Unknown;
   Equation;
   Require ("original_unknown_remains_held", L.Changed_Row_Allowed (A, Before, Proposed, Observed, R), True);
end Test_Run_Metadata_Correspondence;

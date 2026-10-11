with Worldline.Root_Custody_Model;

--  Complete value projections over full supplied rows. Chain authentication,
--  raw decode and fold are mandatory in the consuming native decision; there
--  is deliberately no caller-supplied Is_Current or Fold_Ready input here.
--  Termination remains REQUIRED for every precondition-satisfying input:
--  these ordinary side-effect-free SPARK functions have the intrinsic
--  termination obligation documented by this toolchain's E0016. Explicit
--  per-function Always_Terminates is illegal here; no obligation is waived.
package Worldline.Root_Custody_Context with SPARK_Mode is
   package M renames Worldline.Root_Custody_Model;
   package Q renames M.Q;
   package L renames M.L;
   use type Q.Ordering;
   use type Q.Byte_Count;
   use type M.Root_Phase;
   use type M.Owner;
   use type M.Actor;
   use type Worldline.Hash;

   type Root_Reference is record
      Generation : Q.Quantity;
      Operation  : M.Identity;
      Head       : M.Digest;
   end record;

   type Context_Status is (Projected, Implicit_Genesis, Binding_Not_Established);
   type Store_Owner_Result (Status : Context_Status := Binding_Not_Established)
   is record
      case Status is
         when Projected =>
            Index : Q.Byte_Index;
            Value : M.Owner;
         when Implicit_Genesis => null;
         when Binding_Not_Established => null;
      end case;
   end record;

   type Physical_Status is (Physical_Projected, Physical_Binding_Not_Established);
   type Physical_Actor_Result
     (Status : Physical_Status := Physical_Binding_Not_Established)
   is record
      case Status is
         when Physical_Projected =>
            Index : Q.Byte_Index;
            Value : M.Actor;
         when Physical_Binding_Not_Established => null;
      end case;
   end record;

   function Generation_Valid (Data : Q.Byte_Array; Value : Q.Quantity)
      return Boolean is
     (Q.Span_Valid (Data, Value) and then
      not Q.Is_Negative (Data, Value) and then not Q.Is_Zero (Data, Value))
   with Global => null;

   --  Structural relation required by the original generation fold: the only
   --  non-Ended row is the latest, every older row remains Ended, no duplicate
   --  generation is dropped, and the empty roster denotes implicit S0.
   --  This does not establish that the supplied roster is authentic/complete.
   function Root_Roster_Consistent
     (Data : Q.Byte_Array; Roots : M.Root_State_Array) return Boolean is
     ((for all I in Roots'Range => Generation_Valid (Data, Roots (I).Generation))
      and then
      (for all I in Roots'Range =>
         (for all J in Roots'Range =>
            (if I /= J then
               Q.Compare (Data, Roots (I).Generation, Roots (J).Generation)
                 /= Q.Equal)))
      and then
      (Roots'Length = 0 or else
         (for some I in Roots'Range =>
            Roots (I).Phase /= M.Ended and then
              (for all J in Roots'Range =>
                 (if J /= I then Roots (J).Phase = M.Ended and then
                    Q.Compare (Data, Roots (J).Generation,
                               Roots (I).Generation) = Q.Less)))))
   with Global => null;

   function Root_Joined
     (Data : Q.Byte_Array; State : M.Root_State; Reference : Root_Reference)
      return Boolean is
     (Generation_Valid (Data, Reference.Generation) and then
      Generation_Valid (Data, State.Generation) and then
      Q.Compare (Data, State.Generation, Reference.Generation) = Q.Equal
      and then L.Optional_Same (Data, State.Operation, Reference.Operation)
      and then State.Head = Reference.Head)
   with Global => null;

   --  Total original value equation; this table alone establishes no owner.
   --  Current-store selection and its non-Ended requirement remain below.
   function Original_Owner_Equation (State : M.Root_State) return M.Owner is
     (case State.Phase is
               when M.Front_Owned | M.Prepared | M.Held | M.Running |
                    M.Execution_Native | M.Execution_Ack | M.Handoff_Intent |
                    M.Front_Close_Intent => M.Front,
               when M.Front_Closed | M.Transfer_Sent | M.Roster_Evidence |
                    M.Abandoned | M.Front_Retained_Escrow => M.None,
               when M.Worker_Owned | M.Original_Result | M.Handler_Terminal |
                    M.Worker_Relinquish => M.Worker,
               when M.Handoff_Aborted =>
                 (if State.Owners_Open then
                    M.Front else M.None),
               when M.Historical_Settlement =>
                 (if State.Owners_Open then
                    M.Front else M.Collector),
               when M.Custody_Returned | M.Front_Reconstruction => M.Collector,
               when M.Unknown => M.Reconciler,
               when M.Ended => M.None)
   with Global => null;

   --  The current-store table is never applied to a historical Ended row.
   --  Implicit_Genesis means the original S0 value view; it is not a claim
   --  that missing durable state is genuine genesis. Only authenticated
   --  native genesis/chain/fold can establish that at the effect boundary.
   function Current_Store_Owner
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Reference : Root_Reference) return Store_Owner_Result
   with Global => null,
     Post =>
       (if not Root_Roster_Consistent (Data, Roots) then
          Current_Store_Owner'Result.Status = Binding_Not_Established
        elsif Roots'Length = 0 then
          Current_Store_Owner'Result.Status = Implicit_Genesis
        elsif (for some I in Roots'Range =>
                 Roots (I).Phase /= M.Ended and then
                 Root_Joined (Data, Roots (I), Reference)) then
          Current_Store_Owner'Result.Status = Projected and then
          Current_Store_Owner'Result.Index in Roots'Range and then
          Roots (Current_Store_Owner'Result.Index).Phase /= M.Ended and then
          Root_Joined (Data, Roots (Current_Store_Owner'Result.Index), Reference)
          and then Current_Store_Owner'Result.Value =
            Original_Owner_Equation (Roots (Current_Store_Owner'Result.Index))
        else Current_Store_Owner'Result.Status = Binding_Not_Established);

   --  Exact original physical actor table, deliberately including Ended.
   --  Projection alone never licenses a physical event or resource release:
   --  authentic CLOSED/wait/drain/row/effect operands remain necessary.
   function Physical_Actor
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Original_Root : Root_Reference) return Physical_Actor_Result
   with Global => null,
     Post =>
       (if Root_Roster_Consistent (Data, Roots) and then
           L.Id_Valid (Data, Original_Root.Operation) and then
           (for some I in Roots'Range =>
              Root_Joined (Data, Roots (I), Original_Root)) then
          Physical_Actor'Result.Status = Physical_Projected and then
          Physical_Actor'Result.Index in Roots'Range and then
          Root_Joined (Data, Roots (Physical_Actor'Result.Index), Original_Root)
          and then Physical_Actor'Result.Value =
            (if Roots (Physical_Actor'Result.Index).Owners_Open or else
                Roots (Physical_Actor'Result.Index).Phase in
                  M.Abandoned | M.Front_Retained_Escrow | M.Handoff_Aborted
             then M.Front else M.Collector)
        else Physical_Actor'Result.Status = Physical_Binding_Not_Established);
end Worldline.Root_Custody_Context;

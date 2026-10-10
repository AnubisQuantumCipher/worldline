with Worldline.Root_Custody_Replay;

--  Complete semantic ABANDON row after X4 and X5 in the same transaction.
--  NOT a substitute for those unavailable authentication/fold implementations.
--  No input is a producer-computed permission/Ready/MAC-valid Boolean.
package Worldline.Root_Custody_Abandon with SPARK_Mode is
   package R renames Worldline.Root_Custody_Replay;
   package P renames R.P;
   package C renames P.C;
   package M renames R.M;
   package Q renames R.Q;
   package L renames R.L;
   use type Q.Byte_Count;
   use type Q.Ordering;
   use type M.Root_Phase;
   use type M.Event_Kind;
   use type M.Subject_Kind;
   use type M.Actor;
   use type M.Root_State;
   use type R.Replay_Status;
   use type Worldline.Hash;

   --  Original CAS fields for a root row. No physical flags or inactive
   --  nullable field is added as an extra client CAS condition.
   type Expected_Root is record
      Generation : Q.Quantity;
      Operation : M.Identity;
      Head : M.Digest;
      Phase : M.Root_Phase;
      Owners_Open : Boolean;
      Reattach_Epoch : Q.Quantity;
   end record;
   type Alternative_Set is (Ack_Set, Request_Set, Drain_Set);
   type Alternative_Row is record
      Generation : Q.Quantity;
      Operation : M.Identity;
      Kind_Of_Subject : M.Subject_Kind;
      Subject : M.Identity;
      Subgeneration : Q.Quantity;
      Set : Alternative_Set;
      Event_Id : M.Digest;
   end record;
   type Alternative_Rows is array (Q.Byte_Index range <>) of Alternative_Row;
   function Ack_Kind (Kind : M.Event_Kind) return Boolean is
     (Kind in M.Custody_Ack_Event | M.Abandon_Event | M.Handoff_Abort_Event)
   with Global => null;
   function Same_Alternative
     (Data : Q.Byte_Array; Left, Right : M.Event_Record) return Boolean is
     (Q.Compare (Data, Left.Generation, Right.Generation) = Q.Equal and then
      L.Optional_Same (Data, Left.Operation, Right.Operation) and then
      Left.Kind_Of_Subject = Right.Kind_Of_Subject and then
      L.Optional_Same (Data, Left.Subject, Right.Subject) and then
      Q.Compare (Data, Left.Subgeneration, Right.Subgeneration) = Q.Equal)
   with Global => null;
   function Row_Joined
     (Data : Q.Byte_Array; Row : Alternative_Row; Event : M.Event_Record)
      return Boolean is
     (Row.Set = Ack_Set and then Ack_Kind (Event.Kind) and then
      Row.Event_Id = Event.Event_Id and then
      Q.Compare (Data, Row.Generation, Event.Generation) = Q.Equal and then
      L.Optional_Same (Data, Row.Operation, Event.Operation) and then
      Row.Kind_Of_Subject = Event.Kind_Of_Subject and then
      L.Optional_Same (Data, Row.Subject, Event.Subject) and then
      Q.Compare (Data, Row.Subgeneration, Event.Subgeneration) = Q.Equal)
   with Global => null;
   --  Both directions prevent a supplied free ACK table from omitting its
   --  retained ACK event. Other alternative families are not reinterpreted.
   function Ack_Table_Corresponds
     (Data : Q.Byte_Array; Events : R.Retained_Events; Rows : Alternative_Rows)
      return Boolean is
     ((for all Item of Events =>
         (if Ack_Kind (Item.Event.Kind) then
            (for some Row of Rows => Row_Joined (Data, Row, Item.Event)))) and then
      (for all Row of Rows =>
         (if Row.Set = Ack_Set then
            (for some Item of Events => Row_Joined (Data, Row, Item.Event)))))
   with Global => null;
   function Alternative_Allowed
     (Data : Q.Byte_Array; Events : R.Retained_Events; Proposed : M.Event_Record)
      return Boolean is
     (for all Item of Events =>
        (if Ack_Kind (Item.Event.Kind) and then
             Same_Alternative (Data, Item.Event, Proposed)
         then Item.Event.Kind = Proposed.Kind)) with Global => null;
   --  F.6 step 3 permits free or this kind. Step 7 still requires the original
   --  Transfer_Sent/Roster_Evidence phase; a repeated append is handled first.
   function Bound (Data : Q.Byte_Array; State : M.Root_State;
                   Expected : Expected_Root) return Boolean is
     (Q.Compare (Data, State.Generation, Expected.Generation) = Q.Equal and then
      L.Optional_Same (Data, State.Operation, Expected.Operation))
   with Global => null;
   function CAS_Matches (Data : Q.Byte_Array; State : M.Root_State;
                         Expected : Expected_Root) return Boolean is
     (Bound (Data, State, Expected) and then State.Head = Expected.Head and then
      State.Phase = Expected.Phase and then State.Owners_Open = Expected.Owners_Open
      and then Q.Compare (Data, State.Reattach_Epoch, Expected.Reattach_Epoch) = Q.Equal)
   with Global => null;
   function Fresh_Inputs_Valid
     (Data : Q.Byte_Array; Roots : M.Root_State_Array; Expected : Expected_Root;
      Proposed : M.Event_Record) return Boolean is
     (C.Root_Roster_Consistent (Data, Roots) and then
      C.Generation_Valid (Data, Expected.Generation) and then
      Q.Span_Valid (Data, Expected.Reattach_Epoch) and then
      (not Expected.Operation.Present or else L.Id_Valid (Data, Expected.Operation))
      and then R.Key_Valid (Data, R.Key (Proposed)) and then
      (for all Root of Roots => Q.Span_Valid (Data, Root.Reattach_Epoch) and then
         (not Root.Operation.Present or else L.Id_Valid (Data, Root.Operation))))
   with Global => null;
   function Event_Bound (Data : Q.Byte_Array; Expected : Expected_Root;
                         Proposed : M.Event_Record) return Boolean is
     (Q.Compare (Data, Expected.Generation, Proposed.Generation) = Q.Equal and then
      L.Optional_Same (Data, Expected.Operation, Proposed.Operation) and then
      Proposed.Kind_Of_Subject = M.Root) with Global => null;
   function Rows_Valid (Data : Q.Byte_Array; Rows : Alternative_Rows)
      return Boolean is
     (for all Row of Rows => Q.Span_Valid (Data, Row.Generation) and then
        Q.Span_Valid (Data, Row.Subgeneration) and then
        (not Row.Operation.Present or else L.Id_Valid (Data, Row.Operation)) and then
        (not Row.Subject.Present or else L.Id_Valid (Data, Row.Subject)))
   with Global => null;
   function Legal_Abandon
     (Data : Q.Byte_Array; Roots : M.Root_State_Array; Events : R.Retained_Events;
      Rows : Alternative_Rows; Expected : Expected_Root; Proposed : M.Event_Record)
      return Boolean is
     (Proposed.Kind = M.Abandon_Event and then
      R.Inputs_Valid (Data, Events, R.Key (Proposed)) and then
      R.Resolve (Data, Events, R.Key (Proposed)).Status = R.No_Replay and then
      Fresh_Inputs_Valid (Data, Roots, Expected, Proposed) and then
      Rows_Valid (Data, Rows) and then
      Ack_Table_Corresponds (Data, Events, Rows) and then
      Alternative_Allowed (Data, Events, Proposed) and then
      Event_Bound (Data, Expected, Proposed) and then
      Proposed.Appending_Actor in M.Front | M.Reconciler and then
      (for some Root of Roots => CAS_Matches (Data, Root, Expected) and then
         Root.Phase in M.Transfer_Sent | M.Roster_Evidence))
   with Global => null;

   type Decision_Status is
     (Replay_Unchanged, Append_Abandon, Invalid_Operands, Ambiguous_History,
      History_Table_Mismatch, Alternative_Taken, CAS_Stale,
      Generation_Join_Failed, Phase_Not_Permitted, Actor_Not_Permitted);
   type Decision (Status : Decision_Status := Invalid_Operands) is record
      case Status is
         when Replay_Unchanged => Event_Position : Q.Byte_Index;
         when others => null;
      end case;
   end record;
   function Decide
     (Data : Q.Byte_Array; Roots : M.Root_State_Array; Events : R.Retained_Events;
      Rows : Alternative_Rows; Expected : Expected_Root; Proposed : M.Event_Record)
      return Decision
   with Global => null, Pre => Proposed.Kind = M.Abandon_Event,
     Post =>
       (Decide'Result.Status = Append_Abandon) =
          Legal_Abandon (Data, Roots, Events, Rows, Expected, Proposed) and then
       (Decide'Result.Status = Replay_Unchanged) =
          (R.Resolve (Data, Events, R.Key (Proposed)).Status = R.Found) and then
       (if Decide'Result.Status = Replay_Unchanged then
          Decide'Result.Event_Position in Events'Range and then
          R.Matches (Data, Events (Decide'Result.Event_Position), R.Key (Proposed)));

   function Next_Abandon
     (Data : Q.Byte_Array; Roots : M.Root_State_Array; Events : R.Retained_Events;
      Rows : Alternative_Rows; Expected : Expected_Root; Proposed : M.Event_Record)
      return M.Root_State_Array
   with Global => null,
     Pre => Legal_Abandon (Data, Roots, Events, Rows, Expected, Proposed),
     Post => Next_Abandon'Result'First = Roots'First and then
       Next_Abandon'Result'Last = Roots'Last and then
       (for all I in Roots'Range =>
          Next_Abandon'Result (I) =
            (if Bound (Data, Roots (I), Expected) then
                (Roots (I) with delta Phase => M.Abandoned, Head => Proposed.Event_Id)
             else Roots (I)));
   --  All subjects, resource rows, queues, task lifetimes and physical flags
   --  remain untouched. ABANDON does NOT authorize stop, release, reconstruct,
   --  result overwrite or another generation. FRONT_RETAINED_ESCROW is later.
end Worldline.Root_Custody_Abandon;

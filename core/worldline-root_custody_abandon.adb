package body Worldline.Root_Custody_Abandon with SPARK_Mode is
   function Decide
     (Data : Q.Byte_Array; Roots : M.Root_State_Array; Events : R.Retained_Events;
      Rows : Alternative_Rows; Expected : Expected_Root; Proposed : M.Event_Record)
      return Decision
   is
      Replay : constant R.Replay_Result := R.Resolve (Data, Events, R.Key (Proposed));
   begin
      case Replay.Status is
         when R.Found => return (Status => Replay_Unchanged, Event_Position => Replay.Position);
         when R.Invalid_Operands => return (Status => Invalid_Operands);
         when R.Ambiguous_History => return (Status => Ambiguous_History);
         when R.No_Replay => null;
      end case;
      if not Fresh_Inputs_Valid (Data, Roots, Expected, Proposed) or else
         not Rows_Valid (Data, Rows)
      then
         return (Status => Invalid_Operands);
      elsif not Ack_Table_Corresponds (Data, Events, Rows) then
         return (Status => History_Table_Mismatch);
      elsif not Alternative_Allowed (Data, Events, Proposed) then
         return (Status => Alternative_Taken);
      elsif not (for some Root of Roots => CAS_Matches (Data, Root, Expected)) then
         return (Status => CAS_Stale);
      elsif not Event_Bound (Data, Expected, Proposed) or else
         not (for some Root of Roots => Bound (Data, Root, Expected) and then
                Root.Phase /= M.Ended)
      then
         return (Status => Generation_Join_Failed);
      elsif not (for some Root of Roots => CAS_Matches (Data, Root, Expected) and then
                   Root.Phase in M.Transfer_Sent | M.Roster_Evidence)
      then
         return (Status => Phase_Not_Permitted);
      elsif Proposed.Appending_Actor not in M.Front | M.Reconciler then
         return (Status => Actor_Not_Permitted);
      end if;
      return (Status => Append_Abandon);
   end Decide;
   function Next_Abandon
     (Data : Q.Byte_Array; Roots : M.Root_State_Array; Events : R.Retained_Events;
      Rows : Alternative_Rows; Expected : Expected_Root; Proposed : M.Event_Record)
      return M.Root_State_Array
   is
      Result : M.Root_State_Array (Roots'Range) := Roots;
   begin
      for I in Roots'Range loop
         if Bound (Data, Roots (I), Expected) then
            Result (I).Phase := M.Abandoned;
            Result (I).Head := Proposed.Event_Id;
         end if;
         pragma Loop_Invariant
           (for all J in Roots'First .. I => Result (J) =
              (if Bound (Data, Roots (J), Expected) then
                  (Roots (J) with delta Phase => M.Abandoned, Head => Proposed.Event_Id)
               else Roots (J)));
         pragma Loop_Invariant
           (for all J in Roots'Range => (if J > I then Result (J) = Roots (J)));
      end loop;
      return Result;
   end Next_Abandon;
end Worldline.Root_Custody_Abandon;

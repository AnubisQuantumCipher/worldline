package body Worldline.Root_Custody_Request_Abandon with SPARK_Mode is
   function Decide
     (Data : Q.Byte_Array; Roots : M.Root_State_Array; Subjects : M.Subject_State_Array;
      Events : R.Retained_Events; Rows : A.Alternative_Rows;
      Root : A.Expected_Root; Expected : Expected_Request; Proposed : M.Event_Record)
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
      if not A.Fresh_Inputs_Valid (Data, Roots, Root, Proposed) or else
         not Subjects_Valid (Data, Subjects, Expected) or else not A.Rows_Valid (Data, Rows)
      then
         return (Status => Invalid_Operands);
      elsif not Table_Corresponds (Data, Events, Rows) then
         return (Status => History_Table_Mismatch);
      elsif not Alternative_Allowed (Data, Events, Proposed) then
         return (Status => Alternative_Taken);
      elsif not (for some Item of Roots => A.CAS_Matches (Data, Item, Root)) or else
            not (for some Item of Subjects => Subject_CAS (Data, Item, Expected))
      then
         return (Status => CAS_Stale);
      elsif not Event_Bound (Data, Root, Expected, Proposed) or else
            not Generation_Allowed (Data, Roots, Events, Root)
      then
         return (Status => Generation_Join_Failed);
      elsif Expected.Phase /= M.Transfer_Intent then
         return (Status => Phase_Not_Permitted);
      elsif not Transfer_Head_Joined (Data, Events, Expected, Proposed) then
         return (Status => Transfer_Head_Mismatch);
      elsif Proposed.Appending_Actor not in M.Front | M.Reconciler then
         return (Status => Actor_Not_Permitted);
      end if;
      return (Status => Append_Request_Abandon);
   end Decide;

   procedure Apply_Next
     (Data : Q.Byte_Array; Roots : in out M.Root_State_Array;
      Subjects : in out M.Subject_State_Array;
      Events : R.Retained_Events; Rows : A.Alternative_Rows;
      Root : A.Expected_Root; Expected : Expected_Request; Proposed : M.Event_Record)
   is
   begin
      for I in Subjects'Range loop
         if Subject_Bound (Data, Subjects (I), Expected) then
            Subjects (I).Request := M.Abandoned;
            Subjects (I).Head := Proposed.Event_Id;
         end if;
         pragma Loop_Invariant
           (for all J in Subjects'First .. I => Subjects (J) =
              (if Subject_Bound (Data, Subjects'Loop_Entry (J), Expected) then
                  (Subjects'Loop_Entry (J) with delta Request => M.Abandoned,
                     Head => Proposed.Event_Id)
               else Subjects'Loop_Entry (J)));
         pragma Loop_Invariant
           (for all J in Subjects'Range =>
              (if J > I then Subjects (J) = Subjects'Loop_Entry (J)));
      end loop;
   end Apply_Next;
end Worldline.Root_Custody_Request_Abandon;

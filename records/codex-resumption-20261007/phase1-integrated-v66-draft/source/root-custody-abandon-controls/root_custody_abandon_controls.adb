with Worldline.Root_Custody_Abandon;
procedure Root_Custody_Abandon_Controls is
   package A renames Worldline.Root_Custody_Abandon;
   package R renames A.R;
   package M renames A.M;
   package Q renames A.Q;
   use type A.Decision_Status;
   use type M.Root_State;
   use type M.Root_Phase;
   use type M.Actor;
   Data : constant Q.Byte_Array := (1 => 1, 2 => 2);
   One : constant Q.Quantity := (Negative => False, First => 1, Length => 1);
   Zero : constant Q.Quantity := (Negative => False, First => 1, Length => 0);
   Id : constant M.Identity := (Present => True, Value => (First => 1, Length => 1));
   Root : M.Root_State :=
     (Generation => One, Operation => Id, Phase => M.Transfer_Sent,
      Before_Unknown => M.Front_Owned, Owners_Open => False,
      Abort_Kind => M.Dispatched, Physical => (Launched => True, others => False),
      Unknown_Cause => (Present => False), Reattach_Epoch => Zero, Head => (others => 1));
   Roots : M.Root_State_Array (1 .. 1) := (1 => Root);
   Expected : A.Expected_Root :=
     (Generation => One, Operation => Id, Head => Root.Head, Phase => Root.Phase,
      Owners_Open => False, Reattach_Epoch => Zero);
   Proposed : M.Event_Record :=
     (Kind => M.Abandon_Event, Generation => One, Operation => Id,
      Kind_Of_Subject => M.Root, Subject => (Present => False), Subgeneration => Zero,
      Appending_Actor => M.Front, Record_Digest => (others => 1), Event_Id => (others => 2));
   History : R.Retained_Events (1 .. 1) :=
     (1 => (Event => Proposed, Previous => Root.Head, Mac => (others => 1),
            Record_Bytes => Id, Base_Archive => Id));
   Rows : A.Alternative_Rows (1 .. 1) :=
     (1 => (Generation => One, Operation => Id, Kind_Of_Subject => M.Root,
            Subject => (Present => False), Subgeneration => Zero, Set => A.Ack_Set,
            Event_Id => Proposed.Event_Id));
   procedure Check (Condition : Boolean) is
   begin
      if not Condition then raise Program_Error with "ABANDON control failed"; end if;
   end Check;
begin
   for Phase in M.Root_Phase loop
      for Caller in M.Actor loop
         Roots (1).Phase := Phase;
         Expected.Phase := Phase;
         Proposed.Appending_Actor := Caller;
         Check ((A.Decide (Data, Roots, History (1 .. 0), Rows (1 .. 0),
                          Expected, Proposed).Status = A.Append_Abandon) =
                  (Phase in M.Transfer_Sent | M.Roster_Evidence and then
                   Caller in M.Front | M.Reconciler));
      end loop;
   end loop;
   Roots (1) := Root;
   Expected.Phase := Root.Phase;
   Proposed.Appending_Actor := M.Front;
   declare
      After : constant M.Root_State_Array := A.Next_Abandon
        (Data, Roots, History (1 .. 0), Rows (1 .. 0), Expected, Proposed);
   begin
      Check (After (1) = (Root with delta Phase => M.Abandoned, Head => Proposed.Event_Id));
   end;
   --  Original exact CAS fields are enforced, with no physical-field CAS added.
   Expected.Owners_Open := True;
   Check (A.Decide (Data, Roots, History (1 .. 0), Rows (1 .. 0), Expected,
                    Proposed).Status = A.CAS_Stale);
   Expected.Owners_Open := False;
   Expected.Head := (others => 2);
   Check (A.Decide (Data, Roots, History (1 .. 0), Rows (1 .. 0), Expected,
                    Proposed).Status = A.CAS_Stale);
   --  Committed replay ignores stale phase/head/actor and never computes Next.
   Roots (1).Phase := M.Unknown;
   Proposed.Appending_Actor := M.Collector;
   Check (A.Decide (Data, Roots, History, Rows, Expected,
                    Proposed).Status = A.Replay_Unchanged);
   Roots (1) := Root;
   Expected.Head := Root.Head;
   Proposed.Appending_Actor := M.Reconciler;
   History (1).Event.Kind := M.Custody_Ack_Event;
   Check (A.Decide (Data, Roots, History, Rows, Expected,
                    Proposed).Status = A.Alternative_Taken);
   Check (A.Decide (Data, Roots, History, Rows (1 .. 0), Expected,
                    Proposed).Status = A.History_Table_Mismatch);
end Root_Custody_Abandon_Controls;

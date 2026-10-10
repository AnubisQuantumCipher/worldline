with Worldline.Root_Custody_Request_Abandon;
procedure Request_Abandon_Controls is
   package N renames Worldline.Root_Custody_Request_Abandon;
   package A renames N.A;
   package R renames N.R;
   package M renames N.M;
   package Q renames N.Q;
   use type N.Decision_Status;
   use type A.Decision_Status;
   use type M.Request_Phase;
   use type M.Actor;
   use type M.Root_State;
   use type M.Root_State_Array;
   use type M.Subject_State;
   Data : constant Q.Byte_Array := (1 => 1, 2 => 2);
   One : constant Q.Quantity := (Negative => False, First => 1, Length => 1);
   Two : constant Q.Quantity := (Negative => False, First => 2, Length => 1);
   Zero : constant Q.Quantity := (Negative => False, First => 1, Length => 0);
   Op : constant M.Identity := (Present => True, Value => (First => 1, Length => 1));
   Request_Id : constant M.Identity := (Present => True, Value => (First => 2, Length => 1));
   Base_Root : constant M.Root_State :=
     (Generation => Two, Operation => Op, Phase => M.Worker_Owned,
      Before_Unknown => M.Front_Owned, Owners_Open => False,
      Abort_Kind => M.Dispatched, Physical => (Launched => True, others => False),
      Unknown_Cause => (Present => False), Reattach_Epoch => Zero, Head => (others => 1));
   Original_Roots : constant M.Root_State_Array :=
     (1 => (Base_Root with delta Generation => One, Phase => M.Ended), 2 => Base_Root);
   Roots : M.Root_State_Array := Original_Roots;
   Root : A.Expected_Root :=
     (Generation => Two, Operation => Op, Head => Base_Root.Head,
      Phase => Base_Root.Phase, Owners_Open => False, Reattach_Epoch => Zero);
   Base_Subject : constant M.Subject_State :=
     (Kind => M.Request, Generation => Two, Subject => Request_Id,
      Subgeneration => Zero, Request => M.Transfer_Intent, Descriptor => M.Released,
      Mode => M.Relay, Position => (Present => True, Value => One),
      Carried_From => (Present => True, Value => One), Head => (others => 2));
   Original_Subjects : constant M.Subject_State_Array :=
     (1 => (Base_Subject with delta Generation => One),
      2 => (Base_Subject with delta Kind => M.Descriptor), 3 => Base_Subject);
   Subjects : M.Subject_State_Array := Original_Subjects;
   Expected : N.Expected_Request :=
     (Generation => Two, Subject => Request_Id, Subgeneration => Zero,
      Head => Base_Subject.Head, Phase => M.Transfer_Intent);
   Proposed : M.Event_Record :=
     (Kind => M.Request_Abandon_Event, Generation => Two, Operation => Request_Id,
      Kind_Of_Subject => M.Request, Subject => Request_Id, Subgeneration => Zero,
      Appending_Actor => M.Front, Record_Digest => (others => 1), Event_Id => (others => 3));
   Transfer : constant R.Retained_Event :=
     (Event => (Proposed with delta Kind => M.Request_Transfer_Intent_Event,
        Event_Id => Base_Subject.Head), Previous => (others => 1), Mac => (others => 1),
      Record_Bytes => Op, Base_Archive => Request_Id);
   Events : R.Retained_Events := (1 => Transfer, 2 => Transfer);
   Rows : A.Alternative_Rows :=
     (1 => (Generation => Two, Operation => Request_Id, Kind_Of_Subject => M.Request,
       Subject => Request_Id, Subgeneration => Zero, Set => A.Request_Set,
       Event_Id => Proposed.Event_Id));
   procedure Check (Condition : Boolean) is
   begin
      if not Condition then raise Program_Error with "request abandon control failed"; end if;
   end Check;
begin
   --  Every request phase/actor; a request operation differs from root's WL op.
   for Phase in M.Request_Phase loop
      for Caller in M.Actor loop
         Subjects (3).Request := Phase;
         Expected.Phase := Phase;
         Proposed.Appending_Actor := Caller;
         Check ((N.Decide (Data, Roots, Subjects, Events (1 .. 1), Rows (1 .. 0),
                    Root, Expected, Proposed).Status = N.Append_Request_Abandon) =
                  (Phase = M.Transfer_Intent and then Caller in M.Front | M.Reconciler));
      end loop;
   end loop;
   Subjects := Original_Subjects;
   Expected.Phase := M.Transfer_Intent;
   Proposed.Appending_Actor := M.Reconciler;
   N.Apply_Next (Data, Roots, Subjects, Events (1 .. 1), Rows (1 .. 0), Root, Expected, Proposed);
   Check (Roots = Original_Roots);
   Check (Subjects (1) = Original_Subjects (1) and then Subjects (2) = Original_Subjects (2));
   Check (Subjects (3) = (Base_Subject with delta Request => M.Abandoned, Head => Proposed.Event_Id));
   Subjects := Original_Subjects;
   Expected.Subgeneration := One;
   Check (N.Decide (Data, Roots, Subjects, Events (1 .. 1), Rows (1 .. 0), Root,
                    Expected, Proposed).Status = N.CAS_Stale);
   Expected.Subgeneration := Zero;
   Proposed.Operation := Op;
   Check (N.Decide (Data, Roots, Subjects, Events (1 .. 1), Rows (1 .. 0), Root,
                    Expected, Proposed).Status = N.Transfer_Head_Mismatch);
   Proposed.Operation := Request_Id;
   Events (2).Event := Proposed;
   Events (2).Event.Kind := M.Request_Intake_Event;
   Check (N.Decide (Data, Roots, Subjects, Events, Rows, Root,
                    Expected, Proposed).Status = N.Alternative_Taken);
   Check (N.Decide (Data, Roots, Subjects, Events, Rows (1 .. 0), Root,
                    Expected, Proposed).Status = N.History_Table_Mismatch);
   --  Historical XC-7 exception, without globally discarding Ended roots.
   Root.Generation := One; Root.Phase := M.Ended;
   Expected.Generation := One; Proposed.Generation := One;
   Events (1).Event.Generation := One;
   Check (N.Decide (Data, Roots, Subjects, Events (1 .. 1), Rows (1 .. 0), Root,
                    Expected, Proposed).Status = N.Append_Request_Abandon);
   Events (2).Event := (Proposed with delta Kind => M.Custody_Returned_Event,
      Kind_Of_Subject => M.Root, Subject => (Present => False));
   Check (N.Decide (Data, Roots, Subjects, Events, Rows (1 .. 0), Root,
                    Expected, Proposed).Status = N.Generation_Join_Failed);
   Events (2).Event := Proposed;
   Root.Head := (others => 3);
   Proposed.Appending_Actor := M.Worker;
   Check (N.Decide (Data, Roots, Subjects, Events, Rows (1 .. 0), Root,
                    Expected, Proposed).Status = N.Replay_Unchanged);

   --  Previously missing root ABANDON multiple-root preservation coverage.
   declare
      ARoots : M.Root_State_Array := Original_Roots;
      ARoot : A.Expected_Root :=
        (Generation => Two, Operation => Op, Head => Base_Root.Head,
         Phase => M.Transfer_Sent, Owners_Open => False, Reattach_Epoch => Zero);
      Abandon : constant M.Event_Record :=
        (Kind => M.Abandon_Event, Generation => Two, Operation => Op,
         Kind_Of_Subject => M.Root, Subject => (Present => False), Subgeneration => Zero,
         Appending_Actor => M.Front, Record_Digest => (others => 1), Event_Id => (others => 3));
   begin
      ARoots (2).Phase := M.Transfer_Sent;
      declare
         After : constant M.Root_State_Array := A.Next_Abandon
           (Data, ARoots, Events (1 .. 0), Rows (1 .. 0), ARoot, Abandon);
      begin
         Check (After (1) = ARoots (1));
         Check (After (2) = (ARoots (2) with delta Phase => M.Abandoned, Head => Abandon.Event_Id));
      end;
      ARoot.Generation := One; ARoot.Phase := M.Ended;
      Check (A.Decide (Data, ARoots, Events (1 .. 0), Rows (1 .. 0), ARoot,
        (Abandon with delta Generation => One)).Status = A.Generation_Join_Failed);
   end;
end Request_Abandon_Controls;

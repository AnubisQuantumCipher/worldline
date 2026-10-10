with Worldline.Root_Custody_Replay;
procedure Root_Custody_Replay_Controls is
   package R renames Worldline.Root_Custody_Replay;
   package M renames R.M;
   package Q renames R.Q;
   use type R.Replay_Status;
   use type Q.Byte_Count;
   use type R.Retained_Event;
   Data : constant Q.Byte_Array := (1 => 1, 2 => 2, 3 => 1);
   One : constant Q.Quantity := (Negative => False, First => 1, Length => 1);
   Alias_One : constant Q.Quantity := (Negative => False, First => 3, Length => 1);
   Other : constant Q.Quantity := (Negative => False, First => 2, Length => 1);
   Zero : constant Q.Quantity := (Negative => False, First => 1, Length => 0);
   Id : constant M.Identity := (Present => True, Value => (First => 1, Length => 1));
   Other_Id : constant M.Identity := (Present => True, Value => (First => 2, Length => 1));
   Item : constant R.Retained_Event :=
     (Event => (Kind => M.Prepared_Event, Generation => One, Operation => Id,
       Kind_Of_Subject => M.Root, Subject => (Present => False),
       Subgeneration => Zero, Appending_Actor => M.Front,
       Record_Digest => (others => 1), Event_Id => (others => 2)),
      Previous => (others => 1), Mac => (others => 2),
      Record_Bytes => Id, Base_Archive => Other_Id);
   Events : R.Retained_Events (1 .. 2) := (others => Item);
   Wanted : M.Replay_Identity := R.Key (Item.Event);
   Result : R.Replay_Result;
   procedure Check (Condition : Boolean) is
   begin
      if not Condition then raise Program_Error with "replay control failed"; end if;
   end Check;
   procedure Missing (Value : M.Replay_Identity) is
   begin
      Check (R.Resolve (Data, Events (1 .. 1), Value).Status = R.No_Replay);
   end Missing;
begin
   Result := R.Resolve (Data, Events (1 .. 1), Wanted);
   Check (Result.Status = R.Found and then Events (Result.Position) = Item);
   --  Numeric and identity arena addresses need not be identical.
   Wanted.Generation := Alias_One;
   Wanted.Operation := (Present => True, Value => (First => 3, Length => 1));
   Check (R.Resolve (Data, Events (1 .. 1), Wanted).Status = R.Found);
   --  No phase/head/owner/clock/current-generation operand can reject an
   --  authenticated old replay. Actor is NOT in the original replay key.
   Events (1).Event.Appending_Actor := M.Collector;
   Check (R.Resolve (Data, Events (1 .. 1), Wanted).Status = R.Found);
   Events (1) := Item;
   Wanted := R.Key (Item.Event);
   Missing ((Wanted with delta Generation => Other));
   Missing ((Wanted with delta Operation => Other_Id));
   Missing ((Wanted with delta Kind_Of_Subject => M.Request));
   Missing ((Wanted with delta Subject => Id));
   Missing ((Wanted with delta Subgeneration => Other));
   Missing ((Wanted with delta Kind => M.Held_Event));
   Missing ((Wanted with delta Record_Digest => (others => 2)));
   Check (R.Resolve (Data, Events (1 .. 0), Wanted).Status = R.No_Replay);
   Check (R.Resolve (Data, Events, Wanted).Status = R.Ambiguous_History);
   --  Invalid trailing record must not be hidden by an earlier matching row.
   Events (2).Base_Archive := (Present => False);
   Check (R.Resolve (Data, Events, Wanted).Status = R.Invalid_Operands);
   Events (2) := Item;
   Events (2).Event.Record_Digest := (others => 2);
   Result := R.Resolve (Data, Events, Wanted);
   Check (Result.Status = R.Found and then Result.Position = 1);
end Root_Custody_Replay_Controls;

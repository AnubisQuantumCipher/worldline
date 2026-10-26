--  OUTSIDE PRODUCTION. SOURCE PROPOSAL ONLY; UNCOMPILED / UNPROVED / UNRUN.
with UTF8_Chunk_Proposal;
package body UTF8_Coordinator_Proposal with SPARK_Mode is
   package C renames UTF8_Chunk_Proposal;
   package B renames Worldline.Producer_Bytes;
   use type C.Summary;

   function UTF8 (Bytes : String; Replace_Errors : Boolean) return B.Decoded is
      Quota : constant Positive := C.Quota_For (Bytes'Length);
      type Checkpoint is record
         Present : Boolean := False;
         Start, Before_Output, After_Output : Natural := 0;
         Item : C.Summary := (0, 0, False);
      end record
        with Dynamic_Predicate =>
          (if Checkpoint.Present then
             Checkpoint.Start < Bytes'Length and then
             Checkpoint.Before_Output <= Checkpoint.After_Output and then
             Checkpoint.Item.Output_Length =
               Checkpoint.After_Output - Checkpoint.Before_Output and then
             Checkpoint.Item.Valid and then
             Checkpoint.Item = C.Decode_Chunk
               (Bytes, Checkpoint.Start, Quota, Replace_Errors).Item);
      subtype Checkpoint_Count is Natural range 0 .. C.Checkpoint_Bound;
      type Checkpoint_Array is
        array (Positive range 1 .. C.Checkpoint_Bound) of Checkpoint;
      --  All default Present fields are False: default predicates skip Chunk.
      Saved : Checkpoint_Array := [others => <>];
      Count : Checkpoint_Count := 0;
      Position, Length : Natural := 0;
   begin
      if Bytes'Length = 0 then return (0, True, ""); end if;
      --  Division avoids Count*Quota overflow near Natural'Last.
      pragma Assert ((Bytes'Length - 1) / Quota < C.Checkpoint_Bound);
      while Position < Bytes'Length loop
         pragma Loop_Invariant (Position <= Bytes'Length);
         pragma Loop_Invariant
           (if Position < Bytes'Length then Count <= Position / Quota);
         pragma Loop_Invariant
           (if Count = 0 then Position = 0 and then Length = 0
            else Saved (Count).Item.Next_Position = Position and then
                 Saved (Count).After_Output = Length);
         --  Scalar fields only: no Chunk/prefix decoder in checked invariants.
         pragma Loop_Invariant
           (for all I in 1 .. Count =>
              Saved (I).Present and then Saved (I).Item.Valid and then
              Saved (I).Start < Saved (I).Item.Next_Position and then
              Saved (I).Item.Next_Position <= Position and then
              Saved (I).Before_Output <= Saved (I).After_Output and then
              Saved (I).After_Output <= Length and then
              Saved (I).Item.Output_Length =
                Saved (I).After_Output - Saved (I).Before_Output);
         pragma Loop_Invariant
           (for all I in 1 .. Count =>
              (if I = 1 then
                 Saved (I).Start = 0 and then Saved (I).Before_Output = 0
               else Saved (I).Start = Saved (I - 1).Item.Next_Position and then
                 Saved (I).Before_Output = Saved (I - 1).After_Output));
         pragma Loop_Variant (Increases => Position);
         pragma Assert (Count < C.Checkpoint_Bound);
         declare
            Block : constant C.Chunk_Result :=
              C.Decode_Chunk (Bytes, Position, Quota, Replace_Errors);
         begin
            --  Original strict-invalid and first-pass extent/overflow refusal.
            if not Block.Item.Valid then return (0, False, ""); end if;
            if Block.Item.Next_Position <= Position or else
              Block.Item.Next_Position > Bytes'Length or else
              Block.Item.Output_Length > Natural'Last - Length
            then
               return (0, False, "");
            end if;
            Saved (Count + 1) :=
              (Present => True, Start => Position, Before_Output => Length,
               After_Output => Length + Block.Item.Output_Length,
               Item => Block.Item);
            Count := Count + 1;
            Position := Block.Item.Next_Position;
            Length := Length + Block.Item.Output_Length;
         end;
      end loop;
      pragma Assert (Count > 0);
      --  Only successful complete sizing allocates the exact public result.
      return Result : B.Decoded (Length) with Relaxed_Initialization do
         Result.Valid := True;
         Position := 0;
         declare
            Used : Natural := 0;
         begin
            for I in 1 .. Count loop
               pragma Loop_Invariant (Position <= Bytes'Length);
               pragma Loop_Invariant (Used <= Result.Length);
               pragma Loop_Invariant (Result.Valid'Initialized);
               pragma Loop_Invariant
                 (if Used > 0 then Result.Data (1 .. Used)'Initialized);
               pragma Loop_Invariant
                 (if I = 1 then Position = 0 and then Used = 0
                  else Position = Saved (I - 1).Item.Next_Position and then
                    Used = Saved (I - 1).After_Output);
               declare
                  Block : constant C.Chunk_Result := C.Decode_Chunk
                    (Bytes, Saved (I).Start, Quota, Replace_Errors);
               begin
                  pragma Assert (Saved (I).Present);
                  pragma Assert (Block.Item = Saved (I).Item);
                  --  Raise 1: original replay source/strict-validation mismatch.
                  if Block.Item.Next_Position <= Position or else
                    Block.Item.Next_Position > Bytes'Length or else
                    not Block.Item.Valid
                  then
                     raise Program_Error with "UTF8 decode extent mismatch";
                  end if;
                  --  Raise 2: original public-output/source-copy extent guard.
                  if Block.Item.Output_Length > Result.Length - Used or else
                    Block.Item.Output_Length > Block.Capacity
                  then
                     raise Program_Error with "UTF8 decode extent mismatch";
                  end if;
                  --  Raise 3: preserve the original replacement-space failure
                  --  site as the general saved output-interval mismatch guard.
                  --  Chunk's own checked bound covers replacement construction.
                  if Saved (I).Start /= Position or else
                    Saved (I).Before_Output /= Used or else
                    Saved (I).After_Output < Used or else
                    Saved (I).After_Output - Used /= Block.Item.Output_Length
                  then
                     raise Program_Error with "UTF8 decode extent mismatch";
                  end if;
                  if Block.Item.Output_Length > 0 then
                     Result.Data (Used + 1 .. Used + Block.Item.Output_Length) :=
                       Block.Data (1 .. Block.Item.Output_Length);
                  end if;
                  Used := Used + Block.Item.Output_Length;
                  Position := Block.Item.Next_Position;
               end;
            end loop;
            --  Raise 4: original final exact-length mismatch.
            if Used /= Result.Length then
               raise Program_Error with "UTF8 decode extent mismatch";
            end if;
            pragma Assert (Result'Initialized);
         end;
      end return;
   end UTF8;
end UTF8_Coordinator_Proposal;

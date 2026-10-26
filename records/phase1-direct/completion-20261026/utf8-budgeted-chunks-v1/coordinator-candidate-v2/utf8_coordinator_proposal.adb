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
      Saved : Checkpoint_Array := [others => <>];
      --  Only Size writes Saved. Defaults skip Chunk; no input is copied.

      function Prefix_Valid
        (Count : Checkpoint_Count; Position, Length : Natural) return Boolean is
        (Position <= Bytes'Length and then
         (if Count = 0 then Position = 0 and then Length = 0
          else Saved (Count).Item.Next_Position = Position and then
            Saved (Count).After_Output = Length) and then
         (for all I in 1 .. Count =>
            Saved (I).Present and then Saved (I).Item.Valid and then
            Saved (I).Start < Saved (I).Item.Next_Position and then
            Saved (I).Item.Next_Position <= Position and then
            Saved (I).Before_Output <= Saved (I).After_Output and then
            Saved (I).After_Output <= Length and then
            Saved (I).Item.Output_Length =
              Saved (I).After_Output - Saved (I).Before_Output) and then
         (for all I in 1 .. Count =>
            (if I = 1 then Saved (I).Start = 0 and then
               Saved (I).Before_Output = 0
             else Saved (I).Start = Saved (I - 1).Item.Next_Position and then
               Saved (I).Before_Output = Saved (I - 1).After_Output)));
      --  Exact v1 scalar prefix facts; no Chunk or input scan in this checker.

      procedure Size
        (Count : out Checkpoint_Count; Position, Length : out Natural;
         Complete : out Boolean; Failure : out C.Summary)
        with Always_Terminates,
          Post => Prefix_Valid (Count, Position, Length) and then
            (if Complete then Position = Bytes'Length
             else Position < Bytes'Length and then
               Failure = C.Decode_Chunk
                 (Bytes, Position, Quota, Replace_Errors).Item and then
               (not Failure.Valid or else Failure.Next_Position <= Position
                or else Failure.Next_Position > Bytes'Length or else
                Failure.Output_Length > Natural'Last - Length))
      is
      begin
         Count := 0; Position := 0; Length := 0;
         Complete := False; Failure := (0, 0, False);
         if Bytes'Length > 0 then
            pragma Assert ((Bytes'Length - 1) / Quota < C.Checkpoint_Bound);
         end if;
         while Position < Bytes'Length loop
            pragma Loop_Invariant (Prefix_Valid (Count, Position, Length));
            pragma Loop_Invariant
              (if Position < Bytes'Length then Count <= Position / Quota);
            pragma Loop_Variant (Increases => Position);
            pragma Assert (Count < C.Checkpoint_Bound);
            declare
               Block : constant C.Chunk_Result :=
                 C.Decode_Chunk (Bytes, Position, Quota, Replace_Errors);
            begin
               if not Block.Item.Valid or else
                 Block.Item.Next_Position <= Position or else
                 Block.Item.Next_Position > Bytes'Length or else
                 Block.Item.Output_Length > Natural'Last - Length
               then
                  Failure := Block.Item;
                  return;
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
         Complete := True;
      end Size;

      procedure Validate_Replay
        (Actual, Expected : C.Summary; Capacity, Start, Before_Output,
         After_Output, Position, Used, Total : Natural)
        with Always_Terminates,
          Pre => Used <= Total and then Start = Position and then
            Before_Output = Used and then Before_Output <= After_Output and then
            After_Output <= Total and then Expected.Valid and then
            Expected.Next_Position > Start and then
            Expected.Next_Position <= Bytes'Length and then
            Expected.Output_Length = After_Output - Before_Output and then
            Actual = Expected and then Actual.Output_Length <= Capacity,
          Post => Actual.Valid and then Actual.Next_Position > Position and then
            Actual.Next_Position <= Bytes'Length and then
            Actual.Output_Length <= Total - Used and then
            Actual.Output_Length <= Capacity and then Start = Position and then
            Before_Output = Used and then After_Output >= Used and then
            After_Output - Used = Actual.Output_Length
      is
      begin
         --  Raise 1: unchanged source/strict-validation replay mismatch.
         if Actual.Next_Position <= Position or else
           Actual.Next_Position > Bytes'Length or else not Actual.Valid
         then
            raise Program_Error with "UTF8 decode extent mismatch";
         end if;
         --  Raise 2: unchanged public-output/scratch-copy extent mismatch.
         if Actual.Output_Length > Total - Used or else
           Actual.Output_Length > Capacity
         then
            raise Program_Error with "UTF8 decode extent mismatch";
         end if;
         --  Raise 3: unchanged v1 general saved-interval mismatch guard.
         if Start /= Position or else Before_Output /= Used or else
           After_Output < Used or else After_Output - Used /= Actual.Output_Length
         then
            raise Program_Error with "UTF8 decode extent mismatch";
         end if;
      end Validate_Replay;

      procedure Write_Prefix (Block : C.Chunk_Result; Target : out String)
        with Always_Terminates, Relaxed_Initialization => Target,
          Pre => Target'Length = Block.Item.Output_Length and then
            Block.Item.Output_Length <= Block.Capacity,
          Post => Target'Initialized and then
            Target = Block.Data (1 .. Block.Item.Output_Length)
      is
      begin
         Target := Block.Data (1 .. Block.Item.Output_Length);
      end Write_Prefix;

      procedure Render (Count : Checkpoint_Count; Result : out B.Decoded)
        with Always_Terminates, Relaxed_Initialization => Result,
          Pre => Prefix_Valid (Count, Bytes'Length, Result.Length),
          Post => Result'Initialized and then Result.Valid
      is
         Position, Used : Natural := 0;
      begin
         Result.Valid := True;
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
               Validate_Replay
                 (Block.Item, Saved (I).Item, Block.Capacity, Saved (I).Start,
                  Saved (I).Before_Output, Saved (I).After_Output,
                  Position, Used, Result.Length);
               if Block.Item.Output_Length > 0 then
                  Write_Prefix
                    (Block, Result.Data
                       (Used + 1 .. Used + Block.Item.Output_Length));
               end if;
               Used := Used + Block.Item.Output_Length;
               Position := Block.Item.Next_Position;
            end;
         end loop;
         --  Raise 4: unchanged final exact-length mismatch.
         if Used /= Result.Length then
            raise Program_Error with "UTF8 decode extent mismatch";
         end if;
         pragma Assert (Result'Initialized);
      end Render;

      Count : Checkpoint_Count;
      Position, Length : Natural;
      Complete : Boolean;
      Failure : C.Summary;
   begin
      if Bytes'Length = 0 then return (0, True, ""); end if;
      Size (Count, Position, Length, Complete, Failure);
      if not Complete then
         pragma Assert
           (not Failure.Valid or else Failure.Next_Position <= Position or else
            Failure.Next_Position > Bytes'Length or else
            Failure.Output_Length > Natural'Last - Length);
         return (0, False, "");
      end if;
      pragma Assert (Position = Bytes'Length);
      return Result : B.Decoded (Length) with Relaxed_Initialization do
         Render (Count, Result);
      end return;
   end UTF8;
end UTF8_Coordinator_Proposal;

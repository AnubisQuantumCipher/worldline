--  UNCOMPILED / UNPROVED. This tests pure-record congruence through a
--  local checked predicate; it does not establish the UTF8 algorithm.
package body Chunk_Predicate_Probe with SPARK_Mode is
   type Summary is record
      Next_Position, Output_Length : Natural;
   end record;
   type Block_Result is record
      Item : Summary;
      Data : String (1 .. 8);
   end record;
   function Chunk (Input : String; Start : Natural) return Block_Result
     with Global => null, Pre => Start <= Input'Length,
       Post => Chunk'Result.Item.Next_Position >= Start and then
         Chunk'Result.Item.Next_Position <= Input'Length and then
         Chunk'Result.Item.Output_Length <= 8
   is
      Result : Block_Result := ((Start, 0), [others => Character'Val (0)]);
      Steps : Natural := 0;
      Add : Natural;
   begin
      while Result.Item.Next_Position < Input'Length and then Steps < 2 loop
         pragma Loop_Invariant (Steps <= 2);
         pragma Loop_Invariant
           (Result.Item.Next_Position >= Start and then
            Result.Item.Next_Position <= Input'Length);
         pragma Loop_Invariant (Result.Item.Output_Length <= 4 * Steps);
         pragma Loop_Variant (Increases => Steps);
         Add := 1 + Character'Pos
           (Input (Input'First + Result.Item.Next_Position)) mod 4;
         for J in 1 .. Add loop
            Result.Data (Result.Item.Output_Length + J) :=
              Input (Input'First + Result.Item.Next_Position);
         end loop;
         Result.Item.Output_Length := Result.Item.Output_Length + Add;
         Result.Item.Next_Position := Result.Item.Next_Position + 1;
         Steps := Steps + 1;
      end loop;
      return Result;
   end Chunk;

   procedure Replay (Input : String; Output_Length : out Natural) is
      type Checkpoint is record
         Present : Boolean := False;
         Start : Natural := 0;
         Item : Summary := (0, 0);
      end record
        with Dynamic_Predicate =>
          (if Checkpoint.Present then
             Checkpoint.Start < Input'Length and then
             Checkpoint.Item = Chunk (Input, Checkpoint.Start).Item);
      Saved : Checkpoint;
   begin
      Output_Length := 0;
      if Input'Length = 0 then return; end if;
      declare
         First : constant Block_Result := Chunk (Input, 0);
      begin
         Saved := (Present => True, Start => 0, Item => First.Item);
      end;
      declare
         Second : constant Block_Result := Chunk (Input, Saved.Start);
      begin
         pragma Assert (Saved.Present);
         pragma Assert (Second.Item = Saved.Item);
         Output_Length := Second.Item.Output_Length;
      end;
   end Replay;
end Chunk_Predicate_Probe;


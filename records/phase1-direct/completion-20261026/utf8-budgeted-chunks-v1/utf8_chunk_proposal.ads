--  OUTSIDE-PRODUCTION CANDIDATE. UNCOMPILED / UNPROVED / UNRUN.
--  Only the bounded Chunk primitive; no UTF8 coordinator is integrated.
package UTF8_Chunk_Proposal with SPARK_Mode is
   Checkpoint_Bound : constant Positive := 64;
   Minimum_Quota : constant Positive := 4_096;
   Maximum_Quota : constant Natural := Natural'Last / 3 - 3;
   type Summary is record
      Next_Position, Output_Length : Natural;
      Valid : Boolean;
   end record;
   type Chunk_Result (Capacity : Natural) is record
      Item : Summary;
      Data : String (1 .. Capacity);
   end record;

   function Quota_For (Input_Length : Natural) return Positive
     with Global => null,
       Post => Quota_For'Result >= Minimum_Quota and then
         Quota_For'Result <= Maximum_Quota and then
         Quota_For'Result =
           Natural'Max (Minimum_Quota, Input_Length / Checkpoint_Bound +
             (if Input_Length mod Checkpoint_Bound = 0 then 0 else 1));

   function Buffer_Capacity (Remaining : Natural; Quota : Positive)
      return Positive
     with Global => null, Pre => Quota <= Maximum_Quota,
       Post => Buffer_Capacity'Result =
         3 * (Natural'Min (Quota, Remaining) + 3);

   function Decode_Chunk
     (Bytes : String; Start : Natural; Quota : Positive;
      Replace_Errors : Boolean) return Chunk_Result
     with Global => null, Always_Terminates,
       Pre => Start <= Bytes'Length and then Quota <= Maximum_Quota,
       Post => Decode_Chunk'Result.Capacity =
           Buffer_Capacity (Bytes'Length - Start, Quota) and then
         Decode_Chunk'Result.Item.Next_Position >= Start and then
         Decode_Chunk'Result.Item.Next_Position <= Bytes'Length and then
         Decode_Chunk'Result.Item.Next_Position - Start <=
           Natural'Min (Quota, Bytes'Length - Start) + 3 and then
         Decode_Chunk'Result.Item.Output_Length <=
           Decode_Chunk'Result.Capacity and then
         Decode_Chunk'Result.Item.Output_Length <=
           3 * (Decode_Chunk'Result.Item.Next_Position - Start) and then
         (if Replace_Errors then Decode_Chunk'Result.Item.Valid) and then
         (if Decode_Chunk'Result.Item.Valid then
            Decode_Chunk'Result.Item.Next_Position - Start >=
              Natural'Min (Quota, Bytes'Length - Start));
end UTF8_Chunk_Proposal;


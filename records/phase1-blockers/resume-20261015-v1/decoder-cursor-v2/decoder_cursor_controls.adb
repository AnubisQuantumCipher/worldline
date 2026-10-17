with Resource_Quantities;
with Worldline.JSON_Source_Cursor;

-- PROPOSED CONTROLS, NEVER EXECUTED. Assertions must remain enabled.
-- These finite fixtures do not establish arbitrary-size decoder correctness.
procedure Decoder_Cursor_Controls with SPARK_Mode is
   package Q renames Resource_Quantities;
   package C renames Worldline.JSON_Source_Cursor;
   use type Q.Byte_Count;
   use type C.Encoding;
   use type C.Step_Status;
   use type C.Code_Point;

   procedure Check_Start
     (Data : Q.Byte_Array; Item : C.Span; Kind : C.Encoding; Offset : C.Count)
   with Pre => Kind = C.Detected_Encoding (Data, Item) and then
     Offset = C.BOM_Length (Data, Item)
   is
      Current : constant C.Cursor := C.Initial (Data, Item);
   begin
      pragma Assert (Current.Item.First = Item.First, "initial first");
      pragma Assert (Current.Item.Length = Item.Length, "initial length");
      pragma Assert (Current.Kind = Kind, "encoding precedence");
      pragma Assert (Current.Offset = Offset, "BOM start");
   end Check_Start;

   procedure Check_Step
     (Data : Q.Byte_Array; Current : C.Cursor; Status : C.Step_Status;
      Value : C.Code_Point; Next_Offset : C.Count)
   with Pre => C.Reference_Read (Data, Current).Status = Status and then
     C.Reference_Read (Data, Current).Value = Value and then
     C.Reference_Read (Data, Current).Next_Offset = Next_Offset
   is
      Result : constant C.Step := C.Read (Data, Current);
   begin
      pragma Assert (Result.Status = Status, "step status");
      pragma Assert (Result.Start = Current.Offset, "step original offset");
      pragma Assert (Result.Value = Value, "decoded value");
      pragma Assert (Result.Next_Offset = Next_Offset, "step next offset");
   end Check_Step;

   procedure Check_One
     (Data : Q.Byte_Array; Item : C.Span; Kind : C.Encoding;
      BOM : C.Count; Value : C.Code_Point)
   with Pre => Kind = C.Detected_Encoding (Data, Item) and then
     BOM = C.BOM_Length (Data, Item) and then
     C.Reference_Read (Data, (Item, Kind, BOM)).Status = C.Decoded and then
     C.Reference_Read (Data, (Item, Kind, BOM)).Value = Value and then
     C.Reference_Read (Data, (Item, Kind, BOM)).Next_Offset = Item.Length
   is
      Current : constant C.Cursor := C.Initial (Data, Item);
   begin
      Check_Start (Data, Item, Kind, BOM);
      Check_Step (Data, Current, C.Decoded, Value, Item.Length);
      Check_Step (Data, (Item, Kind, Item.Length), C.End_Of_Text, 0, Item.Length);
   end Check_One;

   Empty : constant Q.Byte_Array (1 .. 0) := [others => 0];
   ASCII : constant Q.Byte_Array := [16#41#];
   Two_Byte : constant Q.Byte_Array := [16#C2#, 16#A2#];
   Three_Byte : constant Q.Byte_Array := [16#E2#, 16#82#, 16#AC#];
   Surrogate_UTF8 : constant Q.Byte_Array := [16#ED#, 16#A0#, 16#80#];
   Last_UTF8 : constant Q.Byte_Array := [16#F4#, 16#8F#, 16#BF#, 16#BF#];
   Sig_UTF8 : constant Q.Byte_Array := [16#EF#, 16#BB#, 16#BF#, 16#41#];
   Sig_16_BE : constant Q.Byte_Array := [16#FE#, 16#FF#, 0, 16#41#];
   Sig_16_LE : constant Q.Byte_Array := [16#FF#, 16#FE#, 16#41#, 0];
   Sig_32_BE : constant Q.Byte_Array := [0, 0, 16#FE#, 16#FF#, 0, 0, 0, 16#41#];
   Sig_32_LE : constant Q.Byte_Array := [16#FF#, 16#FE#, 0, 0, 16#41#, 0, 0, 0];
   Bare_16_BE : constant Q.Byte_Array := [0, 16#41#];
   Bare_16_LE : constant Q.Byte_Array := [16#41#, 0];
   Bare_32_BE : constant Q.Byte_Array := [0, 0, 0, 16#41#];
   Bare_32_LE : constant Q.Byte_Array := [16#41#, 0, 0, 0];
   Pair_BE : constant Q.Byte_Array := [16#FE#, 16#FF#, 16#D8#, 0, 16#DC#, 0];
   Pair_LE : constant Q.Byte_Array := [16#FF#, 16#FE#, 0, 16#D8#, 0, 16#DC#];
   Pair_Last : constant Q.Byte_Array := [16#FE#, 16#FF#, 16#DB#, 16#FF#, 16#DF#, 16#FF#];
   Lone_High : constant Q.Byte_Array := [16#FE#, 16#FF#, 16#D8#, 0];
   Lone_Low : constant Q.Byte_Array := [16#FF#, 16#FE#, 0, 16#DC#];
   High_Then_ASCII : constant Q.Byte_Array := [16#FE#, 16#FF#, 16#D8#, 0, 0, 16#41#];
   Odd_After_High : constant Q.Byte_Array := [16#FE#, 16#FF#, 16#D8#, 0, 0];
   Surrogate_32_BE : constant Q.Byte_Array := [0, 0, 16#FE#, 16#FF#, 0, 0, 16#D8#, 0];
   Surrogate_32_LE : constant Q.Byte_Array := [16#FF#, 16#FE#, 0, 0, 0, 16#D8#, 0, 0];
   Last_32_BE : constant Q.Byte_Array := [0, 0, 16#FE#, 16#FF#, 0, 16#10#, 16#FF#, 16#FF#];
   Last_32_LE : constant Q.Byte_Array := [16#FF#, 16#FE#, 0, 0, 16#FF#, 16#FF#, 16#10#, 0];
   Too_Large_32 : constant Q.Byte_Array := [0, 0, 16#FE#, 16#FF#, 0, 16#11#, 0, 0];
   All_Ones_32 : constant Q.Byte_Array := [16#FF#, 16#FE#, 0, 0, 16#FF#, 16#FF#, 16#FF#, 16#FF#];
   Odd_16 : constant Q.Byte_Array := [16#FE#, 16#FF#, 0];
   Short_32 : constant Q.Byte_Array := [0, 0, 16#FE#, 16#FF#, 0, 0, 0];
   Short_UTF8 : constant Q.Byte_Array := [16#E2#, 16#82#];
   Overlong_UTF8 : constant Q.Byte_Array := [16#C0#, 16#80#];
   Bad_Tail : constant Q.Byte_Array := [16#C2#, 16#41#];
   Too_Large_UTF8 : constant Q.Byte_Array := [16#F4#, 16#90#, 16#80#, 16#80#];
   Continuation : constant Q.Byte_Array := [16#80#];
   BOM_Only_UTF8 : constant Q.Byte_Array := [16#EF#, 16#BB#, 16#BF#];
   BOM_Only_16 : constant Q.Byte_Array := [16#FE#, 16#FF#];
   BOM_Only_32 : constant Q.Byte_Array := [16#FF#, 16#FE#, 0, 0];
   Double_BOM : constant Q.Byte_Array := [16#EF#, 16#BB#, 16#BF#, 16#EF#, 16#BB#, 16#BF#];
   Three_NUL_ASCII : constant Q.Byte_Array := [0, 16#41#, 16#42#];
   Four_BE : constant Q.Byte_Array := [0, 16#41#, 0, 16#42#];
   Four_LE : constant Q.Byte_Array := [16#41#, 0, 16#42#, 0];
   Unaligned_16 : constant Q.Byte_Array := [0, 0, 0];
   Unaligned_32 : constant Q.Byte_Array := [0, 0, 0, 0, 0];
   Offset_Data : constant Q.Byte_Array (7 .. 10) := [16#FF#, 0, 16#41#, 16#FF#];
   Last_Byte : constant Q.Byte_Array (Q.Byte_Count'Last .. Q.Byte_Count'Last) :=
     [others => 16#41#];
   Last_Pair : constant Q.Byte_Array (Q.Byte_Count'Last - 1 .. Q.Byte_Count'Last) :=
     [Q.Byte_Count'Last - 1 => 0, Q.Byte_Count'Last => 16#41#];
begin
   -- Accepted encodings, including BOM-less heuristics and exact BOM priority.
   Check_One (ASCII, (1, ASCII'Length), C.UTF8, 0, Character'Pos ('A'));
   Check_One (Two_Byte, (1, Two_Byte'Length), C.UTF8, 0, 162);
   Check_One (Three_Byte, (1, Three_Byte'Length), C.UTF8, 0, 8364);
   Check_One (Surrogate_UTF8, (1, Surrogate_UTF8'Length), C.UTF8, 0, 55296);
   Check_One (Last_UTF8, (1, Last_UTF8'Length), C.UTF8, 0, 1114111);
   Check_One (Sig_UTF8, (1, Sig_UTF8'Length), C.UTF8, 3, Character'Pos ('A'));
   Check_One (Sig_16_BE, (1, Sig_16_BE'Length), C.UTF16_BE, 2, Character'Pos ('A'));
   Check_One (Sig_16_LE, (1, Sig_16_LE'Length), C.UTF16_LE, 2, Character'Pos ('A'));
   Check_One (Sig_32_BE, (1, Sig_32_BE'Length), C.UTF32_BE, 4, Character'Pos ('A'));
   Check_One (Sig_32_LE, (1, Sig_32_LE'Length), C.UTF32_LE, 4, Character'Pos ('A'));
   Check_One (Bare_16_BE, (1, Bare_16_BE'Length), C.UTF16_BE, 0, Character'Pos ('A'));
   Check_One (Bare_16_LE, (1, Bare_16_LE'Length), C.UTF16_LE, 0, Character'Pos ('A'));
   Check_One (Bare_32_BE, (1, Bare_32_BE'Length), C.UTF32_BE, 0, Character'Pos ('A'));
   Check_One (Bare_32_LE, (1, Bare_32_LE'Length), C.UTF32_LE, 0, Character'Pos ('A'));
   Check_Start (Four_BE, (1, Four_BE'Length), C.UTF16_BE, 0);
   Check_Start (Four_LE, (1, Four_LE'Length), C.UTF16_LE, 0);
   -- Length three intentionally takes no BOM-less UTF16/32 heuristic.
   Check_Start (Three_NUL_ASCII, (1, Three_NUL_ASCII'Length), C.UTF8, 0);
   Check_Step (Three_NUL_ASCII, ((1, Three_NUL_ASCII'Length), C.UTF8, 0), C.Decoded, 0, 1);

   -- Surrogatepass is retained for UTF8/16/32, with exact pair/lookahead rules.
   Check_One (Pair_BE, (1, Pair_BE'Length), C.UTF16_BE, 2, 65536);
   Check_One (Pair_LE, (1, Pair_LE'Length), C.UTF16_LE, 2, 65536);
   Check_One (Pair_Last, (1, Pair_Last'Length), C.UTF16_BE, 2, 1114111);
   Check_One (Lone_High, (1, Lone_High'Length), C.UTF16_BE, 2, 16#D800#);
   Check_One (Lone_Low, (1, Lone_Low'Length), C.UTF16_LE, 2, 16#DC00#);
   Check_Step (High_Then_ASCII, C.Initial (High_Then_ASCII, (1, High_Then_ASCII'Length)), C.Decoded, 16#D800#, 4);
   Check_Step (High_Then_ASCII, ((1, High_Then_ASCII'Length), C.UTF16_BE, 4), C.Decoded, Character'Pos ('A'), 6);
   Check_Step (Odd_After_High, C.Initial (Odd_After_High, (1, Odd_After_High'Length)), C.Decoded, 16#D800#, 4);
   Check_Step (Odd_After_High, ((1, Odd_After_High'Length), C.UTF16_BE, 4), C.Invalid_Sequence, 0, 4);
   Check_One (Surrogate_32_BE, (1, Surrogate_32_BE'Length), C.UTF32_BE, 4, 16#D800#);
   Check_One (Surrogate_32_LE, (1, Surrogate_32_LE'Length), C.UTF32_LE, 4, 16#D800#);
   Check_One (Last_32_BE, (1, Last_32_BE'Length), C.UTF32_BE, 4, 1114111);
   Check_One (Last_32_LE, (1, Last_32_LE'Length), C.UTF32_LE, 4, 1114111);

   -- Invalid/truncated encodings are not EOF and do not move the cursor.
   Check_Step (Too_Large_32, C.Initial (Too_Large_32, (1, Too_Large_32'Length)), C.Invalid_Sequence, 0, 4);
   Check_Step (All_Ones_32, C.Initial (All_Ones_32, (1, All_Ones_32'Length)), C.Invalid_Sequence, 0, 4);
   Check_Step (Odd_16, C.Initial (Odd_16, (1, Odd_16'Length)), C.Invalid_Sequence, 0, 2);
   Check_Step (Short_32, C.Initial (Short_32, (1, Short_32'Length)), C.Invalid_Sequence, 0, 4);
   Check_Step (Short_UTF8, C.Initial (Short_UTF8, (1, Short_UTF8'Length)), C.Invalid_Sequence, 0, 0);
   Check_Step (Overlong_UTF8, C.Initial (Overlong_UTF8, (1, Overlong_UTF8'Length)), C.Invalid_Sequence, 0, 0);
   Check_Step (Bad_Tail, C.Initial (Bad_Tail, (1, Bad_Tail'Length)), C.Invalid_Sequence, 0, 0);
   Check_Step (Too_Large_UTF8, C.Initial (Too_Large_UTF8, (1, Too_Large_UTF8'Length)), C.Invalid_Sequence, 0, 0);
   Check_Step (Continuation, C.Initial (Continuation, (1, Continuation'Length)), C.Invalid_Sequence, 0, 0);

   -- Empty and BOM-only inputs decode to an empty scalar sequence. This
   -- does not call them valid JSON. A second BOM is content, not stripped.
   Check_Start (Empty, (Q.Byte_Count'Last, 0), C.UTF8, 0);
   Check_Step (Empty, C.Initial (Empty, (Q.Byte_Count'Last, 0)), C.End_Of_Text, 0, 0);
   Check_Step (BOM_Only_UTF8, C.Initial (BOM_Only_UTF8, (1, BOM_Only_UTF8'Length)), C.End_Of_Text, 0, 3);
   Check_Step (BOM_Only_16, C.Initial (BOM_Only_16, (1, BOM_Only_16'Length)), C.End_Of_Text, 0, 2);
   Check_Start (BOM_Only_32, (1, BOM_Only_32'Length), C.UTF32_LE, 4);
   Check_Step (BOM_Only_32, C.Initial (BOM_Only_32, (1, BOM_Only_32'Length)), C.End_Of_Text, 0, 4);
   Check_One (Double_BOM, (1, Double_BOM'Length), C.UTF8, 3, 16#FEFF#);

   -- Span-relative indexing, arbitrary lower bounds, finite endpoint-index
   -- fixtures, and invalid huge extents. None allocates a huge input.
   Check_One (Offset_Data, (8, 2), C.UTF16_BE, 0, Character'Pos ('A'));
   -- Read has no BOM-start lower bound or unit-alignment precondition.
   Check_Step (Sig_16_BE, ((1, Sig_16_BE'Length), C.UTF16_BE, 0), C.Decoded, 16#FEFF#, 2);
   Check_Step (Unaligned_16, ((1, Unaligned_16'Length), C.UTF16_LE, 1), C.Decoded, 0, Unaligned_16'Length);
   Check_Step (Unaligned_32, ((1, Unaligned_32'Length), C.UTF32_BE, 1), C.Decoded, 0, Unaligned_32'Length);
   Check_Step (Two_Byte, ((1, Two_Byte'Length), C.UTF8, 1), C.Invalid_Sequence, 0, 1);
   Check_One (Last_Byte, (Q.Byte_Count'Last, 1), C.UTF8, 0, Character'Pos ('A'));
   Check_One (Last_Pair, (Q.Byte_Count'Last - 1, 2), C.UTF16_BE, 0, Character'Pos ('A'));
   Check_Step (ASCII, ((2, 1), C.UTF8, 0), C.Invalid_Position, 0, 0);
   Check_Start (ASCII, (2, 1), C.UTF8, 0);
   Check_Step (ASCII, C.Initial (ASCII, (2, 1)), C.Invalid_Position, 0, 0);
   Check_Step (ASCII, ((1, 2), C.UTF8, 0), C.Invalid_Position, 0, 0);
   Check_Step (ASCII, ((1, ASCII'Length), C.UTF8, Q.Byte_Count'Last), C.Invalid_Position, 0, Q.Byte_Count'Last);
   Check_Step (Empty, ((1, Q.Byte_Count'Last), C.UTF32_BE, 0), C.Invalid_Position, 0, 0);
   Check_Step (Empty, ((1, 0), C.UTF8, 1), C.Invalid_Position, 0, 1);
end Decoder_Cursor_Controls;

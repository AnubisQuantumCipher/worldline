with Ada.Text_IO;
with Worldline.Lifetime_Values;

--  Owned-array endpoint controls of the original native value grammar.
procedure Lifetime_Value_Tests is
   package V renames Worldline.Lifetime_Values;
   use type V.Value_Kind;
   High : constant String (Positive'Last .. Positive'Last) := [Character'Val (0)];
   Parsed : constant V.Node := V.Parse (High, 1, 1);
   Zero : constant Character := Character'Val (0);
   function Header (Tag, Extent : Natural) return String is
     (Character'Val (Tag) & Character'Val (Extent) & String'(1 .. 7 => Zero));

   procedure Check_Grammar is
      Empty_Bytes : constant String (Positive'Last - 8 .. Positive'Last) := Header (5, 0);
      Empty_Node : constant V.Node := V.Parse (Empty_Bytes, 1, 9);
      Nested : constant String := Header (6, 1) & Header (6, 1) & Zero;
      Root : constant V.Node := V.Parse (Nested, 1, Nested'Length);
      Child : constant V.Node := V.Element (Nested, Root, 1);
      Letter : constant String := Header (4, 4) & 'A' & Zero & Zero & Zero;
      Int_128 : constant String := Header (3, 2) & Character'Val (128) & Zero;
      Bad_Int : constant String := Header (3, 2) & Zero & Zero;
      Bad_Text : constant String := Header (4, 4) & String'(1 .. 4 => Character'Val (255));
   begin
      pragma Assert (Empty_Node.Kind = V.Bytes_Value);
      pragma Assert (V.Bytes (Empty_Bytes, Empty_Node) = "");
      pragma Assert (Root.Kind = V.Tuple_Value and then Root.Count = 1);
      pragma Assert (Child.Kind = V.Tuple_Value and then Child.Count = 1);
      pragma Assert (V.Element (Nested, Child, 1).Kind = V.Null_Value);
      pragma Assert (V.Element (Nested, Root, 2).Kind = V.Invalid);
      pragma Assert (V.Complete (Nested, Root) and then V.Equal (Nested, Root, Root));
      pragma Assert (V.Text (Letter, V.Parse (Letter, 1, Letter'Length)) = "A");
      pragma Assert (V.Matches (Int_128, V.Parse (Int_128, 1, Int_128'Length), 128));
      pragma Assert (V.Parse (Bad_Int, 1, Bad_Int'Length).Kind = V.Invalid);
      pragma Assert (V.Parse (Bad_Text, 1, Bad_Text'Length).Kind = V.Invalid);
      pragma Assert (V.Parse (Nested, 1, Nested'Length - 1).Kind = V.Invalid);
   end Check_Grammar;
   procedure Check_Payload_Bounds is
      Empty_Text : constant String (Positive'Last - 8 .. Positive'Last) := Header (4, 0);
      High_Bytes : constant String (Positive'Last - 9 .. Positive'Last) := Header (5, 1) & 'x';
      Bad : constant V.Node := (V.Integer_Value, Natural'Last, 0, 0);
      Bad_Tuple : constant V.Node := (V.Tuple_Value, Natural'Last, 0, 1);
   begin
      pragma Assert (V.Text (Empty_Text, V.Parse (Empty_Text, 1, 9)) = "");
      pragma Assert (V.Bytes (High_Bytes, V.Parse (High_Bytes, 1, 10)) = "x");
      pragma Assert (V.Bytes (High, Bad) = "" and then V.Text (High, Bad) = "");
      pragma Assert (not V.Nonnegative (High, Bad));
      pragma Assert (not V.Positive_Integer (High, Bad));
      pragma Assert (not V.Matches (High, Bad, 0));
      pragma Assert (V.Mod_256 (High, Bad) = 256);
      pragma Assert (not V.Complete (High, Bad_Tuple));
      pragma Assert (not V.Equal (High, Bad_Tuple, Bad_Tuple));
   end Check_Payload_Bounds;
begin
   pragma Assert (Parsed.Kind = V.Null_Value);
   pragma Assert (Parsed.First = 1 and then Parsed.Last = 1);
   pragma Assert (V.Complete (High, Parsed));
   pragma Assert (V.Equal (High, Parsed, Parsed));
   Check_Grammar;
   Check_Payload_Bounds;
   Ada.Text_IO.Put_Line ("PASS lifetime value endpoint and grammar controls");
end Lifetime_Value_Tests;

package body Worldline.Lifetime_Values with SPARK_Mode is
   use type U64;
   function Byte_At (Data : String; Index : Natural) return Natural is
     (Character'Pos (Data (Data'First + Index - 1)));
   function Word (Data : String; First : Natural; Width : Positive) return U64 is
      Value : U64 := 0;
   begin
      for I in reverse 0 .. Width - 1 loop Value := Value * 256 + U64 (Byte_At (Data, First + I)); end loop;
      return Value;
   end Word;
   function Read (Data : String; First, Limit : Natural) return Node is
      Cursor : Natural := First;
      Tag : Natural;
      Extent : U64;
      Form : Value_Kind;
   begin
      if First = 0 or else First > Limit or else Limit > Data'Length then return No_Node; end if;
      Tag := Byte_At (Data, Cursor);
      case Tag is
         when 0 => return (Null_Value, First, First, 0);
         when 1 => return (False_Value, First, First, 0);
         when 2 => return (True_Value, First, First, 0);
         when 3 => Form := Integer_Value;
         when 4 => Form := Text_Value;
         when 5 => Form := Bytes_Value;
         when 6 => Form := Tuple_Value;
         when 7 => Form := Unavailable_Value;
         when others => return No_Node;
      end case;
      if Limit - Cursor < 8 then return No_Node; end if;
      Extent := Word (Data, Cursor + 1, 8);
      Cursor := Cursor + 9;
      if Extent > U64 (Limit - Cursor + 1) then return No_Node; end if;
      if Form = Tuple_Value then
         for I in 1 .. Natural (Extent) loop
            declare Child : constant Node := Read (Data, Cursor, Limit);
            begin
               if Child.Kind = Invalid then return No_Node; end if;
               Cursor := Child.Last + 1;
            end;
         end loop;
         return (Form, First, Cursor - 1, Natural (Extent));
      end if;
      if Form = Integer_Value then
         if Extent = 0 then return No_Node; end if;
         if Extent > 1 and then
           ((Byte_At (Data, Cursor + Natural (Extent) - 1) = 0 and then Byte_At (Data, Cursor + Natural (Extent) - 2) < 128) or else
            (Byte_At (Data, Cursor + Natural (Extent) - 1) = 255 and then Byte_At (Data, Cursor + Natural (Extent) - 2) >= 128)) then return No_Node; end if;
      elsif Form = Text_Value then
         if Extent mod 4 /= 0 then return No_Node; end if;
         for I in 0 .. Natural (Extent) / 4 - 1 loop
            if Word (Data, Cursor + I * 4, 4) > 16#10FFFF# then return No_Node; end if;
         end loop;
      end if;
      return (Form, First, Cursor + Natural (Extent) - 1, 0);
   end Read;
   function Parse (Data : String; First, Last : Natural) return Node is
      Result : constant Node := Read (Data, First, Last);
   begin return (if Result.Last = Last then Result else No_Node); end Parse;
   function Element (Data : String; Parent : Node; Index : Positive) return Node is
      Cursor : Natural := Parent.First + 9;
      Child : Node;
   begin
      if Parent.Kind /= Tuple_Value or else Index > Parent.Count then return No_Node; end if;
      for I in 1 .. Index loop
         Child := Read (Data, Cursor, Parent.Last);
         if Child.Kind = Invalid then return No_Node; end if;
         Cursor := Child.Last + 1;
      end loop;
      return Child;
   end Element;
   function Bytes (Data : String; Item : Node) return String is
   begin
      if Item.Kind not in Bytes_Value | Text_Value | Integer_Value | Unavailable_Value or else
        Item.First = 0 or else Item.Last > Data'Length or else Item.Last < Item.First + 8 then return ""; end if;
      return Data (Data'First + Item.First + 8 .. Data'First + Item.Last - 1);
   end Bytes;
   function Text (Data : String; Item : Node) return String is
      Output : String (1 .. (if Item.Last >= Item.First + 8 then Item.Last - Item.First - 8 else 0));
      Used : Natural := 0;
      procedure Emit (Value : Natural) is
      begin Used := Used + 1; Output (Used) := Character'Val (Value); end Emit;
   begin
      if Item.Kind /= Text_Value or else Item.First = 0 or else Item.Last > Data'Length then return ""; end if;
      for I in 0 .. Output'Length / 4 - 1 loop
         declare Code : constant Natural := Natural (Word (Data, Item.First + 9 + I * 4, 4));
         begin
            if Code < 128 then Emit (Code);
            elsif Code < 2048 then Emit (192 + Code / 64); Emit (128 + Code mod 64);
            elsif Code < 65536 then Emit (224 + Code / 4096); Emit (128 + (Code / 64) mod 64); Emit (128 + Code mod 64);
            else Emit (240 + Code / 262144); Emit (128 + (Code / 4096) mod 64); Emit (128 + (Code / 64) mod 64); Emit (128 + Code mod 64);
            end if;
         end;
      end loop;
      return Output (1 .. Used);
   end Text;
   function Nonnegative (Data : String; Item : Node) return Boolean is
     (Item.Kind = Integer_Value and then Item.Last > Item.First + 8 and then Byte_At (Data, Item.Last) < 128);
   function Positive_Integer (Data : String; Item : Node) return Boolean is
     (Nonnegative (Data, Item) and then (Item.Last > Item.First + 9 or else Byte_At (Data, Item.Last) /= 0));
   function Compare (Data : String; L, R : Node) return Integer is
      LP : constant Boolean := Nonnegative (Data, L);
      RP : constant Boolean := Nonnegative (Data, R);
   begin
      if L.Kind /= Integer_Value or else R.Kind /= Integer_Value then return 0; end if;
      if LP /= RP then return (if LP then 1 else -1); end if;
      if L.Last - L.First /= R.Last - R.First then
         return (if (L.Last - L.First > R.Last - R.First) = LP then 1 else -1);
      end if;
      for I in 0 .. L.Last - L.First - 9 loop
         if Byte_At (Data, L.Last - I) /= Byte_At (Data, R.Last - I) then
            return (if Byte_At (Data, L.Last - I) > Byte_At (Data, R.Last - I) then 1 else -1);
         end if;
      end loop;
      return 0;
   end Compare;
   function Equal (Data : String; L, R : Node) return Boolean is
   begin
      if L.Kind /= R.Kind or else L.Kind = Invalid then return False; end if;
      if L.Kind = Tuple_Value then
         if L.Count /= R.Count then return False; end if;
         for I in 1 .. L.Count loop if not Equal (Data, Element (Data, L, I), Element (Data, R, I)) then return False; end if; end loop;
         return True;
      end if;
      return Bytes (Data, L) = Bytes (Data, R);
   end Equal;
   function Matches (Data : String; Item : Node; Value : U64) return Boolean is
      Remaining : U64 := Value;
   begin
      if not Nonnegative (Data, Item) then return False; end if;
      for I in Item.First + 9 .. Item.Last loop
         if Byte_At (Data, I) /= Natural (Remaining mod 256) then return False; end if;
         Remaining := Remaining / 256;
      end loop;
      return Remaining = 0;
   end Matches;
   function Mod_256 (Data : String; Item : Node) return Natural is
     (if Item.Kind = Integer_Value then Byte_At (Data, Item.First + 9) else 256);
   function Complete (Data : String; Item : Node) return Boolean is
   begin
      if Item.Kind in Invalid | Unavailable_Value then return False; end if;
      if Item.Kind = Tuple_Value then
         for I in 1 .. Item.Count loop if not Complete (Data, Element (Data, Item, I)) then return False; end if; end loop;
      end if;
      return True;
   end Complete;
end Worldline.Lifetime_Values;

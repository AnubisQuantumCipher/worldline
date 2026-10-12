with Evaluation_Pending;
with Exact_Decimal;
with Decimal_Binary64;
with Worldline.Producer_Render;
package body Worldline.Producer_Values with SPARK_Mode is
   function Byte_At (Data : String; Offset : Natural) return Character is
     (if Offset < Data'Length then Data (Data'First + Offset) else Character'Val (0));
   function UTF8_Width (Data : String; Offset : Natural) return Natural is
      B : Natural;
      function Tail (K : Natural) return Boolean is
        (Offset < Data'Length - K and then Character'Pos (Byte_At (Data,Offset + K)) in 128 .. 191);
   begin
      if Offset >= Data'Length then return 0; end if;
      B := Character'Pos (Byte_At (Data,Offset));
      if B < 128 then return 1;
      elsif B in 16#C2# .. 16#DF# and then Data'Length - Offset >= 2 and then Tail (1) then return 2;
      elsif B in 16#E0# .. 16#EF# and then Data'Length - Offset >= 3
        and then Tail (1) and then Tail (2)
        and then (B /= 16#E0# or else Character'Pos (Byte_At (Data,Offset + 1)) >= 16#A0#) then return 3;
      elsif B in 16#F0# .. 16#F4# and then Data'Length - Offset >= 4
        and then Tail (1) and then Tail (2) and then Tail (3)
        and then (B /= 16#F0# or else Character'Pos (Byte_At (Data,Offset + 1)) >= 16#90#)
        and then (B /= 16#F4# or else Character'Pos (Byte_At (Data,Offset + 1)) < 16#90#) then return 4;
      else return 0;
      end if;
   end UTF8_Width;

   procedure Space (Data : String; Position : in out Natural) is
   begin
      while Position < Data'Length and then
        Byte_At (Data, Position) in ' ' | Character'Val (9) | Character'Val (10) | Character'Val (13)
      loop
         pragma Loop_Invariant (Position >= Position'Loop_Entry);
         pragma Loop_Variant (Increases => Position);
         Position := Position + 1;
      end loop;
   end Space;

   function Hex (C : Character) return Integer is
     (if C in '0' .. '9' then Character'Pos (C) - Character'Pos ('0')
      elsif C in 'a' .. 'f' then Character'Pos (C) - Character'Pos ('a') + 10
      elsif C in 'A' .. 'F' then Character'Pos (C) - Character'Pos ('A') + 10
      else -1);

   function Raw (Data : String; Item : Node) return String is
     (if Item.Form /= Missing and then Item.First > 0 and then
         Item.First <= Item.Last and then Item.Last <= Data'Length
      then Data (Data'First + (Item.First - 1) .. Data'First + (Item.Last - 1))
      else "");

   procedure Scan (Data : String; Position : in out Natural; Item : out Node)
     with Always_Terminates,
       Subprogram_Variant => (Decreases => Data'Length - Natural'Min (Position,Data'Length)),
       Post => Position >= Position'Old and then
         (if Item.Form /= Missing then Position > Position'Old and then
            Item.First > Position'Old and then Item.First <= Data'Length and then Item.Last = Position);

   procedure Scan_String (Data : String; Position : in out Natural; Valid : out Boolean) is
      Width : Natural;
   begin
      Valid := False;
      if Byte_At (Data, Position) /= '"' then return; end if;
      Position := Position + 1;
      while Position < Data'Length loop
         pragma Loop_Invariant (Position >= Position'Loop_Entry);
         pragma Loop_Variant (Increases => Position);
         if Byte_At (Data, Position) = '"' then
            Position := Position + 1;
            Valid := True;
            return;
         elsif Character'Pos (Byte_At (Data, Position)) < 32 then return;
         elsif Byte_At (Data, Position) = '\' then
            Position := Position + 1;
            if Position >= Data'Length then return; end if;
            if Byte_At (Data, Position) = 'u' then
               if Data'Length - Position < 5 then return; end if;
               for I in 1 .. 4 loop
                  if Hex (Byte_At (Data, Position + I)) < 0 then return; end if;
               end loop;
               Position := Position + 5;
            elsif Byte_At (Data, Position) in '"' | '\' | '/' | 'b' | 'f' | 'n' | 'r' | 't' then
               Position := Position + 1;
            else return;
            end if;
         else
            Width := UTF8_Width (Data,Position);
            if Width = 0 then return; end if;
            Position := Position + Width;
         end if;
      end loop;
   end Scan_String;

   procedure Scan (Data : String; Position : in out Natural; Item : out Node) is
      Start : Natural;
      Form : Value_Kind;
      Valid : Boolean;
      Child, Key : Node;
      Open, Close : Character;
   begin
      Item := No_Node;
      Space (Data, Position);
      if Position >= Data'Length then return; end if;
      Start := Position;
      for Choice in 1 .. 3 loop
         pragma Loop_Invariant (Position = Start);
         declare Token : constant String :=
           (if Choice = 1 then "NaN" elsif Choice = 2 then "Infinity" else "-Infinity");
         begin
            if Token'Length <= Data'Length - Position and then
              Data (Data'First + Position .. Data'First + Position + (Token'Length - 1)) = Token
            then
               Position := Position + Token'Length;
               Item := (Number_Value,Start + 1,Position); return;
            end if;
         end;
      end loop;
      case Byte_At (Data, Position) is
         when '"' =>
            Scan_String (Data, Position, Valid);
            if not Valid then return; end if;
            Form := String_Value;
         when '{' | '[' =>
            Open := Byte_At (Data, Position);
            Close := (if Open = '{' then '}' else ']');
            Form := (if Open = '{' then Object_Value else Array_Value);
            Position := Position + 1;
            Space (Data, Position);
            if Byte_At (Data, Position) /= Close then
               loop
                  pragma Loop_Invariant (Position > Start);
                  pragma Loop_Variant (Increases => Position);
                  if Open = '{' then
                     Scan (Data, Position, Key);
                     if Key.Form /= String_Value then return; end if;
                     Space (Data, Position);
                     if Byte_At (Data, Position) /= ':' then return; end if;
                     Position := Position + 1;
                  end if;
                  Scan (Data, Position, Child);
                  if Child.Form = Missing then return; end if;
                  Space (Data, Position);
                  exit when Byte_At (Data, Position) = Close;
                  if Byte_At (Data, Position) /= ',' then return; end if;
                  Position := Position + 1;
                  Space (Data, Position);
               end loop;
            end if;
            if Position >= Data'Length or else Byte_At (Data, Position) /= Close then return; end if;
            Position := Position + 1;
         when 'n' | 't' | 'f' =>
            declare
               Literal : constant String :=
                 (if Byte_At (Data, Position) = 'n' then "null"
                  elsif Byte_At (Data, Position) = 't' then "true" else "false");
            begin
               if Data'Length - Position < Literal'Length then return; end if;
               for I in Literal'Range loop
                  if Byte_At (Data, Position + I - Literal'First) /= Literal (I) then return; end if;
               end loop;
               Position := Position + Literal'Length;
               Form := (if Literal = "null" then Null_Value else Boolean_Value);
            end;
         when '-' | '0' .. '9' =>
            Form := Integer_Value;
            if Byte_At (Data, Position) = '-' then
               Position := Position + 1;
               if Position >= Data'Length then return; end if;
            end if;
            if Byte_At (Data, Position) = '0' then Position := Position + 1;
            elsif Byte_At (Data, Position) in '1' .. '9' then
               while Position < Data'Length and then Byte_At (Data, Position) in '0' .. '9' loop
                  pragma Loop_Invariant (Position >= Position'Loop_Entry);
                  pragma Loop_Variant (Increases => Position);
                  Position := Position + 1;
               end loop;
            else return;
            end if;
            if Byte_At (Data, Position) = '.' then
               Form := Number_Value;
               Position := Position + 1;
               if Position >= Data'Length or else Byte_At (Data, Position) not in '0' .. '9' then return; end if;
               while Position < Data'Length and then Byte_At (Data, Position) in '0' .. '9' loop
                  pragma Loop_Invariant (Position >= Position'Loop_Entry);
                  pragma Loop_Variant (Increases => Position);
                  Position := Position + 1;
               end loop;
            end if;
            if Byte_At (Data, Position) in 'e' | 'E' then
               Form := Number_Value;
               Position := Position + 1;
               if Byte_At (Data, Position) in '+' | '-' then Position := Position + 1; end if;
               if Position >= Data'Length or else Byte_At (Data, Position) not in '0' .. '9' then return; end if;
               while Position < Data'Length and then Byte_At (Data, Position) in '0' .. '9' loop
                  pragma Loop_Invariant (Position >= Position'Loop_Entry);
                  pragma Loop_Variant (Increases => Position);
                  Position := Position + 1;
               end loop;
            end if;
         when others => return;
      end case;
      if Position > Start then Item := (Form, Start + 1, Position); end if;
   end Scan;

   function Parse (Data : String) return Node is
      Position : Natural := 0;
      Item : Node;
   begin
      Scan (Data, Position, Item);
      Space (Data, Position);
      if Position = Data'Length then
         return Item;
      else
         return No_Node;
      end if;
   end Parse;

   function First_Key (Data : String; Parent, Key : Node) return Boolean is
      Position : Natural := Parent.First;
      Prior, Item : Node;
   begin
      Space (Data, Position);
      while Position < Key.First - 1 loop
         pragma Loop_Variant (Increases => Position);
         Scan (Data, Position, Prior);
         if Prior.Form /= String_Value then return False; end if;
         if Text (Data, Prior) = Text (Data, Key) then return False; end if;
         Space (Data, Position);
         if Byte_At (Data, Position) /= ':' then return False; end if;
         Position := Position + 1;
         Scan (Data, Position, Item);
         if Item.Form = Missing then return False; end if;
         Space (Data, Position);
         if Byte_At (Data, Position) = ',' then Position := Position + 1; end if;
         Space (Data, Position);
      end loop;
      return True;
   end First_Key;
   function Tree_Admitted
     (Data : String; Parent : Node; Unique_Keys, Standard_Constants : Boolean)
      return Boolean
     with Subprogram_Variant => (Decreases =>
            (if Parent.Form = Missing then 0
             else Long_Long_Integer (Data'Length) + 1 - Long_Long_Integer (Natural'Min (Parent.First, Data'Length)))),
       Post => (if Parent.Form = Missing then not Tree_Admitted'Result);
   function Tree_Admitted
     (Data : String; Parent : Node; Unique_Keys, Standard_Constants : Boolean)
      return Boolean
   is
      Position : Natural := Parent.First;
      Key, Child : Node;
   begin
      if Parent.Form = Missing or else Parent.First = 0 or else
        Parent.First > Parent.Last or else Parent.Last > Data'Length then return False; end if;
      if Standard_Constants and then Parent.Form = Number_Value and then
        Raw (Data,Parent) in "NaN" | "Infinity" | "-Infinity" then return False; end if;
      if Parent.Form not in Array_Value | Object_Value then return True; end if;
      Space (Data,Position);
      while Position < Parent.Last - 1 loop
         pragma Loop_Invariant (Position >= Parent.First);
         pragma Loop_Variant (Decreases => Parent.Last - Position);
         if Parent.Form = Object_Value then
            Scan (Data,Position,Key);
            if Key.Form /= String_Value or else
              (Unique_Keys and then not First_Key (Data,Parent,Key)) then return False; end if;
            Space (Data,Position);
            if Byte_At (Data,Position) /= ':' then return False; end if;
            Position := Position + 1;
         end if;
         Scan (Data,Position,Child);
         if not Tree_Admitted (Data,Child,Unique_Keys,Standard_Constants) then return False; end if;
         Space (Data,Position);
         if Byte_At (Data,Position) = ',' then Position := Position + 1; end if;
         Space (Data,Position);
      end loop;
      return True;
   end Tree_Admitted;
   function Standard_JSON (Data : String) return Boolean is
     (Tree_Admitted (Data,Parse (Data),False,True));
   function Duplicate_Free (Data : String) return Boolean is
     (Tree_Admitted (Data,Parse (Data),True,False));


   function Field (Data : String; Parent : Node; Name : String) return Node is
      Position : Natural;
      Key, Item : Node;
      Found : Node := No_Node;
   begin
      if Parent.Form /= Object_Value or else Parent.First = 0 or else
         Parent.Last > Data'Length then return No_Node; end if;
      Position := Parent.First;
      Space (Data, Position);
      while Position < Parent.Last - 1 loop
         pragma Loop_Invariant (Position >= Parent.First);
         pragma Loop_Invariant (Found.Form = Missing or else
           (Found.First > Parent.First and then Found.First <= Data'Length));
         pragma Loop_Variant (Increases => Position);
         Scan (Data, Position, Key);
         if Key.Form /= String_Value then return No_Node; end if;
         Space (Data, Position);
         if Byte_At (Data, Position) /= ':' then return No_Node; end if;
         Position := Position + 1;
         Scan (Data, Position, Item);
         if Item.Form = Missing then return No_Node; end if;
         if Is_Text (Data, Key, Name) then Found := Item; end if;
         Space (Data, Position);
         if Byte_At (Data, Position) = ',' then Position := Position + 1; end if;
         Space (Data, Position);
      end loop;
      return Found;
   end Field;

   function Element (Data : String; Parent : Node; Index : Positive) return Node is
      Position : Natural;
      Seen : Natural := 0;
      Item : Node;
   begin
      if Parent.Form /= Array_Value or else Parent.First = 0 or else Parent.Last > Data'Length then
         return No_Node;
      end if;
      Position := Parent.First;
      Space (Data, Position);
      while Position < Parent.Last - 1 loop
         pragma Loop_Invariant (Position >= Parent.First);
         pragma Loop_Invariant (Seen <= Position - Parent.First);
         pragma Loop_Variant (Increases => Position);
         Scan (Data, Position, Item);
         if Item.Form = Missing then return No_Node; end if;
         Seen := Seen + 1;
         if Seen = Index then return Item; end if;
         Space (Data, Position);
         if Byte_At (Data, Position) = ',' then Position := Position + 1; end if;
         Space (Data, Position);
      end loop;
      return No_Node;
   end Element;

   function Count (Data : String; Parent : Node) return Natural is
      Position : Natural;
      Seen : Natural := 0;
      Item : Node;
      Unique : Boolean;
   begin
      if Parent.Form not in Array_Value | Object_Value or else Parent.First = 0 or else
        Parent.Last > Data'Length then return 0; end if;
      Position := Parent.First;
      Space (Data, Position);
      while Position < Parent.Last - 1 loop
         pragma Loop_Invariant (Position >= Parent.First);
         pragma Loop_Invariant (Seen <= Position - Parent.First);
         pragma Loop_Variant (Increases => Position);
         Scan (Data, Position, Item);
         if Item.Form = Missing then return 0; end if;
         Unique := Parent.Form /= Object_Value or else First_Key (Data, Parent, Item);
         if Parent.Form = Object_Value then
            Space (Data, Position);
            if Byte_At (Data, Position) /= ':' then return 0; end if;
            Position := Position + 1;
            Scan (Data, Position, Item);
            if Item.Form = Missing then return 0; end if;
         end if;
         if Unique then Seen := Seen + 1; end if;
         Space (Data, Position);
         if Byte_At (Data, Position) = ',' then Position := Position + 1; end if;
         Space (Data, Position);
      end loop;
      return Seen;
   end Count;

   function Text (Data : String; Item : Node) return String is
      Output : String (1 .. (if Item.Form = String_Value and then Item.First > 0 and then
        Item.Last >= Item.First and then Item.Last <= Data'Length then Item.Last - Item.First + 1 else 0)) :=
        [others => Character'Val (0)];
      Used : Natural := 0;
      Position, Code, Low : Natural;
      C : Character;
      procedure Emit (Value : Natural) is
      begin
         Used := Used + 1;
         Output (Used) := Character'Val (Value);
      end Emit;
      procedure Unicode (Value : Natural) is
      begin
         if Value < 128 then Emit (Value);
         elsif Value < 2048 then Emit (192 + Value / 64); Emit (128 + Value mod 64);
         elsif Value < 65536 then
            Emit (224 + Value / 4096); Emit (128 + Value / 64 mod 64); Emit (128 + Value mod 64);
         else
            Emit (240 + Value / 262144); Emit (128 + Value / 4096 mod 64);
            Emit (128 + Value / 64 mod 64); Emit (128 + Value mod 64);
         end if;
      end Unicode;
   begin
      if Item.Form /= String_Value or else Item.First = 0 or else Item.Last > Data'Length or else
        Item.Last - Item.First < 1 then return ""; end if;
      Position := Item.First;
      while Position < Item.Last - 1 loop
         pragma Loop_Invariant (Position >= Item.First and then Used <= Position - Item.First);
         pragma Loop_Variant (Increases => Position);
         C := Byte_At (Data, Position);
         if C = '\' then
            Position := Position + 1;
            C := Byte_At (Data, Position);
            case C is
               when '"' | '\' | '/' => Emit (Character'Pos (C));
               when 'b' => Emit (8);
               when 'f' => Emit (12);
               when 'n' => Emit (10);
               when 'r' => Emit (13);
               when 't' => Emit (9);
               when 'u' =>
                  if Item.Last - 1 - Position < 5 then return ""; end if;
                  Code := 0;
                  for I in 1 .. 4 loop
                     if Hex (Byte_At (Data, Position + I)) < 0 then return ""; end if;
                     Code := Code * 16 + Natural (Hex (Byte_At (Data, Position + I)));
                  end loop;
                  Position := Position + 4;
                  if Code in 16#D800# .. 16#DBFF# and then
                    Item.Last - 1 - Position >= 6 and then Byte_At (Data,Position + 1) = '\'
                    and then Byte_At (Data,Position + 2) = 'u'
                  then
                     Low := 0;
                     for I in 3 .. 6 loop
                        if Hex (Byte_At (Data,Position + I)) < 0 then return ""; end if;
                        Low := Low * 16 + Natural (Hex (Byte_At (Data,Position + I)));
                     end loop;
                     if Low in 16#DC00# .. 16#DFFF# then
                        Code := 65536 + (Code - 16#D800#) * 1024 + Low - 16#DC00#;
                        Position := Position + 6;
                     end if;
                  end if;
                  Unicode (Code);
               when others => return "";
            end case;
         else Emit (Character'Pos (C));
         end if;
         Position := Position + 1;
      end loop;
      return Output (1 .. Used);
   end Text;

   function Is_Text (Data : String; Item : Node; Expected : String) return Boolean is
     (Item.Form = String_Value and then Text (Data, Item) = Expected);
   function Is_True (Data : String; Item : Node) return Boolean is
     (Item.Form = Boolean_Value and then Raw (Data, Item) = "true");
   function Is_False (Data : String; Item : Node) return Boolean is
     (Item.Form = Boolean_Value and then Raw (Data, Item) = "false");
   function Nonempty_Text (Data : String; Item : Node) return Boolean is
      Value : constant String := Text (Data, Item);
   begin
      return Item.Form = String_Value and then Value'Length > 0 and then
        (for all C of Value => C /= Character'Val (0));
   end Nonempty_Text;
   function Decimal (Data : String; Item : Node) return String is
     (if Item.Form = Integer_Value then Raw (Data, Item) else "");
   function Nonnegative (Data : String; Item : Node) return Boolean is
     (Item.Form = Integer_Value and then Item.First > 0 and then Item.Last <= Data'Length
      and then (Byte_At (Data, Item.First - 1) /= '-' or else Decimal (Data, Item) = "-0"));

   function Equal (Left : String; L : Node; Right : String; R : Node) return Boolean is
   begin
      if L.Form = Missing or else L.Form /= R.Form then return False; end if;
      case L.Form is
         when String_Value => return Text (Left, L) = Text (Right, R);
         when Array_Value =>
            if Count (Left, L) /= Count (Right, R) then return False; end if;
            for I in 1 .. Count (Left, L) loop
               if not Equal (Left, Element (Left, L, I), Right, Element (Right, R, I)) then return False; end if;
            end loop;
            return True;
         when Object_Value =>
            if Count (Left, L) /= Count (Right, R) then return False; end if;
            for I in 1 .. Count (Left, L) loop
               declare Name : constant String := Member_Name (Left, L, I);
               begin
                  if not Equal (Left, Field (Left, L, Name), Right, Field (Right, R, Name)) then return False; end if;
               end;
            end loop;
            return True;
         when others => return Raw (Left, L) = Raw (Right, R);
      end case;
   end Equal;

   function Number_Image (Data : String; Item : Node) return String is
      Token : constant String := Raw (Data,Item);
      package P renames Evaluation_Pending;
      use type P.Count;
   begin
      if Item.Form = Integer_Value then return (if Token = "-0" then "0" else Token); end if;
      if Item.Form /= Number_Value then return ""; end if;
      if Token = "NaN" then return "nan";
      elsif Token = "Infinity" then return "inf";
      elsif Token = "-Infinity" then return "-inf";
      end if;
      declare
         Arena : P.Bytes (1 .. P.Count (Token'Length));
      begin
         for K in Arena'Range loop Arena (K) := P.Byte (Character'Pos (Token (Token'First + Integer (K - 1)))); end loop;
         declare
            N : constant Exact_Decimal.Number := Exact_Decimal.Parse (Arena,(1,Arena'Length),0);
         begin
            if not N.Valid or else not N.Floating or else N.After /= Arena'Length then return ""; end if;
            declare B : constant Decimal_Binary64.Conversion := Decimal_Binary64.Convert (N); begin
               return (if B.Valid then Decimal_Binary64.Repr (B.Encoding)
                 elsif N.Negative then "-inf" else "inf");
            end;
         end;
      end;
   end Number_Image;

   function Truth (Data : String; Item : Node) return Boolean is
   begin
      case Item.Form is
         when Missing | Null_Value => return False;
         when Boolean_Value => return Is_True (Data, Item);
         when String_Value => return Text (Data, Item)'Length > 0;
         when Array_Value | Object_Value => return Count (Data, Item) > 0;
         when Integer_Value =>
            return Raw (Data,Item) /= "0" and then Raw (Data,Item) /= "-0";
         when Number_Value =>
            declare S : constant String := Number_Image (Data,Item); begin
               return S /= "" and then S /= "0.0" and then S /= "-0.0";
            end;
      end case;
   end Truth;

   function Slice (Data : String; Item : Node) return String is (Raw (Data, Item));
   function Member_Key (Data : String; Parent : Node; Index : Positive)
      return Node is
      Position : Natural;
      Seen : Natural := 0;
      Key, Item : Node;
   begin
      if Parent.Form /= Object_Value or else Parent.First = 0 or else
         Parent.Last > Data'Length then return No_Node; end if;
      Position := Parent.First;
      Space (Data, Position);
      while Position < Parent.Last - 1 loop
         pragma Loop_Invariant (Position >= Parent.First);
         pragma Loop_Invariant (Seen <= Position - Parent.First);
         pragma Loop_Variant (Increases => Position);
         Scan (Data, Position, Key);
         if Key.Form /= String_Value then return No_Node; end if;
         if First_Key (Data, Parent, Key) then
            Seen := Seen + 1;
            if Seen = Index then return Key; end if;
         end if;
         Space (Data, Position);
         if Byte_At (Data, Position) /= ':' then return No_Node; end if;
         Position := Position + 1;
         Scan (Data, Position, Item);
         if Item.Form = Missing then return No_Node; end if;
         Space (Data, Position);
         if Byte_At (Data, Position) = ',' then Position := Position + 1; end if;
         Space (Data, Position);
      end loop;
      return No_Node;
   end Member_Key;
   function Member_Name (Data : String; Parent : Node; Index : Positive)
      return String is (Text (Data,Member_Key (Data,Parent,Index)));

   function Field (Data, Name : String) return String is
     (Raw (Data, Field (Data, Parse (Data), Name)));
   function Element (Data : String; Index : Natural) return String is
     (if Index = Natural'Last then "" else Raw (Data, Element (Data, Parse (Data), Index + 1)));
   function Text (Data : String) return String is (Text (Data, Parse (Data)));
   function Kind (Data : String) return Value_Kind is (Parse (Data).Form);
   function Count (Data : String) return Natural is (Count (Data, Parse (Data)));
   function Truth (Data : String) return Boolean is (Truth (Data, Parse (Data)));
   function Equal (Left, Right : String) return Boolean is
     (Equal (Left, Parse (Left), Right, Parse (Right)));
   function Quote (Text : String) return String is
     (Worldline.Producer_Render.Quote (Text));
   function Python_String (Value : String) return String is
     (Worldline.Producer_Render.Python_String (Value));
end Worldline.Producer_Values;

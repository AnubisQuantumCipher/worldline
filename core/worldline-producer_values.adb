with Worldline.JSON_Syntax_Types;
with Worldline.Generic_JSON_Syntax;
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

   -- Candidate extraction: one syntax grammar, with the original String
   -- UTF8 primitive as its actual reader. It does not detect/strip a BOM.
   package JS renames Worldline.JSON_Syntax_Types;
   use type JS.Count;
   use type JS.Unit_Kind;
   use type JS.Value_Kind;
   type String_Context is null record;
   Empty_Context : constant String_Context := (null record);

   function String_Length (Data : String; Context : String_Context)
      return JS.Count
   with Global => null,
     Post => String_Length'Result = JS.Count (Data'Length)
   is
      pragma Unreferenced (Context);
   begin
      return JS.Count (Data'Length);
   end String_Length;

   function String_Read
     (Data : String; Context : String_Context; Position : JS.Count)
      return JS.Reader_Unit
   with Global => null,
     Post =>
       (if String_Read'Result.Kind in JS.ASCII_Unit | JS.Non_ASCII_Unit then
           String_Read'Result.Next_Offset > Position and then
           String_Read'Result.Next_Offset <= String_Length (Data, Context)
        else String_Read'Result.Next_Offset = Position) and then
       (if String_Read'Result.Kind = JS.End_Of_Source then
           Position = String_Length (Data, Context))
   is
   begin
      if Position > JS.Count (Data'Length) then
         return (JS.Invalid_Unit, Position);
      elsif Position = JS.Count (Data'Length) then
         return (JS.End_Of_Source, Position);
      end if;
      declare
         -- The actual String extent establishes this conversion. No wider
         -- source is refused or converted through Natural by this adapter.
         Offset : constant Natural := Natural (Position);
         Width : constant Natural := UTF8_Width (Data, Offset);
         Value : constant Character := Byte_At (Data, Offset);
      begin
         if Width = 0 then return (JS.Invalid_Unit, Position);
         elsif Character'Pos (Value) < 128 then
            return (JS.ASCII_Unit, Position + JS.Count (Width),
                    JS.ASCII_Character (Value));
         else
            return (JS.Non_ASCII_Unit, Position + JS.Count (Width));
         end if;
      end;
   end String_Read;

   package String_Grammar is new Worldline.Generic_JSON_Syntax
     (Source_Data => String, Source_Context => String_Context,
      Source_Length_Impl => String_Length, Read_Unit_Impl => String_Read);

   function Original_Form (Form : JS.Value_Kind) return Value_Kind is
     (case Form is
        when JS.Missing => Missing,
        when JS.Null_Value => Null_Value,
        when JS.Boolean_Value => Boolean_Value,
        when JS.Integer_Value => Integer_Value,
        when JS.Number_Value => Number_Value,
        when JS.String_Value => String_Value,
        when JS.Array_Value => Array_Value,
        when JS.Object_Value => Object_Value)
   with Global => null;

   function Original_Node (Item : JS.Node; Length : Natural) return Node
   with Global => null,
     Pre => JS.Within (Item, JS.Count (Length)),
     Post => Original_Node'Result.Form = Original_Form (Item.Form) and then
       (if Item.Form /= JS.Missing then
           Original_Node'Result.First > 0 and then
           JS.Count (Original_Node'Result.First) = Item.First + 1 and then
           JS.Count (Original_Node'Result.Last) = Item.After and then
           Original_Node'Result.First <= Original_Node'Result.Last and then
           Original_Node'Result.Last <= Length)
   is
   begin
      if Item.Form = JS.Missing then return No_Node; end if;
      return (Original_Form (Item.Form), Natural (Item.First + 1), Natural (Item.After));
   end Original_Node;

   procedure Space (Data : String; Position : in out Natural)
     with Post => Position >= Position'Old and then
       (if Position'Old <= Data'Length then Position <= Data'Length
        else Position = Position'Old)
   is
      Wide_Position : JS.Count := JS.Count (Position);
   begin
      String_Grammar.Space (Data, Empty_Context, Wide_Position);
      Position := Natural (Wide_Position);
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
            Item.First > Position'Old and then Item.First <= Data'Length and then Item.Last = Position)
         and then
           (if Position'Old <= Data'Length then Position <= Data'Length
            else Position = Position'Old);

   procedure Scan (Data : String; Position : in out Natural; Item : out Node) is
      Result : constant String_Grammar.Scan_Result :=
        String_Grammar.Scan (Data, Empty_Context, JS.Count (Position));
   begin
      Position := Natural (Result.Position);
      Item := Original_Node (Result.Item, Data'Length);
   end Scan;

   function Parse (Data : String) return Node is
      Wide_Item : constant JS.Node := String_Grammar.Parse (Data, Empty_Context);
   begin
      return Original_Node (Wide_Item, Data'Length);
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
         pragma Loop_Invariant
           (Position <= Natural'Max (Parent.First, Data'Length));
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

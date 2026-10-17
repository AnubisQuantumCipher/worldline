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
   type Child_Status is
     (Child_Ready, Invalid_Container_Delimiters, Invalid_Container_Span,
      Invalid_Member_Key, Invalid_Member_Separator, Invalid_Child_Span,
      Invalid_Child_Separator, Invalid_Trailing_Separator);

   --  The capacity pass must distinguish malformed input from the closing
   --  delimiter, including a malformed suffix after otherwise valid members.
   --  Publish neither a child nor a cursor advance unless the whole step is
   --  valid. The strict iterator below shares this scan, not a second grammar.
   procedure Try_Next_Child
     (Data : String; Parent : Node; Position : in out Natural;
      Key, Item : out Node; Status : out Child_Status)
   with
     Global => null, Always_Terminates,
     Post =>
       (if Status = Child_Ready then
           Parent.Form in Array_Value | Object_Value and then
           Parent.First > 0 and then Parent.First < Parent.Last and then
           Parent.Last <= Data'Length and then
           Position'Old in Parent.First .. Parent.Last - 1 and then
           Position in Position'Old .. Parent.Last - 1 and then
           (if Item.Form = Missing then
               Position = Parent.Last - 1 and then Key.Form = Missing
            else
               Position > Position'Old and then Item.First > Parent.First and then
               Item.First > Position'Old and then Item.First <= Item.Last and then
               Item.Last < Parent.Last and then
               (if Parent.Form = Object_Value then
                   Key.Form = String_Value and then Key.First > Parent.First and then
                   Key.First < Key.Last and then Key.Last < Item.First
                else Key.Form = Missing))
        else Position = Position'Old and then Key = No_Node and then Item = No_Node)
   is
      Start : constant Natural := Position;
      Next : Natural := Position;
      Found_Key, Found_Item : Node := No_Node;
   begin
      Key := No_Node;
      Item := No_Node;
      Status := Invalid_Container_Span;
      if Parent.Form not in Array_Value | Object_Value or else
        Parent.First = 0 or else Parent.First >= Parent.Last or else
        Parent.Last > Data'Length or else
        Position < Parent.First or else Position >= Parent.Last
      then
         return;
      end if;
      if Byte_At (Data, Parent.First - 1) /=
        (if Parent.Form = Array_Value then '[' else '{') or else
        Byte_At (Data, Parent.Last - 1) /=
          (if Parent.Form = Array_Value then ']' else '}')
      then
         Status := Invalid_Container_Delimiters;
         return;
      end if;
      Space (Data, Next);
      if Next > Parent.Last - 1 then
         return;
      elsif Next = Parent.Last - 1 then
         Position := Next;
         Status := Child_Ready;
         return;
      end if;
      if Parent.Form = Object_Value then
         Scan (Data, Next, Found_Key);
         if Found_Key.Form /= String_Value or else
           Found_Key.First <= Parent.First or else
           Found_Key.First >= Found_Key.Last or else Found_Key.Last >= Parent.Last
         then
            Status := Invalid_Member_Key;
            return;
         end if;
         Space (Data, Next);
         if Next >= Parent.Last - 1 or else Byte_At (Data, Next) /= ':' then
            Status := Invalid_Member_Separator;
            return;
         end if;
         Next := Next + 1;
      end if;
      Scan (Data, Next, Found_Item);
      if Found_Item.Form = Missing or else Found_Item.First <= Parent.First or else
        Found_Item.First <= Start or else Found_Item.First > Found_Item.Last or else
        Found_Item.Last >= Parent.Last or else
        (Parent.Form = Object_Value and then Found_Key.Last >= Found_Item.First)
      then
         Status := Invalid_Child_Span;
         return;
      end if;
      Space (Data, Next);
      if Next > Parent.Last - 1 then
         return;
      elsif Next < Parent.Last - 1 then
         if Byte_At (Data, Next) /= ',' then
            Status := Invalid_Child_Separator;
            return;
         end if;
         Next := Next + 1;
         Space (Data, Next);
         if Next >= Parent.Last - 1 then
            Status := Invalid_Trailing_Separator;
            return;
         end if;
      end if;
      Position := Next;
      Key := Found_Key;
      Item := Found_Item;
      Status := Child_Ready;
   end Try_Next_Child;

   procedure Next_Child
     (Data : String; Parent : Node; Position : in out Natural;
      Key, Item : out Node)
   is
      Status : Child_Status;
   begin
      Try_Next_Child (Data, Parent, Position, Key, Item, Status);
      case Status is
         when Child_Ready => null;
         when Invalid_Container_Delimiters =>
            raise Program_Error with "invalid producer container delimiters";
         when Invalid_Container_Span =>
            raise Program_Error with "invalid producer container span";
         when Invalid_Member_Key =>
            raise Program_Error with "invalid producer member key";
         when Invalid_Member_Separator =>
            raise Program_Error with "invalid producer member separator";
         when Invalid_Child_Span =>
            raise Program_Error with "invalid producer child span";
         when Invalid_Child_Separator =>
            raise Program_Error with "invalid producer child separator";
         when Invalid_Trailing_Separator =>
            raise Program_Error with "invalid producer trailing separator";
      end case;
   end Next_Child;


   --  One source unit, shared by Text's exact count/write decoder and the
   --  object index's allocation-free decoded-byte comparisons. Unpaired
   --  surrogates retain the same surrogatepass bytes as before.
   procedure Decode_Unit
     (Data : String; Last : Positive; Position : in out Natural;
      Unit : out Decoded_Unit)
   is
      C : Character;
      Code, Low : Natural;
      procedure Emit (Value : Natural)
        with Pre => Value <= 255 and then Unit.Length < 4,
          Post => Unit.Length = Unit.Length'Old + 1
      is
      begin
         Unit.Length := Unit.Length + 1;
         Unit.Bytes (Unit.Length) := Character'Val (Value);
      end Emit;
      procedure Unicode (Value : Natural)
        with Pre => Value <= 16#10FFFF# and then Unit.Length = 0,
          Post => Unit.Length in 1 .. 4
      is
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
      Unit := (others => <>);
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
               if Last - 1 - Position < 5 then return; end if;
               Code := 0;
               for I in 1 .. 4 loop
                  if Hex (Byte_At (Data, Position + I)) < 0 then return; end if;
                  Code := Code * 16 + Natural (Hex (Byte_At (Data, Position + I)));
               end loop;
               Position := Position + 4;
               if Code in 16#D800# .. 16#DBFF# and then
                 Last - 1 - Position >= 6 and then Byte_At (Data, Position + 1) = '\'
                 and then Byte_At (Data, Position + 2) = 'u'
               then
                  Low := 0;
                  for I in 3 .. 6 loop
                     if Hex (Byte_At (Data, Position + I)) < 0 then return; end if;
                     Low := Low * 16 + Natural (Hex (Byte_At (Data, Position + I)));
                  end loop;
                  if Low in 16#DC00# .. 16#DFFF# then
                     Code := 65536 + (Code - 16#D800#) * 1024 + Low - 16#DC00#;
                     Position := Position + 6;
                  end if;
               end if;
               Unicode (Code);
            when others => return;
         end case;
      else
         Emit (Character'Pos (C));
      end if;
      Position := Position + 1;
      Unit.Valid := True;
   end Decode_Unit;

   function Compare_Keys (Data : String; Left, Right : Node) return Integer
     with Post => Compare_Keys'Result in -1 .. 1
   is
      L_Position : Natural := Left.First;
      R_Position : Natural := Right.First;
      L_Unit, R_Unit : Decoded_Unit;
      L_Used, R_Used : Natural range 0 .. 4 := 0;
      L_Byte, R_Byte : Character;
      L_Present, R_Present : Boolean;
      procedure Next_Byte
        (Last : Positive; Position : in out Natural;
         Unit : in out Decoded_Unit; Used : in out Natural;
         Value : out Character; Present : out Boolean)
      with
        Pre => Last <= Data'Length and then Position <= Last and then
          Used <= Unit.Length,
        Post => Position in Position'Old .. Last and then
          Used <= Unit.Length
      is
      begin
         Value := Character'Val (0);
         Present := False;
         if Used = Unit.Length then
            if Position >= Last - 1 then return; end if;
            Decode_Unit (Data, Last, Position, Unit);
            if not Unit.Valid then
               raise Program_Error with "invalid producer decoded member key";
            end if;
            Used := 0;
         end if;
         Used := Used + 1;
         Value := Unit.Bytes (Used);
         Present := True;
      end Next_Byte;
   begin
      if Left.Form /= String_Value or else Left.First = 0 or else
        Left.First >= Left.Last or else Left.Last > Data'Length or else
        Right.Form /= String_Value or else Right.First = 0 or else
        Right.First >= Right.Last or else Right.Last > Data'Length
      then
         raise Program_Error with "invalid producer member key span";
      end if;
      loop
         pragma Loop_Invariant (L_Position <= Left.Last and then R_Position <= Right.Last);
         pragma Loop_Invariant (L_Used <= L_Unit.Length and then R_Used <= R_Unit.Length);
         pragma Loop_Variant
           (Decreases => Long_Long_Integer (Left.Last - L_Position) +
              Long_Long_Integer (L_Unit.Length - L_Used));
         Next_Byte (Left.Last, L_Position, L_Unit, L_Used, L_Byte, L_Present);
         Next_Byte (Right.Last, R_Position, R_Unit, R_Used, R_Byte, R_Present);
         if not L_Present then return (if R_Present then -1 else 0);
         elsif not R_Present then return 1;
         elsif L_Byte < R_Byte then return -1;
         elsif L_Byte > R_Byte then return 1;
         end if;
      end loop;
   end Compare_Keys;

   function Members (Data : String; Parent : Node) return Member_Index is
      Position : Natural := Parent.First;
      Key, Item : Node;
      Status : Child_Status;
      Total : Natural := 0;

      --  A bounded array and ordinary in-place heapsort avoid both a hidden
      --  map-capacity limit and container callbacks outside this proof scope.
      --  The first sort groups equal decoded names, breaking ties by source
      --  position. The second restores first-occurrence order after compaction.
      procedure Sort
        (Entries : in out Member_Array; Length : Natural; Source_Order : Boolean)
      with
        Pre => Entries'First = 1 and then Length <= Entries'Length
      is
         function Before (Left, Right : Member_Entry) return Boolean is
         begin
            if Source_Order then return Left.Key.First < Right.Key.First; end if;
            declare
               Order : constant Integer := Compare_Keys (Data, Left.Key, Right.Key);
            begin
               return Order < 0 or else
                 (Order = 0 and then Left.Key.First < Right.Key.First);
            end;
         end Before;
         procedure Sift (Root, Last : Positive)
           with Pre => Root <= Last and then Last <= Entries'Length
         is
            Position : Positive := Root;
            Child : Positive;
            Temporary : Member_Entry;
         begin
            while Position <= Last / 2 loop
               pragma Loop_Invariant (Position <= Last);
               pragma Loop_Variant (Increases => Position);
               Child := Position * 2;
               if Child < Last and then Before (Entries (Child), Entries (Child + 1)) then
                  Child := Child + 1;
               end if;
               exit when not Before (Entries (Position), Entries (Child));
               Temporary := Entries (Position);
               Entries (Position) := Entries (Child);
               Entries (Child) := Temporary;
               Position := Child;
            end loop;
         end Sift;
         Temporary : Member_Entry;
      begin
         if Length < 2 then return; end if;
         for Root in reverse 1 .. Length / 2 loop
            Sift (Root, Length);
         end loop;
         for Last in reverse 2 .. Length loop
            Temporary := Entries (1);
            Entries (1) := Entries (Last);
            Entries (Last) := Temporary;
            Sift (1, Last - 1);
         end loop;
      end Sort;
   begin
      if Parent.Form /= Object_Value or else Parent.First = 0 or else
        Parent.First >= Parent.Last or else Parent.Last > Data'Length
      then
         return Empty : Member_Index (0) do
            null;
         end return;
      end if;
      loop
         pragma Loop_Invariant (Position in Parent.First .. Parent.Last - 1);
         pragma Loop_Invariant (Total <= Position - Parent.First);
         pragma Loop_Variant (Increases => Position);
         Try_Next_Child (Data, Parent, Position, Key, Item, Status);
         if Status /= Child_Ready then
            return Empty : Member_Index (0) do
               null;
            end return;
         end if;
         exit when Item.Form = Missing;
         Total := Total + 1;
      end loop;
      return Result : Member_Index (Total) do
         Position := Parent.First;
         for I in 1 .. Total loop
            pragma Loop_Invariant (Position in Parent.First .. Parent.Last - 1);
            Next_Child (Data, Parent, Position, Key, Item);
            if Item.Form = Missing then
               raise Program_Error with "producer member count mismatch";
            end if;
            Result.Entries (I) := (Key, Item);
         end loop;
         Next_Child (Data, Parent, Position, Key, Item);
         if Item.Form /= Missing then
            raise Program_Error with "producer member count mismatch";
         end if;
         Sort (Result.Entries, Total, False);
         declare
            Unique : Natural := 0;
         begin
            for I in 1 .. Total loop
               pragma Loop_Invariant (Unique < I);
               if Unique > 0 and then
                 Compare_Keys (Data, Result.Entries (Unique).Key, Result.Entries (I).Key) = 0
               then
                  Result.Entries (Unique).Item := Result.Entries (I).Item;
               else
                  Unique := Unique + 1;
                  Result.Entries (Unique) := Result.Entries (I);
               end if;
            end loop;
            Sort (Result.Entries, Unique, True);
            Result.Length := Unique;
         end;
      end return;
   end Members;


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
      --  Count and emit with one decoder. The result is built in place rather
      --  than reserving a source-sized local buffer on the primary stack.
      procedure Scan
        (Render : Boolean; Output : out String; Size : out Natural;
         Valid : out Boolean)
      with
        Pre => (Render or else Output'Length = 0) and then
          Item.First > 0 and then Item.First < Item.Last and then Item.Last <= Data'Length,
        Relaxed_Initialization => Output,
        Post => (if Valid then Output'Initialized and then
          (if Render then Size = Output'Length))
      is
         Used : Natural := 0;
         Position : Natural;
         Unit : Decoded_Unit;
         function Ready return Boolean is
           (not Render or else
              (Used <= Output'Length and then
                 (Used = 0 or else
                    Output (Output'First .. Output'First + (Used - 1))'Initialized)))
           with Ghost;
         procedure Emit (Value : Natural)
           with Pre => Value <= 255 and then Ready,
             Post => Ready and then Used > Used'Old and then
               Used - Used'Old = 1
         is
         begin
            if Used = Natural'Last then
               raise Constraint_Error with "decoded text exceeds String extent";
            end if;
            if Render then
               if Used = Output'Length then
                  raise Program_Error with "decoded text extent mismatch";
               end if;
               Output (Output'First + Used) := Character'Val (Value);
            end if;
            Used := Used + 1;
         end Emit;
      begin
         Size := 0;
         Valid := False;
         Position := Item.First;
         while Position < Item.Last - 1 loop
            pragma Loop_Invariant (Position >= Item.First and then Used <= Position - Item.First);
            pragma Loop_Invariant (Position <= Item.Last);
            pragma Loop_Invariant (Ready);
            pragma Loop_Variant (Increases => Position);
            Decode_Unit (Data, Item.Last, Position, Unit);
            if not Unit.Valid then return; end if;
            for K in 1 .. Unit.Length loop
               pragma Loop_Invariant (Ready);
               Emit (Character'Pos (Unit.Bytes (K)));
            end loop;
         end loop;
         if Render and then Used /= Output'Length then
            raise Program_Error with "decoded text extent mismatch";
         end if;
         Size := Used;
         Valid := True;
         pragma Assert (Output'Initialized);
      end Scan;
      Empty : String (1 .. 0);
      Size : Natural;
      Valid : Boolean;
   begin
      if Item.Form /= String_Value or else Item.First = 0 or else
        Item.Last > Data'Length or else Item.Last <= Item.First
      then
         return "";
      end if;
      Scan (False, Empty, Size, Valid);
      if not Valid then return ""; end if;
      return Result : String (1 .. Size) do
         declare
            Written : Natural;
            Complete : Boolean;
         begin
            Scan (True, Result, Written, Complete);
            if not Complete or else Written /= Size then
               raise Program_Error with "decoded text extent mismatch";
            end if;
         end;
      end return;
   end Text;

   function Is_Text (Data : String; Item : Node; Expected : String) return Boolean is
      Position : Natural := Item.First;
      Unit : Decoded_Unit;
      Seen : Natural := 0;
      Matched : Boolean := True;
   begin
      if Item.Form /= String_Value then return False; end if;
      if Item.First = 0 or else Item.First >= Item.Last or else Item.Last > Data'Length then
         return Expected'Length = 0;
      end if;
      while Position < Item.Last - 1 loop
         pragma Loop_Invariant (Position in Item.First .. Item.Last);
         pragma Loop_Invariant (Seen <= Position - Item.First);
         pragma Loop_Variant (Increases => Position);
         Decode_Unit (Data, Item.Last, Position, Unit);
         if not Unit.Valid then return Expected'Length = 0; end if;
         for K in 1 .. Unit.Length loop
            if Seen >= Expected'Length or else
              Expected (Expected'First + Seen) /= Unit.Bytes (K)
            then
               Matched := False;
            end if;
            Seen := Seen + 1;
         end loop;
      end loop;
      return Matched and then Seen = Expected'Length;
   end Is_Text;
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

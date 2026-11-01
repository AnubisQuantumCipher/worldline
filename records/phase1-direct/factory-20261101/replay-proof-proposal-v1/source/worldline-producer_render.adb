with Worldline.Producer_Values;
with Worldline.Producer_Unicode;
package body Worldline.Producer_Render with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   use type V.Value_Kind;
   Hex : constant String := "0123456789abcdef";
   function Hex_Image (Code, Width : Natural) return String
     with Pre => Width <= 8,
          Post => Hex_Image'Result'Length = Width
   is
      Result : String (1 .. Width);
      Remaining : Natural := Code;
   begin
      for I in reverse Result'Range loop
         Result (I) := Hex (Remaining mod 16 + 1);
         Remaining := Remaining / 16;
      end loop;
      return Result;
   end Hex_Image;

   function Quote_Byte_Size (C : Character) return Positive is
     (if C = '"' or else C = '\' or else
         C = Character'Val (8) or else C = Character'Val (9) or else
         C = Character'Val (10) or else C = Character'Val (12) or else
         C = Character'Val (13)
      then 2
      elsif Character'Pos (C) < 32 then 6
      else 1)
     with Global => null, Post => Quote_Byte_Size'Result <= 6;

   function Quote_Byte (C : Character) return String is
     (if C = '"' then "\"""
      elsif C = '\' then "\\"
      elsif C = Character'Val (8) then "\b"
      elsif C = Character'Val (9) then "\t"
      elsif C = Character'Val (10) then "\n"
      elsif C = Character'Val (12) then "\f"
      elsif C = Character'Val (13) then "\r"
      elsif Character'Pos (C) < 32 then
        "\u00" & Hex_Image (Character'Pos (C), 2)
      else String'(1 => C))
     with Global => null,
       Post => Quote_Byte'Result'Length = Quote_Byte_Size (C);

   --  Text discards the entire decoded prefix on any malformed unit. Count
   --  in a type wide enough for every possible escaped source byte, and only
   --  enforce String's extent after decoding succeeds. Thus even an escaped
   --  prefix larger than Natural'Last cannot mask a later malformed unit.
   subtype Quote_Count is Long_Long_Integer
     range 0 .. 6 * Long_Long_Integer (Natural'Last) + 2;

   procedure Measure_Decoded_Quote
     (Data : String; Item : V.Node; Size : out Natural; Valid : out Boolean)
   with
     Global => null, Always_Terminates,
     Pre => Item.Form = V.String_Value and then Item.First > 0 and then
       Item.First < Item.Last and then Item.Last <= Data'Length,
     Post => Size >= 2 and then (if not Valid then Size = 2)
   is
      Position : Natural := Item.First;
      Used : Quote_Count := 2;
      Unit : V.Decoded_Unit;
   begin
      Size := 2;
      Valid := False;
      while Position < Item.Last - 1 loop
         pragma Loop_Invariant (Position in Item.First .. Item.Last);
         pragma Loop_Invariant
           (Used >= 2 and then
              Used - 2 <= 6 * Long_Long_Integer (Position - Item.First));
         pragma Loop_Variant (Increases => Position);
         declare
            Before : constant Natural := Position;
            Prefix : constant Quote_Count := Used;
         begin
            V.Decode_Unit (Data, Item.Last, Position, Unit);
            if not Unit.Valid then return; end if;
            for K in 1 .. Unit.Length loop
               pragma Loop_Invariant (Used >= Prefix);
               pragma Loop_Invariant
                 (Used - Prefix <= 6 * Long_Long_Integer (K - 1));
               pragma Loop_Invariant
                 (Prefix >= 2 and then
                    Prefix - 2 <= 6 * Long_Long_Integer (Before - Item.First));
               pragma Loop_Invariant (Unit.Length <= Position - Before);
               Used := Used + Long_Long_Integer (Quote_Byte_Size (Unit.Bytes (K)));
            end loop;
         end;
      end loop;
      if Used > Long_Long_Integer (Natural'Last) then
         raise Constraint_Error with "producer rendering exceeds String extent";
      end if;
      Size := Natural (Used);
      Valid := True;
   end Measure_Decoded_Quote;
   type Text_Cursor is record
      Position : Natural := 0;
      Unit : V.Decoded_Unit;
      Used : Natural range 0 .. 4 := 0;
   end record;

   procedure Next_Text_Byte
     (Data : String; Last : Positive; Cursor : in out Text_Cursor;
      Value : out Character; Present : out Boolean)
   with
     Global => null, Always_Terminates,
     Pre => Last <= Data'Length and then Cursor.Position <= Last and then
       Cursor.Used <= Cursor.Unit.Length,
     Post => Cursor.Position in Cursor.Position'Old .. Last and then
       Cursor.Used <= Cursor.Unit.Length and then
       (if Present then
           Long_Long_Integer (Last - Cursor.Position) +
             Long_Long_Integer (Cursor.Unit.Length - Cursor.Used) <
           Long_Long_Integer (Last - Cursor.Position'Old) +
             Long_Long_Integer (Cursor.Unit.Length'Old - Cursor.Used'Old))
   is
   begin
      Value := Character'Val (0);
      Present := False;
      if Cursor.Used = Cursor.Unit.Length then
         if Cursor.Position >= Last - 1 then return; end if;
         V.Decode_Unit (Data, Last, Cursor.Position, Cursor.Unit);
         if not Cursor.Unit.Valid then
            raise Program_Error with "invalid producer decoded text";
         end if;
         Cursor.Used := 0;
      end if;
      Cursor.Used := Cursor.Used + 1;
      Value := Cursor.Unit.Bytes (Cursor.Used);
      Present := True;
   end Next_Text_Byte;

   function Delimiter (Data : String; Item : V.Node) return Character
     with Pre => Item.Form = V.String_Value and then Item.First > 0 and then
       Item.First < Item.Last and then Item.Last <= Data'Length
   is
      Single : Boolean := False;
      Double : Boolean := False;
      Cursor : Text_Cursor := (Position => Item.First, others => <>);
      C : Character;
      Present : Boolean;
   begin
      loop
         pragma Loop_Invariant (Cursor.Position <= Item.Last);
         pragma Loop_Invariant (Cursor.Used <= Cursor.Unit.Length);
         pragma Loop_Variant
           (Decreases => Long_Long_Integer (Item.Last - Cursor.Position) +
              Long_Long_Integer (Cursor.Unit.Length - Cursor.Used));
         Next_Text_Byte (Data, Item.Last, Cursor, C, Present);
         exit when not Present;
         if C = ''' then Single := True; end if;
         if C = '"' then Double := True; end if;
      end loop;
      return (if Single and not Double then '"' else ''');
   end Delimiter;

   --  Quote, size-only native emission, and direct native emission all use
   --  this one byte escape convention. Only bounded escape pieces are made.
   procedure Quote_Scan
     (Text : String; Root : V.Node; Decoded, Render : Boolean;
      Output : out String; Size : out Natural)
   with
     Global => null, Always_Terminates,
     Pre => (Render or else Output'Length = 0) and then
       (if Decoded then Root.Form = V.String_Value and then Root.First > 0 and then
           Root.First < Root.Last and then Root.Last <= Text'Length),
     Relaxed_Initialization => Output,
     Post => Output'Initialized and then Size >= 2 and then
       (if Render then Size = Output'Length)
   is
      Used : Natural := 0;
      function Ready return Boolean is
        (not Render or else
           (Used <= Output'Length and then
              (Used = 0 or else
                 Output (Output'First .. Output'First + (Used - 1))'Initialized)))
        with Ghost;
      procedure Put (Piece : String)
        with Always_Terminates, Pre => Ready,
          Post => Ready and then Used >= Used'Old and then
            Used - Used'Old = Piece'Length
      is
      begin
         if Piece'Length > Natural'Last - Used then
            raise Constraint_Error with "producer rendering exceeds String extent";
         end if;
         if Render and then Piece'Length > Output'Length - Used then
            raise Program_Error with "producer rendering extent mismatch";
         end if;
         declare
            Next : constant Natural := Used + Piece'Length;
         begin
            if Render and then Piece'Length > 0 then
               Output (Output'First + Used .. Output'First + (Next - 1)) := Piece;
            end if;
            Used := Next;
         end;
      end Put;
      procedure Put_Byte (C : Character)
        with Always_Terminates, Pre => Ready,
          Post => Ready and then Used > Used'Old
      is
         Width : constant Positive := Quote_Byte_Size (C);
      begin
         if Render then
            Put (Quote_Byte (C));
         else
            if Width > Natural'Last - Used then
               raise Constraint_Error with "producer rendering exceeds String extent";
            end if;
            Used := Used + Width;
         end if;
      end Put_Byte;
   begin
      Put ("""");
      if Decoded then
         declare
            Cursor : Text_Cursor := (Position => Root.First, others => <>);
            C : Character;
            Present : Boolean;
         begin
            loop
               pragma Loop_Invariant (Ready);
               pragma Loop_Invariant (Used > 0);
               pragma Loop_Invariant (Cursor.Position <= Root.Last);
               pragma Loop_Invariant (Cursor.Used <= Cursor.Unit.Length);
               pragma Loop_Variant
                 (Decreases => Long_Long_Integer (Root.Last - Cursor.Position) +
                    Long_Long_Integer (Cursor.Unit.Length - Cursor.Used));
               Next_Text_Byte (Text, Root.Last, Cursor, C, Present);
               exit when not Present;
               Put_Byte (C);
            end loop;
         end;
      else
         for C of Text loop
            pragma Loop_Invariant (Ready);
            pragma Loop_Invariant (Used > 0);
            Put_Byte (C);
         end loop;
      end if;
      Put ("""");
      if Render and then Used /= Output'Length then
         raise Program_Error with "producer rendering extent mismatch";
      end if;
      Size := Used;
      pragma Assert (Output'Initialized);
   end Quote_Scan;

   function Quote_Size (Text : String) return Natural is
      Empty : String (1 .. 0);
      Size : Natural;
   begin
      Quote_Scan (Text, V.No_Node, False, False, Empty, Size);
      pragma Unused (Empty); -- Sizing has no output elements to consume.
      return Size;
   end Quote_Size;

   procedure Write_Quote (Text : String; Output : out String) is
      Size : Natural;
   begin
      Quote_Scan (Text, V.No_Node, False, True, Output, Size);
      pragma Assert (Size = Output'Length);
   end Write_Quote;

   function Quote_Size (Data : String; Item : V.Node) return Natural is
      Size : Natural;
      Valid : Boolean;
   begin
      Measure_Decoded_Quote (Data, Item, Size, Valid);
      return (if Valid then Size else 2);
   end Quote_Size;

   procedure Write_Quote (Data : String; Item : V.Node; Output : out String) is
      Size, Written : Natural;
      Valid : Boolean;
   begin
      Measure_Decoded_Quote (Data, Item, Size, Valid);
      if Output'Length /= Size then
         raise Program_Error with "producer rendering extent mismatch";
      end if;
      if Valid then
         Quote_Scan (Data, Item, True, True, Output, Written);
      else
         Quote_Scan ("", V.No_Node, False, True, Output, Written);
      end if;
      pragma Assert (Written = Size);
   end Write_Quote;

   --  Both passes use the same emitter. The first counts the actual bytes;
   --  the second writes once into the exactly sized result. Neither pass
   --  constructs rendered suffixes or copies the source for child traversal.
   procedure Scan
     (Data : String; Root : V.Node; Render : Boolean;
      Output : out String; Size : out Natural)
   with
     Global => null,
     Always_Terminates,
     Pre => Render or else Output'Length = 0,
     Relaxed_Initialization => Output,
     Post => Output'Initialized and then
       (if Render then Size = Output'Length)
   is
      Used : Natural := 0;

      function Ready return Boolean is
        (not Render or else
           (Used <= Output'Length and then
              (Used = 0 or else
                 Output (Output'First .. Output'First + (Used - 1))'Initialized)))
        with Ghost;

      procedure Put (Piece : String)
        with Always_Terminates, Pre => Ready,
          Post => Ready and then Used >= Used'Old and then
            Used - Used'Old = Piece'Length
      is
      begin
         if Piece'Length > Natural'Last - Used then
            raise Constraint_Error with "producer rendering exceeds String extent";
         end if;
         if Render and then Piece'Length > Output'Length - Used then
            raise Program_Error with "producer rendering extent mismatch";
         end if;
         declare
            Next : constant Natural := Used + Piece'Length;
         begin
            if Render and then Piece'Length > 0 then
               Output (Output'First + Used .. Output'First + (Next - 1)) := Piece;
            end if;
            Used := Next;
         end;
      end Put;

      --  Integer images are their source spans, except for -0. In particular,
      --  the count pass does not request an input-sized Raw/Number_Image result.
      procedure Integer_Repr (Item : V.Node)
        with Always_Terminates,
          Pre => Ready and then Item.Form = V.Integer_Value,
          Post => Ready and then Used >= Used'Old
      is
         Start : constant Natural := Used;
         Length : Natural;
      begin
         --  Retain Number_Image's empty image for invalid numeric spans.
         if Item.First = 0 or else Item.First > Item.Last or else
           Item.Last > Data'Length
         then
            return;
         end if;
         if Item.Last - Item.First = 1 and then
           Data (Data'First + (Item.First - 1)) = '-' and then
           Data (Data'First + (Item.Last - 1)) = '0'
         then
            Put ("0");
            return;
         end if;
         Length := Item.Last - Item.First + 1;
         if Length > Natural'Last - Used then
            raise Constraint_Error with "producer rendering exceeds String extent";
         end if;
         if Render then
            if Length > Output'Length - Used then
               raise Program_Error with "producer rendering extent mismatch";
            end if;
            for I in Item.First .. Item.Last loop
               pragma Loop_Invariant (Ready);
               pragma Loop_Invariant (Used = Start + (I - Item.First));
               pragma Loop_Invariant (Length <= Output'Length - Start);
               Output (Output'First + Used) := Data (Data'First + (I - 1));
               Used := Used + 1;
            end loop;
         else
            Used := Used + Length;
         end if;
      end Integer_Repr;


      procedure String_Repr (Item : V.Node)
        with Always_Terminates,
          Pre => Ready and then Item.Form = V.String_Value and then
            Item.First > 0 and then Item.First < Item.Last and then Item.Last <= Data'Length,
          Post => Ready and then Used >= Used'Old and then
            Used - Used'Old >= 2
      is
         Mark : constant Character := Delimiter (Data, Item);
         Start : constant Natural := Used;
         Cursor : Text_Cursor := (Position => Item.First, others => <>);
         Bytes : String (1 .. 4) := (others => Character'Val (0));
         Present : Boolean;
         Width : Natural range 1 .. 4;
         Code : Natural;
      begin
         Put (String'(1 => Mark));
         loop
            pragma Loop_Invariant (Ready);
            pragma Loop_Invariant (Used > Start);
            pragma Loop_Invariant (Cursor.Position <= Item.Last);
            pragma Loop_Invariant (Cursor.Used <= Cursor.Unit.Length);
            pragma Loop_Variant
              (Decreases => Long_Long_Integer (Item.Last - Cursor.Position) +
                 Long_Long_Integer (Cursor.Unit.Length - Cursor.Used));
            Next_Text_Byte (Data, Item.Last, Cursor, Bytes (1), Present);
            exit when not Present;
            Code := Character'Pos (Bytes (1));
            Width := 1;
            if Code in 16#C2# .. 16#DF# then
               Code := Code - 16#C0#;
               Width := 2;
            elsif Code in 16#E0# .. 16#EF# then
               Code := Code - 16#E0#;
               Width := 3;
            elsif Code in 16#F0# .. 16#F4# then
               Code := Code - 16#F0#;
               Width := 4;
            end if;
            for K in 2 .. Width loop
               pragma Loop_Invariant (Cursor.Position <= Item.Last);
               pragma Loop_Invariant (Cursor.Used <= Cursor.Unit.Length);
               Next_Text_Byte (Data, Item.Last, Cursor, Bytes (K), Present);
               if not Present then
                  raise Program_Error with "incomplete decoded UTF-8 in producer rendering";
               end if;
            end loop;
            pragma Assert (Width = 1 or else Code <= 31);
            if Width >= 2 then
               pragma Assert (Code <= 31);
               Code := Code * 64 + Character'Pos (Bytes (2)) mod 64;
            end if;
            if Width >= 3 then
               pragma Assert (Code <= 2_047);
               Code := Code * 64 + Character'Pos (Bytes (3)) mod 64;
            end if;
            if Width = 4 then
               pragma Assert (Code <= 131_071);
               Code := Code * 64 + Character'Pos (Bytes (4)) mod 64;
            end if;
            declare
               Short_Escape : constant Boolean :=
                 Code = Character'Pos (Mark) or else Code in 9 | 10 | 13 | 92;
               Printable : constant Boolean :=
                 not Short_Escape and then Worldline.Producer_Unicode.Printable (Code);
               Piece_Length : constant Positive :=
                 (if Short_Escape then 2
                  elsif Printable then Width
                  elsif Code < 256 then 4
                  elsif Code < 65_536 then 6
                  else 10);
            begin
               if Render then
                  if Code = Character'Pos (Mark) then Put ('\' & Mark);
                  elsif Code = 92 then Put ("\\");
                  elsif Code = 9 then Put ("\t");
                  elsif Code = 10 then Put ("\n");
                  elsif Code = 13 then Put ("\r");
                  elsif Printable then Put (Bytes (1 .. Width));
                  elsif Piece_Length = 4 then Put ("\x" & Hex_Image (Code, 2));
                  elsif Piece_Length = 6 then Put ("\u" & Hex_Image (Code, 4));
                  else Put ("\U" & Hex_Image (Code, 8));
                  end if;
               else
                  if Piece_Length > Natural'Last - Used then
                     raise Constraint_Error with "producer rendering exceeds String extent";
                  end if;
                  Used := Used + Piece_Length;
               end if;
            end;
         end loop;
         Put (String'(1 => Mark));
      end String_Repr;

      procedure Repr (Item : V.Node)
        with Always_Terminates, Pre => Ready,
          Post => Ready and then Used >= Used'Old,
          Subprogram_Variant => (Decreases =>
            (if Item.Form = V.Missing then 0
             else Long_Long_Integer (Data'Length) + 1 -
               Long_Long_Integer (Natural'Min (Item.First, Data'Length))));

      procedure Repr (Item : V.Node) is
      begin
         case Item.Form is
            when V.Missing | V.Null_Value =>
               Put ("None");
            when V.Boolean_Value =>
               Put (if V.Truth (Data, Item) then "True" else "False");
            when V.Integer_Value =>
               Integer_Repr (Item);
            when V.Number_Value =>
               Put (V.Number_Image (Data, Item));
            when V.String_Value =>
               if Item.First = 0 or else Item.First >= Item.Last or else Item.Last > Data'Length then
                  raise Program_Error with "invalid producer string span";
               end if;
               String_Repr (Item);
            when V.Array_Value | V.Object_Value =>
               if Item.First = 0 or else Item.First >= Item.Last or else
                 Item.Last > Data'Length
               then
                  raise Program_Error with "invalid producer container span";
               end if;
               if Item.Form = V.Array_Value then
                  Put ("[");
                  declare
                     Position : Natural := Item.First;
                     Key, Child : V.Node;
                     First : Boolean := True;
                  begin
                     while Position < Item.Last - 1 loop
                        pragma Loop_Invariant (Ready);
                        pragma Loop_Invariant (Position in Item.First .. Item.Last - 1);
                        pragma Loop_Variant (Increases => Position);
                        V.Next_Child (Data, Item, Position, Key, Child);
                        exit when Child.Form = V.Missing;
                        if not First then Put (", "); end if;
                        Repr (Child);
                        First := False;
                     end loop;
                     pragma Unused (Key); -- Array children have no object key.
                  end;
                  Put ("]");
               else
                  Put ("{");
                  declare
                     Index : constant V.Member_Index := V.Members (Data, Item);
                  begin
                     for I in 1 .. Index.Length loop
                        pragma Loop_Invariant (Ready);
                        if I > 1 then Put (", "); end if;
                        String_Repr (Index.Entries (I).Key);
                        Put (": ");
                        Repr (Index.Entries (I).Item);
                     end loop;
                  end;
                  Put ("}");
               end if;
         end case;
      end Repr;
   begin
      Repr (Root);
      if Render and then Used /= Output'Length then
         raise Program_Error with "producer rendering extent mismatch";
      end if;
      Size := Used;
      pragma Assert (Output'Initialized);
   end Scan;

   function Build (Data : String; Root : V.Node) return String is
      Empty : String (1 .. 0);
      Size : Natural;
   begin
      Scan (Data, Root, False, Empty, Size);
      pragma Unused (Empty); -- Sizing has no output elements to consume.
      declare
         Result_Length : constant Natural := Size;
      begin
         return Result : String (1 .. Result_Length) do
            declare
               Written : Natural;
            begin
               Scan (Data, Root, True, Result, Written);
               pragma Assert (Written = Result_Length);
            end;
         end return;
      end;
   end Build;

   function Quote (Text : String) return String is
      Size : constant Natural := Quote_Size (Text);
   begin
      return Result : String (1 .. Size) do
         Write_Quote (Text, Result);
      end return;
   end Quote;

   function Python_String (Value : String) return String is
      Root : constant V.Node := V.Parse (Value);
   begin
      if Root.Form = V.String_Value then return V.Text (Value, Root); end if;
      return Build (Value, Root);
   end Python_String;
end Worldline.Producer_Render;

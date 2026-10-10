with Worldline.Producer_Values;
with Worldline.Producer_Unicode;
package body Worldline.Producer_Render with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   use type V.Value_Kind;
   Hex : constant String := "0123456789abcdef";
   function Hex_Image (Code, Width : Natural) return String is
      Result : String (1 .. Width);
      Remaining : Natural := Code;
   begin
      for I in reverse Result'Range loop
         Result (I) := Hex (Remaining mod 16 + 1);
         Remaining := Remaining / 16;
      end loop;
      return Result;
   end Hex_Image;
   function Escape_JSON (Text : String; I : Natural) return String
     with Subprogram_Variant => (Decreases => Text'Length - Natural'Min (I, Text'Length)) is
   begin
      if I >= Text'Length then return ""; end if;
      declare
         C : constant Character := Text (Text'First + I);
         Piece : constant String :=
           (if C = '"' then "\"""
            elsif C = '\' then "\\"
            elsif C = Character'Val (8) then "\b"
            elsif C = Character'Val (9) then "\t"
            elsif C = Character'Val (10) then "\n"
            elsif C = Character'Val (12) then "\f"
            elsif C = Character'Val (13) then "\r"
            elsif Character'Pos (C) < 32 then "\u00" & Hex_Image (Character'Pos (C), 2)
            else String'(1 => C));
      begin
         return Piece & Escape_JSON (Text, I + 1);
      end;
   end Escape_JSON;
   function Quote (Text : String) return String is
     ('"' & Escape_JSON (Text, 0) & '"');
   function Delimiter (Text : String) return Character is
      Single : Boolean := False;
      Double : Boolean := False;
   begin
      for C of Text loop
         if C = ''' then Single := True; end if;
         if C = '"' then Double := True; end if;
      end loop;
      return (if Single and not Double then '"' else ''');
   end Delimiter;
   function Escape_Repr (Text : String; I : Natural; Mark : Character)
      return String with Subprogram_Variant => (Decreases =>
        Text'Length - Natural'Min (I, Text'Length)) is
      Width : Natural := 1;
      Code : Natural;
   begin
      if I >= Text'Length then return ""; end if;
      Code := Character'Pos (Text (Text'First + I));
      if Code in 16#C2# .. 16#DF# then Code := Code - 16#C0#; Width := 2;
      elsif Code in 16#E0# .. 16#EF# then Code := Code - 16#E0#; Width := 3;
      elsif Code in 16#F0# .. 16#F4# then Code := Code - 16#F0#; Width := 4;
      end if;
      if Width > Text'Length - I then return ""; end if;
      for J in 1 .. Width - 1 loop
         Code := Code * 64 + Character'Pos (Text (Text'First + I + J)) mod 64;
      end loop;
      declare
         Piece : constant String :=
           (if Code = Character'Pos (Mark) then '\' & Mark
            elsif Code = 92 then "\\"
            elsif Code = 9 then "\t"
            elsif Code = 10 then "\n"
            elsif Code = 13 then "\r"
            elsif not Worldline.Producer_Unicode.Printable (Code) then
              (if Code < 256 then "\x" & Hex_Image (Code, 2)
               elsif Code < 65_536 then "\u" & Hex_Image (Code, 4)
               else "\U" & Hex_Image (Code, 8))
            else Text (Text'First + I .. Text'First + I + Width - 1));
      begin
         return Piece & Escape_Repr (Text, I + Width, Mark);
      end;
   end Escape_Repr;
   function Python_Repr (Value : String) return String
     with Subprogram_Variant => (Decreases => Value'Length,
                                Decreases => V.Count (Value) + 1);
   function Sequence (Value : String; I : Natural; Object : Boolean) return String
     with Subprogram_Variant => (Decreases => Value'Length,
       Decreases => V.Count (Value) - Natural'Min (I, V.Count (Value))) is
      Root : constant V.Node := V.Parse (Value);
   begin
      if I >= V.Count (Value) then return ""; end if;
      if Object then
         declare
            Name : constant String := V.Member_Name (Value, Root, I + 1);
         begin
            return Python_Repr (V.Quote (Name)) & ": " &
              Python_Repr (V.Field (Value, Name)) &
              (if I + 1 < V.Count (Value) then ", " else "") & Sequence (Value, I + 1, True);
         end;
      end if;
      return Python_Repr (V.Element (Value, I)) &
        (if I + 1 < V.Count (Value) then ", " else "") & Sequence (Value, I + 1, False);
   end Sequence;
   function Python_Repr (Value : String) return String is
   begin
      if V.Kind (Value) = V.String_Value then
         declare
            Text : constant String := V.Text (Value);
            Mark : constant Character := Delimiter (Text);
         begin
            return Mark & Escape_Repr (Text, 0, Mark) & Mark;
         end;
      end if;
      case V.Kind (Value) is
         when V.Null_Value => return "None";
         when V.Boolean_Value => return (if V.Truth (Value) then "True" else "False");
         when V.Integer_Value | V.Number_Value => return V.Number_Image (Value,V.Parse (Value));
         when V.Array_Value => return "[" & Sequence (Value, 0, False) & "]";
         when V.Object_Value => return "{" & Sequence (Value, 0, True) & "}";
         when V.Missing => return "None";
         when V.String_Value => return "";
      end case;
   end Python_Repr;
   function Python_String (Value : String) return String is
   begin
      if V.Kind (Value) = V.String_Value then return V.Text (Value); end if;
      return Python_Repr (Value);
   end Python_String;
end Worldline.Producer_Render;

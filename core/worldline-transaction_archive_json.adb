with Decimal_Binary64;
with Interfaces;
with SPARK.Big_Integers;
with Worldline.Producer_Render;

package body Worldline.Transaction_Archive_JSON with SPARK_Mode is
   use SPARK.Big_Integers;
   use type E.Count;
   use type E.Value_Kind;
   use type E.Layer;
   use type E.Q.Byte;
   use type Interfaces.Unsigned_64;
   package R renames Worldline.Producer_Render;

   function Payload_Text (Data : E.Bytes; V : E.View) return String is
   begin
      if not E.Bytes_Valid (Data, V.Payload) then return ""; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, V.Payload);
         Text : String (1 .. Raw'Length);
      begin
         for I in Text'Range loop Text (I) := Character'Val (Raw (Raw'First + E.Count (I - 1))); end loop;
         return Text;
      end;
   end Payload_Text;

   function Integer_Text (Data : E.Bytes; V : E.View) return String is
      Value : Big_Integer := To_Big_Integer (0);
      Copy : Big_Integer;
      Size : Natural := 1;
   begin
      if not E.Bytes_Valid (Data, V.Payload) then return ""; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, V.Payload);
      begin
         for B of reverse Raw loop Value := Value * To_Big_Integer (256) + To_Big_Integer (Integer (B)); end loop;
      end;
      Copy := Value;
      while Copy >= To_Big_Integer (10) loop
         pragma Loop_Variant (Decreases => Copy);
         Size := Size + 1;
         Copy := Copy / To_Big_Integer (10);
      end loop;
      declare
         Width : constant Natural := Size + (if V.Sign then 1 else 0);
         Answer : String (1 .. Width) with Relaxed_Initialization;
         First : constant Positive := (if V.Sign then 2 else 1);
      begin
         if V.Sign then Answer (1) := '-'; end if;
         Copy := Value;
         for I in reverse First .. Answer'Last loop
            pragma Loop_Invariant (for all K in Answer'Range => (if K > I then Answer (K)'Initialized));
            pragma Loop_Invariant (if V.Sign then Answer (1)'Initialized);
            Answer (I) := Character'Val (48 + To_Integer (Copy mod To_Big_Integer (10)));
            Copy := Copy / To_Big_Integer (10);
         end loop;
         return Answer;
      end;
   end Integer_Text;

   function Float_Text (Data : E.Bytes; V : E.View) return String is
      Bits : Interfaces.Unsigned_64 := 0;
   begin
      if not E.Bytes_Valid (Data, V.Payload) then return ""; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, V.Payload);
      begin
         if Raw'Length /= 8 then return ""; end if;
         for B of Raw loop Bits := Interfaces.Shift_Left (Bits, 8) or Interfaces.Unsigned_64 (B); end loop;
      end;
      if not Decimal_Binary64.Finite (Bits) then return ""; end if;
      return Decimal_Binary64.Repr (Bits);
   end Float_Text;

   function Binary_Text (Data : E.Bytes; V : E.View) return String is
      Alphabet : constant String := "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
   begin
      if not E.Bytes_Valid (Data, V.Payload) then return ""; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, V.Payload);
         Size : constant E.Count := (Raw'Length / 3) * 4 + (if Raw'Length mod 3 = 0 then 0 else 4);
         Answer : String (1 .. Natural (Size)) := (others => '=');
         Offset : E.Count := 0;
         Cursor : Natural := 1;
         B, C, D : Natural;
      begin
         while Offset < Raw'Length loop
            pragma Loop_Variant (Decreases => Raw'Length - Offset);
            B := Natural (Raw (Raw'First + Offset));
            C := (if Raw'Length - Offset > 1 then Natural (Raw (Raw'First + Offset + 1)) else 0);
            D := (if Raw'Length - Offset > 2 then Natural (Raw (Raw'First + Offset + 2)) else 0);
            Answer (Cursor) := Alphabet (B / 4 + 1);
            Answer (Cursor + 1) := Alphabet ((B mod 4) * 16 + C / 16 + 1);
            if Raw'Length - Offset > 1 then Answer (Cursor + 2) := Alphabet ((C mod 16) * 4 + D / 64 + 1); end if;
            if Raw'Length - Offset > 2 then Answer (Cursor + 3) := Alphabet (D mod 64 + 1); end if;
            if Raw'Length - Offset <= 3 then exit; end if;
            Offset := Offset + 3;
            Cursor := Cursor + 4;
         end loop;
         return "{""encoding"":""base64"",""payload"":""" & Answer & """}";
      end;
   end Binary_Text;

   function Leaf (Data : E.Bytes; V : E.View) return String is
   begin
      case V.Form is
         when E.Null_Value => return "null";
         when E.Boolean_Value => return (if V.Boolean_Bit then "true" else "false");
         when E.Text_Value | E.World_State_Value => return R.Quote (Payload_Text (Data, V));
         when E.Integer_Value => return Integer_Text (Data, V);
         when E.Float_Value => return Float_Text (Data, V);
         when E.Bytes_Value => return Binary_Text (Data, V);
         when others => return "";
      end case;
   end Leaf;

   function Pair_Children (Data : E.Bytes; Pair : E.Span; Layer : E.Layer) return E.Span is
   begin
      if Layer = E.Terminal then return Pair; end if;
      return E.Decode (Data, Pair,
        (if Layer in E.Operation | E.Recovery then E.Finalization else E.Terminal)).Children;
   end Pair_Children;
   function Key_Text (Data : E.Bytes; Key : E.Span; Layer : E.Layer; Record_Key : Boolean) return String is
   begin
      if Layer = E.Terminal then
         if Key.Length < 2 then return ""; end if;
         declare
            V : E.View;
         begin
            V.Form := E.Text_Value;
            V.Payload := ((Key.First + 1, Key.Length - 2), 1);
            return Payload_Text (Data, V);
         end;
      end if;
      return Payload_Text (Data, E.Decode (Data, Key,
        (if Layer in E.Operation | E.Recovery and then not Record_Key then Layer
         elsif Layer in E.Operation | E.Recovery then E.Finalization else E.Terminal)));
   end Key_Text;

   function Omitted (Name : String; Mode : Projection) return Boolean is
     (case Mode is
         when Whole_Value | Root_Set => False,
         when Context_Body => Name = "contextHash",
         when Requirement_Body => Name = "requirementHash",
         when Policy_Body => Name in "sourceSha256" | "warnings" | "sourceObservation",
         when Receipt_Body => Name in "receiptRoot" | "chainHash",
         when Receipt_Id_Body => Name in "receiptId" | "receiptRoot" | "chainHash",
         when Root_Set_Member => Name not in "rootHash" | "rootKey");
   function Child_Mode (Name : String; Mode : Projection) return Projection is
     (if Mode = Requirement_Body and then Name = "policy" then Policy_Body
      elsif Mode = Root_Set then Root_Set_Member else Whole_Value);
   function Output_Name (Name : String; Mode : Projection) return String is
     (if Mode = Root_Set_Member and then Name = "rootHash" then "manifestRoot" else Name);

   function Extent (Data : E.Bytes; Item : E.Span; Layer : E.Layer; Mode : Projection) return E.Count
     with Global => null, Subprogram_Variant => (Decreases => Item.Length);
   function Extent (Data : E.Bytes; Item : E.Span; Layer : E.Layer; Mode : Projection) return E.Count is
      V : constant E.View := E.Decode (Data, Item, Layer);
      N : E.Count;
      Size : E.Count := 2;
      Kept : E.Count := 0;
   begin
      if V.Form not in E.List_Value | E.Tuple_Value | E.Object_Value | E.Record_Value then
         return E.Count (Leaf (Data, V)'Length);
      end if;
      N := E.Array_Length (Data, V.Children);
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               Child : E.Span := E.Array_Element (Data, V.Children, I);
               Pair : E.Span;
               Next : Projection := Child_Mode ("", Mode);
               Keep : Boolean := True;
            begin
               if V.Form in E.Object_Value | E.Record_Value then
                  Pair := Pair_Children (Data, Child, Layer);
                  declare
                     Name : constant String := Key_Text (Data, E.Array_Element (Data, Pair, 0), Layer, V.Form = E.Record_Value);
                  begin
                     Keep := not Omitted (Name, Mode);
                     if Keep then
                        Size := Size + E.Count (R.Quote (Output_Name (Name, Mode))'Length) + 1;
                        Next := Child_Mode (Name, Mode);
                     end if;
                  end;
                  Child := E.Array_Element (Data, Pair, 1);
               end if;
               if Keep then
                  if Kept /= 0 then Size := Size + 1; end if;
                  Kept := Kept + 1;
                  if Child.Length = 0 or else Child.Length >= Item.Length then return 0; end if;
                  declare
                     Child_Size : constant E.Count := Extent (Data, Child, Layer, Next);
                  begin
                     if Child_Size = 0 then return 0; end if;
                     Size := Size + Child_Size;
                  end;
               end if;
            end;
         end loop;
      end if;
      return Size;
   end Extent;

   procedure Emit (Data : E.Bytes; Item : E.Span; Layer : E.Layer; Mode : Projection;
                   Output : in out String; Cursor : in out Natural)
     with Subprogram_Variant => (Decreases => Item.Length);
   procedure Emit (Data : E.Bytes; Item : E.Span; Layer : E.Layer; Mode : Projection;
                   Output : in out String; Cursor : in out Natural)
   is
      V : constant E.View := E.Decode (Data, Item, Layer);
      N : constant Natural := Natural (E.Array_Length (Data, V.Children));
      type Ordinals is array (Positive range <>) of E.Count;
      Order : Ordinals (1 .. N);
      Kept : Natural := 0;
      procedure Put (Text : String) is
      begin
         for Ch of Text loop Cursor := Cursor + 1; Output (Cursor) := Ch; end loop;
      end Put;
      function Name (Ordinal : E.Count) return String is
         Pair : constant E.Span := Pair_Children (Data, E.Array_Element (Data, V.Children, Ordinal), Layer);
      begin
         return Key_Text (Data, E.Array_Element (Data, Pair, 0), Layer, V.Form = E.Record_Value);
      end Name;
      procedure Sift (First, Last : Positive) is
         Root : Positive := First;
         Child : Positive;
         Temp : E.Count;
      begin
         while Root <= Last / 2 loop
            pragma Loop_Variant (Increases => Root);
            Child := Root * 2;
            if Child < Last and then Output_Name (Name (Order (Child)), Mode) < Output_Name (Name (Order (Child + 1)), Mode) then Child := Child + 1; end if;
            if Output_Name (Name (Order (Root)), Mode) >= Output_Name (Name (Order (Child)), Mode) then exit; end if;
            Temp := Order (Root); Order (Root) := Order (Child); Order (Child) := Temp;
            Root := Child;
         end loop;
      end Sift;
   begin
      if V.Form not in E.List_Value | E.Tuple_Value | E.Object_Value | E.Record_Value then
         Put (Leaf (Data, V)); return;
      end if;
      for I in Order'Range loop Order (I) := E.Count (I - 1); end loop;
      if V.Form in E.Object_Value | E.Record_Value and then N > 1 then
         for I in reverse 1 .. N / 2 loop Sift (I, N); end loop;
         for Last in reverse 2 .. N loop
            declare
               Temp : constant E.Count := Order (1);
            begin
               Order (1) := Order (Last); Order (Last) := Temp;
               Sift (1, Last - 1);
            end;
         end loop;
      end if;
      Put ((if V.Form in E.Object_Value | E.Record_Value then "{" else "["));
      for I in Order'Range loop
         declare
            Child : E.Span := E.Array_Element (Data, V.Children, Order (I));
            Pair : E.Span;
            Next : Projection := Child_Mode ("", Mode);
            Keep : Boolean := True;
         begin
            if V.Form in E.Object_Value | E.Record_Value then
               Pair := Pair_Children (Data, Child, Layer);
               declare
                  Key : constant String := Name (Order (I));
               begin
                  Keep := not Omitted (Key, Mode);
                  if Keep then
                     if Kept /= 0 then Put (","); end if;
                     Put (R.Quote (Output_Name (Key, Mode))); Put (":");
                     Next := Child_Mode (Key, Mode);
                  end if;
               end;
               Child := E.Array_Element (Data, Pair, 1);
            elsif Kept /= 0 then Put (",");
            end if;
            if Keep then
               Kept := Kept + 1;
               if Child.Length > 0 and then Child.Length < Item.Length then Emit (Data, Child, Layer, Next, Output, Cursor); end if;
            end if;
         end;
      end loop;
      Put ((if V.Form in E.Object_Value | E.Record_Value then "}" else "]"));
   end Emit;

   function Render (Data : E.Bytes; Encoded : E.Span; Layer : E.Layer := E.Operation;
                    Mode : Projection := Whole_Value) return String is
      Size : constant E.Count := Extent (Data, Encoded, Layer, Mode);
      Result : String (1 .. Natural (Size)) := (others => ' ');
      Cursor : Natural := 0;
   begin
      if Size = 0 then return ""; end if;
      Emit (Data, Encoded, Layer, Mode, Result, Cursor);
      --  The fixed-size result is returned; the final write cursor is local.
      pragma Unused (Cursor);
      return Result;
   end Render;
end Worldline.Transaction_Archive_JSON;

with Worldline.Archive_Base64;
package body Worldline.Custody_V2_Archive_Projection with SPARK_Mode is
   package B renames Worldline.Archive_Base64;
   use type E.Count;
   use type E.Q.Byte;
   use type E.Encoding_Level;
   use type E.Value_Kind;
   function Byte_Length (Data : E.Bytes; Item : E.Byte_View) return E.Count is
   begin
      if Item.Level = 0 then return Item.Encoded.Length; end if;
      declare
         Prior : constant E.Byte_View := (Item.Encoded, Item.Level - 1);
         N : constant E.Count := Byte_Length (Data, Prior);
         Padding : E.Count := 0;
      begin
         if N = 0 or else N < 4 or else N mod 4 /= 0 then return 0; end if;
         if Byte_At (Data, Prior, N - 1) = Character'Pos ('=') then
            Padding := 1;
            if Byte_At (Data, Prior, N - 2) = Character'Pos ('=') then Padding := 2; end if;
         end if;
         return N / 4 * 3 - Padding;
      end;
   end Byte_Length;
   function Byte_At (Data : E.Bytes; Item : E.Byte_View; Offset : E.Count)
      return E.Q.Byte
   is
   begin
      if Item.Level = 0 then
         if not E.C.P.Valid (Data, Item.Encoded) or else Offset >= Item.Encoded.Length then return 0; end if;
         return Data (Item.Encoded.First + Offset);
      end if;
      declare
         Prior : constant E.Byte_View := (Item.Encoded, Item.Level - 1);
         N : constant E.Count := Byte_Length (Data, Prior);
         Group : E.Count;
         X, Y : E.Q.Byte;
      begin
         if Offset >= Byte_Length (Data, Item) then return 0; end if;
         Group := Offset / 3 * 4;
         if Group >= N or else N - Group < 4 then return 0; end if;
         case Offset mod 3 is
            when 0 => X := Byte_At (Data, Prior, Group); Y := Byte_At (Data, Prior, Group + 1);
            when 1 => X := Byte_At (Data, Prior, Group + 1); Y := Byte_At (Data, Prior, Group + 2);
            when others => X := Byte_At (Data, Prior, Group + 2); Y := Byte_At (Data, Prior, Group + 3);
         end case;
         if not B.Is_Digit (X) or else not B.Is_Digit (Y) then return 0; end if;
         case Offset mod 3 is
            when 0 => return B.Digit (X) * 4 + B.Digit (Y) / 16;
            when 1 => return B.Digit (X) mod 16 * 16 + B.Digit (Y) / 4;
            when others => return B.Digit (X) mod 4 * 64 + B.Digit (Y);
         end case;
      end;
   end Byte_At;
   function Borrow_Valid (Data : E.Bytes; Item : E.Byte_View) return Boolean is
   begin
      if Item.Level = 0 then return E.C.P.Valid (Data, Item.Encoded); end if;
      if Item.Level = 1 then return B.Canonical (Data, (Item.Encoded.First, Item.Encoded.Length)); end if;
      declare
         Prior : constant E.Byte_View := (Item.Encoded, Item.Level - 1);
         N : constant E.Count := Byte_Length (Data, Prior);
         Padding : E.Count := 0;
      begin
         if not Borrow_Valid (Data, Prior) then return False; end if;
         if N = 0 then return True; end if;
         if N < 4 or else N mod 4 /= 0 then return False; end if;
         if Byte_At (Data, Prior, N - 1) = Character'Pos ('=') then
            Padding := 1;
            if Byte_At (Data, Prior, N - 2) = Character'Pos ('=') then Padding := 2; end if;
         end if;
         for I in E.Count range 0 .. N - 1 loop
            pragma Loop_Variant (Increases => I);
            if (if I < N - Padding then not B.Is_Digit (Byte_At (Data, Prior, I))
                else Byte_At (Data, Prior, I) /= Character'Pos ('=')) then return False; end if;
         end loop;
         if Padding = 2 then
            return B.Digit (Byte_At (Data, Prior, N - 3)) mod 16 = 0;
         elsif Padding = 1 then
            return B.Digit (Byte_At (Data, Prior, N - 2)) mod 4 = 0;
         end if;
         return True;
      end;
   end Borrow_Valid;
   function Bytes_Equal (Left_Data, Right_Data : E.Bytes; Left, Right : E.Byte_View)
      return Boolean is
     (Borrow_Valid (Left_Data, Left) and then Borrow_Valid (Right_Data, Right) and then
      Byte_Length (Left_Data, Left) = Byte_Length (Right_Data, Right) and then
      (for all I in E.Count range 0 .. Byte_Length (Left_Data, Left) - 1 =>
         Byte_At (Left_Data, Left, I) = Byte_At (Right_Data, Right, I)));
   function Hex_Digit (Value : E.Q.Byte) return E.Q.Byte is
     (if Value <= 9 then Character'Pos ('0') + Value else Character'Pos ('a') + Value - 10);
   function Hex_Matches
     (Hex_Data, Raw_Data : E.Bytes; Hex, Raw : E.Byte_View) return Boolean
   is
      N : constant E.Count := Byte_Length (Hex_Data, Hex);
   begin
      if not Borrow_Valid (Hex_Data, Hex) or else not Borrow_Valid (Raw_Data, Raw) or else
         N mod 2 /= 0 or else N / 2 /= Byte_Length (Raw_Data, Raw) then return False; end if;
      for I in E.Count range 0 .. N / 2 - 1 loop
         pragma Loop_Variant (Increases => I);
         declare
            Value : constant E.Q.Byte := Byte_At (Raw_Data, Raw, I);
         begin
            if Byte_At (Hex_Data, Hex, I * 2) /= Hex_Digit (Value / 16) or else
               Byte_At (Hex_Data, Hex, I * 2 + 1) /= Hex_Digit (Value mod 16) then return False; end if;
         end;
      end loop;
      return True;
   end Hex_Matches;
   function Scoped_Archive_Operation_Matches
     (Scoped_Data, Operation_Data : E.Bytes;
      Scoped_Value, Operation_Value : E.Span;
      Profile : Projection_Profile := Scoped_Tree) return Boolean
   is
      Tagged_View : constant E.View := E.Decode (Scoped_Data, Scoped_Value, E.Operation);
      Original : constant E.View := E.Decode (Operation_Data, Operation_Value, E.Operation);
      Tag : constant E.View := E.Decode (Scoped_Data, S.A.Field (Scoped_Data, Scoped_Value, "type"), E.Operation);
      function Type_Is (Name : String) return Boolean is (E.Text_Is (Scoped_Data, Tag, Name));
      function Scalar (Name : String) return E.View is
        (E.Decode (Scoped_Data, S.A.Field (Scoped_Data, Scoped_Value, Name), E.Operation));
      function Atom (Name : String; Form : E.Value_Kind) return Boolean is
        (Type_Is (Name) and then Scalar ("value").Form = Form and then Original.Form = Form and then
         (case Form is
            when E.Null_Value => True,
            when E.Boolean_Value => Scalar ("value").Boolean_Bit = Original.Boolean_Bit,
            when others => Bytes_Equal (Scoped_Data, Operation_Data, Scalar ("value").Payload, Original.Payload)));
      Fields : E.View;
      Sequence : Boolean := False;
      N : E.Count;
   begin
      if not S.Valid (Scoped_Data, Scoped_Value) or else not S.A.Valid (Operation_Data, Operation_Value) or else
         Tagged_View.Form /= E.Object_Value or else Tag.Form /= E.Text_Value then return False; end if;
      if Profile = Original_Image then
         return Type_Is ("bytes") and then Scalar ("value").Form = E.Text_Value and then
           Hex_Matches (Scoped_Data, Operation_Data, Scalar ("value").Payload, (Operation_Value, 0));
      end if;
      if Profile = Relay_Frame and then (not Type_Is ("dict") or else Original.Form /= E.Object_Value) then return False; end if;
      case Original.Form is
         when E.Invalid => return False;
         when E.Null_Value => return Atom ("NoneType", E.Null_Value);
         when E.Boolean_Value => return Atom ("bool", E.Boolean_Value);
         when E.Text_Value => return Atom ("str", E.Text_Value);
         when E.Bytes_Value =>
            return Type_Is ("bytes") and then Scalar ("value").Form = E.Text_Value and then
              Hex_Matches (Scoped_Data, Operation_Data, Scalar ("value").Payload, Original.Payload);
         when E.Float_Value =>
            return Type_Is ("float") and then Scalar ("bits").Form = E.Text_Value and then
              Byte_Length (Operation_Data, Original.Payload) = 8 and then
              Hex_Matches (Scoped_Data, Operation_Data, Scalar ("bits").Payload, Original.Payload);
         when E.Integer_Value =>
            return Type_Is ("integer") and then Scalar ("negative").Form = E.Boolean_Value and then
              Scalar ("negative").Boolean_Bit = Original.Sign and then Scalar ("magnitude").Form = E.Text_Value and then
              Hex_Matches (Scoped_Data, Operation_Data, Scalar ("magnitude").Payload, Original.Payload);
         when E.World_State_Value =>
            -- No original scoped representation exists; Original_Image above
            -- is the lossless native position profile for this original kind.
            return False;
         when E.List_Value | E.Tuple_Value =>
            if (Original.Form = E.List_Value and then not Type_Is ("list")) or else
               (Original.Form = E.Tuple_Value and then not Type_Is ("tuple")) then return False; end if;
            Fields := Scalar ("items"); Sequence := True;
         when E.Object_Value =>
            if not Type_Is ("dict") then return False; end if;
            Fields := Scalar ("fields");
         when E.Record_Value =>
            if not Bytes_Equal (Scoped_Data, Operation_Data, Tag.Payload, Original.Record_Name) then return False; end if;
            Fields := Scalar ("fields");
      end case;
      if (Sequence and then Fields.Form /= E.List_Value) or else
         (not Sequence and then Fields.Form /= E.Object_Value) then return False; end if;
      N := E.Array_Length (Operation_Data, Original.Children);
      if N /= E.Array_Length (Scoped_Data, Fields.Children) then return False; end if;
      for I in E.Count range 0 .. N - 1 loop
         pragma Loop_Variant (Increases => I);
         declare
            Left_Child : E.Span := E.Array_Element (Scoped_Data, Fields.Children, I);
            Right_Child : E.Span := E.Array_Element (Operation_Data, Original.Children, I);
            Child_Profile : Projection_Profile := Scoped_Tree;
         begin
            if not Sequence then
               declare
                  Left_Pair : constant E.View := E.Decode (Scoped_Data, Left_Child, E.Finalization);
                  Right_Pair : constant E.View := E.Decode (Operation_Data, Right_Child, E.Finalization);
                  Left_Key : constant E.View := E.Decode (Scoped_Data,
                    E.Array_Element (Scoped_Data, Left_Pair.Children, 0), E.Operation);
                  Right_Key : constant E.View := E.Decode (Operation_Data,
                    E.Array_Element (Operation_Data, Right_Pair.Children, 0),
                    (if Original.Form = E.Record_Value then E.Finalization else E.Operation));
               begin
                  if Left_Pair.Form /= E.List_Value or else Right_Pair.Form /= E.List_Value or else
                     E.Array_Length (Scoped_Data, Left_Pair.Children) /= 2 or else
                     E.Array_Length (Operation_Data, Right_Pair.Children) /= 2 or else
                     Left_Key.Form /= Right_Key.Form or else Left_Key.Form not in E.Text_Value | E.Bytes_Value or else
                     not Bytes_Equal (Scoped_Data, Operation_Data, Left_Key.Payload, Right_Key.Payload)
                  then return False; end if;
                  if Profile = Relay_Frame and then E.Text_Is (Operation_Data, Right_Key, "payload") then
                     Child_Profile := Original_Image;
                  end if;
                  Left_Child := E.Array_Element (Scoped_Data, Left_Pair.Children, 1);
                  Right_Child := E.Array_Element (Operation_Data, Right_Pair.Children, 1);
               end;
            end if;
            if Left_Child.Length = 0 or else Left_Child.Length >= Scoped_Value.Length or else
               Right_Child.Length = 0 or else Right_Child.Length >= Operation_Value.Length or else
               not Scoped_Archive_Operation_Matches (Scoped_Data, Operation_Data, Left_Child, Right_Child, Child_Profile)
            then return False; end if;
         end;
      end loop;
      return True;
   end Scoped_Archive_Operation_Matches;
end Worldline.Custody_V2_Archive_Projection;

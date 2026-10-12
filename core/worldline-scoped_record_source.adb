with Worldline.Recovery_Archive;
with Worldline.Archive_Base64;
with Worldline.Retained_Evidence_Replay;
package body Worldline.Scoped_Record_Source with SPARK_Mode is
   package RA renames Worldline.Recovery_Archive;
   package B renames Worldline.Archive_Base64;
   package R renames Worldline.Retained_Evidence_Replay;
   use type E.Value_Kind;
   use type E.Encoding_Level;
   use type E.Q.Byte;
   use type E.Span;

   -- Byte projections through the fixed base64 composition, never a new arena.
   function Size (Data : E.Bytes; V : E.Byte_View) return E.Count
     with Global => null,
       Post => (if V.Level > 0 then Size'Result <= (E.Count'Last / 4) * 3),
       Subprogram_Variant => (Decreases => V.Level, Decreases => 0);
   function Octet (Data : E.Bytes; V : E.Byte_View; I : E.Count) return E.Q.Byte
     with Global => null,
       Subprogram_Variant => (Decreases => V.Level, Decreases => 1);
   function Size (Data : E.Bytes; V : E.Byte_View) return E.Count is
      P : E.Byte_View := V;
      N : E.Count;
   begin
      if V.Level = 0 then return V.Encoded.Length; end if;
      P.Level := P.Level - 1; N := Size (Data, P);
      if N < 4 then return 0; end if;
      return (N / 4) * 3 -
        (if Octet (Data, P, N - 2) = Character'Pos ('=') then 2
         elsif Octet (Data, P, N - 1) = Character'Pos ('=') then 1 else 0);
   end Size;
   function Octet (Data : E.Bytes; V : E.Byte_View; I : E.Count) return E.Q.Byte is
      P : E.Byte_View := V;
      J : E.Count;
      X, Y : E.Q.Byte;
   begin
      if I >= Size (Data, V) then return 0; end if;
      if V.Level = 0 then
         if V.Encoded.First not in Data'Range or else
           I > Data'Last - V.Encoded.First then return 0; end if;
         return Data (V.Encoded.First + I);
      end if;
      P.Level := P.Level - 1; J := (I / 3) * 4 + I mod 3;
      X := Octet (Data, P, J); Y := Octet (Data, P, J + 1);
      if not B.Is_Digit (X) or else not B.Is_Digit (Y) then return 0; end if;
      case I mod 3 is
         when 0 => return B.Digit (X) * 4 + B.Digit (Y) / 16;
         when 1 => return (B.Digit (X) mod 16) * 16 + B.Digit (Y) / 4;
         when others => return (B.Digit (X) mod 4) * 64 + B.Digit (Y);
      end case;
   end Octet;
   function Pair (Data : E.Bytes; V : E.View; I : E.Count) return E.View is
     (E.Decode (Data, E.Array_Element (Data, V.Children, I), E.Finalization));
   function Value (Data : E.Bytes; V : E.View; I : E.Count) return E.Span is
      P : constant E.View := Pair (Data, V, I);
   begin
      if P.Form /= E.List_Value or else E.Array_Length (Data, P.Children) /= 2 then return (1, 0); end if;
      return E.Array_Element (Data, P.Children, 1);
   end Value;
   function Virtual (Data : E.Bytes; Item : E.Span; Wrapped : Boolean) return E.View is
      V : E.View := E.Decode (Data, Item, E.Operation);
      T, P : E.View;
   begin
      if not Wrapped then return V; end if;
      T := E.Decode (Data, Value (Data, V, 0), E.Operation);
      P := E.Decode (Data, Value (Data, V, 1), E.Operation);
      if E.Text_Is (Data, T, "dict") then V.Form := E.Object_Value; V.Children := P.Children;
      elsif E.Text_Is (Data, T, "list") then V.Form := E.List_Value; V.Children := P.Children;
      elsif E.Text_Is (Data, T, "str") or else E.Text_Is (Data, T, "bool") or else
        E.Text_Is (Data, T, "NoneType") then V := P;
      else V.Form := E.Invalid;
      end if;
      return V;
   end Virtual;
   function Field (Data : E.Bytes; V : E.View; Name : String) return E.Span is
      N : constant E.Count := E.Array_Length (Data, V.Children);
   begin
      if V.Form /= E.Object_Value then return (1, 0); end if;
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               P : constant E.View := Pair (Data, V, I);
            begin
               if E.Text_Is (Data, E.Decode (Data, E.Array_Element (Data, P.Children, 0), E.Operation), Name)
               then return Value (Data, V, I); end if;
            end;
         end loop;
      end if;
      return (1, 0);
   end Field;
   function Hex (Data : E.Bytes; V : E.View) return Boolean is
      N : E.Count;
      C : E.Q.Byte;
   begin
      if V.Form /= E.Text_Value or else not E.Bytes_Valid (Data, V.Payload) then return False; end if;
      N := Size (Data, V.Payload);
      if N mod 2 /= 0 then return False; end if;
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            C := Octet (Data, V.Payload, I);
            if C not in Character'Pos ('0') .. Character'Pos ('9') and then
               C not in Character'Pos ('a') .. Character'Pos ('f') then return False; end if;
         end loop;
      end if;
      return True;
   end Hex;
   type Source_View is record
      V : E.View;
      Hexadecimal : Boolean := False;
      Good : Boolean := False;
   end record;
   function Restored (Data : E.Bytes; Item : E.Span; Wrapped : Boolean) return Source_View
     with Global => null
   is
      V : constant E.View := Virtual (Data, Item, Wrapped);
      T : constant E.View := Virtual (Data, Field (Data, V, "type"), Wrapped);
      P : E.View;
      R : Source_View;
      N : constant E.Count := E.Array_Length (Data, V.Children);
      function F (Name : String) return E.View is
        (Virtual (Data, Field (Data, V, Name), Wrapped));
   begin
      if V.Form /= E.Object_Value or else T.Form /= E.Text_Value then return R; end if;
      R.V := V;
      if E.Text_Is (Data, T, "integer") then
         P := F ("magnitude");
         if N /= 3 or else F ("negative").Form /= E.Boolean_Value or else not Hex (Data, P) then return R; end if;
         R.V.Form := E.Integer_Value; R.V.Sign := F ("negative").Boolean_Bit;
         R.V.Payload := P.Payload; R.Hexadecimal := True;
      else
         if N /= 2 then return R; end if;
         if E.Text_Is (Data, T, "bytes") or else E.Text_Is (Data, T, "float") then
            P := F ((if E.Text_Is (Data, T, "bytes") then "value" else "bits"));
            if not Hex (Data, P) then return R; end if;
            R.V.Form := (if E.Text_Is (Data, T, "bytes") then E.Bytes_Value else E.Float_Value);
            if R.V.Form = E.Float_Value and then Size (Data, P.Payload) /= 16 then return R; end if;
            R.V.Payload := P.Payload; R.Hexadecimal := True;
         elsif E.Text_Is (Data, T, "str") or else E.Text_Is (Data, T, "bool") or else E.Text_Is (Data, T, "NoneType") then
            P := F ("value");
            if (E.Text_Is (Data, T, "str") and then P.Form /= E.Text_Value) or else
              (E.Text_Is (Data, T, "bool") and then P.Form /= E.Boolean_Value) or else
              (E.Text_Is (Data, T, "NoneType") and then P.Form /= E.Null_Value) then return R; end if;
            R.V := P;
         elsif E.Text_Is (Data, T, "tuple") or else E.Text_Is (Data, T, "list") then
            P := F ("items"); if P.Form /= E.List_Value then return R; end if;
            R.V.Form := (if E.Text_Is (Data, T, "tuple") then E.Tuple_Value else E.List_Value);
            R.V.Children := P.Children;
         else
            P := F ("fields"); if P.Form /= E.Object_Value then return R; end if;
            R.V.Form := (if E.Text_Is (Data, T, "dict") then E.Object_Value else E.Record_Value);
            R.V.Record_Name := T.Payload; R.V.Children := P.Children;
         end if;
      end if;
      R.V.Raw := Item; R.V.At_Layer := E.Operation;
      R.Good := True; return R;
   end Restored;
   function Byte_Length (Data : E.Bytes; S : Source_View) return E.Count is
     (Size (Data, S.V.Payload) / (if S.Hexadecimal then 2 else 1));
   function Byte_At (Data : E.Bytes; S : Source_View; I : E.Count) return E.Q.Byte is
      function Digit (C : E.Q.Byte) return E.Q.Byte is
        (if C <= Character'Pos ('9') then C - Character'Pos ('0') else C - Character'Pos ('a') + 10);
   begin
      if S.Hexadecimal then return Digit (Octet (Data, S.V.Payload, 2 * I)) * 16 + Digit (Octet (Data, S.V.Payload, 2 * I + 1)); end if;
      return Octet (Data, S.V.Payload, I);
   end Byte_At;
   function Scoped_Record_Value_Matches
     (Data : E.Bytes; Encoded, Typed : E.Span;
      Carrier_Scoped, Typed_Scoped : Boolean := False) return Boolean is
   begin
      -- The inner original restore is not the enclosing codec roundtrip:
      -- padded integer magnitudes and negative zero are legal here.
      return RA.Restored_Source_Value_Matches
        (Data, Data, Encoded, Typed,
         (if Carrier_Scoped then 2 else 1), Typed_Scoped);
   end Scoped_Record_Value_Matches;
   function Source_Record_Value_Matches
     (Data : E.Bytes; Encoded, Typed : E.Span;
      Carrier_Scoped, Typed_Scoped : Boolean := False) return Boolean is
      Wrapper : Source_View;
      Schema, Image : Source_View;
      Schema_Span, Image_Span : E.Span;
   begin
      if not RA.Source_Valid (Data, Encoded, Carrier_Scoped) or else
        not RA.Source_Valid (Data, Typed, Typed_Scoped) then return False; end if;
      Wrapper := Restored (Data, Encoded, Carrier_Scoped);
      if not Wrapper.Good or else Wrapper.V.Form /= E.Object_Value then
         return Scoped_Record_Value_Matches
           (Data, Encoded, Typed, Carrier_Scoped, Typed_Scoped);
      end if;
      Schema_Span := Field (Data, Wrapper.V, "schema");
      Schema := Restored (Data, Schema_Span, Carrier_Scoped);
      if not Schema.Good or else
        not E.Text_Is (Data, Schema.V, "worldline.scoped-source-image-v1") then
         return Scoped_Record_Value_Matches
           (Data, Encoded, Typed, Carrier_Scoped, Typed_Scoped);
      end if;
      -- Only the original explicitly declared image schema selects this seam.
      if E.Array_Length (Data, Wrapper.V.Children) /= 2 then return False; end if;
      Image_Span := Field (Data, Wrapper.V, "image");
      Image := Restored (Data, Image_Span, Carrier_Scoped);
      if not Image.Good or else Image.V.Form /= E.Bytes_Value then return False; end if;
      if not Carrier_Scoped and then RA.Source_Valid (Data, Image_Span, True) then
         return R.Archive_Image_Matches
           (Data, Image_Span, Typed, False, Typed_Scoped, True);
      end if;
      -- The parser consumes an actual byte arena, not a hex/base64 Byte_View.
      -- One full-size decoded image is therefore necessary at this seam.
      -- No fixed cap, partial parse, header/digest trust or second encoding.
      declare
         Actual_Length : constant E.Count := Byte_Length (Data, Image);
         Actual : E.Bytes (1 .. Actual_Length) with Relaxed_Initialization;
      begin
         for I in Actual'Range loop
            pragma Loop_Invariant (for all K in Actual'First .. I - 1 => Actual (K)'Initialized);
            Actual (I) := Byte_At (Data, Image, I - Actual'First);
         end loop;
         return RA.Ordered_Source_Value_Matches
           (Actual, Data, (Actual'First, Actual'Length), Typed, False, Typed_Scoped);
      end;
   end Source_Record_Value_Matches;
end Worldline.Scoped_Record_Source;

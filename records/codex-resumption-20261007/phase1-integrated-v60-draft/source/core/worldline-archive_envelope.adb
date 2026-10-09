package body Worldline.Archive_Envelope with SPARK_Mode is
   package B renames Archive_Base64;
   package T renames Archive_Text;
   use type Q.Byte;
   use type C.Kind;
   use type C.Node;

   function Bytes_Valid (Data : Bytes; Item : Byte_View) return Boolean is
   begin
      if Item.Level = 0 then
         return C.P.Valid (Data, Item.Encoded);
      end if;
      declare
         Prior : constant Byte_View := (Item.Encoded, Item.Level - 1);
      begin
         if not Bytes_Valid (Data, Prior) then return False; end if;
         declare
            Raw : constant Bytes := Materialize (Data, Prior);
         begin
            return B.Canonical (Raw, (Raw'First, Raw'Length));
         end;
      end;
   end Bytes_Valid;

   function Materialize (Data : Bytes; Item : Byte_View) return Bytes is
   begin
      if Item.Level = 0 then
         if Item.Encoded.Length = 0 then return (1 .. 0 => 0); end if;
         return Data (Item.Encoded.First ..
                      Item.Encoded.First + (Item.Encoded.Length - 1));
      end if;
      declare
         Raw : constant Bytes := Materialize
           (Data, (Item.Encoded, Item.Level - 1));
         S : constant B.Span := (Raw'First, Raw'Length);
         Result : Bytes (1 .. B.Decoded_Length (Raw, S));
      begin
         B.Decode (Raw, S, Result);
         return Result;
      end;
   end Materialize;

   function Is_Array (Data : Bytes; Item : Span) return Boolean is
      N : constant C.Node := C.Prefix (Data, Item, 0);
   begin
      return N.Valid and then N.Form = C.Array_Value
        and then N.After = Item.Length;
   end Is_Array;

   function Array_Length (Data : Bytes; Sequence : Span) return Count is
      Offset : Count := 1;
      Found : Count := 0;
      N : C.Node;
   begin
      if not Is_Array (Data, Sequence) or else Sequence.Length < 2 then return 0; end if;
      while Offset < Sequence.Length - 1 loop
         pragma Loop_Invariant (Offset in 1 .. Sequence.Length);
         pragma Loop_Invariant (Found < Offset);
         pragma Loop_Variant (Decreases => Sequence.Length - Offset);
         N := C.Prefix (Data, Sequence, Offset);
         if not N.Valid then return 0; end if;
         Found := Found + 1;
         Offset := N.After;
         if Offset < Sequence.Length - 1 then Offset := Offset + 1; end if;
      end loop;
      return Found;
   end Array_Length;

   function Array_Element (Data : Bytes; Sequence : Span; Ordinal : Count)
      return Span
   is
      Offset : Count := 1;
      Found : Count := 0;
      N : C.Node;
   begin
      if not Is_Array (Data, Sequence) or else Sequence.Length < 2 then return (1, 0); end if;
      while Offset < Sequence.Length - 1 loop
         pragma Loop_Invariant (Offset in 1 .. Sequence.Length);
         pragma Loop_Invariant (Found < Offset);
         pragma Loop_Variant (Decreases => Sequence.Length - Offset);
         N := C.Prefix (Data, Sequence, Offset);
         if not N.Valid then return (1, 0); end if;
         if Found = Ordinal then return C.Part (Sequence, N.First, N.After); end if;
         Found := Found + 1;
         Offset := N.After;
         if Offset < Sequence.Length - 1 then Offset := Offset + 1; end if;
      end loop;
      return (1, 0);
   end Array_Element;

   function Text_Is (Data : Bytes; Item : View; Text : String) return Boolean is
   begin
      if Item.Form /= Text_Value or else not Bytes_Valid (Data, Item.Payload) then
         return False;
      end if;
      declare
         Raw : constant Bytes := Materialize (Data, Item.Payload);
      begin
         return Raw'Length = Text'Length and then
           (for all I in Text'Range =>
              Raw (Raw'First + Count (I - Text'First)) = Character'Pos (Text (I)));
      end;
   end Text_Is;

   function Literal (Data : Bytes; Item : Span; Text : String) return Boolean is
     (C.P.Valid (Data, Item) and then Item.Length = Text'Length and then
       (for all I in Text'Range =>
          Data (Item.First + Count (I - Text'First)) = Character'Pos (Text (I))));

   function String_Payload (Data : Bytes; Item : Span) return Span is
      N : constant C.Node := C.Prefix (Data, Item, 0);
   begin
      if not N.Valid or else N.Form /= C.String_Value or else
        N.After /= Item.Length or else Item.Length < 2 then return (1, 0); end if;
      --  Base64 payloads contain no JSON escapes, quote or non-ASCII byte.
      --  Canonical base64 validation below rejects such raw inner characters.
      return C.Part (Item, 1, Item.Length - 1);
   end String_Payload;

   function Terminal_Tag (Data : Bytes; Item : Span; Text : String) return Boolean is
      N : constant C.Node := C.Prefix (Data, Item, 0);
   begin
      return N.Valid and then N.After = Item.Length and then
        C.String_Is (Data, Item, N, Text);
   end Terminal_Tag;

   function Decode (Data : Bytes; Encoded : Span; At_Layer : Layer) return View is
      Failure : constant View :=
        (Raw => Encoded, At_Layer => At_Layer, others => <>);
      Result : View := Failure;
      Sequence : Span := Encoded;
      Tag, Value, Extra : Span;
      Header_Count : Count;
      Tag_View, Value_View, Extra_View : View;
      Lower : Layer := Terminal;
      function Has_Tag (Name : String) return Boolean is
        (if At_Layer = Terminal then Terminal_Tag (Data, Tag, Name)
         else Text_Is (Data, Tag_View, Name));
   begin
      if At_Layer /= Terminal then
         Lower := (if At_Layer in Recovery | Finalization_Record then Finalization
                   else Layer'Pred (At_Layer));
         Value_View := Decode (Data, Encoded, Lower);
         if Value_View.Form /= List_Value then return Failure; end if;
         Sequence := Value_View.Children;
      end if;
      if not Is_Array (Data, Sequence) then return Failure; end if;
      Header_Count := Array_Length (Data, Sequence);
      Tag := Array_Element (Data, Sequence, 0);
      Value := Array_Element (Data, Sequence, 1);
      Extra := Array_Element (Data, Sequence, 2);
      if At_Layer /= Terminal then
         Tag_View := Decode (Data, Tag, Lower);
         Value_View := Decode (Data, Value, Lower);
         Extra_View := Decode (Data, Extra, Lower);
      end if;
      if At_Layer = Terminal then
         if Has_Tag ("null") and then Header_Count = 1 then
            Result.Form := Null_Value;
         elsif Has_Tag ("bool") and then Header_Count = 2 and then
           (Literal (Data, Value, "true") or else Literal (Data, Value, "false")) then
            Result.Form := Boolean_Value;
            Result.Boolean_Bit := Literal (Data, Value, "true");
         elsif (Has_Tag ("str") or else Has_Tag ("float")) and then Header_Count = 2 then
            declare
               N : constant C.Node := C.Prefix (Data, Value, 0);
            begin
               if not N.Valid or else N.Form /= C.String_Value or else N.After /= Value.Length then
                  return Failure;
               end if;
            end;
            Result.Payload := (String_Payload (Data, Value), 1);
            if not Bytes_Valid (Data, Result.Payload) then return Failure; end if;
            declare
               Raw : constant Bytes := Materialize (Data, Result.Payload);
            begin
               if Has_Tag ("str") then
                  if not T.Text_Valid (Raw, (Raw'First, Raw'Length)) then return Failure; end if;
                  Result.Form := Text_Value;
               else
                  --  Exact existing struct.pack('!d') payload, no rounding,
                  --  nonfinite filtering, NaN normalization or sign loss.
                  if Raw'Length /= 8 then return Failure; end if;
                  Result.Form := Float_Value;
               end if;
            end;
         elsif Has_Tag ("int") and then Header_Count = 3 then
            if not (Literal (Data, Value, "true") or else Literal (Data, Value, "false")) then
               return Failure;
            end if;
            declare
               N : constant C.Node := C.Prefix (Data, Extra, 0);
            begin
               if not N.Valid or else N.Form /= C.String_Value or else N.After /= Extra.Length then
                  return Failure;
               end if;
            end;
            Result.Sign := Literal (Data, Value, "true");
            Result.Payload := (String_Payload (Data, Extra), 1);
            if not Bytes_Valid (Data, Result.Payload) then return Failure; end if;
            declare
               Raw : constant Bytes := Materialize (Data, Result.Payload);
            begin
               if (Raw'Length = 0 and then Result.Sign) or else
                 (Raw'Length > 0 and then Raw (Raw'Last) = 0) then return Failure; end if;
            end;
            Result.Form := Integer_Value;
         elsif (Has_Tag ("array") or else Has_Tag ("object")) and then
           Header_Count = 2 and then Is_Array (Data, Value) then
            Result.Form := (if Has_Tag ("array") then List_Value else Object_Value);
            Result.Children := Value;
         else return Failure;
         end if;
      elsif At_Layer = Finalization then
         if Header_Count /= 2 then return Failure; end if;
         if Has_Tag ("scalar") and then Value_View.Form in
           Null_Value | Boolean_Value | Integer_Value | Float_Value | Text_Value then
            Result := Value_View;
         elsif Has_Tag ("bytes") and then Value_View.Form = Text_Value then
            Result.Payload := Value_View.Payload;
            if Result.Payload.Level = Encoding_Level'Last then return Failure; end if;
            Result.Payload.Level := Result.Payload.Level + 1;
            if not Bytes_Valid (Data, Result.Payload) then return Failure; end if;
            Result.Form := Bytes_Value;
         elsif (Has_Tag ("list") or else Has_Tag ("tuple") or else Has_Tag ("object"))
           and then Value_View.Form = List_Value then
            Result.Form := (if Has_Tag ("list") then List_Value
                            elsif Has_Tag ("tuple") then Tuple_Value else Object_Value);
            Result.Children := Value_View.Children;
         else return Failure;
         end if;
      elsif At_Layer = Finalization_Record then
         if Has_Tag ("atom") and then Header_Count = 2 and then
           Value_View.Form in Null_Value | Boolean_Value | Integer_Value |
             Float_Value | Text_Value | Bytes_Value then
            Result := Value_View;
         elsif (Has_Tag ("list") or else Has_Tag ("tuple") or else Has_Tag ("object"))
           and then Header_Count = 2 and then Value_View.Form = List_Value then
            Result.Form := (if Has_Tag ("list") then List_Value
                            elsif Has_Tag ("tuple") then Tuple_Value else Object_Value);
            Result.Children := Value_View.Children;
         elsif Has_Tag ("record") and then Header_Count = 3 and then
           Value_View.Form = Text_Value and then Extra_View.Form = List_Value then
            Result.Record_Name := Value_View.Payload;
            Result.Children := Extra_View.Children;
            Result.Form := Record_Value;
         else return Failure;
         end if;
      else
         if Has_Tag ("atom") and then Header_Count = 2 and then
           (Value_View.Form in
              Null_Value | Boolean_Value | Float_Value | Text_Value | Bytes_Value
            or else (At_Layer = Recovery and then Value_View.Form = Integer_Value)) then
            Result := Value_View;
         elsif At_Layer = Operation and then Has_Tag ("integer-magnitude") and then
           Header_Count = 3 and then Value_View.Form = Boolean_Value and then
           Extra_View.Form = Bytes_Value then
            Result.Sign := Value_View.Boolean_Bit;
            Result.Payload := Extra_View.Payload;
            declare
               Raw : constant Bytes := Materialize (Data, Result.Payload);
            begin
               if (Raw'Length = 0 and then Result.Sign) or else
                 (Raw'Length > 0 and then Raw (Raw'Last) = 0) then return Failure; end if;
            end;
            Result.Form := Integer_Value;
         elsif Has_Tag ("world-state") and then Header_Count = 2 and then Value_View.Form = Text_Value then
            Result.Form := World_State_Value;
            Result.Payload := Value_View.Payload;
         elsif (Has_Tag ("list") or else Has_Tag ("tuple") or else Has_Tag ("object")) and then
           Header_Count = 2 and then Value_View.Form = List_Value then
            Result.Form := (if Has_Tag ("list") then List_Value
                            elsif Has_Tag ("tuple") then Tuple_Value else Object_Value);
            Result.Children := Value_View.Children;
         elsif Has_Tag ("record") and then Header_Count = 4 and then
           Value_View.Form = Text_Value and then Extra_View.Form = Text_Value then
            Result.Module_Name := Value_View.Payload;
            Result.Record_Name := Extra_View.Payload;
            declare
               Fields : constant View := Decode
                 (Data, Array_Element (Data, Sequence, 3), Lower);
            begin
               if Fields.Form /= List_Value then return Failure; end if;
               Result.Children := Fields.Children;
               Result.Form := Record_Value;
            end;
         else return Failure;
         end if;
      end if;
      Result.Raw := Encoded;
      Result.At_Layer := At_Layer;
      return Result;
   end Decode;
end Worldline.Archive_Envelope;

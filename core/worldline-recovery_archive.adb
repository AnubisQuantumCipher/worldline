with Interfaces;
with Decimal_Binary64;
with SPARK.Big_Integers;
with Worldline.Operation_Archive;
with System;
with Worldline.Evaluation_Wire;
with Worldline.Scoped_Archive;
with Worldline.Custody_V2_Archive_Projection;
package body Worldline.Recovery_Archive with SPARK_Mode is
   package AP renames Worldline.Custody_V2_Archive_Projection;
   use type E.Value_Kind;
   use type E.Bytes;
   use type E.Q.Byte;
   use type E.Layer;
   function Text_Is (Data : E.Bytes; Encoded : E.Span; Text : String) return Boolean is
      V : constant E.View := E.Decode (Data, Encoded, E.Recovery);
   begin
      -- WorldState is the original StrEnum: category lookup accepts its full
      -- textual value, while the archive still preserves the explicit tag.
      return E.Text_Is (Data,
        (if V.Form = E.World_State_Value then (V with delta Form => E.Text_Value) else V), Text);
   end Text_Is;
   function Boolean_Is (Data : E.Bytes; Encoded : E.Span; Value : Boolean) return Boolean is
      V : constant E.View := E.Decode (Data, Encoded, E.Recovery);
   begin
      return V.Form = E.Boolean_Value and then V.Boolean_Bit = Value;
   end Boolean_Is;
   function Stored_Bytes_Valid (Data : E.Bytes; Encoded : E.Span) return Boolean is
      V : constant E.View := E.Decode (Data, Encoded, E.Recovery);
   begin
      return V.Form = E.Bytes_Value and then E.Bytes_Valid (Data, V.Payload);
   end Stored_Bytes_Valid;
   function Stored_Bytes (Data : E.Bytes; Encoded : E.Span) return E.Bytes is
     (E.Materialize (Data, E.Decode (Data, Encoded, E.Recovery).Payload));
   function Integer_Valid (Data : E.Bytes; Encoded : E.Span) return Boolean is
      V : constant E.View := E.Decode (Data, Encoded, E.Recovery);
   begin
      return V.Form = E.Integer_Value and then E.Bytes_Valid (Data, V.Payload);
   end Integer_Valid;
   function Integer_Negative (Data : E.Bytes; Encoded : E.Span) return Boolean is
      V : constant E.View := E.Decode (Data, Encoded, E.Recovery);
   begin
      return V.Form = E.Integer_Value and then V.Sign;
   end Integer_Negative;
   function Integer_Magnitude (Data : E.Bytes; Encoded : E.Span) return E.Bytes is
     (E.Materialize (Data, E.Decode (Data, Encoded, E.Recovery).Payload));
   function Pair (Data : E.Bytes; Item : E.View; Ordinal : E.Count) return E.View is
     (E.Decode (Data, E.Array_Element (Data, Item.Children, Ordinal), E.Finalization));
   function Payload_Is (Data : E.Bytes; Payload : E.Byte_View; Text : String) return Boolean is
   begin
      if not E.Bytes_Valid (Data, Payload) then return False; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, Payload);
      begin
         return Raw'Length = Text'Length and then
           (for all I in Text'Range =>
              Raw (Raw'First + E.Count (I - Text'First)) = Character'Pos (Text (I)));
      end;
   end Payload_Is;
   function Record_Is
     (Data : E.Bytes; Encoded : E.Span; Module_Name, Record_Name : String)
      return Boolean
   is
      Item : constant E.View := E.Decode (Data, Encoded, E.Recovery);
   begin
      return Item.Form = E.Record_Value and then
        Payload_Is (Data, Item.Module_Name, Module_Name) and then
        Payload_Is (Data, Item.Record_Name, Record_Name);
   end Record_Is;
   function Same_Key (Data : E.Bytes; L, R : E.View) return Boolean is
     (L.Form = R.Form and then L.Form in E.Text_Value | E.Bytes_Value
      and then E.Bytes_Valid (Data, L.Payload) and then E.Bytes_Valid (Data, R.Payload)
      and then E.Materialize (Data, L.Payload) = E.Materialize (Data, R.Payload));
   function Finalization_Class (Data : E.Bytes; Item : E.View; Name : String)
      return Boolean is
     (Item.Form = E.Record_Value and then Payload_Is (Data, Item.Record_Name, Name));
   function Finalization_Module_Is
     (Data : E.Bytes; Item : E.View; Other_Data : E.Bytes; Module_Name : E.Byte_View)
      return Boolean is
     (Payload_Is (Other_Data, Module_Name,
        (if Finalization_Class (Data, Item, "OwnedRecord") then "worldline.evaluation_wire"
         else "worldline.finalization_values")));
   function Finalization_Field_Roster
     (Data : E.Bytes; Item : E.View; Roster : String) return Boolean
   is
      First : Positive := Roster'First;
      Ordinal : E.Count := 0;
   begin
      for Last in Roster'Range loop
         if Roster (Last) = '|' or else Last = Roster'Last then
            declare
               Finish : constant Integer := (if Roster (Last) = '|' then Last - 1 else Last);
               P : constant E.View := Pair (Data, Item, Ordinal);
               Key : constant E.View := E.Decode
                 (Data, E.Array_Element (Data, P.Children, 0), E.Finalization);
            begin
               if P.Form /= E.List_Value or else E.Array_Length (Data, P.Children) /= 2
                 or else not E.Text_Is (Data, Key, Roster (First .. Finish))
               then return False; end if;
            end;
            Ordinal := Ordinal + 1;
            if Last < Roster'Last then First := Last + 1; end if;
         end if;
      end loop;
      return E.Array_Length (Data, Item.Children) = Ordinal;
   end Finalization_Field_Roster;
   function Finalization_Record_Fields (Data : E.Bytes; Item : E.View) return Boolean is
   begin
      -- Exact original nine-class projection of Operation_Archive.Record_Fields.
      -- There is no module byte in the original three-item finalization grammar.
      if Finalization_Class (Data, Item, "StartValue") then
         return Finalization_Field_Roster (Data, Item,
           "store_id|subject|run|epoch|requirement|policy|verifier_plan|base_context|parent|config|repository|required|declaration");
      elsif Finalization_Class (Data, Item, "InputValue") then
         return Finalization_Field_Roster (Data, Item, "start|root|manifests|filesystem|config|repository");
      elsif Finalization_Class (Data, Item, "UnsealedResult") then
         return Finalization_Field_Roster (Data, Item,
           "start|check|source|execution|verifier|state|outcome|payload|declared|wire");
      elsif Finalization_Class (Data, Item, "CaptureValue") then
         return Finalization_Field_Roster (Data, Item,
           "start|input|post_root|post_manifests|context|source|results|completion");
      elsif Finalization_Class (Data, Item, "ComponentsValue") then
         return Finalization_Field_Roster (Data, Item, "environment|evidence");
      elsif Finalization_Class (Data, Item, "SealValue") then
         return Finalization_Field_Roster (Data, Item, "capture|content|components|evidence|environment");
      elsif Finalization_Class (Data, Item, "ClassifiedValue") then
         return Finalization_Field_Roster (Data, Item, "state|outcome|promotion");
      elsif Finalization_Class (Data, Item, "SealedValue") then
         return Finalization_Field_Roster (Data, Item,
           "value|identity|classification|finalization_state|finalization_outcome");
      elsif Finalization_Class (Data, Item, "OwnedRecord") then
         if not Finalization_Field_Roster (Data, Item, "raw|confinement") then return False; end if;
         declare
            Raw_Pair : constant E.View := Pair (Data, Item, 0);
            Conf_Pair : constant E.View := Pair (Data, Item, 1);
            Raw : constant E.View := E.Decode
              (Data, E.Array_Element (Data, Raw_Pair.Children, 1), E.Finalization_Record);
            Conf : constant E.View := E.Decode
              (Data, E.Array_Element (Data, Conf_Pair.Children, 1), E.Finalization_Record);
         begin
            if Raw.Form /= E.Bytes_Value or else Conf.Form /= E.Integer_Value
              or else Conf.Sign then return False; end if;
            declare
               Raw_Bytes : constant E.Bytes := E.Materialize (Data, Raw.Payload);
               Conf_Bytes : constant E.Bytes := E.Materialize (Data, Conf.Payload);
            begin
               return Raw_Bytes'Length = Worldline.Evaluation_Wire.Raw_Record'Size / System.Storage_Unit
                 and then (Conf_Bytes'Length = 0 or else
                   (Conf_Bytes'Length = 1 and then Conf_Bytes (Conf_Bytes'First) in 1 .. 2));
            end;
         end;
      end if;
      return False;
   end Finalization_Record_Fields;
   function Valid_Finalization_Record (Data : E.Bytes; Encoded : E.Span) return Boolean is
      Item : constant E.View := E.Decode (Data, Encoded, E.Finalization_Record);
      N : E.Count;
      Child : E.Span;
   begin
      case Item.Form is
         when E.Null_Value | E.Boolean_Value | E.Integer_Value | E.Float_Value |
              E.Text_Value | E.Bytes_Value => return True;
         when E.Record_Value =>
            if not Finalization_Record_Fields (Data, Item) then return False; end if;
         when E.List_Value | E.Tuple_Value | E.Object_Value => null;
         when others => return False;
      end case;
      N := E.Array_Length (Data, Item.Children);
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            if Item.Form in E.List_Value | E.Tuple_Value then
               Child := E.Array_Element (Data, Item.Children, I);
            else
               declare
                  P : constant E.View := Pair (Data, Item, I);
                  Key : constant E.View := E.Decode
                    (Data, E.Array_Element (Data, P.Children, 0), E.Finalization);
               begin
                  if P.Form /= E.List_Value or else E.Array_Length (Data, P.Children) /= 2
                    or else Key.Form /= E.Text_Value then return False; end if;
                  if Item.Form = E.Object_Value and then I > 0 then
                     for J in E.Count range 0 .. I - 1 loop
                        declare
                           Earlier : constant E.View := Pair (Data, Item, J);
                           Other : constant E.View := E.Decode
                             (Data, E.Array_Element (Data, Earlier.Children, 0), E.Finalization);
                        begin
                           if Same_Key (Data, Key, Other) then return False; end if;
                        end;
                     end loop;
                  end if;
                  Child := E.Array_Element (Data, P.Children, 1);
               end;
            end if;
            if Child.Length = 0 or else Child.Length >= Encoded.Length or else
              not Valid_Finalization_Record (Data, Child) then return False; end if;
         end loop;
      end if;
      return True;
   end Valid_Finalization_Record;
   function Finalization_Record_Field
     (Data : E.Bytes; Encoded : E.Span; Name : String) return E.Span
   is
      Item : constant E.View := E.Decode (Data, Encoded, E.Finalization_Record);
      N : E.Count;
   begin
      if not Valid_Finalization_Record (Data, Encoded) or else
        Item.Form not in E.Record_Value | E.Object_Value then return (1, 0); end if;
      N := E.Array_Length (Data, Item.Children);
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               P : constant E.View := Pair (Data, Item, I);
            begin
               if E.Text_Is (Data, E.Decode
                 (Data, E.Array_Element (Data, P.Children, 0), E.Finalization), Name)
               then return E.Array_Element (Data, P.Children, 1); end if;
            end;
         end loop;
      end if;
      return (1, 0);
   end Finalization_Record_Field;
   function Valid (Data : E.Bytes; Encoded : E.Span) return Boolean is
      Item : constant E.View := E.Decode (Data, Encoded, E.Recovery);
      N : E.Count;
      Child : E.Span;
   begin
      case Item.Form is
         when E.Invalid => return False;
         when E.Null_Value | E.Boolean_Value | E.Integer_Value | E.Float_Value |
              E.Text_Value | E.Bytes_Value => return True;
         when E.World_State_Value =>
            return Payload_Is (Data, Item.Payload, "MUTABLE") or else
              Payload_Is (Data, Item.Payload, "FINALIZING") or else
              Payload_Is (Data, Item.Payload, "VALID") or else
              Payload_Is (Data, Item.Payload, "DEGRADED") or else
              Payload_Is (Data, Item.Payload, "DEAD") or else
              Payload_Is (Data, Item.Payload, "ARCHIVED") or else
              Payload_Is (Data, Item.Payload, "COLLAPSED");
         when E.Record_Value =>
            -- Recovery's _RECORDS is exactly the original roster, not the
            -- operation_capture extension for resource and recovery-v3 DTOs.
            if Payload_Is (Data, Item.Module_Name, "worldline.resource_run_ledger") or else
              Payload_Is (Data, Item.Module_Name, "worldline.recovery_authority_kernel_v3") or else
              not Worldline.Operation_Archive.Record_Fields (Data, Item)
            then return False; end if;
         when E.List_Value | E.Tuple_Value | E.Object_Value => null;
      end case;
      N := E.Array_Length (Data, Item.Children);
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            if Item.Form in E.List_Value | E.Tuple_Value then
               Child := E.Array_Element (Data, Item.Children, I);
            else
               declare
                  P : constant E.View := Pair (Data, Item, I);
               begin
                  if P.Form /= E.List_Value or else E.Array_Length (Data, P.Children) /= 2 then
                     return False;
                  end if;
                  if Item.Form = E.Object_Value then
                     declare
                        Key : constant E.View := E.Decode
                          (Data, E.Array_Element (Data, P.Children, 0), E.Recovery);
                     begin
                        if Key.Form not in E.Text_Value | E.Bytes_Value then return False; end if;
                        if I > 0 then
                           for J in E.Count range 0 .. I - 1 loop
                              declare
                                 Earlier : constant E.View := Pair (Data, Item, J);
                                 Other : constant E.View := E.Decode
                                   (Data, E.Array_Element (Data, Earlier.Children, 0), E.Recovery);
                              begin
                                 if Same_Key (Data, Key, Other) then return False; end if;
                              end;
                           end loop;
                        end if;
                     end;
                  end if;
                  Child := E.Array_Element (Data, P.Children, 1);
               end;
            end if;
            if Child.Length = 0 or else Child.Length >= Encoded.Length or else
              not Valid (Data, Child) then return False; end if;
         end loop;
      end if;
      return True;
   end Valid;
   function Field (Data : E.Bytes; Encoded : E.Span; Name : String) return E.Span is
      Item : constant E.View := E.Decode (Data, Encoded, E.Recovery);
      N : E.Count;
   begin
      if Item.Form not in E.Object_Value | E.Record_Value then
         return (1, 0);
      end if;
      N := E.Array_Length (Data, Item.Children);
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               P : constant E.View := Pair (Data, Item, I);
               Key_Span : constant E.Span := E.Array_Element (Data, P.Children, 0);
               Key : constant E.View := E.Decode
                 (Data, Key_Span, (if Item.Form = E.Record_Value then E.Finalization else E.Recovery));
            begin
               if P.Form /= E.List_Value or else E.Array_Length (Data, P.Children) /= 2 then
                  return (1, 0);
               end if;
               if E.Text_Is (Data, Key, Name) then
                  return E.Array_Element (Data, P.Children, 1);
               end if;
            end;
         end loop;
      end if;
      return (1, 0);
   end Field;
   function Same_Encoding (Data : E.Bytes; Left, Right : E.Span) return Boolean is
   begin
      if not Valid (Data, Left) or else not Valid (Data, Right) or else
        Left.Length /= Right.Length then return False; end if;
      if Left.Length > 0 then
         for I in E.Count range 0 .. Left.Length - 1 loop
            if Data (Left.First + I) /= Data (Right.First + I) then return False; end if;
         end loop;
      end if;
      return True;
   end Same_Encoding;
   function Across
     (L_Data, R_Data : E.Bytes; L, R : E.Byte_View) return Boolean is
     (E.Bytes_Valid (L_Data, L) and then E.Bytes_Valid (R_Data, R)
      and then E.Materialize (L_Data, L) = E.Materialize (R_Data, R));
   function Float_Bits (Data : E.Bytes; V : E.View) return Interfaces.Unsigned_64 is
      use type Interfaces.Unsigned_64;
      Bits : Interfaces.Unsigned_64 := 0;
   begin
      if V.Form /= E.Float_Value or else not E.Bytes_Valid (Data, V.Payload) then return 0; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, V.Payload);
      begin
         if Raw'Length /= 8 then return 0; end if;
         for I in Raw'Range loop
            Bits := Interfaces.Shift_Left (Bits, 8) or Interfaces.Unsigned_64 (Raw (I));
         end loop;
      end;
      return Bits;
   end Float_Bits;
   function Integral_Equal (L_Data, R_Data : E.Bytes; L, R : E.View) return Boolean is
      function Bool_Integer (Data : E.Bytes; B, I : E.View) return Boolean is
      begin
         if I.Sign or else not E.Bytes_Valid (Data, I.Payload) then return False; end if;
         declare
            Raw : constant E.Bytes := E.Materialize (Data, I.Payload);
         begin
            return (if B.Boolean_Bit then Raw'Length = 1 and then Raw (Raw'First) = 1
                    else Raw'Length = 0);
         end;
      end Bool_Integer;
   begin
      if L.Form = E.Boolean_Value and then R.Form = E.Boolean_Value then
         return L.Boolean_Bit = R.Boolean_Bit;
      elsif L.Form = E.Boolean_Value then return Bool_Integer (R_Data, L, R);
      elsif R.Form = E.Boolean_Value then return Bool_Integer (L_Data, R, L);
      else return L.Sign = R.Sign and then Across (L_Data, R_Data, L.Payload, R.Payload);
      end if;
   end Integral_Equal;
   function Integer_Float_Equal
     (I_Data, F_Data : E.Bytes; I, F : E.View) return Boolean
   is
      package D renames Decimal_Binary64;
      use SPARK.Big_Integers;
      use type Interfaces.Unsigned_64;
      Bits : constant D.Bits := Float_Bits (F_Data, F);
      Magnitude : constant D.Bits := D.Magnitude (Bits);
   begin
      -- Infinity is not DB.Value's virtual next binade. A NaN is never equal.
      if not D.Finite (Bits) then return False; end if;
      if I.Form = E.Integer_Value and then I.Sign /= (Bits >= D.Sign_Bit) and then
        Magnitude /= 0 then return False; end if;
      declare
         Rational : constant D.Rational := D.Value (Magnitude);
      begin
         if Rational.Numerator mod Rational.Denominator /= To_Big_Integer (0) then return False; end if;
         declare
            Expected : Big_Integer := Rational.Numerator / Rational.Denominator;
         begin
            if I.Form = E.Boolean_Value then
               return Expected = To_Big_Integer (Boolean'Pos (I.Boolean_Bit))
                 and then (not I.Boolean_Bit or else Bits < D.Sign_Bit);
            end if;
            if not E.Bytes_Valid (I_Data, I.Payload) then return False; end if;
            declare
               Raw : constant E.Bytes := E.Materialize (I_Data, I.Payload);
            begin
               -- Compare to the exact finite binary64 integer a byte at a time.
               -- No arbitrary input integer is narrowed, rounded or allocated
               -- as a Big_Integer; excessive magnitude simply is not equal.
               for K in Raw'Range loop
                  if To_Big_Integer (Integer (Raw (K))) /= Expected mod To_Big_Integer (256) then
                     return False;
                  end if;
                  Expected := Expected / To_Big_Integer (256);
               end loop;
               return Expected = To_Big_Integer (0);
            end;
         end;
      end;
   end Integer_Float_Equal;
   function Numeric_Equal (L_Data, R_Data : E.Bytes; L, R : E.View) return Boolean is
      package D renames Decimal_Binary64;
      use type Interfaces.Unsigned_64;
   begin
      if L.Form /= E.Float_Value and then R.Form /= E.Float_Value then
         return Integral_Equal (L_Data, R_Data, L, R);
      elsif L.Form /= E.Float_Value then return Integer_Float_Equal (L_Data, R_Data, L, R);
      elsif R.Form /= E.Float_Value then return Integer_Float_Equal (R_Data, L_Data, R, L);
      else
         declare
            LB : constant D.Bits := Float_Bits (L_Data, L);
            RB : constant D.Bits := Float_Bits (R_Data, R);
         begin
            return D.Magnitude (LB) <= D.Infinity and then D.Magnitude (RB) <= D.Infinity
              and then ((D.Magnitude (LB) = 0 and then D.Magnitude (RB) = 0) or else LB = RB);
         end;
      end if;
   end Numeric_Equal;
   function Source_View (Data : E.Bytes; Encoded : E.Span; At_Layer : E.Layer;
                         Scoped : Boolean) return E.View
   is
      Item : E.View := E.Decode (Data, Encoded, At_Layer);
      Type_Name, Payload : E.View;
      function Value (Ordinal : E.Count) return E.View is
         P : constant E.View := Pair (Data, Item, Ordinal);
      begin
         return E.Decode (Data, E.Array_Element (Data, P.Children, 1), E.Operation);
      end Value;
   begin
      if not Scoped then return Item; end if;
      Type_Name := Value (0); Payload := Value (1);
      if E.Text_Is (Data, Type_Name, "integer") then
         Item.Form := E.Integer_Value; Item.Sign := Payload.Boolean_Bit;
         Item.Payload := Value (2).Payload;
      elsif E.Text_Is (Data, Type_Name, "bytes") then
         Item.Form := E.Bytes_Value; Item.Payload := Payload.Payload;
      elsif E.Text_Is (Data, Type_Name, "float") then
         Item.Form := E.Float_Value; Item.Payload := Payload.Payload;
      elsif E.Text_Is (Data, Type_Name, "str") or else
        E.Text_Is (Data, Type_Name, "bool") or else E.Text_Is (Data, Type_Name, "NoneType") then
         Item := Payload;
      elsif E.Text_Is (Data, Type_Name, "list") or else E.Text_Is (Data, Type_Name, "tuple") then
         Item.Form := (if E.Text_Is (Data, Type_Name, "list") then E.List_Value else E.Tuple_Value);
         Item.Children := Payload.Children;
      elsif E.Text_Is (Data, Type_Name, "dict") then
         Item.Form := E.Object_Value; Item.Children := Payload.Children;
      else
         Item.Form := E.Record_Value; Item.Record_Name := Type_Name.Payload;
         Item.Children := Payload.Children;
      end if;
      Item.Raw := Encoded; Item.At_Layer := At_Layer;
      return Item;
   end Source_View;
   subtype Restore_View_Depth is Natural range 0 .. 2;
   -- Explicit original S.restore position; no dictionary is inspected to
   -- select a codec. Metadata order is a set, not canonical S.record order.
   function Source_Text_Is (Data : E.Bytes; Item : E.View; Text : String)
      return Boolean is
   begin
      if Item.Form /= E.Text_Value or else
        not AP.Borrow_Valid (Data, Item.Payload) or else
        AP.Byte_Length (Data, Item.Payload) /= E.Count (Text'Length)
      then return False; end if;
      for I in Text'Range loop
         if AP.Byte_At (Data, Item.Payload, E.Count (I - Text'First)) /=
           Character'Pos (Text (I)) then return False; end if;
      end loop;
      return True;
   end Source_Text_Is;
   function Source_Object_Field
     (Data : E.Bytes; Item : E.View; Name : String) return E.Span
   is
      N : constant E.Count := E.Array_Length (Data, Item.Children);
   begin
      if Item.Form /= E.Object_Value then return (1, 0); end if;
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               P : constant E.View := Pair (Data, Item, I);
               Key : constant E.View := E.Decode
                 (Data, E.Array_Element (Data, P.Children, 0), E.Operation);
            begin
               if P.Form = E.List_Value and then
                 E.Array_Length (Data, P.Children) = 2 and then
                 Source_Text_Is (Data, Key, Name)
               then return E.Array_Element (Data, P.Children, 1); end if;
            end;
         end loop;
      end if;
      return (1, 0);
   end Source_Object_Field;
   function Source_Hex_Valid (Data : E.Bytes; Item : E.View) return Boolean is
      N : E.Count;
      Octet : E.Q.Byte;
   begin
      if Item.Form /= E.Text_Value or else
        not AP.Borrow_Valid (Data, Item.Payload) then return False; end if;
      N := AP.Byte_Length (Data, Item.Payload);
      if N mod 2 /= 0 then return False; end if;
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            Octet := AP.Byte_At (Data, Item.Payload, I);
            if Octet not in Character'Pos ('0') .. Character'Pos ('9') and then
              Octet not in Character'Pos ('a') .. Character'Pos ('f')
            then return False; end if;
         end loop;
      end if;
      return True;
   end Source_Hex_Valid;
   function Restored_Source_View
     (Data : E.Bytes; Encoded : E.Span; Depth : Record_Restore_Depth)
      return E.View
   is
      Wrapped : constant Boolean := Depth = 2;
      Item : constant E.View := Source_View (Data, Encoded, E.Operation, Wrapped);
      Kind : constant E.View := Source_View
        (Data, Source_Object_Field (Data, Item, "type"), E.Operation, Wrapped);
      Result : E.View := Item;
      Payload : E.View;
      N : constant E.Count := E.Array_Length (Data, Item.Children);
      function Value (Name : String) return E.View is
        (Source_View (Data, Source_Object_Field (Data, Item, Name),
           E.Operation, Wrapped));
   begin
      if Item.Form /= E.Object_Value or else Kind.Form /= E.Text_Value then
         return (others => <>);
      end if;
      if Source_Text_Is (Data, Kind, "integer") then
         Payload := Value ("magnitude");
         if N /= 3 or else Value ("negative").Form /= E.Boolean_Value or else
           not Source_Hex_Valid (Data, Payload) then return (others => <>); end if;
         Result.Form := E.Integer_Value;
         Result.Sign := Value ("negative").Boolean_Bit;
         Result.Payload := Payload.Payload;
      else
         if N /= 2 then return (others => <>); end if;
         if Source_Text_Is (Data, Kind, "bytes") or else
           Source_Text_Is (Data, Kind, "float")
         then
            Payload := Value
              ((if Source_Text_Is (Data, Kind, "bytes") then "value" else "bits"));
            if not Source_Hex_Valid (Data, Payload) then return (others => <>); end if;
            Result.Form := (if Source_Text_Is (Data, Kind, "bytes")
                            then E.Bytes_Value else E.Float_Value);
            if Result.Form = E.Float_Value and then
              AP.Byte_Length (Data, Payload.Payload) /= 16
            then return (others => <>); end if;
            Result.Payload := Payload.Payload;
         elsif Source_Text_Is (Data, Kind, "str") or else
           Source_Text_Is (Data, Kind, "bool") or else
           Source_Text_Is (Data, Kind, "NoneType")
         then
            Payload := Value ("value");
            if (Source_Text_Is (Data, Kind, "str") and then
                 Payload.Form /= E.Text_Value) or else
              (Source_Text_Is (Data, Kind, "bool") and then
                 Payload.Form /= E.Boolean_Value) or else
              (Source_Text_Is (Data, Kind, "NoneType") and then
                 Payload.Form /= E.Null_Value)
            then return (others => <>); end if;
            Result := Payload;
         elsif Source_Text_Is (Data, Kind, "tuple") or else
           Source_Text_Is (Data, Kind, "list")
         then
            Payload := Value ("items");
            if Payload.Form /= E.List_Value then return (others => <>); end if;
            Result.Form := (if Source_Text_Is (Data, Kind, "tuple")
                            then E.Tuple_Value else E.List_Value);
            Result.Children := Payload.Children;
         else
            Payload := Value ("fields");
            if Payload.Form /= E.Object_Value then return (others => <>); end if;
            Result.Form := (if Source_Text_Is (Data, Kind, "dict")
                            then E.Object_Value else E.Record_Value);
            Result.Record_Name := Kind.Payload;
            Result.Children := Payload.Children;
         end if;
      end if;
      Result.Raw := Encoded; Result.At_Layer := E.Operation;
      return Result;
   end Restored_Source_View;
   function Scoped_Module (Data : E.Bytes; Item : E.View) return String is
   begin
      if Finalization_Class (Data, Item, "RunContext") or else
        Finalization_Class (Data, Item, "RunBinding") or else
        Finalization_Class (Data, Item, "RunRow") or else
        Finalization_Class (Data, Item, "RunState") or else
        Finalization_Class (Data, Item, "RunObservation") or else
        Finalization_Class (Data, Item, "RunRequest") then return "worldline.resource_run_ledger";
      elsif Finalization_Class (Data, Item, "PhysicalFacts") then return "worldline.resource_os_observation";
      elsif Finalization_Class (Data, Item, "BoundUse") or else
        Finalization_Class (Data, Item, "NativeObservation") then return "worldline.recovery_authority_kernel_v3";
      elsif Finalization_Class (Data, Item, "ActorNativeObservation") or else
        Finalization_Class (Data, Item, "ActorCapability") then return "worldline.resource_actor_admission";
      elsif Finalization_Class (Data, Item, "ActorExecutionCrosswalk") or else
        Finalization_Class (Data, Item, "ActorExecutionNativeDecision") then return "worldline.resource_actor_execution";
      elsif Finalization_Class (Data, Item, "ProcessObservation") or else
        Finalization_Class (Data, Item, "RootController") or else
        Finalization_Class (Data, Item, "TaskOrigin") or else
        Finalization_Class (Data, Item, "NamespaceObservation") then return "worldline.resource_child_schema";
      elsif Finalization_Class (Data, Item, "ResourceChildNativeObservation") then
         return "worldline.resource_child_execution";
      else return "worldline.resource_scoped_run_ledger";
      end if;
   end Scoped_Module;
   function Source_Payload_Length
     (Data : E.Bytes; Item : E.View; Hexadecimal : Boolean) return E.Count is
     (AP.Byte_Length (Data, Item.Payload) / (if Hexadecimal then 2 else 1));
   function Source_Payload_Byte
     (Data : E.Bytes; Item : E.View; Hexadecimal : Boolean; Offset : E.Count)
      return E.Q.Byte
     with Global => null
   is
      function Digit (Octet : E.Q.Byte) return E.Q.Byte is
        (if Octet in Character'Pos ('0') .. Character'Pos ('9') then
           Octet - Character'Pos ('0')
         elsif Octet in Character'Pos ('a') .. Character'Pos ('f') then
           Octet - Character'Pos ('a') + 10
         else 0);
   begin
      if not Hexadecimal then return AP.Byte_At (Data, Item.Payload, Offset); end if;
      if Offset >= AP.Byte_Length (Data, Item.Payload) / 2 then return 0; end if;
      return Digit (AP.Byte_At (Data, Item.Payload, 2 * Offset)) * 16 +
        Digit (AP.Byte_At (Data, Item.Payload, 2 * Offset + 1));
   end Source_Payload_Byte;
   function Source_Payload_Equal
     (L_Data, R_Data : E.Bytes; L, R : E.View; L_Scoped, R_Scoped : Boolean)
      return Boolean
   is
      LH : constant Boolean := L_Scoped and then
        L.Form in E.Bytes_Value | E.Integer_Value | E.Float_Value;
      RH : constant Boolean := R_Scoped and then
        R.Form in E.Bytes_Value | E.Integer_Value | E.Float_Value;
      LN, RN : E.Count;
   begin
      if not AP.Borrow_Valid (L_Data, L.Payload) or else
        not AP.Borrow_Valid (R_Data, R.Payload) then return False; end if;
      LN := Source_Payload_Length (L_Data, L, LH);
      RN := Source_Payload_Length (R_Data, R, RH);
      if LN /= RN then return False; end if;
      if LN > 0 then
         for I in E.Count range 0 .. LN - 1 loop
            if Source_Payload_Byte (L_Data, L, LH, I) /=
              Source_Payload_Byte (R_Data, R, RH, I)
            then return False; end if;
         end loop;
      end if;
      return True;
   end Source_Payload_Equal;
   function Restored_Integer_Matches
     (L_Data, R_Data : E.Bytes; L, R : E.View; R_Scoped : Boolean)
      return Boolean
   is
      LN : E.Count := Source_Payload_Length (L_Data, L, True);
      RN : E.Count := Source_Payload_Length (R_Data, R, R_Scoped);
   begin
      if not AP.Borrow_Valid (L_Data, L.Payload) or else
        not AP.Borrow_Valid (R_Data, R.Payload) then return False; end if;
      while LN > 0 and then Source_Payload_Byte (L_Data, L, True, LN - 1) = 0 loop
         pragma Loop_Variant (Decreases => LN);
         LN := LN - 1;
      end loop;
      while RN > 0 and then Source_Payload_Byte (R_Data, R, R_Scoped, RN - 1) = 0 loop
         pragma Loop_Variant (Decreases => RN);
         RN := RN - 1;
      end loop;
      if LN /= RN or else (LN > 0 and then L.Sign /= R.Sign) then return False; end if;
      if LN > 0 then
         for I in E.Count range 0 .. LN - 1 loop
            if Source_Payload_Byte (L_Data, L, True, I) /=
              Source_Payload_Byte (R_Data, R, R_Scoped, I)
            then return False; end if;
         end loop;
      end if;
      return True;
   end Restored_Integer_Matches;
   function Equal_Trees
     (L_Data, R_Data : E.Bytes; Left, Right : E.Span; L_Layer, R_Layer : E.Layer;
      Exact : Boolean := False; L_Scoped, R_Scoped : Boolean := False;
      L_Record_Depth : Restore_View_Depth := 0;
      Source_Order : Boolean := False) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Left.Length);
   function Equal_Trees
     (L_Data, R_Data : E.Bytes; Left, Right : E.Span; L_Layer, R_Layer : E.Layer;
      Exact : Boolean := False; L_Scoped, R_Scoped : Boolean := False;
      L_Record_Depth : Restore_View_Depth := 0;
      Source_Order : Boolean := False) return Boolean is
      L : constant E.View :=
        (if L_Record_Depth = 0 then Source_View (L_Data, Left, L_Layer, L_Scoped)
         else Restored_Source_View (L_Data, Left, Record_Restore_Depth (L_Record_Depth)));
      R : constant E.View := Source_View (R_Data, Right, R_Layer, R_Scoped);
      L_Source : constant Boolean := L_Scoped or else L_Record_Depth > 0;
      LN, RN : E.Count;
   begin
      if not Exact and then L.Form in E.Boolean_Value | E.Integer_Value | E.Float_Value and then
        R.Form in E.Boolean_Value | E.Integer_Value | E.Float_Value
      then return Numeric_Equal (L_Data, R_Data, L, R); end if;
      if not Exact and then L.Form in E.Text_Value | E.World_State_Value and then
        R.Form in E.Text_Value | E.World_State_Value
      then return Across (L_Data, R_Data, L.Payload, R.Payload); end if;
      if L.Form /= R.Form then return False; end if;
      case L.Form is
         when E.Null_Value => return True;
         when E.Boolean_Value => return L.Boolean_Bit = R.Boolean_Bit;
         when E.Integer_Value =>
            if Exact and then L_Record_Depth > 0 then
               return Restored_Integer_Matches (L_Data, R_Data, L, R, R_Scoped);
            end if;
            return Exact and then L.Sign = R.Sign and then
              Source_Payload_Equal (L_Data, R_Data, L, R, L_Source, R_Scoped);
         when E.Float_Value | E.Text_Value | E.World_State_Value =>
            return Exact and then L.Sign = R.Sign and then
              Source_Payload_Equal (L_Data, R_Data, L, R, L_Source, R_Scoped);
         when E.Bytes_Value =>
            return Source_Payload_Equal (L_Data, R_Data, L, R, L_Source, R_Scoped);
         when E.Record_Value =>
            if not AP.Bytes_Equal (L_Data, R_Data, L.Record_Name, R.Record_Name) then return False; end if;
            if L_Source and then R_Scoped then
               if Scoped_Module (L_Data, L) /= Scoped_Module (R_Data, R) then return False; end if;
            elsif L_Source then
               if not Payload_Is (R_Data, R.Module_Name, Scoped_Module (L_Data, L)) then return False; end if;
            elsif R_Scoped then
               if not Payload_Is (L_Data, L.Module_Name, Scoped_Module (R_Data, R)) then return False; end if;
            elsif L_Layer = E.Finalization_Record then
               if R_Layer /= E.Finalization_Record and then
                 not Finalization_Module_Is (L_Data, L, R_Data, R.Module_Name) then return False; end if;
            elsif R_Layer = E.Finalization_Record then
               if not Finalization_Module_Is (R_Data, R, L_Data, L.Module_Name) then return False; end if;
            elsif not Across (L_Data, R_Data, L.Module_Name, R.Module_Name) then return False;
            end if;
         when E.List_Value | E.Tuple_Value | E.Object_Value => null;
         when others => return False;
      end case;
      LN := E.Array_Length (L_Data, L.Children);
      RN := E.Array_Length (R_Data, R.Children);
      if LN /= RN then return False; end if;
      if LN > 0 then
         for K in E.Count range 0 .. LN - 1 loop
            if L.Form in E.List_Value | E.Tuple_Value then
               declare
                  LC : constant E.Span := E.Array_Element (L_Data, L.Children, K);
                  RC : constant E.Span := E.Array_Element (R_Data, R.Children, K);
               begin
                  if LC.Length = 0 or else LC.Length >= Left.Length or else
                    not Equal_Trees (L_Data, R_Data, LC, RC, L_Layer, R_Layer,
                      Exact, L_Scoped, R_Scoped, L_Record_Depth, Source_Order) then return False; end if;
               end;
            elsif L.Form = E.Record_Value and then L_Record_Depth > 0 then
               -- S.restore reconstructs a declared dataclass by keyword name,
               -- so metadata/field input permutations are not an extra limit.
               declare
                  RP : constant E.View := Pair (R_Data, R, K);
                  RKey : constant E.View := E.Decode
                    (R_Data, E.Array_Element (R_Data, RP.Children, 0),
                     (if R_Scoped then E.Operation else E.Finalization));
                  RC : constant E.Span := E.Array_Element (R_Data, RP.Children, 1);
                  Found : Boolean := False;
               begin
                  for J in E.Count range 0 .. LN - 1 loop
                     declare
                        LP : constant E.View := Pair (L_Data, L, J);
                        LKey : constant E.View := E.Decode
                          (L_Data, E.Array_Element (L_Data, LP.Children, 0), E.Operation);
                        LC : constant E.Span := E.Array_Element (L_Data, LP.Children, 1);
                     begin
                        if LKey.Form = E.Text_Value and then
                          AP.Bytes_Equal (L_Data, R_Data, LKey.Payload, RKey.Payload)
                        then
                           if LC.Length = 0 or else LC.Length >= Left.Length or else
                             not Equal_Trees (L_Data, R_Data, LC, RC, L_Layer, R_Layer,
                               Exact, L_Scoped, R_Scoped, L_Record_Depth, Source_Order)
                           then return False; end if;
                           Found := True; exit;
                        end if;
                     end;
                  end loop;
                  if not Found then return False; end if;
               end;
            elsif L.Form = E.Record_Value then
               declare
                  LP : constant E.View := Pair (L_Data, L, K);
                  RP : constant E.View := Pair (R_Data, R, K);
                  LC : constant E.Span := E.Array_Element (L_Data, LP.Children, 1);
                  RC : constant E.Span := E.Array_Element (R_Data, RP.Children, 1);
               begin
                  if Exact and then not Across
                    (L_Data, R_Data,
                     E.Decode (L_Data, E.Array_Element (L_Data, LP.Children, 0),
                       (if L_Scoped then E.Operation else E.Finalization)).Payload,
                     E.Decode (R_Data, E.Array_Element (R_Data, RP.Children, 0),
                       (if R_Scoped then E.Operation else E.Finalization)).Payload)
                  then return False; end if;
                  if LC.Length = 0 or else LC.Length >= Left.Length or else
                    not Equal_Trees (L_Data, R_Data, LC, RC, L_Layer, R_Layer,
                      Exact, L_Scoped, R_Scoped, L_Record_Depth, Source_Order) then return False; end if;
               end;
            else
               declare
                  LP : constant E.View := Pair (L_Data, L, K);
                  Key : constant E.View := E.Decode
                    (L_Data, E.Array_Element (L_Data, LP.Children, 0),
                     (if L_Layer = E.Finalization_Record then E.Finalization else L_Layer));
                  LC : constant E.Span := E.Array_Element (L_Data, LP.Children, 1);
                  Found : Boolean := False;
               begin
                  if LC.Length = 0 or else LC.Length >= Left.Length then return False; end if;
                  if Source_Order or else L_Record_Depth > 0 then
                     declare
                        RP : constant E.View := Pair (R_Data, R, K);
                        RKey : constant E.View := E.Decode
                          (R_Data, E.Array_Element (R_Data, RP.Children, 0),
                           (if R_Layer = E.Finalization_Record then E.Finalization else R_Layer));
                     begin
                        if Key.Form /= RKey.Form or else
                          (L_Record_Depth > 0 and then Key.Form /= E.Text_Value) or else
                          not AP.Bytes_Equal (L_Data, R_Data, Key.Payload, RKey.Payload) or else
                          not Equal_Trees (L_Data, R_Data, LC,
                            E.Array_Element (R_Data, RP.Children, 1), L_Layer, R_Layer,
                            Exact, L_Scoped, R_Scoped, L_Record_Depth, Source_Order)
                        then return False; end if;
                     end;
                  else
                     for J in E.Count range 0 .. RN - 1 loop
                        declare
                           RP : constant E.View := Pair (R_Data, R, J);
                           RKey : constant E.View := E.Decode
                             (R_Data, E.Array_Element (R_Data, RP.Children, 0),
                              (if R_Layer = E.Finalization_Record then E.Finalization else R_Layer));
                        begin
                           if Key.Form = RKey.Form and then Across
                             (L_Data, R_Data, Key.Payload, RKey.Payload)
                           then
                              if not Equal_Trees (L_Data, R_Data, LC,
                                E.Array_Element (R_Data, RP.Children, 1), L_Layer, R_Layer,
                                Exact, L_Scoped, R_Scoped, L_Record_Depth, Source_Order)
                              then return False; end if;
                              Found := True; exit;
                           end if;
                        end;
                     end loop;
                     if not Found then return False; end if;
                  end if;
               end;
            end if;
         end loop;
      end if;
      return True;
   end Equal_Trees;
   function Equal (L_Data, R_Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (Valid (L_Data, Left) and then Valid (R_Data, Right) and then
      Equal_Trees (L_Data, R_Data, Left, Right, E.Recovery, E.Recovery));
   function Equal_Operation
     (L_Data, R_Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (Worldline.Operation_Archive.Valid (L_Data, Left) and then
      Worldline.Operation_Archive.Valid (R_Data, Right) and then
      Equal_Trees (L_Data, R_Data, Left, Right, E.Operation, E.Operation));
   function Equal_Finalization_Record
     (L_Data, R_Data : E.Bytes; Left, Right : E.Span;
      Right_Layer : E.Layer := E.Recovery) return Boolean is
     (Right_Layer in E.Recovery | E.Operation and then
      Valid_Finalization_Record (L_Data, Left) and then
      (if Right_Layer = E.Recovery then Valid (R_Data, Right)
       else Worldline.Operation_Archive.Valid (R_Data, Right)) and then
      Equal_Trees (L_Data, R_Data, Left, Right, E.Finalization_Record, Right_Layer));
   function Root_Record_Fields (Data : E.Bytes; Item : E.View) return Boolean is
   begin
      -- Only the fixed root_worker_codec._schema declarations supplement OA.
      -- These added constructors are plain dataclasses: annotations are not
      -- runtime validation and must not narrow their original accepted values.
      if Worldline.Operation_Archive.Record_Fields (Data, Item) then return True; end if;
      if Item.Form /= E.Record_Value then return False; end if;
      if Payload_Is (Data, Item.Module_Name, "worldline.resource_scoped_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "ScopedState") then
         return Finalization_Field_Roster (Data, Item,
           "current|resource_epoch|universe_head|ledger_head|history_head|physical_head");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_scoped_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "ScopeFrame") then
         return Finalization_Field_Roster (Data, Item,
           "scope|first_epoch|universe_head|frame_head|prior_frame|store_genesis|store_id|root_head|prime|root_count|cause|requester|receipt|catalogue_head|observation_head");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_scoped_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "PhysicalKey") then
         return Finalization_Field_Roster (Data, Item,
           "machine|resource|unit");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_scoped_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "PhysicalBucket") then
         return Finalization_Field_Roster (Data, Item,
           "key|capacity|held_total|charged_total|capacity_source|catalogue_head|observation_head");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_scoped_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "PhysicalProjection") then
         return Finalization_Field_Roster (Data, Item,
           "key|bound|origin|catalogue_head|numerator|denominator|amount");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_scoped_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "CurrentObservation") then
         return Finalization_Field_Roster (Data, Item,
           "scope|resource_epoch|universe_head|ledger_head|history_head|physical_head|store_genesis|store_id|root_head|prime|root_count|cause|requester|receipt|catalogue_head|observation_head");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_scoped_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "ScopedIntent") then
         return Finalization_Field_Roster (Data, Item,
           "kind|original|expected_epoch|expected_ledger_head|request_id|cause|requester|receipt");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_scoped_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "ScopedPacket") then
         return Finalization_Field_Roster (Data, Item,
           "before|history|rows|projection|buckets|proposed|proposed_history|proposed_rows|proposed_projection|proposed_buckets|actual_buckets|observed|facts|current|request");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_scoped_run_ledger") and then
        Payload_Is (Data, Item.Record_Name, "ScopedNativeDecision") then
         return Finalization_Field_Roster (Data, Item,
           "entry_point|status|raw_input|raw_arena|raw_rosters|raw_output|transport_status");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_os_observation") and then
        Payload_Is (Data, Item.Record_Name, "PhysicalFacts") then
         return Finalization_Field_Roster (Data, Item,
           "current|current_epoch|retained|current_universe_head|current_ledger_head|intent|dispatch|observation_head|actual_unit|cgroup|invocation|namespace|held_namespace|peer|held_peer|helper_image|expected_helper_image|challenge|held_challenge|protocol|closed_event|namespace_wait|helper_wait|cgroup_events|cgroup_type|manager_delegate|cgroup_owner|cgroup_group_write|cgroup_other_write|actual_store_genesis|actual_store_id|owner_store_genesis|owner_store_id|genesis_universe|genesis_instance|genesis_context_head|genesis_prime|genesis_root_count|phase");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_actor_admission") and then
        Payload_Is (Data, Item.Record_Name, "ActorNativeObservation") then
         return Finalization_Field_Roster (Data, Item,
           "bound|raw_frame|raw_sender|ticket|raw_proc_status|raw_proc_cgroup|raw_proc_maps|raw_proc_cmdline|raw_pidfd_info|namespace|held_namespace|helper_image|expected_helper_image|executable_plan|expected_executable_plan|original_requester|requester_credentials|expected_requester_credentials|dispatch|running_event|expected_running_event|canonical_use_event|expected_canonical_use_event|store_genesis|expected_store_genesis|source_lease|expected_source_lease|actor_wait|helper_wait|namespace_wait|host_pid|namespace_pid|sender_uid|sender_gid|real_uid|effective_uid|saved_uid|real_gid|effective_gid|saved_gid|capability_version|effective_low|permitted_low|inheritable_low|effective_high|permitted_high|inheritable_high|securebits|no_new_privs|requester_uid|requester_gid|configured_requester_uid|workload_uid|workload_gid|proc_host_pid|proc_namespace_pid|proc_real_uid|proc_effective_uid|proc_saved_uid|proc_real_gid|proc_effective_gid|proc_saved_gid|proc_effective|proc_permitted|proc_inheritable|proc_bounding|proc_ambient|proc_no_new_privs|proc_fs_uid|proc_fs_gid");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_actor_admission") and then
        Payload_Is (Data, Item.Record_Name, "ActorCapability") then
         return Finalization_Field_Roster (Data, Item,
           "index|bounding|ambient");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_actor_execution") and then
        Payload_Is (Data, Item.Record_Name, "ActorExecutionCrosswalk") then
         return Finalization_Field_Roster (Data, Item,
           "resource_current|operation_policy|operation_root_set|owner_genesis|installation|gate_config|managed_observation|original_grant|complete_crosswalk|current_source|original_request|original_requester|original_transaction|preparer|selected_plan");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_actor_execution") and then
        Payload_Is (Data, Item.Record_Name, "ActorExecutionNativeDecision") then
         return Finalization_Field_Roster (Data, Item,
           "entry_point|status|actor_input|actor_arena|actor_rosters|crosswalk|authority_input|authority_arena|authority_rosters|raw_output|transport_status");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_child_schema") and then
        Payload_Is (Data, Item.Record_Name, "ProcessObservation") then
         return Finalization_Field_Roster (Data, Item,
           "raw_status|raw_stat|raw_cgroup|raw_maps|raw_cmdline|raw_pidfd_info|namespace|cgroup|actual_unit|invocation|source_lease|pidfd_wait|host_pid|start_tick|parent_pid|parent_start_tick|real_uid|effective_uid|saved_uid|real_gid|effective_gid|saved_gid");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_child_schema") and then
        Payload_Is (Data, Item.Record_Name, "RootController") then
         return Finalization_Field_Roster (Data, Item,
           "bound|process|requester_uid|requester_gid|raw_manager|raw_channel|owner_endpoint|expected_owner_endpoint|source_lease|expected_source_lease|worker_image|expected_worker_image|handler_plan|expected_handler_plan|raw_request|requester|dispatch|running_event|expected_running_event|store_genesis|expected_store_genesis|current_source");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_child_schema") and then
        Payload_Is (Data, Item.Record_Name, "TaskOrigin") then
         return Finalization_Field_Roster (Data, Item,
           "action|root|child|task_id|root_world|child_world|root_instance|child_instance|world_store|full_world_ancestry|original_workload|sandbox|adapter|context|mission|stdin|credential_source|executable_source|configuration|owner_plan|native_cost_input|raw_request|requester|cause|root_dispatch|root_running_event|task_journal|task_intent|task_reservation_event|task_launch_event|parent_namespace_source|fd_lineage|source_lease");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_child_schema") and then
        Payload_Is (Data, Item.Record_Name, "NamespaceObservation") then
         return Finalization_Field_Roster (Data, Item,
           "identity|parent|raw_nsfs|raw_get_parent|source_lease");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_child_execution") and then
        Payload_Is (Data, Item.Record_Name, "ResourceChildNativeObservation") then
         return Finalization_Field_Roster (Data, Item,
           "entry_point|mode|status|actor_input|resource_arena|resource_rosters|authority_input|authority_arena|authority_rosters|crosswalk|child_input|raw_output|transport_status");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.resource_actor_credentials") and then
        Payload_Is (Data, Item.Record_Name, "ActorCredentialObservation") then
         return Finalization_Field_Roster (Data, Item,
           "raw_frame|raw_sender_credentials|host_pid|sender_real_uid|sender_real_gid|ticket|namespace_pid|uids|gids|capability_version|capability_words|securebits|no_new_privs|capabilities|supplementary_groups");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.root_worker_credentials") and then
        Payload_Is (Data, Item.Record_Name, "RootCredentialObservation") then
         return Finalization_Field_Roster (Data, Item,
           "raw_frame|raw_sender_credentials|host_pid|sender_real_uid|sender_real_gid|ticket|namespace_pid|uids|gids|capability_version|capability_words|securebits|no_new_privs|capabilities|supplementary_groups");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.root_worker_prepared_inputs") and then
        Payload_Is (Data, Item.Record_Name, "PreparedInputs") then
         return Finalization_Field_Roster (Data, Item,
           "operation|journal_raw|admission_head|reserved_event_raw|effect_intent_event_raw|reserved_snapshot|effect_intent_snapshot|full_ordered_events");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.root_worker_prepared_wire") and then
        Payload_Is (Data, Item.Record_Name, "SnapshotWire") then
         return Finalization_Field_Roster (Data, Item,
           "request|rosters|counts");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.root_worker_prepared_wire") and then
        Payload_Is (Data, Item.Record_Name, "PreparedWire") then
         return Finalization_Field_Roster (Data, Item,
           "retained|arena|reserve|intent");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.root_worker_retained_inputs") and then
        Payload_Is (Data, Item.Record_Name, "RetainedInputs") then
         return Finalization_Field_Roster (Data, Item,
           "arena|key|genesis_archive|head_archive|genesis_rows|event_rows|head_rows|owner_capture_archive|gate_raw|run_database_archive|schema");
      elsif Payload_Is (Data, Item.Module_Name, "worldline.protected_scoped_resource_service") and then
        Payload_Is (Data, Item.Record_Name, "ScopedSnapshot") then
         return Finalization_Field_Roster (Data, Item,
           "state|history|rows|projection|buckets");
      end if;
      return False;
   end Root_Record_Fields;
   function Source_Valid
     (Data : E.Bytes; Encoded : E.Span; Scoped : Boolean := False) return Boolean
   is
      Item : E.View;
      N : E.Count;
      Child : E.Span;
   begin
      if Scoped then return Worldline.Scoped_Archive.Valid (Data, Encoded); end if;
      Item := E.Decode (Data, Encoded, E.Operation);
      case Item.Form is
         when E.Invalid => return False;
         when E.Null_Value | E.Boolean_Value | E.Integer_Value | E.Float_Value |
              E.Text_Value | E.Bytes_Value => return True;
         when E.World_State_Value =>
            return Payload_Is (Data, Item.Payload, "MUTABLE") or else
              Payload_Is (Data, Item.Payload, "FINALIZING") or else
              Payload_Is (Data, Item.Payload, "VALID") or else
              Payload_Is (Data, Item.Payload, "DEGRADED") or else
              Payload_Is (Data, Item.Payload, "DEAD") or else
              Payload_Is (Data, Item.Payload, "ARCHIVED") or else
              Payload_Is (Data, Item.Payload, "COLLAPSED");
         when E.Record_Value =>
            if not Root_Record_Fields (Data, Item) then return False; end if;
         when E.List_Value | E.Tuple_Value | E.Object_Value => null;
      end case;
      N := E.Array_Length (Data, Item.Children);
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            if Item.Form in E.List_Value | E.Tuple_Value then
               Child := E.Array_Element (Data, Item.Children, I);
            else
               declare
                  P : constant E.View := Pair (Data, Item, I);
               begin
                  if P.Form /= E.List_Value or else E.Array_Length (Data, P.Children) /= 2 then
                     return False;
                  end if;
                  if Item.Form = E.Object_Value then
                     declare
                        Key : constant E.View := E.Decode
                          (Data, E.Array_Element (Data, P.Children, 0), E.Operation);
                     begin
                        if Key.Form not in E.Text_Value | E.Bytes_Value then return False; end if;
                        if I > 0 then
                           for J in E.Count range 0 .. I - 1 loop
                              declare
                                 Earlier : constant E.View := Pair (Data, Item, J);
                                 Other_Key : constant E.View := E.Decode
                                   (Data, E.Array_Element (Data, Earlier.Children, 0), E.Operation);
                              begin
                                 if Same_Key (Data, Key, Other_Key) then return False; end if;
                              end;
                           end loop;
                        end if;
                     end;
                  end if;
                  Child := E.Array_Element (Data, P.Children, 1);
               end;
            end if;
            if Child.Length = 0 or else Child.Length >= Encoded.Length or else
              not Source_Valid (Data, Child) then return False; end if;
         end loop;
      end if;
      return True;
   end Source_Valid;
   function Source_Value_Matches
     (L_Data, R_Data : E.Bytes; Left, Right : E.Span;
      Left_Scoped, Right_Scoped : Boolean := False) return Boolean is
     (Source_Valid (L_Data, Left, Left_Scoped) and then
      Source_Valid (R_Data, Right, Right_Scoped) and then
      Equal_Trees (L_Data, R_Data, Left, Right, E.Operation, E.Operation,
        True, Left_Scoped, Right_Scoped));
   function Restored_Source_Value_Matches
     (L_Data, R_Data : E.Bytes; Left, Right : E.Span;
      Left_Record_Depth : Record_Restore_Depth;
      Right_Scoped : Boolean := False) return Boolean is
     (Source_Valid (L_Data, Left, Left_Record_Depth = 2) and then
      Source_Valid (R_Data, Right, Right_Scoped) and then
      Equal_Trees (L_Data, R_Data, Left, Right, E.Operation, E.Operation,
        True, False, Right_Scoped, Restore_View_Depth (Left_Record_Depth)));
   function Ordered_Source_Value_Matches
     (L_Data, R_Data : E.Bytes; Left, Right : E.Span;
      Left_Scoped, Right_Scoped : Boolean := False) return Boolean is
     (Source_Valid (L_Data, Left, Left_Scoped) and then
      Source_Valid (R_Data, Right, Right_Scoped) and then
      Equal_Trees (L_Data, R_Data, Left, Right, E.Operation, E.Operation,
        True, Left_Scoped, Right_Scoped, 0, True));
end Worldline.Recovery_Archive;

with Worldline.Custody_V2_Closed_V1;
with Worldline.Custody_V2_Root_Values;
with Worldline.Custody_V2_Archive_Projection;
with Worldline.Custody_V2_Fold_Engine;
package body Worldline.Custody_V2_Closed_State with SPARK_Mode is
   package O renames Worldline.Custody_V2_Root_Values;
   package V renames I.V;
   package T renames V.S;
   package AP renames Worldline.Custody_V2_Archive_Projection;
   package F renames Worldline.Custody_V2_Fold_Engine;
   use type E.Value_Kind;
   use type E.Encoding_Level;
   use type E.Layer;
   use type I.Decode_Status;
   use type F.Fold_Status;
   use type I.Q.Byte;
   use type I.S.SQL_Class;
   use type I.Original_Format;
   function Payload_Equal (A, B : E.Bytes; L, R : E.Byte_View) return Boolean is
     (AP.Bytes_Equal (A, B, L, R));
   -- Actual source geometry, not a depth or value cap. Every encoded child
   -- remains inside its immutable typed container and excludes that header.
   function Child_Of (Parent, Child : E.Span) return Boolean is
     (Child.Length < Parent.Length and then Child.First >= Parent.First and then
      Child.First - Parent.First <= Parent.Length and then
      Child.Length <= Parent.Length - (Child.First - Parent.First));
   function Pair_Key (Data : E.Bytes; Item : E.View; N : E.Count) return E.Span is
      Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, Item.Children, N),
        (if Item.At_Layer = E.Terminal then E.Terminal else E.Layer'Pred (Item.At_Layer)));
   begin
      return E.Array_Element (Data, Pair.Children, 0);
   end Pair_Key;
   function Pair_Value (Data : E.Bytes; Item : E.View; N : E.Count) return E.Span is
      Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, Item.Children, N),
        (if Item.At_Layer = E.Terminal then E.Terminal else E.Layer'Pred (Item.At_Layer)));
   begin
      return E.Array_Element (Data, Pair.Children, 1);
   end Pair_Value;
   function Equal_At (A, B : E.Bytes; Left, Right : E.Span; Layer : E.Layer) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Left.Length);
   function Key_Equal (A, B : E.Bytes; L, R : E.Span) return Boolean is
     (Equal_At (A, B, L, R, E.Operation));
   function Equal_At (A, B : E.Bytes; Left, Right : E.Span; Layer : E.Layer) return Boolean
   is
      Left_Data : E.Bytes renames A;
      Right_Data : E.Bytes renames B;
      L : constant E.View := E.Decode (Left_Data, Left, Layer);
      R : constant E.View := E.Decode (Right_Data, Right, Layer);
      Count : E.Count;
   begin
      if L.Form = E.Invalid or else L.Form /= R.Form then return False; end if;
      case L.Form is
         when E.Invalid => return False;
         when E.Null_Value => return True;
         when E.Boolean_Value => return L.Boolean_Bit = R.Boolean_Bit;
         when E.Integer_Value =>
            return L.Sign = R.Sign and then Payload_Equal (Left_Data, Right_Data, L.Payload, R.Payload);
         when E.Text_Value | E.Bytes_Value | E.Float_Value | E.World_State_Value =>
            return Payload_Equal (Left_Data, Right_Data, L.Payload, R.Payload);
         when E.Record_Value =>
            if not Payload_Equal (Left_Data, Right_Data, L.Module_Name, R.Module_Name) or else
               not Payload_Equal (Left_Data, Right_Data, L.Record_Name, R.Record_Name) then return False; end if;
         when E.List_Value | E.Tuple_Value | E.Object_Value => null;
      end case;
      Count := E.Array_Length (Left_Data, L.Children);
      if Count /= E.Array_Length (Right_Data, R.Children) then return False; end if;
      if Count = 0 then return True; end if;
      for N in E.Count range 0 .. Count - 1 loop
         pragma Loop_Variant (Increases => N);
         if L.Form = E.Object_Value then
            declare
               Left_Key : constant E.Span := Pair_Key (Left_Data, L, N);
               Left_Value : constant E.Span := Pair_Value (Left_Data, L, N);
               Found : Boolean := False;
            begin
               if not Child_Of (Left, Left_Key) or else not Child_Of (Left, Left_Value) then return False; end if;
               -- Equal row count cannot substitute for a dictionary bijection:
               -- reject a repeated left key before searching the right image.
               if N > 0 then
                  for M in E.Count range 0 .. N - 1 loop
                     pragma Loop_Variant (Increases => M);
                     if Equal_At (Left_Data, Left_Data, Left_Key,
                       Pair_Key (Left_Data, L, M), Layer) then return False; end if;
                  end loop;
               end if;
               for M in E.Count range 0 .. Count - 1 loop
                  pragma Loop_Variant (Increases => M);
                  if Equal_At (Left_Data, Right_Data, Left_Key, Pair_Key (Right_Data, R, M), Layer) then
                     if Found or else not Equal_At (Left_Data, Right_Data,
                       Left_Value, Pair_Value (Right_Data, R, M), Layer) then return False; end if;
                     Found := True;
                  end if;
               end loop;
               if not Found then return False; end if;
            end;
         elsif L.Form = E.Record_Value then
            declare
               Key : constant E.Span := Pair_Key (Left_Data, L, N);
               Value : constant E.Span := Pair_Value (Left_Data, L, N);
            begin
               if not Child_Of (Left, Key) or else not Child_Of (Left, Value) or else
                  not Equal_At (Left_Data, Right_Data, Key, Pair_Key (Right_Data, R, N), E.Finalization) or else
                  not Equal_At (Left_Data, Right_Data, Value, Pair_Value (Right_Data, R, N), Layer)
               then return False; end if;
            end;
         else
            declare Child : constant E.Span := E.Array_Element (Left_Data, L.Children, N); begin
               if not Child_Of (Left, Child) or else not Equal_At (Left_Data, Right_Data,
                 Child, E.Array_Element (Right_Data, R.Children, N), Layer) then return False; end if;
            end;
         end if;
      end loop;
      return True;
   end Equal_At;
   function Original_Equal
     (Left_Data, Right_Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (Equal_At (Left_Data, Right_Data, Left, Right, E.Operation));
   function Cell_Matches
     (Value : I.Parsed_Input; Cell : I.S.SQL_Cell; Data : E.Bytes; Item : E.Span) return Boolean
   is
      Viewed : constant E.View := E.Decode (Data, Item, E.Operation);
      Kind : constant E.Value_Kind :=
        (case Cell.Kind is when I.S.SQL_Null => E.Null_Value,
         when I.S.SQL_Integer => E.Integer_Value, when I.S.SQL_Text => E.Text_Value,
         when I.S.SQL_Blob => E.Bytes_Value, when I.S.SQL_Real => E.Float_Value);
   begin
      if Viewed.Form /= Kind then return False; end if;
      if Kind = E.Null_Value then return True; end if;
      if Kind = E.Integer_Value and then Viewed.Sign /= Cell.Integer_Value.Negative then return False; end if;
      declare
         Expected : constant E.Span :=
           (if Cell.Kind = I.S.SQL_Integer then (Cell.Integer_Value.First, Cell.Integer_Value.Length)
            else (Cell.Bytes.First, Cell.Bytes.Length));
      begin
         return AP.Bytes_Equal (Value.Arena, Data, (Expected, 0), Viewed.Payload);
      end;
   end Cell_Matches;
   function Event_Record_Matches
     (Value : I.Parsed_Input; Index : E.Count; Data : E.Bytes; Record_Image : E.Span) return Boolean
   is
      function Field (Name : String; Column : Positive) return Boolean is
        (Cell_Matches (Value, Value.Event_SQL (Index, Column), Data, O.Record_Field (Data, Record_Image, Name)));
   begin
      if Value.Status /= I.Parsed or else Index = 0 or else Index > Value.Decoded_Event_Count or else
         not O.Valid (Data, Record_Image) or else not O.Type_Is (Data, Record_Image, "dict") or else
         E.Array_Length (Data, E.Decode (Data, Record_Image, E.Operation).Children) /= 14 then return False; end if;
      return Field ("seq", 1) and then Field ("event_id", 2) and then Field ("previous", 3) and then
        Field ("generation", 4) and then Field ("operation", 5) and then Field ("subject_kind", 6) and then
        Field ("subject", 7) and then Field ("subgeneration", 8) and then Field ("kind", 9) and then
        Field ("actor", 10) and then Field ("base", 12) and then Field ("mac", 13) and then
        Value.Extras (Index).Original_Encoding = I.Operation_Original and then
        Original_Equal (Value.Arena, Data, Value.Extras (Index).Original_Payload,
          O.Record_Field (Data, Record_Image, "record")) and then
        AP.Scoped_Archive_Operation_Matches (Value.Arena, Data, Value.Events (Index).Record_Archive,
          O.Record_Field (Data, Record_Image, "retained_record"));
   end Event_Record_Matches;
   function Ignored (Data : E.Bytes; Key : E.View; Fields : String) return Boolean is
      First : Integer := Fields'First;
   begin
      for Last in Fields'Range loop
         pragma Loop_Variant (Increases => Last);
         if Fields (Last) = ',' then
            if E.Text_Is (Data, Key, Fields (First .. Last - 1)) then return True; end if;
            First := Last + 1;
         end if;
      end loop;
      return E.Text_Is (Data, Key, Fields (First .. Fields'Last));
   end Ignored;
   function Except (A, B : E.Bytes; Left, Right : E.Span; Fields : String) return Boolean is
      L : constant E.View := E.Decode (A, Left, E.Operation);
      R : constant E.View := E.Decode (B, Right, E.Operation);
      LC, RC : E.Count := 0;
   begin
      if L.Form /= E.Object_Value or else R.Form /= E.Object_Value then return False; end if;
      for N in E.Count range 1 .. E.Array_Length (A, L.Children) loop
         pragma Loop_Variant (Increases => N);
         if not Ignored (A, E.Decode (A, Pair_Key (A, L, N - 1), E.Operation), Fields) then
            LC := LC + 1;
            declare Found : Boolean := False; begin
               for M in E.Count range 1 .. E.Array_Length (B, R.Children) loop
                  pragma Loop_Variant (Increases => M);
                  if Key_Equal (A, B, Pair_Key (A, L, N - 1), Pair_Key (B, R, M - 1)) then
                     if Found or else not Original_Equal (A, B,
                       Pair_Value (A, L, N - 1), Pair_Value (B, R, M - 1)) then return False; end if;
                     Found := True;
                  end if;
               end loop;
               if not Found then return False; end if;
            end;
         end if;
      end loop;
      for N in E.Count range 1 .. E.Array_Length (B, R.Children) loop
         pragma Loop_Variant (Increases => N);
         if not Ignored (B, E.Decode (B, Pair_Key (B, R, N - 1), E.Operation), Fields) then RC := RC + 1; end if;
      end loop;
      return LC = RC;
   end Except;
   function Scoped_Except (Scoped_Data, Original_Data : E.Bytes; Scoped, Original : E.Span; Fields : String) return Boolean is
      Object : constant E.View := E.Decode (Original_Data, Original, E.Operation);
      Members : constant E.View := E.Decode (Scoped_Data, T.A.Field (Scoped_Data, Scoped, "fields"), E.Operation);
      OC, SC : E.Count := 0;
   begin
      if not V.Type_Is (Scoped_Data, Scoped, "dict") or else Object.Form /= E.Object_Value or else
         Members.Form /= E.Object_Value then return False; end if;
      for N in E.Count range 1 .. E.Array_Length (Original_Data, Object.Children) loop
         pragma Loop_Variant (Increases => N);
         declare Key : constant E.View := E.Decode (Original_Data,
           Pair_Key (Original_Data, Object, N - 1), E.Operation); Found : Boolean := False;
         begin
            if not Ignored (Original_Data, Key, Fields) then
               OC := OC + 1;
               for M in E.Count range 1 .. E.Array_Length (Scoped_Data, Members.Children) loop
                  pragma Loop_Variant (Increases => M);
                  declare Other_Key : constant E.View := E.Decode (Scoped_Data,
                    Pair_Key (Scoped_Data, Members, M - 1), E.Operation);
                  begin
                     if Key.Form = Other_Key.Form and then
                        Payload_Equal (Original_Data, Scoped_Data, Key.Payload, Other_Key.Payload) then
                        if Found or else not AP.Scoped_Archive_Operation_Matches
                          (Scoped_Data, Original_Data, Pair_Value (Scoped_Data, Members, M - 1),
                           Pair_Value (Original_Data, Object, N - 1)) then return False; end if;
                        Found := True;
                     end if;
                  end;
               end loop;
               if not Found then return False; end if;
            end if;
         end;
      end loop;
      for N in E.Count range 1 .. E.Array_Length (Scoped_Data, Members.Children) loop
         pragma Loop_Variant (Increases => N);
         if not Ignored (Scoped_Data, E.Decode (Scoped_Data,
           Pair_Key (Scoped_Data, Members, N - 1), E.Operation), Fields) then SC := SC + 1; end if;
      end loop;
      return OC = SC;
   end Scoped_Except;
   function Snapshot_Projection (Value : I.Parsed_Input; Data : E.Bytes; State : E.Span) return Boolean is
      Owner : constant E.Span := T.Field (Value.Arena, Value.Owner_Roster, "current");
      Paths : constant E.Span := O.Record_Field (Data, State, "paths");
      Projected : constant E.Span := T.Field (Value.Arena, Owner, "paths");
   begin
      if not AP.Scoped_Archive_Operation_Matches (Value.Arena, Data,
        T.Field (Value.Arena, Owner, "installation"), O.Record_Field (Data, State, "installation")) or else
         not AP.Scoped_Archive_Operation_Matches (Value.Arena, Data,
           T.Field (Value.Arena, Owner, "descriptor_raw"), O.Record_Field (Data, State, "descriptor_raw")) or else
         V.Count (Value.Arena, Projected) /= O.Count (Data, Paths) then return False; end if;
      for N in E.Count range 1 .. O.Count (Data, Paths) loop
         pragma Loop_Variant (Increases => N);
         declare
            Actual : constant E.Span := O.Element (Data, Paths, N - 1);
            Expected : constant E.Span := V.Element (Value.Arena, Projected, N - 1);
            DB : constant E.Span := O.Record_Field (Data, Actual, "logical_database");
            Expected_DB : constant E.Span := T.Field (Value.Arena, Expected, "logical_database");
         begin
            if not AP.Scoped_Archive_Operation_Matches (Value.Arena, Data,
              T.Field (Value.Arena, Expected, "path"), O.Record_Field (Data, Actual, "path")) or else
               not AP.Scoped_Archive_Operation_Matches (Value.Arena, Data,
                 T.Field (Value.Arena, Expected, "identity"), O.Record_Field (Data, Actual, "identity")) then return False; end if;
            if O.Valid (Data, DB) then
               if not Scoped_Except (Value.Arena, Data, Expected_DB, DB,
                 "custody_v2_rows,custody_v2_load,authenticated_root_events,root_events") then return False; end if;
            elsif not AP.Scoped_Archive_Operation_Matches (Value.Arena, Data,
              T.Field (Value.Arena, Expected, "raw"), O.Record_Field (Data, Actual, "raw")) then return False; end if;
         end;
      end loop;
      return True;
   end Snapshot_Projection;
   function Snapshot_Rows (Value : I.Parsed_Input; Data : E.Bytes; Database : E.Span) return Boolean is
      Captured : constant E.Span := O.Record_Field (Data, Database, "custody_v2_rows");
      function Rows_Match (Rows : I.SQL_Rows; Name : String) return Boolean is
         Actual : constant E.Span := O.Record_Field (Data, Captured, Name);
      begin
         if not O.Is_Sequence (Data, Actual) or else O.Count (Data, Actual) /= Rows'Length (1) then return False; end if;
         for N in Rows'Range (1) loop
            pragma Loop_Variant (Increases => N);
            declare Row : constant E.Span := O.Element (Data, Actual, N - Rows'First (1)); begin
               if not O.Is_Sequence (Data, Row) or else O.Count (Data, Row) /= Rows'Length (2) then return False; end if;
               for Column in Rows'Range (2) loop
                  pragma Loop_Variant (Increases => Column);
                  if not Cell_Matches (Value, Rows (N, Column), Data,
                    O.Element (Data, Row, E.Count (Column - Rows'First (2)))) then return False; end if;
               end loop;
            end;
         end loop;
         return True;
      end Rows_Match;
   begin
      return O.Type_Is (Data, Captured, "dict") and then
        E.Array_Length (Data, E.Decode (Data, Captured, E.Operation).Children) = 6 and then
        Rows_Match (Value.Event_SQL, "events") and then Rows_Match (Value.Head_SQL, "heads") and then
        Rows_Match (Value.Root_SQL, "roots") and then Rows_Match (Value.Subject_SQL, "subjects") and then
        Rows_Match (Value.Alternative_SQL, "alternatives") and then Rows_Match (Value.Blob_SQL, "blobs");
   end Snapshot_Rows;
   function Native_Snapshot (Data : E.Bytes; State, Database, Containing : E.Span) return Boolean
     with Global => null,
       Subprogram_Variant => (Decreases => Containing.Length, Decreases => 1);
   function Native_Snapshot (Data : E.Bytes; State, Database, Containing : E.Span) return Boolean is
      Load : constant E.Span := O.Record_Field (Data, Database, "custody_v2_load");
      Image : constant E.Span := O.Record_Field (Data, Load, "envelope");
   begin
      if not O.Valid_Bytes (Data, Image) then return False; end if;
      declare Raw : constant E.Bytes := O.Bytes_Value (Data, Image); Size : constant I.Sizes := I.Counts (Raw); begin
         if Raw'Length >= Containing.Length or else Size.Status /= I.Parsed then return False; end if;
         declare
            Value : I.Parsed_Input (Size.Arena, Size.Events, Size.Heads, Size.Roots, Size.Subjects, Size.Alternatives, Size.Blobs);
            Result : F.Observation;
         begin
            I.Decode (Raw, Value);
            if Value.Status /= I.Parsed or else not Snapshot_Projection (Value, Data, State) or else
               not Snapshot_Rows (Value, Data, Database) then return False; end if;
            Result := F.Load_Decide (Value);
            return Result.State = F.History_Folded;
         end;
      end;
   end Native_Snapshot;
   function Prefix (Data : E.Bytes; Before, Current : E.Span) return Boolean is
   begin
      if not O.Is_Sequence (Data, Before) or else not O.Is_Sequence (Data, Current) or else
         O.Count (Data, Before) > O.Count (Data, Current) then return False; end if;
      for N in E.Count range 1 .. O.Count (Data, Before) loop
         pragma Loop_Variant (Increases => N);
         if not Original_Equal (Data, Data, O.Element (Data, Before, N - 1), O.Element (Data, Current, N - 1)) then return False; end if;
      end loop;
      return True;
   end Prefix;
   function Tables (Data : E.Bytes; Before, Current : E.Span; V2 : Boolean) return Boolean is
   begin
      if not O.Is_Sequence (Data, Before) or else not O.Is_Sequence (Data, Current) or else
         O.Count (Data, Before) /= O.Count (Data, Current) then return False; end if;
      for N in E.Count range 1 .. O.Count (Data, Before) loop
         pragma Loop_Variant (Increases => N);
         declare
            L : constant E.Span := O.Element (Data, Before, N - 1);
            Found : Boolean := False;
         begin
            for Earlier in E.Count range 1 .. N - 1 loop
               pragma Loop_Variant (Increases => Earlier);
               if Original_Equal (Data, Data, O.Record_Field (Data, L, "name"),
                 O.Record_Field (Data, O.Element (Data, Before, Earlier - 1), "name"))
               then return False; end if;
            end loop;
            for M in E.Count range 1 .. O.Count (Data, Current) loop
               pragma Loop_Variant (Increases => M);
               declare R : constant E.Span := O.Element (Data, Current, M - 1); begin
                  if Original_Equal (Data, Data, O.Record_Field (Data, L, "name"), O.Record_Field (Data, R, "name")) then
                     if Found or else not Except (Data, Data, L, R, "rows") then return False; end if;
                     Found := True;
                     if O.Text_Is (Data, O.Record_Field (Data, L, "name"), "events") then
                        if not Prefix (Data, O.Record_Field (Data, L, "rows"), O.Record_Field (Data, R, "rows")) then return False; end if;
                     elsif not (O.Text_Is (Data, O.Record_Field (Data, L, "name"), "head") or else
                       (V2 and then (O.Text_Is (Data, O.Record_Field (Data, L, "name"), "root_state") or else
                         O.Text_Is (Data, O.Record_Field (Data, L, "name"), "subject_state") or else
                         O.Text_Is (Data, O.Record_Field (Data, L, "name"), "alternatives") or else
                         O.Text_Is (Data, O.Record_Field (Data, L, "name"), "blobs")))) and then
                       not Original_Equal (Data, Data, O.Record_Field (Data, L, "rows"), O.Record_Field (Data, R, "rows")) then return False; end if;
                  end if;
               end;
            end loop;
            if not Found then return False; end if;
         end;
      end loop;
      return True;
   end Tables;
   function Matches
     (Data : E.Bytes; Before, Current, Containing_Input, Owner_Key, Owner_Plan : E.Span)
      return Boolean is
      Left : constant E.Span := O.Record_Field (Data, Before, "paths");
      Right : constant E.Span := O.Record_Field (Data, Current, "paths");
   begin
      if not E.C.P.Valid (Data, Containing_Input) or else not O.Valid (Data, Before) or else
         not O.Valid (Data, Current) or else not O.Type_Is (Data, Before, "dict") or else
         not O.Type_Is (Data, Current, "dict") or else
         not Original_Equal (Data, Data, O.Record_Field (Data, Before, "installation"), O.Record_Field (Data, Current, "installation")) or else
         not Original_Equal (Data, Data, O.Record_Field (Data, Before, "descriptor_raw"), O.Record_Field (Data, Current, "descriptor_raw")) or else
         not O.Is_Sequence (Data, Left) or else not O.Is_Sequence (Data, Right) or else
         O.Count (Data, Left) /= O.Count (Data, Right) then return False; end if;
      for N in E.Count range 1 .. O.Count (Data, Left) loop
         pragma Loop_Variant (Increases => N);
         declare
            L : constant E.Span := O.Element (Data, Left, N - 1);
            R : constant E.Span := O.Element (Data, Right, N - 1);
            LD : constant E.Span := O.Record_Field (Data, L, "logical_database");
            RD : constant E.Span := O.Record_Field (Data, R, "logical_database");
         begin
            if not Original_Equal (Data, Data, O.Record_Field (Data, L, "path"), O.Record_Field (Data, R, "path")) or else
               not Original_Equal (Data, Data, O.Record_Field (Data, L, "identity"), O.Record_Field (Data, R, "identity")) then return False; end if;
            if O.Valid (Data, LD) or else O.Valid (Data, RD) then
               if not O.Type_Is (Data, LD, "dict") or else not O.Type_Is (Data, RD, "dict") then return False; end if;
               if O.Valid (Data, O.Record_Field (Data, LD, "custody_v2_rows")) or else
                  O.Valid (Data, O.Record_Field (Data, RD, "custody_v2_rows")) then
                  if not Native_Snapshot (Data, Before, LD, Containing_Input) or else
                     not Native_Snapshot (Data, Current, RD, Containing_Input) or else
                     not Except (Data, Data, LD, RD, "tables,custody_v2_rows,custody_v2_load,authenticated_root_events,root_events") or else
                     not Tables (Data, O.Record_Field (Data, LD, "tables"), O.Record_Field (Data, RD, "tables"), True) then return False; end if;
               elsif O.Valid (Data, O.Record_Field (Data, LD, "authenticated_root_events")) or else
                  O.Valid (Data, O.Record_Field (Data, RD, "authenticated_root_events")) then
                  if not Worldline.Custody_V2_Closed_V1.Matches (Data, Owner_Key, Before, LD, Owner_Plan) or else
                     not Worldline.Custody_V2_Closed_V1.Matches (Data, Owner_Key, Current, RD, Owner_Plan) or else
                     not Prefix (Data, O.Record_Field (Data, LD, "authenticated_root_events"),
                       O.Record_Field (Data, RD, "authenticated_root_events")) or else
                     not Except (Data, Data, LD, RD, "tables,authenticated_root_events,authenticated_root_head") or else
                     not Tables (Data, O.Record_Field (Data, LD, "tables"),
                       O.Record_Field (Data, RD, "tables"), False) then return False; end if;
               else
                  if not Original_Equal (Data, Data, LD, RD) then return False; end if;
               end if;
            elsif not Original_Equal (Data, Data, O.Record_Field (Data, L, "raw"), O.Record_Field (Data, R, "raw")) then return False; end if;
         end;
      end loop;
      return True;
   end Matches;
end Worldline.Custody_V2_Closed_State;

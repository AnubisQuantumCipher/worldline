with Worldline.Scoped_Capture_Projection;
with Worldline.Recovery_Archive;
with Worldline.Retained_Source_Layout;
with Worldline.Custody_V2_Empty_Seed;
with Worldline.Custody_V2_Values;
with Worldline.Retained_Raw_Decode;
with System;
package body Worldline.Retained_Evidence_Replay with SPARK_Mode is
   package P renames Worldline.Custody_V2_Values;
   package RD renames Worldline.Retained_Raw_Decode;
   package SA renames Worldline.Scoped_Archive;
   package OA renames SA.A;
   package Q renames V.Q;
   package N renames V.N;
   package W renames V.W;
   package O renames V.O;
   package D renames V.D;
   package X renames V.X;
   package Y renames V.Y;
   package T renames V.T;
   package CW renames RD.CW;
   package CO renames RD.CO;
   package CX renames RD.CX;
   package HC renames RD.HC;
   package G renames Worldline.Custody_V2_Empty_Seed;
   package Lyt renames Worldline.Retained_Source_Layout;
   use type Interfaces.Unsigned_64;
   use type Q.Byte_Count;
   use type Q.Byte;
   use type Interfaces.Unsigned_32;
   use type Interfaces.Unsigned_8;
   use type Interfaces.Integer_64;
   use type E.Value_Kind;
   use type Q.Byte_Array;
   use type A.Grant;
   use type A.Use_Row;
   use type A.C.Chain_Row;
   function Original_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
     (Worldline.Recovery_Archive.Source_Valid (Data, Item, False));
   function Field (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     with Post => Field'Result.Length <= Item.Length
   is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if SA.Valid (Data, Item) then return P.Record_Field (Data, Item, Name);
      elsif Original_Valid (Data, Item) and then View.Form in E.Record_Value | E.Object_Value then
         if E.Array_Length (Data, View.Children) > 0 then
            for I in E.Count range 0 .. E.Array_Length (Data, View.Children) - 1 loop
               declare
                  Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, View.Children, I), E.Finalization);
               begin
                  if Pair.Form = E.List_Value and then E.Array_Length (Data, Pair.Children) = 2
                    and then E.Text_Is (Data, E.Decode
                      (Data, E.Array_Element (Data, Pair.Children, 0),
                       (if View.Form = E.Record_Value then E.Finalization else E.Operation)), Name)
                  then return E.Array_Element (Data, Pair.Children, 1); end if;
               end;
            end loop;
         end if;
         return (1, 0);
      else return (1, 0); end if;
   end Field;
   function Text_Is (Data : E.Bytes; Item : E.Span; Text : String) return Boolean is
   begin
      if SA.Valid (Data, Item) then return SA.Text_Is (Data, Item, Text);
      else return Original_Valid (Data, Item) and then E.Text_Is (Data, E.Decode (Data, Item, E.Operation), Text); end if;
   end Text_Is;
   function Sequence_Count (Data : E.Bytes; Item : E.Span) return E.Count is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if SA.Valid (Data, Item) then return P.Count (Data, Item);
      elsif Original_Valid (Data, Item) and then View.Form in E.List_Value | E.Tuple_Value then
         return E.Array_Length (Data, View.Children);
      else return 0; end if;
   end Sequence_Count;
   function Element (Data : E.Bytes; Item : E.Span; Ordinal : E.Count) return E.Span is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if SA.Valid (Data, Item) then return P.Element (Data, Item, Ordinal);
      elsif Original_Valid (Data, Item) and then View.Form in E.List_Value | E.Tuple_Value then
         return E.Array_Element (Data, View.Children, Ordinal);
      else return (1, 0); end if;
   end Element;
   function Nibble (B : Q.Byte) return Q.Byte is
     (if B in Character'Pos ('0') .. Character'Pos ('9') then B - Character'Pos ('0')
      else B - Character'Pos ('a') + 10)
     with Global => null,
       Pre => B in Character'Pos ('0') .. Character'Pos ('9') or else B in Character'Pos ('a') .. Character'Pos ('f'),
       Post => Nibble'Result <= 15;
   function Text_Bytes (Data : E.Bytes; Item : E.Span) return E.Bytes is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if P.Valid_Text (Data, Item) then return P.Text_Value (Data, Item);
      elsif Original_Valid (Data, Item) and then View.Form = E.Text_Value and then E.Bytes_Valid (Data, View.Payload) then
         return E.Materialize (Data, View.Payload);
      else return (1 .. 0 => 0); end if;
   end Text_Bytes;
   function Hex_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if not P.Valid_Text (Data, Item) and then
        not (Original_Valid (Data, Item) and then View.Form = E.Text_Value and then E.Bytes_Valid (Data, View.Payload))
      then return False; end if;
      declare
         Raw : constant E.Bytes := Text_Bytes (Data, Item);
      begin
         return Raw'Length mod 2 = 0 and then
           (for all B of Raw => B in Character'Pos ('0') .. Character'Pos ('9') or else B in Character'Pos ('a') .. Character'Pos ('f'));
      end;
   end Hex_Valid;
   function Hex_Bytes (Data : E.Bytes; Item : E.Span) return E.Bytes
     with Global => null, Pre => Hex_Valid (Data, Item)
   is
      Raw : constant E.Bytes := Text_Bytes (Data, Item);
      Result : E.Bytes (1 .. Raw'Length / 2);
   begin
      for I in Result'Range loop
         Result (I) := 16 * Nibble (Raw (Raw'First + (I - 1) * 2)) + Nibble (Raw (Raw'First + (I - 1) * 2 + 1));
      end loop;
      return Result;
   end Hex_Bytes;
   function Bytes_Shape (Data : E.Bytes; Item : E.Span; Size : E.Count) return Boolean is
     (Archive_Bytes_Valid (Data, Item) and then Archive_Bytes (Data, Item)'Length = Size);
   function Tuple_Is (Data : E.Bytes; Item : E.Span) return Boolean is
     ((SA.Valid (Data, Item) and then P.Type_Is (Data, Item, "tuple"))
      or else (Original_Valid (Data, Item) and then E.Decode (Data, Item, E.Operation).Form = E.Tuple_Value));
   function Count_Is (Data : E.Bytes; Item : E.Span; Expected : E.Count) return Boolean is
      Value : Interfaces.Unsigned_64 := Interfaces.Unsigned_64 (Expected);
   begin
      if not Archive_Integer_Valid (Data, Item) or else Archive_Integer_Negative (Data, Item) then return False; end if;
      declare Mag : constant E.Bytes := Archive_Integer_Magnitude (Data, Item); begin
         for B of Mag loop
            if Interfaces.Unsigned_64 (B) /= (Value and 255) then return False; end if;
            Value := Interfaces.Shift_Right (Value, 8);
         end loop;
         return Value = 0;
      end;
   end Count_Is;
   function Transport_Zero (Data : E.Bytes; Item : E.Span) return Boolean is
     (Count_Is (Data, Item, 0));
   function Roster_Item (Data : E.Bytes; Rosters : E.Span; Ordinal : E.Count) return E.Span is
     (Element (Data, Rosters, Ordinal));
   function Roster_Data (Data : E.Bytes; Rosters : E.Span; Ordinal : E.Count) return E.Span is
     (Element (Data, Roster_Item (Data, Rosters, Ordinal), 1));
   function Roster_Valid (Data : E.Bytes; Rosters : E.Span; Ordinal : E.Count;
                         Name : String; Size : E.Count) return Boolean is
      Item : constant E.Span := Roster_Item (Data, Rosters, Ordinal);
      Raw : constant E.Span := Roster_Data (Data, Rosters, Ordinal);
   begin
      if not Tuple_Is (Data, Item) or else Sequence_Count (Data, Item) /= 3
        or else not Text_Is (Data, Element (Data, Item, 0), Name)
        or else not Archive_Bytes_Valid (Data, Raw) or else Size = 0 then return False; end if;
      declare Bytes : constant E.Bytes := Archive_Bytes (Data, Raw); begin
         return Bytes'Length mod Size = 0 and then Count_Is
           (Data, Element (Data, Item, 2), Bytes'Length / Size);
      end;
   end Roster_Valid;
   function Load_Array (Data : Q.Byte_Array) return N.Raw_History_Array
     with Global => null, Pre => Data'Length mod (N.Raw_Scope_Frame'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := N.Raw_Scope_Frame'Size / System.Storage_Unit;
      Result : N.Raw_History_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Load_Array (Data : Q.Byte_Array) return W.Raw_Row_Array
     with Global => null, Pre => Data'Length mod (W.Raw_Row'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := W.Raw_Row'Size / System.Storage_Unit;
      Result : W.Raw_Row_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Load_Array (Data : Q.Byte_Array) return N.Raw_Projection_Array
     with Global => null, Pre => Data'Length mod (N.Raw_Projection'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := N.Raw_Projection'Size / System.Storage_Unit;
      Result : N.Raw_Projection_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Load_Array (Data : Q.Byte_Array) return N.Raw_Bucket_Array
     with Global => null, Pre => Data'Length mod (N.Raw_Bucket'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := N.Raw_Bucket'Size / System.Storage_Unit;
      Result : N.Raw_Bucket_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Load_Array (Data : Q.Byte_Array) return W.Raw_Native_Array
     with Global => null, Pre => Data'Length mod (W.Raw_Native'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := W.Raw_Native'Size / System.Storage_Unit;
      Result : W.Raw_Native_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Load_Array (Data : Q.Byte_Array) return N.Raw_Facts_Array
     with Global => null, Pre => Data'Length mod (O.Raw_Facts'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := O.Raw_Facts'Size / System.Storage_Unit;
      Result : N.Raw_Facts_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Load_Array (Data : Q.Byte_Array) return D.Raw_Capability_Array
     with Global => null, Pre => Data'Length mod (D.Raw_Capability'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := D.Raw_Capability'Size / System.Storage_Unit;
      Result : D.Raw_Capability_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Load_Array (Data : Q.Byte_Array) return D.Raw_Group_Array
     with Global => null, Pre => Data'Length mod (W.Raw_Quantity'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := W.Raw_Quantity'Size / System.Storage_Unit;
      Result : D.Raw_Group_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Load_Array (Data : Q.Byte_Array) return Y.Raw_Task_Array
     with Global => null, Pre => Data'Length mod (Y.Raw_Task'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := Y.Raw_Task'Size / System.Storage_Unit;
      Result : Y.Raw_Task_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Load_Array (Data : Q.Byte_Array) return Y.Raw_Process_Array
     with Global => null, Pre => Data'Length mod (Y.Raw_Process'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := Y.Raw_Process'Size / System.Storage_Unit;
      Result : Y.Raw_Process_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Load_Array (Data : Q.Byte_Array) return Y.Raw_Namespace_Array
     with Global => null, Pre => Data'Length mod (Y.Raw_Namespace'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := Y.Raw_Namespace'Size / System.Storage_Unit;
      Result : Y.Raw_Namespace_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Load_Array (Data : Q.Byte_Array) return V.Raw_Grant_Array
     with Global => null, Pre => Data'Length mod (T.Raw_Grant'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := T.Raw_Grant'Size / System.Storage_Unit;
      Result : V.Raw_Grant_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Load_Array (Data : Q.Byte_Array) return V.Raw_Use_Array
     with Global => null, Pre => Data'Length mod (T.Raw_Use'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := T.Raw_Use'Size / System.Storage_Unit;
      Result : V.Raw_Use_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Load_Array (Data : Q.Byte_Array) return V.Raw_Chain_Array
     with Global => null, Pre => Data'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) = 0
   is
      Size : constant Q.Byte_Count := T.C.Raw_Row'Size / System.Storage_Unit;
      Result : V.Raw_Chain_Array (1 .. Data'Length / Size);
   begin
      for I in Result'Range loop
         Result (I) := RD.Load (Data (Data'First + (I - 1) * Size .. Data'First + I * Size - 1));
      end loop;
      return Result;
   end Load_Array;
   function Reestablish_Root_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Root_Replay_Result
   is
      Result : Root_Replay_Result;
      actor_input_Archive : constant E.Span := Field (Data, Observation_Archive, "actor_input");
      resource_arena_Archive : constant E.Span := Field (Data, Observation_Archive, "resource_arena");
      resource_rosters_Archive : constant E.Span := Field (Data, Observation_Archive, "resource_rosters");
      authority_input_Archive : constant E.Span := Field (Data, Observation_Archive, "authority_input");
      authority_arena_Archive : constant E.Span := Field (Data, Observation_Archive, "authority_arena");
      authority_rosters_Archive : constant E.Span := Field (Data, Observation_Archive, "authority_rosters");
      crosswalk_Archive : constant E.Span := Field (Data, Observation_Archive, "crosswalk");
      child_input_Archive : constant E.Span := Field (Data, Observation_Archive, "child_input");
      raw_output_Archive : constant E.Span := Field (Data, Observation_Archive, "raw_output");
   begin
      if not Archive_Record_Is (Data, Observation_Archive, "ResourceChildNativeObservation")
        or else not Text_Is (Data, Field (Data, Observation_Archive, "entry_point"), "wl_resource_child_execution_decide_v1")
        or else not Bytes_Shape (Data, actor_input_Archive, D.Raw_Packet'Size / System.Storage_Unit)
        or else not Bytes_Shape (Data, authority_input_Archive, T.Raw_Input'Size / System.Storage_Unit)
        or else not Bytes_Shape (Data, crosswalk_Archive, X.Raw_Crosswalk'Size / System.Storage_Unit)
        or else not Bytes_Shape (Data, child_input_Archive, Y.Raw_Input'Size / System.Storage_Unit)
        or else not Bytes_Shape (Data, raw_output_Archive, W.Raw_Result'Size / System.Storage_Unit)
        or else not Archive_Bytes_Valid (Data, resource_arena_Archive)
        or else not Archive_Bytes_Valid (Data, authority_arena_Archive)
        or else not Tuple_Is (Data, resource_rosters_Archive)
        or else Sequence_Count (Data, resource_rosters_Archive) /= 17
        or else not Roster_Valid (Data, resource_rosters_Archive, 0, "history", N.Raw_Scope_Frame'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 1, "proposed_history", N.Raw_Scope_Frame'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 2, "rows", W.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 3, "proposed_rows", W.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 4, "projection", N.Raw_Projection'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 5, "proposed_projection", N.Raw_Projection'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 6, "buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 7, "proposed_buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 8, "actual_buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 9, "observed", W.Raw_Native'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 10, "facts", O.Raw_Facts'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 11, "capabilities", D.Raw_Capability'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 12, "groups", W.Raw_Quantity'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 13, "proc_groups", W.Raw_Quantity'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 14, "tasks", Y.Raw_Task'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 15, "processes", Y.Raw_Process'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 16, "namespaces", Y.Raw_Namespace'Size / System.Storage_Unit)
        or else not Tuple_Is (Data, authority_rosters_Archive)
        or else Sequence_Count (Data, authority_rosters_Archive) /= 4
        or else not Roster_Valid (Data, authority_rosters_Archive, 0, "grants", T.Raw_Grant'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, authority_rosters_Archive, 1, "uses", T.Raw_Use'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, authority_rosters_Archive, 2, "receipts", T.C.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, authority_rosters_Archive, 3, "events", T.C.Raw_Row'Size / System.Storage_Unit)
      then return Result; end if;
      declare
         Raw : constant D.Raw_Packet := RD.Load (Archive_Bytes (Data, actor_input_Archive));
         Authority : constant T.Raw_Input := RD.Load (Archive_Bytes (Data, authority_input_Archive));
         Crosswalk : constant X.Raw_Crosswalk := RD.Load (Archive_Bytes (Data, crosswalk_Archive));
         Child : constant Y.Raw_Input := RD.Load (Archive_Bytes (Data, child_input_Archive));
         Arena : constant Q.Byte_Array := Archive_Bytes (Data, resource_arena_Archive);
         Authority_Arena : constant Q.Byte_Array := Archive_Bytes (Data, authority_arena_Archive);
         Copy_history : constant N.Raw_History_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 0)));
         Copy_proposed_history : constant N.Raw_History_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 1)));
         Copy_rows : constant W.Raw_Row_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 2)));
         Copy_proposed_rows : constant W.Raw_Row_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 3)));
         Copy_projection : constant N.Raw_Projection_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 4)));
         Copy_proposed_projection : constant N.Raw_Projection_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 5)));
         Copy_buckets : constant N.Raw_Bucket_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 6)));
         Copy_proposed_buckets : constant N.Raw_Bucket_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 7)));
         Copy_actual_buckets : constant N.Raw_Bucket_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 8)));
         Copy_observed : constant W.Raw_Native_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 9)));
         Copy_facts : constant N.Raw_Facts_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 10)));
         Copy_capabilities : constant D.Raw_Capability_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 11)));
         Copy_groups : constant D.Raw_Group_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 12)));
         Copy_proc_groups : constant D.Raw_Group_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 13)));
         Copy_tasks : constant Y.Raw_Task_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 14)));
         Copy_processes : constant Y.Raw_Process_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 15)));
         Copy_namespaces : constant Y.Raw_Namespace_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 16)));
         Copy_grants : constant V.Raw_Grant_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, authority_rosters_Archive, 0)));
         Copy_uses : constant V.Raw_Use_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, authority_rosters_Archive, 1)));
         Copy_receipts : constant V.Raw_Chain_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, authority_rosters_Archive, 2)));
         Copy_events : constant V.Raw_Chain_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, authority_rosters_Archive, 3)));
         Native : constant V.Result := V.Child_Decide (Raw, Arena, Copy_history, Copy_proposed_history, Copy_rows, Copy_proposed_rows, Copy_projection, Copy_proposed_projection, Copy_buckets, Copy_proposed_buckets, Copy_actual_buckets, Copy_observed, Copy_facts, Copy_capabilities, Copy_groups, Copy_proc_groups, Authority, Authority_Arena, Copy_grants, Copy_uses, Copy_receipts, Copy_events, Crosswalk, Child, Copy_tasks, Copy_processes, Copy_namespaces);
      begin
         if not Native.Well_Formed or else Native.Status > J.Status'Pos (J.Status'Last) then return Result; end if;
         Result.Native_Status := J.Status'Val (Native.Status);
         Result.Mode := J.Admission_Mode'Val (Child.Mode);
         Result.Action := A.Operation'Val (Authority.Bound.Action);
         Result.Id := T.Decode (Authority.Bound).Id;
         -- The output and human label are compared only after complete native
         -- redecision; neither can grant replay or rescue malformed operands.
         Result.State := Output_Conflict;
         declare
            Output : constant W.Raw_Result := RD.Load (Archive_Bytes (Data, raw_output_Archive));
         begin
            if Output.Status = Native.Status
              and then Text_Is (Data, Field (Data, Observation_Archive, "status"), J.Status'Image (Result.Native_Status))
              and then Text_Is (Data, Field (Data, Observation_Archive, "mode"), J.Admission_Mode'Image (Result.Mode))
              and then Transport_Zero (Data, Field (Data, Observation_Archive, "transport_status"))
            then Result.State := Native_Redecided; end if;
         end;
      end;
      return Result;
   end Reestablish_Root_Observation;
   function Reestablish_Scoped_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Scoped_Replay_Result
   is
      Result : Scoped_Replay_Result;
      raw_input_Archive : constant E.Span := Field (Data, Observation_Archive, "raw_input");
      raw_arena_Archive : constant E.Span := Field (Data, Observation_Archive, "raw_arena");
      raw_rosters_Archive : constant E.Span := Field (Data, Observation_Archive, "raw_rosters");
      raw_output_Archive : constant E.Span := Field (Data, Observation_Archive, "raw_output");
   begin
      if not Archive_Record_Is (Data, Observation_Archive, "ScopedNativeDecision")
        or else not Bytes_Shape (Data, raw_input_Archive, N.Raw_Packet'Size / System.Storage_Unit)
        or else not Bytes_Shape (Data, raw_output_Archive, W.Raw_Result'Size / System.Storage_Unit)
        or else not Archive_Bytes_Valid (Data, raw_arena_Archive)
        or else not Tuple_Is (Data, raw_rosters_Archive)
        or else Sequence_Count (Data, raw_rosters_Archive) /= 11
        or else not Roster_Valid (Data, raw_rosters_Archive, 0, "history", N.Raw_Scope_Frame'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 1, "proposed_history", N.Raw_Scope_Frame'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 2, "rows", W.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 3, "proposed_rows", W.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 4, "projection", N.Raw_Projection'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 5, "proposed_projection", N.Raw_Projection'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 6, "buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 7, "proposed_buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 8, "actual_buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 9, "observed", W.Raw_Native'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 10, "facts", O.Raw_Facts'Size / System.Storage_Unit)
      then return Result; end if;
      if Text_Is (Data, Field (Data, Observation_Archive, "entry_point"), "wl_resource_scoped_run_ledger_check_v1") then Result.Roster_Entry := Check_Entry;
      elsif Text_Is (Data, Field (Data, Observation_Archive, "entry_point"), "wl_resource_scoped_run_ledger_validate_v1") then Result.Roster_Entry := Validate_Entry;
      elsif Text_Is (Data, Field (Data, Observation_Archive, "entry_point"), "wl_resource_scoped_run_ledger_classify_v1") then Result.Roster_Entry := Classify_Entry;
      else return Result; end if;
      declare
         Raw : constant N.Raw_Packet := RD.Load (Archive_Bytes (Data, raw_input_Archive));
         Arena : constant Q.Byte_Array := Archive_Bytes (Data, raw_arena_Archive);
         Copy_history : constant N.Raw_History_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 0)));
         Copy_proposed_history : constant N.Raw_History_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 1)));
         Copy_rows : constant W.Raw_Row_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 2)));
         Copy_proposed_rows : constant W.Raw_Row_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 3)));
         Copy_projection : constant N.Raw_Projection_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 4)));
         Copy_proposed_projection : constant N.Raw_Projection_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 5)));
         Copy_buckets : constant N.Raw_Bucket_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 6)));
         Copy_proposed_buckets : constant N.Raw_Bucket_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 7)));
         Copy_actual_buckets : constant N.Raw_Bucket_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 8)));
         Copy_observed : constant W.Raw_Native_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 9)));
         Copy_facts : constant N.Raw_Facts_Array := Load_Array (Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 10)));
         Native : V.Result;
         Output : constant W.Raw_Result := RD.Load (Archive_Bytes (Data, raw_output_Archive));
         Label_Matches : Boolean := False;
      begin
         case Result.Roster_Entry is
            when Check_Entry => Native := V.Scoped_Check (Raw, Arena, Copy_history, Copy_proposed_history, Copy_rows, Copy_proposed_rows, Copy_projection, Copy_proposed_projection, Copy_buckets, Copy_proposed_buckets, Copy_actual_buckets, Copy_observed, Copy_facts);
            when Validate_Entry => Native := V.Scoped_Validate (Raw, Arena, Copy_history, Copy_proposed_history, Copy_rows, Copy_proposed_rows, Copy_projection, Copy_proposed_projection, Copy_buckets, Copy_proposed_buckets, Copy_actual_buckets, Copy_observed, Copy_facts);
            when Classify_Entry => Native := V.Scoped_Classify (Raw, Arena, Copy_history, Copy_proposed_history, Copy_rows, Copy_proposed_rows, Copy_projection, Copy_proposed_projection, Copy_buckets, Copy_proposed_buckets, Copy_actual_buckets, Copy_observed, Copy_facts);
         end case;
         if not Native.Well_Formed then return Result; end if;
         Result.Native_Status := Native.Status;
         Result.Action := S.Action'Val (Raw.Request.Kind);
         Result.Original_Command := J.L.Operation'Val (Raw.Request.Original.Kind);
         case Result.Roster_Entry is
            when Check_Entry =>
               if Native.Status <= S.Status'Pos (S.Status'Last) then
                  Label_Matches := Text_Is (Data, Field (Data, Observation_Archive, "status"), S.Status'Image (S.Status'Val (Native.Status)));
               end if;
            when Validate_Entry =>
               Label_Matches :=
                 (Native.Status = 0 and then Text_Is (Data, Field (Data, Observation_Archive, "status"), "INVALID_SNAPSHOT")) or else
                 (Native.Status = 1 and then Text_Is (Data, Field (Data, Observation_Archive, "status"), "CONSISTENT_SNAPSHOT"));
            when Classify_Entry =>
               if Native.Status <= J.L.Liveness'Pos (J.L.Liveness'Last) then
                  Label_Matches := Text_Is (Data, Field (Data, Observation_Archive, "status"), J.L.Liveness'Image (J.L.Liveness'Val (Native.Status)));
               end if;
         end case;
         Result.State := Output_Conflict;
         if Output.Status = Native.Status and then Label_Matches
           and then Transport_Zero (Data, Field (Data, Observation_Archive, "transport_status"))
         then Result.State := Native_Redecided; end if;
      end;
      return Result;
   end Reestablish_Scoped_Observation;
   function Reestablish_Historical_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Operation_Replay_Result
     with Global => null;
   function Historical_Material_Matches
     (Data, Material_Data : E.Bytes; Observation_Archive, Material_Archive : E.Span) return Boolean
     with Global => null;
   function Reestablish_Operation_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Operation_Replay_Result
   is
      Result : Operation_Replay_Result;
      input_Archive : constant E.Span := Field (Data, Observation_Archive, "input");
      arena_Archive : constant E.Span := Field (Data, Observation_Archive, "arena");
      rosters_Archive : constant E.Span := Field (Data, Observation_Archive, "rosters");
      output_Archive : constant E.Span := Field (Data, Observation_Archive, "output");
      View : constant E.View := E.Decode (Data, Observation_Archive, E.Operation);
   begin
      if Sequence_Count (Data, rosters_Archive) = 12 then
         return Reestablish_Historical_Observation (Data, Observation_Archive);
      end if;
      if not Original_Valid (Data, Observation_Archive) or else View.Form /= E.Object_Value
        or else (if SA.Valid (Data, Observation_Archive) then SA.Member_Count (Data, Observation_Archive) /= 5
                 else E.Array_Length (Data, View.Children) /= 5)
        or else not Hex_Valid (Data, input_Archive)
        or else not Hex_Valid (Data, arena_Archive)
        or else not Hex_Valid (Data, output_Archive)
        or else Hex_Bytes (Data, input_Archive)'Length /= T.Raw_Input'Size / System.Storage_Unit
        or else Hex_Bytes (Data, output_Archive)'Length /= T.Raw_Result'Size / System.Storage_Unit
        or else Sequence_Count (Data, rosters_Archive) /= 4
        or else not Hex_Valid (Data, Element (Data, rosters_Archive, 0))
        or else Hex_Bytes (Data, Element (Data, rosters_Archive, 0))'Length mod (T.Raw_Grant'Size / System.Storage_Unit) /= 0
        or else not Hex_Valid (Data, Element (Data, rosters_Archive, 1))
        or else Hex_Bytes (Data, Element (Data, rosters_Archive, 1))'Length mod (T.Raw_Use'Size / System.Storage_Unit) /= 0
        or else not Hex_Valid (Data, Element (Data, rosters_Archive, 2))
        or else Hex_Bytes (Data, Element (Data, rosters_Archive, 2))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) /= 0
        or else not Hex_Valid (Data, Element (Data, rosters_Archive, 3))
        or else Hex_Bytes (Data, Element (Data, rosters_Archive, 3))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) /= 0
      then return Result; end if;
      declare
         Authority : constant T.Raw_Input := RD.Load (Hex_Bytes (Data, input_Archive));
         Arena : constant Q.Byte_Array := Hex_Bytes (Data, arena_Archive);
         Copy_grants : constant V.Raw_Grant_Array := Load_Array (Hex_Bytes (Data, Element (Data, rosters_Archive, 0)));
         Copy_uses : constant V.Raw_Use_Array := Load_Array (Hex_Bytes (Data, Element (Data, rosters_Archive, 1)));
         Copy_receipts : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, rosters_Archive, 2)));
         Copy_events : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, rosters_Archive, 3)));
         Native : constant V.Result := V.Operation_Decide (Authority, Arena, Copy_grants, Copy_uses, Copy_receipts, Copy_events);
      begin
         if not Native.Well_Formed or else Native.Status > A.Decision'Pos (A.Decision'Last) then return Result; end if;
         Result.Command := A.Command'Val (Authority.Mode);
         Result.Native_Status := A.Decision'Val (Native.Status);
         Result.Action := A.Operation'Val (Authority.Bound.Action);
         Result.Id := T.Decode (Authority.Bound).Id;
         Result.State := Output_Conflict;
         declare
            Output : constant T.Raw_Result := RD.Load (Hex_Bytes (Data, output_Archive));
         begin
            if Interfaces.Unsigned_32 (Output.Disposition) = Native.Status
              and then Text_Is (Data, Field (Data, Observation_Archive, "decision"), A.Decision'Image (Result.Native_Status))
            then Result.State := Native_Redecided; end if;
         end;
      end;
      return Result;
   end Reestablish_Operation_Observation;
   function Identity_Matches (Arena : Q.Byte_Array; Raw : W.Raw_Id; Expected : E.Bytes) return Boolean is
   begin
      if not W.Well_Formed (Arena, Raw) then return False; end if;
      declare
         Id : constant J.L.Identity := W.Decode (Arena, Raw);
      begin
         return Id.Present and then Id.Value.Length = Expected'Length and then
           (for all I in Expected'Range => Arena (Id.Value.First + (I - Expected'First)) = Expected (I));
      end;
   end Identity_Matches;
   function Scoped_Identity_Matches
     (Data : E.Bytes; Observation_Archive : E.Span; Expected : E.Bytes;
      Reservation : Boolean := False) return Boolean
   is
      Replay : constant Scoped_Replay_Result := Reestablish_Scoped_Observation (Data, Observation_Archive);
   begin
      if Replay.State /= Native_Redecided then return False; end if;
      declare
         Raw : constant N.Raw_Packet := RD.Load (Archive_Bytes (Data, Field (Data, Observation_Archive, "raw_input")));
         Arena : constant Q.Byte_Array := Archive_Bytes (Data, Field (Data, Observation_Archive, "raw_arena"));
      begin
         return Identity_Matches (Arena,
           (if Reservation then Raw.Request.Original.Reservation else Raw.Request.Original.Operation_Id), Expected);
      end;
   end Scoped_Identity_Matches;
   -- Source correspondence is separate from authorization: every native
   -- operand is compared to its actual complete retained material record.
   function Dictionary_Count (Data : E.Bytes; Item : E.Span) return E.Count is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if SA.Valid (Data, Item) then return SA.Member_Count (Data, Item);
      elsif Original_Valid (Data, Item) and then View.Form = E.Object_Value then return E.Array_Length (Data, View.Children);
      else return 0; end if;
   end Dictionary_Count;
   function Record_Is (Data : E.Bytes; Item : E.Span; Name : String) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
      Expected : constant E.Count :=
        (if Name = "ScopedState" then 6
         elsif Name = "ScopeFrame" then 15
         elsif Name = "PhysicalKey" then 3
         elsif Name = "PhysicalBucket" then 7
         elsif Name = "PhysicalProjection" then 7
         elsif Name = "CurrentObservation" then 16
         elsif Name = "ScopedIntent" then 8
         elsif Name = "ScopedPacket" then 15
         elsif Name = "ScopedNativeDecision" then 7
         elsif Name = "RunContext" then 9
         elsif Name = "RunBinding" then 10
         elsif Name = "RunRow" then 11
         elsif Name = "RunState" then 7
         elsif Name = "RunObservation" then 8
         elsif Name = "RunRequest" then 10
         elsif Name = "PhysicalFacts" then 39
         elsif Name = "ActorNativeObservation" then 70
         elsif Name = "ActorCapability" then 3
         elsif Name = "ActorExecutionCrosswalk" then 15
         elsif Name = "ActorExecutionNativeDecision" then 11
         elsif Name = "BoundUse" then 30
         elsif Name = "NativeObservation" then 2
         elsif Name = "ProcessObservation" then 22
         elsif Name = "RootController" then 22
         elsif Name = "TaskOrigin" then 33
         elsif Name = "NamespaceObservation" then 5
         elsif Name = "ResourceChildNativeObservation" then 13
         elsif Name = "CollapseInput" then 35 else 0);
   begin
      if SA.Valid (Data, Item) and then P.Type_Is (Data, Item, Name) then return True; end if;
      if Expected = 0 or else not Original_Valid (Data, Item) or else View.Form /= E.Record_Value or else not E.Bytes_Valid (Data, View.Record_Name) or else E.Array_Length (Data, View.Children) /= Expected then return False; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, View.Record_Name);
      begin
         if Raw'Length /= Name'Length or else not (for all I in Name'Range => Raw (Raw'First + E.Count (I - Name'First)) = Character'Pos (Name (I))) then return False; end if;
      end;
      for I in E.Count range 0 .. Expected - 1 loop
         declare
            Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, View.Children, I), E.Finalization);
            Key : constant E.View := E.Decode (Data, E.Array_Element (Data, Pair.Children, 0), E.Finalization);
         begin
            if Pair.Form /= E.List_Value or else E.Array_Length (Data, Pair.Children) /= 2 then return False; end if;
            if Name = "ScopedState" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "current")) or else
               (I = 1 and then E.Text_Is (Data, Key, "resource_epoch")) or else
               (I = 2 and then E.Text_Is (Data, Key, "universe_head")) or else
               (I = 3 and then E.Text_Is (Data, Key, "ledger_head")) or else
               (I = 4 and then E.Text_Is (Data, Key, "history_head")) or else
               (I = 5 and then E.Text_Is (Data, Key, "physical_head"))) then return False; end if;
            if Name = "ScopeFrame" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "scope")) or else
               (I = 1 and then E.Text_Is (Data, Key, "first_epoch")) or else
               (I = 2 and then E.Text_Is (Data, Key, "universe_head")) or else
               (I = 3 and then E.Text_Is (Data, Key, "frame_head")) or else
               (I = 4 and then E.Text_Is (Data, Key, "prior_frame")) or else
               (I = 5 and then E.Text_Is (Data, Key, "store_genesis")) or else
               (I = 6 and then E.Text_Is (Data, Key, "store_id")) or else
               (I = 7 and then E.Text_Is (Data, Key, "root_head")) or else
               (I = 8 and then E.Text_Is (Data, Key, "prime")) or else
               (I = 9 and then E.Text_Is (Data, Key, "root_count")) or else
               (I = 10 and then E.Text_Is (Data, Key, "cause")) or else
               (I = 11 and then E.Text_Is (Data, Key, "requester")) or else
               (I = 12 and then E.Text_Is (Data, Key, "receipt")) or else
               (I = 13 and then E.Text_Is (Data, Key, "catalogue_head")) or else
               (I = 14 and then E.Text_Is (Data, Key, "observation_head"))) then return False; end if;
            if Name = "PhysicalKey" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "machine")) or else
               (I = 1 and then E.Text_Is (Data, Key, "resource")) or else
               (I = 2 and then E.Text_Is (Data, Key, "unit"))) then return False; end if;
            if Name = "PhysicalBucket" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "key")) or else
               (I = 1 and then E.Text_Is (Data, Key, "capacity")) or else
               (I = 2 and then E.Text_Is (Data, Key, "held_total")) or else
               (I = 3 and then E.Text_Is (Data, Key, "charged_total")) or else
               (I = 4 and then E.Text_Is (Data, Key, "capacity_source")) or else
               (I = 5 and then E.Text_Is (Data, Key, "catalogue_head")) or else
               (I = 6 and then E.Text_Is (Data, Key, "observation_head"))) then return False; end if;
            if Name = "PhysicalProjection" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "key")) or else
               (I = 1 and then E.Text_Is (Data, Key, "bound")) or else
               (I = 2 and then E.Text_Is (Data, Key, "origin")) or else
               (I = 3 and then E.Text_Is (Data, Key, "catalogue_head")) or else
               (I = 4 and then E.Text_Is (Data, Key, "numerator")) or else
               (I = 5 and then E.Text_Is (Data, Key, "denominator")) or else
               (I = 6 and then E.Text_Is (Data, Key, "amount"))) then return False; end if;
            if Name = "CurrentObservation" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "scope")) or else
               (I = 1 and then E.Text_Is (Data, Key, "resource_epoch")) or else
               (I = 2 and then E.Text_Is (Data, Key, "universe_head")) or else
               (I = 3 and then E.Text_Is (Data, Key, "ledger_head")) or else
               (I = 4 and then E.Text_Is (Data, Key, "history_head")) or else
               (I = 5 and then E.Text_Is (Data, Key, "physical_head")) or else
               (I = 6 and then E.Text_Is (Data, Key, "store_genesis")) or else
               (I = 7 and then E.Text_Is (Data, Key, "store_id")) or else
               (I = 8 and then E.Text_Is (Data, Key, "root_head")) or else
               (I = 9 and then E.Text_Is (Data, Key, "prime")) or else
               (I = 10 and then E.Text_Is (Data, Key, "root_count")) or else
               (I = 11 and then E.Text_Is (Data, Key, "cause")) or else
               (I = 12 and then E.Text_Is (Data, Key, "requester")) or else
               (I = 13 and then E.Text_Is (Data, Key, "receipt")) or else
               (I = 14 and then E.Text_Is (Data, Key, "catalogue_head")) or else
               (I = 15 and then E.Text_Is (Data, Key, "observation_head"))) then return False; end if;
            if Name = "ScopedIntent" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "kind")) or else
               (I = 1 and then E.Text_Is (Data, Key, "original")) or else
               (I = 2 and then E.Text_Is (Data, Key, "expected_epoch")) or else
               (I = 3 and then E.Text_Is (Data, Key, "expected_ledger_head")) or else
               (I = 4 and then E.Text_Is (Data, Key, "request_id")) or else
               (I = 5 and then E.Text_Is (Data, Key, "cause")) or else
               (I = 6 and then E.Text_Is (Data, Key, "requester")) or else
               (I = 7 and then E.Text_Is (Data, Key, "receipt"))) then return False; end if;
            if Name = "ScopedPacket" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "before")) or else
               (I = 1 and then E.Text_Is (Data, Key, "history")) or else
               (I = 2 and then E.Text_Is (Data, Key, "rows")) or else
               (I = 3 and then E.Text_Is (Data, Key, "projection")) or else
               (I = 4 and then E.Text_Is (Data, Key, "buckets")) or else
               (I = 5 and then E.Text_Is (Data, Key, "proposed")) or else
               (I = 6 and then E.Text_Is (Data, Key, "proposed_history")) or else
               (I = 7 and then E.Text_Is (Data, Key, "proposed_rows")) or else
               (I = 8 and then E.Text_Is (Data, Key, "proposed_projection")) or else
               (I = 9 and then E.Text_Is (Data, Key, "proposed_buckets")) or else
               (I = 10 and then E.Text_Is (Data, Key, "actual_buckets")) or else
               (I = 11 and then E.Text_Is (Data, Key, "observed")) or else
               (I = 12 and then E.Text_Is (Data, Key, "facts")) or else
               (I = 13 and then E.Text_Is (Data, Key, "current")) or else
               (I = 14 and then E.Text_Is (Data, Key, "request"))) then return False; end if;
            if Name = "ScopedNativeDecision" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "entry_point")) or else
               (I = 1 and then E.Text_Is (Data, Key, "status")) or else
               (I = 2 and then E.Text_Is (Data, Key, "raw_input")) or else
               (I = 3 and then E.Text_Is (Data, Key, "raw_arena")) or else
               (I = 4 and then E.Text_Is (Data, Key, "raw_rosters")) or else
               (I = 5 and then E.Text_Is (Data, Key, "raw_output")) or else
               (I = 6 and then E.Text_Is (Data, Key, "transport_status"))) then return False; end if;
            if Name = "RunContext" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "universe")) or else
               (I = 1 and then E.Text_Is (Data, Key, "policy")) or else
               (I = 2 and then E.Text_Is (Data, Key, "resource")) or else
               (I = 3 and then E.Text_Is (Data, Key, "unit")) or else
               (I = 4 and then E.Text_Is (Data, Key, "instance")) or else
               (I = 5 and then E.Text_Is (Data, Key, "host")) or else
               (I = 6 and then E.Text_Is (Data, Key, "boot")) or else
               (I = 7 and then E.Text_Is (Data, Key, "authority")) or else
               (I = 8 and then E.Text_Is (Data, Key, "policy_epoch"))) then return False; end if;
            if Name = "RunBinding" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "reservation")) or else
               (I = 1 and then E.Text_Is (Data, Key, "operation")) or else
               (I = 2 and then E.Text_Is (Data, Key, "owner")) or else
               (I = 3 and then E.Text_Is (Data, Key, "workload")) or else
               (I = 4 and then E.Text_Is (Data, Key, "universe_head")) or else
               (I = 5 and then E.Text_Is (Data, Key, "capability")) or else
               (I = 6 and then E.Text_Is (Data, Key, "grant_use")) or else
               (I = 7 and then E.Text_Is (Data, Key, "payload")) or else
               (I = 8 and then E.Text_Is (Data, Key, "provenance")) or else
               (I = 9 and then E.Text_Is (Data, Key, "resource_epoch"))) then return False; end if;
            if Name = "RunRow" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "scope")) or else
               (I = 1 and then E.Text_Is (Data, Key, "bound")) or else
               (I = 2 and then E.Text_Is (Data, Key, "parent")) or else
               (I = 3 and then E.Text_Is (Data, Key, "kind")) or else
               (I = 4 and then E.Text_Is (Data, Key, "state")) or else
               (I = 5 and then E.Text_Is (Data, Key, "amount")) or else
               (I = 6 and then E.Text_Is (Data, Key, "observed_usage")) or else
               (I = 7 and then E.Text_Is (Data, Key, "planned_unit")) or else
               (I = 8 and then E.Text_Is (Data, Key, "actual_unit")) or else
               (I = 9 and then E.Text_Is (Data, Key, "cgroup")) or else
               (I = 10 and then E.Text_Is (Data, Key, "invocation"))) then return False; end if;
            if Name = "RunState" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "scope")) or else
               (I = 1 and then E.Text_Is (Data, Key, "resource_epoch")) or else
               (I = 2 and then E.Text_Is (Data, Key, "universe_head")) or else
               (I = 3 and then E.Text_Is (Data, Key, "ledger_head")) or else
               (I = 4 and then E.Text_Is (Data, Key, "capacity")) or else
               (I = 5 and then E.Text_Is (Data, Key, "held_total")) or else
               (I = 6 and then E.Text_Is (Data, Key, "charged_total"))) then return False; end if;
            if Name = "RunObservation" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "scope")) or else
               (I = 1 and then E.Text_Is (Data, Key, "resource_epoch")) or else
               (I = 2 and then E.Text_Is (Data, Key, "bound")) or else
               (I = 3 and then E.Text_Is (Data, Key, "actual_unit")) or else
               (I = 4 and then E.Text_Is (Data, Key, "cgroup")) or else
               (I = 5 and then E.Text_Is (Data, Key, "invocation")) or else
               (I = 6 and then E.Text_Is (Data, Key, "observation_head")) or else
               (I = 7 and then E.Text_Is (Data, Key, "observed"))) then return False; end if;
            if Name = "RunRequest" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "kind")) or else
               (I = 1 and then E.Text_Is (Data, Key, "scope")) or else
               (I = 2 and then E.Text_Is (Data, Key, "expected_epoch")) or else
               (I = 3 and then E.Text_Is (Data, Key, "expected_ledger_head")) or else
               (I = 4 and then E.Text_Is (Data, Key, "request_id")) or else
               (I = 5 and then E.Text_Is (Data, Key, "reservation")) or else
               (I = 6 and then E.Text_Is (Data, Key, "operation_id")) or else
               (I = 7 and then E.Text_Is (Data, Key, "requester")) or else
               (I = 8 and then E.Text_Is (Data, Key, "bound")) or else
               (I = 9 and then E.Text_Is (Data, Key, "new_row"))) then return False; end if;
            if Name = "PhysicalFacts" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "current")) or else
               (I = 1 and then E.Text_Is (Data, Key, "current_epoch")) or else
               (I = 2 and then E.Text_Is (Data, Key, "retained")) or else
               (I = 3 and then E.Text_Is (Data, Key, "current_universe_head")) or else
               (I = 4 and then E.Text_Is (Data, Key, "current_ledger_head")) or else
               (I = 5 and then E.Text_Is (Data, Key, "intent")) or else
               (I = 6 and then E.Text_Is (Data, Key, "dispatch")) or else
               (I = 7 and then E.Text_Is (Data, Key, "observation_head")) or else
               (I = 8 and then E.Text_Is (Data, Key, "actual_unit")) or else
               (I = 9 and then E.Text_Is (Data, Key, "cgroup")) or else
               (I = 10 and then E.Text_Is (Data, Key, "invocation")) or else
               (I = 11 and then E.Text_Is (Data, Key, "namespace")) or else
               (I = 12 and then E.Text_Is (Data, Key, "held_namespace")) or else
               (I = 13 and then E.Text_Is (Data, Key, "peer")) or else
               (I = 14 and then E.Text_Is (Data, Key, "held_peer")) or else
               (I = 15 and then E.Text_Is (Data, Key, "helper_image")) or else
               (I = 16 and then E.Text_Is (Data, Key, "expected_helper_image")) or else
               (I = 17 and then E.Text_Is (Data, Key, "challenge")) or else
               (I = 18 and then E.Text_Is (Data, Key, "held_challenge")) or else
               (I = 19 and then E.Text_Is (Data, Key, "protocol")) or else
               (I = 20 and then E.Text_Is (Data, Key, "closed_event")) or else
               (I = 21 and then E.Text_Is (Data, Key, "namespace_wait")) or else
               (I = 22 and then E.Text_Is (Data, Key, "helper_wait")) or else
               (I = 23 and then E.Text_Is (Data, Key, "cgroup_events")) or else
               (I = 24 and then E.Text_Is (Data, Key, "cgroup_type")) or else
               (I = 25 and then E.Text_Is (Data, Key, "manager_delegate")) or else
               (I = 26 and then E.Text_Is (Data, Key, "cgroup_owner")) or else
               (I = 27 and then E.Text_Is (Data, Key, "cgroup_group_write")) or else
               (I = 28 and then E.Text_Is (Data, Key, "cgroup_other_write")) or else
               (I = 29 and then E.Text_Is (Data, Key, "actual_store_genesis")) or else
               (I = 30 and then E.Text_Is (Data, Key, "actual_store_id")) or else
               (I = 31 and then E.Text_Is (Data, Key, "owner_store_genesis")) or else
               (I = 32 and then E.Text_Is (Data, Key, "owner_store_id")) or else
               (I = 33 and then E.Text_Is (Data, Key, "genesis_universe")) or else
               (I = 34 and then E.Text_Is (Data, Key, "genesis_instance")) or else
               (I = 35 and then E.Text_Is (Data, Key, "genesis_context_head")) or else
               (I = 36 and then E.Text_Is (Data, Key, "genesis_prime")) or else
               (I = 37 and then E.Text_Is (Data, Key, "genesis_root_count")) or else
               (I = 38 and then E.Text_Is (Data, Key, "phase"))) then return False; end if;
            if Name = "ActorNativeObservation" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "bound")) or else
               (I = 1 and then E.Text_Is (Data, Key, "raw_frame")) or else
               (I = 2 and then E.Text_Is (Data, Key, "raw_sender")) or else
               (I = 3 and then E.Text_Is (Data, Key, "ticket")) or else
               (I = 4 and then E.Text_Is (Data, Key, "raw_proc_status")) or else
               (I = 5 and then E.Text_Is (Data, Key, "raw_proc_cgroup")) or else
               (I = 6 and then E.Text_Is (Data, Key, "raw_proc_maps")) or else
               (I = 7 and then E.Text_Is (Data, Key, "raw_proc_cmdline")) or else
               (I = 8 and then E.Text_Is (Data, Key, "raw_pidfd_info")) or else
               (I = 9 and then E.Text_Is (Data, Key, "namespace")) or else
               (I = 10 and then E.Text_Is (Data, Key, "held_namespace")) or else
               (I = 11 and then E.Text_Is (Data, Key, "helper_image")) or else
               (I = 12 and then E.Text_Is (Data, Key, "expected_helper_image")) or else
               (I = 13 and then E.Text_Is (Data, Key, "executable_plan")) or else
               (I = 14 and then E.Text_Is (Data, Key, "expected_executable_plan")) or else
               (I = 15 and then E.Text_Is (Data, Key, "original_requester")) or else
               (I = 16 and then E.Text_Is (Data, Key, "requester_credentials")) or else
               (I = 17 and then E.Text_Is (Data, Key, "expected_requester_credentials")) or else
               (I = 18 and then E.Text_Is (Data, Key, "dispatch")) or else
               (I = 19 and then E.Text_Is (Data, Key, "running_event")) or else
               (I = 20 and then E.Text_Is (Data, Key, "expected_running_event")) or else
               (I = 21 and then E.Text_Is (Data, Key, "canonical_use_event")) or else
               (I = 22 and then E.Text_Is (Data, Key, "expected_canonical_use_event")) or else
               (I = 23 and then E.Text_Is (Data, Key, "store_genesis")) or else
               (I = 24 and then E.Text_Is (Data, Key, "expected_store_genesis")) or else
               (I = 25 and then E.Text_Is (Data, Key, "source_lease")) or else
               (I = 26 and then E.Text_Is (Data, Key, "expected_source_lease")) or else
               (I = 27 and then E.Text_Is (Data, Key, "actor_wait")) or else
               (I = 28 and then E.Text_Is (Data, Key, "helper_wait")) or else
               (I = 29 and then E.Text_Is (Data, Key, "namespace_wait")) or else
               (I = 30 and then E.Text_Is (Data, Key, "host_pid")) or else
               (I = 31 and then E.Text_Is (Data, Key, "namespace_pid")) or else
               (I = 32 and then E.Text_Is (Data, Key, "sender_uid")) or else
               (I = 33 and then E.Text_Is (Data, Key, "sender_gid")) or else
               (I = 34 and then E.Text_Is (Data, Key, "real_uid")) or else
               (I = 35 and then E.Text_Is (Data, Key, "effective_uid")) or else
               (I = 36 and then E.Text_Is (Data, Key, "saved_uid")) or else
               (I = 37 and then E.Text_Is (Data, Key, "real_gid")) or else
               (I = 38 and then E.Text_Is (Data, Key, "effective_gid")) or else
               (I = 39 and then E.Text_Is (Data, Key, "saved_gid")) or else
               (I = 40 and then E.Text_Is (Data, Key, "capability_version")) or else
               (I = 41 and then E.Text_Is (Data, Key, "effective_low")) or else
               (I = 42 and then E.Text_Is (Data, Key, "permitted_low")) or else
               (I = 43 and then E.Text_Is (Data, Key, "inheritable_low")) or else
               (I = 44 and then E.Text_Is (Data, Key, "effective_high")) or else
               (I = 45 and then E.Text_Is (Data, Key, "permitted_high")) or else
               (I = 46 and then E.Text_Is (Data, Key, "inheritable_high")) or else
               (I = 47 and then E.Text_Is (Data, Key, "securebits")) or else
               (I = 48 and then E.Text_Is (Data, Key, "no_new_privs")) or else
               (I = 49 and then E.Text_Is (Data, Key, "requester_uid")) or else
               (I = 50 and then E.Text_Is (Data, Key, "requester_gid")) or else
               (I = 51 and then E.Text_Is (Data, Key, "configured_requester_uid")) or else
               (I = 52 and then E.Text_Is (Data, Key, "workload_uid")) or else
               (I = 53 and then E.Text_Is (Data, Key, "workload_gid")) or else
               (I = 54 and then E.Text_Is (Data, Key, "proc_host_pid")) or else
               (I = 55 and then E.Text_Is (Data, Key, "proc_namespace_pid")) or else
               (I = 56 and then E.Text_Is (Data, Key, "proc_real_uid")) or else
               (I = 57 and then E.Text_Is (Data, Key, "proc_effective_uid")) or else
               (I = 58 and then E.Text_Is (Data, Key, "proc_saved_uid")) or else
               (I = 59 and then E.Text_Is (Data, Key, "proc_real_gid")) or else
               (I = 60 and then E.Text_Is (Data, Key, "proc_effective_gid")) or else
               (I = 61 and then E.Text_Is (Data, Key, "proc_saved_gid")) or else
               (I = 62 and then E.Text_Is (Data, Key, "proc_effective")) or else
               (I = 63 and then E.Text_Is (Data, Key, "proc_permitted")) or else
               (I = 64 and then E.Text_Is (Data, Key, "proc_inheritable")) or else
               (I = 65 and then E.Text_Is (Data, Key, "proc_bounding")) or else
               (I = 66 and then E.Text_Is (Data, Key, "proc_ambient")) or else
               (I = 67 and then E.Text_Is (Data, Key, "proc_no_new_privs")) or else
               (I = 68 and then E.Text_Is (Data, Key, "proc_fs_uid")) or else
               (I = 69 and then E.Text_Is (Data, Key, "proc_fs_gid"))) then return False; end if;
            if Name = "ActorCapability" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "index")) or else
               (I = 1 and then E.Text_Is (Data, Key, "bounding")) or else
               (I = 2 and then E.Text_Is (Data, Key, "ambient"))) then return False; end if;
            if Name = "ActorExecutionCrosswalk" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "resource_current")) or else
               (I = 1 and then E.Text_Is (Data, Key, "operation_policy")) or else
               (I = 2 and then E.Text_Is (Data, Key, "operation_root_set")) or else
               (I = 3 and then E.Text_Is (Data, Key, "owner_genesis")) or else
               (I = 4 and then E.Text_Is (Data, Key, "installation")) or else
               (I = 5 and then E.Text_Is (Data, Key, "gate_config")) or else
               (I = 6 and then E.Text_Is (Data, Key, "managed_observation")) or else
               (I = 7 and then E.Text_Is (Data, Key, "original_grant")) or else
               (I = 8 and then E.Text_Is (Data, Key, "complete_crosswalk")) or else
               (I = 9 and then E.Text_Is (Data, Key, "current_source")) or else
               (I = 10 and then E.Text_Is (Data, Key, "original_request")) or else
               (I = 11 and then E.Text_Is (Data, Key, "original_requester")) or else
               (I = 12 and then E.Text_Is (Data, Key, "original_transaction")) or else
               (I = 13 and then E.Text_Is (Data, Key, "preparer")) or else
               (I = 14 and then E.Text_Is (Data, Key, "selected_plan"))) then return False; end if;
            if Name = "ActorExecutionNativeDecision" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "entry_point")) or else
               (I = 1 and then E.Text_Is (Data, Key, "status")) or else
               (I = 2 and then E.Text_Is (Data, Key, "actor_input")) or else
               (I = 3 and then E.Text_Is (Data, Key, "actor_arena")) or else
               (I = 4 and then E.Text_Is (Data, Key, "actor_rosters")) or else
               (I = 5 and then E.Text_Is (Data, Key, "crosswalk")) or else
               (I = 6 and then E.Text_Is (Data, Key, "authority_input")) or else
               (I = 7 and then E.Text_Is (Data, Key, "authority_arena")) or else
               (I = 8 and then E.Text_Is (Data, Key, "authority_rosters")) or else
               (I = 9 and then E.Text_Is (Data, Key, "raw_output")) or else
               (I = 10 and then E.Text_Is (Data, Key, "transport_status"))) then return False; end if;
            if Name = "BoundUse" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "mode")) or else
               (I = 1 and then E.Text_Is (Data, Key, "operation")) or else
               (I = 2 and then E.Text_Is (Data, Key, "transaction")) or else
               (I = 3 and then E.Text_Is (Data, Key, "capability")) or else
               (I = 4 and then E.Text_Is (Data, Key, "universe_head")) or else
               (I = 5 and then E.Text_Is (Data, Key, "instance")) or else
               (I = 6 and then E.Text_Is (Data, Key, "subject")) or else
               (I = 7 and then E.Text_Is (Data, Key, "staged_root")) or else
               (I = 8 and then E.Text_Is (Data, Key, "current_requirement")) or else
               (I = 9 and then E.Text_Is (Data, Key, "resulting_requirement")) or else
               (I = 10 and then E.Text_Is (Data, Key, "requester")) or else
               (I = 11 and then E.Text_Is (Data, Key, "grant_use")) or else
               (I = 12 and then E.Text_Is (Data, Key, "policy_identity")) or else
               (I = 13 and then E.Text_Is (Data, Key, "selected_evaluation")) or else
               (I = 14 and then E.Text_Is (Data, Key, "history_head")) or else
               (I = 15 and then E.Text_Is (Data, Key, "reservation")) or else
               (I = 16 and then E.Text_Is (Data, Key, "host")) or else
               (I = 17 and then E.Text_Is (Data, Key, "before_prime")) or else
               (I = 18 and then E.Text_Is (Data, Key, "before_root")) or else
               (I = 19 and then E.Text_Is (Data, Key, "before_mapping")) or else
               (I = 20 and then E.Text_Is (Data, Key, "staged_mapping")) or else
               (I = 21 and then E.Text_Is (Data, Key, "input_snapshot")) or else
               (I = 22 and then E.Text_Is (Data, Key, "kernel_build")) or else
               (I = 23 and then E.Text_Is (Data, Key, "kernel_library")) or else
               (I = 24 and then E.Text_Is (Data, Key, "kernel_mapping")) or else
               (I = 25 and then E.Text_Is (Data, Key, "issuer_head")) or else
               (I = 26 and then E.Text_Is (Data, Key, "receipt_head")) or else
               (I = 27 and then E.Text_Is (Data, Key, "causal_head")) or else
               (I = 28 and then E.Text_Is (Data, Key, "policy_epoch")) or else
               (I = 29 and then E.Text_Is (Data, Key, "resource_epoch"))) then return False; end if;
            if Name = "NativeObservation" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "live_mapping")) or else
               (I = 1 and then E.Text_Is (Data, Key, "live_root"))) then return False; end if;
            if Name = "ProcessObservation" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "raw_status")) or else
               (I = 1 and then E.Text_Is (Data, Key, "raw_stat")) or else
               (I = 2 and then E.Text_Is (Data, Key, "raw_cgroup")) or else
               (I = 3 and then E.Text_Is (Data, Key, "raw_maps")) or else
               (I = 4 and then E.Text_Is (Data, Key, "raw_cmdline")) or else
               (I = 5 and then E.Text_Is (Data, Key, "raw_pidfd_info")) or else
               (I = 6 and then E.Text_Is (Data, Key, "namespace")) or else
               (I = 7 and then E.Text_Is (Data, Key, "cgroup")) or else
               (I = 8 and then E.Text_Is (Data, Key, "actual_unit")) or else
               (I = 9 and then E.Text_Is (Data, Key, "invocation")) or else
               (I = 10 and then E.Text_Is (Data, Key, "source_lease")) or else
               (I = 11 and then E.Text_Is (Data, Key, "pidfd_wait")) or else
               (I = 12 and then E.Text_Is (Data, Key, "host_pid")) or else
               (I = 13 and then E.Text_Is (Data, Key, "start_tick")) or else
               (I = 14 and then E.Text_Is (Data, Key, "parent_pid")) or else
               (I = 15 and then E.Text_Is (Data, Key, "parent_start_tick")) or else
               (I = 16 and then E.Text_Is (Data, Key, "real_uid")) or else
               (I = 17 and then E.Text_Is (Data, Key, "effective_uid")) or else
               (I = 18 and then E.Text_Is (Data, Key, "saved_uid")) or else
               (I = 19 and then E.Text_Is (Data, Key, "real_gid")) or else
               (I = 20 and then E.Text_Is (Data, Key, "effective_gid")) or else
               (I = 21 and then E.Text_Is (Data, Key, "saved_gid"))) then return False; end if;
            if Name = "RootController" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "bound")) or else
               (I = 1 and then E.Text_Is (Data, Key, "process")) or else
               (I = 2 and then E.Text_Is (Data, Key, "requester_uid")) or else
               (I = 3 and then E.Text_Is (Data, Key, "requester_gid")) or else
               (I = 4 and then E.Text_Is (Data, Key, "raw_manager")) or else
               (I = 5 and then E.Text_Is (Data, Key, "raw_channel")) or else
               (I = 6 and then E.Text_Is (Data, Key, "owner_endpoint")) or else
               (I = 7 and then E.Text_Is (Data, Key, "expected_owner_endpoint")) or else
               (I = 8 and then E.Text_Is (Data, Key, "source_lease")) or else
               (I = 9 and then E.Text_Is (Data, Key, "expected_source_lease")) or else
               (I = 10 and then E.Text_Is (Data, Key, "worker_image")) or else
               (I = 11 and then E.Text_Is (Data, Key, "expected_worker_image")) or else
               (I = 12 and then E.Text_Is (Data, Key, "handler_plan")) or else
               (I = 13 and then E.Text_Is (Data, Key, "expected_handler_plan")) or else
               (I = 14 and then E.Text_Is (Data, Key, "raw_request")) or else
               (I = 15 and then E.Text_Is (Data, Key, "requester")) or else
               (I = 16 and then E.Text_Is (Data, Key, "dispatch")) or else
               (I = 17 and then E.Text_Is (Data, Key, "running_event")) or else
               (I = 18 and then E.Text_Is (Data, Key, "expected_running_event")) or else
               (I = 19 and then E.Text_Is (Data, Key, "store_genesis")) or else
               (I = 20 and then E.Text_Is (Data, Key, "expected_store_genesis")) or else
               (I = 21 and then E.Text_Is (Data, Key, "current_source"))) then return False; end if;
            if Name = "TaskOrigin" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "action")) or else
               (I = 1 and then E.Text_Is (Data, Key, "root")) or else
               (I = 2 and then E.Text_Is (Data, Key, "child")) or else
               (I = 3 and then E.Text_Is (Data, Key, "task_id")) or else
               (I = 4 and then E.Text_Is (Data, Key, "root_world")) or else
               (I = 5 and then E.Text_Is (Data, Key, "child_world")) or else
               (I = 6 and then E.Text_Is (Data, Key, "root_instance")) or else
               (I = 7 and then E.Text_Is (Data, Key, "child_instance")) or else
               (I = 8 and then E.Text_Is (Data, Key, "world_store")) or else
               (I = 9 and then E.Text_Is (Data, Key, "full_world_ancestry")) or else
               (I = 10 and then E.Text_Is (Data, Key, "original_workload")) or else
               (I = 11 and then E.Text_Is (Data, Key, "sandbox")) or else
               (I = 12 and then E.Text_Is (Data, Key, "adapter")) or else
               (I = 13 and then E.Text_Is (Data, Key, "context")) or else
               (I = 14 and then E.Text_Is (Data, Key, "mission")) or else
               (I = 15 and then E.Text_Is (Data, Key, "stdin")) or else
               (I = 16 and then E.Text_Is (Data, Key, "credential_source")) or else
               (I = 17 and then E.Text_Is (Data, Key, "executable_source")) or else
               (I = 18 and then E.Text_Is (Data, Key, "configuration")) or else
               (I = 19 and then E.Text_Is (Data, Key, "owner_plan")) or else
               (I = 20 and then E.Text_Is (Data, Key, "native_cost_input")) or else
               (I = 21 and then E.Text_Is (Data, Key, "raw_request")) or else
               (I = 22 and then E.Text_Is (Data, Key, "requester")) or else
               (I = 23 and then E.Text_Is (Data, Key, "cause")) or else
               (I = 24 and then E.Text_Is (Data, Key, "root_dispatch")) or else
               (I = 25 and then E.Text_Is (Data, Key, "root_running_event")) or else
               (I = 26 and then E.Text_Is (Data, Key, "task_journal")) or else
               (I = 27 and then E.Text_Is (Data, Key, "task_intent")) or else
               (I = 28 and then E.Text_Is (Data, Key, "task_reservation_event")) or else
               (I = 29 and then E.Text_Is (Data, Key, "task_launch_event")) or else
               (I = 30 and then E.Text_Is (Data, Key, "parent_namespace_source")) or else
               (I = 31 and then E.Text_Is (Data, Key, "fd_lineage")) or else
               (I = 32 and then E.Text_Is (Data, Key, "source_lease"))) then return False; end if;
            if Name = "NamespaceObservation" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "identity")) or else
               (I = 1 and then E.Text_Is (Data, Key, "parent")) or else
               (I = 2 and then E.Text_Is (Data, Key, "raw_nsfs")) or else
               (I = 3 and then E.Text_Is (Data, Key, "raw_get_parent")) or else
               (I = 4 and then E.Text_Is (Data, Key, "source_lease"))) then return False; end if;
            if Name = "ResourceChildNativeObservation" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "entry_point")) or else
               (I = 1 and then E.Text_Is (Data, Key, "mode")) or else
               (I = 2 and then E.Text_Is (Data, Key, "status")) or else
               (I = 3 and then E.Text_Is (Data, Key, "actor_input")) or else
               (I = 4 and then E.Text_Is (Data, Key, "resource_arena")) or else
               (I = 5 and then E.Text_Is (Data, Key, "resource_rosters")) or else
               (I = 6 and then E.Text_Is (Data, Key, "authority_input")) or else
               (I = 7 and then E.Text_Is (Data, Key, "authority_arena")) or else
               (I = 8 and then E.Text_Is (Data, Key, "authority_rosters")) or else
               (I = 9 and then E.Text_Is (Data, Key, "crosswalk")) or else
               (I = 10 and then E.Text_Is (Data, Key, "child_input")) or else
               (I = 11 and then E.Text_Is (Data, Key, "raw_output")) or else
               (I = 12 and then E.Text_Is (Data, Key, "transport_status"))) then return False; end if;
            if Name = "CollapseInput" and then not
              ((I = 0 and then E.Text_Is (Data, Key, "candidate_state")) or else
               (I = 1 and then E.Text_Is (Data, Key, "phase")) or else
               (I = 2 and then E.Text_Is (Data, Key, "mode")) or else
               (I = 3 and then E.Text_Is (Data, Key, "conflicts")) or else
               (I = 4 and then E.Text_Is (Data, Key, "foreign_writes")) or else
               (I = 5 and then E.Text_Is (Data, Key, "roster_complete")) or else
               (I = 6 and then E.Text_Is (Data, Key, "staged_roster_complete")) or else
               (I = 7 and then E.Text_Is (Data, Key, "expected_parent")) or else
               (I = 8 and then E.Text_Is (Data, Key, "candidate_parent")) or else
               (I = 9 and then E.Text_Is (Data, Key, "expected_subject")) or else
               (I = 10 and then E.Text_Is (Data, Key, "evidence_subject")) or else
               (I = 11 and then E.Text_Is (Data, Key, "expected_base")) or else
               (I = 12 and then E.Text_Is (Data, Key, "candidate_base")) or else
               (I = 13 and then E.Text_Is (Data, Key, "expected_delta")) or else
               (I = 14 and then E.Text_Is (Data, Key, "candidate_delta")) or else
               (I = 15 and then E.Text_Is (Data, Key, "expected_root_set")) or else
               (I = 16 and then E.Text_Is (Data, Key, "candidate_root_set")) or else
               (I = 17 and then E.Text_Is (Data, Key, "expected_staged_root")) or else
               (I = 18 and then E.Text_Is (Data, Key, "actual_staged_root")) or else
               (I = 19 and then E.Text_Is (Data, Key, "staged_content_root")) or else
               (I = 20 and then E.Text_Is (Data, Key, "tested_root")) or else
               (I = 21 and then E.Text_Is (Data, Key, "current_requirement")) or else
               (I = 22 and then E.Text_Is (Data, Key, "resulting_requirement")) or else
               (I = 23 and then E.Text_Is (Data, Key, "evaluated_requirement")) or else
               (I = 24 and then E.Text_Is (Data, Key, "declared_verifiers")) or else
               (I = 25 and then E.Text_Is (Data, Key, "executed_verifiers")) or else
               (I = 26 and then E.Text_Is (Data, Key, "staged_evaluated_requirement")) or else
               (I = 27 and then E.Text_Is (Data, Key, "staged_executed_verifiers")) or else
               (I = 28 and then E.Text_Is (Data, Key, "staged_examined_root")) or else
               (I = 29 and then E.Text_Is (Data, Key, "expected_checkpoint")) or else
               (I = 30 and then E.Text_Is (Data, Key, "witnessed_checkpoint")) or else
               (I = 31 and then E.Text_Is (Data, Key, "registered_watch_set")) or else
               (I = 32 and then E.Text_Is (Data, Key, "watched_set")) or else
               (I = 33 and then E.Text_Is (Data, Key, "generation_before")) or else
               (I = 34 and then E.Text_Is (Data, Key, "generation_after"))) then return False; end if;
         end;
      end loop;
      return True;
   end Record_Is;
   function Null_Is (Data : E.Bytes; Item : E.Span) return Boolean is
     (P.Is_Null (Data, Item) or else (Original_Valid (Data, Item) and then E.Decode (Data, Item, E.Operation).Form = E.Null_Value));
   function Boolean_Is (Data : E.Bytes; Item : E.Span; Value : Boolean) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if P.Type_Is (Data, Item, "bool") then
         return E.Decode (Data, OA.Field (Data, Item, "value"), E.Operation).Boolean_Bit = Value;
      else return Original_Valid (Data, Item) and then View.Form = E.Boolean_Value and then View.Boolean_Bit = Value; end if;
   end Boolean_Is;
   function Stored_Bytes_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return P.Valid_Bytes (Data, Item) or else
        (Original_Valid (Data, Item) and then View.Form = E.Bytes_Value and then E.Bytes_Valid (Data, View.Payload));
   end Stored_Bytes_Valid;
   function Stored_Bytes (Data : E.Bytes; Item : E.Span) return E.Bytes
     with Global => null, Pre => Stored_Bytes_Valid (Data, Item)
   is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if P.Valid_Bytes (Data, Item) then return P.Bytes_Value (Data, Item);
      else return E.Materialize (Data, View.Payload); end if;
   end Stored_Bytes;
   function Integer_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return P.Is_Integer (Data, Item) or else
        (Original_Valid (Data, Item) and then View.Form = E.Integer_Value and then E.Bytes_Valid (Data, View.Payload));
   end Integer_Valid;
   function Integer_Magnitude (Data : E.Bytes; Item : E.Span) return E.Bytes
     with Global => null, Pre => Integer_Valid (Data, Item)
   is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if P.Is_Integer (Data, Item) then return P.Magnitude_Value (Data, Item);
      else return E.Materialize (Data, View.Payload); end if;
   end Integer_Magnitude;
   function Integer_Negative (Data : E.Bytes; Item : E.Span) return Boolean
     with Global => null, Pre => Integer_Valid (Data, Item)
   is
   begin
      if P.Is_Integer (Data, Item) then return P.Negative (Data, Item);
      else return E.Decode (Data, Item, E.Operation).Sign; end if;
   end Integer_Negative;
   function Magnitude_Matches (Arena : Q.Byte_Array; First, Length : Interfaces.Integer_64; Raw : E.Bytes) return Boolean is
   begin
      if First < 1 or else Length < 0 or else First > Interfaces.Integer_64 (Q.Byte_Index'Last)
        or else Length > Interfaces.Integer_64 (Q.Byte_Count'Last)
      then return False; end if;
      declare
         Start : constant Q.Byte_Index := Q.Byte_Index (First);
         Extent : constant Q.Byte_Count := Q.Byte_Count (Length);
      begin
         return Extent = Raw'Length and then
           (if Extent > 0 then Start >= Arena'First and then Start <= Arena'Last and then Extent - 1 <= Arena'Last - Start) and then
           (for all I in Raw'Range => Arena (Start + (I - Raw'First)) = Raw (I));
      end;
   end Magnitude_Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Id) return Boolean is
   begin
      if not W.Well_Formed (Arena, Raw) then return False; end if;
      if Raw.Present = 0 then return Null_Is (Data, Item); end if;
      return Stored_Bytes_Valid (Data, Item) and then
        Magnitude_Matches (Arena, Raw.First, Raw.Length, Stored_Bytes (Data, Item));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Quantity) return Boolean is
   begin
      return W.Well_Formed (Arena, Raw) and then Integer_Valid (Data, Item) and then
        Integer_Negative (Data, Item) = (Raw.Negative = 1) and then
        Magnitude_Matches (Arena, Raw.First, Raw.Length, Integer_Magnitude (Data, Item));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Epoch) return Boolean is
   begin
      return W.Well_Formed (Arena, Raw) and then
        (if Raw.Present = 0 then Null_Is (Data, Item) else Matches (Arena, Data, Item, Raw.Value));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.Raw_UID) return Boolean is
   begin
      if not T.Well_Formed (Raw) then return False; end if;
      if Raw.Present = 0 then return Null_Is (Data, Item) and then Raw.Value = 0; end if;
      if not Integer_Valid (Data, Item) or else Integer_Negative (Data, Item) then return False; end if;
      declare
         Mag : constant E.Bytes := Integer_Magnitude (Data, Item);
         Value : Interfaces.Unsigned_32 := Raw.Value;
      begin
         for I in Mag'Range loop
            if Interfaces.Unsigned_32 (Mag (I)) /= (Value and 255) then return False; end if;
            Value := Interfaces.Shift_Right (Value, System.Storage_Unit);
         end loop;
         return Value = 0;
      end;
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.Raw_Quantity) return Boolean is
   begin
      if not T.Well_Formed (Raw) then return False; end if;
      if Raw.Present = 0 then return Null_Is (Data, Item); end if;
      return Dictionary_Count (Data, Item) = 2 and then
        Boolean_Is (Data, Field (Data, Item, "negative"), Raw.Negative = 1) and then
        Hex_Valid (Data, Field (Data, Item, "raw")) and then
        Magnitude_Matches (Arena, Raw.First, Raw.Length, Hex_Bytes (Data, Field (Data, Item, "raw")));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.RW.Raw_Epoch) return Boolean is
   begin
      if not T.RW.Well_Formed (Arena, Raw) then return False; end if;
      if Raw.Present = 0 then return Null_Is (Data, Item); end if;
      return Integer_Valid (Data, Item) and then Integer_Negative (Data, Item) = (Raw.Negative = 1) and then
        Magnitude_Matches (Arena, Raw.First, Raw.Length, Integer_Magnitude (Data, Item));
   end Matches;
   function Digest_Matches (Data : E.Bytes; Item : E.Span; Raw : T.C.Raw_Digest; Hex : Boolean) return Boolean is
   begin
      if not T.C.Well_Formed (Raw) then return False; end if;
      if Raw.Present = 0 then return Null_Is (Data, Item) and then (for all B of Raw.Value => B = 0); end if;
      if (if Hex then not Hex_Valid (Data, Item) else not Stored_Bytes_Valid (Data, Item)) then return False; end if;
      declare
         Bytes : constant E.Bytes := (if Hex then Hex_Bytes (Data, Item) else Stored_Bytes (Data, Item));
      begin
         return Bytes'Length = Raw.Value'Length and then
           (for all I in Raw.Value'Range => Raw.Value (I) = Bytes (Bytes'First + Q.Byte_Count (I - Raw.Value'First)));
      end;
   end Digest_Matches;
   function Digest_Matches (Data : E.Bytes; Item : E.Span; Raw : T.RW.Raw_Digest; Hex : Boolean) return Boolean is
   begin
      if not T.RW.Well_Formed (Raw) then return False; end if;
      if Raw.Present = 0 then return Null_Is (Data, Item) and then (for all B of Raw.Value => B = 0); end if;
      if (if Hex then not Hex_Valid (Data, Item) else not Stored_Bytes_Valid (Data, Item)) then return False; end if;
      declare
         Bytes : constant E.Bytes := (if Hex then Hex_Bytes (Data, Item) else Stored_Bytes (Data, Item));
      begin
         return Bytes'Length = Raw.Value'Length and then
           (for all I in Raw.Value'Range => Raw.Value (I) = Bytes (Bytes'First + Q.Byte_Count (I - Raw.Value'First)));
      end;
   end Digest_Matches;
   function Operation_Name (Op : A.Operation) return String is
   begin
      case Op is
         when A.Ping => return "ping";
         when A.Status => return "status";
         when A.List_Worlds => return "list";
         when A.Show_World => return "show";
         when A.Verify_Log => return "log.verify";
         when A.Initialize => return "init";
         when A.Add_Root => return "root.add";
         when A.Remove_Root => return "root.remove";
         when A.List_Roots => return "root.list";
         when A.Fork_World => return "fork";
         when A.Race_Worlds => return "race";
         when A.Graph => return "graph";
         when A.Log => return "log";
         when A.Why => return "why";
         when A.Inspect => return "inspect";
         when A.Switch => return "switch";
         when A.Prepare_Collapse => return "collapse.prepare";
         when A.Commit_Collapse => return "collapse.commit";
         when A.Commit_Transaction => return "transaction.commit";
         when A.Abort_Transaction => return "transaction.abort";
         when A.List_Transactions => return "transaction.list";
         when A.Show_Transaction => return "transaction.show";
         when A.Prepare_Return => return "return.prepare";
         when A.Cancel_Job => return "job.cancel";
         when A.Simulate => return "simulate";
         when A.Doctor => return "doctor";
         when A.Adapters => return "adapters";
         when A.Enable_Ghost => return "ghost.enable";
         when A.Disable_Ghost => return "ghost.disable";
         when A.Ghost_Status => return "ghost.status";
         when A.Run_Ghost => return "ghost.run";
         when A.Shell_Info => return "shell.info";
         when A.Prune => return "prune";
         when A.Anchor_Status => return "anchor.status";
         when A.Revalidate => return "revalidate";
         when A.Validation_Status => return "validation.status";
         when A.Return_Services => return "return.services";
         when A.Return_Terminals => return "return.terminals";
         when A.Return_Windows => return "return.windows";
         when A.Automatic_Ghosts => return "automatic.ghosts";
         when A.Resolve_Quarantine => return "quarantine.resolve";
      end case;
   end Operation_Name;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Context) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Binding) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Row) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_State) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Native) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Request) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_State) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Scope_Frame) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Physical_Key) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Bucket) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Projection) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Current_Observation) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Intent) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Packet) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : D.Raw_Observation) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : D.Raw_Capability) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : O.Raw_Facts) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : X.Raw_Crosswalk) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Process) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Controller) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Task) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Namespace) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.RW.Raw_Binding) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.RW.Raw_Native) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.Raw_Binding) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.Raw_Grant) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.Raw_Use) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.Raw_Evidence) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.RW.Raw_Request) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.C.Raw_Row) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_History_Array) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Row_Array) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Projection_Array) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Bucket_Array) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Native_Array) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Facts_Array) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : D.Raw_Capability_Array) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : D.Raw_Group_Array) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Task_Array) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Process_Array) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Namespace_Array) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : V.Raw_Grant_Array) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : V.Raw_Use_Array) return Boolean with Global => null;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : V.Raw_Chain_Array) return Boolean with Global => null;
   function Ids_Match (Data : E.Bytes; Item : E.Span; Raw : T.Raw_Ids) return Boolean is
   begin
      return Dictionary_Count (Data, Item) = Raw'Length and then
Digest_Matches (Data, Field (Data, Item, "operation_id"), Raw (A.Operation_Id), True)
        and then Digest_Matches (Data, Field (Data, Item, "request_id"), Raw (A.Request_Id), True)
        and then Digest_Matches (Data, Field (Data, Item, "transaction"), Raw (A.Transaction), True)
        and then Digest_Matches (Data, Field (Data, Item, "universe_head"), Raw (A.Universe_Head), True)
        and then Digest_Matches (Data, Field (Data, Item, "instance"), Raw (A.Instance), True)
        and then Digest_Matches (Data, Field (Data, Item, "root_set"), Raw (A.Root_Set), True)
        and then Digest_Matches (Data, Field (Data, Item, "prime"), Raw (A.Prime), True)
        and then Digest_Matches (Data, Field (Data, Item, "policy"), Raw (A.Policy), True)
        and then Digest_Matches (Data, Field (Data, Item, "requirement"), Raw (A.Requirement), True)
        and then Digest_Matches (Data, Field (Data, Item, "issuer"), Raw (A.Issuer), True)
        and then Digest_Matches (Data, Field (Data, Item, "issuer_head"), Raw (A.Issuer_Head), True)
        and then Digest_Matches (Data, Field (Data, Item, "grant_id"), Raw (A.Grant_Id), True)
        and then Digest_Matches (Data, Field (Data, Item, "use_id"), Raw (A.Use_Id), True)
        and then Digest_Matches (Data, Field (Data, Item, "reservation"), Raw (A.Reservation), True)
        and then Digest_Matches (Data, Field (Data, Item, "resource_head"), Raw (A.Resource_Head), True)
        and then Digest_Matches (Data, Field (Data, Item, "receipt_genesis"), Raw (A.Receipt_Genesis), True)
        and then Digest_Matches (Data, Field (Data, Item, "receipt_head"), Raw (A.Receipt_Head), True)
        and then Digest_Matches (Data, Field (Data, Item, "causal_genesis"), Raw (A.Causal_Genesis), True)
        and then Digest_Matches (Data, Field (Data, Item, "causal_head"), Raw (A.Causal_Head), True)
        and then Digest_Matches (Data, Field (Data, Item, "input_snapshot"), Raw (A.Input_Snapshot), True)
        and then Digest_Matches (Data, Field (Data, Item, "kernel_build"), Raw (A.Kernel_Build), True)
        and then Digest_Matches (Data, Field (Data, Item, "kernel_library"), Raw (A.Kernel_Library), True)
        and then Digest_Matches (Data, Field (Data, Item, "kernel_mapping"), Raw (A.Kernel_Mapping), True)
        and then Digest_Matches (Data, Field (Data, Item, "provenance"), Raw (A.Provenance), True)
        and then Digest_Matches (Data, Field (Data, Item, "target"), Raw (A.Target), True)
        and then Digest_Matches (Data, Field (Data, Item, "quarantine_head"), Raw (A.Quarantine_Head), True)
        and then Digest_Matches (Data, Field (Data, Item, "original_operation"), Raw (A.Original_Operation), True);
   end Ids_Match;
   function Rights_Match (Data : E.Bytes; Item : E.Span; Raw : T.Raw_Rights) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all Op in Raw'Range => Raw (Op) <= 1 and then
           Boolean_Is (Data, Element (Data, Item, E.Count (A.Operation'Pos (Op))), Raw (Op) = 1));
   end Rights_Match;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Context) return Boolean is
   begin
      return Record_Is (Data, Item, "RunContext")
        and then Matches (Arena, Data, Field (Data, Item, "universe"), Raw.Universe)
        and then Matches (Arena, Data, Field (Data, Item, "policy"), Raw.Policy)
        and then Matches (Arena, Data, Field (Data, Item, "resource"), Raw.Resource)
        and then Matches (Arena, Data, Field (Data, Item, "unit"), Raw.Unit)
        and then Matches (Arena, Data, Field (Data, Item, "instance"), Raw.Instance)
        and then Matches (Arena, Data, Field (Data, Item, "host"), Raw.Host)
        and then Matches (Arena, Data, Field (Data, Item, "boot"), Raw.Boot)
        and then Matches (Arena, Data, Field (Data, Item, "authority"), Raw.Authority)
        and then Matches (Arena, Data, Field (Data, Item, "policy_epoch"), Raw.Policy_Epoch);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Binding) return Boolean is
   begin
      return Record_Is (Data, Item, "RunBinding")
        and then Matches (Arena, Data, Field (Data, Item, "reservation"), Raw.Reservation)
        and then Matches (Arena, Data, Field (Data, Item, "operation"), Raw.Operation)
        and then Matches (Arena, Data, Field (Data, Item, "owner"), Raw.Owner)
        and then Matches (Arena, Data, Field (Data, Item, "workload"), Raw.Workload)
        and then Matches (Arena, Data, Field (Data, Item, "universe_head"), Raw.Universe_Head)
        and then Matches (Arena, Data, Field (Data, Item, "capability"), Raw.Capability)
        and then Matches (Arena, Data, Field (Data, Item, "grant_use"), Raw.Grant_Use)
        and then Matches (Arena, Data, Field (Data, Item, "payload"), Raw.Payload)
        and then Matches (Arena, Data, Field (Data, Item, "provenance"), Raw.Provenance)
        and then Matches (Arena, Data, Field (Data, Item, "resource_epoch"), Raw.Resource_Epoch);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Row) return Boolean is
   begin
      return Record_Is (Data, Item, "RunRow")
        and then Matches (Arena, Data, Field (Data, Item, "scope"), Raw.Scope)
        and then Matches (Arena, Data, Field (Data, Item, "bound"), Raw.Bound)
        and then Matches (Arena, Data, Field (Data, Item, "parent"), Raw.Parent)
        and then Raw.Kind <= J.L.Charge_Kind'Pos (J.L.Charge_Kind'Last)
        and then Text_Is (Data, Field (Data, Item, "kind"), J.L.Charge_Kind'Image (J.L.Charge_Kind'Val (Raw.Kind)))
        and then Raw.State <= J.L.Phase'Pos (J.L.Phase'Last)
        and then Text_Is (Data, Field (Data, Item, "state"), J.L.Phase'Image (J.L.Phase'Val (Raw.State)))
        and then Matches (Arena, Data, Field (Data, Item, "amount"), Raw.Amount)
        and then Matches (Arena, Data, Field (Data, Item, "observed_usage"), Raw.Observed_Usage)
        and then Matches (Arena, Data, Field (Data, Item, "planned_unit"), Raw.Planned_Unit)
        and then Matches (Arena, Data, Field (Data, Item, "actual_unit"), Raw.Actual_Unit)
        and then Matches (Arena, Data, Field (Data, Item, "cgroup"), Raw.Cgroup)
        and then Matches (Arena, Data, Field (Data, Item, "invocation"), Raw.Invocation);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_State) return Boolean is
   begin
      return Record_Is (Data, Item, "RunState")
        and then Matches (Arena, Data, Field (Data, Item, "scope"), Raw.Scope)
        and then Matches (Arena, Data, Field (Data, Item, "resource_epoch"), Raw.Resource_Epoch)
        and then Matches (Arena, Data, Field (Data, Item, "universe_head"), Raw.Universe_Head)
        and then Matches (Arena, Data, Field (Data, Item, "ledger_head"), Raw.Ledger_Head)
        and then Matches (Arena, Data, Field (Data, Item, "capacity"), Raw.Capacity)
        and then Matches (Arena, Data, Field (Data, Item, "held_total"), Raw.Held_Total)
        and then Matches (Arena, Data, Field (Data, Item, "charged_total"), Raw.Charged_Total);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Native) return Boolean is
   begin
      return Record_Is (Data, Item, "RunObservation")
        and then Matches (Arena, Data, Field (Data, Item, "scope"), Raw.Scope)
        and then Matches (Arena, Data, Field (Data, Item, "resource_epoch"), Raw.Resource_Epoch)
        and then Matches (Arena, Data, Field (Data, Item, "bound"), Raw.Bound)
        and then Matches (Arena, Data, Field (Data, Item, "actual_unit"), Raw.Actual_Unit)
        and then Matches (Arena, Data, Field (Data, Item, "cgroup"), Raw.Cgroup)
        and then Matches (Arena, Data, Field (Data, Item, "invocation"), Raw.Invocation)
        and then Matches (Arena, Data, Field (Data, Item, "observation_head"), Raw.Observation_Head)
        and then Raw.Observed <= J.L.Liveness'Pos (J.L.Liveness'Last)
        and then Text_Is (Data, Field (Data, Item, "observed"), J.L.Liveness'Image (J.L.Liveness'Val (Raw.Observed)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Request) return Boolean is
   begin
      return Record_Is (Data, Item, "RunRequest")
        and then Raw.Kind <= J.L.Operation'Pos (J.L.Operation'Last)
        and then Text_Is (Data, Field (Data, Item, "kind"), J.L.Operation'Image (J.L.Operation'Val (Raw.Kind)))
        and then Matches (Arena, Data, Field (Data, Item, "scope"), Raw.Scope)
        and then Matches (Arena, Data, Field (Data, Item, "expected_epoch"), Raw.Expected_Epoch)
        and then Matches (Arena, Data, Field (Data, Item, "expected_ledger_head"), Raw.Expected_Ledger_Head)
        and then Matches (Arena, Data, Field (Data, Item, "request_id"), Raw.Request_Id)
        and then Matches (Arena, Data, Field (Data, Item, "reservation"), Raw.Reservation)
        and then Matches (Arena, Data, Field (Data, Item, "operation_id"), Raw.Operation_Id)
        and then Matches (Arena, Data, Field (Data, Item, "requester"), Raw.Requester)
        and then Matches (Arena, Data, Field (Data, Item, "bound"), Raw.Bound)
        and then (if Null_Is (Data, Field (Data, Item, "new_row")) then Raw.Kind /= J.L.Operation'Pos (J.L.Reserve) and then Lyt.Unused_Row (Raw.New_Row) else Matches (Arena, Data, Field (Data, Item, "new_row"), Raw.New_Row));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_State) return Boolean is
   begin
      return Record_Is (Data, Item, "ScopedState")
        and then Matches (Arena, Data, Field (Data, Item, "current"), Raw.Current)
        and then Matches (Arena, Data, Field (Data, Item, "resource_epoch"), Raw.Resource_Epoch)
        and then Matches (Arena, Data, Field (Data, Item, "universe_head"), Raw.Universe_Head)
        and then Matches (Arena, Data, Field (Data, Item, "ledger_head"), Raw.Ledger_Head)
        and then Matches (Arena, Data, Field (Data, Item, "history_head"), Raw.History_Head)
        and then Matches (Arena, Data, Field (Data, Item, "physical_head"), Raw.Physical_Head);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Scope_Frame) return Boolean is
   begin
      return Record_Is (Data, Item, "ScopeFrame")
        and then Matches (Arena, Data, Field (Data, Item, "scope"), Raw.Scope)
        and then Matches (Arena, Data, Field (Data, Item, "first_epoch"), Raw.First_Epoch)
        and then Matches (Arena, Data, Field (Data, Item, "universe_head"), Raw.Universe_Head)
        and then Matches (Arena, Data, Field (Data, Item, "frame_head"), Raw.Frame_Head)
        and then Matches (Arena, Data, Field (Data, Item, "prior_frame"), Raw.Prior_Frame)
        and then Matches (Arena, Data, Field (Data, Item, "store_genesis"), Raw.Store_Genesis)
        and then Matches (Arena, Data, Field (Data, Item, "store_id"), Raw.Store_Id)
        and then Matches (Arena, Data, Field (Data, Item, "root_head"), Raw.Root_Head)
        and then Matches (Arena, Data, Field (Data, Item, "prime"), Raw.Prime)
        and then Matches (Arena, Data, Field (Data, Item, "root_count"), Raw.Root_Count)
        and then Matches (Arena, Data, Field (Data, Item, "cause"), Raw.Cause)
        and then Matches (Arena, Data, Field (Data, Item, "requester"), Raw.Requester)
        and then Matches (Arena, Data, Field (Data, Item, "receipt"), Raw.Receipt)
        and then Matches (Arena, Data, Field (Data, Item, "catalogue_head"), Raw.Catalogue_Head)
        and then Matches (Arena, Data, Field (Data, Item, "observation_head"), Raw.Observation_Head);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Physical_Key) return Boolean is
   begin
      return Record_Is (Data, Item, "PhysicalKey")
        and then Matches (Arena, Data, Field (Data, Item, "machine"), Raw.Machine)
        and then Matches (Arena, Data, Field (Data, Item, "resource"), Raw.Resource)
        and then Matches (Arena, Data, Field (Data, Item, "unit"), Raw.Unit);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Bucket) return Boolean is
   begin
      return Record_Is (Data, Item, "PhysicalBucket")
        and then Matches (Arena, Data, Field (Data, Item, "key"), Raw.Key)
        and then Matches (Arena, Data, Field (Data, Item, "capacity"), Raw.Capacity)
        and then Matches (Arena, Data, Field (Data, Item, "held_total"), Raw.Held_Total)
        and then Matches (Arena, Data, Field (Data, Item, "charged_total"), Raw.Charged_Total)
        and then Matches (Arena, Data, Field (Data, Item, "capacity_source"), Raw.Capacity_Source)
        and then Matches (Arena, Data, Field (Data, Item, "catalogue_head"), Raw.Catalogue_Head)
        and then Matches (Arena, Data, Field (Data, Item, "observation_head"), Raw.Observation_Head);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Projection) return Boolean is
   begin
      return Record_Is (Data, Item, "PhysicalProjection")
        and then Matches (Arena, Data, Field (Data, Item, "key"), Raw.Key)
        and then Matches (Arena, Data, Field (Data, Item, "bound"), Raw.Bound)
        and then Matches (Arena, Data, Field (Data, Item, "origin"), Raw.Origin)
        and then Matches (Arena, Data, Field (Data, Item, "catalogue_head"), Raw.Catalogue_Head)
        and then Matches (Arena, Data, Field (Data, Item, "numerator"), Raw.Numerator)
        and then Matches (Arena, Data, Field (Data, Item, "denominator"), Raw.Denominator)
        and then Matches (Arena, Data, Field (Data, Item, "amount"), Raw.Amount);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Current_Observation) return Boolean is
   begin
      return Record_Is (Data, Item, "CurrentObservation")
        and then Matches (Arena, Data, Field (Data, Item, "scope"), Raw.Scope)
        and then Matches (Arena, Data, Field (Data, Item, "resource_epoch"), Raw.Resource_Epoch)
        and then Matches (Arena, Data, Field (Data, Item, "universe_head"), Raw.Universe_Head)
        and then Matches (Arena, Data, Field (Data, Item, "ledger_head"), Raw.Ledger_Head)
        and then Matches (Arena, Data, Field (Data, Item, "history_head"), Raw.History_Head)
        and then Matches (Arena, Data, Field (Data, Item, "physical_head"), Raw.Physical_Head)
        and then Matches (Arena, Data, Field (Data, Item, "store_genesis"), Raw.Store_Genesis)
        and then Matches (Arena, Data, Field (Data, Item, "store_id"), Raw.Store_Id)
        and then Matches (Arena, Data, Field (Data, Item, "root_head"), Raw.Root_Head)
        and then Matches (Arena, Data, Field (Data, Item, "prime"), Raw.Prime)
        and then Matches (Arena, Data, Field (Data, Item, "root_count"), Raw.Root_Count)
        and then Matches (Arena, Data, Field (Data, Item, "cause"), Raw.Cause)
        and then Matches (Arena, Data, Field (Data, Item, "requester"), Raw.Requester)
        and then Matches (Arena, Data, Field (Data, Item, "receipt"), Raw.Receipt)
        and then Matches (Arena, Data, Field (Data, Item, "catalogue_head"), Raw.Catalogue_Head)
        and then Matches (Arena, Data, Field (Data, Item, "observation_head"), Raw.Observation_Head);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Intent) return Boolean is
   begin
      return Record_Is (Data, Item, "ScopedIntent")
        and then Raw.Kind <= S.Action'Pos (S.Action'Last)
        and then Text_Is (Data, Field (Data, Item, "kind"), S.Action'Image (S.Action'Val (Raw.Kind)))
        and then Matches (Arena, Data, Field (Data, Item, "original"), Raw.Original)
        and then Matches (Arena, Data, Field (Data, Item, "expected_epoch"), Raw.Expected_Epoch)
        and then Matches (Arena, Data, Field (Data, Item, "expected_ledger_head"), Raw.Expected_Ledger_Head)
        and then Matches (Arena, Data, Field (Data, Item, "request_id"), Raw.Request_Id)
        and then Matches (Arena, Data, Field (Data, Item, "cause"), Raw.Cause)
        and then Matches (Arena, Data, Field (Data, Item, "requester"), Raw.Requester)
        and then Matches (Arena, Data, Field (Data, Item, "receipt"), Raw.Receipt);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Packet) return Boolean is
   begin
      return Record_Is (Data, Item, "ScopedPacket")
        and then Raw.Schema_Version = 1
        and then Matches (Arena, Data, Field (Data, Item, "before"), Raw.Before_State)
        and then Matches (Arena, Data, Field (Data, Item, "proposed"), Raw.Proposed_State)
        and then Matches (Arena, Data, Field (Data, Item, "current"), Raw.Current)
        and then Matches (Arena, Data, Field (Data, Item, "request"), Raw.Request);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : D.Raw_Observation) return Boolean is
   begin
      return Record_Is (Data, Item, "ActorNativeObservation")
        and then Matches (Arena, Data, Field (Data, Item, "bound"), Raw.Bound)
        and then Matches (Arena, Data, Field (Data, Item, "raw_frame"), Raw.Raw_Frame)
        and then Matches (Arena, Data, Field (Data, Item, "raw_sender"), Raw.Raw_Sender)
        and then Matches (Arena, Data, Field (Data, Item, "ticket"), Raw.Ticket)
        and then Matches (Arena, Data, Field (Data, Item, "raw_proc_status"), Raw.Raw_Proc_Status)
        and then Matches (Arena, Data, Field (Data, Item, "raw_proc_cgroup"), Raw.Raw_Proc_Cgroup)
        and then Matches (Arena, Data, Field (Data, Item, "raw_proc_maps"), Raw.Raw_Proc_Maps)
        and then Matches (Arena, Data, Field (Data, Item, "raw_proc_cmdline"), Raw.Raw_Proc_Cmdline)
        and then Matches (Arena, Data, Field (Data, Item, "raw_pidfd_info"), Raw.Raw_Pidfd_Info)
        and then Matches (Arena, Data, Field (Data, Item, "namespace"), Raw.Namespace)
        and then Matches (Arena, Data, Field (Data, Item, "held_namespace"), Raw.Held_Namespace)
        and then Matches (Arena, Data, Field (Data, Item, "helper_image"), Raw.Helper_Image)
        and then Matches (Arena, Data, Field (Data, Item, "expected_helper_image"), Raw.Expected_Helper_Image)
        and then Matches (Arena, Data, Field (Data, Item, "executable_plan"), Raw.Executable_Plan)
        and then Matches (Arena, Data, Field (Data, Item, "expected_executable_plan"), Raw.Expected_Executable_Plan)
        and then Matches (Arena, Data, Field (Data, Item, "original_requester"), Raw.Original_Requester)
        and then Matches (Arena, Data, Field (Data, Item, "requester_credentials"), Raw.Requester_Credentials)
        and then Matches (Arena, Data, Field (Data, Item, "expected_requester_credentials"), Raw.Expected_Requester_Credentials)
        and then Matches (Arena, Data, Field (Data, Item, "dispatch"), Raw.Dispatch)
        and then Matches (Arena, Data, Field (Data, Item, "running_event"), Raw.Running_Event)
        and then Matches (Arena, Data, Field (Data, Item, "expected_running_event"), Raw.Expected_Running_Event)
        and then Matches (Arena, Data, Field (Data, Item, "canonical_use_event"), Raw.Canonical_Use_Event)
        and then Matches (Arena, Data, Field (Data, Item, "expected_canonical_use_event"), Raw.Expected_Canonical_Use_Event)
        and then Matches (Arena, Data, Field (Data, Item, "store_genesis"), Raw.Store_Genesis)
        and then Matches (Arena, Data, Field (Data, Item, "expected_store_genesis"), Raw.Expected_Store_Genesis)
        and then Matches (Arena, Data, Field (Data, Item, "source_lease"), Raw.Source_Lease)
        and then Matches (Arena, Data, Field (Data, Item, "expected_source_lease"), Raw.Expected_Source_Lease)
        and then Matches (Arena, Data, Field (Data, Item, "actor_wait"), Raw.Actor_Wait)
        and then Matches (Arena, Data, Field (Data, Item, "helper_wait"), Raw.Helper_Wait)
        and then Matches (Arena, Data, Field (Data, Item, "namespace_wait"), Raw.Namespace_Wait)
        and then Matches (Arena, Data, Field (Data, Item, "host_pid"), Raw.Host_Pid)
        and then Matches (Arena, Data, Field (Data, Item, "namespace_pid"), Raw.Namespace_Pid)
        and then Matches (Arena, Data, Field (Data, Item, "sender_uid"), Raw.Sender_Uid)
        and then Matches (Arena, Data, Field (Data, Item, "sender_gid"), Raw.Sender_Gid)
        and then Matches (Arena, Data, Field (Data, Item, "real_uid"), Raw.Real_Uid)
        and then Matches (Arena, Data, Field (Data, Item, "effective_uid"), Raw.Effective_Uid)
        and then Matches (Arena, Data, Field (Data, Item, "saved_uid"), Raw.Saved_Uid)
        and then Matches (Arena, Data, Field (Data, Item, "real_gid"), Raw.Real_Gid)
        and then Matches (Arena, Data, Field (Data, Item, "effective_gid"), Raw.Effective_Gid)
        and then Matches (Arena, Data, Field (Data, Item, "saved_gid"), Raw.Saved_Gid)
        and then Matches (Arena, Data, Field (Data, Item, "capability_version"), Raw.Capability_Version)
        and then Matches (Arena, Data, Field (Data, Item, "effective_low"), Raw.Effective_Low)
        and then Matches (Arena, Data, Field (Data, Item, "permitted_low"), Raw.Permitted_Low)
        and then Matches (Arena, Data, Field (Data, Item, "inheritable_low"), Raw.Inheritable_Low)
        and then Matches (Arena, Data, Field (Data, Item, "effective_high"), Raw.Effective_High)
        and then Matches (Arena, Data, Field (Data, Item, "permitted_high"), Raw.Permitted_High)
        and then Matches (Arena, Data, Field (Data, Item, "inheritable_high"), Raw.Inheritable_High)
        and then Matches (Arena, Data, Field (Data, Item, "securebits"), Raw.Securebits)
        and then Matches (Arena, Data, Field (Data, Item, "no_new_privs"), Raw.No_New_Privs)
        and then Matches (Arena, Data, Field (Data, Item, "requester_uid"), Raw.Requester_Uid)
        and then Matches (Arena, Data, Field (Data, Item, "requester_gid"), Raw.Requester_Gid)
        and then Matches (Arena, Data, Field (Data, Item, "configured_requester_uid"), Raw.Configured_Requester_Uid)
        and then Matches (Arena, Data, Field (Data, Item, "workload_uid"), Raw.Workload_Uid)
        and then Matches (Arena, Data, Field (Data, Item, "workload_gid"), Raw.Workload_Gid)
        and then Matches (Arena, Data, Field (Data, Item, "proc_host_pid"), Raw.Proc_Host_Pid)
        and then Matches (Arena, Data, Field (Data, Item, "proc_namespace_pid"), Raw.Proc_Namespace_Pid)
        and then Matches (Arena, Data, Field (Data, Item, "proc_real_uid"), Raw.Proc_Real_Uid)
        and then Matches (Arena, Data, Field (Data, Item, "proc_effective_uid"), Raw.Proc_Effective_Uid)
        and then Matches (Arena, Data, Field (Data, Item, "proc_saved_uid"), Raw.Proc_Saved_Uid)
        and then Matches (Arena, Data, Field (Data, Item, "proc_real_gid"), Raw.Proc_Real_Gid)
        and then Matches (Arena, Data, Field (Data, Item, "proc_effective_gid"), Raw.Proc_Effective_Gid)
        and then Matches (Arena, Data, Field (Data, Item, "proc_saved_gid"), Raw.Proc_Saved_Gid)
        and then Matches (Arena, Data, Field (Data, Item, "proc_effective"), Raw.Proc_Effective)
        and then Matches (Arena, Data, Field (Data, Item, "proc_permitted"), Raw.Proc_Permitted)
        and then Matches (Arena, Data, Field (Data, Item, "proc_inheritable"), Raw.Proc_Inheritable)
        and then Matches (Arena, Data, Field (Data, Item, "proc_bounding"), Raw.Proc_Bounding)
        and then Matches (Arena, Data, Field (Data, Item, "proc_ambient"), Raw.Proc_Ambient)
        and then Matches (Arena, Data, Field (Data, Item, "proc_no_new_privs"), Raw.Proc_No_New_Privs)
        and then Matches (Arena, Data, Field (Data, Item, "proc_fs_uid"), Raw.Proc_Fs_Uid)
        and then Matches (Arena, Data, Field (Data, Item, "proc_fs_gid"), Raw.Proc_Fs_Gid);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : D.Raw_Capability) return Boolean is
   begin
      return Record_Is (Data, Item, "ActorCapability")
        and then Matches (Arena, Data, Field (Data, Item, "index"), Raw.Index)
        and then Matches (Arena, Data, Field (Data, Item, "bounding"), Raw.Bounding)
        and then Matches (Arena, Data, Field (Data, Item, "ambient"), Raw.Ambient);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : O.Raw_Facts) return Boolean is
   begin
      return Record_Is (Data, Item, "PhysicalFacts")
        and then Matches (Arena, Data, Field (Data, Item, "current"), Raw.Current)
        and then Matches (Arena, Data, Field (Data, Item, "current_epoch"), Raw.Current_Epoch)
        and then Matches (Arena, Data, Field (Data, Item, "retained"), Raw.Retained)
        and then Matches (Arena, Data, Field (Data, Item, "current_universe_head"), Raw.Current_Universe_Head)
        and then Matches (Arena, Data, Field (Data, Item, "current_ledger_head"), Raw.Current_Ledger_Head)
        and then Matches (Arena, Data, Field (Data, Item, "intent"), Raw.Intent)
        and then Matches (Arena, Data, Field (Data, Item, "dispatch"), Raw.Dispatch)
        and then Matches (Arena, Data, Field (Data, Item, "observation_head"), Raw.Observation_Head)
        and then Matches (Arena, Data, Field (Data, Item, "actual_unit"), Raw.Actual_Unit)
        and then Matches (Arena, Data, Field (Data, Item, "cgroup"), Raw.Cgroup)
        and then Matches (Arena, Data, Field (Data, Item, "invocation"), Raw.Invocation)
        and then Matches (Arena, Data, Field (Data, Item, "namespace"), Raw.Namespace)
        and then Matches (Arena, Data, Field (Data, Item, "held_namespace"), Raw.Held_Namespace)
        and then Matches (Arena, Data, Field (Data, Item, "peer"), Raw.Peer)
        and then Matches (Arena, Data, Field (Data, Item, "held_peer"), Raw.Held_Peer)
        and then Matches (Arena, Data, Field (Data, Item, "helper_image"), Raw.Helper_Image)
        and then Matches (Arena, Data, Field (Data, Item, "expected_helper_image"), Raw.Expected_Helper_Image)
        and then Matches (Arena, Data, Field (Data, Item, "challenge"), Raw.Challenge)
        and then Matches (Arena, Data, Field (Data, Item, "held_challenge"), Raw.Held_Challenge)
        and then Matches (Arena, Data, Field (Data, Item, "protocol"), Raw.Protocol)
        and then Matches (Arena, Data, Field (Data, Item, "closed_event"), Raw.Closed_Event)
        and then Matches (Arena, Data, Field (Data, Item, "namespace_wait"), Raw.Namespace_Wait)
        and then Matches (Arena, Data, Field (Data, Item, "helper_wait"), Raw.Helper_Wait)
        and then Matches (Arena, Data, Field (Data, Item, "cgroup_events"), Raw.Cgroup_Events)
        and then Matches (Arena, Data, Field (Data, Item, "cgroup_type"), Raw.Cgroup_Type)
        and then Matches (Arena, Data, Field (Data, Item, "manager_delegate"), Raw.Manager_Delegate)
        and then Matches (Arena, Data, Field (Data, Item, "cgroup_owner"), Raw.Cgroup_Owner)
        and then Matches (Arena, Data, Field (Data, Item, "cgroup_group_write"), Raw.Cgroup_Group_Write)
        and then Matches (Arena, Data, Field (Data, Item, "cgroup_other_write"), Raw.Cgroup_Other_Write)
        and then Matches (Arena, Data, Field (Data, Item, "actual_store_genesis"), Raw.Actual_Store_Genesis)
        and then Matches (Arena, Data, Field (Data, Item, "actual_store_id"), Raw.Actual_Store_Id)
        and then Matches (Arena, Data, Field (Data, Item, "owner_store_genesis"), Raw.Owner_Store_Genesis)
        and then Matches (Arena, Data, Field (Data, Item, "owner_store_id"), Raw.Owner_Store_Id)
        and then Matches (Arena, Data, Field (Data, Item, "genesis_universe"), Raw.Genesis_Universe)
        and then Matches (Arena, Data, Field (Data, Item, "genesis_instance"), Raw.Genesis_Instance)
        and then Matches (Arena, Data, Field (Data, Item, "genesis_context_head"), Raw.Genesis_Context_Head)
        and then Matches (Arena, Data, Field (Data, Item, "genesis_prime"), Raw.Genesis_Prime)
        and then Matches (Arena, Data, Field (Data, Item, "genesis_root_count"), Raw.Genesis_Root_Count)
        and then Raw.Phase <= O.K.Journal_Phase'Pos (O.K.Journal_Phase'Last)
        and then Text_Is (Data, Field (Data, Item, "phase"), O.K.Journal_Phase'Image (O.K.Journal_Phase'Val (Raw.Phase)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : X.Raw_Crosswalk) return Boolean is
   begin
      return Record_Is (Data, Item, "ActorExecutionCrosswalk")
        and then Matches (Arena, Data, Field (Data, Item, "resource_current"), Raw.Resource_Current)
        and then Digest_Matches (Data, Field (Data, Item, "operation_policy"), Raw.Operation_Policy, False)
        and then Digest_Matches (Data, Field (Data, Item, "operation_root_set"), Raw.Operation_Root_Set, False)
        and then Matches (Arena, Data, Field (Data, Item, "owner_genesis"), Raw.Owner_Genesis)
        and then Matches (Arena, Data, Field (Data, Item, "installation"), Raw.Installation)
        and then Matches (Arena, Data, Field (Data, Item, "gate_config"), Raw.Gate_Config)
        and then Matches (Arena, Data, Field (Data, Item, "managed_observation"), Raw.Managed_Observation)
        and then Matches (Arena, Data, Field (Data, Item, "original_grant"), Raw.Original_Grant)
        and then Matches (Arena, Data, Field (Data, Item, "complete_crosswalk"), Raw.Complete_Crosswalk)
        and then Matches (Arena, Data, Field (Data, Item, "current_source"), Raw.Current_Source)
        and then Matches (Arena, Data, Field (Data, Item, "original_request"), Raw.Original_Request)
        and then Matches (Arena, Data, Field (Data, Item, "original_requester"), Raw.Original_Requester)
        and then Matches (Arena, Data, Field (Data, Item, "original_transaction"), Raw.Original_Transaction)
        and then Matches (Arena, Data, Field (Data, Item, "preparer"), Raw.Preparer)
        and then Matches (Arena, Data, Field (Data, Item, "selected_plan"), Raw.Selected_Plan);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Process) return Boolean is
   begin
      return Record_Is (Data, Item, "ProcessObservation")
        and then Matches (Arena, Data, Field (Data, Item, "raw_status"), Raw.raw_status)
        and then Matches (Arena, Data, Field (Data, Item, "raw_stat"), Raw.raw_stat)
        and then Matches (Arena, Data, Field (Data, Item, "raw_cgroup"), Raw.raw_cgroup)
        and then Matches (Arena, Data, Field (Data, Item, "raw_maps"), Raw.raw_maps)
        and then Matches (Arena, Data, Field (Data, Item, "raw_cmdline"), Raw.raw_cmdline)
        and then Matches (Arena, Data, Field (Data, Item, "raw_pidfd_info"), Raw.raw_pidfd_info)
        and then Matches (Arena, Data, Field (Data, Item, "namespace"), Raw.namespace)
        and then Matches (Arena, Data, Field (Data, Item, "cgroup"), Raw.cgroup)
        and then Matches (Arena, Data, Field (Data, Item, "actual_unit"), Raw.actual_unit)
        and then Matches (Arena, Data, Field (Data, Item, "invocation"), Raw.invocation)
        and then Matches (Arena, Data, Field (Data, Item, "source_lease"), Raw.source_lease)
        and then Matches (Arena, Data, Field (Data, Item, "pidfd_wait"), Raw.pidfd_wait)
        and then Matches (Arena, Data, Field (Data, Item, "host_pid"), Raw.host_pid)
        and then Matches (Arena, Data, Field (Data, Item, "start_tick"), Raw.start_tick)
        and then Matches (Arena, Data, Field (Data, Item, "parent_pid"), Raw.parent_pid)
        and then Matches (Arena, Data, Field (Data, Item, "parent_start_tick"), Raw.parent_start_tick)
        and then Matches (Arena, Data, Field (Data, Item, "real_uid"), Raw.real_uid)
        and then Matches (Arena, Data, Field (Data, Item, "effective_uid"), Raw.effective_uid)
        and then Matches (Arena, Data, Field (Data, Item, "saved_uid"), Raw.saved_uid)
        and then Matches (Arena, Data, Field (Data, Item, "real_gid"), Raw.real_gid)
        and then Matches (Arena, Data, Field (Data, Item, "effective_gid"), Raw.effective_gid)
        and then Matches (Arena, Data, Field (Data, Item, "saved_gid"), Raw.saved_gid);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Controller) return Boolean is
   begin
      return Record_Is (Data, Item, "RootController")
        and then Matches (Arena, Data, Field (Data, Item, "bound"), Raw.Bound)
        and then Matches (Arena, Data, Field (Data, Item, "process"), Raw.Process)
        and then Matches (Arena, Data, Field (Data, Item, "requester_uid"), Raw.Requester_Uid)
        and then Matches (Arena, Data, Field (Data, Item, "requester_gid"), Raw.Requester_Gid)
        and then Matches (Arena, Data, Field (Data, Item, "raw_manager"), Raw.raw_manager)
        and then Matches (Arena, Data, Field (Data, Item, "raw_channel"), Raw.raw_channel)
        and then Matches (Arena, Data, Field (Data, Item, "owner_endpoint"), Raw.owner_endpoint)
        and then Matches (Arena, Data, Field (Data, Item, "expected_owner_endpoint"), Raw.expected_owner_endpoint)
        and then Matches (Arena, Data, Field (Data, Item, "source_lease"), Raw.source_lease)
        and then Matches (Arena, Data, Field (Data, Item, "expected_source_lease"), Raw.expected_source_lease)
        and then Matches (Arena, Data, Field (Data, Item, "worker_image"), Raw.worker_image)
        and then Matches (Arena, Data, Field (Data, Item, "expected_worker_image"), Raw.expected_worker_image)
        and then Matches (Arena, Data, Field (Data, Item, "handler_plan"), Raw.handler_plan)
        and then Matches (Arena, Data, Field (Data, Item, "expected_handler_plan"), Raw.expected_handler_plan)
        and then Matches (Arena, Data, Field (Data, Item, "raw_request"), Raw.raw_request)
        and then Matches (Arena, Data, Field (Data, Item, "requester"), Raw.requester)
        and then Matches (Arena, Data, Field (Data, Item, "dispatch"), Raw.dispatch)
        and then Matches (Arena, Data, Field (Data, Item, "running_event"), Raw.running_event)
        and then Matches (Arena, Data, Field (Data, Item, "expected_running_event"), Raw.expected_running_event)
        and then Matches (Arena, Data, Field (Data, Item, "store_genesis"), Raw.store_genesis)
        and then Matches (Arena, Data, Field (Data, Item, "expected_store_genesis"), Raw.expected_store_genesis)
        and then Matches (Arena, Data, Field (Data, Item, "current_source"), Raw.current_source);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Task) return Boolean is
   begin
      return Record_Is (Data, Item, "TaskOrigin")
        and then Raw.Action <= A.Operation'Pos (A.Operation'Last)
        and then Text_Is (Data, Field (Data, Item, "action"), Operation_Name (A.Operation'Val (Raw.Action)))
        and then Matches (Arena, Data, Field (Data, Item, "root"), Raw.Root)
        and then Matches (Arena, Data, Field (Data, Item, "child"), Raw.Child)
        and then Matches (Arena, Data, Field (Data, Item, "task_id"), Raw.task_id)
        and then Matches (Arena, Data, Field (Data, Item, "root_world"), Raw.root_world)
        and then Matches (Arena, Data, Field (Data, Item, "child_world"), Raw.child_world)
        and then Matches (Arena, Data, Field (Data, Item, "root_instance"), Raw.root_instance)
        and then Matches (Arena, Data, Field (Data, Item, "child_instance"), Raw.child_instance)
        and then Matches (Arena, Data, Field (Data, Item, "world_store"), Raw.world_store)
        and then Matches (Arena, Data, Field (Data, Item, "full_world_ancestry"), Raw.full_world_ancestry)
        and then Matches (Arena, Data, Field (Data, Item, "original_workload"), Raw.original_workload)
        and then Matches (Arena, Data, Field (Data, Item, "sandbox"), Raw.sandbox)
        and then Matches (Arena, Data, Field (Data, Item, "adapter"), Raw.adapter)
        and then Matches (Arena, Data, Field (Data, Item, "context"), Raw.context)
        and then Matches (Arena, Data, Field (Data, Item, "mission"), Raw.mission)
        and then Matches (Arena, Data, Field (Data, Item, "stdin"), Raw.stdin)
        and then Matches (Arena, Data, Field (Data, Item, "credential_source"), Raw.credential_source)
        and then Matches (Arena, Data, Field (Data, Item, "executable_source"), Raw.executable_source)
        and then Matches (Arena, Data, Field (Data, Item, "configuration"), Raw.configuration)
        and then Matches (Arena, Data, Field (Data, Item, "owner_plan"), Raw.owner_plan)
        and then Matches (Arena, Data, Field (Data, Item, "native_cost_input"), Raw.native_cost_input)
        and then Matches (Arena, Data, Field (Data, Item, "raw_request"), Raw.raw_request)
        and then Matches (Arena, Data, Field (Data, Item, "requester"), Raw.requester)
        and then Matches (Arena, Data, Field (Data, Item, "cause"), Raw.cause)
        and then Matches (Arena, Data, Field (Data, Item, "root_dispatch"), Raw.root_dispatch)
        and then Matches (Arena, Data, Field (Data, Item, "root_running_event"), Raw.root_running_event)
        and then Matches (Arena, Data, Field (Data, Item, "task_journal"), Raw.task_journal)
        and then Matches (Arena, Data, Field (Data, Item, "task_intent"), Raw.task_intent)
        and then Matches (Arena, Data, Field (Data, Item, "task_reservation_event"), Raw.task_reservation_event)
        and then Matches (Arena, Data, Field (Data, Item, "task_launch_event"), Raw.task_launch_event)
        and then Matches (Arena, Data, Field (Data, Item, "parent_namespace_source"), Raw.parent_namespace_source)
        and then Matches (Arena, Data, Field (Data, Item, "fd_lineage"), Raw.fd_lineage)
        and then Matches (Arena, Data, Field (Data, Item, "source_lease"), Raw.source_lease);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Namespace) return Boolean is
   begin
      return Record_Is (Data, Item, "NamespaceObservation")
        and then Matches (Arena, Data, Field (Data, Item, "identity"), Raw.identity)
        and then Matches (Arena, Data, Field (Data, Item, "parent"), Raw.parent)
        and then Matches (Arena, Data, Field (Data, Item, "raw_nsfs"), Raw.raw_nsfs)
        and then Matches (Arena, Data, Field (Data, Item, "raw_get_parent"), Raw.raw_get_parent)
        and then Matches (Arena, Data, Field (Data, Item, "source_lease"), Raw.source_lease);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.RW.Raw_Binding) return Boolean is
   begin
      return Record_Is (Data, Item, "BoundUse")
        and then Raw.Mode <= T.RW.R.Promotion_Mode'Pos (T.RW.R.Promotion_Mode'Last)
        and then Text_Is (Data, Field (Data, Item, "mode"), T.RW.R.Promotion_Mode'Image (T.RW.R.Promotion_Mode'Val (Raw.Mode)))
        and then Digest_Matches (Data, Field (Data, Item, "operation"), Raw.Operation, False)
        and then Digest_Matches (Data, Field (Data, Item, "transaction"), Raw.Transaction, False)
        and then Digest_Matches (Data, Field (Data, Item, "capability"), Raw.Capability, False)
        and then Digest_Matches (Data, Field (Data, Item, "universe_head"), Raw.Universe_Head, False)
        and then Digest_Matches (Data, Field (Data, Item, "instance"), Raw.Instance, False)
        and then Digest_Matches (Data, Field (Data, Item, "subject"), Raw.Subject, False)
        and then Digest_Matches (Data, Field (Data, Item, "staged_root"), Raw.Staged_Root, False)
        and then Digest_Matches (Data, Field (Data, Item, "current_requirement"), Raw.Current_Requirement, False)
        and then Digest_Matches (Data, Field (Data, Item, "resulting_requirement"), Raw.Resulting_Requirement, False)
        and then Digest_Matches (Data, Field (Data, Item, "requester"), Raw.Requester, False)
        and then Digest_Matches (Data, Field (Data, Item, "grant_use"), Raw.Grant_Use, False)
        and then Digest_Matches (Data, Field (Data, Item, "policy_identity"), Raw.Policy_Identity, False)
        and then Digest_Matches (Data, Field (Data, Item, "selected_evaluation"), Raw.Selected_Evaluation, False)
        and then Digest_Matches (Data, Field (Data, Item, "history_head"), Raw.History_Head, False)
        and then Digest_Matches (Data, Field (Data, Item, "reservation"), Raw.Reservation, False)
        and then Digest_Matches (Data, Field (Data, Item, "host"), Raw.Host, False)
        and then Digest_Matches (Data, Field (Data, Item, "before_prime"), Raw.Before_Prime, False)
        and then Digest_Matches (Data, Field (Data, Item, "before_root"), Raw.Before_Root, False)
        and then Digest_Matches (Data, Field (Data, Item, "before_mapping"), Raw.Before_Mapping, False)
        and then Digest_Matches (Data, Field (Data, Item, "staged_mapping"), Raw.Staged_Mapping, False)
        and then Digest_Matches (Data, Field (Data, Item, "input_snapshot"), Raw.Input_Snapshot, False)
        and then Digest_Matches (Data, Field (Data, Item, "kernel_build"), Raw.Kernel_Build, False)
        and then Digest_Matches (Data, Field (Data, Item, "kernel_library"), Raw.Kernel_Library, False)
        and then Digest_Matches (Data, Field (Data, Item, "kernel_mapping"), Raw.Kernel_Mapping, False)
        and then Digest_Matches (Data, Field (Data, Item, "issuer_head"), Raw.Issuer_Head, False)
        and then Digest_Matches (Data, Field (Data, Item, "receipt_head"), Raw.Receipt_Head, False)
        and then Digest_Matches (Data, Field (Data, Item, "causal_head"), Raw.Causal_Head, False)
        and then Matches (Arena, Data, Field (Data, Item, "policy_epoch"), Raw.Policy_Epoch)
        and then Matches (Arena, Data, Field (Data, Item, "resource_epoch"), Raw.Resource_Epoch);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.RW.Raw_Native) return Boolean is
   begin
      return Record_Is (Data, Item, "NativeObservation")
        and then Digest_Matches (Data, Field (Data, Item, "live_mapping"), Raw.Live_Mapping, False)
        and then Digest_Matches (Data, Field (Data, Item, "live_root"), Raw.Live_Root, False);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.Raw_Binding) return Boolean is
   begin
      return Dictionary_Count (Data, Item) = 8
        and then Raw.Action <= A.Operation'Pos (A.Operation'Last)
        and then Text_Is (Data, Field (Data, Item, "action"), Operation_Name (A.Operation'Val (Raw.Action)))
        and then Ids_Match (Data, Field (Data, Item, "id"), Raw.Id)
        and then Matches (Arena, Data, Field (Data, Item, "peer"), Raw.Peer)
        and then Matches (Arena, Data, Field (Data, Item, "preparer"), Raw.Preparer)
        and then Matches (Arena, Data, Field (Data, Item, "owner"), Raw.Owner)
        and then Matches (Arena, Data, Field (Data, Item, "target_owner"), Raw.Target_Owner)
        and then Matches (Arena, Data, Field (Data, Item, "policy_epoch"), Raw.Policy_Epoch)
        and then Matches (Arena, Data, Field (Data, Item, "resource_epoch"), Raw.Resource_Epoch);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.Raw_Grant) return Boolean is
   begin
      return Dictionary_Count (Data, Item) = 14
        and then Digest_Matches (Data, Field (Data, Item, "id"), Raw.Id, True)
        and then Digest_Matches (Data, Field (Data, Item, "parent"), Raw.Parent, True)
        and then Digest_Matches (Data, Field (Data, Item, "issuer"), Raw.Issuer, True)
        and then Digest_Matches (Data, Field (Data, Item, "instance"), Raw.Instance, True)
        and then Digest_Matches (Data, Field (Data, Item, "root_set"), Raw.Root_Set, True)
        and then Digest_Matches (Data, Field (Data, Item, "policy"), Raw.Policy, True)
        and then Matches (Arena, Data, Field (Data, Item, "subject"), Raw.Subject)
        and then Matches (Arena, Data, Field (Data, Item, "owner"), Raw.Owner)
        and then Rights_Match (Data, Field (Data, Item, "allowed"), Raw.Allowed)
        and then Raw.State <= A.Grant_State'Pos (A.Grant_State'Last)
        and then Text_Is (Data, Field (Data, Item, "state"), A.Grant_State'Image (A.Grant_State'Val (Raw.State)))
        and then Matches (Arena, Data, Field (Data, Item, "epoch"), Raw.Epoch)
        and then Matches (Arena, Data, Field (Data, Item, "ceiling"), Raw.Ceiling)
        and then Matches (Arena, Data, Field (Data, Item, "issued_at"), Raw.Issued_At)
        and then Matches (Arena, Data, Field (Data, Item, "expires_at"), Raw.Expires_At);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.Raw_Use) return Boolean is
   begin
      return Dictionary_Count (Data, Item) = 2
        and then Matches (Arena, Data, Field (Data, Item, "bound"), Raw.Bound)
        and then Raw.State <= A.Use_State'Pos (A.Use_State'Last)
        and then Text_Is (Data, Field (Data, Item, "state"), A.Use_State'Image (A.Use_State'Val (Raw.State)));
   end Matches;
   function Effect_Material_Matches
     (Arena, Data : E.Bytes; Item : E.Span; Raw : T.Raw_Evidence) return Boolean is
   begin
      if Raw.Effect_Material_Length = 0 then
         return Raw.Effect_Material_First = 1 and then
           (Item.Length = 0 or else Null_Is (Data, Item));
      end if;
      if Raw.Effect_Material_First < 1 or else Raw.Effect_Material_Length < 0
        or else Q.Byte_Count (Raw.Effect_Material_First) not in Arena'Range
        or else Q.Byte_Count (Raw.Effect_Material_Length) > Arena'Last - Q.Byte_Count (Raw.Effect_Material_First) + 1
        or else not Stored_Bytes_Valid (Data, Item) then return False; end if;
      declare
         Source : constant E.Bytes := Stored_Bytes (Data, Item);
         Encoded : constant E.Span := (Q.Byte_Index (Raw.Effect_Material_First), Q.Byte_Count (Raw.Effect_Material_Length));
      begin
         return Original_Valid (Arena, Encoded) and then Source'Length = Encoded.Length
           and then (for all I in Source'Range => Source (I) = Arena (Encoded.First + (I - Source'First)));
      end;
   end Effect_Material_Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.Raw_Evidence) return Boolean is
   begin
      return (Dictionary_Count (Data, Item) = 11 or else (Dictionary_Count (Data, Item) = 10 and then Raw.Effect_Material_Length = 0))
        and then Effect_Material_Matches (Arena, Data, Field (Data, Item, "effect_material"), Raw)
        and then Matches (Arena, Data, Field (Data, Item, "effect_binding"), Raw.Effect_Binding)
        and then Digest_Matches (Data, Field (Data, Item, "actual_receipt_root"), Raw.Actual_Receipt_Root, True)
        and then Digest_Matches (Data, Field (Data, Item, "actual_causal_root"), Raw.Actual_Causal_Root, True)
        and then Matches (Arena, Data, Field (Data, Item, "no_effect_binding"), Raw.No_Effect_Binding)
        and then Matches (Arena, Data, Field (Data, Item, "owner_resolution"), Raw.Owner_Resolution)
        and then Digest_Matches (Data, Field (Data, Item, "quarantine_head"), Raw.Quarantine_Head, True)
        and then Digest_Matches (Data, Field (Data, Item, "witnessed_receipt_head"), Raw.Witnessed_Receipt_Head, True)
        and then Digest_Matches (Data, Field (Data, Item, "witnessed_causal_head"), Raw.Witnessed_Causal_Head, True)
        and then Matches (Arena, Data, Field (Data, Item, "recovery"), Raw.Recovery)
        and then Digest_Matches (Data, Field (Data, Item, "original_use"), Raw.Original_Use, True);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.RW.Raw_Request) return Boolean is
   begin
      return Dictionary_Count (Data, Item) = 4
        and then Raw.Schema_Version = 3
        and then Raw.State = 1
        and then Raw.Fresh = 1
        and then Raw.Grant_Eligible = 0
        and then Raw.Historical <= T.RW.R.Historical_Verdict'Pos (T.RW.R.Historical_Verdict'Last)
        and then Text_Is (Data, Field (Data, Item, "historical"), T.RW.R.Historical_Verdict'Image (T.RW.R.Historical_Verdict'Val (Raw.Historical)))
        and then Matches (Arena, Data, Field (Data, Item, "issued"), Raw.Issued_Binding)
        and then Matches (Arena, Data, Field (Data, Item, "recovered"), Raw.Recovered_Binding)
        and then Matches (Arena, Data, Field (Data, Item, "native"), Raw.Native);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : T.C.Raw_Row) return Boolean is
   begin
      return Dictionary_Count (Data, Item) = 4
        and then Digest_Matches (Data, Field (Data, Item, "previous"), Raw.Previous, True)
        and then Digest_Matches (Data, Field (Data, Item, "actual_payload_root"), Raw.Actual_Payload_Root, True)
        and then Digest_Matches (Data, Field (Data, Item, "stored_payload_root"), Raw.Stored_Payload_Root, True)
        and then Digest_Matches (Data, Field (Data, Item, "stored_head"), Raw.Stored_Head, True);
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_History_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Row_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Projection_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Bucket_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : W.Raw_Native_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Facts_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : D.Raw_Capability_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : D.Raw_Group_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Task_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Process_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : Y.Raw_Namespace_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : V.Raw_Grant_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : V.Raw_Use_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : V.Raw_Chain_Array) return Boolean is
   begin
      return Sequence_Count (Data, Item) = Raw'Length and then
        (for all I in Raw'Range => Matches (Arena, Data, Element (Data, Item, I - Raw'First), Raw (I)));
   end Matches;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : N.Raw_History_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (N.Raw_Scope_Frame'Size / System.Storage_Unit) = 0 and then Bytes'Length / (N.Raw_Scope_Frame'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := N.Raw_Scope_Frame'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : W.Raw_Row_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (W.Raw_Row'Size / System.Storage_Unit) = 0 and then Bytes'Length / (W.Raw_Row'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := W.Raw_Row'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : N.Raw_Projection_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (N.Raw_Projection'Size / System.Storage_Unit) = 0 and then Bytes'Length / (N.Raw_Projection'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := N.Raw_Projection'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : N.Raw_Bucket_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (N.Raw_Bucket'Size / System.Storage_Unit) = 0 and then Bytes'Length / (N.Raw_Bucket'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := N.Raw_Bucket'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : W.Raw_Native_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (W.Raw_Native'Size / System.Storage_Unit) = 0 and then Bytes'Length / (W.Raw_Native'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := W.Raw_Native'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : N.Raw_Facts_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (O.Raw_Facts'Size / System.Storage_Unit) = 0 and then Bytes'Length / (O.Raw_Facts'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := O.Raw_Facts'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : D.Raw_Capability_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (D.Raw_Capability'Size / System.Storage_Unit) = 0 and then Bytes'Length / (D.Raw_Capability'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := D.Raw_Capability'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : D.Raw_Group_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (W.Raw_Quantity'Size / System.Storage_Unit) = 0 and then Bytes'Length / (W.Raw_Quantity'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := W.Raw_Quantity'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : Y.Raw_Task_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (Y.Raw_Task'Size / System.Storage_Unit) = 0 and then Bytes'Length / (Y.Raw_Task'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := Y.Raw_Task'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : Y.Raw_Process_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (Y.Raw_Process'Size / System.Storage_Unit) = 0 and then Bytes'Length / (Y.Raw_Process'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := Y.Raw_Process'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : Y.Raw_Namespace_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (Y.Raw_Namespace'Size / System.Storage_Unit) = 0 and then Bytes'Length / (Y.Raw_Namespace'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := Y.Raw_Namespace'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : V.Raw_Grant_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (T.Raw_Grant'Size / System.Storage_Unit) = 0 and then Bytes'Length / (T.Raw_Grant'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := T.Raw_Grant'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : V.Raw_Use_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (T.Raw_Use'Size / System.Storage_Unit) = 0 and then Bytes'Length / (T.Raw_Use'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := T.Raw_Use'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Padding_Valid (Bytes : Q.Byte_Array; Raw : V.Raw_Chain_Array) return Boolean
     with Global => null, Pre => Bytes'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) = 0 and then Bytes'Length / (T.C.Raw_Row'Size / System.Storage_Unit) = Raw'Length
   is
      Stride : constant Q.Byte_Count := T.C.Raw_Row'Size / System.Storage_Unit;
   begin
      for I in Raw'Range loop
         if not RD.Source_Padding_Valid (Bytes (Bytes'First + (I - Raw'First) * Stride .. Bytes'First + (I - Raw'First) * Stride + Stride - 1), Raw (I)) then return False; end if;
      end loop;
      return True;
   end Padding_Valid;
   function Zero_Bytes (Bytes : Q.Byte_Array) return Boolean is ((for all B of Bytes => B = 0));
   function Authority_Matches
     (Arena, Data : E.Bytes; Item : E.Span; Raw : T.Raw_Input;
      Grants : V.Raw_Grant_Array; Uses : V.Raw_Use_Array;
      Receipts, Events : V.Raw_Chain_Array; Expected_Count : E.Count := 7) return Boolean is
   begin
      return Dictionary_Count (Data, Item) = Expected_Count and then Raw.Schema = 1
        and then Matches (Arena, Data, Field (Data, Item, "binding"), Raw.Bound)
        and then Matches (Arena, Data, Field (Data, Item, "now"), Raw.Now)
        and then Matches (Arena, Data, Field (Data, Item, "evidence"), Raw.Facts)
        and then Matches (Arena, Data, Field (Data, Item, "grants"), Grants)
        and then Matches (Arena, Data, Field (Data, Item, "uses"), Uses)
        and then Matches (Arena, Data, Field (Data, Item, "receipts"), Receipts)
        and then Matches (Arena, Data, Field (Data, Item, "events"), Events);
   end Authority_Matches;
   function Packet_Matches
     (Arena, Data : E.Bytes; Item : E.Span; Raw : N.Raw_Packet;
      Copy_history : N.Raw_History_Array;
      Copy_proposed_history : N.Raw_History_Array;
      Copy_rows : W.Raw_Row_Array;
      Copy_proposed_rows : W.Raw_Row_Array;
      Copy_projection : N.Raw_Projection_Array;
      Copy_proposed_projection : N.Raw_Projection_Array;
      Copy_buckets : N.Raw_Bucket_Array;
      Copy_proposed_buckets : N.Raw_Bucket_Array;
      Copy_actual_buckets : N.Raw_Bucket_Array;
      Copy_observed : W.Raw_Native_Array;
      Copy_facts : N.Raw_Facts_Array) return Boolean is
   begin
      return Matches (Arena, Data, Item, Raw)
        and then Matches (Arena, Data, Field (Data, Item, "history"), Copy_history)
        and then Matches (Arena, Data, Field (Data, Item, "proposed_history"), Copy_proposed_history)
        and then Matches (Arena, Data, Field (Data, Item, "rows"), Copy_rows)
        and then Matches (Arena, Data, Field (Data, Item, "proposed_rows"), Copy_proposed_rows)
        and then Matches (Arena, Data, Field (Data, Item, "projection"), Copy_projection)
        and then Matches (Arena, Data, Field (Data, Item, "proposed_projection"), Copy_proposed_projection)
        and then Matches (Arena, Data, Field (Data, Item, "buckets"), Copy_buckets)
        and then Matches (Arena, Data, Field (Data, Item, "proposed_buckets"), Copy_proposed_buckets)
        and then Matches (Arena, Data, Field (Data, Item, "actual_buckets"), Copy_actual_buckets)
        and then Matches (Arena, Data, Field (Data, Item, "observed"), Copy_observed)
        and then Matches (Arena, Data, Field (Data, Item, "facts"), Copy_facts);
   end Packet_Matches;
   function Root_Material_Matches
     (Data : E.Bytes; Observation_Archive, Material_Archive : E.Span) return Boolean
   is
      actor_input_Archive : constant E.Span := Field (Data, Observation_Archive, "actor_input");
      resource_arena_Archive : constant E.Span := Field (Data, Observation_Archive, "resource_arena");
      resource_rosters_Archive : constant E.Span := Field (Data, Observation_Archive, "resource_rosters");
      authority_input_Archive : constant E.Span := Field (Data, Observation_Archive, "authority_input");
      authority_arena_Archive : constant E.Span := Field (Data, Observation_Archive, "authority_arena");
      authority_rosters_Archive : constant E.Span := Field (Data, Observation_Archive, "authority_rosters");
      crosswalk_Archive : constant E.Span := Field (Data, Observation_Archive, "crosswalk");
      child_input_Archive : constant E.Span := Field (Data, Observation_Archive, "child_input");
      raw_output_Archive : constant E.Span := Field (Data, Observation_Archive, "raw_output");
   begin
      if not Archive_Record_Is (Data, Observation_Archive, "ResourceChildNativeObservation")
        or else not Bytes_Shape (Data, actor_input_Archive, D.Raw_Packet'Size / System.Storage_Unit)
        or else not Bytes_Shape (Data, authority_input_Archive, T.Raw_Input'Size / System.Storage_Unit)
        or else not Bytes_Shape (Data, crosswalk_Archive, X.Raw_Crosswalk'Size / System.Storage_Unit)
        or else not Bytes_Shape (Data, child_input_Archive, Y.Raw_Input'Size / System.Storage_Unit)
        or else not Archive_Bytes_Valid (Data, resource_arena_Archive)
        or else not Archive_Bytes_Valid (Data, authority_arena_Archive)
        or else not Tuple_Is (Data, resource_rosters_Archive)
        or else Sequence_Count (Data, resource_rosters_Archive) /= 17
        or else not Roster_Valid (Data, resource_rosters_Archive, 0, "history", N.Raw_Scope_Frame'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 1, "proposed_history", N.Raw_Scope_Frame'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 2, "rows", W.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 3, "proposed_rows", W.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 4, "projection", N.Raw_Projection'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 5, "proposed_projection", N.Raw_Projection'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 6, "buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 7, "proposed_buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 8, "actual_buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 9, "observed", W.Raw_Native'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 10, "facts", O.Raw_Facts'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 11, "capabilities", D.Raw_Capability'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 12, "groups", W.Raw_Quantity'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 13, "proc_groups", W.Raw_Quantity'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 14, "tasks", Y.Raw_Task'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 15, "processes", Y.Raw_Process'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, resource_rosters_Archive, 16, "namespaces", Y.Raw_Namespace'Size / System.Storage_Unit)
        or else not Tuple_Is (Data, authority_rosters_Archive)
        or else Sequence_Count (Data, authority_rosters_Archive) /= 4
        or else not Roster_Valid (Data, authority_rosters_Archive, 0, "grants", T.Raw_Grant'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, authority_rosters_Archive, 1, "uses", T.Raw_Use'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, authority_rosters_Archive, 2, "receipts", T.C.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, authority_rosters_Archive, 3, "events", T.C.Raw_Row'Size / System.Storage_Unit)
      then return False; end if;
      declare
         Actor_Source : constant Q.Byte_Array := Archive_Bytes (Data, actor_input_Archive);
         Authority_Source : constant Q.Byte_Array := Archive_Bytes (Data, authority_input_Archive);
         Crosswalk_Source : constant Q.Byte_Array := Archive_Bytes (Data, crosswalk_Archive);
         Child_Source : constant Q.Byte_Array := Archive_Bytes (Data, child_input_Archive);
         Raw : constant D.Raw_Packet := RD.Load (Actor_Source);
         Authority : constant T.Raw_Input := RD.Load (Authority_Source);
         Crosswalk : constant X.Raw_Crosswalk := RD.Load (Crosswalk_Source);
         Child : constant Y.Raw_Input := RD.Load (Child_Source);
         Arena : constant Q.Byte_Array := Archive_Bytes (Data, resource_arena_Archive);
         Authority_Arena : constant Q.Byte_Array := Archive_Bytes (Data, authority_arena_Archive);
         Source_history : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 0));
         Copy_history : constant N.Raw_History_Array := Load_Array (Source_history);
         Source_proposed_history : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 1));
         Copy_proposed_history : constant N.Raw_History_Array := Load_Array (Source_proposed_history);
         Source_rows : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 2));
         Copy_rows : constant W.Raw_Row_Array := Load_Array (Source_rows);
         Source_proposed_rows : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 3));
         Copy_proposed_rows : constant W.Raw_Row_Array := Load_Array (Source_proposed_rows);
         Source_projection : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 4));
         Copy_projection : constant N.Raw_Projection_Array := Load_Array (Source_projection);
         Source_proposed_projection : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 5));
         Copy_proposed_projection : constant N.Raw_Projection_Array := Load_Array (Source_proposed_projection);
         Source_buckets : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 6));
         Copy_buckets : constant N.Raw_Bucket_Array := Load_Array (Source_buckets);
         Source_proposed_buckets : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 7));
         Copy_proposed_buckets : constant N.Raw_Bucket_Array := Load_Array (Source_proposed_buckets);
         Source_actual_buckets : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 8));
         Copy_actual_buckets : constant N.Raw_Bucket_Array := Load_Array (Source_actual_buckets);
         Source_observed : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 9));
         Copy_observed : constant W.Raw_Native_Array := Load_Array (Source_observed);
         Source_facts : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 10));
         Copy_facts : constant N.Raw_Facts_Array := Load_Array (Source_facts);
         Source_capabilities : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 11));
         Copy_capabilities : constant D.Raw_Capability_Array := Load_Array (Source_capabilities);
         Source_groups : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 12));
         Copy_groups : constant D.Raw_Group_Array := Load_Array (Source_groups);
         Source_proc_groups : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 13));
         Copy_proc_groups : constant D.Raw_Group_Array := Load_Array (Source_proc_groups);
         Source_tasks : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 14));
         Copy_tasks : constant Y.Raw_Task_Array := Load_Array (Source_tasks);
         Source_processes : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 15));
         Copy_processes : constant Y.Raw_Process_Array := Load_Array (Source_processes);
         Source_namespaces : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, resource_rosters_Archive, 16));
         Copy_namespaces : constant Y.Raw_Namespace_Array := Load_Array (Source_namespaces);
         Source_grants : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, authority_rosters_Archive, 0));
         Copy_grants : constant V.Raw_Grant_Array := Load_Array (Source_grants);
         Source_uses : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, authority_rosters_Archive, 1));
         Copy_uses : constant V.Raw_Use_Array := Load_Array (Source_uses);
         Source_receipts : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, authority_rosters_Archive, 2));
         Copy_receipts : constant V.Raw_Chain_Array := Load_Array (Source_receipts);
         Source_events : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, authority_rosters_Archive, 3));
         Copy_events : constant V.Raw_Chain_Array := Load_Array (Source_events);
         Resource_Position : Lyt.Cursor := Lyt.Start (Arena'Length);
         Authority_Position : Lyt.Cursor := Lyt.Start (Authority_Arena'Length);
      begin
         if not RD.Source_Padding_Valid (Actor_Source, Raw)
           or else not RD.Source_Padding_Valid (Authority_Source, Authority)
           or else not RD.Source_Padding_Valid (Crosswalk_Source, Crosswalk)
           or else not RD.Source_Padding_Valid (Child_Source, Child)
           or else not Padding_Valid (Source_history, Copy_history)
           or else not Padding_Valid (Source_proposed_history, Copy_proposed_history)
           or else not Padding_Valid (Source_rows, Copy_rows)
           or else not Padding_Valid (Source_proposed_rows, Copy_proposed_rows)
           or else not Padding_Valid (Source_projection, Copy_projection)
           or else not Padding_Valid (Source_proposed_projection, Copy_proposed_projection)
           or else not Padding_Valid (Source_buckets, Copy_buckets)
           or else not Padding_Valid (Source_proposed_buckets, Copy_proposed_buckets)
           or else not Padding_Valid (Source_actual_buckets, Copy_actual_buckets)
           or else not Padding_Valid (Source_observed, Copy_observed)
           or else not Padding_Valid (Source_facts, Copy_facts)
           or else not Padding_Valid (Source_capabilities, Copy_capabilities)
           or else not Padding_Valid (Source_groups, Copy_groups)
           or else not Padding_Valid (Source_proc_groups, Copy_proc_groups)
           or else not Padding_Valid (Source_tasks, Copy_tasks)
           or else not Padding_Valid (Source_processes, Copy_processes)
           or else not Padding_Valid (Source_namespaces, Copy_namespaces)
           or else not Padding_Valid (Source_grants, Copy_grants)
           or else not Padding_Valid (Source_uses, Copy_uses)
           or else not Padding_Valid (Source_receipts, Copy_receipts)
           or else not Padding_Valid (Source_events, Copy_events) then return False; end if;
         Lyt.Append (Raw.Ledger, Resource_Position);
         for I in Copy_history'Range loop Lyt.Append (Copy_history (I), Resource_Position); end loop;
         for I in Copy_proposed_history'Range loop Lyt.Append (Copy_proposed_history (I), Resource_Position); end loop;
         for I in Copy_rows'Range loop Lyt.Append (Copy_rows (I), Resource_Position); end loop;
         for I in Copy_proposed_rows'Range loop Lyt.Append (Copy_proposed_rows (I), Resource_Position); end loop;
         for I in Copy_projection'Range loop Lyt.Append (Copy_projection (I), Resource_Position); end loop;
         for I in Copy_proposed_projection'Range loop Lyt.Append (Copy_proposed_projection (I), Resource_Position); end loop;
         for I in Copy_buckets'Range loop Lyt.Append (Copy_buckets (I), Resource_Position); end loop;
         for I in Copy_proposed_buckets'Range loop Lyt.Append (Copy_proposed_buckets (I), Resource_Position); end loop;
         for I in Copy_actual_buckets'Range loop Lyt.Append (Copy_actual_buckets (I), Resource_Position); end loop;
         for I in Copy_observed'Range loop Lyt.Append (Copy_observed (I), Resource_Position); end loop;
         for I in Copy_facts'Range loop Lyt.Append (Copy_facts (I), Resource_Position); end loop;
         if Child.Mode = J.Admission_Mode'Pos (J.Child_Admission) then
            Lyt.Append (Raw.Captured, Resource_Position);
         elsif not Zero_Bytes (Actor_Source (Actor_Source'First + Raw.Captured'Position .. Actor_Source'First + Raw.Captured'Position + Raw.Captured'Size / System.Storage_Unit - 1)) then return False; end if;
         for I in Copy_capabilities'Range loop Lyt.Append (Copy_capabilities (I), Resource_Position); end loop;
         for I in Copy_groups'Range loop Lyt.Append (Copy_groups (I), Resource_Position); end loop;
         for I in Copy_proc_groups'Range loop Lyt.Append (Copy_proc_groups (I), Resource_Position); end loop;
         Lyt.Append (Crosswalk, Resource_Position);
         Lyt.Append (Child.Controller, Resource_Position);
         if Child.Mode /= J.Admission_Mode'Pos (J.Root_Controller_Admission) then
            Lyt.Append (Child.Child_Task, Resource_Position);
         elsif not Zero_Bytes (Child_Source (Child_Source'First + Child.Child_Task'Position .. Child_Source'First + Child.Child_Task'Position + Child.Child_Task'Size / System.Storage_Unit - 1)) then return False; end if;
         for I in Copy_tasks'Range loop Lyt.Append (Copy_tasks (I), Resource_Position); end loop;
         for I in Copy_processes'Range loop Lyt.Append (Copy_processes (I), Resource_Position); end loop;
         for I in Copy_namespaces'Range loop Lyt.Append (Copy_namespaces (I), Resource_Position); end loop;
         Lyt.Append (Authority, Authority_Position);
         for I in Copy_grants'Range loop Lyt.Append (Copy_grants (I), Authority_Position); end loop;
         for I in Copy_uses'Range loop Lyt.Append (Copy_uses (I), Authority_Position); end loop;
         if not Lyt.Complete (Resource_Position) or else not Lyt.Complete (Authority_Position) then return False; end if;
         if Child.Mode > J.Admission_Mode'Pos (J.Admission_Mode'Last)
           or else Authority.Mode /= A.Command'Pos (A.Authorize_Execution)
           or else not Matches (Arena, Data, Field (Data, Material_Archive, "controller"), Child.Controller)
           or else not Matches (Arena, Data, Field (Data, Material_Archive, "crosswalk"), Crosswalk)
           or else not Packet_Matches (Arena, Data, Field (Data, Material_Archive, "packet"), Raw.Ledger, Copy_history, Copy_proposed_history, Copy_rows, Copy_proposed_rows, Copy_projection, Copy_proposed_projection, Copy_buckets, Copy_proposed_buckets, Copy_actual_buckets, Copy_observed, Copy_facts)
           or else not Authority_Matches (Authority_Arena, Data, Field (Data, Material_Archive, "authority_snapshot"), Authority, Copy_grants, Copy_uses, Copy_receipts, Copy_events)
         then return False; end if;
         if Child.Mode = J.Admission_Mode'Pos (J.Root_Controller_Admission) then
            return Dictionary_Count (Data, Material_Archive) = 4 and then
              Copy_capabilities'Length = 0 and then Copy_groups'Length = 0 and then Copy_proc_groups'Length = 0 and then
              Copy_tasks'Length = 0 and then Copy_processes'Length = 0 and then Copy_namespaces'Length = 0;
         elsif Child.Mode = J.Admission_Mode'Pos (J.Task_Reservation_Admission) then
            return Dictionary_Count (Data, Material_Archive) = 6 and then
              Matches (Arena, Data, Field (Data, Material_Archive, "task"), Child.Child_Task) and then
              Matches (Arena, Data, Field (Data, Material_Archive, "tasks"), Copy_tasks) and then
              Copy_capabilities'Length = 0 and then Copy_groups'Length = 0 and then Copy_proc_groups'Length = 0 and then
              Copy_processes'Length = 0 and then Copy_namespaces'Length = 0;
         else
            return Dictionary_Count (Data, Material_Archive) = 12 and then
              Matches (Arena, Data, Field (Data, Material_Archive, "actor"), Raw.Captured) and then
              Matches (Arena, Data, Field (Data, Material_Archive, "task"), Child.Child_Task) and then
              Matches (Arena, Data, Field (Data, Material_Archive, "capabilities"), Copy_capabilities) and then
              Matches (Arena, Data, Field (Data, Material_Archive, "groups"), Copy_groups) and then
              Matches (Arena, Data, Field (Data, Material_Archive, "proc_groups"), Copy_proc_groups) and then
              Matches (Arena, Data, Field (Data, Material_Archive, "tasks"), Copy_tasks) and then
              Matches (Arena, Data, Field (Data, Material_Archive, "processes"), Copy_processes) and then
              Matches (Arena, Data, Field (Data, Material_Archive, "namespaces"), Copy_namespaces);
         end if;
      end;
   end Root_Material_Matches;
   function Scoped_Material_Matches
     (Data : E.Bytes; Observation_Archive, Material_Archive : E.Span) return Boolean
   is
      raw_input_Archive : constant E.Span := Field (Data, Observation_Archive, "raw_input");
      raw_arena_Archive : constant E.Span := Field (Data, Observation_Archive, "raw_arena");
      raw_rosters_Archive : constant E.Span := Field (Data, Observation_Archive, "raw_rosters");
   begin
      if not Archive_Record_Is (Data, Observation_Archive, "ScopedNativeDecision")
        or else not Bytes_Shape (Data, raw_input_Archive, N.Raw_Packet'Size / System.Storage_Unit)
        or else not Archive_Bytes_Valid (Data, raw_arena_Archive)
        or else not Tuple_Is (Data, raw_rosters_Archive)
        or else Sequence_Count (Data, raw_rosters_Archive) /= 11
        or else not Roster_Valid (Data, raw_rosters_Archive, 0, "history", N.Raw_Scope_Frame'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 1, "proposed_history", N.Raw_Scope_Frame'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 2, "rows", W.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 3, "proposed_rows", W.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 4, "projection", N.Raw_Projection'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 5, "proposed_projection", N.Raw_Projection'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 6, "buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 7, "proposed_buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 8, "actual_buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 9, "observed", W.Raw_Native'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, raw_rosters_Archive, 10, "facts", O.Raw_Facts'Size / System.Storage_Unit)
      then return False; end if;
      declare
         Input_Source : constant Q.Byte_Array := Archive_Bytes (Data, raw_input_Archive);
         Raw : constant N.Raw_Packet := RD.Load (Input_Source);
         Arena : constant Q.Byte_Array := Archive_Bytes (Data, raw_arena_Archive);
         Source_history : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 0));
         Copy_history : constant N.Raw_History_Array := Load_Array (Source_history);
         Source_proposed_history : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 1));
         Copy_proposed_history : constant N.Raw_History_Array := Load_Array (Source_proposed_history);
         Source_rows : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 2));
         Copy_rows : constant W.Raw_Row_Array := Load_Array (Source_rows);
         Source_proposed_rows : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 3));
         Copy_proposed_rows : constant W.Raw_Row_Array := Load_Array (Source_proposed_rows);
         Source_projection : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 4));
         Copy_projection : constant N.Raw_Projection_Array := Load_Array (Source_projection);
         Source_proposed_projection : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 5));
         Copy_proposed_projection : constant N.Raw_Projection_Array := Load_Array (Source_proposed_projection);
         Source_buckets : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 6));
         Copy_buckets : constant N.Raw_Bucket_Array := Load_Array (Source_buckets);
         Source_proposed_buckets : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 7));
         Copy_proposed_buckets : constant N.Raw_Bucket_Array := Load_Array (Source_proposed_buckets);
         Source_actual_buckets : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 8));
         Copy_actual_buckets : constant N.Raw_Bucket_Array := Load_Array (Source_actual_buckets);
         Source_observed : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 9));
         Copy_observed : constant W.Raw_Native_Array := Load_Array (Source_observed);
         Source_facts : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, raw_rosters_Archive, 10));
         Copy_facts : constant N.Raw_Facts_Array := Load_Array (Source_facts);
         Position : Lyt.Cursor := Lyt.Start (Arena'Length);
      begin
         if not RD.Source_Padding_Valid (Input_Source, Raw)
           or else not Padding_Valid (Source_history, Copy_history)
           or else not Padding_Valid (Source_proposed_history, Copy_proposed_history)
           or else not Padding_Valid (Source_rows, Copy_rows)
           or else not Padding_Valid (Source_proposed_rows, Copy_proposed_rows)
           or else not Padding_Valid (Source_projection, Copy_projection)
           or else not Padding_Valid (Source_proposed_projection, Copy_proposed_projection)
           or else not Padding_Valid (Source_buckets, Copy_buckets)
           or else not Padding_Valid (Source_proposed_buckets, Copy_proposed_buckets)
           or else not Padding_Valid (Source_actual_buckets, Copy_actual_buckets)
           or else not Padding_Valid (Source_observed, Copy_observed)
           or else not Padding_Valid (Source_facts, Copy_facts) then return False; end if;
         Lyt.Append (Raw, Position);
         for I in Copy_history'Range loop Lyt.Append (Copy_history (I), Position); end loop;
         for I in Copy_proposed_history'Range loop Lyt.Append (Copy_proposed_history (I), Position); end loop;
         for I in Copy_rows'Range loop Lyt.Append (Copy_rows (I), Position); end loop;
         for I in Copy_proposed_rows'Range loop Lyt.Append (Copy_proposed_rows (I), Position); end loop;
         for I in Copy_projection'Range loop Lyt.Append (Copy_projection (I), Position); end loop;
         for I in Copy_proposed_projection'Range loop Lyt.Append (Copy_proposed_projection (I), Position); end loop;
         for I in Copy_buckets'Range loop Lyt.Append (Copy_buckets (I), Position); end loop;
         for I in Copy_proposed_buckets'Range loop Lyt.Append (Copy_proposed_buckets (I), Position); end loop;
         for I in Copy_actual_buckets'Range loop Lyt.Append (Copy_actual_buckets (I), Position); end loop;
         for I in Copy_observed'Range loop Lyt.Append (Copy_observed (I), Position); end loop;
         for I in Copy_facts'Range loop Lyt.Append (Copy_facts (I), Position); end loop;
         if not Lyt.Complete (Position) then return False; end if;
         return Packet_Matches (Arena, Data, Material_Archive, Raw, Copy_history, Copy_proposed_history, Copy_rows, Copy_proposed_rows, Copy_projection, Copy_proposed_projection, Copy_buckets, Copy_proposed_buckets, Copy_actual_buckets, Copy_observed, Copy_facts);
      end;
   end Scoped_Material_Matches;
   function Basic_Authority_Material_Matches
     (Data, Material_Data : E.Bytes; Observation_Archive, Material_Archive : E.Span; Reserve_Only : Boolean := False) return Boolean
   is
      input_Archive : constant E.Span := Field (Data, Observation_Archive, "input");
      arena_Archive : constant E.Span := Field (Data, Observation_Archive, "arena");
      rosters_Archive : constant E.Span := Field (Data, Observation_Archive, "rosters");
   begin
      if not Original_Valid (Data, Observation_Archive)
        or else not Hex_Valid (Data, input_Archive)
        or else not Hex_Valid (Data, arena_Archive)
        or else Hex_Bytes (Data, input_Archive)'Length /= T.Raw_Input'Size / System.Storage_Unit
        or else Sequence_Count (Data, rosters_Archive) /= 4
        or else not Hex_Valid (Data, Element (Data, rosters_Archive, 0))
        or else Hex_Bytes (Data, Element (Data, rosters_Archive, 0))'Length mod (T.Raw_Grant'Size / System.Storage_Unit) /= 0
        or else not Hex_Valid (Data, Element (Data, rosters_Archive, 1))
        or else Hex_Bytes (Data, Element (Data, rosters_Archive, 1))'Length mod (T.Raw_Use'Size / System.Storage_Unit) /= 0
        or else not Hex_Valid (Data, Element (Data, rosters_Archive, 2))
        or else Hex_Bytes (Data, Element (Data, rosters_Archive, 2))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) /= 0
        or else not Hex_Valid (Data, Element (Data, rosters_Archive, 3))
        or else Hex_Bytes (Data, Element (Data, rosters_Archive, 3))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) /= 0
      then return False; end if;
      declare
         Input_Source : constant Q.Byte_Array := Hex_Bytes (Data, input_Archive);
         Authority : constant T.Raw_Input := RD.Load (Input_Source);
         Arena : constant Q.Byte_Array := Hex_Bytes (Data, arena_Archive);
         Source_grants : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, rosters_Archive, 0));
         Copy_grants : constant V.Raw_Grant_Array := Load_Array (Source_grants);
         Source_uses : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, rosters_Archive, 1));
         Copy_uses : constant V.Raw_Use_Array := Load_Array (Source_uses);
         Source_receipts : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, rosters_Archive, 2));
         Copy_receipts : constant V.Raw_Chain_Array := Load_Array (Source_receipts);
         Source_events : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, rosters_Archive, 3));
         Copy_events : constant V.Raw_Chain_Array := Load_Array (Source_events);
         Position : Lyt.Cursor := Lyt.Start (Arena'Length);
      begin
         if Reserve_Only and then Authority.Mode /= A.Command'Pos (A.Reserve_Use) then return False; end if;
         if not RD.Source_Padding_Valid (Input_Source, Authority)
           or else not Padding_Valid (Source_grants, Copy_grants)
           or else not Padding_Valid (Source_uses, Copy_uses)
           or else not Padding_Valid (Source_receipts, Copy_receipts)
           or else not Padding_Valid (Source_events, Copy_events) then return False; end if;
         Lyt.Append (Authority, Position);
         for I in Copy_grants'Range loop Lyt.Append (Copy_grants (I), Position); end loop;
         for I in Copy_uses'Range loop Lyt.Append (Copy_uses (I), Position); end loop;
         if not Lyt.Complete (Position) then return False; end if;
         return Authority_Matches (Arena, Material_Data, Material_Archive, Authority, Copy_grants, Copy_uses, Copy_receipts, Copy_events);
      end;
   end Basic_Authority_Material_Matches;

   function Operation_Material_Matches
     (Data : E.Bytes; Observation_Archive, Material_Archive : E.Span) return Boolean is
      function Compare (Source : E.Bytes; Material : E.Span) return Boolean is
      begin
         if Sequence_Count (Data, Field (Data, Observation_Archive, "rosters")) = 12 then return Historical_Material_Matches (Data, Source, Observation_Archive, Material); end if;
         return Basic_Authority_Material_Matches (Data, Source, Observation_Archive, Material);
      end Compare;
   begin
      if Stored_Bytes_Valid (Data, Material_Archive) then
         declare
            Source : constant E.Bytes := Stored_Bytes (Data, Material_Archive);
            Material : constant E.Span := (Source'First, Source'Length);
         begin
            return Original_Valid (Source, Material) and then Compare (Source, Material);
         end;
      else return Compare (Data, Material_Archive); end if;
   end Operation_Material_Matches;
   function Reservation_Material_Matches
     (Data : E.Bytes; Observation_Archive, Material_Archive : E.Span) return Boolean is
      function Compare (Source : E.Bytes; Material : E.Span) return Boolean is
      begin
         return Basic_Authority_Material_Matches (Data, Source, Observation_Archive, Material, True);
      end Compare;
   begin
      if Stored_Bytes_Valid (Data, Material_Archive) then
         declare
            Source : constant E.Bytes := Stored_Bytes (Data, Material_Archive);
            Material : constant E.Span := (Source'First, Source'Length);
         begin
            return Original_Valid (Source, Material) and then Compare (Source, Material);
         end;
      else return Compare (Data, Material_Archive); end if;
   end Reservation_Material_Matches;
   function Projection_Matches (Arena, Data : E.Bytes; Raw : W.Raw_Id; Item : E.Span) return Boolean is
   begin
      if not W.Well_Formed (Arena, Raw) or else Raw.Present /= 1 then return False; end if;
      return E.C.Operation_Archive_JSON_Matches (Arena, Data,
        (First => Q.Byte_Index (Raw.First), Length => Q.Byte_Count (Raw.Length)), Item);
   end Projection_Matches;
   --  Keep the raw-record projection separate from the recursive archive walk.
   --  Every original projection conjunct below is preserved in its original order.
   function Root_Native_Capture_Matches
     (Data : E.Bytes; Input, Arena_Item, Source, Before, After,
      Physical_Raw, Native_Fields, Provenance_Archive : E.Span) return Boolean
     with Global => null,
       Pre => Bytes_Shape (Data, Input, Y.Raw_Input'Size / System.Storage_Unit)
         and then Archive_Bytes_Valid (Data, Arena_Item)
   is
      Raw : constant Y.Raw_Input := RD.Load (Archive_Bytes (Data, Input));
      Arena : constant E.Bytes := Archive_Bytes (Data, Arena_Item);
   begin
      if Raw.Mode /= J.Admission_Mode'Pos (J.Root_Controller_Admission)
        or else not Y.Well_Formed (Arena, Raw.Controller)
      then return False; end if;
      return Projection_Matches (Arena, Data, Raw.Controller.current_source, Source)
        and then Projection_Matches (Arena, Data, Raw.Controller.raw_request, Field (Data, Provenance_Archive, "original_request"))
        and then Projection_Matches (Arena, Data, Raw.Controller.raw_manager, Field (Data, Physical_Raw, "manager"))
        and then Matches (Arena, Data, Field (Data, Before, "status"), Raw.Controller.Process.raw_status)
        and then Matches (Arena, Data, Field (Data, Before, "stat"), Raw.Controller.Process.raw_stat)
        and then Matches (Arena, Data, Field (Data, Before, "cgroup"), Raw.Controller.Process.raw_cgroup)
        and then Matches (Arena, Data, Field (Data, Before, "maps"), Raw.Controller.Process.raw_maps)
        and then Matches (Arena, Data, Field (Data, Before, "cmdline"), Raw.Controller.Process.raw_cmdline)
        -- Original before/after observation permits CPU counters/stat and
        -- status counters to change, but cgroup/maps/cmdline are immutable.
        and then OA.Same_Encoding (Data, Field (Data, Before, "cgroup"), Field (Data, After, "cgroup"))
        and then OA.Same_Encoding (Data, Field (Data, Before, "maps"), Field (Data, After, "maps"))
        and then OA.Same_Encoding (Data, Field (Data, Before, "cmdline"), Field (Data, After, "cmdline"))
        and then Matches (Arena, Data, Field (Data, Native_Fields, "helper_image"), Raw.Controller.worker_image)
        and then Matches (Arena, Data, Field (Data, Native_Fields, "dispatch"), Raw.Controller.dispatch)
        and then Matches (Arena, Data, Field (Data, Native_Fields, "actual_unit"), Raw.Controller.Process.actual_unit)
        and then Matches (Arena, Data, Field (Data, Native_Fields, "cgroup"), Raw.Controller.Process.cgroup)
        and then Matches (Arena, Data, Field (Data, Native_Fields, "invocation"), Raw.Controller.Process.invocation)
        and then Matches (Arena, Data, Field (Data, Native_Fields, "namespace"), Raw.Controller.Process.namespace);
   end Root_Native_Capture_Matches;
   function Root_Capture_Matches
     (Data : E.Bytes; Observation_Archive, Provenance_Archive : E.Span) return Boolean
   is
      Input : constant E.Span := Field (Data, Observation_Archive, "child_input");
      Arena_Item : constant E.Span := Field (Data, Observation_Archive, "resource_arena");
      Source : E.Span := Field (Data, Provenance_Archive, "current_source");
      Process : constant E.Span := Field (Data, Provenance_Archive, "process");
      Before : constant E.Span := Field (Data, Process, "raw");
      After : constant E.Span := Field (Data, Process, "after");
      Physical : constant E.Span := Field (Data, Provenance_Archive, "physical");
      Physical_Raw : constant E.Span := Field (Data, Physical, "raw");
      Native_Fields : constant E.Span := Field (Data, Physical, "native_fields");
      Subject : constant E.Span := Field (Data, Provenance_Archive, "subject_capture");
      Capture : constant E.Span := Field (Data, Provenance_Archive, "owned_descriptor_roster");
      Has_Subject : constant Boolean := Subject.Length > 0;
      Extra_Members : constant E.Count := (if Has_Subject then 1 else 0);
   begin
      if not Archive_Record_Is (Data, Observation_Archive, "ResourceChildNativeObservation")
        or else not Bytes_Shape (Data, Input, Y.Raw_Input'Size / System.Storage_Unit)
        or else not Archive_Bytes_Valid (Data, Arena_Item)
        or else Field (Data, Provenance_Archive, "owner_state").Length = 0
      then return False; end if;
      if Source.Length > 0 then
         if Dictionary_Count (Data, Provenance_Archive) /= 10 + Extra_Members
           or else Field (Data, Provenance_Archive, "owned_descriptor_roster").Length = 0
           or else Field (Data, Provenance_Archive, "authority").Length = 0
           or else Field (Data, Provenance_Archive, "running_event").Length = 0
           or else Field (Data, Provenance_Archive, "resource_capture").Length = 0
           or else Field (Data, Provenance_Archive, "resource_classifications").Length = 0
         then return False; end if;
      else
         if Dictionary_Count (Data, Provenance_Archive) /= 8 + Extra_Members
           or else Field (Data, Provenance_Archive, "owned_descriptor_roster").Length = 0
           or else Field (Data, Provenance_Archive, "state_correspondence").Length = 0
           or else Field (Data, Provenance_Archive, "native_classification").Length = 0
         then return False; end if;
         Source := Field (Data, Field (Data, Field (Data, Provenance_Archive, "seed_record"), "provenance"), "current_source");
      end if;
      if Has_Subject and then not Worldline.Scoped_Capture_Projection.Subject_Capture_Matches
        (Data, Subject, Field (Data, Capture, "inventory"), Field (Data, Capture, "packet"))
      then return False; end if;
      return Root_Native_Capture_Matches
        (Data, Input, Arena_Item, Source, Before, After,
         Physical_Raw, Native_Fields, Provenance_Archive);
   end Root_Capture_Matches;
   function Archive_Field
     (Data : E.Bytes; Item : E.Span; Name : String) return E.Span is
     (Field (Data, Item, Name));
   function Owned (Raw : V.Raw_Grant_Array) return A.Grants
     with Global => null, Pre => (for all I in Raw'Range => T.Well_Formed (Raw (I)))
   is
      Result : A.Grants (Raw'Range);
   begin
      for I in Raw'Range loop
         Result (I) := T.Decode (Raw (I));
         pragma Loop_Invariant (for all K in Raw'First .. I => Result (K) = T.Decode (Raw (K)));
      end loop;
      return Result;
   end Owned;
   function Owned (Raw : V.Raw_Use_Array) return A.Uses
     with Global => null, Pre => (for all I in Raw'Range => T.Well_Formed (Raw (I)))
   is
      Result : A.Uses (Raw'Range);
   begin
      for I in Raw'Range loop
         Result (I) := T.Decode (Raw (I));
         pragma Loop_Invariant (for all K in Raw'First .. I => Result (K) = T.Decode (Raw (K)));
      end loop;
      return Result;
   end Owned;
   function Owned (Raw : V.Raw_Chain_Array) return A.C.Retained_Rows
     with Global => null, Pre => (for all I in Raw'Range => T.C.Well_Formed (Raw (I)))
   is
      Result : A.C.Retained_Rows (Raw'Range);
   begin
      for I in Raw'Range loop
         Result (I) := T.C.Decode (Raw (I));
         pragma Loop_Invariant (for all K in Raw'First .. I => Result (K) = T.C.Decode (Raw (K)));
      end loop;
      return Result;
   end Owned;
   function Exchange_Native
     (Raw : CX.Raw_Input; Arena : E.Bytes;
      Copy_grants : V.Raw_Grant_Array;
      Copy_uses : V.Raw_Use_Array;
      Copy_rows : W.Raw_Row_Array;
      Copy_observed : W.Raw_Native_Array;
      Copy_worker_receipts : V.Raw_Chain_Array;
      Copy_worker_events : V.Raw_Chain_Array;
      Copy_effect_receipts : V.Raw_Chain_Array;
      Copy_effect_events : V.Raw_Chain_Array) return V.Result is
      P : constant CO.Raw_Input := Raw.Operation_Input;
   begin
      if not CX.Well_Formed (Arena, Raw)
        or else not (for all I in Copy_grants'Range => T.Well_Formed (Copy_grants (I)))
        or else not (for all I in Copy_uses'Range => T.Well_Formed (Copy_uses (I)))
        or else not (for all I in Copy_rows'Range => W.Well_Formed (Arena, Copy_rows (I)))
        or else not (for all I in Copy_observed'Range => W.Well_Formed (Arena, Copy_observed (I)))
        or else not (for all I in Copy_worker_receipts'Range => T.C.Well_Formed (Copy_worker_receipts (I)))
        or else not (for all I in Copy_worker_events'Range => T.C.Well_Formed (Copy_worker_events (I)))
        or else not (for all I in Copy_effect_receipts'Range => T.C.Well_Formed (Copy_effect_receipts (I)))
        or else not (for all I in Copy_effect_events'Range => T.C.Well_Formed (Copy_effect_events (I)))
      then return V.Rejected; end if;
      return (True, CEX.Decision'Pos (CEX.Decide (Arena, Owned (Copy_grants), Owned (Copy_uses),
         T.Decode (P.Authority.Bound), T.Decode (P.Authority.Now).Value, T.Decode (Arena, P.Authority.Facts),
         W.Decode (Arena, P.State), W.Decode_Rows (Arena, Copy_rows), W.Decode_Native (Arena, Copy_observed),
         W.Decode (Arena, P.Bound), W.Decode (Arena, P.Requester), T.Decode (P.Peer),
         P.Collapse, CX.Decode (Arena, Raw.Material),
         CEX.Phase'Val (Raw.Before), CEX.Command'Val (Raw.Mode), Owned (Copy_worker_receipts), Owned (Copy_worker_events),
         Owned (Copy_effect_receipts), Owned (Copy_effect_events))));
   end Exchange_Native;
   function Completion_Native
     (Raw : HC.Raw_Input; Arena : E.Bytes;
      Copy_grants : V.Raw_Grant_Array;
      Copy_uses : V.Raw_Use_Array;
      Copy_rows : W.Raw_Row_Array;
      Copy_observed : W.Raw_Native_Array;
      Copy_worker_receipts : V.Raw_Chain_Array;
      Copy_worker_events : V.Raw_Chain_Array;
      Copy_effect_receipts : V.Raw_Chain_Array;
      Copy_effect_events : V.Raw_Chain_Array;
      Copy_current_grants : V.Raw_Grant_Array;
      Copy_current_uses : V.Raw_Use_Array;
      Copy_current_receipts : V.Raw_Chain_Array;
      Copy_current_events : V.Raw_Chain_Array) return V.Result is
      P : constant CO.Raw_Input := Raw.Historical.Operation_Input;
   begin
      if not HC.Well_Formed (Arena, Raw)
        or else not (for all I in Copy_grants'Range => T.Well_Formed (Copy_grants (I)))
        or else not (for all I in Copy_uses'Range => T.Well_Formed (Copy_uses (I)))
        or else not (for all I in Copy_rows'Range => W.Well_Formed (Arena, Copy_rows (I)))
        or else not (for all I in Copy_observed'Range => W.Well_Formed (Arena, Copy_observed (I)))
        or else not (for all I in Copy_worker_receipts'Range => T.C.Well_Formed (Copy_worker_receipts (I)))
        or else not (for all I in Copy_worker_events'Range => T.C.Well_Formed (Copy_worker_events (I)))
        or else not (for all I in Copy_effect_receipts'Range => T.C.Well_Formed (Copy_effect_receipts (I)))
        or else not (for all I in Copy_effect_events'Range => T.C.Well_Formed (Copy_effect_events (I)))
        or else not (for all I in Copy_current_grants'Range => T.Well_Formed (Copy_current_grants (I)))
        or else not (for all I in Copy_current_uses'Range => T.Well_Formed (Copy_current_uses (I)))
        or else not (for all I in Copy_current_receipts'Range => T.C.Well_Formed (Copy_current_receipts (I)))
        or else not (for all I in Copy_current_events'Range => T.C.Well_Formed (Copy_current_events (I)))
      then return V.Rejected; end if;
      return (True, H.Decision'Pos (H.Decide (Arena, Owned (Copy_grants), Owned (Copy_uses),
         T.Decode (P.Authority.Bound), T.Decode (P.Authority.Now).Value, T.Decode (Arena, P.Authority.Facts),
         W.Decode (Arena, P.State), W.Decode_Rows (Arena, Copy_rows), W.Decode_Native (Arena, Copy_observed),
         W.Decode (Arena, P.Bound), W.Decode (Arena, P.Requester), T.Decode (P.Peer),
         P.Collapse, CX.Decode (Arena, Raw.Historical.Material),
         Owned (Copy_worker_receipts), Owned (Copy_worker_events), Owned (Copy_effect_receipts), Owned (Copy_effect_events),
         Owned (Copy_current_grants), Owned (Copy_current_uses), T.Decode (Raw.Current.Bound), T.Decode (Arena, Raw.Current.Facts),
         Owned (Copy_current_receipts), Owned (Copy_current_events))));
   end Completion_Native;
   function Exchange_Shape (Data : E.Bytes; Observation_Archive : E.Span) return Boolean is
      View : constant E.View := E.Decode (Data, Observation_Archive, E.Operation);
      Input : constant E.Span := Field (Data, Observation_Archive, "input");
      Arena : constant E.Span := Field (Data, Observation_Archive, "arena");
      Rosters : constant E.Span := Field (Data, Observation_Archive, "rosters");
      Output : constant E.Span := Field (Data, Observation_Archive, "output");
   begin
      return Original_Valid (Data, Observation_Archive) and then View.Form = E.Object_Value
        and then Dictionary_Count (Data, Observation_Archive) = 5
        and then Hex_Valid (Data, Input) and then Hex_Bytes (Data, Input)'Length = CX.Raw_Input'Size / System.Storage_Unit
        and then Hex_Valid (Data, Arena)
        and then Hex_Valid (Data, Output) and then Hex_Bytes (Data, Output)'Length = T.Raw_Result'Size / System.Storage_Unit
        and then Sequence_Count (Data, Rosters) = 8
        and then Hex_Valid (Data, Element (Data, Rosters, 0))
        and then Hex_Bytes (Data, Element (Data, Rosters, 0))'Length mod (T.Raw_Grant'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 1))
        and then Hex_Bytes (Data, Element (Data, Rosters, 1))'Length mod (T.Raw_Use'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 2))
        and then Hex_Bytes (Data, Element (Data, Rosters, 2))'Length mod (W.Raw_Row'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 3))
        and then Hex_Bytes (Data, Element (Data, Rosters, 3))'Length mod (W.Raw_Native'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 4))
        and then Hex_Bytes (Data, Element (Data, Rosters, 4))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 5))
        and then Hex_Bytes (Data, Element (Data, Rosters, 5))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 6))
        and then Hex_Bytes (Data, Element (Data, Rosters, 6))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 7))
        and then Hex_Bytes (Data, Element (Data, Rosters, 7))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) = 0;
   end Exchange_Shape;
   function Completion_Shape (Data : E.Bytes; Observation_Archive : E.Span) return Boolean is
      View : constant E.View := E.Decode (Data, Observation_Archive, E.Operation);
      Input : constant E.Span := Field (Data, Observation_Archive, "input");
      Arena : constant E.Span := Field (Data, Observation_Archive, "arena");
      Rosters : constant E.Span := Field (Data, Observation_Archive, "rosters");
      Output : constant E.Span := Field (Data, Observation_Archive, "output");
   begin
      return Original_Valid (Data, Observation_Archive) and then View.Form = E.Object_Value
        and then Dictionary_Count (Data, Observation_Archive) = 5
        and then Hex_Valid (Data, Input) and then Hex_Bytes (Data, Input)'Length = HC.Raw_Input'Size / System.Storage_Unit
        and then Hex_Valid (Data, Arena)
        and then Hex_Valid (Data, Output) and then Hex_Bytes (Data, Output)'Length = T.Raw_Result'Size / System.Storage_Unit
        and then Sequence_Count (Data, Rosters) = 12
        and then Hex_Valid (Data, Element (Data, Rosters, 0))
        and then Hex_Bytes (Data, Element (Data, Rosters, 0))'Length mod (T.Raw_Grant'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 1))
        and then Hex_Bytes (Data, Element (Data, Rosters, 1))'Length mod (T.Raw_Use'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 2))
        and then Hex_Bytes (Data, Element (Data, Rosters, 2))'Length mod (W.Raw_Row'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 3))
        and then Hex_Bytes (Data, Element (Data, Rosters, 3))'Length mod (W.Raw_Native'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 4))
        and then Hex_Bytes (Data, Element (Data, Rosters, 4))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 5))
        and then Hex_Bytes (Data, Element (Data, Rosters, 5))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 6))
        and then Hex_Bytes (Data, Element (Data, Rosters, 6))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 7))
        and then Hex_Bytes (Data, Element (Data, Rosters, 7))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 8))
        and then Hex_Bytes (Data, Element (Data, Rosters, 8))'Length mod (T.Raw_Grant'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 9))
        and then Hex_Bytes (Data, Element (Data, Rosters, 9))'Length mod (T.Raw_Use'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 10))
        and then Hex_Bytes (Data, Element (Data, Rosters, 10))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) = 0
        and then Hex_Valid (Data, Element (Data, Rosters, 11))
        and then Hex_Bytes (Data, Element (Data, Rosters, 11))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) = 0;
   end Completion_Shape;
   function Reestablish_Exchange_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Exchange_Replay_Result is
      Result : Exchange_Replay_Result;
      Rosters : constant E.Span := Field (Data, Observation_Archive, "rosters");
   begin
      if not Exchange_Shape (Data, Observation_Archive) then return Result; end if;
      declare
         Raw : constant CX.Raw_Input := RD.Load (Hex_Bytes (Data, Field (Data, Observation_Archive, "input")));
         Arena : constant E.Bytes := Hex_Bytes (Data, Field (Data, Observation_Archive, "arena"));
         Copy_grants : constant V.Raw_Grant_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 0)));
         Copy_uses : constant V.Raw_Use_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 1)));
         Copy_rows : constant W.Raw_Row_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 2)));
         Copy_observed : constant W.Raw_Native_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 3)));
         Copy_worker_receipts : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 4)));
         Copy_worker_events : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 5)));
         Copy_effect_receipts : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 6)));
         Copy_effect_events : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 7)));
         Native : constant V.Result := Exchange_Native (Raw, Arena, Copy_grants, Copy_uses, Copy_rows, Copy_observed, Copy_worker_receipts, Copy_worker_events, Copy_effect_receipts, Copy_effect_events);
         P : constant T.Raw_Input := Raw.Operation_Input.Authority;
         Output : constant T.Raw_Result := RD.Load (Hex_Bytes (Data, Field (Data, Observation_Archive, "output")));
      begin
         if not Native.Well_Formed then return Result; end if;
         Result.Action := A.Operation'Val (P.Bound.Action);
         Result.Id := T.Decode (P.Bound).Id;
         Result.State := Output_Conflict;
         Result.Native_Status := CEX.Decision'Val (Native.Status);
         if Interfaces.Unsigned_32 (Output.Disposition) = Native.Status and then
           Text_Is (Data, Field (Data, Observation_Archive, "decision"), CEX.Decision'Image (Result.Native_Status))
         then Result.State := Native_Redecided; end if;
      end;
      return Result;
   end Reestablish_Exchange_Observation;
   function Reestablish_Historical_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Operation_Replay_Result is
      Result : Operation_Replay_Result;
      Rosters : constant E.Span := Field (Data, Observation_Archive, "rosters");
   begin
      if not Completion_Shape (Data, Observation_Archive) then return Result; end if;
      declare
         Raw : constant HC.Raw_Input := RD.Load (Hex_Bytes (Data, Field (Data, Observation_Archive, "input")));
         Arena : constant E.Bytes := Hex_Bytes (Data, Field (Data, Observation_Archive, "arena"));
         Copy_grants : constant V.Raw_Grant_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 0)));
         Copy_uses : constant V.Raw_Use_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 1)));
         Copy_rows : constant W.Raw_Row_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 2)));
         Copy_observed : constant W.Raw_Native_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 3)));
         Copy_worker_receipts : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 4)));
         Copy_worker_events : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 5)));
         Copy_effect_receipts : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 6)));
         Copy_effect_events : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 7)));
         Copy_current_grants : constant V.Raw_Grant_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 8)));
         Copy_current_uses : constant V.Raw_Use_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 9)));
         Copy_current_receipts : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 10)));
         Copy_current_events : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 11)));
         Native : constant V.Result := Completion_Native (Raw, Arena, Copy_grants, Copy_uses, Copy_rows, Copy_observed, Copy_worker_receipts, Copy_worker_events, Copy_effect_receipts, Copy_effect_events, Copy_current_grants, Copy_current_uses, Copy_current_receipts, Copy_current_events);
         P : constant T.Raw_Input := Raw.Current;
         Output : constant T.Raw_Result := RD.Load (Hex_Bytes (Data, Field (Data, Observation_Archive, "output")));
      begin
         if not Native.Well_Formed then return Result; end if;
         Result.Action := A.Operation'Val (P.Bound.Action);
         Result.Id := T.Decode (P.Bound).Id;
         Result.State := Output_Conflict;
         Result.Roster_Entry := Historical_Completion_Entry;
         Result.Command := A.Replay_Use;
         Result.Historical_Status := H.Decision'Val (Native.Status);
         if Interfaces.Unsigned_32 (Output.Disposition) = Native.Status and then
           (case Result.Historical_Status is
              when H.Refused => Text_Is (Data, Field (Data, Observation_Archive, "decision"), "REFUSED"),
              when H.Resolve_Effect => Text_Is (Data, Field (Data, Observation_Archive, "decision"), "RESOLVED_EFFECT"),
              when H.Resolve_No_Effect => Text_Is (Data, Field (Data, Observation_Archive, "decision"), "RESOLVED_NO_EFFECT"),
              when H.Effect_Already => Text_Is (Data, Field (Data, Observation_Archive, "decision"), "EFFECT_ALREADY"),
              when H.No_Effect_Already => Text_Is (Data, Field (Data, Observation_Archive, "decision"), "NO_EFFECT_ALREADY"))
         then Result.State := Native_Redecided; end if;
      end;
      return Result;
   end Reestablish_Historical_Observation;
   function Collapse_Hash_Matches (Data : E.Bytes; Item : E.Span; Raw : CW.Raw_Optional_Hash) return Boolean is
   begin
      if not CW.Hash_Well_Formed (Raw) then return False; end if;
      if Raw.Present = 0 then return Null_Is (Data, Item) and then (for all B of Raw.Value => B = 0); end if;
      if not Stored_Bytes_Valid (Data, Item) then return False; end if;
      declare
         Bytes : constant E.Bytes := Stored_Bytes (Data, Item);
      begin
         return Bytes'Length = Raw.Value'Length and then
           (for all I in Raw.Value'Range => Raw.Value (I) = Bytes (Bytes'First + Q.Byte_Count (I - Raw.Value'First)));
      end;
   end Collapse_Hash_Matches;
   function Collapse_Counter_Matches (Data : E.Bytes; Item : E.Span; Raw : CW.Raw_Optional_Counter) return Boolean is
   begin
      if not CW.Counter_Well_Formed (Raw) then return False; end if;
      if Raw.Present = 0 then return Null_Is (Data, Item) and then (for all B of Raw.Value_LE => B = 0); end if;
      if not Integer_Valid (Data, Item) or else Integer_Negative (Data, Item) then return False; end if;
      declare
         Mag : constant E.Bytes := Integer_Magnitude (Data, Item);
         Value : Interfaces.Unsigned_64 := CW.Counter_Value (Raw.Value_LE);
      begin
         for I in Mag'Range loop
            if Interfaces.Unsigned_64 (Mag (I)) /= (Value and 255) then return False; end if;
            Value := Interfaces.Shift_Right (Value, System.Storage_Unit);
         end loop;
         return Value = 0;
      end;
   end Collapse_Counter_Matches;
   function Collapse_Matches (Data : E.Bytes; Item : E.Span; Raw : CW.Raw_Request) return Boolean is
   begin
      return Record_Is (Data, Item, "CollapseInput") and then CW.Well_Formed (Raw)
        and then ((Raw.Candidate_State = 0 and then Text_Is (Data, Field (Data, Item, "candidate_state"), "MUTABLE")) or else (Raw.Candidate_State = 1 and then Text_Is (Data, Field (Data, Item, "candidate_state"), "FINALIZING")) or else (Raw.Candidate_State = 2 and then Text_Is (Data, Field (Data, Item, "candidate_state"), "VALID")) or else (Raw.Candidate_State = 3 and then Text_Is (Data, Field (Data, Item, "candidate_state"), "DEGRADED")) or else (Raw.Candidate_State = 4 and then Text_Is (Data, Field (Data, Item, "candidate_state"), "DEAD")) or else (Raw.Candidate_State = 5 and then Text_Is (Data, Field (Data, Item, "candidate_state"), "ARCHIVED")) or else (Raw.Candidate_State = 6 and then Text_Is (Data, Field (Data, Item, "candidate_state"), "COLLAPSED")))
        and then ((Raw.Phase = 0 and then Text_Is (Data, Field (Data, Item, "phase"), "COMMIT")) or else (Raw.Phase = 1 and then Text_Is (Data, Field (Data, Item, "phase"), "PREPARE")))
        and then ((Raw.Evaluation_Mode = 0 and then Text_Is (Data, Field (Data, Item, "mode"), "CANDIDATE_EVALUATION")) or else (Raw.Evaluation_Mode = 1 and then Text_Is (Data, Field (Data, Item, "mode"), "CHECKPOINT_RETURN")))
        and then ((Raw.Conflicts = 0 and then Text_Is (Data, Field (Data, Item, "conflicts"), "UNMEASURED")) or else (Raw.Conflicts = 1 and then Text_Is (Data, Field (Data, Item, "conflicts"), "NONE_FOUND")) or else (Raw.Conflicts = 2 and then Text_Is (Data, Field (Data, Item, "conflicts"), "FOUND")))
        and then ((Raw.Foreign_Writes = 0 and then Text_Is (Data, Field (Data, Item, "foreign_writes"), "UNMEASURED")) or else (Raw.Foreign_Writes = 1 and then Text_Is (Data, Field (Data, Item, "foreign_writes"), "NONE_FOUND")) or else (Raw.Foreign_Writes = 2 and then Text_Is (Data, Field (Data, Item, "foreign_writes"), "FOUND")))
        and then Boolean_Is (Data, Field (Data, Item, "roster_complete"), Raw.Roster_Complete = 1)
        and then Boolean_Is (Data, Field (Data, Item, "staged_roster_complete"), Raw.Staged_Roster_Complete = 1)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "expected_parent"), Raw.Expected_Parent)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "candidate_parent"), Raw.Candidate_Parent)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "expected_subject"), Raw.Expected_Subject)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "evidence_subject"), Raw.Evidence_Subject)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "expected_base"), Raw.Expected_Base)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "candidate_base"), Raw.Candidate_Base)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "expected_delta"), Raw.Expected_Delta)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "candidate_delta"), Raw.Candidate_Delta)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "expected_root_set"), Raw.Expected_Root_Set)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "candidate_root_set"), Raw.Candidate_Root_Set)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "expected_staged_root"), Raw.Expected_Staged_Root)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "actual_staged_root"), Raw.Actual_Staged_Root)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "staged_content_root"), Raw.Staged_Content_Root)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "tested_root"), Raw.Tested_Root)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "current_requirement"), Raw.Current_Requirement)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "resulting_requirement"), Raw.Resulting_Requirement)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "evaluated_requirement"), Raw.Evaluated_Requirement)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "declared_verifiers"), Raw.Declared_Verifiers)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "executed_verifiers"), Raw.Executed_Verifiers)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "staged_evaluated_requirement"), Raw.Staged_Evaluated_Requirement)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "staged_executed_verifiers"), Raw.Staged_Executed_Verifiers)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "staged_examined_root"), Raw.Staged_Examined_Root)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "expected_checkpoint"), Raw.Expected_Checkpoint)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "witnessed_checkpoint"), Raw.Witnessed_Checkpoint)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "registered_watch_set"), Raw.Registered_Watch_Set)
        and then Collapse_Hash_Matches (Data, Field (Data, Item, "watched_set"), Raw.Watched_Set)
        and then Collapse_Counter_Matches (Data, Field (Data, Item, "generation_before"), Raw.Generation_Before)
        and then Collapse_Counter_Matches (Data, Field (Data, Item, "generation_after"), Raw.Generation_After);
   end Collapse_Matches;
   function Exchange_Value_Matches (Arena, Data : E.Bytes; Item : E.Span; Raw : CX.Raw_Material) return Boolean is
   begin
      return Dictionary_Count (Data, Item) = 13
        and then Matches (Arena, Data, Field (Data, Item, "worker_issued"), Raw.Worker_Issued)
        and then Matches (Arena, Data, Field (Data, Item, "worker_recovered"), Raw.Worker_Recovered)
        and then Matches (Arena, Data, Field (Data, Item, "canonical_issued"), Raw.Canonical_Issued)
        and then Matches (Arena, Data, Field (Data, Item, "canonical_recovered"), Raw.Canonical_Recovered)
        and then Matches (Arena, Data, Field (Data, Item, "worker_native"), Raw.Worker_Native)
        and then Matches (Arena, Data, Field (Data, Item, "canonical_native"), Raw.Canonical_Native)
        and then Digest_Matches (Data, Field (Data, Item, "worker_receipt_genesis"), Raw.Worker_Receipt_Genesis, True)
        and then Digest_Matches (Data, Field (Data, Item, "owner_receipt_genesis"), Raw.Owner_Receipt_Genesis, True)
        and then Digest_Matches (Data, Field (Data, Item, "worker_receipt_head"), Raw.Worker_Receipt_Head, True)
        and then Digest_Matches (Data, Field (Data, Item, "worker_causal_genesis"), Raw.Worker_Causal_Genesis, True)
        and then Digest_Matches (Data, Field (Data, Item, "owner_causal_genesis"), Raw.Owner_Causal_Genesis, True)
        and then Digest_Matches (Data, Field (Data, Item, "worker_causal_head"), Raw.Worker_Causal_Head, True)
        and then Digest_Matches (Data, Field (Data, Item, "quarantine_head"), Raw.Quarantine_Head, True);
   end Exchange_Value_Matches;
   function Exchange_Arguments_Matches
     (Arena, Data : E.Bytes; Arguments : E.Span; Raw : CX.Raw_Input;
      Copy_grants : V.Raw_Grant_Array;
      Copy_uses : V.Raw_Use_Array;
      Copy_rows : W.Raw_Row_Array;
      Copy_observed : W.Raw_Native_Array;
      Copy_worker_receipts : V.Raw_Chain_Array;
      Copy_worker_events : V.Raw_Chain_Array;
      Copy_effect_receipts : V.Raw_Chain_Array;
      Copy_effect_events : V.Raw_Chain_Array) return Boolean is
      P : constant CO.Raw_Input := Raw.Operation_Input;
      Request : constant E.Span := Element (Data, Arguments, 4);
   begin
      return Sequence_Count (Data, Arguments) = 12
        and then Raw.Before <= CEX.Phase'Pos (CEX.Phase'Last)
        and then Raw.Mode <= CEX.Command'Pos (CEX.Command'Last)
        and then Text_Is (Data, Element (Data, Arguments, 8), CEX.Phase'Image (CEX.Phase'Val (Raw.Before)))
        and then Text_Is (Data, Element (Data, Arguments, 9), CEX.Command'Image (CEX.Command'Val (Raw.Mode)))
        and then P.Authority.Mode = A.Command'Pos (A.Reserve_Use)
        and then Authority_Matches (Arena, Data, Element (Data, Arguments, 0), P.Authority,
          Copy_grants, Copy_uses, Copy_effect_receipts, Copy_effect_events)
        and then Matches (Arena, Data, Element (Data, Arguments, 1), P.State)
        and then Matches (Arena, Data, Element (Data, Arguments, 2), Copy_rows)
        and then Matches (Arena, Data, Element (Data, Arguments, 3), Copy_observed)
        and then Record_Is (Data, Request, "RunRequest")
        and then Matches (Arena, Data, Field (Data, Request, "bound"), P.Bound)
        and then Matches (Arena, Data, Field (Data, Request, "requester"), P.Requester)
        and then Matches (Arena, Data, Element (Data, Arguments, 5), P.Peer)
        and then Collapse_Matches (Data, Element (Data, Arguments, 6), P.Collapse)
        and then Exchange_Value_Matches (Arena, Data, Element (Data, Arguments, 7), Raw.Material)
        and then Matches (Arena, Data, Element (Data, Arguments, 10), Copy_worker_receipts)
        and then Matches (Arena, Data, Element (Data, Arguments, 11), Copy_worker_events);
   end Exchange_Arguments_Matches;
   procedure Append_Exchange
     (Raw : CX.Raw_Input; Grants : V.Raw_Grant_Array; Uses : V.Raw_Use_Array;
      Rows : W.Raw_Row_Array; Observed : W.Raw_Native_Array; Position : in out Lyt.Cursor) is
   begin
      Lyt.Append (Raw.Operation_Input.Authority, Position);
      for I in Grants'Range loop Lyt.Append (Grants (I), Position); end loop;
      for I in Uses'Range loop Lyt.Append (Uses (I), Position); end loop;
      Lyt.Append (Raw.Operation_Input.State, Position);
      Lyt.Append (Raw.Operation_Input.Bound, Position);
      Lyt.Append (Raw.Operation_Input.Requester, Position);
      Lyt.Append (Raw.Material, Position);
      for I in Rows'Range loop Lyt.Append (Rows (I), Position); end loop;
      for I in Observed'Range loop Lyt.Append (Observed (I), Position); end loop;
   end Append_Exchange;
   function Exchange_Material_Matches
     (Data : E.Bytes; Observation_Archive, Arguments_Archive : E.Span) return Boolean is
      Rosters : constant E.Span := Field (Data, Observation_Archive, "rosters");
   begin
      if not Exchange_Shape (Data, Observation_Archive) then return False; end if;
      declare
         Input_Source : constant Q.Byte_Array := Hex_Bytes (Data, Field (Data, Observation_Archive, "input"));
         Raw : constant CX.Raw_Input := RD.Load (Input_Source);
         Arena : constant E.Bytes := Hex_Bytes (Data, Field (Data, Observation_Archive, "arena"));
         Source_grants : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 0));
         Copy_grants : constant V.Raw_Grant_Array := Load_Array (Source_grants);
         Source_uses : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 1));
         Copy_uses : constant V.Raw_Use_Array := Load_Array (Source_uses);
         Source_rows : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 2));
         Copy_rows : constant W.Raw_Row_Array := Load_Array (Source_rows);
         Source_observed : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 3));
         Copy_observed : constant W.Raw_Native_Array := Load_Array (Source_observed);
         Source_worker_receipts : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 4));
         Copy_worker_receipts : constant V.Raw_Chain_Array := Load_Array (Source_worker_receipts);
         Source_worker_events : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 5));
         Copy_worker_events : constant V.Raw_Chain_Array := Load_Array (Source_worker_events);
         Source_effect_receipts : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 6));
         Copy_effect_receipts : constant V.Raw_Chain_Array := Load_Array (Source_effect_receipts);
         Source_effect_events : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 7));
         Copy_effect_events : constant V.Raw_Chain_Array := Load_Array (Source_effect_events);
         Position : Lyt.Cursor := Lyt.Start (Arena'Length);
      begin
         if not RD.Source_Padding_Valid (Input_Source, Raw)
           or else not Padding_Valid (Source_grants, Copy_grants)
           or else not Padding_Valid (Source_uses, Copy_uses)
           or else not Padding_Valid (Source_rows, Copy_rows)
           or else not Padding_Valid (Source_observed, Copy_observed)
           or else not Padding_Valid (Source_worker_receipts, Copy_worker_receipts)
           or else not Padding_Valid (Source_worker_events, Copy_worker_events)
           or else not Padding_Valid (Source_effect_receipts, Copy_effect_receipts)
           or else not Padding_Valid (Source_effect_events, Copy_effect_events) then return False; end if;
         Append_Exchange (Raw, Copy_grants, Copy_uses, Copy_rows, Copy_observed, Position);
         if not Lyt.Complete (Position) then return False; end if;
         return Exchange_Arguments_Matches (Arena, Data, Arguments_Archive, Raw, Copy_grants, Copy_uses, Copy_rows, Copy_observed, Copy_worker_receipts, Copy_worker_events, Copy_effect_receipts, Copy_effect_events);
      end;
   end Exchange_Material_Matches;
   function Historical_Snapshot_Matches
     (Arena, Data : E.Bytes; Item : E.Span; Raw : HC.Raw_Input;
      Copy_grants : V.Raw_Grant_Array;
      Copy_uses : V.Raw_Use_Array;
      Copy_rows : W.Raw_Row_Array;
      Copy_observed : W.Raw_Native_Array;
      Copy_worker_receipts : V.Raw_Chain_Array;
      Copy_worker_events : V.Raw_Chain_Array;
      Copy_effect_receipts : V.Raw_Chain_Array;
      Copy_effect_events : V.Raw_Chain_Array;
      Copy_current_grants : V.Raw_Grant_Array;
      Copy_current_uses : V.Raw_Use_Array;
      Copy_current_receipts : V.Raw_Chain_Array;
      Copy_current_events : V.Raw_Chain_Array) return Boolean is
      Proof : constant E.Span := Field (Data, Item, "owner_completion");
      Owner : constant E.Span := Field (Data, Proof, "owner");
      Arguments : constant E.Span := Field (Data, Proof, "arguments");
      Observation : constant E.Span := Field (Data, Proof, "native");
   begin
      if Dictionary_Count (Data, Proof) /= 3 or else
        not Authority_Matches (Arena, Data, Item, Raw.Current, Copy_current_grants, Copy_current_uses,
          Copy_current_receipts, Copy_current_events, 8)
        or else not Matches (Arena, Data, Field (Data, Owner, "binding"), Raw.Historical.Operation_Input.Authority.Facts.Owner_Resolution)
        or else not Digest_Matches (Data, Field (Data, Owner, "operation"), Raw.Historical.Operation_Input.Authority.Facts.Owner_Resolution.Id (A.Operation_Id), True)
        or else not Exchange_Arguments_Matches (Arena, Data, Arguments, Raw.Historical, Copy_grants, Copy_uses, Copy_rows, Copy_observed, Copy_worker_receipts, Copy_worker_events, Copy_effect_receipts, Copy_effect_events)
        or else not Exchange_Material_Matches (Data, Observation, Arguments)
      then return False; end if;
      -- Original operation_decision independently reruns the original dual
      -- observation before historical completion. Preserve that exact join.
      return Reestablish_Exchange_Observation (Data, Observation).State = Native_Redecided;
   end Historical_Snapshot_Matches;
   function Historical_Material_Matches
     (Data, Material_Data : E.Bytes; Observation_Archive, Material_Archive : E.Span) return Boolean is
      Rosters : constant E.Span := Field (Data, Observation_Archive, "rosters");
   begin
      if not Completion_Shape (Data, Observation_Archive) then return False; end if;
      declare
         Input_Source : constant Q.Byte_Array := Hex_Bytes (Data, Field (Data, Observation_Archive, "input"));
         Raw : constant HC.Raw_Input := RD.Load (Input_Source);
         Arena : constant E.Bytes := Hex_Bytes (Data, Field (Data, Observation_Archive, "arena"));
         Source_grants : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 0));
         Copy_grants : constant V.Raw_Grant_Array := Load_Array (Source_grants);
         Source_uses : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 1));
         Copy_uses : constant V.Raw_Use_Array := Load_Array (Source_uses);
         Source_rows : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 2));
         Copy_rows : constant W.Raw_Row_Array := Load_Array (Source_rows);
         Source_observed : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 3));
         Copy_observed : constant W.Raw_Native_Array := Load_Array (Source_observed);
         Source_worker_receipts : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 4));
         Copy_worker_receipts : constant V.Raw_Chain_Array := Load_Array (Source_worker_receipts);
         Source_worker_events : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 5));
         Copy_worker_events : constant V.Raw_Chain_Array := Load_Array (Source_worker_events);
         Source_effect_receipts : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 6));
         Copy_effect_receipts : constant V.Raw_Chain_Array := Load_Array (Source_effect_receipts);
         Source_effect_events : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 7));
         Copy_effect_events : constant V.Raw_Chain_Array := Load_Array (Source_effect_events);
         Source_current_grants : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 8));
         Copy_current_grants : constant V.Raw_Grant_Array := Load_Array (Source_current_grants);
         Source_current_uses : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 9));
         Copy_current_uses : constant V.Raw_Use_Array := Load_Array (Source_current_uses);
         Source_current_receipts : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 10));
         Copy_current_receipts : constant V.Raw_Chain_Array := Load_Array (Source_current_receipts);
         Source_current_events : constant Q.Byte_Array := Hex_Bytes (Data, Element (Data, Rosters, 11));
         Copy_current_events : constant V.Raw_Chain_Array := Load_Array (Source_current_events);
         Position : Lyt.Cursor := Lyt.Start (Arena'Length);
      begin
         if not RD.Source_Padding_Valid (Input_Source, Raw)
           or else not Padding_Valid (Source_grants, Copy_grants)
           or else not Padding_Valid (Source_uses, Copy_uses)
           or else not Padding_Valid (Source_rows, Copy_rows)
           or else not Padding_Valid (Source_observed, Copy_observed)
           or else not Padding_Valid (Source_worker_receipts, Copy_worker_receipts)
           or else not Padding_Valid (Source_worker_events, Copy_worker_events)
           or else not Padding_Valid (Source_effect_receipts, Copy_effect_receipts)
           or else not Padding_Valid (Source_effect_events, Copy_effect_events)
           or else not Padding_Valid (Source_current_grants, Copy_current_grants)
           or else not Padding_Valid (Source_current_uses, Copy_current_uses)
           or else not Padding_Valid (Source_current_receipts, Copy_current_receipts)
           or else not Padding_Valid (Source_current_events, Copy_current_events) then return False; end if;
         Append_Exchange (Raw.Historical, Copy_grants, Copy_uses, Copy_rows, Copy_observed, Position);
         Lyt.Append (Raw.Current, Position);
         for I in Copy_current_grants'Range loop Lyt.Append (Copy_current_grants (I), Position); end loop;
         for I in Copy_current_uses'Range loop Lyt.Append (Copy_current_uses (I), Position); end loop;
         if not Lyt.Complete (Position) then return False; end if;
         return Historical_Snapshot_Matches (Arena, Material_Data, Material_Archive, Raw, Copy_grants, Copy_uses, Copy_rows, Copy_observed, Copy_worker_receipts, Copy_worker_events, Copy_effect_receipts, Copy_effect_events, Copy_current_grants, Copy_current_uses, Copy_current_receipts, Copy_current_events);
      end;
   end Historical_Material_Matches;
   function Input_Snapshot_Matches (Data : E.Bytes; Capture : E.Span; Bound : T.Raw_Binding) return Boolean is
      Item : constant E.Span := Field (Data, Capture, "input_snapshot_raw");
   begin
      if Bound.Id (A.Input_Snapshot).Present /= 1 or else not Stored_Bytes_Valid (Data, Item) then return False; end if;
      declare
         Bytes : constant E.Bytes := Stored_Bytes (Data, Item);
         Sum : constant G.SHA.Digest := G.Hash (Bytes, (Bytes'First, Bytes'Length));
         Expected : constant T.C.Raw_Digest := Bound.Id (A.Input_Snapshot);
      begin
         return (for all I in Expected.Value'Range => Expected.Value (I) = Sum (Sum'First + Integer (I - Expected.Value'First)));
      end;
   end Input_Snapshot_Matches;
   function Operation_Capture_Matches
     (Data : E.Bytes; Observation_Archive, Material_Archive, Event_Archive : E.Span) return Boolean
   is
      Native : constant E.Span := Field (Data, Event_Archive, "native");
      Snapshot_Item : constant E.Span := Field (Data, Event_Archive, "snapshot");
      Capture_Item : constant E.Span := Field (Data, Event_Archive, "capture");
      Rosters : constant E.Span := Field (Data, Observation_Archive, "rosters");
   begin
      if Dictionary_Count (Data, Event_Archive) /= 7 or else Dictionary_Count (Data, Native) /= 2
        or else not Hex_Valid (Data, Snapshot_Item) or else not Hex_Valid (Data, Capture_Item)
        or else not OA.Same_Encoding (Data, Observation_Archive, Field (Data, Native, "observation"))
        or else not Operation_Material_Matches (Data, Observation_Archive, Material_Archive)
      then return False; end if;
      declare
         Snapshot_Data : constant E.Bytes := Hex_Bytes (Data, Snapshot_Item);
         Capture_Data : constant E.Bytes := Hex_Bytes (Data, Capture_Item);
         Snapshot : constant E.Span := (Snapshot_Data'First, Snapshot_Data'Length);
         Capture : constant E.Span := (Capture_Data'First, Capture_Data'Length);
         Arena : constant E.Bytes := Hex_Bytes (Data, Field (Data, Observation_Archive, "arena"));
      begin
         if Sequence_Count (Data, Rosters) = 12 then
            if not Completion_Shape (Data, Observation_Archive) then return False; end if;
            declare
               Raw : constant HC.Raw_Input := RD.Load (Hex_Bytes (Data, Field (Data, Observation_Archive, "input")));
               Copy_grants : constant V.Raw_Grant_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 0)));
               Copy_uses : constant V.Raw_Use_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 1)));
               Copy_rows : constant W.Raw_Row_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 2)));
               Copy_observed : constant W.Raw_Native_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 3)));
               Copy_worker_receipts : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 4)));
               Copy_worker_events : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 5)));
               Copy_effect_receipts : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 6)));
               Copy_effect_events : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 7)));
               Copy_current_grants : constant V.Raw_Grant_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 8)));
               Copy_current_uses : constant V.Raw_Use_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 9)));
               Copy_current_receipts : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 10)));
               Copy_current_events : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 11)));
            begin
               return HC.Well_Formed (Arena, Raw)
                 and then (Text_Is (Data, Field (Data, Native, "command"), "RESOLVE_EFFECT_HISTORICAL") or else
                           Text_Is (Data, Field (Data, Native, "command"), "RESOLVE_NO_EFFECT_HISTORICAL"))
                 and then Historical_Snapshot_Matches (Arena, Snapshot_Data, Snapshot, Raw, Copy_grants, Copy_uses, Copy_rows, Copy_observed, Copy_worker_receipts, Copy_worker_events, Copy_effect_receipts, Copy_effect_events, Copy_current_grants, Copy_current_uses, Copy_current_receipts, Copy_current_events)
                 and then Matches (Arena, Capture_Data, Field (Capture_Data, Capture, "binding"), Raw.Current.Bound)
                 and then Digest_Matches (Capture_Data, Field (Capture_Data, Capture, "operation"), Raw.Current.Bound.Id (A.Operation_Id), True)
                 and then Digest_Matches (Data, Field (Data, Event_Archive, "operation"), Raw.Current.Bound.Id (A.Operation_Id), True)
                 and then Input_Snapshot_Matches (Capture_Data, Capture, Raw.Current.Bound);
            end;
         else
            if not Hex_Valid (Data, Field (Data, Observation_Archive, "input")) or else
              Hex_Bytes (Data, Field (Data, Observation_Archive, "input"))'Length /= T.Raw_Input'Size / System.Storage_Unit
            then return False; end if;
            declare
               Raw : constant T.Raw_Input := RD.Load (Hex_Bytes (Data, Field (Data, Observation_Archive, "input")));
               Copy_grants : constant V.Raw_Grant_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 0)));
               Copy_uses : constant V.Raw_Use_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 1)));
               Copy_receipts : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 2)));
               Copy_events : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, Rosters, 3)));
            begin
               return T.Well_Formed (Raw)
                 and then Text_Is (Data, Field (Data, Native, "command"), A.Command'Image (A.Command'Val (Raw.Mode)))
                 and then Authority_Matches (Arena, Snapshot_Data, Snapshot, Raw, Copy_grants, Copy_uses, Copy_receipts, Copy_events)
                 and then Matches (Arena, Capture_Data, Field (Capture_Data, Capture, "binding"), Raw.Bound)
                 and then Digest_Matches (Capture_Data, Field (Capture_Data, Capture, "operation"), Raw.Bound.Id (A.Operation_Id), True)
                 and then Digest_Matches (Data, Field (Data, Event_Archive, "operation"), Raw.Bound.Id (A.Operation_Id), True)
                 and then Input_Snapshot_Matches (Capture_Data, Capture, Raw.Bound);
            end;
         end if;
      end;
   end Operation_Capture_Matches;
   generic
      Recovery : Boolean;
   function Decode_Collapse_Values_Common (Data : E.Bytes; Values : E.Span) return Collapse_Values_Result;
   function Decode_Collapse_Values_Common (Data : E.Bytes; Values : E.Span) return Collapse_Values_Result is
      package RA renames Worldline.Recovery_Archive;
      function Field (Data : E.Bytes; Item : E.Span; Name : String) return E.Span is
        (if Recovery then RA.Field (Data, Item, Name) else Archive_Field (Data, Item, Name));
      function Record_Is (Data : E.Bytes; Item : E.Span; Name : String) return Boolean is
         View : constant E.View := E.Decode (Data, Item, E.Recovery);
      begin
         if not Recovery then return Archive_Record_Is (Data, Item, Name); end if;
         if not RA.Valid (Data, Item) or else View.Form /= E.Record_Value or else not E.Bytes_Valid (Data, View.Record_Name) then return False; end if;
         declare Raw : constant E.Bytes := E.Materialize (Data, View.Record_Name); begin
            return Raw'Length = Name'Length and then (for all I in Name'Range => Raw (Raw'First + E.Count (I - Name'First)) = Character'Pos (Name (I)));
         end;
      end Record_Is;
      function Null_Is (Data : E.Bytes; Item : E.Span) return Boolean is
        (if Recovery then RA.Valid (Data, Item) and then E.Decode (Data, Item, E.Recovery).Form = E.Null_Value else Archive_Is_None (Data, Item));
      function Text_Is (Data : E.Bytes; Item : E.Span; Text : String) return Boolean is
        (if Recovery then RA.Text_Is (Data, Item, Text) else Archive_Text_Is (Data, Item, Text));
      function Boolean_Is (Data : E.Bytes; Item : E.Span; Value : Boolean) return Boolean is
        (if Recovery then RA.Boolean_Is (Data, Item, Value) else Archive_Boolean_Is (Data, Item, Value));
      function Stored_Bytes_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
        (if Recovery then RA.Stored_Bytes_Valid (Data, Item) else Archive_Bytes_Valid (Data, Item));
      function Stored_Bytes (Data : E.Bytes; Item : E.Span) return E.Bytes is
        (if Recovery then RA.Stored_Bytes (Data, Item) else Archive_Bytes (Data, Item))
        with Pre => Stored_Bytes_Valid (Data, Item);
      function Integer_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
        (if Recovery then RA.Integer_Valid (Data, Item) else Archive_Integer_Valid (Data, Item));
      function Integer_Negative (Data : E.Bytes; Item : E.Span) return Boolean is
        (if Recovery then RA.Integer_Negative (Data, Item) else Archive_Integer_Negative (Data, Item))
        with Pre => Integer_Valid (Data, Item);
      function Integer_Magnitude (Data : E.Bytes; Item : E.Span) return E.Bytes is
        (if Recovery then RA.Integer_Magnitude (Data, Item) else Archive_Integer_Magnitude (Data, Item))
        with Pre => Integer_Valid (Data, Item);
      Raw : CW.Raw_Request := (Candidate_State => 0, Phase => 0, Evaluation_Mode => 0, Conflicts => 0, Foreign_Writes => 0, Roster_Complete => 0, Staged_Roster_Complete => 0, Expected_Parent => (Present => 0, Value => (others => 0)), Candidate_Parent => (Present => 0, Value => (others => 0)), Expected_Subject => (Present => 0, Value => (others => 0)), Evidence_Subject => (Present => 0, Value => (others => 0)), Expected_Base => (Present => 0, Value => (others => 0)), Candidate_Base => (Present => 0, Value => (others => 0)), Expected_Delta => (Present => 0, Value => (others => 0)), Candidate_Delta => (Present => 0, Value => (others => 0)), Expected_Root_Set => (Present => 0, Value => (others => 0)), Candidate_Root_Set => (Present => 0, Value => (others => 0)), Expected_Staged_Root => (Present => 0, Value => (others => 0)), Actual_Staged_Root => (Present => 0, Value => (others => 0)), Staged_Content_Root => (Present => 0, Value => (others => 0)), Tested_Root => (Present => 0, Value => (others => 0)), Current_Requirement => (Present => 0, Value => (others => 0)), Resulting_Requirement => (Present => 0, Value => (others => 0)), Evaluated_Requirement => (Present => 0, Value => (others => 0)), Declared_Verifiers => (Present => 0, Value => (others => 0)), Executed_Verifiers => (Present => 0, Value => (others => 0)), Staged_Evaluated_Requirement => (Present => 0, Value => (others => 0)), Staged_Executed_Verifiers => (Present => 0, Value => (others => 0)), Staged_Examined_Root => (Present => 0, Value => (others => 0)), Expected_Checkpoint => (Present => 0, Value => (others => 0)), Witnessed_Checkpoint => (Present => 0, Value => (others => 0)), Registered_Watch_Set => (Present => 0, Value => (others => 0)), Watched_Set => (Present => 0, Value => (others => 0)), Generation_Before => (Present => 0, Value_LE => (others => 0)), Generation_After => (Present => 0, Value_LE => (others => 0)));
   begin
      if not Record_Is (Data, Values, "CollapseInput") then return (Present => False); end if;
      if Text_Is (Data, Field (Data, Values, "candidate_state"), "MUTABLE") then Raw.Candidate_State := 0;
      elsif Text_Is (Data, Field (Data, Values, "candidate_state"), "FINALIZING") then Raw.Candidate_State := 1;
      elsif Text_Is (Data, Field (Data, Values, "candidate_state"), "VALID") then Raw.Candidate_State := 2;
      elsif Text_Is (Data, Field (Data, Values, "candidate_state"), "DEGRADED") then Raw.Candidate_State := 3;
      elsif Text_Is (Data, Field (Data, Values, "candidate_state"), "DEAD") then Raw.Candidate_State := 4;
      elsif Text_Is (Data, Field (Data, Values, "candidate_state"), "ARCHIVED") then Raw.Candidate_State := 5;
      elsif Text_Is (Data, Field (Data, Values, "candidate_state"), "COLLAPSED") then Raw.Candidate_State := 6;
      else return (Present => False); end if;
      if Text_Is (Data, Field (Data, Values, "phase"), "COMMIT") then Raw.Phase := 0;
      elsif Text_Is (Data, Field (Data, Values, "phase"), "PREPARE") then Raw.Phase := 1;
      else return (Present => False); end if;
      if Text_Is (Data, Field (Data, Values, "mode"), "CANDIDATE_EVALUATION") then Raw.Evaluation_Mode := 0;
      elsif Text_Is (Data, Field (Data, Values, "mode"), "CHECKPOINT_RETURN") then Raw.Evaluation_Mode := 1;
      else return (Present => False); end if;
      if Text_Is (Data, Field (Data, Values, "conflicts"), "UNMEASURED") then Raw.Conflicts := 0;
      elsif Text_Is (Data, Field (Data, Values, "conflicts"), "NONE_FOUND") then Raw.Conflicts := 1;
      elsif Text_Is (Data, Field (Data, Values, "conflicts"), "FOUND") then Raw.Conflicts := 2;
      else return (Present => False); end if;
      if Text_Is (Data, Field (Data, Values, "foreign_writes"), "UNMEASURED") then Raw.Foreign_Writes := 0;
      elsif Text_Is (Data, Field (Data, Values, "foreign_writes"), "NONE_FOUND") then Raw.Foreign_Writes := 1;
      elsif Text_Is (Data, Field (Data, Values, "foreign_writes"), "FOUND") then Raw.Foreign_Writes := 2;
      else return (Present => False); end if;
      if Boolean_Is (Data, Field (Data, Values, "roster_complete"), True) then Raw.Roster_Complete := 1;
      elsif Boolean_Is (Data, Field (Data, Values, "roster_complete"), False) then Raw.Roster_Complete := 0;
      else return (Present => False); end if;
      if Boolean_Is (Data, Field (Data, Values, "staged_roster_complete"), True) then Raw.Staged_Roster_Complete := 1;
      elsif Boolean_Is (Data, Field (Data, Values, "staged_roster_complete"), False) then Raw.Staged_Roster_Complete := 0;
      else return (Present => False); end if;
      declare
         Item : constant E.Span := Field (Data, Values, "expected_parent");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Expected_Parent.Value'Length then return (Present => False); end if;
               Raw.Expected_Parent.Present := 1;
               for I in Raw.Expected_Parent.Value'Range loop Raw.Expected_Parent.Value (I) := Source (Source'First + E.Count (I - Raw.Expected_Parent.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "candidate_parent");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Candidate_Parent.Value'Length then return (Present => False); end if;
               Raw.Candidate_Parent.Present := 1;
               for I in Raw.Candidate_Parent.Value'Range loop Raw.Candidate_Parent.Value (I) := Source (Source'First + E.Count (I - Raw.Candidate_Parent.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "expected_subject");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Expected_Subject.Value'Length then return (Present => False); end if;
               Raw.Expected_Subject.Present := 1;
               for I in Raw.Expected_Subject.Value'Range loop Raw.Expected_Subject.Value (I) := Source (Source'First + E.Count (I - Raw.Expected_Subject.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "evidence_subject");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Evidence_Subject.Value'Length then return (Present => False); end if;
               Raw.Evidence_Subject.Present := 1;
               for I in Raw.Evidence_Subject.Value'Range loop Raw.Evidence_Subject.Value (I) := Source (Source'First + E.Count (I - Raw.Evidence_Subject.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "expected_base");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Expected_Base.Value'Length then return (Present => False); end if;
               Raw.Expected_Base.Present := 1;
               for I in Raw.Expected_Base.Value'Range loop Raw.Expected_Base.Value (I) := Source (Source'First + E.Count (I - Raw.Expected_Base.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "candidate_base");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Candidate_Base.Value'Length then return (Present => False); end if;
               Raw.Candidate_Base.Present := 1;
               for I in Raw.Candidate_Base.Value'Range loop Raw.Candidate_Base.Value (I) := Source (Source'First + E.Count (I - Raw.Candidate_Base.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "expected_delta");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Expected_Delta.Value'Length then return (Present => False); end if;
               Raw.Expected_Delta.Present := 1;
               for I in Raw.Expected_Delta.Value'Range loop Raw.Expected_Delta.Value (I) := Source (Source'First + E.Count (I - Raw.Expected_Delta.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "candidate_delta");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Candidate_Delta.Value'Length then return (Present => False); end if;
               Raw.Candidate_Delta.Present := 1;
               for I in Raw.Candidate_Delta.Value'Range loop Raw.Candidate_Delta.Value (I) := Source (Source'First + E.Count (I - Raw.Candidate_Delta.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "expected_root_set");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Expected_Root_Set.Value'Length then return (Present => False); end if;
               Raw.Expected_Root_Set.Present := 1;
               for I in Raw.Expected_Root_Set.Value'Range loop Raw.Expected_Root_Set.Value (I) := Source (Source'First + E.Count (I - Raw.Expected_Root_Set.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "candidate_root_set");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Candidate_Root_Set.Value'Length then return (Present => False); end if;
               Raw.Candidate_Root_Set.Present := 1;
               for I in Raw.Candidate_Root_Set.Value'Range loop Raw.Candidate_Root_Set.Value (I) := Source (Source'First + E.Count (I - Raw.Candidate_Root_Set.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "expected_staged_root");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Expected_Staged_Root.Value'Length then return (Present => False); end if;
               Raw.Expected_Staged_Root.Present := 1;
               for I in Raw.Expected_Staged_Root.Value'Range loop Raw.Expected_Staged_Root.Value (I) := Source (Source'First + E.Count (I - Raw.Expected_Staged_Root.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "actual_staged_root");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Actual_Staged_Root.Value'Length then return (Present => False); end if;
               Raw.Actual_Staged_Root.Present := 1;
               for I in Raw.Actual_Staged_Root.Value'Range loop Raw.Actual_Staged_Root.Value (I) := Source (Source'First + E.Count (I - Raw.Actual_Staged_Root.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "staged_content_root");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Staged_Content_Root.Value'Length then return (Present => False); end if;
               Raw.Staged_Content_Root.Present := 1;
               for I in Raw.Staged_Content_Root.Value'Range loop Raw.Staged_Content_Root.Value (I) := Source (Source'First + E.Count (I - Raw.Staged_Content_Root.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "tested_root");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Tested_Root.Value'Length then return (Present => False); end if;
               Raw.Tested_Root.Present := 1;
               for I in Raw.Tested_Root.Value'Range loop Raw.Tested_Root.Value (I) := Source (Source'First + E.Count (I - Raw.Tested_Root.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "current_requirement");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Current_Requirement.Value'Length then return (Present => False); end if;
               Raw.Current_Requirement.Present := 1;
               for I in Raw.Current_Requirement.Value'Range loop Raw.Current_Requirement.Value (I) := Source (Source'First + E.Count (I - Raw.Current_Requirement.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "resulting_requirement");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Resulting_Requirement.Value'Length then return (Present => False); end if;
               Raw.Resulting_Requirement.Present := 1;
               for I in Raw.Resulting_Requirement.Value'Range loop Raw.Resulting_Requirement.Value (I) := Source (Source'First + E.Count (I - Raw.Resulting_Requirement.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "evaluated_requirement");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Evaluated_Requirement.Value'Length then return (Present => False); end if;
               Raw.Evaluated_Requirement.Present := 1;
               for I in Raw.Evaluated_Requirement.Value'Range loop Raw.Evaluated_Requirement.Value (I) := Source (Source'First + E.Count (I - Raw.Evaluated_Requirement.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "declared_verifiers");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Declared_Verifiers.Value'Length then return (Present => False); end if;
               Raw.Declared_Verifiers.Present := 1;
               for I in Raw.Declared_Verifiers.Value'Range loop Raw.Declared_Verifiers.Value (I) := Source (Source'First + E.Count (I - Raw.Declared_Verifiers.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "executed_verifiers");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Executed_Verifiers.Value'Length then return (Present => False); end if;
               Raw.Executed_Verifiers.Present := 1;
               for I in Raw.Executed_Verifiers.Value'Range loop Raw.Executed_Verifiers.Value (I) := Source (Source'First + E.Count (I - Raw.Executed_Verifiers.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "staged_evaluated_requirement");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Staged_Evaluated_Requirement.Value'Length then return (Present => False); end if;
               Raw.Staged_Evaluated_Requirement.Present := 1;
               for I in Raw.Staged_Evaluated_Requirement.Value'Range loop Raw.Staged_Evaluated_Requirement.Value (I) := Source (Source'First + E.Count (I - Raw.Staged_Evaluated_Requirement.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "staged_executed_verifiers");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Staged_Executed_Verifiers.Value'Length then return (Present => False); end if;
               Raw.Staged_Executed_Verifiers.Present := 1;
               for I in Raw.Staged_Executed_Verifiers.Value'Range loop Raw.Staged_Executed_Verifiers.Value (I) := Source (Source'First + E.Count (I - Raw.Staged_Executed_Verifiers.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "staged_examined_root");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Staged_Examined_Root.Value'Length then return (Present => False); end if;
               Raw.Staged_Examined_Root.Present := 1;
               for I in Raw.Staged_Examined_Root.Value'Range loop Raw.Staged_Examined_Root.Value (I) := Source (Source'First + E.Count (I - Raw.Staged_Examined_Root.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "expected_checkpoint");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Expected_Checkpoint.Value'Length then return (Present => False); end if;
               Raw.Expected_Checkpoint.Present := 1;
               for I in Raw.Expected_Checkpoint.Value'Range loop Raw.Expected_Checkpoint.Value (I) := Source (Source'First + E.Count (I - Raw.Expected_Checkpoint.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "witnessed_checkpoint");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Witnessed_Checkpoint.Value'Length then return (Present => False); end if;
               Raw.Witnessed_Checkpoint.Present := 1;
               for I in Raw.Witnessed_Checkpoint.Value'Range loop Raw.Witnessed_Checkpoint.Value (I) := Source (Source'First + E.Count (I - Raw.Witnessed_Checkpoint.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "registered_watch_set");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Registered_Watch_Set.Value'Length then return (Present => False); end if;
               Raw.Registered_Watch_Set.Present := 1;
               for I in Raw.Registered_Watch_Set.Value'Range loop Raw.Registered_Watch_Set.Value (I) := Source (Source'First + E.Count (I - Raw.Registered_Watch_Set.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "watched_set");
      begin
         if not Null_Is (Data, Item) then
            if not Stored_Bytes_Valid (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Stored_Bytes (Data, Item); begin
               if Source'Length /= Raw.Watched_Set.Value'Length then return (Present => False); end if;
               Raw.Watched_Set.Present := 1;
               for I in Raw.Watched_Set.Value'Range loop Raw.Watched_Set.Value (I) := Source (Source'First + E.Count (I - Raw.Watched_Set.Value'First)); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "generation_before");
      begin
         if not Null_Is (Data, Item) then
            if not Integer_Valid (Data, Item) or else Integer_Negative (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Integer_Magnitude (Data, Item); begin
               if Source'Length > Raw.Generation_Before.Value_LE'Length then return (Present => False); end if;
               Raw.Generation_Before.Present := 1;
               for I in Source'Range loop Raw.Generation_Before.Value_LE (Raw.Generation_Before.Value_LE'First + Integer (I - Source'First)) := Source (I); end loop;
            end;
         end if;
      end;
      declare
         Item : constant E.Span := Field (Data, Values, "generation_after");
      begin
         if not Null_Is (Data, Item) then
            if not Integer_Valid (Data, Item) or else Integer_Negative (Data, Item) then return (Present => False); end if;
            declare Source : constant E.Bytes := Integer_Magnitude (Data, Item); begin
               if Source'Length > Raw.Generation_After.Value_LE'Length then return (Present => False); end if;
               Raw.Generation_After.Present := 1;
               for I in Source'Range loop Raw.Generation_After.Value_LE (Raw.Generation_After.Value_LE'First + Integer (I - Source'First)) := Source (I); end loop;
            end;
         end if;
      end;
      if not CW.Well_Formed (Raw) then return (Present => False); end if;
      return (Present => True, Raw => Raw);
   end Decode_Collapse_Values_Common;
   function Decode_Operation_Collapse is new Decode_Collapse_Values_Common (False);
   function Decode_Recovery_Collapse is new Decode_Collapse_Values_Common (True);
   function Decode_Collapse_Values (Data : E.Bytes; Values : E.Span) return Collapse_Values_Result is
     (Decode_Operation_Collapse (Data, Values));
   function Decode_Recovery_Collapse_Values (Data : E.Bytes; Values : E.Span) return Collapse_Values_Result is
     (Decode_Recovery_Collapse (Data, Values));
   function Reestablish_Reservation_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Operation_Replay_Result
   is
      Result : Operation_Replay_Result;
      input_Archive : constant E.Span := Field (Data, Observation_Archive, "input");
      arena_Archive : constant E.Span := Field (Data, Observation_Archive, "arena");
      rosters_Archive : constant E.Span := Field (Data, Observation_Archive, "rosters");
      output_Archive : constant E.Span := Field (Data, Observation_Archive, "output");
      View : constant E.View := E.Decode (Data, Observation_Archive, E.Operation);
   begin
      if not Original_Valid (Data, Observation_Archive) or else View.Form /= E.Object_Value
        or else (if SA.Valid (Data, Observation_Archive) then SA.Member_Count (Data, Observation_Archive) /= 5
                 else E.Array_Length (Data, View.Children) /= 5)
        or else not Hex_Valid (Data, input_Archive)
        or else not Hex_Valid (Data, arena_Archive)
        or else not Hex_Valid (Data, output_Archive)
        or else Hex_Bytes (Data, input_Archive)'Length /= T.Raw_Input'Size / System.Storage_Unit
        or else Hex_Bytes (Data, output_Archive)'Length /= T.Raw_Result'Size / System.Storage_Unit
        or else Sequence_Count (Data, rosters_Archive) /= 4
        or else not Hex_Valid (Data, Element (Data, rosters_Archive, 0))
        or else Hex_Bytes (Data, Element (Data, rosters_Archive, 0))'Length mod (T.Raw_Grant'Size / System.Storage_Unit) /= 0
        or else not Hex_Valid (Data, Element (Data, rosters_Archive, 1))
        or else Hex_Bytes (Data, Element (Data, rosters_Archive, 1))'Length mod (T.Raw_Use'Size / System.Storage_Unit) /= 0
        or else not Hex_Valid (Data, Element (Data, rosters_Archive, 2))
        or else Hex_Bytes (Data, Element (Data, rosters_Archive, 2))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) /= 0
        or else not Hex_Valid (Data, Element (Data, rosters_Archive, 3))
        or else Hex_Bytes (Data, Element (Data, rosters_Archive, 3))'Length mod (T.C.Raw_Row'Size / System.Storage_Unit) /= 0
      then return Result; end if;
      declare
         Authority : constant T.Raw_Input := RD.Load (Hex_Bytes (Data, input_Archive));
         Arena : constant Q.Byte_Array := Hex_Bytes (Data, arena_Archive);
         Copy_grants : constant V.Raw_Grant_Array := Load_Array (Hex_Bytes (Data, Element (Data, rosters_Archive, 0)));
         Copy_uses : constant V.Raw_Use_Array := Load_Array (Hex_Bytes (Data, Element (Data, rosters_Archive, 1)));
         Copy_receipts : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, rosters_Archive, 2)));
         Copy_events : constant V.Raw_Chain_Array := Load_Array (Hex_Bytes (Data, Element (Data, rosters_Archive, 3)));
      begin
         if Authority.Mode /= A.Command'Pos (A.Reserve_Use)
           or else not T.Well_Formed (Authority)
           or else not T.Recovery_Well_Formed (Arena, Authority.Facts)
           or else not (for all I in Copy_grants'Range => T.Well_Formed (Copy_grants (I)))
           or else not (for all I in Copy_uses'Range => T.Well_Formed (Copy_uses (I)))
           or else not (for all I in Copy_receipts'Range => T.C.Well_Formed (Copy_receipts (I)))
           or else not (for all I in Copy_events'Range => T.C.Well_Formed (Copy_events (I)))
         then return Result; end if;
         Result.Command := A.Command'Val (Authority.Mode);
         Result.Native_Status := A.Reservation_Decision (Arena, Owned (Copy_grants), Owned (Copy_uses), T.Decode (Authority.Bound), T.Decode (Authority.Now).Value);
         Result.Action := A.Operation'Val (Authority.Bound.Action);
         Result.Id := T.Decode (Authority.Bound).Id;
         Result.State := Output_Conflict;
         declare
            Output : constant T.Raw_Result := RD.Load (Hex_Bytes (Data, output_Archive));
         begin
            if Interfaces.Unsigned_32 (Output.Disposition) = A.Decision'Pos (Result.Native_Status)
              and then Text_Is (Data, Field (Data, Observation_Archive, "decision"), A.Decision'Image (Result.Native_Status))
            then Result.State := Native_Redecided; end if;
         end;
      end;
      return Result;
   end Reestablish_Reservation_Observation;
   function Archive_Text_Is (Data : E.Bytes; Item : E.Span; Text : String) return Boolean is (Text_Is (Data, Item, Text));
   function Archive_Boolean_Is (Data : E.Bytes; Item : E.Span; Value : Boolean) return Boolean is (Boolean_Is (Data, Item, Value));
   function Archive_Bytes_Valid (Data : E.Bytes; Item : E.Span) return Boolean is (Stored_Bytes_Valid (Data, Item));
   function Archive_Bytes (Data : E.Bytes; Item : E.Span) return E.Bytes is (Stored_Bytes (Data, Item));
   function Archive_Integer_Valid (Data : E.Bytes; Item : E.Span) return Boolean is (Integer_Valid (Data, Item));
   function Archive_Integer_Negative (Data : E.Bytes; Item : E.Span) return Boolean is (Integer_Negative (Data, Item));
   function Archive_Integer_Magnitude (Data : E.Bytes; Item : E.Span) return E.Bytes is (Integer_Magnitude (Data, Item));
   function Archive_Is_None (Data : E.Bytes; Item : E.Span) return Boolean is (Null_Is (Data, Item));
   function Archive_Length (Data : E.Bytes; Item : E.Span) return E.Count is (Sequence_Count (Data, Item));
   function Archive_Index (Data : E.Bytes; Item : E.Span; Index : E.Count) return E.Span is (Element (Data, Item, Index));
   function Archive_Record_Is (Data : E.Bytes; Item : E.Span; Name : String) return Boolean is (Record_Is (Data, Item, Name));
   function Archive_Is_Sequence (Data : E.Bytes; Item : E.Span) return Boolean is
     ((SA.Valid (Data, Item) and then (P.Type_Is (Data, Item, "tuple") or else P.Type_Is (Data, Item, "list")))
      or else (Original_Valid (Data, Item) and then E.Decode (Data, Item, E.Operation).Form in E.Tuple_Value | E.List_Value));
   function Archive_Equal (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (OA.Valid (Data, Left) and then OA.Valid (Data, Right) and then OA.Same_Encoding (Data, Left, Right));
   function Archive_Image_Matches
     (Data : E.Bytes; Image, Value : E.Span;
      Image_Scoped, Value_Scoped : Boolean := False;
      Carrier_Scoped : Boolean := False) return Boolean
   is
      Carrier : constant E.View := E.Decode (Data, Image, E.Operation);
   begin
      if Carrier_Scoped then
         if not P.Valid_Bytes (Data, Image) then return False; end if;
      elsif not Original_Valid (Data, Image) or else Carrier.Form /= E.Bytes_Value
        or else not E.Bytes_Valid (Data, Carrier.Payload) then return False; end if;
      declare
         Actual : constant E.Bytes :=
           (if Carrier_Scoped then P.Bytes_Value (Data, Image)
            else E.Materialize (Data, Carrier.Payload));
      begin
         return Worldline.Recovery_Archive.Ordered_Source_Value_Matches
           (Actual, Data, (Actual'First, Actual'Length), Value,
            Image_Scoped, Value_Scoped);
      end;
   end Archive_Image_Matches;
   function Actor_Material_Matches
     (Data : E.Bytes; Observation_Archive, Material_Archive : E.Span) return Boolean
   is
      actor_input_Archive : constant E.Span := Field (Data, Observation_Archive, "actor_input");
      actor_arena_Archive : constant E.Span := Field (Data, Observation_Archive, "actor_arena");
      actor_rosters_Archive : constant E.Span := Field (Data, Observation_Archive, "actor_rosters");
      authority_input_Archive : constant E.Span := Field (Data, Observation_Archive, "authority_input");
      authority_arena_Archive : constant E.Span := Field (Data, Observation_Archive, "authority_arena");
      authority_rosters_Archive : constant E.Span := Field (Data, Observation_Archive, "authority_rosters");
      crosswalk_Archive : constant E.Span := Field (Data, Observation_Archive, "crosswalk");
      raw_output_Archive : constant E.Span := Field (Data, Observation_Archive, "raw_output");
   begin
      if not Archive_Record_Is (Data, Observation_Archive, "ActorExecutionNativeDecision")
        or else not Bytes_Shape (Data, actor_input_Archive, D.Raw_Packet'Size / System.Storage_Unit)
        or else not Bytes_Shape (Data, authority_input_Archive, T.Raw_Input'Size / System.Storage_Unit)
        or else not Bytes_Shape (Data, crosswalk_Archive, X.Raw_Crosswalk'Size / System.Storage_Unit)
        or else not Archive_Bytes_Valid (Data, actor_arena_Archive)
        or else not Archive_Bytes_Valid (Data, authority_arena_Archive)
        or else not Tuple_Is (Data, actor_rosters_Archive)
        or else Sequence_Count (Data, actor_rosters_Archive) /= 14
        or else not Roster_Valid (Data, actor_rosters_Archive, 0, "history", N.Raw_Scope_Frame'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, actor_rosters_Archive, 1, "proposed_history", N.Raw_Scope_Frame'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, actor_rosters_Archive, 2, "rows", W.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, actor_rosters_Archive, 3, "proposed_rows", W.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, actor_rosters_Archive, 4, "projection", N.Raw_Projection'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, actor_rosters_Archive, 5, "proposed_projection", N.Raw_Projection'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, actor_rosters_Archive, 6, "buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, actor_rosters_Archive, 7, "proposed_buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, actor_rosters_Archive, 8, "actual_buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, actor_rosters_Archive, 9, "observed", W.Raw_Native'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, actor_rosters_Archive, 10, "facts", O.Raw_Facts'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, actor_rosters_Archive, 11, "capabilities", D.Raw_Capability'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, actor_rosters_Archive, 12, "groups", W.Raw_Quantity'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, actor_rosters_Archive, 13, "proc_groups", W.Raw_Quantity'Size / System.Storage_Unit)
        or else not Tuple_Is (Data, authority_rosters_Archive)
        or else Sequence_Count (Data, authority_rosters_Archive) /= 4
        or else not Roster_Valid (Data, authority_rosters_Archive, 0, "grants", T.Raw_Grant'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, authority_rosters_Archive, 1, "uses", T.Raw_Use'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, authority_rosters_Archive, 2, "receipts", T.C.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, authority_rosters_Archive, 3, "events", T.C.Raw_Row'Size / System.Storage_Unit)
      then return False; end if;
      declare
         Actor_Source : constant Q.Byte_Array := Archive_Bytes (Data, actor_input_Archive);
         Authority_Source : constant Q.Byte_Array := Archive_Bytes (Data, authority_input_Archive);
         Crosswalk_Source : constant Q.Byte_Array := Archive_Bytes (Data, crosswalk_Archive);
         Raw : constant D.Raw_Packet := RD.Load (Actor_Source);
         Authority : constant T.Raw_Input := RD.Load (Authority_Source);
         Crosswalk : constant X.Raw_Crosswalk := RD.Load (Crosswalk_Source);
         Arena : constant Q.Byte_Array := Archive_Bytes (Data, actor_arena_Archive);
         Authority_Arena : constant Q.Byte_Array := Archive_Bytes (Data, authority_arena_Archive);
         Source_history : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 0));
         Copy_history : constant N.Raw_History_Array := Load_Array (Source_history);
         Source_proposed_history : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 1));
         Copy_proposed_history : constant N.Raw_History_Array := Load_Array (Source_proposed_history);
         Source_rows : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 2));
         Copy_rows : constant W.Raw_Row_Array := Load_Array (Source_rows);
         Source_proposed_rows : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 3));
         Copy_proposed_rows : constant W.Raw_Row_Array := Load_Array (Source_proposed_rows);
         Source_projection : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 4));
         Copy_projection : constant N.Raw_Projection_Array := Load_Array (Source_projection);
         Source_proposed_projection : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 5));
         Copy_proposed_projection : constant N.Raw_Projection_Array := Load_Array (Source_proposed_projection);
         Source_buckets : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 6));
         Copy_buckets : constant N.Raw_Bucket_Array := Load_Array (Source_buckets);
         Source_proposed_buckets : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 7));
         Copy_proposed_buckets : constant N.Raw_Bucket_Array := Load_Array (Source_proposed_buckets);
         Source_actual_buckets : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 8));
         Copy_actual_buckets : constant N.Raw_Bucket_Array := Load_Array (Source_actual_buckets);
         Source_observed : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 9));
         Copy_observed : constant W.Raw_Native_Array := Load_Array (Source_observed);
         Source_facts : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 10));
         Copy_facts : constant N.Raw_Facts_Array := Load_Array (Source_facts);
         Source_capabilities : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 11));
         Copy_capabilities : constant D.Raw_Capability_Array := Load_Array (Source_capabilities);
         Source_groups : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 12));
         Copy_groups : constant D.Raw_Group_Array := Load_Array (Source_groups);
         Source_proc_groups : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, actor_rosters_Archive, 13));
         Copy_proc_groups : constant D.Raw_Group_Array := Load_Array (Source_proc_groups);
         Source_grants : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, authority_rosters_Archive, 0));
         Copy_grants : constant V.Raw_Grant_Array := Load_Array (Source_grants);
         Source_uses : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, authority_rosters_Archive, 1));
         Copy_uses : constant V.Raw_Use_Array := Load_Array (Source_uses);
         Source_receipts : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, authority_rosters_Archive, 2));
         Copy_receipts : constant V.Raw_Chain_Array := Load_Array (Source_receipts);
         Source_events : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, authority_rosters_Archive, 3));
         Copy_events : constant V.Raw_Chain_Array := Load_Array (Source_events);
         Resource_Position : Lyt.Cursor := Lyt.Start (Arena'Length);
         Authority_Position : Lyt.Cursor := Lyt.Start (Authority_Arena'Length);
      begin
         if not RD.Source_Padding_Valid (Actor_Source, Raw)
           or else not RD.Source_Padding_Valid (Authority_Source, Authority)
           or else not RD.Source_Padding_Valid (Crosswalk_Source, Crosswalk)
           or else not Padding_Valid (Source_history, Copy_history)
           or else not Padding_Valid (Source_proposed_history, Copy_proposed_history)
           or else not Padding_Valid (Source_rows, Copy_rows)
           or else not Padding_Valid (Source_proposed_rows, Copy_proposed_rows)
           or else not Padding_Valid (Source_projection, Copy_projection)
           or else not Padding_Valid (Source_proposed_projection, Copy_proposed_projection)
           or else not Padding_Valid (Source_buckets, Copy_buckets)
           or else not Padding_Valid (Source_proposed_buckets, Copy_proposed_buckets)
           or else not Padding_Valid (Source_actual_buckets, Copy_actual_buckets)
           or else not Padding_Valid (Source_observed, Copy_observed)
           or else not Padding_Valid (Source_facts, Copy_facts)
           or else not Padding_Valid (Source_capabilities, Copy_capabilities)
           or else not Padding_Valid (Source_groups, Copy_groups)
           or else not Padding_Valid (Source_proc_groups, Copy_proc_groups)
           or else not Padding_Valid (Source_grants, Copy_grants)
           or else not Padding_Valid (Source_uses, Copy_uses)
           or else not Padding_Valid (Source_receipts, Copy_receipts)
           or else not Padding_Valid (Source_events, Copy_events) then return False; end if;
         Lyt.Append (Raw.Ledger, Resource_Position);
         for I in Copy_history'Range loop Lyt.Append (Copy_history (I), Resource_Position); end loop;
         for I in Copy_proposed_history'Range loop Lyt.Append (Copy_proposed_history (I), Resource_Position); end loop;
         for I in Copy_rows'Range loop Lyt.Append (Copy_rows (I), Resource_Position); end loop;
         for I in Copy_proposed_rows'Range loop Lyt.Append (Copy_proposed_rows (I), Resource_Position); end loop;
         for I in Copy_projection'Range loop Lyt.Append (Copy_projection (I), Resource_Position); end loop;
         for I in Copy_proposed_projection'Range loop Lyt.Append (Copy_proposed_projection (I), Resource_Position); end loop;
         for I in Copy_buckets'Range loop Lyt.Append (Copy_buckets (I), Resource_Position); end loop;
         for I in Copy_proposed_buckets'Range loop Lyt.Append (Copy_proposed_buckets (I), Resource_Position); end loop;
         for I in Copy_actual_buckets'Range loop Lyt.Append (Copy_actual_buckets (I), Resource_Position); end loop;
         for I in Copy_observed'Range loop Lyt.Append (Copy_observed (I), Resource_Position); end loop;
         for I in Copy_facts'Range loop Lyt.Append (Copy_facts (I), Resource_Position); end loop;
         Lyt.Append (Raw.Captured, Resource_Position);
         for I in Copy_capabilities'Range loop Lyt.Append (Copy_capabilities (I), Resource_Position); end loop;
         for I in Copy_groups'Range loop Lyt.Append (Copy_groups (I), Resource_Position); end loop;
         for I in Copy_proc_groups'Range loop Lyt.Append (Copy_proc_groups (I), Resource_Position); end loop;
         Lyt.Append (Crosswalk, Resource_Position);
         Lyt.Append (Authority, Authority_Position);
         for I in Copy_grants'Range loop Lyt.Append (Copy_grants (I), Authority_Position); end loop;
         for I in Copy_uses'Range loop Lyt.Append (Copy_uses (I), Authority_Position); end loop;
         if not Lyt.Complete (Resource_Position) or else not Lyt.Complete (Authority_Position) then return False; end if;
         return Dictionary_Count (Data, Material_Archive) = 7
           and then Authority.Mode = A.Command'Pos (A.Authorize_Execution)
           and then Matches (Arena, Data, Field (Data, Material_Archive, "crosswalk"), Crosswalk)
           and then Packet_Matches (Arena, Data, Field (Data, Material_Archive, "packet"), Raw.Ledger, Copy_history, Copy_proposed_history, Copy_rows, Copy_proposed_rows, Copy_projection, Copy_proposed_projection, Copy_buckets, Copy_proposed_buckets, Copy_actual_buckets, Copy_observed, Copy_facts)
           and then Authority_Matches (Authority_Arena, Data, Field (Data, Material_Archive, "authority_snapshot"), Authority, Copy_grants, Copy_uses, Copy_receipts, Copy_events)
           and then Matches (Arena, Data, Field (Data, Material_Archive, "actor"), Raw.Captured)
           and then Matches (Arena, Data, Field (Data, Material_Archive, "capabilities"), Copy_capabilities)
           and then Matches (Arena, Data, Field (Data, Material_Archive, "groups"), Copy_groups)
           and then Matches (Arena, Data, Field (Data, Material_Archive, "proc_groups"), Copy_proc_groups);
      end;
   end Actor_Material_Matches;

   function Root_Scoped_Material_Matches
     (Data : E.Bytes; Observation_Archive, Packet_Archive : E.Span) return Boolean is
      Input : constant E.Span := Field (Data, Observation_Archive, "actor_input");
      Storage : constant E.Span := Field (Data, Observation_Archive, "resource_arena");
      Rosters : constant E.Span := Field (Data, Observation_Archive, "resource_rosters");
   begin
      if not Archive_Record_Is (Data, Observation_Archive, "ResourceChildNativeObservation")
        or else not Bytes_Shape (Data, Input, D.Raw_Packet'Size / System.Storage_Unit)
        or else not Archive_Bytes_Valid (Data, Storage) or else Sequence_Count (Data, Rosters) /= 17
        or else not Roster_Valid (Data, Rosters, 0, "history", N.Raw_Scope_Frame'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 1, "proposed_history", N.Raw_Scope_Frame'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 2, "rows", W.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 3, "proposed_rows", W.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 4, "projection", N.Raw_Projection'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 5, "proposed_projection", N.Raw_Projection'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 6, "buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 7, "proposed_buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 8, "actual_buckets", N.Raw_Bucket'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 9, "observed", W.Raw_Native'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 10, "facts", O.Raw_Facts'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 11, "capabilities", D.Raw_Capability'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 12, "groups", W.Raw_Quantity'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 13, "proc_groups", W.Raw_Quantity'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 14, "tasks", Y.Raw_Task'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 15, "processes", Y.Raw_Process'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, Rosters, 16, "namespaces", Y.Raw_Namespace'Size / System.Storage_Unit)
      then return False; end if;
      declare
         Source : constant Q.Byte_Array := Archive_Bytes (Data, Input);
         Raw : constant D.Raw_Packet := RD.Load (Source);
         Arena : constant Q.Byte_Array := Archive_Bytes (Data, Storage);
         Source_history : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, Rosters, 0));
         Copy_history : constant N.Raw_History_Array := Load_Array (Source_history);
         Source_proposed_history : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, Rosters, 1));
         Copy_proposed_history : constant N.Raw_History_Array := Load_Array (Source_proposed_history);
         Source_rows : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, Rosters, 2));
         Copy_rows : constant W.Raw_Row_Array := Load_Array (Source_rows);
         Source_proposed_rows : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, Rosters, 3));
         Copy_proposed_rows : constant W.Raw_Row_Array := Load_Array (Source_proposed_rows);
         Source_projection : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, Rosters, 4));
         Copy_projection : constant N.Raw_Projection_Array := Load_Array (Source_projection);
         Source_proposed_projection : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, Rosters, 5));
         Copy_proposed_projection : constant N.Raw_Projection_Array := Load_Array (Source_proposed_projection);
         Source_buckets : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, Rosters, 6));
         Copy_buckets : constant N.Raw_Bucket_Array := Load_Array (Source_buckets);
         Source_proposed_buckets : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, Rosters, 7));
         Copy_proposed_buckets : constant N.Raw_Bucket_Array := Load_Array (Source_proposed_buckets);
         Source_actual_buckets : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, Rosters, 8));
         Copy_actual_buckets : constant N.Raw_Bucket_Array := Load_Array (Source_actual_buckets);
         Source_observed : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, Rosters, 9));
         Copy_observed : constant W.Raw_Native_Array := Load_Array (Source_observed);
         Source_facts : constant Q.Byte_Array := Archive_Bytes (Data, Roster_Data (Data, Rosters, 10));
         Copy_facts : constant N.Raw_Facts_Array := Load_Array (Source_facts);
      begin
         return RD.Source_Padding_Valid (Source, Raw)
           and then Padding_Valid (Source_history, Copy_history)
           and then Padding_Valid (Source_proposed_history, Copy_proposed_history)
           and then Padding_Valid (Source_rows, Copy_rows)
           and then Padding_Valid (Source_proposed_rows, Copy_proposed_rows)
           and then Padding_Valid (Source_projection, Copy_projection)
           and then Padding_Valid (Source_proposed_projection, Copy_proposed_projection)
           and then Padding_Valid (Source_buckets, Copy_buckets)
           and then Padding_Valid (Source_proposed_buckets, Copy_proposed_buckets)
           and then Padding_Valid (Source_actual_buckets, Copy_actual_buckets)
           and then Padding_Valid (Source_observed, Copy_observed)
           and then Padding_Valid (Source_facts, Copy_facts)
           and then Packet_Matches (Arena, Data, Packet_Archive, Raw.Ledger, Copy_history, Copy_proposed_history, Copy_rows, Copy_proposed_rows, Copy_projection, Copy_proposed_projection, Copy_buckets, Copy_proposed_buckets, Copy_actual_buckets, Copy_observed, Copy_facts);
      end;
   end Root_Scoped_Material_Matches;
end Worldline.Retained_Evidence_Replay;

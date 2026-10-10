with Worldline.Custody_V2_Empty_Seed;
with Worldline.Custody_V2_Values;
with Worldline.Retained_Raw_Decode;
with Worldline.Scoped_Archive;
with System;
with Interfaces;
package body Worldline.Actor_Archive_Replay with SPARK_Mode is
   package P renames Worldline.Custody_V2_Values;
   package RD renames Worldline.Retained_Raw_Decode;
   package SA renames Worldline.Scoped_Archive;
   package OA renames SA.A;
   package V renames R.V;
   package Q renames V.Q;
   package N renames V.N;
   package W renames V.W;
   package O renames V.O;
   package D renames V.D;
   package WX renames V.X;
   package T renames V.T;
   package G renames Worldline.Custody_V2_Empty_Seed;
   use type Q.Byte_Count;
   use type Q.Byte;
   use type Interfaces.Unsigned_32;
   use type E.Value_Kind;
   use type Q.Byte_Array;
   use type R.Replay_State;
   use type A.Command;
   use type R.Operation_Entry;
   function Field (Data : E.Bytes; Item : E.Span; Name : String) return E.Span is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if SA.Valid (Data, Item) then return P.Record_Field (Data, Item, Name);
      elsif OA.Valid (Data, Item) and then View.Form = E.Record_Value then
         if E.Array_Length (Data, View.Children) > 0 then
            for I in E.Count range 0 .. E.Array_Length (Data, View.Children) - 1 loop
               declare
                  Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, View.Children, I), E.Finalization);
               begin
                  if Pair.Form = E.List_Value and then E.Array_Length (Data, Pair.Children) = 2
                    and then E.Text_Is (Data, E.Decode (Data, E.Array_Element (Data, Pair.Children, 0), E.Finalization), Name)
                  then return E.Array_Element (Data, Pair.Children, 1); end if;
               end;
            end loop;
         end if;
         return (1, 0);
      else return OA.Field (Data, Item, Name); end if;
   end Field;
   function Text_Is (Data : E.Bytes; Item : E.Span; Text : String) return Boolean is
   begin
      if SA.Valid (Data, Item) then return SA.Text_Is (Data, Item, Text);
      else return OA.Valid (Data, Item) and then E.Text_Is (Data, E.Decode (Data, Item, E.Operation), Text); end if;
   end Text_Is;
   function Sequence_Count (Data : E.Bytes; Item : E.Span) return E.Count is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if SA.Valid (Data, Item) then return P.Count (Data, Item);
      elsif OA.Valid (Data, Item) and then View.Form in E.List_Value | E.Tuple_Value then
         return E.Array_Length (Data, View.Children);
      else return 0; end if;
   end Sequence_Count;
   function Element (Data : E.Bytes; Item : E.Span; Ordinal : E.Count) return E.Span is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if SA.Valid (Data, Item) then return P.Element (Data, Item, Ordinal);
      elsif OA.Valid (Data, Item) and then View.Form in E.List_Value | E.Tuple_Value then
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
      elsif OA.Valid (Data, Item) and then View.Form = E.Text_Value and then E.Bytes_Valid (Data, View.Payload) then
         return E.Materialize (Data, View.Payload);
      else return (1 .. 0 => 0); end if;
   end Text_Bytes;
   function Hex_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if not P.Valid_Text (Data, Item) and then
        not (OA.Valid (Data, Item) and then View.Form = E.Text_Value and then E.Bytes_Valid (Data, View.Payload))
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
   begin
      return P.Valid_Bytes (Data, Item) and then P.Bytes_Value (Data, Item)'Length = Size;
   end Bytes_Shape;
   function Transport_Zero (Data : E.Bytes; Item : E.Span) return Boolean is
      Count : constant P.Count_Result := P.Nonnegative_Count (Data, Item);
   begin
      return Count.Present and then Count.Value = 0;
   end Transport_Zero;
   function Roster_Item (Data : E.Bytes; Rosters : E.Span; Ordinal : E.Count) return E.Span is
     (Element (Data, Rosters, Ordinal));
   function Roster_Data (Data : E.Bytes; Rosters : E.Span; Ordinal : E.Count) return E.Span is
     (Element (Data, Roster_Item (Data, Rosters, Ordinal), 1));
   function Roster_Valid (Data : E.Bytes; Rosters : E.Span; Ordinal : E.Count;
                          Name : String; Size : E.Count) return Boolean is
      Item : constant E.Span := Roster_Item (Data, Rosters, Ordinal);
      Raw : constant E.Span := Roster_Data (Data, Rosters, Ordinal);
      Count : constant P.Count_Result := P.Nonnegative_Count (Data, Element (Data, Item, 2));
   begin
      if not P.Type_Is (Data, Item, "tuple") or else Sequence_Count (Data, Item) /= 3
        or else not Text_Is (Data, Element (Data, Item, 0), Name)
        or else not P.Valid_Bytes (Data, Raw) or else not Count.Present or else Size = 0
      then return False; end if;
      declare
         Bytes : constant E.Bytes := P.Bytes_Value (Data, Raw);
      begin
         -- Divide only after divisibility: no multiplying attacker count by
         -- stride, no extra roster count bound, no partial row acceptance.
         return Bytes'Length mod Size = 0 and then Count.Value = Bytes'Length / Size;
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
   function Reestablish_Actor_Observation
     (Data : E.Bytes; Observation_Archive : E.Span) return Actor_Replay_Result
   is
      Result : Actor_Replay_Result;
      actor_input_Archive : constant E.Span := Field (Data, Observation_Archive, "actor_input");
      actor_arena_Archive : constant E.Span := Field (Data, Observation_Archive, "actor_arena");
      actor_rosters_Archive : constant E.Span := Field (Data, Observation_Archive, "actor_rosters");
      authority_input_Archive : constant E.Span := Field (Data, Observation_Archive, "authority_input");
      authority_arena_Archive : constant E.Span := Field (Data, Observation_Archive, "authority_arena");
      authority_rosters_Archive : constant E.Span := Field (Data, Observation_Archive, "authority_rosters");
      crosswalk_Archive : constant E.Span := Field (Data, Observation_Archive, "crosswalk");
      raw_output_Archive : constant E.Span := Field (Data, Observation_Archive, "raw_output");
   begin
      if not P.Type_Is (Data, Observation_Archive, "ActorExecutionNativeDecision")
        or else not Text_Is (Data, Field (Data, Observation_Archive, "entry_point"), "wl_resource_actor_execution_decide_v1")
        or else not Bytes_Shape (Data, actor_input_Archive, D.Raw_Packet'Size / System.Storage_Unit)
        or else not Bytes_Shape (Data, authority_input_Archive, T.Raw_Input'Size / System.Storage_Unit)
        or else not Bytes_Shape (Data, crosswalk_Archive, WX.Raw_Crosswalk'Size / System.Storage_Unit)
        or else not Bytes_Shape (Data, raw_output_Archive, W.Raw_Result'Size / System.Storage_Unit)
        or else not P.Valid_Bytes (Data, actor_arena_Archive)
        or else not P.Valid_Bytes (Data, authority_arena_Archive)
        or else not P.Type_Is (Data, actor_rosters_Archive, "tuple")
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
        or else not P.Type_Is (Data, authority_rosters_Archive, "tuple")
        or else Sequence_Count (Data, authority_rosters_Archive) /= 4
        or else not Roster_Valid (Data, authority_rosters_Archive, 0, "grants", T.Raw_Grant'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, authority_rosters_Archive, 1, "uses", T.Raw_Use'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, authority_rosters_Archive, 2, "receipts", T.C.Raw_Row'Size / System.Storage_Unit)
        or else not Roster_Valid (Data, authority_rosters_Archive, 3, "events", T.C.Raw_Row'Size / System.Storage_Unit)
      then return Result; end if;
      declare
         Raw : constant D.Raw_Packet := RD.Load (P.Bytes_Value (Data, actor_input_Archive));
         Authority : constant T.Raw_Input := RD.Load (P.Bytes_Value (Data, authority_input_Archive));
         Crosswalk : constant WX.Raw_Crosswalk := RD.Load (P.Bytes_Value (Data, crosswalk_Archive));
         Arena : constant Q.Byte_Array := P.Bytes_Value (Data, actor_arena_Archive);
         Authority_Arena : constant Q.Byte_Array := P.Bytes_Value (Data, authority_arena_Archive);
         Copy_history : constant N.Raw_History_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 0)));
         Copy_proposed_history : constant N.Raw_History_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 1)));
         Copy_rows : constant W.Raw_Row_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 2)));
         Copy_proposed_rows : constant W.Raw_Row_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 3)));
         Copy_projection : constant N.Raw_Projection_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 4)));
         Copy_proposed_projection : constant N.Raw_Projection_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 5)));
         Copy_buckets : constant N.Raw_Bucket_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 6)));
         Copy_proposed_buckets : constant N.Raw_Bucket_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 7)));
         Copy_actual_buckets : constant N.Raw_Bucket_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 8)));
         Copy_observed : constant W.Raw_Native_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 9)));
         Copy_facts : constant N.Raw_Facts_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 10)));
         Copy_capabilities : constant D.Raw_Capability_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 11)));
         Copy_groups : constant D.Raw_Group_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 12)));
         Copy_proc_groups : constant D.Raw_Group_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, actor_rosters_Archive, 13)));
         Copy_grants : constant V.Raw_Grant_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, authority_rosters_Archive, 0)));
         Copy_uses : constant V.Raw_Use_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, authority_rosters_Archive, 1)));
         Copy_receipts : constant V.Raw_Chain_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, authority_rosters_Archive, 2)));
         Copy_events : constant V.Raw_Chain_Array := Load_Array (P.Bytes_Value (Data, Roster_Data (Data, authority_rosters_Archive, 3)));
         Native : constant V.Result := V.Execution_Decide
           (Raw, Arena, Copy_history, Copy_proposed_history, Copy_rows,
            Copy_proposed_rows, Copy_projection, Copy_proposed_projection,
            Copy_buckets, Copy_proposed_buckets, Copy_actual_buckets,
            Copy_observed, Copy_facts, Copy_capabilities, Copy_groups,
            Copy_proc_groups, Authority, Authority_Arena, Copy_grants,
            Copy_uses, Copy_receipts, Copy_events, Crosswalk);
      begin
         if not Native.Well_Formed or else Native.Status > X.Status'Pos (X.Status'Last) then return Result; end if;
         Result.Native_Status := X.Status'Val (Native.Status);
         Result.Action := A.Operation'Val (Authority.Bound.Action);
         Result.Id := T.Decode (Authority.Bound).Id;
         -- The output and human label are compared only after complete native
         -- redecision; neither can grant replay or rescue malformed operands.
         Result.State := R.Output_Conflict;
         declare
            Output : constant W.Raw_Result := RD.Load (P.Bytes_Value (Data, raw_output_Archive));
         begin
            if Output.Status = Native.Status
              and then Text_Is (Data, Field (Data, Observation_Archive, "status"), X.Status'Image (Result.Native_Status))
              and then Transport_Zero (Data, Field (Data, Observation_Archive, "transport_status"))
            then Result.State := R.Native_Redecided; end if;
         end;
      end;
      return Result;
   end Reestablish_Actor_Observation;
   function Stored_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return P.Valid_Bytes (Data, Item) or else Hex_Valid (Data, Item)
        or else (OA.Valid (Data, Item) and then View.Form = E.Bytes_Value
                 and then E.Bytes_Valid (Data, View.Payload));
   end Stored_Valid;
   function Stored (Data : E.Bytes; Item : E.Span) return E.Bytes
     with Global => null, Pre => Stored_Valid (Data, Item)
   is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if P.Valid_Bytes (Data, Item) then return P.Bytes_Value (Data, Item);
      elsif Hex_Valid (Data, Item) then return Hex_Bytes (Data, Item);
      else return E.Materialize (Data, View.Payload); end if;
   end Stored;
   function Same (Left_Data : E.Bytes; Left : E.Span;
                  Right_Data : E.Bytes; Right : E.Span) return Boolean is
   begin
      return OA.Valid (Left_Data, Left) and then OA.Valid (Right_Data, Right)
        and then Left.Length = Right.Length
        and then E.Materialize (Left_Data, (Left, 0)) =
                 E.Materialize (Right_Data, (Right, 0));
   end Same;
   function Same_Text (Left_Data : E.Bytes; Left : E.Span;
                       Right_Data : E.Bytes; Right : E.Span) return Boolean is
   begin
      return Left.Length > 0 and then Right.Length > 0
        and then Text_Bytes (Left_Data, Left) = Text_Bytes (Right_Data, Right);
   end Same_Text;
   function Same_Stored (Left_Data : E.Bytes; Left : E.Span;
                         Right_Data : E.Bytes; Right : E.Span) return Boolean is
   begin
      return Stored_Valid (Left_Data, Left) and then Stored_Valid (Right_Data, Right)
        and then Stored (Left_Data, Left) = Stored (Right_Data, Right);
   end Same_Stored;
   function Object_Count (Data : E.Bytes; Item : E.Span) return E.Count is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if SA.Valid (Data, Item) then return SA.Member_Count (Data, Item);
      elsif OA.Valid (Data, Item) and then View.Form = E.Object_Value then
         return E.Array_Length (Data, View.Children);
      else return 0; end if;
   end Object_Count;
   function Present (Data : E.Bytes; Item : E.Span; Names : String) return Boolean is
      First : Positive := Names'First;
   begin
      for I in Names'Range loop
         if Names (I) = ',' then
            if Field (Data, Item, Names (First .. I - 1)).Length = 0 then return False; end if;
            First := I + 1;
         end if;
      end loop;
      return First <= Names'Last and then Field (Data, Item, Names (First .. Names'Last)).Length > 0;
   end Present;
   function Immutable_Source_Matches
     (Frame_Data : E.Bytes; Native : E.Span; Data : E.Bytes; Context : E.Span)
      return Boolean is
      Current_Item : constant E.Span := Field (Data, Context, "native_context");
   begin
      if not Stored_Valid (Data, Current_Item) then return False; end if;
      declare
         Current : constant E.Bytes := Stored (Data, Current_Item);
         Whole : constant E.Span := (Current'First, Current'Length);
      begin
         -- Historical mapping addresses/epochs are preserved; restart changes
         -- neither original selected binary nor original selected build bytes.
         return Same (Frame_Data, Field (Frame_Data, Native, "library_bytes"),
                      Current, Field (Current, Whole, "library_bytes"))
           and then Same (Frame_Data, Field (Frame_Data, Native, "build_bytes"),
                          Current, Field (Current, Whole, "build_bytes"))
           and then Same (Frame_Data, Field (Frame_Data, Native, "library_path"),
                          Current, Field (Current, Whole, "library_path"));
      end;
   end Immutable_Source_Matches;
   function History_Prefix (Frame_Data : E.Bytes; History : E.Span;
                            Data : E.Bytes; Context : E.Span) return Boolean is
      Actual_Item : constant E.Span := Field (Data, Context, "resource_ack_history_raw");
   begin
      if not Stored_Valid (Data, Actual_Item) or else not OA.Valid (Frame_Data, History) then return False; end if;
      declare
         Actual : constant E.Bytes := Stored (Data, Actual_Item);
         Whole : constant E.Span := (Actual'First, Actual'Length);
         Count : constant E.Count := Sequence_Count (Frame_Data, History);
      begin
         if not OA.Valid (Actual, Whole) or else Count > Sequence_Count (Actual, Whole) then return False; end if;
         if Count > 0 then
            for I in E.Count range 0 .. Count - 1 loop
               if not Same (Frame_Data, Element (Frame_Data, History, I),
                            Actual, Element (Actual, Whole, I)) then return False; end if;
            end loop;
         end if;
         return True;
      end;
   end History_Prefix;
   function Digest_Matches (Data : E.Bytes; Item : E.Span; Source : E.Bytes; Encoded : E.Span)
      return Boolean is
   begin
      if not Hex_Valid (Data, Item) or else not OA.Valid (Source, Encoded) then return False; end if;
      declare
         Expected : constant E.Bytes := Hex_Bytes (Data, Item);
         Sum : constant G.SHA.Digest := G.Hash (Source, Encoded);
      begin
         return Expected'Length = Sum'Length and then
           (for all I in Expected'Range => Expected (I) = Sum (Sum'First + Integer (I - Expected'First)));
      end;
   end Digest_Matches;
   function Byte_Id_Matches (Data : E.Bytes; Item : E.Span; Source : E.Bytes; Value : E.Span)
      return Boolean is
   begin
      return Hex_Valid (Data, Item) and then Stored_Valid (Source, Value)
        and then Hex_Bytes (Data, Item) = Stored (Source, Value);
   end Byte_Id_Matches;
   function Quantity_Matches (Data : E.Bytes; Quantity : E.Span; Source : E.Bytes; Integer_Item : E.Span)
      return Boolean is
      Raw : constant E.Span := Field (Data, Quantity, "raw");
      View : constant E.View := E.Decode (Source, Integer_Item, E.Operation);
      Negative : constant E.View := E.Decode (Data, Field (Data, Quantity, "negative"), E.Operation);
   begin
      return Object_Count (Data, Quantity) = 2 and then Negative.Form = E.Boolean_Value
        and then not Negative.Boolean_Bit and then Hex_Valid (Data, Raw)
        and then OA.Valid (Source, Integer_Item) and then View.Form = E.Integer_Value
        and then not View.Sign and then E.Bytes_Valid (Source, View.Payload)
        and then Hex_Bytes (Data, Raw) = E.Materialize (Source, View.Payload);
   end Quantity_Matches;
   function Observation_Equals (Left : E.Bytes; L : E.Span; Right : E.Bytes; R_Item : E.Span)
      return Boolean is
      L_Rosters : constant E.Span := Field (Left, L, "rosters");
      R_Rosters : constant E.Span := Field (Right, R_Item, "rosters");
      Count : constant E.Count := Sequence_Count (Left, L_Rosters);
   begin
      if Object_Count (Left, L) /= 5 or else Object_Count (Right, R_Item) /= 5
        or else not Same_Text (Left, Field (Left, L, "decision"), Right, Field (Right, R_Item, "decision"))
        or else not Same_Text (Left, Field (Left, L, "input"), Right, Field (Right, R_Item, "input"))
        or else not Same_Text (Left, Field (Left, L, "arena"), Right, Field (Right, R_Item, "arena"))
        or else not Same_Text (Left, Field (Left, L, "output"), Right, Field (Right, R_Item, "output"))
        or else Count /= Sequence_Count (Right, R_Rosters) then return False; end if;
      if Count > 0 then
         for I in E.Count range 0 .. Count - 1 loop
            if not Same_Text (Left, Element (Left, L_Rosters, I), Right, Element (Right, R_Rosters, I)) then return False; end if;
         end loop;
      end if;
      return True;
   end Observation_Equals;
   function Followup_Current_Matches (Full : E.Bytes; Whole : E.Span; Snap_Data : E.Bytes; Fresh : E.Span;
                                      Data : E.Bytes; Event : E.Span) return Boolean is
      Id : constant E.Span := Field (Snap_Data, Fresh, "id");
      View : constant E.View := E.Decode (Full, Whole, E.Operation);
      Last : constant E.Span := E.Array_Element (Full, View.Children, 16);
      Effect : constant E.Span := Field (Full, Whole, "original_effect_native");
      Rows : constant E.Span := Field (Full, Whole, "full_current_rows");
      Universe : constant E.Span := Field (Full, Whole, "current_universe");
      Scoped : constant Boolean := P.Type_Is (Full, Field (Full, Rows, "state"), "ScopedState");
   begin
      if Object_Count (Full, Whole) /= 17 or else Last.Length = 0 or else Last.First <= Full'First
        or else Full (Last.First - 1) /= Character'Pos (',')
        or else Field (Full, Whole, "full_current_rows").First < Last.First
        or else Object_Count (Full, Rows) /= (if Scoped then 5 else 2)
        or else not Present (Full, Rows, (if Scoped then "state,history,rows,projection,buckets" else "state,rows"))
        or else not Same_Text (Full, Field (Full, Effect, "command"), Data, Field (Data, Field (Data, Event, "native"), "command"))
        or else not Observation_Equals (Full, Field (Full, Effect, "observation"), Data, Field (Data, Field (Data, Event, "native"), "observation"))
        or else not Byte_Id_Matches (Snap_Data, Field (Snap_Data, Id, "universe_head"), Full, Field (Full, Whole, "current_universe_head"))
        or else not Byte_Id_Matches (Snap_Data, Field (Snap_Data, Id, "resource_head"), Full, Field (Full, Whole, "current_resource_head"))
        or else not Byte_Id_Matches (Snap_Data, Field (Snap_Data, Id, "policy"), Full, Field (Full, Field (Full, Field (Full, Whole, "current_scope"), "policy"), "bytes"))
        or else not Same (Snap_Data, Field (Snap_Data, Id, "issuer_head"), Full, Field (Full, Field (Full, Whole, "current_issuer"), "event_head"))
        or else not Quantity_Matches (Snap_Data, Field (Snap_Data, Fresh, "resource_epoch"), Full, Field (Full, Whole, "current_resource_epoch"))
        or else not Quantity_Matches (Snap_Data, Field (Snap_Data, Fresh, "policy_epoch"), Full, Field (Full, Field (Full, Universe, "record"), "policy_epoch"))
        or else not Digest_Matches (Snap_Data, Field (Snap_Data, Id, "kernel_mapping"), Full, Field (Full, Whole, "current_kernel"))
      then return False; end if;
      declare
         -- Original producer appends full_current_rows last and excludes exactly
         -- that pair from input_snapshot. Keep the original wrapper/float bits,
         -- insertion order and every preceding complete field unchanged.
         Filtered : constant E.Bytes := Full (Full'First .. Last.First - 2) &
           Full (Last.First + Last.Length .. Full'Last);
      begin
         return Digest_Matches (Snap_Data, Field (Snap_Data, Id, "input_snapshot"),
                                Filtered, (Filtered'First, Filtered'Length));
      end;
   end Followup_Current_Matches;
   function Null_Is (Data : E.Bytes; Item : E.Span) return Boolean is
     (P.Is_Null (Data, Item) or else
      (OA.Valid (Data, Item) and then E.Decode (Data, Item, E.Operation).Form = E.Null_Value));
   function Typed_Bytes (Data : E.Bytes; Item : E.Span) return Boolean is
     (P.Valid_Bytes (Data, Item) or else (OA.Valid (Data, Item)
      and then E.Decode (Data, Item, E.Operation).Form = E.Bytes_Value
      and then E.Bytes_Valid (Data, E.Decode (Data, Item, E.Operation).Payload)));
   function Binding_Record (Data : E.Bytes; Item : E.Span) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
      Name : constant String := "RunBinding";
   begin
      if P.Type_Is (Data, Item, Name) then return True; end if;
      if not OA.Valid (Data, Item) or else View.Form /= E.Record_Value
        or else E.Array_Length (Data, View.Children) /= 10 or else not E.Bytes_Valid (Data, View.Record_Name)
      then return False; end if;
      declare
         Bytes : constant E.Bytes := E.Materialize (Data, View.Record_Name);
      begin
         return Bytes'Length = Name'Length and then
           (for all I in Name'Range => Bytes (Bytes'First + E.Count (I - Name'First)) = Character'Pos (Name (I)));
      end;
   end Binding_Record;
   function History_Replay_Item (Data : E.Bytes; Context : E.Span; Ordinal : E.Count) return E.Span is
      Profile : constant E.Span := Field (Data, Context, "resource_ack_history");
      Archives : constant E.Span := Field (Data, Profile, "replay_archives");
   begin
      return Element (Data, Archives, Ordinal);
   end History_Replay_Item;
   function Snapshot_Matches (Full : E.Bytes; Snapshot, History : E.Span;
                              Data : E.Bytes; Context : E.Span) return Boolean is
      Count : constant E.Count := Sequence_Count (Full, History);
   begin
      if Count = 0 or else not P.Type_Is (Full, Snapshot, "dict") or else SA.Member_Count (Full, Snapshot) /= 5 then return False; end if;
      declare
         Replay_Item : constant E.Span := History_Replay_Item (Data, Context, Count - 1);
      begin
         if not Stored_Valid (Data, Replay_Item) then return False; end if;
         declare
            Replay_Data : constant E.Bytes := Stored (Data, Replay_Item);
            Whole : constant E.Span := (Replay_Data'First, Replay_Data'Length);
            Packet : constant E.Span := Field (Replay_Data, Whole, "packet");
         begin
            return Same (Full, Field (Full, Snapshot, "state"), Replay_Data, Field (Replay_Data, Packet, "proposed"))
              and then Same (Full, Field (Full, Snapshot, "history"), Replay_Data, Field (Replay_Data, Packet, "proposed_history"))
              and then Same (Full, Field (Full, Snapshot, "rows"), Replay_Data, Field (Replay_Data, Packet, "proposed_rows"))
              and then Same (Full, Field (Full, Snapshot, "projection"), Replay_Data, Field (Replay_Data, Packet, "proposed_projection"))
              and then Same (Full, Field (Full, Snapshot, "buckets"), Replay_Data, Field (Replay_Data, Packet, "proposed_buckets"));
         end;
      end;
   end Snapshot_Matches;
   function Atomic_Matches (Left : E.Bytes; L : E.Span; Right : E.Bytes; R_Item : E.Span)
      return Boolean is
      LV : constant E.View := E.Decode (Left, L, E.Operation);
      RV : constant E.View := E.Decode (Right, R_Item, E.Operation);
   begin
      if Null_Is (Left, L) or else Null_Is (Right, R_Item) then
         return Null_Is (Left, L) and then Null_Is (Right, R_Item);
      elsif Typed_Bytes (Left, L) and then Typed_Bytes (Right, R_Item) then
         return Stored (Left, L) = Stored (Right, R_Item);
      elsif P.Is_Integer (Left, L) and then OA.Valid (Right, R_Item) and then RV.Form = E.Integer_Value then
         return E.Bytes_Valid (Right, RV.Payload) and then P.Negative (Left, L) = RV.Sign
           and then P.Magnitude_Value (Left, L) = E.Materialize (Right, RV.Payload);
      elsif OA.Valid (Left, L) and then LV.Form = E.Integer_Value and then P.Is_Integer (Right, R_Item) then
         return E.Bytes_Valid (Left, LV.Payload) and then LV.Sign = P.Negative (Right, R_Item)
           and then E.Materialize (Left, LV.Payload) = P.Magnitude_Value (Right, R_Item);
      else return Same (Left, L, Right, R_Item); end if;
   end Atomic_Matches;
   function Bound_Matches (Left : E.Bytes; L : E.Span; Right : E.Bytes; R_Item : E.Span) return Boolean is
      Names : constant String := "reservation,operation,owner,workload,universe_head,capability,grant_use,payload,provenance,resource_epoch";
      First : Positive := Names'First;
   begin
      if not Binding_Record (Left, L) or else not Binding_Record (Right, R_Item) then return False; end if;
      for I in Names'Range loop
         if Names (I) = ',' then
            if not Atomic_Matches (Left, Field (Left, L, Names (First .. I - 1)),
                                   Right, Field (Right, R_Item, Names (First .. I - 1))) then return False; end if;
            First := I + 1;
         end if;
      end loop;
      return Atomic_Matches (Left, Field (Left, L, Names (First .. Names'Last)),
                              Right, Field (Right, R_Item, Names (First .. Names'Last)));
   end Bound_Matches;
   function Actor_Current_Matches (Full : E.Bytes; Whole : E.Span;
                                  Data : E.Bytes; Context : E.Span) return Boolean is
      History : constant E.Span := Field (Full, Whole, "complete_scoped_history");
      Selected : constant E.Span := Field (Full, Whole, "selected_scoped_history");
      Snapshot : constant E.Span := Field (Full, Whole, "complete_snapshot");
      State : constant E.Span := Field (Full, Snapshot, "state");
      Current : constant E.Span := Field (Full, Whole, "current_observation");
      Crosswalk : constant E.Span := Field (Full, Whole, "execution_crosswalk");
      Owner_Raw : constant E.Span := Field (Data, Context, "owner_genesis_raw");
      Original_Item : constant E.Span := Field (Full, Whole, "original_capture");
      Selected_Count : E.Count := 0;
      Running_Count : E.Count := 0;
   begin
      if not Same (Full, Field (Full, State, "current"), Full, Field (Full, Current, "scope"))
        or else not Same (Full, Field (Full, State, "resource_epoch"), Full, Field (Full, Current, "resource_epoch"))
        or else not Same (Full, Field (Full, State, "ledger_head"), Full, Field (Full, Current, "ledger_head"))
        or else not Same (Full, Field (Full, Crosswalk, "resource_current"), Full, Current)
        or else not Same (Full, Field (Full, Crosswalk, "resource_source"), Full, Field (Full, Whole, "current_source"))
        or else not Same (Full, Field (Full, Crosswalk, "original_request"), Full, Field (Full, Whole, "original_request"))
        or else not Text_Is (Full, Field (Full, Crosswalk, "schema"), "worldline.protected-operation-resource-crosswalk-v1")
        or else not Snapshot_Matches (Full, Snapshot, History, Data, Context)
        or else not Stored_Valid (Data, Owner_Raw) or else not Stored_Valid (Full, Original_Item)
      then return False; end if;
      declare
         Owner : constant E.Bytes := Stored (Data, Owner_Raw);
         Original : constant E.Bytes := Stored (Full, Original_Item);
         Capture : constant E.Span := (Original'First, Original'Length);
         Bound : constant E.Span := Field (Original, Field (Original, Capture, "resource_intent"), "bound");
      begin
         if not Same (Full, Field (Full, Crosswalk, "owner_genesis"), Owner, (Owner'First, Owner'Length))
           or else not Same (Full, Field (Full, Crosswalk, "transaction"), Original, Field (Original, Capture, "transaction"))
           or else not Atomic_Matches (Full, Field (Full, Whole, "reservation"), Original, Field (Original, Field (Original, Capture, "resource_intent"), "reservation"))
         then return False; end if;
         if Sequence_Count (Full, History) > 0 then
            for I in E.Count range 0 .. Sequence_Count (Full, History) - 1 loop
               declare
                  Event : constant E.Span := Element (Full, History, I);
                  Replay_Item : constant E.Span := History_Replay_Item (Data, Context, I);
               begin
                  if not Stored_Valid (Data, Replay_Item) then return False; end if;
                  declare
                     Replay_Data : constant E.Bytes := Stored (Data, Replay_Item);
                     Whole_Replay : constant E.Span := (Replay_Data'First, Replay_Data'Length);
                     Packet : constant E.Span := Field (Replay_Data, Whole_Replay, "packet");
                     Native : constant E.Span := Field (Replay_Data, Whole_Replay, "native");
                     Request : constant E.Span := Field (Replay_Data, Field (Replay_Data, Packet, "request"), "original");
                     Replay : constant R.Scoped_Replay_Result := R.Reestablish_Scoped_Observation (Replay_Data, Native);
                  begin
                     if Replay.State /= R.Native_Redecided or else Replay.Native_Status /= 0
                       or else not R.Scoped_Material_Matches (Replay_Data, Native, Packet) then return False; end if;
                     if Byte_Id_Matches (Full, Field (Full, Whole, "operation"), Replay_Data, Field (Replay_Data, Request, "operation_id"))
                       and then Atomic_Matches (Full, Field (Full, Whole, "reservation"), Replay_Data, Field (Replay_Data, Request, "reservation"))
                     then
                        if Selected_Count >= Sequence_Count (Full, Selected)
                          or else not Same (Full, Event, Full, Element (Full, Selected, Selected_Count))
                          or else not Bound_Matches (Replay_Data, Field (Replay_Data, Request, "bound"), Original, Bound)
                        then return False; end if;
                        Selected_Count := Selected_Count + 1;
                        if Text_Is (Replay_Data, Field (Replay_Data, Request, "kind"), "RECORD_RUNNING") then
                           if not Same (Full, Event, Full, Field (Full, Whole, "running_event")) then return False; end if;
                           Running_Count := Running_Count + 1;
                        end if;
                     end if;
                  end;
               end;
            end loop;
         end if;
         return Selected_Count = Sequence_Count (Full, Selected) and then Running_Count = 1;
      end;
   end Actor_Current_Matches;
   function Digest_Bytes_Matches (Data : E.Bytes; Item : E.Span; Source : E.Bytes; Encoded : E.Span)
      return Boolean is
   begin
      if not Stored_Valid (Data, Item) or else not OA.Valid (Source, Encoded) then return False; end if;
      declare
         Expected : constant E.Bytes := Stored (Data, Item);
         Sum : constant G.SHA.Digest := G.Hash (Source, Encoded);
      begin
         return Expected'Length = Sum'Length and then
           (for all I in Expected'Range => Expected (I) = Sum (Sum'First + Integer (I - Expected'First)));
      end;
   end Digest_Bytes_Matches;
   function Broker_Facts_Matches (Data : E.Bytes; Facts, Args : E.Span) return Boolean is
      Material : constant E.Span := Element (Data, Args, 7);
      Worker : constant E.Span := Field (Data, Material, "worker_native");
      Canonical : constant E.Span := Field (Data, Material, "canonical_native");
      Worker_Facts : constant E.Span := Field (Data, Facts, "worker");
      Canonical_Facts : constant E.Span := Field (Data, Facts, "canonical");
      Root_Item : constant E.Span := Field (Data, Canonical_Facts, "root_set");
      Root_Text : constant E.Bytes := Text_Bytes (Data, Root_Item);
      Expected_Root : constant E.Span := Field (Data, Canonical, "live_root");
   begin
      -- Each native observed mapping binds the actual complete observation,
      -- not the archived permission/status or a caller's projected root flag.
      if not Digest_Bytes_Matches (Data, Field (Data, Worker, "live_mapping"), Data,
                             Field (Data, Field (Data, Worker_Facts, "mapping"), "target"))
        or else not Atomic_Matches (Data, Field (Data, Worker, "live_root"), Data, Field (Data, Worker_Facts, "root"))
        or else not Digest_Bytes_Matches (Data, Field (Data, Canonical, "live_mapping"), Data, Field (Data, Canonical_Facts, "mapping"))
        or else not Stored_Valid (Data, Expected_Root)
      then return False; end if;
      declare
         Bytes : constant E.Bytes := Stored (Data, Expected_Root);
         Hex_Digits : constant String := "0123456789abcdef";
         Prefix : constant String := "sha256:";
      begin
         if Root_Text'Length /= Prefix'Length + Bytes'Length * 2 then return False; end if;
         for I in Prefix'Range loop
            if Root_Text (Root_Text'First + E.Count (I - Prefix'First)) /= Character'Pos (Prefix (I)) then return False; end if;
         end loop;
         for I in Bytes'Range loop
            if Root_Text (Root_Text'First + Prefix'Length + (I - Bytes'First) * 2) /= Character'Pos (Hex_Digits (Integer (Bytes (I) / 16) + 1))
              or else Root_Text (Root_Text'First + Prefix'Length + (I - Bytes'First) * 2 + 1) /= Character'Pos (Hex_Digits (Integer (Bytes (I) mod 16) + 1))
            then return False; end if;
         end loop;
         return True;
      end;
   end Broker_Facts_Matches;
   function Resource_Rows_Matches (Full : E.Bytes; Whole : E.Span;
                                   Data : E.Bytes; Context : E.Span) return Boolean is
      Rows : constant E.Span := Field (Full, Whole, "full_current_rows");
      State : constant E.Span := Field (Full, Rows, "state");
      Row_Set : constant E.Span := Field (Full, Rows, "rows");
      Profile : E.Span := Field (Data, Context, "resource_ack_history");
   begin
      if P.Type_Is (Full, State, "ScopedState") then
         declare
            Archives : constant E.Span := Field (Data, Profile, "replay_archives");
            Count : constant E.Count := Sequence_Count (Data, Archives);
         begin
            if Count > 0 then
               for I in E.Count range 0 .. Count - 1 loop
                  declare
                     Replay_Item : constant E.Span := Element (Data, Archives, I);
                  begin
                     if not Stored_Valid (Data, Replay_Item) then return False; end if;
                     declare
                        Replay_Data : constant E.Bytes := Stored (Data, Replay_Item);
                        Whole_Replay : constant E.Span := (Replay_Data'First, Replay_Data'Length);
                        Packet : constant E.Span := Field (Replay_Data, Whole_Replay, "packet");
                     begin
                        if Same (Full, State, Replay_Data, Field (Replay_Data, Packet, "proposed"))
                          and then Same (Full, Row_Set, Replay_Data, Field (Replay_Data, Packet, "proposed_rows"))
                          and then Same (Full, Field (Full, Rows, "history"), Replay_Data, Field (Replay_Data, Packet, "proposed_history"))
                          and then Same (Full, Field (Full, Rows, "projection"), Replay_Data, Field (Replay_Data, Packet, "proposed_projection"))
                          and then Same (Full, Field (Full, Rows, "buckets"), Replay_Data, Field (Replay_Data, Packet, "proposed_buckets"))
                        then return True; end if;
                     end;
                  end;
               end loop;
            end if;
            return False;
         end;
      end if;
      if Field (Data, Profile, "original").Length > 0 then Profile := Field (Data, Profile, "original"); end if;
      declare
         Events : constant E.Span := Field (Data, Profile, "events");
         Count : constant E.Count := Sequence_Count (Data, Events);
      begin
         if Count > 0 then
            for I in E.Count range 0 .. Count - 1 loop
               declare
                  Row : constant E.Span := Element (Data, Events, I);
                  Raw_Item : constant E.Span := Element (Data, Row, 2);
               begin
                  if Sequence_Count (Data, Row) /= 3 or else not P.Valid_Bytes (Data, Raw_Item) then return False; end if;
                  declare
                     Raw : constant E.Bytes := P.Bytes_Value (Data, Raw_Item);
                     All_Raw : constant E.Span := (Raw'First, Raw'Length);
                     Proposed : constant E.C.Member := E.C.Field (Raw, All_Raw, "proposed");
                     Proposed_Rows : constant E.C.Member := E.C.Field (Raw, All_Raw, "proposed_rows");
                  begin
                     if Proposed.Found and then Proposed_Rows.Found
                       and then E.C.Operation_Archive_JSON_Matches (Raw, Full,
                         E.C.Part (All_Raw, Proposed.Value.First, Proposed.Value.After), State)
                       and then E.C.Operation_Archive_JSON_Matches (Raw, Full,
                         E.C.Part (All_Raw, Proposed_Rows.Value.First, Proposed_Rows.Value.After), Row_Set)
                     then return True; end if;
                  end;
               end;
            end loop;
         end if;
         return False;
      end;
   end Resource_Rows_Matches;
   function Frame_Matches_Raw (Source : E.Bytes; Item : E.Span; Data : E.Bytes; Raw_Item : E.Span) return Boolean is
   begin
      if not Stored_Valid (Data, Raw_Item) then return False; end if;
      declare
         Raw : constant E.Bytes := Stored (Data, Raw_Item);
      begin
         return Same (Source, Item, Raw, (Raw'First, Raw'Length));
      end;
   end Frame_Matches_Raw;
   function Crosswalk_Source_Matches (Full : E.Bytes; Crosswalk, Whole : E.Span;
                                     Snapshot : E.Bytes; Snap : E.Span;
                                     Data : E.Bytes; Context : E.Span) return Boolean is
      Grants : constant E.Span := Field (Snapshot, Snap, "grants");
      Fresh : constant E.Span := Field (Snapshot, Field (Snapshot, Snap, "evidence"), "owner_resolution");
      Grant_Id : constant E.Span := Field (Snapshot, Field (Snapshot, Fresh, "id"), "grant_id");
      Current : constant E.Span := Field (Full, Whole, "current_observation");
      Matches : E.Count := 0;
   begin
      if not Frame_Matches_Raw (Full, Field (Full, Crosswalk, "installation"), Data, Field (Data, Context, "installation_raw"))
        or else not Same_Stored (Full, Field (Full, Crosswalk, "gate_config_raw"), Data, Field (Data, Context, "gate_config_raw"))
        or else not Frame_Matches_Raw (Full, Field (Full, Crosswalk, "gate_managed_observation"), Data, Field (Data, Context, "gate_managed_observation_raw"))
        or else not Byte_Id_Matches (Full, Field (Full, Crosswalk, "resource_policy"), Full, Field (Full, Field (Full, Current, "scope"), "policy"))
        or else not Byte_Id_Matches (Full, Field (Full, Crosswalk, "root_head"), Full, Field (Full, Current, "root_head"))
      then return False; end if;
      if Sequence_Count (Snapshot, Grants) > 0 then
         for I in E.Count range 0 .. Sequence_Count (Snapshot, Grants) - 1 loop
            declare
               Grant : constant E.Span := Element (Snapshot, Grants, I);
            begin
               if Same (Snapshot, Field (Snapshot, Grant, "id"), Snapshot, Grant_Id) then
                  if not Same (Full, Field (Full, Crosswalk, "operation_grant"), Snapshot, Grant)
                    or else not Same (Full, Field (Full, Crosswalk, "operation_policy"), Snapshot, Field (Snapshot, Grant, "policy"))
                  then return False; end if;
                  Matches := Matches + 1;
               end if;
            end;
         end loop;
      end if;
      return Matches = 1;
   end Crosswalk_Source_Matches;
   function Operation_Boundary_Matches
     (Data : E.Bytes; Material, Event, Context : E.Span; Kind : Boundary_Kind)
      return Boolean
   is
      Native : constant E.Span := Field (Data, Material, "native");
      Snapshot : constant E.Span := Field (Data, Material, "snapshot");
      Full_Item : constant E.Span := Field (Data, Material, "full_current");
   begin
      if Kind = Full_Broker then
         if not Stored_Valid (Data, Material) then return False; end if;
         declare
            Broker : constant E.Bytes := Stored (Data, Material);
            Whole : constant E.Span := (Broker'First, Broker'Length);
            Args : constant E.Span := Field (Broker, Whole, "arguments");
            Observation : constant E.Span := Field (Broker, Whole, "native");
            Facts : constant E.Span := Field (Broker, Whole, "facts");
            Exchange : constant R.Exchange_Replay_Result := R.Reestablish_Exchange_Observation (Broker, Observation);
            Original_Item : constant E.Span := Field (Data, Event, "capture");
         begin
            if Object_Count (Broker, Whole) /= 5
              or else not Present (Broker, Whole, "phase,mode,arguments,facts,native")
              or else Sequence_Count (Broker, Args) /= 12
              or else Exchange.State /= R.Native_Redecided
              or else not R.Exchange_Material_Matches (Broker, Observation, Args)
              or else not Broker_Facts_Matches (Broker, Facts, Args)
              or else not Same (Broker, Field (Broker, Whole, "phase"), Broker, Element (Broker, Args, 8))
              or else not Same (Broker, Field (Broker, Whole, "mode"), Broker, Element (Broker, Args, 9))
              or else Object_Count (Broker, Facts) /= 3
              or else not Present (Broker, Facts, "worker,canonical,worldline_chains")
              or else not Stored_Valid (Data, Original_Item)
            then return False; end if;
            declare
               Original : constant E.Bytes := Stored (Data, Original_Item);
               Capture : constant E.Span := (Original'First, Original'Length);
               Snap : constant E.Span := Element (Broker, Args, 0);
            begin
               return Same (Broker, Field (Broker, Snap, "binding"), Original, Field (Original, Capture, "binding"))
                 and then Same_Text (Data, Field (Data, Event, "operation"),
                                    Broker, Field (Broker, Field (Broker, Field (Broker, Snap, "binding"), "id"), "operation_id"))
                 and then Same (Broker, Element (Broker, Args, 5), Original,
                                Field (Original, Field (Original, Field (Original, Capture, "request"), "peer"), "uid"))
                 and then Immutable_Source_Matches (Original, Field (Original, Capture, "native"), Data, Context);
            end;
         end;
      end if;
      if Object_Count (Data, Material) /= 6
        or else not Present (Data, Material, "schema,operation,full_current,snapshot,native")
        or else not Stored_Valid (Data, Snapshot) or else not Stored_Valid (Data, Full_Item)
        or else not Same_Text (Data, Field (Data, Material, "operation"), Data, Field (Data, Event, "operation"))
      then return False; end if;
      declare
         Full : constant E.Bytes := Stored (Data, Full_Item);
         Whole : constant E.Span := (Full'First, Full'Length);
         Snap_Data : constant E.Bytes := Stored (Data, Snapshot);
         Snap : constant E.Span := (Snap_Data'First, Snap_Data'Length);
         Fresh : constant E.Span := Field (Snap_Data, Field (Snap_Data, Snap, "evidence"), "owner_resolution");
         Original_Item : constant E.Span := Field (Full, Whole, "original_capture");
         Replay : constant R.Operation_Replay_Result := R.Reestablish_Operation_Observation (Data, Native);
      begin
         if not OA.Valid (Full, Whole) or else not OA.Valid (Snap_Data, Snap)
           or else Replay.State /= R.Native_Redecided
           or else Replay.Roster_Entry /= R.Authority_Entry
           or else Replay.Command /= (if Kind = Followup then A.Authorize_Followup else A.Authorize_Execution)
           or else not R.Operation_Material_Matches (Data, Native, Snapshot)
           or else not Same_Text (Data, Field (Data, Material, "operation"),
                                 Snap_Data, Field (Snap_Data, Field (Snap_Data, Field (Snap_Data, Snap, "binding"), "id"), "operation_id"))
           or else not Same_Stored (Full, Original_Item, Data, Field (Data, Event, "capture"))
         then return False; end if;
         declare
            Original : constant E.Bytes := Stored (Full, Original_Item);
            Capture : constant E.Span := (Original'First, Original'Length);
         begin
            if not Same (Original, Field (Original, Capture, "binding"), Snap_Data, Field (Snap_Data, Snap, "binding"))
              or else not Same (Original, Field (Original, Capture, "request"), Full, Field (Full, Whole, "original_request"))
            then return False; end if;
         end;
         if Kind = Followup then
            return Text_Is (Data, Field (Data, Material, "schema"), "worldline.protected-followup-material-v1")
              and then Object_Count (Full, Whole) = 17
              and then Text_Is (Full, Field (Full, Whole, "schema"), "worldline.protected-followup-current-input-v1")
              and then Present (Full, Whole, "schema,right,original_request,original_capture,original_effect_snapshot,original_effect_native,current_scope,current_resource_epoch,current_universe_head,current_resource_head,current_source,current_universe,current_issuer,current_prime,current_requirement,current_kernel,full_current_rows")
              and then Same_Text (Data, Field (Data, Material, "right"), Full, Field (Full, Whole, "right"))
              and then Same_Text (Full, Field (Full, Whole, "right"), Snap_Data, Field (Snap_Data, Fresh, "action"))
              and then Same_Stored (Full, Field (Full, Whole, "original_effect_snapshot"), Data, Field (Data, Event, "snapshot"))
              and then Followup_Current_Matches (Full, Whole, Snap_Data, Fresh, Data, Event)
              and then Resource_Rows_Matches (Full, Whole, Data, Context)
              and then Immutable_Source_Matches (Full, Field (Full, Whole, "current_kernel"), Data, Context);
         else
            declare
               Crosswalk : constant E.Span := Field (Full, Whole, "execution_crosswalk");
            begin
               return Text_Is (Data, Field (Data, Material, "schema"), "worldline.protected-actor-execution-material-v1")
                 and then Object_Count (Full, Whole) = 19
                 and then Text_Is (Full, Field (Full, Whole, "schema"), "worldline.protected-actor-execution-current-v1")
                 and then Present (Full, Whole, "schema,operation,reservation,original_request,original_capture,current_binding,current_observation,current_source,complete_snapshot,complete_scoped_history,selected_scoped_history,running_event,universe,issuer,prime,requirement,native_mapping,plan,execution_crosswalk")
                 and then Same_Text (Data, Field (Data, Material, "operation"), Full, Field (Full, Whole, "operation"))
                 and then Same_Stored (Data, Field (Data, Material, "reservation"), Full, Field (Full, Whole, "reservation"))
                 and then Same (Snap_Data, Fresh, Full, Field (Full, Whole, "current_binding"))
                 and then Object_Count (Full, Crosswalk) = 16
                 and then Present (Full, Crosswalk, "schema,owner_genesis,installation,gate_config_raw,gate_managed_observation,operation_grant,operation_binding,operation_policy,resource_policy,root_set,root_head,resource_current,resource_source,transaction,original_request,preparer_peer")
                 and then Same (Full, Field (Full, Crosswalk, "operation_binding"), Snap_Data, Fresh)
                 and then Same (Full, Field (Full, Crosswalk, "operation_policy"), Snap_Data, Field (Snap_Data, Field (Snap_Data, Fresh, "id"), "policy"))
                 and then Same (Full, Field (Full, Crosswalk, "root_set"), Snap_Data, Field (Snap_Data, Field (Snap_Data, Fresh, "id"), "root_set"))
                 and then History_Prefix (Full, Field (Full, Whole, "complete_scoped_history"), Data, Context)
                 and then Actor_Current_Matches (Full, Whole, Data, Context)
                 and then Crosswalk_Source_Matches (Full, Crosswalk, Whole, Snap_Data, Snap, Data, Context)
                 and then Immutable_Source_Matches (Full, Field (Full, Whole, "native_mapping"), Data, Context);
            end;
         end if;
      end;
   end Operation_Boundary_Matches;
end Worldline.Actor_Archive_Replay;

with SPARK.Big_Integers;
with Interfaces;
with Worldline.Scoped_Capture_Projection;
with Worldline.Recovery_Archive;

package body Worldline.Scoped_Capture_History_Projection with SPARK_Mode is
   package P renames Worldline.Scoped_Capture_Projection;
   use SPARK.Big_Integers;
   use type E.Count;
   use type E.Span;
   use type E.Bytes;
   use type E.Value_Kind;
   use type E.Q.Byte;
   use type R.Replay_State;
   use type R.Scoped_Entry;
   use type Interfaces.Unsigned_32;
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     renames P.Raw_Source_Field;
   function Element (Data : E.Bytes; Item : E.Span; Index : E.Count) return E.Span
     renames R.Archive_Index;
   function Len (Data : E.Bytes; Item : E.Span) return E.Count renames R.Archive_Length;
   function Text (Data : E.Bytes; Item : E.Span; Value : String) return Boolean
     renames R.Archive_Text_Is;
   function Is_None (Data : E.Bytes; Item : E.Span) return Boolean renames R.Archive_Is_None;
   function Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (Worldline.Recovery_Archive.Ordered_Source_Value_Matches
       (Data, Data, Left, Right, False, False));
   function Field_Same (Data : E.Bytes; Left, Right : E.Span; Name : String) return Boolean is
     (Same (Data, F (Data, Left, Name), F (Data, Right, Name)));
   function Bytes_Is (Data : E.Bytes; Item : E.Span; Value : String) return Boolean is
   begin
      if not R.Archive_Bytes_Valid (Data, Item) then return False; end if;
      declare Raw : constant E.Bytes := R.Archive_Bytes (Data, Item); begin
         return Raw'Length = E.Count (Value'Length) and then
           (for all I in Value'Range => Raw (Raw'First + E.Count (I - Value'First)) = Character'Pos (Value (I)));
      end;
   end Bytes_Is;
   function Wire_Matches (Data : E.Bytes; Original, Decoded : E.Span) return Boolean is
     (R.Archive_Bytes_Valid (Data, Decoded) and then
       (Same (Data, Original, Decoded) or else P.Id_Hex (Data, Decoded, Original)
        or else (Text (Data, Original, "") and then R.Archive_Bytes (Data, Decoded)'Length = 0)));
   function Contains (Data : E.Bytes; Items, Item : E.Span) return Boolean is
   begin
      if not R.Archive_Is_Sequence (Data, Items) then return False; end if;
      if Len (Data, Items) > 0 then
         for I in E.Count range 0 .. Len (Data, Items) - 1 loop
            if Same (Data, Element (Data, Items, I), Item) then return True; end if;
         end loop;
      end if;
      return False;
   end Contains;
   function No_Owner (Data : E.Bytes; Row, Owner : E.Span) return Boolean is
      Owned : constant E.Span := F (Data, Owner, "owned_reservations");
   begin
      if not Text (Data, F (Data, Owner, "schema"), "worldline.scoped-history-owner-source-v1")
        or else not R.Archive_Is_Sequence (Data, Owned)
        or else not R.Archive_Bytes_Valid (Data, F (Data, F (Data, Row, "bound"), "reservation"))
      then return False; end if;
      return not Contains (Data, Owned, F (Data, F (Data, Row, "bound"), "reservation"));
   end No_Owner;
   function Original_Source (Data : E.Bytes; Source : E.Span) return E.Span is
      Wrapped : constant E.Span := F (Data, Source, "retained_original");
   begin
      return (if Wrapped.Length > 0 then Wrapped else Source);
   end Original_Source;
   function Prefix (Data : E.Bytes; Earlier, Later : E.Span) return Boolean is
   begin
      if not R.Archive_Is_Sequence (Data, Earlier) or else not R.Archive_Is_Sequence (Data, Later)
        or else Len (Data, Earlier) > Len (Data, Later) then return False; end if;
      if Len (Data, Earlier) > 0 then
         for I in E.Count range 0 .. Len (Data, Earlier) - 1 loop
            if not Same (Data, Element (Data, Earlier, I), Element (Data, Later, I)) then return False; end if;
         end loop;
      end if;
      return True;
   end Prefix;
   function Preimages_Match (Data : E.Bytes; Events, Images : E.Span) return Boolean is
   begin
      if not R.Archive_Is_Sequence (Data, Events) or else not R.Archive_Is_Sequence (Data, Images)
        or else Len (Data, Events) /= Len (Data, Images) then return False; end if;
      if Len (Data, Events) > 0 then
         for I in E.Count range 0 .. Len (Data, Events) - 1 loop
            declare Image : constant E.Span := Element (Data, Images, I); begin
               if not Same (Data, Element (Data, Events, I), F (Data, Image, "event"))
                 or else not P.JSON_Value_Matches (Data, F (Data, Image, "json"), F (Data, Image, "event"))
               then return False; end if;
            end;
         end loop;
      end if;
      return True;
   end Preimages_Match;
   function Event_With_Cause (Data : E.Bytes; Events : E.Span; Cause : String) return E.Span is
      Result : E.Span := (1, 0);
   begin
      if not R.Archive_Is_Sequence (Data, Events) then return Result; end if;
      if Len (Data, Events) > 0 then
         for I in E.Count range 0 .. Len (Data, Events) - 1 loop
            if Text (Data, F (Data, Element (Data, Events, I), "cause"), Cause) then
               if Result.Length > 0 then return (1, 0); end if;
               Result := Element (Data, Events, I);
            end if;
         end loop;
      end if;
      return Result;
   end Event_With_Cause;
   function Event_Hash (Data : E.Bytes; Event, Images, Id : E.Span) return Boolean is
   begin
      if Len (Data, Images) > 0 then
         for I in E.Count range 0 .. Len (Data, Images) - 1 loop
            declare Image : constant E.Span := Element (Data, Images, I); begin
               if Same (Data, Event, F (Data, Image, "event")) then
                  return P.JSON_Value_Matches (Data, F (Data, Image, "json"), F (Data, Image, "event"))
                    and then P.Hash_Field (Data, F (Data, Image, "json"), Id);
               end if;
            end;
         end loop;
      end if;
      return False;
   end Event_Hash;
   function Selected_Events_Match (Data : E.Bytes; Row, Source, Events : E.Span) return Boolean is
      Selected : constant E.Span := F (Data, Source, "events");
      Next : E.Count := 0;
   begin
      if not R.Archive_Is_Sequence (Data, Selected) or else not R.Archive_Is_Sequence (Data, Events)
        or else not P.Id_Hex (Data, F (Data, F (Data, Row, "bound"), "reservation"), F (Data, Source, "reservation"))
      then return False; end if;
      if Len (Data, Events) > 0 then
         for I in E.Count range 0 .. Len (Data, Events) - 1 loop
            declare Event : constant E.Span := Element (Data, Events, I); begin
               if Same (Data, F (Data, Event, "reservation"), F (Data, Source, "reservation"))
                 and then not Text (Data, F (Data, Event, "cause"), "OBSERVATION")
               then
                  if Next >= Len (Data, Selected) or else not Same (Data, Event, Element (Data, Selected, Next)) then return False; end if;
                  Next := Next + 1;
               end if;
            end;
         end loop;
      end if;
      return Next = Len (Data, Selected);
   end Selected_Events_Match;
   function Text_View (Data : E.Bytes; Item : E.Span) return E.View is
     (E.Decode (Data, Item, E.Operation));
   function Id_Text (Data : E.Bytes; Id, Encoded : E.Span) return Boolean is
      V : constant E.View := Text_View (Data, Encoded);
   begin
      return R.Archive_Bytes_Valid (Data, Id) and then V.Form = E.Text_Value
        and then E.Bytes_Valid (Data, V.Payload) and then R.Archive_Bytes (Data, Id) = E.Materialize (Data, V.Payload);
   end Id_Text;
   function Legacy_Atom (Data : E.Bytes; Raw, Value : E.Span) return Boolean is
   begin
      if Is_None (Data, Raw) or else Is_None (Data, Value) then return Is_None (Data, Raw) and then Is_None (Data, Value); end if;
      if R.Archive_Bytes_Valid (Data, Value) then return P.Id_Hex (Data, Value, F (Data, Raw, "bytes")); end if;
      if R.Archive_Integer_Valid (Data, Value) then
         declare Magnitude : constant E.Bytes := R.Archive_Integer_Magnitude (Data, Value); begin
            if not R.Archive_Boolean_Is (Data, F (Data, Raw, "negative"), R.Archive_Integer_Negative (Data, Value)) then return False; end if;
            if Magnitude'Length = 0 then
               return not R.Archive_Integer_Negative (Data, Value) and then Text (Data, F (Data, Raw, "magnitude"), "");
            end if;
            -- Original dto_record quantities have canonical little-endian bytes.
            if Magnitude (Magnitude'Last) = 0 then return False; end if;
            declare Encoded : constant E.Span := F (Data, Raw, "magnitude");
                    V : constant E.View := Text_View (Data, Encoded); begin
               if V.Form /= E.Text_Value or else not E.Bytes_Valid (Data, V.Payload) then return False; end if;
               declare Hex : constant E.Bytes := E.Materialize (Data, V.Payload); begin
                  if Magnitude'Length > E.Count'Last / 2 or else Hex'Length /= Magnitude'Length * 2 then return False; end if;
                  for I in Magnitude'Range loop
                     declare
                        B : constant Natural := Natural (Magnitude (I));
                        H : constant Natural := B / 16;
                        L : constant Natural := B mod 16;
                        J : constant E.Count := Hex'First + (I - Magnitude'First) * 2;
                     begin
                        if Integer (Hex (J)) /= (if H < 10 then H + 48 else H + 87)
                          or else Integer (Hex (J + 1)) /= (if L < 10 then L + 48 else L + 87) then return False; end if;
                     end;
                  end loop;
                  return True;
               end;
            end;
         end;
      end if;
      return Same (Data, Raw, Value);
   end Legacy_Atom;
   function Legacy_Context (Data : E.Bytes; Raw, Value : E.Span) return Boolean is
   begin
      if not Text (Data, F (Data, Raw, "type"), "RunContext") or else not R.Archive_Record_Is (Data, Value, "RunContext")
        or else not R.Archive_Integer_Valid (Data, F (Data, Raw, "schema_version"))
        or else P.Number (Data, F (Data, Raw, "schema_version")) /= To_Big_Integer (1) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "universe"), F (Data, Value, "universe")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "policy"), F (Data, Value, "policy")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "resource"), F (Data, Value, "resource")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "unit"), F (Data, Value, "unit")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "instance"), F (Data, Value, "instance")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "host"), F (Data, Value, "host")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "boot"), F (Data, Value, "boot")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "authority"), F (Data, Value, "authority")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "policy_epoch"), F (Data, Value, "policy_epoch")) then return False; end if;
      return True;
   end Legacy_Context;
   function Legacy_Binding (Data : E.Bytes; Raw, Value : E.Span) return Boolean is
   begin
      if not Text (Data, F (Data, Raw, "type"), "RunBinding") or else not R.Archive_Record_Is (Data, Value, "RunBinding")
        or else not R.Archive_Integer_Valid (Data, F (Data, Raw, "schema_version"))
        or else P.Number (Data, F (Data, Raw, "schema_version")) /= To_Big_Integer (1) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "reservation"), F (Data, Value, "reservation")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "operation"), F (Data, Value, "operation")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "owner"), F (Data, Value, "owner")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "workload"), F (Data, Value, "workload")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "universe_head"), F (Data, Value, "universe_head")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "capability"), F (Data, Value, "capability")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "grant_use"), F (Data, Value, "grant_use")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "payload"), F (Data, Value, "payload")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "provenance"), F (Data, Value, "provenance")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "resource_epoch"), F (Data, Value, "resource_epoch")) then return False; end if;
      return True;
   end Legacy_Binding;
   function Prepared_Matches (Data : E.Bytes; Row, Prepared, Derivation : E.Span) return Boolean is
      Raw : constant E.Span := F (Data, F (Data, Prepared, "payload"), "row");
      Items : constant E.Span := F (Data, Derivation, "prepared_rows");
      Found : E.Span := (1, 0);
   begin
      if not R.Archive_Is_Sequence (Data, Items) then return False; end if;
      if Len (Data, Items) > 0 then
         for I in E.Count range 0 .. Len (Data, Items) - 1 loop
            if Same (Data, Prepared, F (Data, Element (Data, Items, I), "event")) then
               if Found.Length > 0 then return False; end if;
               Found := F (Data, Element (Data, Items, I), "row");
            end if;
         end loop;
      end if;
      if not R.Archive_Record_Is (Data, Found, "RunRow") or else not Text (Data, F (Data, Raw, "type"), "RunRow")
        or else not Text (Data, F (Data, Found, "state"), "RESERVED")
        or else not Legacy_Context (Data, F (Data, Raw, "scope"), F (Data, Found, "scope"))
        or else not Legacy_Binding (Data, F (Data, Raw, "bound"), F (Data, Found, "bound"))
        or else not Field_Same (Data, Found, Row, "scope") or else not Field_Same (Data, Found, Row, "bound")
      then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "parent"), F (Data, Found, "parent")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "kind"), F (Data, Found, "kind")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "state"), F (Data, Found, "state")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "amount"), F (Data, Found, "amount")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "observed_usage"), F (Data, Found, "observed_usage")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "planned_unit"), F (Data, Found, "planned_unit")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "actual_unit"), F (Data, Found, "actual_unit")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "cgroup"), F (Data, Found, "cgroup")) then return False; end if;
      if not Legacy_Atom (Data, F (Data, Raw, "invocation"), F (Data, Found, "invocation")) then return False; end if;
      return R.Archive_Integer_Valid (Data, F (Data, Raw, "schema_version"))
        and then P.Number (Data, F (Data, Raw, "schema_version")) = To_Big_Integer (1);
   end Prepared_Matches;
   function Line_Number (Raw : E.Bytes; Index : Positive) return E.Span is
      Start : E.Count := Raw'First;
      Current : Positive := 1;
   begin
      for I in Raw'Range loop
         if Raw (I) = 10 then
            if Current = Index then return (Start, I - Start); end if;
            if Current = Positive'Last then return (1, 0); end if;
            Current := Current + 1; Start := I + 1;
         end if;
      end loop;
      return (1, 0);
   end Line_Number;
   function Raw_Text (Raw : E.Bytes; Item : E.Span; Value : String) return Boolean is
     (E.C.P.Valid (Raw, Item) and then Item.Length = E.Count (Value'Length)
       and then (for all I in Value'Range => Raw (Item.First + E.Count (I - Value'First)) = Character'Pos (Value (I))));
   function Raw_Same (A : E.Bytes; Left : E.Span; B : E.Bytes; Right : E.Span) return Boolean is
     (E.C.P.Valid (A, Left) and then E.C.P.Valid (B, Right)
      and then Left.Length = Right.Length
      and then (Left.Length = 0 or else
        (for all I in E.Count range 0 .. Left.Length - 1 =>
          A (Left.First + I) = B (Right.First + I))));
   function Decimal (Raw : E.Bytes; Item : E.Span) return Valid_Big_Integer is
      Value : Big_Integer := To_Big_Integer (0);
   begin
      if not E.C.P.Valid (Raw, Item) or else Item.Length = 0 then return To_Big_Integer (-1); end if;
      if Item.Length > 1 and then Raw (Item.First) = 48 then return To_Big_Integer (-1); end if;
      for I in E.Count range 0 .. Item.Length - 1 loop
         if Raw (Item.First + I) not in 48 .. 57 then return To_Big_Integer (-1); end if;
         Value := Value * To_Big_Integer (10) + To_Big_Integer (Integer (Raw (Item.First + I)) - 48);
      end loop;
      return Value;
   end Decimal;
   function Frame_Matches (Data : E.Bytes; Derivation, Held, Closed : E.Span; Root : Boolean) return Boolean is
   begin
      if not R.Archive_Bytes_Valid (Data, F (Data, Derivation, "closed_frame"))
        or else not R.Archive_Bytes_Valid (Data, F (Data, Derivation, "held_frame"))
        or else not R.Archive_Integer_Valid (Data, F (Data, Held, "init_pid"))
        or else not R.Archive_Integer_Valid (Data, F (Data, Closed, (if Root then "raw_main_wait" else "main_wait_status")))
      then return False; end if;
      declare
         Raw : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Derivation, "closed_frame"));
         Original : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Derivation, "held_frame"));
         Status : constant Big_Integer := Decimal (Raw, Line_Number (Raw, 5));
         Low : constant Big_Integer := Status mod To_Big_Integer (128);
         Lines : E.Count := 0;
         Held_Lines : E.Count := 0;
      begin
         for B of Raw loop if B = 10 then Lines := Lines + 1; end if; end loop;
         for B of Original loop if B = 10 then Held_Lines := Held_Lines + 1; end if; end loop;
         if Raw'Length = 0 or else Original'Length = 0 or else Raw (Raw'Last) /= 10 or else Original (Original'Last) /= 10
           or else Lines /= 6 or else Held_Lines /= 4
           or else not Raw_Text (Raw, Line_Number (Raw, 2), "CLOSED")
           or else not Raw_Text (Raw, Line_Number (Raw, 6), "ECHILD")
           or else not Raw_Text (Original, Line_Number (Original, 2), "HELD")
           or else Decimal (Raw, Line_Number (Raw, 4)) /= P.Number (Data, F (Data, Held, "init_pid"))
           or else Decimal (Original, Line_Number (Original, 4)) /= P.Number (Data, F (Data, Held, "init_pid"))
           or else P.Number (Data, F (Data, Held, "init_pid")) <= To_Big_Integer (0)
           or else Status < To_Big_Integer (0)
           or else Status /= P.Number (Data, F (Data, Closed, (if Root then "raw_main_wait" else "main_wait_status")))
           or else Low = To_Big_Integer (127)
         then return False; end if;
         if not E.C.P.Valid (Raw, Line_Number (Raw, 1)) or else not E.C.P.Valid (Original, Line_Number (Original, 1))
           or else not Raw_Same (Raw, Line_Number (Raw, 1), Original, Line_Number (Original, 1))
           or else not E.C.P.Valid (Raw, Line_Number (Raw, 3)) or else not E.C.P.Valid (Original, Line_Number (Original, 3))
           or else Line_Number (Raw, 3).Length = 0
           or else not Raw_Same (Raw, Line_Number (Raw, 3), Original, Line_Number (Original, 3))
         then return False; end if;
         return (Root and then Raw_Text (Raw, Line_Number (Raw, 1), "WL-ROOT-WORKER-SUPERVISOR-v1"))
           or else (not Root and then (Raw_Text (Raw, Line_Number (Raw, 1), "WL-RESOURCE-SUPERVISOR-v1")
                                     or else Raw_Text (Raw, Line_Number (Raw, 1), "WL-RESOURCE-SUPERVISOR-v3")));
      end;
   end Frame_Matches;
   function Frame_Ticket_Matches (Data : E.Bytes; Derivation, Ticket : E.Span) return Boolean is
      V : constant E.View := Text_View (Data, Ticket);
   begin
      if V.Form /= E.Text_Value or else not E.Bytes_Valid (Data, V.Payload)
        or else not R.Archive_Bytes_Valid (Data, F (Data, Derivation, "closed_frame"))
      then return False; end if;
      declare Raw : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Derivation, "closed_frame"));
              Part : constant E.Span := Line_Number (Raw, 3); begin
         if not E.C.P.Valid (Raw, Part) or else Part.Length = 0 then return False; end if;
         declare
            Ticket_Raw : constant E.Bytes := E.Materialize (Data, V.Payload);
         begin
            return Raw_Same (Raw, Part, Ticket_Raw, (Ticket_Raw'First, Ticket_Raw'Length));
         end;
      end;
   end Frame_Ticket_Matches;
   function Absent_Fields (Data : E.Bytes; Fact : E.Span) return Boolean is
   begin
      if not Is_None (Data, F (Data, Fact, "dispatch")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "actual_unit")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "cgroup")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "invocation")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "namespace")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "held_namespace")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "peer")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "held_peer")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "helper_image")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "expected_helper_image")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "challenge")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "held_challenge")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "protocol")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "closed_event")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "namespace_wait")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "helper_wait")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "cgroup_events")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "cgroup_type")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "manager_delegate")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "cgroup_owner")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "cgroup_group_write")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "cgroup_other_write")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "actual_store_genesis")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "actual_store_id")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "owner_store_genesis")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "owner_store_id")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "genesis_universe")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "genesis_instance")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "genesis_context_head")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "genesis_prime")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "genesis_root_count")) then return False; end if;
      return True;
   end Absent_Fields;
   function Unavailable_Source_Matches
     (Data : E.Bytes; Row, Fact, Source, Owner : E.Span) return Boolean
   is
      Original : constant E.Span := Original_Source (Data, Source);
      Events : constant E.Span := F (Data, Owner, "launch_events");
      Observations : constant E.Span := F (Data, Owner, "observation_events");
      Selected : constant E.Span := F (Data, Original, "events");
      Derivation : constant E.Span := F (Data, Source, "history_derivation");
      Prepared : constant E.Span := Event_With_Cause (Data, Selected, "PREPARED");
      Missing : constant E.Span := F (Data, Original, "historical");
   begin
      if not No_Owner (Data, Row, Owner) or else not R.Archive_Record_Is (Data, Fact, "PhysicalFacts")
        or else not Same (Data, F (Data, Fact, "retained"), F (Data, Row, "bound")) then return False; end if;
      if not Text (Data, F (Data, Derivation, "schema"), "worldline.scoped-history-derivation-v1")
        or else not Absent_Fields (Data, Fact)
        or else not Is_None (Data, F (Data, Original, "kernel"))
        or else not Same (Data, F (Data, Original, "journal_head"), F (Data, Owner, "launch_head"))
        or else not Selected_Events_Match (Data, Row, Original, Events)
        or else not Preimages_Match (Data, Events, F (Data, Derivation, "launch_preimages"))
        or else not P.Id_Hex (Data, F (Data, Fact, "observation_head"), F (Data, Original, "challenge"))
      then return False; end if;
      if Prepared.Length > 0 then
         if not Prepared_Matches (Data, Row, Prepared, Derivation)
           or else not Event_Hash (Data, Prepared, F (Data, Derivation, "launch_preimages"), F (Data, Fact, "intent"))
         then return False; end if;
      elsif not Is_None (Data, F (Data, Fact, "intent")) or else Len (Data, Selected) /= 0 then return False; end if;
      if Text (Data, F (Data, Fact, "phase"), "NEVER_DISPATCHED") then
         if Prepared.Length = 0 then return False; end if;
         -- MACHINE_ADMISSION is retained without changing the launch phase.
         if Len (Data, Selected) > 0 then
            for I in E.Count range 0 .. Len (Data, Selected) - 1 loop
               if not Text (Data, F (Data, Element (Data, Selected, I), "cause"), "PREPARED")
                 and then not Text (Data, F (Data, Element (Data, Selected, I), "cause"), "MACHINE_ADMISSION")
               then return False; end if;
            end loop;
         end if;
         return True;
      end if;
      if not Text (Data, F (Data, Fact, "phase"), "UNAVAILABLE")
        or else not Text (Data, F (Data, Missing, "schema"), "worldline.missing-owned-closed-witness-v1")
        or else not Text (Data, F (Data, Missing, "retained"), "UNKNOWN")
        or else not R.Archive_Is_Sequence (Data, Observations) then return False; end if;
      -- Absence is a full authenticated-prefix search, never the shape of None.
      if Len (Data, Observations) > 0 then
         for I in E.Count range 0 .. Len (Data, Observations) - 1 loop
            declare Event : constant E.Span := Element (Data, Observations, I); begin
               if Text (Data, F (Data, Event, "cause"), "CLOSED_NATIVE_WITNESS")
                 and then Same (Data, F (Data, Event, "reservation"), F (Data, Original, "reservation")) then return False; end if;
            end;
         end loop;
      end if;
      return True;
   end Unavailable_Source_Matches;

   function Physical_Closed_Matches
     (Data : E.Bytes; Row, Fact, Raw, Source, Derivation, Events : E.Span) return Boolean
   is
      Held : constant E.Span := F (Data, Raw, "held");
      Root : constant Boolean := F (Data, Raw, "outer").Length > 0;
      Closed : constant E.Span := (if Root then F (Data, F (Data, Raw, "closed"), "record") else F (Data, Raw, "closed"));
      Outer : constant E.Span := F (Data, F (Data, Raw, "outer"), "record");
      Manager : constant E.Span := F (Data, Derivation, "manager_view");
      Cgroup : constant E.Span := F (Data, Raw, "cgroup");
      Identity : constant E.Span := F (Data, Cgroup, "identity");
      Prepared : constant E.Span := Event_With_Cause (Data, F (Data, Source, "events"), "PREPARED");
      Dispatch : constant E.Span := Event_With_Cause (Data, F (Data, Source, "events"), "DISPATCH_INTENT");
      Held_Event : constant E.Span := Event_With_Cause (Data, F (Data, Source, "events"), "HELD");
      Closed_Event : constant E.Span := Event_With_Cause (Data, F (Data, Source, "events"), "CLOSED");
      Images : constant E.Span := F (Data, Derivation, "original_launch_preimages");
   begin
      if not Text (Data, F (Data, Fact, "phase"), "NAMESPACE_CLOSED")
        or else not Same (Data, F (Data, Fact, "retained"), F (Data, Row, "bound"))
        or else not Bytes_Is (Data, F (Data, Fact, "protocol"), "CLOSED_ECHILD")
        or else not Bytes_Is (Data, F (Data, Fact, "namespace_wait"), "PIDFD_TERMINAL")
        or else not Bytes_Is (Data, F (Data, Fact, "helper_wait"), "PIDFD_TERMINAL")
        or else not Wire_Matches (Data, F (Data, Raw, "namespace_wait"), F (Data, Derivation, "namespace_wait"))
        or else not Wire_Matches (Data, F (Data, Raw, "helper_wait"), F (Data, Derivation, "helper_wait"))
        or else not Field_Same (Data, Fact, Derivation, "namespace_wait") or else not Field_Same (Data, Fact, Derivation, "helper_wait")
        or else not Wire_Matches (Data, F (Data, Held, "frame"), F (Data, Derivation, "held_frame"))
        or else not Wire_Matches (Data, F (Data, Closed, "frame"), F (Data, Derivation, "closed_frame"))
        or else not Frame_Matches (Data, Derivation, Held, Closed, Root)
        or else not Wire_Matches (Data, F (Data, Held, "peer"), F (Data, Fact, "peer"))
        or else not Same (Data, F (Data, Fact, "peer"), F (Data, Fact, "held_peer"))
        or else not Same (Data, F (Data, Fact, "namespace"), F (Data, Fact, "held_namespace"))
        or else not Same (Data, F (Data, Fact, "helper_image"), F (Data, Fact, "expected_helper_image"))
        or else not Same (Data, F (Data, Fact, "challenge"), F (Data, Fact, "held_challenge"))
        or else not Same (Data, F (Data, Fact, "actual_unit"), F (Data, Row, "planned_unit"))
        or else not Wire_Matches (Data, F (Data, F (Data, Raw, "manager"), "stdout"), F (Data, Manager, "stdout"))
        or else not Wire_Matches (Data, F (Data, F (Data, Raw, "manager"), "stderr"), F (Data, Manager, "stderr"))
        or else not Same (Data, F (Data, F (Data, Raw, "manager"), "returncode"), F (Data, Manager, "returncode"))
        or else not R.Archive_Integer_Valid (Data, F (Data, Manager, "returncode"))
        or else P.Number (Data, F (Data, Manager, "returncode")) /= To_Big_Integer (0)
        or else not P.Property (Data, Manager, "Id", F (Data, Fact, "actual_unit"))
        or else not P.Property (Data, Manager, "ControlGroup", F (Data, Fact, "cgroup"))
        or else not P.Property (Data, Manager, "InvocationID", F (Data, Fact, "invocation"))
        or else not P.Property (Data, Manager, "Delegate", F (Data, Fact, "manager_delegate"))
        or else not R.Archive_Bytes_Valid (Data, F (Data, Manager, "stdout"))
        or else not Wire_Matches (Data, F (Data, Cgroup, "events"), F (Data, Fact, "cgroup_events"))
        or else not Wire_Matches (Data, F (Data, Cgroup, "type"), F (Data, Fact, "cgroup_type"))
        or else not Same (Data, F (Data, Fact, "cgroup_owner"), F (Data, Identity, "uid"))
      then return False; end if;
      if not R.Archive_Integer_Valid (Data, F (Data, Identity, "mode"))
        or else not R.Archive_Integer_Valid (Data, F (Data, Fact, "cgroup_group_write"))
        or else not R.Archive_Integer_Valid (Data, F (Data, Fact, "cgroup_other_write"))
        or else P.Number (Data, F (Data, Fact, "cgroup_group_write")) /=
          (P.Number (Data, F (Data, Identity, "mode")) / To_Big_Integer (16)) mod To_Big_Integer (2) * To_Big_Integer (16)
        or else P.Number (Data, F (Data, Fact, "cgroup_other_write")) /=
          (P.Number (Data, F (Data, Identity, "mode")) / To_Big_Integer (2)) mod To_Big_Integer (2) * To_Big_Integer (2)
      then return False; end if;
      declare Stdout : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Manager, "stdout"));
              Position : E.Count := Stdout'First;
              Found : Boolean := False; begin
         -- The original terminal helper branch requires the actual MainPID=0.
         for I in Stdout'Range loop
            if Stdout (I) = 10 then
               if Raw_Text (Stdout, (Position, I - Position), "MainPID=0") then Found := True; end if;
               Position := I + 1;
            end if;
         end loop;
         if not Found then return False; end if;
      end;
      if not Selected_Events_Match (Data, Row, Source, Events)
        or else not Preimages_Match (Data, Events, Images)
        or else not Prepared_Matches (Data, Row, Prepared, Derivation)
        or else not Event_Hash (Data, Prepared, Images, F (Data, Fact, "intent"))
      then return False; end if;
      -- The scoped producer leaves the legacy genesis-only facts absent. They
      -- are not historical kernel evidence and cannot be invented by a witness.
      if not Is_None (Data, F (Data, Fact, "actual_store_genesis")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "actual_store_id")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "owner_store_genesis")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "owner_store_id")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "genesis_universe")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "genesis_instance")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "genesis_context_head")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "genesis_prime")) then return False; end if;
      if not Is_None (Data, F (Data, Fact, "genesis_root_count")) then return False; end if;
      if Root then
         if not Same (Data, F (Data, Held, "dispatch"), F (Data, Raw, "dispatch"))
           or else not Frame_Ticket_Matches (Data, Derivation, F (Data, F (Data, Raw, "dispatch"), "ticket"))
           or else not P.Namespace_Matches (Data, F (Data, Fact, "namespace"), F (Data, Held, "namespace_identity"))
           or else not P.Id_Hex (Data, F (Data, Fact, "challenge"), F (Data, F (Data, Raw, "dispatch"), "ticket"))
           or else not Same (Data, F (Data, Outer, "namespace_event"), F (Data, Raw, "closed"))
           or else not Bytes_Is (Data, F (Data, Outer, "outer_pidfd_wait"), "PIDFD_TERMINAL")
           or else not Bytes_Is (Data, F (Data, Outer, "actual_namespace_wait"), "PIDFD_TERMINAL")
           or else not R.Archive_Integer_Valid (Data, F (Data, Outer, "actual_launcher_wait"))
           or else not P.Id_Hex (Data, F (Data, Fact, "closed_event"), F (Data, F (Data, Raw, "outer"), "event_id"))
           or else not Same (Data, F (Data, F (Data, Closed, "held"), "record"), Held)
           or else not Same (Data, F (Data, F (Data, Closed, "actual_capture"), "held"), Held)
           or else not Bytes_Is (Data, F (Data, F (Data, Closed, "actual_capture"), "namespace_wait"), "PIDFD_TERMINAL")
         then return False; end if;
         return P.JSON_Value_Matches (Data, F (Data, Derivation, "dispatch_json"), F (Data, F (Data, Raw, "dispatch"), "resource_dispatch"))
           and then P.Hash_Field (Data, F (Data, Derivation, "dispatch_json"), F (Data, Fact, "dispatch"))
           and then P.Hash_Field (Data, F (Data, Derivation, "helper_image_bytes"), F (Data, Fact, "helper_image"));
      end if;
      return Wire_Matches (Data, F (Data, Closed, "namespace"), F (Data, Fact, "namespace"))
        and then Frame_Ticket_Matches (Data, Derivation, F (Data, F (Data, Dispatch, "payload"), "ticket"))
        and then Wire_Matches (Data, F (Data, Held, "namespace"), F (Data, Fact, "held_namespace"))
        and then Wire_Matches (Data, F (Data, Closed, "peer"), F (Data, Fact, "peer"))
        and then Wire_Matches (Data, F (Data, Held, "helper_sha256"), F (Data, Fact, "helper_image"))
        and then Wire_Matches (Data, F (Data, Held, "challenge"), F (Data, Fact, "challenge"))
        and then Same (Data, F (Data, Held_Event, "payload"), Held)
        and then Same (Data, F (Data, Closed_Event, "payload"), Closed)
        and then Event_Hash (Data, Dispatch, Images, F (Data, Fact, "dispatch"))
        and then Event_Hash (Data, Closed_Event, Images, F (Data, Fact, "closed_event"))
        and then P.JSON_Value_Matches (Data, F (Data, Derivation, "held_event_json"), F (Data, Derivation, "held_event_value"))
        and then Same (Data, Held_Event, F (Data, Derivation, "held_event_value"))
        and then P.Hash_Field (Data, F (Data, Derivation, "held_event_json"), F (Data, Derivation, "held_event_digest"))
        and then P.Id_Hex (Data, F (Data, Derivation, "held_event_digest"), F (Data, Closed, "held"));
   end Physical_Closed_Matches;

   function Historical_Source_Matches
     (Data : E.Bytes; Row, Fact, Source, Owner : E.Span) return Boolean
   is
      Original : constant E.Span := Original_Source (Data, Source);
      Historical : constant E.Span := F (Data, Original, "historical");
      Witness : constant E.Span := F (Data, Historical, "witness");
      Derivation : constant E.Span := F (Data, Source, "history_derivation");
      Payload : constant E.Span := F (Data, Derivation, "witness_body");
      Packet : constant E.Span := F (Data, Payload, "packet");
      Native : constant E.Span := F (Data, Payload, "native");
      Origin_Row : constant E.Span := F (Data, Payload, "original_row");
      Origin_Source : constant E.Span := F (Data, Payload, "source");
      Events : constant E.Span := F (Data, Payload, "launch_prefix");
      Raw : constant E.Span := F (Data, Origin_Source, "kernel");
      Projection : constant E.Span := F (Data, Derivation, "original_projection");
      Current_Projection : constant E.Span := F (Data, Derivation, "projection_value");
      Blank : constant E.Span := F (Data, Current_Projection, "current");
      Current_Prepared : constant E.Span := Event_With_Cause (Data, F (Data, Original, "events"), "PREPARED");
      Rows : constant E.Span := F (Data, Packet, "rows");
      Facts : constant E.Span := F (Data, Packet, "facts");
      Old_Fact : E.Span := (1, 0);
      Replay : constant R.Scoped_Replay_Result := R.Reestablish_Scoped_Observation (Data, Native);
   begin
      if not No_Owner (Data, Row, Owner)
        or else not Is_None (Data, F (Data, Original, "kernel"))
        or else not Same (Data, F (Data, Original, "journal_head"), F (Data, Owner, "launch_head"))
        or else not Selected_Events_Match (Data, Row, Original, F (Data, Owner, "launch_events"))
        or else not Preimages_Match (Data, F (Data, Owner, "launch_events"), F (Data, Derivation, "launch_preimages"))
        or else not Text (Data, F (Data, Historical, "schema"), "worldline.genuine-retained-closed-projection-v1")
        or else not Text (Data, F (Data, Witness, "schema"), "worldline.protected-scoped-observation-event-v1")
        or else not Text (Data, F (Data, Witness, "cause"), "CLOSED_NATIVE_WITNESS")
        or else not P.Id_Hex (Data, F (Data, F (Data, Row, "bound"), "reservation"), F (Data, Witness, "reservation"))
        or else not Contains (Data, F (Data, Owner, "observation_events"), Witness)
        or else not Text (Data, F (Data, Derivation, "schema"), "worldline.scoped-history-derivation-v1")
        or else not P.JSON_Value_Matches (Data, F (Data, Derivation, "witness_json"), Witness)
        or else not P.Scoped_Record_Matches
          (Data, F (Data, Witness, "payload"), Payload, False, False)
        or else not Field_Same (Data, Origin_Row, Row, "bound") or else not Field_Same (Data, Origin_Row, Row, "scope")
        or else not Field_Same (Data, Origin_Row, Row, "actual_unit") or else not Field_Same (Data, Origin_Row, Row, "cgroup")
        or else not Field_Same (Data, Origin_Row, Row, "invocation")
        or else not Field_Same (Data, Origin_Row, Row, "planned_unit")
        or else not Same (Data, F (Data, F (Data, F (Data, Packet, "request"), "original"), "bound"), F (Data, Row, "bound"))
        or else Replay.State /= R.Native_Redecided or else Replay.Roster_Entry /= R.Classify_Entry
        or else Replay.Native_Status /= 2 or else not Text (Data, F (Data, Native, "status"), "REAPED")
        or else not R.Scoped_Material_Matches (Data, Native, Packet)
        or else not Same (Data, F (Data, Packet, "before"), F (Data, Packet, "proposed"))
        or else not Same (Data, F (Data, Packet, "history"), F (Data, Packet, "proposed_history"))
        or else not Same (Data, F (Data, Packet, "rows"), F (Data, Packet, "proposed_rows"))
        or else not Same (Data, F (Data, Packet, "projection"), F (Data, Packet, "proposed_projection"))
        or else not Same (Data, F (Data, Packet, "buckets"), F (Data, Packet, "proposed_buckets"))
        or else not Same (Data, F (Data, Packet, "buckets"), F (Data, Packet, "actual_buckets"))
        or else not P.Scoped_Record_Matches
          (Data, F (Data, Historical, "actual_native_redecision"), Native, False, False)
        or else not P.Current_Source_Matches (Data, Packet, Projection)
        or else not Same (Data, F (Data, Projection, "source"), F (Data, Payload, "current_source"))
        or else not Same (Data, F (Data, Projection, "binding"), F (Data, Owner, "binding"))
        or else not Same (Data, F (Data, Payload, "installation"), F (Data, Owner, "installation"))
        or else not Same (Data, F (Data, Payload, "installation"), F (Data, F (Data, Payload, "current_source"), "installation"))
        or else not Same (Data, Events, F (Data, Origin_Source, "launch_prefix"))
        or else not Prefix (Data, Events, F (Data, Owner, "launch_events"))
        or else not Preimages_Match (Data, Events, F (Data, Derivation, "original_launch_preimages"))
        or else not Same (Data, F (Data, Payload, "owned_closed"), F (Data, Raw, "closed"))
        or else Is_None (Data, F (Data, Payload, "owned_closed"))
        or else not Same (Data, Origin_Source, F (Data, Derivation, "original_source_value"))
        or else not P.Scoped_Record_Matches
          (Data, F (Data, Derivation, "original_source_scoped"), Origin_Source, False, False)
        or else not P.JSON_Value_Matches (Data, F (Data, Derivation, "original_source_json"), F (Data, Derivation, "original_source_scoped"))
        or else (if F (Data, Raw, "outer").Length > 0 then
            not Same (Data, F (Data, Payload, "owned_closed_event"), F (Data, Raw, "closed"))
            and then not Same (Data, F (Data, Payload, "owned_closed_event"), F (Data, Raw, "outer"))
          else not Same (Data, F (Data, Payload, "owned_closed_event"),
            Event_With_Cause (Data, F (Data, Origin_Source, "events"), "CLOSED")))
        or else not R.Archive_Is_Sequence (Data, Rows) or else not R.Archive_Is_Sequence (Data, Facts)
        or else Len (Data, Rows) /= Len (Data, Facts)
      then return False; end if;
      if Len (Data, Rows) > 0 then
         for I in E.Count range 0 .. Len (Data, Rows) - 1 loop
            if Same (Data, F (Data, Element (Data, Rows, I), "bound"), F (Data, Row, "bound")) then
               if Old_Fact.Length > 0 or else not Same (Data, Element (Data, Rows, I), Origin_Row) then return False; end if;
               Old_Fact := Element (Data, Facts, I);
            end if;
         end loop;
      end if;
      if not R.Archive_Record_Is (Data, Old_Fact, "PhysicalFacts")
        or else not P.Scoped_Record_Matches
          (Data, F (Data, Historical, "original_physical"), Old_Fact, False, False)
        or else not Physical_Closed_Matches (Data, Origin_Row, Old_Fact, Raw, Origin_Source, Derivation, Events)
      then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "retained") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "intent") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "dispatch") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "actual_unit") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "cgroup") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "invocation") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "namespace") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "held_namespace") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "peer") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "held_peer") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "helper_image") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "expected_helper_image") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "challenge") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "held_challenge") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "protocol") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "closed_event") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "namespace_wait") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "helper_wait") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "cgroup_events") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "cgroup_type") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "manager_delegate") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "cgroup_owner") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "cgroup_group_write") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "cgroup_other_write") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "actual_store_genesis") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "actual_store_id") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "owner_store_genesis") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "owner_store_id") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "genesis_universe") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "genesis_instance") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "genesis_context_head") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "genesis_prime") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "genesis_root_count") then return False; end if;
      if not Field_Same (Data, Fact, Old_Fact, "phase") then return False; end if;
      -- Complete raw source preimage before the retained launch_prefix was
      -- appended; observation_head belongs to that genuine original sample.
      declare Sample : constant E.Span := F (Data, Derivation, "sample_source"); begin
         if (if Text (Data, F (Data, Sample, "head_encoding"), "OPERATION_ARCHIVE")
                or else Text (Data, F (Data, Sample, "head_encoding"), "ROOT_RAW_ARCHIVE") then
                 not P.Head_Source_Matches (Data, Old_Fact, Sample)
             else not P.JSON_Value_Matches (Data, F (Data, Derivation, "sample_source_json"), Sample)
               or else not P.Hash_Field (Data, F (Data, Derivation, "sample_source_json"), F (Data, Old_Fact, "observation_head")))
           or else not Field_Same (Data, Sample, Origin_Source, "reservation")
           or else not Field_Same (Data, Sample, Origin_Source, "journal_head")
           or else not Field_Same (Data, Sample, Origin_Source, "challenge")
           or else not Field_Same (Data, Sample, Origin_Source, "events")
           or else not Field_Same (Data, Sample, Origin_Source, "kernel")
         then return False; end if;
      end;
      if not R.Archive_Record_Is (Data, Blank, "PhysicalFacts") or else not Absent_Fields (Data, Blank)
        or else (if Current_Prepared.Length = 0 then not Is_None (Data, F (Data, Blank, "intent"))
          else not Prepared_Matches (Data, Row, Current_Prepared, Derivation)
            or else not Event_Hash (Data, Current_Prepared, F (Data, Derivation, "launch_preimages"), F (Data, Blank, "intent")))
        or else not Text (Data, F (Data, Blank, "phase"), "UNAVAILABLE")
        or else not Same (Data, F (Data, Blank, "retained"), F (Data, Row, "bound"))
        or else not P.Id_Hex (Data, F (Data, Blank, "observation_head"), F (Data, Original, "challenge"))
        or else not Same (Data, F (Data, Current_Projection, "witness"), Witness)
        or else not P.Scoped_Record_Matches
          (Data, F (Data, Derivation, "projection_scoped"), Current_Projection, False, False)
        or else not P.JSON_Value_Matches (Data, F (Data, Derivation, "projection_json"), F (Data, Derivation, "projection_scoped"))
        or else not P.Hash_Field (Data, F (Data, Derivation, "projection_json"), F (Data, Fact, "observation_head"))
      then return False; end if;
      if not Field_Same (Data, Blank, Fact, "current") then return False; end if;
      if not Field_Same (Data, Blank, Fact, "current_epoch") then return False; end if;
      if not Field_Same (Data, Blank, Fact, "current_universe_head") then return False; end if;
      if not Field_Same (Data, Blank, Fact, "current_ledger_head") then return False; end if;
      return True;
   end Historical_Source_Matches;
   function Original_Property (Data : E.Bytes; Properties : E.Span; Name : String) return E.Span is
      V : constant E.View := E.Decode (Data, Properties, E.Operation);
      Members : constant E.Span := V.Children;
      Result : E.Span := (1, 0);
      Count : constant E.Count := E.Array_Length (Data, Members);
   begin
      if Count > 0 then
         for I in E.Count range 0 .. Count - 1 loop
            declare
               Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, Members, I), E.Finalization);
               Key : constant E.Span := E.Array_Element (Data, Pair.Children, 0);
            begin
               if Text (Data, Key, Name) or else Bytes_Is (Data, Key, Name) then
                  if Result.Length > 0 then return (1, 0); end if;
                  Result := E.Array_Element (Data, Pair.Children, 1);
               end if;
            end;
         end loop;
      end if;
      return Result;
   end Original_Property;

   function Manager_View_Matches (Data : E.Bytes; Original, View : E.Span) return Boolean is
     (Wire_Matches (Data, F (Data, Original, "stdout"), F (Data, View, "stdout"))
      and then Wire_Matches (Data, F (Data, Original, "stderr"), F (Data, View, "stderr"))
      and then Field_Same (Data, Original, View, "returncode")
      and then R.Archive_Integer_Valid (Data, F (Data, View, "returncode"))
      and then P.Number (Data, F (Data, View, "returncode")) = To_Big_Integer (0));

   function Manager_Pid_Matches (Data : E.Bytes; Manager : E.Span; Pid : Valid_Big_Integer) return Boolean is
   begin
      if Pid < To_Big_Integer (0) or else not R.Archive_Bytes_Valid (Data, F (Data, Manager, "stdout")) then return False; end if;
      declare Raw : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Manager, "stdout")); begin
         return P.Decimal (Raw, P.Line (Raw, "MainPID", 61)) = Pid;
      end;
   end Manager_Pid_Matches;

   function Held_Frame_Matches (Data : E.Bytes; Protocol, Held, Ticket, Kind : E.Span) return Boolean is
      T : constant E.View := Text_View (Data, Ticket);
   begin
      if not R.Archive_Bytes_Valid (Data, F (Data, Protocol, "held_frame"))
        or else T.Form /= E.Text_Value or else not E.Bytes_Valid (Data, T.Payload)
        or else not R.Archive_Integer_Valid (Data, F (Data, Held, "init_pid"))
      then return False; end if;
      declare
         Raw : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Protocol, "held_frame"));
         Lines : E.Count := 0;
         Part : constant E.Span := Line_Number (Raw, 3);
      begin
         for B of Raw loop if B = 10 then Lines := Lines + 1; end if; end loop;
         if Raw'Length = 0 or else Raw (Raw'Last) /= 10 or else Lines /= 4
           or else not Raw_Text (Raw, Line_Number (Raw, 2), "HELD")
           or else not E.C.P.Valid (Raw, Part) or else Part.Length = 0
         then return False; end if;
         declare
            Ticket_Raw : constant E.Bytes := E.Materialize (Data, T.Payload);
         begin
            if not Raw_Same (Raw, Part, Ticket_Raw, (Ticket_Raw'First, Ticket_Raw'Length))
            then return False; end if;
         end;
         if P.Number (Data, F (Data, Held, "init_pid")) <= To_Big_Integer (0)
           or else Decimal (Raw, Line_Number (Raw, 4)) /= P.Number (Data, F (Data, Held, "init_pid"))
         then return False; end if;
         return (Text (Data, Kind, "ROOT") and then Raw_Text (Raw, Line_Number (Raw, 1), "WL-ROOT-WORKER-SUPERVISOR-v1"))
           or else (Text (Data, Kind, "ACTOR_V3") and then Raw_Text (Raw, Line_Number (Raw, 1), "WL-RESOURCE-SUPERVISOR-v3"))
           or else (Text (Data, Kind, "SUPERVISOR_V1") and then Raw_Text (Raw, Line_Number (Raw, 1), "WL-RESOURCE-SUPERVISOR-v1"));
      end;
   end Held_Frame_Matches;

   function FS_Text_Matches (Data : E.Bytes; Item, Encoded : E.Span) return Boolean is
      V : constant E.View := Text_View (Data, Item);
   begin
      if R.Archive_Bytes_Valid (Data, Item) then
         return R.Archive_Bytes_Valid (Data, Encoded) and then Same (Data, Item, Encoded)
           and then (for all B of R.Archive_Bytes (Data, Item) => B /= 0);
      end if;
      if V.Form /= E.Text_Value or else not E.Bytes_Valid (Data, V.Payload)
        or else not R.Archive_Bytes_Valid (Data, Encoded) then return False; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, V.Payload);
         Target : constant E.Bytes := R.Archive_Bytes (Data, Encoded);
         I, J : E.Count := 0;
      begin
         -- Original text identities use UTF-8/surrogatepass; Linux fsencode
         -- converts only U+DC80..U+DCFF back to their original single byte.
         -- All other valid UTF-8 characters retain their complete byte extent.
         while I < Raw'Length loop
            declare
               First : constant Natural := Natural (Raw (Raw'First + I));
               Width : E.Count;
               Code : Natural;
               Minimum : Natural;
            begin
               if First < 128 then Width := 1; Code := First; Minimum := 0;
               elsif First in 194 .. 223 then Width := 2; Code := First - 192; Minimum := 128;
               elsif First in 224 .. 239 then Width := 3; Code := First - 224; Minimum := 2048;
               elsif First in 240 .. 244 then Width := 4; Code := First - 240; Minimum := 65536;
               else return False; end if;
               if Width > Raw'Length - I then return False; end if;
               if Width > 1 then
                  for K in E.Count range 1 .. Width - 1 loop
                     declare B : constant Natural := Natural (Raw (Raw'First + I + K)); begin
                        if B not in 128 .. 191 then return False; end if;
                        Code := Code * 64 + B - 128;
                     end;
                  end loop;
               end if;
               if Code < Minimum or else Code > 16#10FFFF# or else Code = 0 then return False; end if;
               if Code in 16#DC80# .. 16#DCFF# then
                  if J >= Target'Length or else Natural (Target (Target'First + J)) /= Code - 16#DC00# then return False; end if;
                  J := J + 1;
               else
                  if Code in 16#D800# .. 16#DFFF# or else Width > Target'Length - J then return False; end if;
                  for K in E.Count range 0 .. Width - 1 loop
                     if Raw (Raw'First + I + K) /= Target (Target'First + J + K) then return False; end if;
                  end loop;
                  J := J + Width;
               end if;
               I := I + Width;
            end;
         end loop;
         return J = Target'Length;
      end;
   end FS_Text_Matches;

   function Command_Matches (Data : E.Bytes; Arguments, Encoded, Command : E.Span) return Boolean is
      Position : E.Count := 0;
   begin
      if not R.Archive_Is_Sequence (Data, Arguments) or else not R.Archive_Is_Sequence (Data, Encoded)
        or else Len (Data, Arguments) = 0 or else Len (Data, Arguments) /= Len (Data, Encoded)
        or else not R.Archive_Bytes_Valid (Data, Command) then return False; end if;
      declare Raw : constant E.Bytes := R.Archive_Bytes (Data, Command); begin
         for I in E.Count range 0 .. Len (Data, Arguments) - 1 loop
            if not FS_Text_Matches (Data, Element (Data, Arguments, I), Element (Data, Encoded, I)) then return False; end if;
            declare Word : constant E.Bytes := R.Archive_Bytes (Data, Element (Data, Encoded, I)); begin
               if Position > Raw'Length or else Word'Length >= Raw'Length - Position then return False; end if;
               if Word'Length > 0 then
                  for K in E.Count range 0 .. Word'Length - 1 loop
                     if Word (Word'First + K) /= Raw (Raw'First + Position + K) then return False; end if;
                  end loop;
               end if;
               Position := Position + Word'Length;
               if Raw (Raw'First + Position) /= 0 then return False; end if;
               Position := Position + 1;
            end;
         end loop;
         return Position = Raw'Length;
      end;
   end Command_Matches;

   function Helper_Process_Matches (Data : E.Bytes; Raw_Process, Process : E.Span) return Boolean is
      Observation : constant E.Span := F (Data, Process, "observation");
      Other : constant E.Span := F (Data, F (Data, Process, "raw"), "raw");
   begin
      if not R.Archive_Record_Is (Data, Observation, "ProcessObservation")
        or else not R.Archive_Bytes_Valid (Data, F (Data, Raw_Process, "status"))
        or else not R.Archive_Bytes_Valid (Data, F (Data, Raw_Process, "stat"))
        or else not R.Archive_Bytes_Valid (Data, F (Data, Other, "status"))
        or else not Field_Same (Data, Raw_Process, Other, "cgroup")
        or else not Field_Same (Data, Raw_Process, Other, "maps")
        or else not Field_Same (Data, Raw_Process, Other, "cmdline")
      then return False; end if;
      declare
         Status : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Raw_Process, "status"));
         Stat : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Raw_Process, "stat"));
         Before : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Other, "status"));
         Pid : constant Big_Integer := P.Number (Data, F (Data, Observation, "host_pid"));
         Ppid : constant Big_Integer := P.Number (Data, F (Data, Observation, "parent_pid"));
         Start : constant Big_Integer := P.Number (Data, F (Data, Observation, "start_tick"));
         NSpid : constant E.Span := P.Line (Status, "NSpid", 58);
         Original_NSpid : constant E.Span := P.Line (Before, "NSpid", 58);
      begin
         if Pid <= To_Big_Integer (0) or else Ppid < To_Big_Integer (0) or else Start < To_Big_Integer (0)
           or else P.Decimal (Status, P.Word (Status, P.Line (Status, "Pid", 58), 1)) /= Pid
           or else P.Decimal (Status, P.Word (Status, P.Line (Status, "PPid", 58), 1)) /= Ppid
           or else P.Stat_Number (Stat, 1) /= Pid or else P.Stat_Number (Stat, 4) /= Ppid or else P.Stat_Number (Stat, 22) /= Start
           or else not E.C.P.Valid (Status, NSpid) or else NSpid.Length = 0
           or else not E.C.P.Valid (Before, Original_NSpid)
           or else not Raw_Same (Status, NSpid, Before, Original_NSpid)
           or else P.Word (Status, P.Line (Status, "Uid", 58), 5).Length /= 0
           or else P.Word (Status, P.Line (Status, "Gid", 58), 5).Length /= 0
         then return False; end if;
         for I in Positive range 1 .. 4 loop
            for Gid in Boolean loop
               declare Name : constant String := (if Gid then "Gid" else "Uid");
                  Value : constant Big_Integer := P.Decimal (Status, P.Word (Status, P.Line (Status, Name, 58), I));
               begin
                  if Value < To_Big_Integer (0)
                    or else Value /= P.Decimal (Before, P.Word (Before, P.Line (Before, Name, 58), I))
                  then return False; end if;
               end;
            end loop;
         end loop;
         return True;
      end;
   end Helper_Process_Matches;

   function Root_Event_Matches (Data : E.Bytes; Event, Events, Row : E.Span; Kind : String) return Boolean is
     (Text (Data, F (Data, Event, "kind"), Kind)
      and then P.Id_Hex (Data, F (Data, F (Data, Row, "bound"), "operation"), F (Data, Event, "operation"))
      and then Contains (Data, Events, Event));

   function Root_Held_Event (Data : E.Bytes; Events, Held, Row : E.Span) return E.Span is
      Result : E.Span := (1, 0);
   begin
      if not R.Archive_Is_Sequence (Data, Events) then return Result; end if;
      if Len (Data, Events) > 0 then
         for I in E.Count range 0 .. Len (Data, Events) - 1 loop
            declare Event : constant E.Span := Element (Data, Events, I); begin
               if Text (Data, F (Data, Event, "kind"), "HELD")
                 and then P.Id_Hex (Data, F (Data, F (Data, Row, "bound"), "operation"), F (Data, Event, "operation"))
                 and then Same (Data, F (Data, Event, "record"), Held)
               then
                  if Result.Length > 0 then return (1, 0); end if;
                  Result := Event;
               end if;
            end;
         end loop;
      end if;
      return Result;
   end Root_Held_Event;

   function Owned_Protocol_Matches
     (Data : E.Bytes; Row, Fact, Source, Roster_Entry, History : E.Span) return Boolean
   is
      Raw : constant E.Span := F (Data, Source, "kernel");
      Held : constant E.Span := F (Data, Roster_Entry, "held");
      Closed_Event : constant E.Span := F (Data, Roster_Entry, "closed");
      Outer_Event : constant E.Span := F (Data, Roster_Entry, "outer");
      Dispatch : constant E.Span := F (Data, Roster_Entry, "dispatch");
      Protocol : constant E.Span := F (Data, Source, "owned_protocol");
      Projection : constant E.Span := F (Data, Source, "physical_projection");
      Kind : constant E.Span := F (Data, Roster_Entry, "kind");
      Root : constant Boolean := Text (Data, Kind, "ROOT");
      Closed : constant E.Span := (if Root then F (Data, Closed_Event, "record") else Closed_Event);
      Outer : constant E.Span := F (Data, Outer_Event, "record");
      Has_Closed : constant Boolean := not Is_None (Data, Closed_Event);
      Has_Outer : constant Boolean := not Is_None (Data, Outer_Event);
      Fully_Closed : constant Boolean := Has_Closed and then (not Root or else Has_Outer);
      Events : constant E.Span := F (Data, History, "launch_events");
      Root_Events : constant E.Span := F (Data, History, "root_events");
      Selected : constant E.Span := F (Data, Protocol, "events");
      Prepared : constant E.Span := Event_With_Cause (Data, Selected, "PREPARED");
      Held_Event : constant E.Span := Event_With_Cause (Data, Selected, "HELD");
      Dispatch_Event : constant E.Span := Event_With_Cause (Data, Selected, "DISPATCH_INTENT");
      Ticket : constant E.Span := (if Root then F (Data, Dispatch, "ticket") else F (Data, F (Data, Dispatch, "payload"), "ticket"));
      Arguments : constant E.Span := (if Root then F (Data, Dispatch, "helper_arguments")
                                    else F (Data, F (Data, Dispatch, "payload"), "helper_arguments"));
      Helper : constant E.Span := F (Data, F (Data, Source, "process_inventory"), "helper_pidfd");
      Helper_Proc : constant E.Span := F (Data, Raw, "helper_proc");
      Manager : constant E.Span := F (Data, Protocol, "manager_view");
      Identity : constant E.Span := F (Data, F (Data, Raw, "cgroup"), "identity");
      Initial_Manager : constant E.Span := F (Data, Protocol, "held_manager_view");
      Helper_Pid : constant Big_Integer := P.Number (Data, F (Data, Held, "helper_pid"));
   begin
      if not R.Archive_Record_Is (Data, Row, "RunRow") or else not R.Archive_Record_Is (Data, Fact, "PhysicalFacts")
        or else not Same (Data, Row, F (Data, Roster_Entry, "row"))
        or else not Same (Data, F (Data, Fact, "retained"), F (Data, Row, "bound"))
        or else not Text (Data, F (Data, Protocol, "schema"), "worldline.owned-scoped-protocol-preimages-v1")
        or else not Same (Data, Held, F (Data, Raw, "held"))
        or else not Same (Data, Closed_Event, F (Data, Raw, "closed"))
        or else (Root and then not Same (Data, Outer_Event, F (Data, Raw, "outer")))
        or else (not Root and then (not Is_None (Data, Outer_Event) or else F (Data, Raw, "outer").Length /= 0))
        or else Helper_Pid <= To_Big_Integer (0)
        or else not Held_Frame_Matches (Data, Protocol, Held, Ticket, Kind)
        or else not Wire_Matches (Data, F (Data, Held, "frame"), F (Data, Protocol, "held_frame"))
        or else not Wire_Matches (Data, F (Data, Held, "peer"), F (Data, Fact, "peer"))
        or else not Same (Data, F (Data, Fact, "peer"), F (Data, Fact, "held_peer"))
        or else not Manager_View_Matches (Data, F (Data, Raw, "manager"), Manager)
        or else not Manager_View_Matches (Data, F (Data, Held, "manager"), Initial_Manager)
        or else not Manager_Pid_Matches (Data, Initial_Manager, Helper_Pid)
        or else not P.Property (Data, Initial_Manager, "Id", F (Data, Fact, "actual_unit"))
        or else not P.Property (Data, Initial_Manager, "ControlGroup", F (Data, Fact, "cgroup"))
        or else not P.Property (Data, Initial_Manager, "InvocationID", F (Data, Fact, "invocation"))
        or else not Wire_Matches (Data, Original_Property (Data, F (Data, Held, "properties"), "Id"), F (Data, Fact, "actual_unit"))
        or else not Wire_Matches (Data, Original_Property (Data, F (Data, Held, "properties"), "ControlGroup"), F (Data, Fact, "cgroup"))
        or else not Wire_Matches (Data, Original_Property (Data, F (Data, Held, "properties"), "InvocationID"), F (Data, Fact, "invocation"))
        or else not P.Property (Data, Manager, "Id", F (Data, Fact, "actual_unit"))
        or else not P.Property (Data, Manager, "ControlGroup", F (Data, Fact, "cgroup"))
        or else not P.Property (Data, Manager, "InvocationID", F (Data, Fact, "invocation"))
        or else not P.Property (Data, Manager, "Delegate", F (Data, Fact, "manager_delegate"))
        or else not Wire_Matches (Data, F (Data, Raw, "namespace_wait"), F (Data, Fact, "namespace_wait"))
        or else not Wire_Matches (Data, F (Data, Raw, "helper_wait"), F (Data, Fact, "helper_wait"))
        or else not Wire_Matches (Data, F (Data, F (Data, Raw, "cgroup"), "events"), F (Data, Fact, "cgroup_events"))
        or else not Wire_Matches (Data, F (Data, F (Data, Raw, "cgroup"), "type"), F (Data, Fact, "cgroup_type"))
        or else not Same (Data, F (Data, Identity, "uid"), F (Data, Fact, "cgroup_owner"))
        or else not R.Archive_Integer_Valid (Data, F (Data, Identity, "mode"))
        or else P.Number (Data, F (Data, Identity, "mode")) < To_Big_Integer (0)
        or else (P.Number (Data, F (Data, Identity, "mode")) / To_Big_Integer (4096)) mod To_Big_Integer (16) /= To_Big_Integer (4)
        or else not R.Archive_Integer_Valid (Data, F (Data, Fact, "cgroup_group_write"))
        or else not R.Archive_Integer_Valid (Data, F (Data, Fact, "cgroup_other_write"))
        or else P.Number (Data, F (Data, Fact, "cgroup_group_write")) /=
          (P.Number (Data, F (Data, Identity, "mode")) / To_Big_Integer (16)) mod To_Big_Integer (2) * To_Big_Integer (16)
        or else P.Number (Data, F (Data, Fact, "cgroup_other_write")) /=
          (P.Number (Data, F (Data, Identity, "mode")) / To_Big_Integer (2)) mod To_Big_Integer (2) * To_Big_Integer (2)
        or else not Wire_Matches (Data, (if Root then F (Data, F (Data, Held, "helper_proc"), "maps") else F (Data, Held, "maps")), F (Data, Protocol, "held_maps"))
        or else not Wire_Matches (Data, (if Root then F (Data, F (Data, Held, "helper_proc"), "cgroup") else F (Data, Held, "proc_cgroup")), F (Data, Protocol, "held_cgroup"))
        or else not P.Maps_Match (Data, F (Data, Protocol, "held_maps"), F (Data, Source, "inventory"))
        or else not P.Process_Cgroup_Matches (Data, F (Data, Protocol, "held_cgroup"), F (Data, Fact, "cgroup"))
        or else not P.JSON_Value_Matches (Data, F (Data, Projection, "dispatch_json"), F (Data, Projection, "dispatch_value"))
        or else not Same (Data, F (Data, Projection, "dispatch_value"), (if Root then F (Data, Dispatch, "resource_dispatch") else Dispatch))
        or else not P.Hash_Field (Data, F (Data, Projection, "dispatch_json"), F (Data, Fact, "dispatch"))
        or else not P.Hash_Field (Data, F (Data, Projection, "helper_image_bytes"), F (Data, Fact, "helper_image"))
        or else not Same (Data, F (Data, Fact, "helper_image"), F (Data, Fact, "expected_helper_image"))
        or else not Same (Data, F (Data, Fact, "namespace"), F (Data, Fact, "held_namespace"))
        or else not Same (Data, F (Data, Fact, "challenge"), F (Data, Fact, "held_challenge"))
        or else not Selected_Events_Match (Data, Row, Protocol, Events)
        or else not Preimages_Match (Data, Events, F (Data, Protocol, "launch_preimages"))
        or else not Prepared_Matches (Data, Row, Prepared, Protocol)
        or else not Event_Hash (Data, Prepared, F (Data, Protocol, "launch_preimages"), F (Data, Fact, "intent"))
      then return False; end if;
      if Bytes_Is (Data, F (Data, Fact, "helper_wait"), "PIDFD_LIVE") then
         if not Helper_Process_Matches (Data, Helper_Proc, Helper)
           or else not Same (Data, F (Data, Helper, "wait"), F (Data, Fact, "helper_wait"))
           or else P.Number (Data, F (Data, F (Data, Helper, "observation"), "host_pid")) /= Helper_Pid
           or else not Manager_Pid_Matches (Data, Manager, Helper_Pid)
           or else not P.Process_Cgroup_Matches (Data, F (Data, Helper_Proc, "cgroup"), F (Data, Fact, "cgroup"))
           or else not Command_Matches (Data, Arguments, F (Data, Protocol, "argument_bytes"), F (Data, Helper_Proc, "cmdline"))
         then return False; end if;
      elsif not Bytes_Is (Data, F (Data, Fact, "helper_wait"), "PIDFD_TERMINAL")
        or else not Is_None (Data, Helper_Proc) or else not Manager_Pid_Matches (Data, Manager, To_Big_Integer (0))
      then return False; end if;
      if Root then
         if not Same (Data, F (Data, Held, "dispatch"), Dispatch) or else not Same (Data, F (Data, Raw, "dispatch"), Dispatch)
           or else not P.Namespace_Matches (Data, F (Data, Fact, "namespace"), F (Data, Held, "namespace_identity"))
           or else not Field_Same (Data, F (Data, Held, "namespace_identity"), F (Data, Projection, "namespace_identity"), "device")
           or else not Field_Same (Data, F (Data, Held, "namespace_identity"), F (Data, Projection, "namespace_identity"), "inode")
           or else not P.Id_Hex (Data, F (Data, Fact, "challenge"), Ticket)
           or else Root_Held_Event (Data, Root_Events, Held, Row).Length = 0
           or else not Is_None (Data, F (Data, Roster_Entry, "closed_event"))
           or else not Wire_Matches (Data, F (Data, F (Data, Held, "helper_proc"), "cmdline"), F (Data, Protocol, "held_command"))
           or else not Command_Matches (Data, Arguments, F (Data, Protocol, "argument_bytes"), F (Data, Protocol, "held_command"))
         then return False; end if;
      else
         declare Challenge : constant E.Span := F (Data, Protocol, "held_challenge_value"); begin
            if not Wire_Matches (Data, F (Data, Held, "namespace"), F (Data, Fact, "namespace"))
              or else not Wire_Matches (Data, F (Data, Held, "helper_sha256"), F (Data, Fact, "helper_image"))
              or else not Same (Data, Dispatch, Dispatch_Event)
              or else not Same (Data, F (Data, Held_Event, "payload"), Held)
              or else not Event_Hash (Data, Dispatch, F (Data, Protocol, "launch_preimages"), F (Data, Fact, "dispatch"))
              or else not P.JSON_Value_Matches (Data, F (Data, Protocol, "held_challenge_json"), Challenge)
              or else not Same (Data, F (Data, Challenge, "dispatch"), Dispatch)
              or else not Same (Data, F (Data, Challenge, "held_frame"), F (Data, Held, "frame"))
              or else not Field_Same (Data, Challenge, Held, "peer")
              or else not Field_Same (Data, Challenge, Held, "namespace")
              or else not Field_Same (Data, Challenge, Held, "manager")
              or else not Field_Same (Data, Challenge, Held, "maps")
              or else not Field_Same (Data, Challenge, Held, "proc_cgroup")
              or else not P.Hash_Field (Data, F (Data, Protocol, "held_challenge_json"), F (Data, Fact, "challenge"))
              or else not Wire_Matches (Data, F (Data, Held, "challenge"), F (Data, Fact, "challenge"))
              or else not Wire_Matches (Data, F (Data, Held, "cmdline"), F (Data, Protocol, "held_command"))
              or else not Command_Matches (Data, Arguments, F (Data, Protocol, "argument_bytes"), F (Data, Protocol, "held_command"))
            then return False; end if;
         end;
      end if;
      if Has_Closed then
         if not Wire_Matches (Data, F (Data, Closed, "frame"), F (Data, Protocol, "closed_frame"))
           or else not Frame_Matches (Data, Protocol, Held, Closed, Root)
           or else not Frame_Ticket_Matches (Data, Protocol, Ticket)
           or else not Bytes_Is (Data, F (Data, Fact, "namespace_wait"), "PIDFD_TERMINAL")
         then return False; end if;
         if Root then
            if not (Root_Event_Matches (Data, Closed_Event, Root_Events, Row, "CLOSED")
                    or else Root_Event_Matches (Data, Closed_Event, Root_Events, Row, "CLOSED_NS"))
              or else not Root_Event_Matches (Data, F (Data, Closed, "held"), Root_Events, Row, "HELD")
              or else not Same (Data, F (Data, F (Data, Closed, "held"), "record"), Held)
              or else not Same (Data, F (Data, F (Data, Closed, "actual_capture"), "held"), Held)
              or else not Bytes_Is (Data, F (Data, F (Data, Closed, "actual_capture"), "namespace_wait"), "PIDFD_TERMINAL")
              or else not Same (Data, F (Data, F (Data, Closed, "actual_capture"), "held_event"), F (Data, Closed, "held"))
              or else not Is_None (Data, F (Data, F (Data, Closed, "actual_capture"), "closed"))
              or else not Is_None (Data, F (Data, F (Data, Closed, "actual_capture"), "outer"))
              or else not P.Property (Data, F (Data, F (Data, Closed, "actual_capture"), "current_manager"), "Id", F (Data, Fact, "actual_unit"))
              or else not P.Property (Data, F (Data, F (Data, Closed, "actual_capture"), "current_manager"), "ControlGroup", F (Data, Fact, "cgroup"))
              or else not P.Property (Data, F (Data, F (Data, Closed, "actual_capture"), "current_manager"), "InvocationID", F (Data, Fact, "invocation"))
              or else not Wire_Matches (Data, Original_Property (Data, F (Data, F (Data, Closed, "actual_capture"), "current_properties"), "ControlGroup"), F (Data, Fact, "cgroup"))
              or else not Wire_Matches (Data, Original_Property (Data, F (Data, F (Data, Closed, "actual_capture"), "current_properties"), "InvocationID"), F (Data, Fact, "invocation"))
            then return False; end if;
         else
            if not Wire_Matches (Data, F (Data, Closed, "namespace"), F (Data, Fact, "namespace"))
              or else not Wire_Matches (Data, F (Data, Closed, "peer"), F (Data, Fact, "peer"))
              or else not Contains (Data, Events, F (Data, Roster_Entry, "closed_event"))
              or else not Same (Data, F (Data, F (Data, Roster_Entry, "closed_event"), "payload"), Closed)
              or else not Same (Data, F (Data, Roster_Entry, "closed_event"), Event_With_Cause (Data, Selected, "CLOSED"))
              or else not Event_Hash (Data, F (Data, Roster_Entry, "closed_event"), F (Data, Protocol, "launch_preimages"), F (Data, Fact, "closed_event"))
              or else not Same (Data, Held_Event, F (Data, Protocol, "held_event_value"))
              or else not P.JSON_Value_Matches (Data, F (Data, Protocol, "held_event_json"), F (Data, Protocol, "held_event_value"))
              or else not P.Hash_Field (Data, F (Data, Protocol, "held_event_json"), F (Data, Protocol, "held_event_digest"))
              or else not P.Id_Hex (Data, F (Data, Protocol, "held_event_digest"), F (Data, Closed, "held"))
            then return False; end if;
         end if;
      elsif not Is_None (Data, F (Data, Fact, "closed_event")) or else (not Root and then not Is_None (Data, F (Data, Roster_Entry, "closed_event"))) then return False; end if;
      if Root and then Has_Outer then
         if not Has_Closed or else
           (if Text (Data, F (Data, Closed_Event, "kind"), "CLOSED_NS") then
              not Root_Event_Matches (Data, Outer_Event, Root_Events, Row, "CLOSED_OUTER")
            else not Root_Event_Matches (Data, Outer_Event, Root_Events, Row, "CLOSED"))
           or else not Same (Data, F (Data, Outer, "namespace_event"), Closed_Event)
           or else not Bytes_Is (Data, F (Data, Outer, "outer_pidfd_wait"), "PIDFD_TERMINAL")
           or else not Bytes_Is (Data, F (Data, Outer, "actual_namespace_wait"), "PIDFD_TERMINAL")
           or else not R.Archive_Integer_Valid (Data, F (Data, Outer, "actual_launcher_wait"))
           or else not Bytes_Is (Data, F (Data, Fact, "helper_wait"), "PIDFD_TERMINAL")
           or else not P.Id_Hex (Data, F (Data, Fact, "closed_event"), F (Data, Outer_Event, "event_id"))
           or else not P.Property (Data, F (Data, Outer, "manager"), "Id", F (Data, Fact, "actual_unit"))
           or else not P.Property (Data, F (Data, Outer, "manager"), "ControlGroup", F (Data, Fact, "cgroup"))
           or else not P.Property (Data, F (Data, Outer, "manager"), "InvocationID", F (Data, Fact, "invocation"))
           or else not Manager_Pid_Matches (Data, F (Data, Outer, "manager"), To_Big_Integer (0))
         then return False; end if;
      end if;
      if Fully_Closed then
         return Text (Data, F (Data, Fact, "phase"), "NAMESPACE_CLOSED")
           and then Bytes_Is (Data, F (Data, Fact, "protocol"), "CLOSED_ECHILD");
      else
         return Text (Data, F (Data, Fact, "phase"), "NAMESPACE_HELD")
           and then Bytes_Is (Data, F (Data, Fact, "protocol"), "HELD")
           and then Is_None (Data, F (Data, Fact, "closed_event"));
      end if;
   end Owned_Protocol_Matches;
end Worldline.Scoped_Capture_History_Projection;

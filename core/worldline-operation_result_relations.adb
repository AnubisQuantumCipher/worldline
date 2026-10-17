with Attest.SHA256;
with Canonical_Artifacts;
with Interfaces;
with Worldline.Retained_Evidence_Replay;
with Worldline.Transaction_Relations;
with Worldline.Ordinary_Receipt_Policy;
with Worldline.Raw_JSON;
package body Worldline.Operation_Result_Relations with SPARK_Mode is
   package J renames Canonical_Artifacts;
   package SHA renames Attest.SHA256;
   package R renames A.R;
   package Q renames A.Q;
   package Replay renames Worldline.Retained_Evidence_Replay;
   package Ordinary renames Worldline.Ordinary_Receipt_Policy;
   use type E.Value_Kind; use type Q.Byte; use type E.Span;
   use type Worldline.Hash; use type Interfaces.Unsigned_64;
   use type Interfaces.Unsigned_32; use type A.Operation;
   use type J.Kind;
   use type E.Bytes;
   use type A.C.Reason;
   use type Replay.Replay_State; use type A.Command; use type A.Decision;
   function Whole (Data : E.Bytes) return E.Span is
     ((Data'First, Data'Length));
   function Field (Data : E.Bytes; Value : E.Span; Name : String) return E.Span is
     (O.Field (Data, Value, Name));
   function Name (Value : A.Identity_Field) return String is
   begin
      case Value is
         when A.Operation_Id => return "operation_id";
         when A.Request_Id => return "request_id";
         when A.Transaction => return "transaction";
         when A.Universe_Head => return "universe_head";
         when A.Instance => return "instance";
         when A.Root_Set => return "root_set";
         when A.Prime => return "prime";
         when A.Policy => return "policy";
         when A.Requirement => return "requirement";
         when A.Issuer => return "issuer";
         when A.Issuer_Head => return "issuer_head";
         when A.Grant_Id => return "grant_id";
         when A.Use_Id => return "use_id";
         when A.Reservation => return "reservation";
         when A.Resource_Head => return "resource_head";
         when A.Receipt_Genesis => return "receipt_genesis";
         when A.Receipt_Head => return "receipt_head";
         when A.Causal_Genesis => return "causal_genesis";
         when A.Causal_Head => return "causal_head";
         when A.Input_Snapshot => return "input_snapshot";
         when A.Kernel_Build => return "kernel_build";
         when A.Kernel_Library => return "kernel_library";
         when A.Kernel_Mapping => return "kernel_mapping";
         when A.Provenance => return "provenance";
         when A.Target => return "target";
         when A.Quarantine_Head => return "quarantine_head";
         when A.Original_Operation => return "original_operation";
      end case;
   end Name;
   function Action_Name (Value : A.Operation) return String is
   begin
      case Value is
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
   end Action_Name;
   function Text (Data : E.Bytes; Value : E.Span; Expected : String) return Boolean is
     (E.Text_Is (Data, E.Decode (Data, Value, E.Operation), Expected));
   function Null_Value (Data : E.Bytes; Value : E.Span) return Boolean is
     (Value.Length > 0 and then E.Decode (Data, Value, E.Operation).Form = E.Null_Value);
   function Bytes_Value (Data : E.Bytes; Value : E.Span) return E.Bytes is
      View : constant E.View := E.Decode (Data, Value, E.Operation);
   begin
      if View.Form /= E.Bytes_Value or else not E.Bytes_Valid (Data, View.Payload)
      then return (1 .. 0 => 0); end if;
      return E.Materialize (Data, View.Payload);
   end Bytes_Value;
   function Archive_Unhex (Data : E.Bytes; Value : E.Span) return E.Bytes is
      View : constant E.View := E.Decode (Data, Value, E.Operation);
      function Digit (Value : Q.Byte) return Natural is
        (if Value in Character'Pos ('0') .. Character'Pos ('9')
         then Natural (Value - Character'Pos ('0'))
         elsif Value in Character'Pos ('a') .. Character'Pos ('f')
         then Natural (Value - Character'Pos ('a')) + 10 else 16);
   begin
      if View.Form /= E.Text_Value or else not E.Bytes_Valid (Data, View.Payload)
      then return (1 .. 0 => 0); end if;
      declare
         Text : constant E.Bytes := E.Materialize (Data, View.Payload);
         Raw : E.Bytes (1 .. Text'Length / 2) := (others => 0);
      begin
         if Text'Length mod 2 /= 0 then return (1 .. 0 => 0); end if;
         if Raw'Length > 0 then
            for I in E.Count range 0 .. Raw'Length - 1 loop
               declare
                  High : constant Natural := Digit (Text (Text'First + 2 * I));
                  Low : constant Natural := Digit (Text (Text'First + 2 * I + 1));
               begin
                  if High > 15 or else Low > 15 then return (1 .. 0 => 0); end if;
                  Raw (1 + I) := Q.Byte (High * 16 + Low);
               end;
            end loop;
         end if;
         return Raw;
      end;
   end Archive_Unhex;
   function Record_Field (Data : E.Bytes; Value : E.Span; Key : String) return E.Span is
      View : constant E.View := E.Decode (Data, Value, E.Operation);
      N : constant E.Count := E.Array_Length (Data, View.Children);
   begin
      if View.Form = E.Object_Value then return Field (Data, Value, Key); end if;
      if View.Form /= E.Record_Value or else not O.Valid (Data, Value) then return (1, 0); end if;
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            declare
               Pair : constant E.View := E.Decode
                 (Data, E.Array_Element (Data, View.Children, I), E.Finalization);
            begin
               if Pair.Form = E.List_Value and then E.Array_Length (Data, Pair.Children) = 2
                 and then E.Text_Is (Data, E.Decode (Data,
                   E.Array_Element (Data, Pair.Children, 0), E.Finalization), Key)
               then return E.Array_Element (Data, Pair.Children, 1); end if;
            end;
         end loop;
      end if;
      return (1, 0);
   end Record_Field;
   function Hash_Of (Data : E.Bytes; Value : E.Span; Domain : String := "")
     return R.Optional_Digest is
      Ctx : SHA.Context := SHA.Initial;
      Buffer : Attest.Byte_Array (0 .. SHA.Block_Bytes - 1) := (others => 0);
      Fill : Natural := 0;
      procedure Feed (B : Q.Byte) is
      begin
         Buffer (Fill) := Attest.Byte (B); Fill := Fill + 1;
         if Fill = Buffer'Length then SHA.Update (Ctx, Buffer); Fill := 0; end if;
      end Feed;
   begin
      if not J.P.Valid (Data, Value) or else Interfaces.Unsigned_64 (Value.Length) >
        SHA.Max_Message_Bytes - Interfaces.Unsigned_64 (Domain'Length)
      then return (Present => False, Value => Worldline.Zero_Hash); end if;
      for C of Domain loop Feed (Q.Byte (Character'Pos (C))); end loop;
      if Value.Length > 0 then
         for I in E.Count range 0 .. Value.Length - 1 loop
            Feed (Data (Value.First + I));
            pragma Loop_Invariant (Fill < Buffer'Length);
         end loop;
      end if;
      if Fill > 0 then SHA.Update (Ctx, Buffer (0 .. Fill - 1)); end if;
      return (Present => True, Value => SHA.Final (Ctx));
   end Hash_Of;
   function Hex (Data : E.Bytes; Value : E.Span; Raw : E.Bytes) return Boolean is
      View : constant E.View := E.Decode (Data, Value, E.Operation);
      Hex_Digits : constant String := "0123456789abcdef";
   begin
      if View.Form /= E.Text_Value or else not E.Bytes_Valid (Data, View.Payload) then return False; end if;
      declare
         Encoded : constant E.Bytes := E.Materialize (Data, View.Payload);
      begin
         if Encoded'Length mod 2 /= 0 or else Encoded'Length / 2 /= Raw'Length then return False; end if;
         if Raw'Length > 0 then
            for I in E.Count range 0 .. Raw'Length - 1 loop
               if Encoded (Encoded'First + 2 * I) /= Character'Pos (Hex_Digits (Natural (Raw (Raw'First + I) / 16) + 1))
                 or else Encoded (Encoded'First + 2 * I + 1) /= Character'Pos (Hex_Digits (Natural (Raw (Raw'First + I) mod 16) + 1))
               then return False; end if;
            end loop;
         end if;
         return True;
      end;
   end Hex;
   function Digest_Matches (Data : E.Bytes; Value : E.Span; Id : R.Optional_Digest) return Boolean is
   begin
      if not Id.Present then return Null_Value (Data, Value); end if;
      declare
         Raw : E.Bytes (1 .. E.Count (Id.Value'Length)) := (others => 0);
      begin
         for I in Id.Value'Range loop Raw (1 + E.Count (I - Id.Value'First)) := Q.Byte (Id.Value (I)); end loop;
         return Hex (Data, Value, Raw);
      end;
   end Digest_Matches;
   function UID_Matches (Data : E.Bytes; Value : E.Span; Id : A.Optional_UID) return Boolean is
      View : constant E.View := E.Decode (Data, Value, E.Operation);
      Got : Interfaces.Unsigned_32 := 0;
   begin
      if not Id.Present then return Null_Value (Data, Value); end if;
      if View.Form /= E.Integer_Value or else View.Sign or else not E.Bytes_Valid (Data, View.Payload)
      then return False; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, View.Payload);
      begin
         if Raw'Length > 4 then return False; end if;
         if Raw'Length > 0 then
            for I in reverse E.Count range 0 .. Raw'Length - 1 loop
               Got := Interfaces.Shift_Left (Got, 8) or Interfaces.Unsigned_32 (Raw (Raw'First + I));
            end loop;
         end if;
         return Got = Id.Value;
      end;
   end UID_Matches;
   function Epoch_Matches (Data : E.Bytes; Value : E.Span; Id : R.Optional_Epoch) return Boolean is
      Negative : constant E.View := E.Decode (Data, Field (Data, Value, "negative"), E.Operation);
   begin
      if not Id.Present then return Null_Value (Data, Value); end if;
      if Negative.Form /= E.Boolean_Value or else Negative.Boolean_Bit /= Id.Value.Negative
        or else not Q.Span_Valid (Data, Id.Value) then return False; end if;
      if Id.Value.Length = 0 then
         return Hex (Data, Field (Data, Value, "raw"), (1 .. 0 => 0));
      end if;
      return Hex (Data, Field (Data, Value, "raw"),
        Data (Id.Value.First .. Id.Value.First + (Id.Value.Length - 1)));
   end Epoch_Matches;
   function Binding_Matches (Data : E.Bytes; Value : E.Span; Bound : A.Binding) return Boolean is
      Ids : constant E.Span := Field (Data, Value, "id");
   begin
      return O.Valid (Data, Value) and then Text (Data, Field (Data, Value, "action"), Action_Name (Bound.Action))
        and then (for all F in A.Identity_Field => Digest_Matches (Data, Field (Data, Ids, Name (F)), Bound.Id (F)))
        and then UID_Matches (Data, Field (Data, Value, "peer"), Bound.Peer)
        and then UID_Matches (Data, Field (Data, Value, "preparer"), Bound.Preparer)
        and then UID_Matches (Data, Field (Data, Value, "owner"), Bound.Owner)
        and then UID_Matches (Data, Field (Data, Value, "target_owner"), Bound.Target_Owner)
        and then Epoch_Matches (Data, Field (Data, Value, "policy_epoch"), Bound.Policy_Epoch)
        and then Epoch_Matches (Data, Field (Data, Value, "resource_epoch"), Bound.Resource_Epoch);
   end Binding_Matches;
   function Record_DTO_Matches (Data : E.Bytes; Value, DTO : E.Span) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Value.Length);
   function Record_DTO_Matches (Data : E.Bytes; Value, DTO : E.Span) return Boolean is
      Item : constant E.View := E.Decode (Data, Value, E.Operation);
      Projection : constant E.View := E.Decode (Data, DTO, E.Operation);
      N : constant E.Count := E.Array_Length (Data, Item.Children);
   begin
      if not O.Valid (Data, Value) or else not O.Valid (Data, DTO) then return False; end if;
      case Item.Form is
         when E.Null_Value | E.Text_Value => return O.Same_Encoding (Data, Value, DTO);
         when E.Bytes_Value =>
            return Projection.Form = E.Object_Value
              and then E.Array_Length (Data, Projection.Children) = 1
              and then Hex (Data, Field (Data, DTO, "bytes"), E.Materialize (Data, Item.Payload));
         when E.Integer_Value =>
            declare
               Negative : constant E.View := E.Decode (Data, Field (Data, DTO, "negative"), E.Operation);
            begin
               return Projection.Form = E.Object_Value
                 and then E.Array_Length (Data, Projection.Children) = 2
                 and then Negative.Form = E.Boolean_Value and then Negative.Boolean_Bit = Item.Sign
                 and then Hex (Data, Field (Data, DTO, "magnitude"), E.Materialize (Data, Item.Payload));
            end;
         when E.Record_Value =>
            if Projection.Form /= E.Object_Value
              or else N > E.Count'Last - 2
              or else E.Array_Length (Data, Projection.Children) /= N + 2
            then return False; end if;
            declare
               Name : constant E.View := E.Decode (Data, Field (Data, DTO, "type"), E.Operation);
               Schema : constant E.View := E.Decode (Data, Field (Data, DTO, "schema_version"), E.Operation);
            begin
               if Name.Form /= E.Text_Value or else Schema.Form /= E.Integer_Value
                 or else Schema.Sign or else E.Materialize (Data, Schema.Payload) /= (1 => 1)
                 or else E.Materialize (Data, Name.Payload) /= E.Materialize (Data, Item.Record_Name)
               then return False; end if;
            end;
            if N > 0 then
               for I in E.Count range 0 .. N - 1 loop
                  declare
                     Pair : constant E.View := E.Decode
                       (Data, E.Array_Element (Data, Item.Children, I), E.Finalization);
                     Key : constant E.View := E.Decode
                       (Data, E.Array_Element (Data, Pair.Children, 0), E.Finalization);
                     Raw_Key : constant E.Bytes := E.Materialize (Data, Key.Payload);
                     Child : constant E.Span := E.Array_Element (Data, Pair.Children, 1);
                     Key_Text : String (1 .. Natural (Raw_Key'Length));
                  begin
                     for K in Key_Text'Range loop
                        Key_Text (K) := Character'Val (Raw_Key (Raw_Key'First + E.Count (K - 1)));
                     end loop;
                     if Child.Length = 0 or else Child.Length >= Value.Length
                       or else not Record_DTO_Matches (Data, Child, Field (Data, DTO, Key_Text))
                     then return False; end if;
                  end;
               end loop;
            end if;
            return True;
         when others => return False;
      end case;
   end Record_DTO_Matches;
   function Snapshot_Source_Matches (Input, Current : E.Bytes; Original, Capture : E.Span) return Boolean is
      type Source_Field is (Operation_Field, Request_Field, Document_Field, Transaction_Field,
        Grant_Field, Use_Field, Subject_Field, Payload_Field, Provenance_Field, Native_Field,
        Facts_Field, Universe_Field, Issuer_Field, Intent_Field);
      function Name (F : Source_Field) return String is
      begin
         case F is
            when Operation_Field => return "operation";
            when Request_Field => return "request";
            when Document_Field => return "document";
            when Transaction_Field => return "transaction";
            when Grant_Field => return "grant";
            when Use_Field => return "use";
            when Subject_Field => return "subject";
            when Payload_Field => return "payload";
            when Provenance_Field => return "provenance";
            when Native_Field => return "native";
            when Facts_Field => return "facts";
            when Universe_Field => return "universe";
            when Issuer_Field => return "issuer";
            when Intent_Field => return "resource_intent";
         end case;
      end Name;
   begin
      if not O.Valid (Input, Original) or else not O.Valid (Current, Capture) then return False; end if;
      for F in Source_Field loop
         declare
            L : constant E.Span := Field (Input, Original, Name (F));
            R : constant E.Span := Field (Current, Capture, Name (F));
         begin
            if L.Length = 0 or else L.Length /= R.Length then return False; end if;
            for I in E.Count range 0 .. L.Length - 1 loop
               if Input (L.First + I) /= Current (R.First + I) then return False; end if;
            end loop;
         end;
      end loop;
      return True;
   end Snapshot_Source_Matches;
   function Capture_Source_Reference
     (Data : E.Bytes; Material : E.Span) return Boolean is
      Capture : constant E.Span := Field (Data, Material, "capture");
      Snapshot : constant E.Span := Field (Data, Material, "original_snapshot");
      Observation : constant E.Span := Field (Data, Material, "original_observation");
      Preimage : constant E.Span := Field (Data, Material, "reservation_preimage");
      Request : constant E.Span := Field (Data, Capture, "request");
      Binding : constant E.Span := Field (Data, Capture, "binding");
      Identifiers : constant E.Span := Field (Data, Binding, "id");
      Intent : constant E.Span := Field (Data, Capture, "resource_intent");
      Metadata : constant E.Span := Field (Data, Material, "requester");
      Resource : constant E.Span := Field (Data, Capture, "resource_material");
      Grants : constant E.View := E.Decode (Data, Field (Data, Snapshot, "grants"), E.Operation);
      Reserved : constant Replay.Operation_Replay_Result :=
        Replay.Reestablish_Reservation_Observation (Data, Observation);
   begin
      if not O.Valid (Data, Material)
        or else not O.Same_Encoding (Data, Capture, Field (Data, Material, "stored_capture"))
        or else not O.Same_Encoding (Data, Field (Data, Capture, "operation"), Field (Data, Identifiers, Name (A.Operation_Id)))
        or else not Digest_Matches (Data, Field (Data, Identifiers, Name (A.Request_Id)), Hash_Of (Data, Request))
        or else not Digest_Matches (Data, Field (Data, Identifiers, Name (A.Use_Id)), Hash_Of (Data, Field (Data, Capture, "use")))
        or else not O.Same_Encoding (Data, Binding, Field (Data, Snapshot, "binding"))
        or else not Replay.Reservation_Material_Matches (Data, Observation, Snapshot)
        or else Reserved.State /= Replay.Native_Redecided
        or else Reserved.Command /= A.Reserve_Use
        or else Reserved.Native_Status /= A.Reserved_New
        or else not O.Same_Encoding (Data, Field (Data, Preimage, "operation"), Field (Data, Capture, "operation"))
        or else not O.Same_Encoding (Data, Field (Data, Preimage, "request"), Request)
        or else not O.Same_Encoding (Data, Field (Data, Preimage, "binding"), Binding)
        or else not Digest_Matches (Data, Field (Data, Capture, "reservation_event"), Hash_Of (Data, Preimage))
        or else not O.Same_Encoding (Data, Binding, Field (Data, Metadata, "binding"))
        or else not O.Same_Encoding (Data, Request, Field (Data, Metadata, "originalRequest"))
        or else not O.Same_Encoding (Data, Field (Data, Capture, "reservation_event"), Field (Data, Metadata, "reservationEvent"))
        or else not O.Same_Encoding (Data, Field (Data, Binding, "peer"), Field (Data, Field (Data, Request, "peer"), "uid"))
        or else not O.Same_Encoding (Data, Field (Data, Binding, "target_owner"), Field (Data, Resource, "target_owner"))
        or else not O.Same_Encoding (Data, Field (Data, Identifiers, Name (A.Grant_Id)), Field (Data, Field (Data, Capture, "grant"), "id"))
        or else not O.Same_Encoding (Data, Field (Data, Identifiers, Name (A.Universe_Head)), Field (Data, Field (Data, Capture, "universe"), "event_head"))
        or else not O.Same_Encoding (Data, Field (Data, Identifiers, Name (A.Issuer_Head)), Field (Data, Field (Data, Capture, "issuer"), "event_head"))
        or else not Record_DTO_Matches (Data,
          Field (Data, Field (Data, Field (Data, Capture, "universe"), "record"), "policy_epoch"),
          Field (Data, Binding, "policy_epoch"))
        or else not Text (Data, Field (Data, Metadata, "schema"), "worldline.requester-operation-binding-v1")
        or else not O.Same_Encoding (Data, Field (Data, Binding, "action"),
          Field (Data, Field (Data, Capture, "document"), "op"))
        or else Grants.Form /= E.List_Value or else E.Array_Length (Data, Grants.Children) = 0
        or else not (for some I in E.Count range 0 .. E.Array_Length (Data, Grants.Children) - 1 =>
          O.Same_Encoding (Data, E.Array_Element (Data, Grants.Children, I), Field (Data, Capture, "grant")))
        or else not Record_DTO_Matches (Data, Intent, Field (Data, Resource, "request"))
        or else not Record_DTO_Matches (Data, Record_Field (Data, Intent, "scope"), Field (Data, Resource, "scope"))
        or else not Record_DTO_Matches (Data, Record_Field (Data, Intent, "bound"), Field (Data, Resource, "bound"))
      then return False; end if;
      declare
         Reservation : constant E.Bytes := Bytes_Value (Data, Record_Field (Data, Intent, "reservation"));
         Operation : constant E.Bytes := Bytes_Value (Data, Record_Field (Data, Intent, "operation_id"));
         Input : constant E.Bytes := Bytes_Value (Data, Field (Data, Capture, "input_snapshot_raw"));
         Native : constant E.Span := Field (Data, Capture, "native");
         Build : constant E.Bytes := Bytes_Value (Data, Field (Data, Native, "build_bytes"));
         Library : constant E.Bytes := Bytes_Value (Data, Field (Data, Native, "library_bytes"));
         Raw_Request : constant E.Bytes := Archive_Unhex (Data, Field (Data, Request, "rawRequest"));
      begin
         return Reservation'Length > 0 and then Operation'Length > 0
           and then Hex (Data, Field (Data, Field (Data, Binding, "id"), "reservation"), Reservation)
           and then Hex (Data, Field (Data, Capture, "operation"), Operation)
           and then Worldline.Raw_JSON.Raw_JSON_Operation_Matches
             (Raw_Request, Data, Whole (Raw_Request), Field (Data, Capture, "document"))
           and then O.Valid (Input, Whole (Input))
           and then Snapshot_Source_Matches (Input, Data, Whole (Input), Capture)
           and then Digest_Matches (Data, Field (Data, Identifiers, Name (A.Input_Snapshot)), Hash_Of (Input, Whole (Input)))
           and then Digest_Matches (Data, Field (Data, Identifiers, Name (A.Kernel_Build)), Hash_Of (Build, Whole (Build)))
           and then Digest_Matches (Data, Field (Data, Identifiers, Name (A.Kernel_Library)), Hash_Of (Library, Whole (Library)))
           and then Digest_Matches (Data, Field (Data, Identifiers, Name (A.Kernel_Mapping)), Hash_Of (Data, Native))
           and then Hex (Data, Field (Data, Identifiers, Name (A.Provenance)),
             Bytes_Value (Data, Record_Field (Data, Record_Field (Data, Intent, "bound"), "provenance")))
           and then Hex (Data, Field (Data, Identifiers, Name (A.Target)),
             Bytes_Value (Data, Record_Field (Data, Record_Field (Data, Intent, "bound"), "workload")));
      end;
   end Capture_Source_Reference;
   function Capture_Reference
     (Data : E.Bytes; Material : E.Span; Bound : A.Binding) return Boolean is
     (Capture_Source_Reference (Data, Material)
      and then Binding_Matches (Data, Field (Data, Field (Data, Material, "capture"), "binding"), Bound));
   function Capture_Matches
     (Data : E.Bytes; Material : E.Span; Bound : A.Binding) return Boolean is
     (Capture_Reference (Data, Material, Bound));
   function Material_View_Matches
     (Data : E.Bytes; Original, Projected : E.Span) return Boolean is
      type Store_Kind is (Receipt_Kind, Event_Kind);
   begin
      if not O.Valid (Data, Original) or else not O.Valid (Data, Projected) then return False; end if;
      for Kind in Store_Kind loop
         declare
            Key : constant String := (if Kind = Receipt_Kind then "receipts" else "events");
            Source : constant E.View := E.Decode (Data, Field (Data, Original, Key), E.Operation);
            View : constant E.View := E.Decode (Data, Field (Data, Projected, Key), E.Operation);
            N : constant E.Count := E.Array_Length (Data, Source.Children);
         begin
            if Source.Form /= E.List_Value or else View.Form /= E.List_Value
              or else N /= E.Array_Length (Data, View.Children)
              or else not Ordinary.History (Data, Field (Data, Projected, Key),
                (if Kind = Receipt_Kind then A.C.Receipt_Chain else A.C.Causal_Chain))
            then return False; end if;
            if N > 0 then
               for I in E.Count range 0 .. N - 1 loop
                  declare
                     Pair : constant E.View := E.Decode (Data, E.Array_Element (Data, Source.Children, I), E.Operation);
                     Item : constant E.Span := E.Array_Element (Data, View.Children, I);
                  begin
                     if Pair.Form /= E.Tuple_Value or else E.Array_Length (Data, Pair.Children) /= 2
                       or else not O.Same_Encoding (Data, E.Array_Element (Data, Pair.Children, 0), Field (Data, Item, "sql"))
                       or else not O.Same_Encoding (Data, E.Array_Element (Data, Pair.Children, 1), Field (Data, Item, "raw"))
                     then return False; end if;
                  end;
               end loop;
            end if;
         end;
      end loop;
      return True;
   end Material_View_Matches;
   function Material_Extends (Data : E.Bytes; Original, Current : E.Span) return Boolean is
      type Store_Kind is (Receipt_Kind, Event_Kind);
   begin
      for Kind in Store_Kind loop
         declare
            Key : constant String := (if Kind = Receipt_Kind then "receipts" else "events");
            Before : constant E.View := E.Decode (Data, Field (Data, Original, Key), E.Operation);
            After : constant E.View := E.Decode (Data, Field (Data, Current, Key), E.Operation);
            N : constant E.Count := E.Array_Length (Data, Before.Children);
         begin
            if Before.Form /= E.List_Value or else After.Form /= E.List_Value
              or else N > E.Array_Length (Data, After.Children) then return False; end if;
            if N > 0 then
               for I in E.Count range 0 .. N - 1 loop
                  if not O.Same_Encoding (Data, E.Array_Element (Data, Before.Children, I),
                    E.Array_Element (Data, After.Children, I)) then return False; end if;
               end loop;
            end if;
         end;
      end loop;
      return True;
   end Material_Extends;
   function Store_Source_Matches (Data : E.Bytes; Material : E.Span) return Boolean is
      Capture : constant E.Span := Field (Data, Material, "capture");
      Provenance : constant E.Span := Field (Data, Capture, "provenance");
      Original : constant E.Span := Field (Data, Material, "original_worldline_chains");
      Current : constant E.Span := Field (Data, Material, "current_store");
      Views : constant E.Span := Field (Data, Material, "store_views");
   begin
      return Material_View_Matches (Data, Provenance, Field (Data, Views, "provenance"))
        and then Material_View_Matches (Data, Original, Field (Data, Views, "original"))
        and then Material_View_Matches (Data, Current, Field (Data, Views, "current"))
        and then Material_Extends (Data, Provenance, Original)
        and then Material_Extends (Data, Original, Current);
   end Store_Source_Matches;
   function Result_Source_Reference
     (Data : E.Bytes; Material : E.Span) return Boolean is
      Capture : constant E.Span := Field (Data, Material, "capture");
      Binding : constant E.Span := Field (Data, Capture, "binding");
      Commit : constant Boolean :=
        Text (Data, Field (Data, Binding, "action"), Action_Name (A.Commit_Collapse))
        or else Text (Data, Field (Data, Binding, "action"), Action_Name (A.Commit_Transaction));
      Result : constant E.Span := Field (Data, Material, "result");
      Actual : constant E.Span := Field (Data, Result, "actual_transaction");
      Original : constant E.Span := Field (Data, Capture, "transaction");
      Chains : constant E.Span := Field (Data, Material, "original_worldline_chains");
      Stored : constant E.Span := Field (Data, Material, "stored_result");
   begin
      if not O.Valid (Data, Result)
        or else not O.Same_Encoding (Data, Chains, Field (Data, Result, "actual_store"))
        or else not Store_Source_Matches (Data, Material)
        or else Field (Data, Result, "result").Length = 0
        or else (if Null_Value (Data, Stored) then
          not Commit
          else not O.Same_Encoding (Data, Result, Stored))
      then return False; end if;
      if Null_Value (Data, Original) then return Null_Value (Data, Actual); end if;
      if not O.Same_Encoding (Data, Actual, Field (Data, Material, "current_transaction"))
      then return False; end if;
      if not O.Same_Encoding (Data, Field (Data, Original, "transactionId"), Field (Data, Actual, "transactionId"))
        or else not Digest_Matches (Data,
          Field (Data, Field (Data, Binding, "id"), Name (A.Transaction)),
          Hash_Of (Data, Field (Data, Actual, "transactionId")))
      then return False; end if;
      -- Commit effects name the exact original authorized staged tree and
      -- original evidence/cursors. Historical completion ignores today's grant.
      if Commit then
         return Transaction_Relations.Committed_Result_Matches
           (Data, Original, Actual, Field (Data, Result, "result"), Chains,
            Field (Data, Material, "commit_authority"));
      end if;
      return True;
   end Result_Source_Reference;
   function Result_Reference
     (Data : E.Bytes; Material : E.Span; Bound : A.Binding) return Boolean is
     (Result_Source_Reference (Data, Material)
      and then Binding_Matches (Data, Field (Data, Field (Data, Material, "capture"), "binding"), Bound));
   function Result_Matches
     (Data : E.Bytes; Material : E.Span; Bound : A.Binding) return Boolean is
     (Result_Reference (Data, Material, Bound));
   function JSON_Field (Data : E.Bytes; Value : E.Span; Name : String) return E.Span is
      Member : constant J.Member := J.Field (Data, Value, Name);
   begin
      if not Member.Found then return (1, 0); end if;
      return J.Part (Value, Member.Value.First, Member.Value.After);
   end JSON_Field;
   function JSON_Text (Data : E.Bytes; Value : E.Span; Text : String) return Boolean is
     (J.String_Is (Data, Value, J.Prefix (Data, Value, 0), Text));
   function Member_Count (Data : E.Bytes; Value : E.Span) return E.Count is
      Root : constant J.Node := J.Prefix (Data, Value, 0);
      Offset : E.Count := 1;
      Total : E.Count := 0;
   begin
      if not Root.Valid or else Root.Form /= J.Object_Value
        or else Root.After /= Value.Length or else Value.Length < 2
      then return 0; end if;
      while Offset < Value.Length - 1 loop
         pragma Loop_Invariant (Total <= Offset and then Offset < Value.Length);
         pragma Loop_Variant (Decreases => Value.Length - Offset);
         declare
            Key : constant J.Node := J.Prefix (Data, Value, Offset);
         begin
            if not Key.Valid or else Key.Form /= J.String_Value
              or else Key.After >= Value.Length - 1
              or else Data (Value.First + Key.After) /= Character'Pos (':')
            then return 0; end if;
            declare
               Child : constant J.Node := J.Prefix (Data, Value, Key.After + 1);
            begin
               if not Child.Valid or else Child.After <= Offset
                 or else Child.After > Value.Length - 1
               then return 0; end if;
               Total := Total + 1;
               if Child.After = Value.Length - 1 then return Total; end if;
               if Data (Value.First + Child.After) /= Character'Pos (',') then return 0; end if;
               Offset := Child.After + 1;
            end;
         end;
      end loop;
      return Total;
   end Member_Count;
   function JSON_Hex (JSON_Data : E.Bytes; Value : E.Span; Raw_Data : E.Bytes; Raw : E.Span) return Boolean is
      Hex_Digits : constant String := "0123456789abcdef";
   begin
      if not J.P.Valid (JSON_Data, Value) or else not J.P.Valid (Raw_Data, Raw)
        or else Value.Length < 2 or else (Value.Length - 2) mod 2 /= 0
        or else (Value.Length - 2) / 2 /= Raw.Length
        or else JSON_Data (Value.First) /= Character'Pos ('"')
        or else JSON_Data (Value.First + Value.Length - 1) /= Character'Pos ('"')
      then return False; end if;
      if Raw.Length > 0 then
         for I in E.Count range 0 .. Raw.Length - 1 loop
            if JSON_Data (Value.First + 1 + 2 * I) /= Character'Pos (Hex_Digits (Natural (Raw_Data (Raw.First + I) / 16) + 1))
              or else JSON_Data (Value.First + 2 + 2 * I) /= Character'Pos (Hex_Digits (Natural (Raw_Data (Raw.First + I) mod 16) + 1))
            then return False; end if;
         end loop;
      end if;
      return True;
   end JSON_Hex;
   function JSON_Same (L : E.Bytes; LS : E.Span; R : E.Bytes; RS : E.Span) return Boolean is
     (LS.Length > 0 and then LS.Length = RS.Length and then J.P.Valid (L, LS)
       and then J.P.Valid (R, RS) and then
       (for all I in E.Count range 0 .. LS.Length - 1 => L (LS.First + I) = R (RS.First + I)));
   function Historical_Payload_Matches
     (Data : E.Bytes; Source : E.Span; Payload : E.Bytes; Value : E.Span) return Boolean is
      Capture : constant E.Span := Field (Data, Source, "capture");
      Result : constant E.Span := Field (Data, Source, "result");
      Chains : constant E.Span := Field (Data, Source, "original_worldline_chains");
   begin
      return Capture_Source_Reference (Data, Source)
        and then Result_Source_Reference (Data, Source)
        and then JSON_Hex (Payload, JSON_Field (Payload, Value, "originalCapture"), Data, Capture)
        and then JSON_Hex (Payload, JSON_Field (Payload, Value, "actualResult"), Data, Result)
        and then JSON_Hex (Payload, JSON_Field (Payload, Value, "originalWorldlineChains"), Data, Chains)
        and then J.Operation_Archive_JSON_Matches
          (Payload, Data, JSON_Field (Payload, Value, "operation"), Field (Data, Capture, "operation"))
        and then J.Operation_Archive_JSON_Matches
          (Payload, Data, JSON_Field (Payload, Value, "requester"), Field (Data, Source, "requester"));
   end Historical_Payload_Matches;
   function Payloads_Reference
     (Data : E.Bytes; Material : E.Span; Bound : A.Binding; Facts : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Boolean is
      Receipt_View : constant E.View := E.Decode (Data, Field (Data, Material, "receipt_payloads"), E.Operation);
      Event_View : constant E.View := E.Decode (Data, Field (Data, Material, "event_payloads"), E.Operation);
      Historical : constant E.View := E.Decode (Data, Field (Data, Material, "historical_sources"), E.Operation);
      Historical_Index : E.Count := 0;
      Capture : constant E.Span := Field (Data, Material, "capture");
      Result : constant E.Span := Field (Data, Material, "result");
      Chains : constant E.Span := Field (Data, Material, "original_worldline_chains");
      Requester : constant E.Span := Field (Data, Material, "requester");
      Selected : Boolean := False;
   begin
      if Receipt_View.Form /= E.List_Value or else Event_View.Form /= E.List_Value
        or else Receipts'Length = 0 or else Receipts'Length /= Events'Length
        or else E.Array_Length (Data, Receipt_View.Children) /= Receipts'Length
        or else E.Array_Length (Data, Event_View.Children) /= Events'Length
        or else Historical.Form /= E.List_Value
        or else E.Array_Length (Data, Historical.Children) /= Receipts'Length - 1
      then return False; end if;
      for I in E.Count range 0 .. Receipts'Length - 1 loop
         pragma Loop_Invariant (Historical_Index = (if Selected then I - 1 else I));
         declare
            Receipt : constant E.Bytes := Bytes_Value (Data, E.Array_Element (Data, Receipt_View.Children, I));
            Event : constant E.Bytes := Bytes_Value (Data, E.Array_Element (Data, Event_View.Children, I));
            RS : constant E.Span := Whole (Receipt); ES : constant E.Span := Whole (Event);
            RR : constant A.C.Chain_Row := Receipts (Receipts'First + I);
            ER : constant A.C.Chain_Row := Events (Events'First + I);
            Operation : constant E.Span := JSON_Field (Receipt, RS, "operation");
         begin
            if not J.Canonical (Receipt, RS) or else not J.Canonical (Event, ES)
              or else not JSON_Text (Receipt, JSON_Field (Receipt, RS, "schema"), "worldline.protected-operation-use-receipt-v1")
              or else not JSON_Text (Event, JSON_Field (Event, ES, "schema"), "worldline.protected-operation-causal-v1")
              or else Member_Count (Receipt, RS) /= 6
              or else Member_Count (Event, ES) /= 7
              or else Member_Count (Receipt, JSON_Field (Receipt, RS, "requester")) /= 4
              or else not R.Same (Hash_Of (Receipt, RS, "worldline-operation-use-receipt-v1" & ASCII.NUL), RR.Actual_Payload_Root)
              or else not R.Same (Hash_Of (Event, ES, "worldline-operation-causal-v1" & ASCII.NUL), ER.Actual_Payload_Root)
              or else not JSON_Same (Receipt, Operation, Event, JSON_Field (Event, ES, "operation"))
              or else not JSON_Same (Receipt, JSON_Field (Receipt, RS, "requester"), Event, JSON_Field (Event, ES, "requester"))
              or else not JSON_Same (Receipt, JSON_Field (Receipt, RS, "originalCapture"), Event, JSON_Field (Event, ES, "originalCapture"))
              or else not JSON_Same (Receipt, JSON_Field (Receipt, RS, "actualResult"), Event, JSON_Field (Event, ES, "actualResult"))
              or else not JSON_Same (Receipt, JSON_Field (Receipt, RS, "originalWorldlineChains"), Event, JSON_Field (Event, ES, "originalWorldlineChains"))
            then return False; end if;
            if I > 0 then
               for Earlier in E.Count range 0 .. I - 1 loop
                  declare
                     Prior : constant E.Bytes := Bytes_Value
                       (Data, E.Array_Element (Data, Receipt_View.Children, Earlier));
                  begin
                     if JSON_Same (Receipt, Operation, Prior,
                       JSON_Field (Prior, Whole (Prior), "operation"))
                     then return False; end if;
                  end;
               end loop;
            end if;
            declare
               Head : E.Bytes (1 .. 32) := (others => 0);
            begin
               for K in RR.Stored_Head.Value'Range loop Head (1 + E.Count (K - RR.Stored_Head.Value'First)) := Q.Byte (RR.Stored_Head.Value (K)); end loop;
               if not RR.Stored_Head.Present or else not JSON_Hex (Event, JSON_Field (Event, ES, "receipt_head"), Head, Whole (Head)) then return False; end if;
            end;
            -- Search the complete roster by its actual operation. Replaying an
            -- old exact result after another operation appended is not last-row
            -- authority and must not charge or append a second capability use.
            declare
               Id : E.Bytes (1 .. 32) := (others => 0);
            begin
               for K in Bound.Id (A.Operation_Id).Value'Range loop Id (1 + E.Count (K - Bound.Id (A.Operation_Id).Value'First)) := Q.Byte (Bound.Id (A.Operation_Id).Value (K)); end loop;
               if JSON_Hex (Receipt, Operation, Id, Whole (Id)) then
                  if Selected or else not R.Same (Facts.Actual_Receipt_Root, RR.Actual_Payload_Root)
                    or else not R.Same (Facts.Actual_Causal_Root, ER.Actual_Payload_Root)
                    or else not JSON_Hex (Receipt, JSON_Field (Receipt, RS, "originalCapture"), Data, Capture)
                    or else not JSON_Hex (Receipt, JSON_Field (Receipt, RS, "actualResult"), Data, Result)
                    or else not JSON_Hex (Receipt, JSON_Field (Receipt, RS, "originalWorldlineChains"), Data, Chains)
                    or else not J.Operation_Archive_JSON_Matches
                      (Receipt, Data, JSON_Field (Receipt, RS, "requester"), Requester)
                  then return False; end if;
                  declare
                     Intents : constant E.View := E.Decode
                       (Data, Field (Data, Material, "original_intents"), E.Operation);
                     N : constant E.Count := E.Array_Length (Data, Intents.Children);
                     Seen_Receipt, Seen_Event : Boolean := False;
                  begin
                     if Intents.Form /= E.List_Value then return False; end if;
                     if N > 0 then
                        for K in E.Count range 0 .. N - 1 loop
                           declare
                              Intent : constant E.Span := E.Array_Element (Data, Intents.Children, K);
                           begin
                              if not Text (Data, Field (Data, Intent, "name"), "OPERATION_CHAIN_INTENT")
                                or else not Digest_Matches (Data, Field (Data, Intent, "operation"), Bound.Id (A.Operation_Id))
                              then return False; end if;
                              if Text (Data, Field (Data, Intent, "kind"), "operation_receipts") then
                                 if Seen_Receipt or else not Hex (Data, Field (Data, Intent, "payload"), Receipt)
                                   or else not Digest_Matches (Data, Field (Data, Intent, "root"), RR.Actual_Payload_Root)
                                   or else not Digest_Matches (Data, Field (Data, Intent, "previous"), RR.Previous)
                                   or else not Digest_Matches (Data, Field (Data, Intent, "head"), RR.Stored_Head)
                                 then return False; end if;
                                 Seen_Receipt := True;
                              elsif Text (Data, Field (Data, Intent, "kind"), "operation_events") then
                                 if Seen_Event or else not Hex (Data, Field (Data, Intent, "payload"), Event)
                                   or else not Digest_Matches (Data, Field (Data, Intent, "root"), ER.Actual_Payload_Root)
                                   or else not Digest_Matches (Data, Field (Data, Intent, "previous"), ER.Previous)
                                   or else not Digest_Matches (Data, Field (Data, Intent, "head"), ER.Stored_Head)
                                 then return False; end if;
                                 Seen_Event := True;
                              else return False;
                              end if;
                           end;
                        end loop;
                     end if;
                  end;
                  Selected := True;
               else
                  if Historical_Index >= E.Array_Length (Data, Historical.Children)
                    or else not Historical_Payload_Matches
                      (Data, E.Array_Element (Data, Historical.Children, Historical_Index), Receipt, RS)
                  then return False; end if;
                  Historical_Index := Historical_Index + 1;
               end if;
            end;
         end;
      end loop;
      return Selected and then Historical_Index = E.Array_Length (Data, Historical.Children);
   end Payloads_Reference;
   function Payloads_Match
     (Data : E.Bytes; Material : E.Span; Bound : A.Binding; Facts : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Boolean is
     (Payloads_Reference (Data, Material, Bound, Facts, Receipts, Events));
   function Assessment_Reference
     (Data : E.Bytes; Bound : A.Binding; Facts : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Reason is
      Material : constant E.Span := Facts.Effect_Material;
      Result : constant E.Span := Field (Data, Material, "result");
      Chains : constant E.Span := Field (Data, Material, "original_worldline_chains");
   begin
      if not A.Same (Data, Bound, Facts.Effect_Binding)
        or else not Capture_Matches (Data, Material, Bound)
      then return Original_Capture_Refused; end if;
      if not O.Same_Encoding (Data, Chains, Field (Data, Result, "actual_store"))
        or else not Store_Source_Matches (Data, Material)
      then return Canonical_Material_Changed; end if;
      if not Result_Matches (Data, Material, Bound) then return Transaction_Result_Refused; end if;
      if not Payloads_Match (Data, Material, Bound, Facts, Receipts, Events)
      then return Same_Use_Record_Changed; end if;
      if not (R.Same (Bound.Id (A.Receipt_Head), Bound.Id (A.Receipt_Genesis))
          or else (for some I in Receipts'Range => R.Same (Receipts (I).Stored_Head, Bound.Id (A.Receipt_Head))))
        or else not (R.Same (Bound.Id (A.Causal_Head), Bound.Id (A.Causal_Genesis))
          or else (for some I in Events'Range => R.Same (Events (I).Stored_Head, Bound.Id (A.Causal_Head))))
        or else A.C.Replay (A.C.Receipt_Chain, Receipts, Bound.Id (A.Receipt_Genesis),
          Facts.Effect_Binding.Id (A.Receipt_Genesis), Facts.Witnessed_Receipt_Head).Disposition /= A.C.Ready
        or else A.C.Replay (A.C.Causal_Chain, Events, Bound.Id (A.Causal_Genesis),
          Facts.Effect_Binding.Id (A.Causal_Genesis), Facts.Witnessed_Causal_Head).Disposition /= A.C.Ready
      then return Original_Full_Chain_Refused; end if;
      return Ready;
   end Assessment_Reference;
   function Assess
     (Data : E.Bytes; Bound : A.Binding; Facts : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Reason is
     (Assessment_Reference (Data, Bound, Facts, Receipts, Events));
   function Matches
     (Data : E.Bytes; Bound : A.Binding; Facts : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Boolean is
     (Capture_Matches (Data, Facts.Effect_Material, Bound)
      and then Result_Matches (Data, Facts.Effect_Material, Bound)
      and then Payloads_Match (Data, Facts.Effect_Material, Bound, Facts, Receipts, Events));
end Worldline.Operation_Result_Relations;

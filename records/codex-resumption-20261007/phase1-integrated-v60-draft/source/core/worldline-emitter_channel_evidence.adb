with SPARK.Big_Integers;
with Worldline.Custody_V2_Requester_Join;
with Worldline.Custody_V2_Root_Evidence;
with Worldline.Custody_V2_Root_Values;
with Worldline.Custody_V2_Archive_Projection;
with Worldline.Retained_Evidence_Replay;
with Worldline.Scoped_Capture_Projection;
with Worldline.Scoped_Capture_Namespace_Projection;
with Worldline.Emitter_Ordinal;
package body Worldline.Emitter_Channel_Evidence with SPARK_Mode is
   package V renames I.V;
   package S renames V.S;
   package A renames S.A;
   package D renames SE.D;
   package RJ renames Worldline.Custody_V2_Requester_Join;
   package RE renames Worldline.Custody_V2_Root_Evidence;
   package RV renames Worldline.Custody_V2_Root_Values;
   package AP renames Worldline.Custody_V2_Archive_Projection;
   package R renames Worldline.Retained_Evidence_Replay;
   package CP renames Worldline.Scoped_Capture_Projection;
   package NP renames Worldline.Scoped_Capture_Namespace_Projection;
   package O renames Worldline.Emitter_Ordinal;
   use SPARK.Big_Integers;
   use type E.Count;
   use type E.Bytes;
   use type E.Value_Kind;
   use type Q.Byte;
   use type Q.Ordering;
   use type I.Original_Format;
   use type D.Decode_Status;
   use type M.Subject_Kind;
   use type M.Actor;
   use type M.Event_Kind;
   use type M.Transfer_Mode;
   use type R.Replay_State;
   use type R.J.Admission_Mode;
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     renames R.Archive_Field;
   function SF (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     renames S.Field;
   function Raw_Same (Left_Data, Right_Data : E.Bytes; Left, Right : E.Span)
      return Boolean is
     (E.C.P.Valid (Left_Data, Left) and then E.C.P.Valid (Right_Data, Right) and then
      Left.Length = Right.Length and then
      (for all K in E.Count range 1 .. Left.Length =>
         Left_Data (Left.First + K - 1) = Right_Data (Right.First + K - 1)));
   -- Full original tree equality across independent borrowed arenas and the two
   -- original encoders. Object order, record names and float bits are retained.
   function Same_Value (LD, RD : E.Bytes; Left, Right : E.Span) return Boolean
     with Subprogram_Variant => (Decreases => Left.Length)
   is
      L : constant E.View := E.Decode (LD, Left, E.Operation);
      H : constant E.View := E.Decode (RD, Right, E.Operation);
      function Payload (LV, HV : E.Byte_View) return Boolean is
        (E.Bytes_Valid (LD, LV) and then E.Bytes_Valid (RD, HV) and then
         E.Materialize (LD, LV) = E.Materialize (RD, HV));
   begin
      if not A.Valid (LD, Left) or else not A.Valid (RD, Right) or else
         L.Form /= H.Form then return False; end if;
      case L.Form is
         when E.Null_Value => return True;
         when E.Boolean_Value => return L.Boolean_Bit = H.Boolean_Bit;
         when E.Integer_Value =>
            return L.Sign = H.Sign and then E.Bytes_Valid (LD, L.Payload) and then
              E.Bytes_Valid (RD, H.Payload) and then
              O.Same_Value (E.Materialize (LD, L.Payload), E.Materialize (RD, H.Payload));
         when E.Text_Value | E.Bytes_Value | E.Float_Value => return Payload (L.Payload, H.Payload);
         when E.World_State_Value => return Payload (L.Payload, H.Payload);
         when E.List_Value | E.Tuple_Value | E.Object_Value | E.Record_Value =>
            if E.Array_Length (LD, L.Children) /= E.Array_Length (RD, H.Children) or else
               (L.Form = E.Record_Value and then
                not (Payload (L.Module_Name, H.Module_Name) and then Payload (L.Record_Name, H.Record_Name)))
            then return False; end if;
            for K in E.Count range 1 .. E.Array_Length (LD, L.Children) loop
               pragma Loop_Variant (Increases => K);
               declare
                  LC : constant E.Span := E.Array_Element (LD, L.Children, K - 1);
                  RC : constant E.Span := E.Array_Element (RD, H.Children, K - 1);
               begin
                  if LC.Length >= Left.Length then return False; end if;
                  if L.Form in E.Object_Value | E.Record_Value then
                     declare
                        LP : constant E.View := E.Decode (LD, LC, E.Finalization);
                        RP : constant E.View := E.Decode (RD, RC, E.Finalization);
                     begin
                        if LP.Form /= E.List_Value or else RP.Form /= E.List_Value or else
                           E.Array_Length (LD, LP.Children) /= 2 or else E.Array_Length (RD, RP.Children) /= 2
                        then return False; end if;
                        if L.Form = E.Object_Value then
                           if not Same_Value (LD, RD, E.Array_Element (LD, LP.Children, 0),
                             E.Array_Element (RD, RP.Children, 0)) then return False; end if;
                        else
                           declare
                              LN : constant E.View := E.Decode (LD, E.Array_Element (LD, LP.Children, 0), E.Finalization);
                              RN : constant E.View := E.Decode (RD, E.Array_Element (RD, RP.Children, 0), E.Finalization);
                           begin
                              if LN.Form /= E.Text_Value or else RN.Form /= E.Text_Value or else
                                 not Payload (LN.Payload, RN.Payload) then return False; end if;
                           end;
                        end if;
                        if not Same_Value (LD, RD, E.Array_Element (LD, LP.Children, 1),
                          E.Array_Element (RD, RP.Children, 1)) then return False; end if;
                     end;
                  elsif not Same_Value (LD, RD, LC, RC) then return False;
                  end if;
               end;
            end loop;
            return True;
         when E.Invalid => return False;
      end case;
   end Same_Value;
   function Integer_Is (Data : E.Bytes; Item : E.Span; Number : Integer) return Boolean is
     (R.Archive_Integer_Valid (Data, Item) and then CP.Number (Data, Item) = To_Big_Integer (Number));
   function Nonnegative (Data : E.Bytes; Item : E.Span) return Boolean is
     (R.Archive_Integer_Valid (Data, Item) and then not R.Archive_Integer_Negative (Data, Item));
   function Count_Number (Count : E.Count) return Valid_Big_Integer is
      Rest : E.Count := Count;
      Place : Valid_Big_Integer := To_Big_Integer (1);
      Result : Valid_Big_Integer := To_Big_Integer (0);
   begin
      while Rest > 0 loop
         pragma Loop_Variant (Decreases => Rest);
         Result := Result + To_Big_Integer (Integer (Rest mod 256)) * Place;
         Place := Place * 256;
         Rest := Rest / 256;
      end loop;
      return Result;
   end Count_Number;
   function Decimal (Data : E.Bytes; Item : E.Span) return Boolean is
   begin
      if not RV.Valid_Text (Data, Item) then return False; end if;
      declare Text : constant E.Bytes := RV.Text_Value (Data, Item); begin
         return Text'Length > 0 and then (Text'Length = 1 or else Text (Text'First) /= 48) and then
           (for all B of Text => B in 48 .. 57);
      end;
   end Decimal;
   function Decimal_Quantity (Data : E.Bytes; Item : E.Span; Magnitude : E.Bytes) return Boolean is
     (RV.Valid_Text (Data, Item) and then O.Canonical_Decimal_Matches (RV.Text_Value (Data, Item), Magnitude));
   function Quantity (Context_Data, Data : E.Bytes; Item : E.Span; Expected : Q.Quantity) return Boolean is
     (Q.Span_Valid (Context_Data, Expected) and then not Q.Is_Negative (Context_Data, Expected) and then
      R.Archive_Bytes_Valid (Data, Item) and then
      O.Same_Value (R.Archive_Bytes (Data, Item),
        Context_Data (Expected.First .. Expected.First + Expected.Length - 1)));
   function Quantity_Within (Context_Data, Data : E.Bytes; Item : E.Span; Expected : Q.Quantity)
      return Boolean is
   begin
      if not Q.Span_Valid (Context_Data, Expected) or else Q.Is_Negative (Context_Data, Expected) or else
         not R.Archive_Bytes_Valid (Data, Item) then return False; end if;
      declare
         Left : constant E.Bytes := R.Archive_Bytes (Data, Item);
         L : E.Count := Left'Length;
         H : E.Count := Expected.Length;
      begin
         while L > 0 and then Left (Left'First + L - 1) = 0 loop
            pragma Loop_Variant (Decreases => L);
            L := L - 1;
         end loop;
         while H > 0 and then Context_Data (Expected.First + H - 1) = 0 loop
            pragma Loop_Variant (Decreases => H);
            H := H - 1;
         end loop;
         if L /= H then return L < H; end if;
         while L > 0 loop
            pragma Loop_Variant (Decreases => L);
            if Left (Left'First + L - 1) /= Context_Data (Expected.First + L - 1) then
               return Left (Left'First + L - 1) < Context_Data (Expected.First + L - 1);
            end if;
            L := L - 1;
         end loop;
         return True;
      end;
   end Quantity_Within;
   function Stable_Identity (LD, RD : E.Bytes; Left, Right : E.Span) return Boolean is
      function Member (Name : String) return Boolean is
        (Same_Value (LD, RD, F (LD, Left, Name), F (RD, Right, Name)));
   begin
      return Member ("device") and then Member ("inode") and then Member ("mode") and then
        Member ("uid") and then Member ("gid") and then
        R.Archive_Bytes_Valid (LD, F (LD, Left, "fdinfo")) and then
        R.Archive_Bytes_Valid (RD, F (RD, Right, "fdinfo"));
   end Stable_Identity;
   function Socket_Origin (LD, RD : E.Bytes; Current, Original : E.Span) return Boolean is
      function Call (Name : String) return Boolean is
         Now : constant E.Span := F (LD, Current, Name);
         Old : constant E.Span := F (RD, Original, Name);
      begin
         return Same_Value (LD, RD, F (LD, Now, "result"), F (RD, Old, "result")) and then
           Same_Value (LD, RD, F (LD, Now, "errno"), F (RD, Old, "errno")) and then
           Same_Value (LD, RD, F (LD, Now, "raw"), F (RD, Old, "raw"));
      end Call;
   begin
      return A.Valid (LD, Current) and then A.Valid (RD, Original) and then
        Stable_Identity (LD, RD, F (LD, F (LD, Current, "fstat"), "identity"),
          F (RD, F (RD, Original, "fstat"), "identity")) and then
        Call ("peercred") and then Call ("domain") and then Call ("type") and then Call ("peername");
   end Socket_Origin;
   function Enrolled_Endpoint
     (Native_Data, Data : E.Bytes; Inventory, Role, Channel, Source : E.Span;
      Duplicate : E.Span := (1, 0)) return Boolean is
      Current : constant E.Span := F (Native_Data, Role, "current");
      FD : constant E.Span := F (Data, Channel, "fd");
      Identity : constant E.Span := F (Data, F (Data, Channel, "fstat"), "identity");
      Role_FD : constant E.Span := F (Native_Data, Role,
        (if R.Archive_Is_None (Native_Data, F (Native_Data, Role, "worker_fd")) then "front_fd" else "worker_fd"));
      Actor : constant E.Span := F (Native_Data, Inventory, "current_actor");
      function OFD (KD : E.Bytes; Item, Old_FD, New_FD : E.Span) return Boolean is
         Args : constant E.Span := F (KD, Item, "args");
      begin
         return R.Archive_Text_Is (KD, F (KD, Item, "call"), "kcmp") and then
           Integer_Is (KD, F (KD, Item, "result"), 0) and then
           Integer_Is (KD, F (KD, Item, "errno"), 0) and then
           Integer_Is (KD, F (KD, Args, "type"), 0) and then
           Same_Value (KD, KD, F (KD, Args, "idx1"), Old_FD) and then
           Same_Value (KD, KD, F (KD, Args, "idx2"), New_FD) and then
           Same_Value (KD, Native_Data, F (KD, Args, "pid1"), F (Native_Data, Actor, "pid")) and then
           Same_Value (KD, Native_Data, F (KD, Args, "pid2"), F (Native_Data, Actor, "pid")) and then
           Same_Value (KD, Data, F (KD, Item, "source"), Source);
      end OFD;
   begin
      -- Every branch retains the complete socket/OFD identity and native role
      -- origin. FD numbers are local aliases, not identities across dup/SCM.
      if not Stable_Identity (Data, Native_Data, Identity, Current) or else
         not Socket_Origin (Data, Native_Data, Channel, F (Native_Data, Role, "socket")) or else
         not Same_Value (Native_Data, Data, F (Native_Data, Inventory, "current_source"), Source)
      then return False; end if;
      if Same_Value (Data, Native_Data, FD, Role_FD) and then
         Same_Value (Data, Native_Data, FD, F (Native_Data, F (Native_Data, Role, "socket"), "fd"))
      then return True; end if;
      if Duplicate.Length > 0 then
         declare
            Receipt : constant E.Span := F (Data, Duplicate, "receipt");
            Old_FD : constant E.Span := F (Data, F (Data, Receipt, "args"), "fd");
            Before_List : constant E.Span := F (Data, Receipt, "before");
            Found : Boolean := False;
         begin
            if not R.Archive_Text_Is (Data, F (Data, Receipt, "call"), "dup") or else
               not Same_Value (Data, Data, F (Data, Receipt, "result"), FD) or else
               not Same_Value (Data, Data, F (Data, Receipt, "api_result"), FD) or else
               not Integer_Is (Data, F (Data, Receipt, "errno"), 0) or else
               not Same_Value (Data, Data, F (Data, Receipt, "source"), Source) or else
               not Stable_Identity (Data, Data, F (Data, Receipt, "identity"), Identity) or else
               not Same_Value (Data, Data, F (Data, Receipt, "proc_fdinfo"), F (Data, F (Data, Receipt, "identity"), "fdinfo")) or else
               not OFD (Data, F (Data, Receipt, "ofd"), Old_FD, FD) or else
               not OFD (Data, F (Data, Duplicate, "ofd"), Old_FD, FD) or else
               not R.Archive_Is_Sequence (Data, Before_List) then return False; end if;
            for K in E.Count range 1 .. R.Archive_Length (Data, Before_List) loop
               pragma Loop_Variant (Increases => K);
               declare Item : constant E.Span := R.Archive_Index (Data, Before_List, K - 1); begin
                  if Same_Value (Data, Data, F (Data, Item, "fd"), Old_FD) and then
                     Stable_Identity (Data, Native_Data, F (Data, Item, "identity"), Current) and then
                     Same_Value (Data, Data, F (Data, Item, "fdinfo"), F (Data, F (Data, Item, "identity"), "fdinfo"))
                  then Found := True; end if;
               end;
            end loop;
            return Found;
         end;
      end if;
      -- The native owner validates complete reconstruction/evolution,
      -- dup/KCMP/SCM and same-holder actor chains back to the real service
      -- registry. A reverse refreshed observation FD is not the service FD.
      return CP.Scoped_Descriptor_Alias_Matches (Native_Data, Data, Inventory,
        F (Native_Data, Role, "role"), FD, Identity);
   end Enrolled_Endpoint;
   function Text_Reference (Context_Data, Data : E.Bytes; Item, Expected : E.Span) return Boolean is
   begin
      if not RV.Valid_Text (Data, Item) or else not E.C.P.Valid (Context_Data, Expected) then return False; end if;
      declare Text : constant E.Bytes := RV.Text_Value (Data, Item); begin
         return Raw_Same (Text, Context_Data, (Text'First, Text'Length), Expected);
      end;
   end Text_Reference;
   function Object_Size (Data : E.Bytes; Item : E.Span; Size : E.Count) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return A.Valid (Data, Item) and then View.Form = E.Object_Value and then
        E.Array_Length (Data, View.Children) = Size;
   end Object_Size;
   function Scoped_Source (Value : I.Parsed_Input; Event_Index : Q.Byte_Count) return E.Span is
     (if Event_Index in Value.Events'Range then
        SF (Value.Arena, SF (Value.Arena, Value.Events (Event_Index).Record_Archive, "x5"), "source_identity")
      else (1, 0));
   function Facts (Value : I.Parsed_Input; Event_Index : Q.Byte_Count) return E.Span is
     (if Event_Index in Value.Events'Range then
        SF (Value.Arena, SF (Value.Arena, Value.Events (Event_Index).Record_Archive, "x5"), "subject_evidence")
      else (1, 0));
   function Request (Value : I.Parsed_Input; Index : Q.Byte_Count) return E.Span is
     (SF (Value.Arena, Facts (Value, Index), "request"));
   function Scope_Domain
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subject : P.Optional_Subject; Data : E.Bytes; Scope : E.Span) return Boolean is
   begin
      if Index not in Value.Events'Range or else not Subject.Present or else
         Subject.Value.Kind /= M.Request or else not Object_Size (Data, Scope, 6) or else
         not Quantity (Value.Arena, Data, F (Data, Scope, "generation"), Before.Generation) or else
         not Quantity (Value.Arena, Data, F (Data, Scope, "subgeneration"), Subject.Value.Subgeneration) or else
         not Quantity_Within (Value.Arena, Data, F (Data, Scope, "reattach_epoch"), Before.Reattach_Epoch) or else
         not Text_Reference (Value.Arena, Data, F (Data, Scope, "operation"), Value.Events (Index).Operation) or else
         not Text_Reference (Value.Arena, Data, F (Data, Scope, "request"), Value.Events (Index).Subject)
      then return False; end if;
      if not Before.Operation.Present then return R.Archive_Is_None (Data, F (Data, Scope, "root_operation")); end if;
      for K in Value.Events'First .. Index - 1 loop
         pragma Loop_Variant (Increases => K);
         declare Event : constant D.Decoded_Event := D.Decode (Value.Arena, Value.Events (K)); begin
            if Event.Status = D.Decoded and then Event.Value.Kind_Of_Subject = M.Root and then
               M.L.Optional_Same (Value.Arena, Event.Value.Operation, Before.Operation) and then
               Q.Compare (Value.Arena, Event.Value.Generation, Before.Generation) = Q.Equal and then
               Text_Reference (Value.Arena, Data, F (Data, Scope, "root_operation"), Value.Events (K).Operation)
            then return True; end if;
         end;
      end loop;
      return False;
   end Scope_Domain;
   function Native_Origin
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Data : E.Bytes; List, Source, Channel : E.Span; Duplicate : E.Span := (1, 0))
      return Boolean is
      Found : Boolean := False;
   begin
      if not A.Valid (Data, List) or else E.Decode (Data, List, E.Operation).Form /= E.Tuple_Value or else
         R.Archive_Length (Data, List) = 0 then return False; end if;
      for K in E.Count range 1 .. R.Archive_Length (Data, List) loop
         pragma Loop_Variant (Increases => K);
         declare
            Item : constant E.Span := R.Archive_Index (Data, List, K - 1);
            Obs : constant E.Span := F (Data, Item, "observation");
            Material : constant E.Span := F (Data, Item, "material");
            Provenance : constant E.Span := F (Data, Item, "provenance");
            Inventory : constant E.Span := F (Data, F (Data, Provenance, "owned_descriptor_roster"), "inventory");
         begin
            if R.Archive_Text_Is (Data, F (Data, Item, "role"), "root-admission") or else
               R.Archive_Text_Is (Data, F (Data, Item, "role"), "root-execution") then
               declare Native : constant R.Root_Replay_Result := R.Reestablish_Root_Observation (Data, Obs); begin
                  if Native.State /= R.Native_Redecided or else Native.Mode /= R.J.Root_Controller_Admission or else
                     not R.Root_Material_Matches (Data, Obs, Material) or else
                     not R.Root_Capture_Matches (Data, Obs, Provenance) or else
                     not CP.Scoped_Capture_Matches (Data, Obs, Provenance) or else
                     not Native.Id (R.A.Operation_Id).Present then return False; end if;
                  if Before.Operation.Present then
                     declare Root_Found : Boolean := False; begin
                        for N in Value.Events'First .. Index - 1 loop
                           pragma Loop_Variant (Increases => N);
                           declare Event : constant D.Decoded_Event := D.Decode (Value.Arena, Value.Events (N)); begin
                              if Event.Status = D.Decoded and then Event.Value.Kind_Of_Subject = M.Root and then
                                 M.L.Optional_Same (Value.Arena, Event.Value.Operation, Before.Operation) and then
                                 Q.Compare (Value.Arena, Event.Value.Generation, Before.Generation) = Q.Equal and then
                                 I.C.G.Origin_Matches (Value.Arena, Value.Events (N).Operation, Native.Id (R.A.Operation_Id).Value)
                              then Root_Found := True; end if;
                           end;
                        end loop;
                        if not Root_Found then return False; end if;
                     end;
                  end if;
                  if not Same_Value (Data, Data, Source, F (Data, Inventory, "current_source")) then return False; end if;
                  if Channel.Length > 0 then
                     declare Roles : constant E.Span := F (Data, Inventory, "roles"); Endpoint : Boolean := False; begin
                        if not R.Archive_Is_Sequence (Data, Roles) then return False; end if;
                        for N in E.Count range 1 .. R.Archive_Length (Data, Roles) loop
                           pragma Loop_Variant (Increases => N);
                           declare Role : constant E.Span := R.Archive_Index (Data, Roles, N - 1); begin
                              if Enrolled_Endpoint (Data, Data, Inventory, Role, Channel, Source, Duplicate)
                              then Endpoint := True; end if;
                           end;
                        end loop;
                        if not Endpoint then return False; end if;
                     end;
                  end if;
                  Found := True;
               end;
            elsif R.Archive_Text_Is (Data, F (Data, Item, "role"), "operation") then
               if not R.Operation_Material_Matches (Data, Obs, Material) or else
                  R.Reestablish_Operation_Observation (Data, Obs).State /= R.Native_Redecided then return False; end if;
            elsif R.Archive_Text_Is (Data, F (Data, Item, "role"), "scoped-classify") or else
                  R.Archive_Text_Is (Data, F (Data, Item, "role"), "scoped-check") or else
                  R.Archive_Text_Is (Data, F (Data, Item, "role"), "scoped-validate") then
               if not R.Scoped_Material_Matches (Data, Obs, Material) or else
                  R.Reestablish_Scoped_Observation (Data, Obs).State /= R.Native_Redecided or else
                  not CP.Scoped_Capture_Matches (Data, Obs, Provenance) then return False; end if;
            else return False;
            end if;
         end;
      end loop;
      return Found;
   end Native_Origin;
   -- Called only after SE.Output_Context_Reference redecides this current
   -- native tuple; endpoint binding reuses that result, not another replay.
   function Endpoint_Reference
     (Value : I.Parsed_Input; Index : Q.Byte_Count;
      Data : E.Bytes; Channel, Source : E.Span) return Boolean is
      List : constant E.Span := Value.Extras (Index).Native_Observations_Payload;
   begin
      for K in E.Count range 1 .. R.Archive_Length (Value.Arena, List) loop
         pragma Loop_Variant (Increases => K);
         declare
            Item : constant E.Span := R.Archive_Index (Value.Arena, List, K - 1);
            Inventory : constant E.Span := F (Value.Arena, F (Value.Arena, F (Value.Arena, Item, "provenance"),
              "owned_descriptor_roster"), "inventory");
            Native_Source : constant E.Span := F (Value.Arena, Inventory, "current_source");
            Roles : constant E.Span := F (Value.Arena, Inventory, "roles");
         begin
            if Same_Value (Value.Arena, Data, Native_Source, Source) and then
               AP.Scoped_Archive_Operation_Matches (Value.Arena, Data, Scoped_Source (Value, Index), Source) and then
               R.Archive_Is_Sequence (Value.Arena, Roles) then
               for N in E.Count range 1 .. R.Archive_Length (Value.Arena, Roles) loop
                  pragma Loop_Variant (Increases => N);
                  declare Role : constant E.Span := R.Archive_Index (Value.Arena, Roles, N - 1); begin
                     if Enrolled_Endpoint (Value.Arena, Data, Inventory, Role, Channel, Source)
                     then return True; end if;
                  end;
               end loop;
            end if;
         end;
      end loop;
      return False;
   end Endpoint_Reference;
   function Admission
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Subject : P.Optional_Subject;
      Data : E.Bytes; Candidate : E.Span) return Q.Byte_Count is
   begin
      if not Subject.Present then return 0; end if;
      for K in Value.Events'First .. Index - 1 loop
         pragma Loop_Variant (Increases => K);
         declare Event : constant D.Decoded_Event := D.Decode (Value.Arena, Value.Events (K)); begin
            if Event.Status = D.Decoded and then Event.Value.Kind in M.Request_Queued_Event | M.Request_Intake_Event and then
               Event.Value.Kind_Of_Subject = M.Request and then
               Q.Compare (Value.Arena, Event.Value.Generation, Subject.Value.Generation) = Q.Equal and then
               Q.Compare (Value.Arena, Event.Value.Subgeneration, Subject.Value.Subgeneration) = Q.Equal and then
               M.L.Same (Value.Arena, Event.Value.Subject, Subject.Value.Subject) and then
               Raw_Same (Value.Arena, Value.Arena, Value.Events (K).Operation, Value.Events (Index).Operation) and then
               Text_Reference (Value.Arena, Data, F (Data, Candidate, "admission_head"), Value.Events (K).Event_Id) and then
               RJ.Same (Value.Arena, Request (Value, K), Request (Value, Index))
            then return K; end if;
         end;
      end loop;
      return 0;
   end Admission;
   function Source_Reference
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subject : P.Optional_Subject; Data : E.Bytes; Source : E.Span) return Boolean is
   begin
      -- The public entry already established full current source/native joins.
      if AP.Scoped_Archive_Operation_Matches (Value.Arena, Data, Scoped_Source (Value, Index), Source) then
         return True;
      end if;
      for K in Value.Events'First .. Index loop
         pragma Loop_Variant (Increases => K);
         declare
            Event : constant D.Decoded_Event := D.Decode (Value.Arena, Value.Events (K));
            List : constant E.Span := Value.Extras (K).Native_Observations_Payload;
         begin
            if Event.Status = D.Decoded and then Event.Value.Kind_Of_Subject = M.Request and then
               Event.Value.Appending_Actor in M.Front | M.Worker and then
               Q.Compare (Value.Arena, Event.Value.Generation, Subject.Value.Generation) = Q.Equal and then
               Q.Compare (Value.Arena, Event.Value.Subgeneration, Subject.Value.Subgeneration) = Q.Equal and then
               M.L.Same (Value.Arena, Event.Value.Subject, Subject.Value.Subject) and then
               Raw_Same (Value.Arena, Value.Arena, Value.Events (K).Operation, Value.Events (Index).Operation) and then
               AP.Scoped_Archive_Operation_Matches (Value.Arena, Data, Scoped_Source (Value, K), Source) and then
               Value.Extras (K).Native_Observations_Encoding = I.Operation_Original then
               for N in E.Count range 1 .. R.Archive_Length (Value.Arena, List) loop
                  pragma Loop_Variant (Increases => N);
                  declare
                     Item : constant E.Span := R.Archive_Index (Value.Arena, List, N - 1);
                     Inventory : constant E.Span := F (Value.Arena, F (Value.Arena, F (Value.Arena, Item, "provenance"), "owned_descriptor_roster"), "inventory");
                     Old_Source : constant E.Span := F (Value.Arena, Inventory, "current_source");
                  begin
                     if Same_Value (Value.Arena, Data, Old_Source, Source) and then
                        Native_Origin (Value, Index, Before, Value.Arena, List, Old_Source, (1, 0)) then return True; end if;
                  end;
               end loop;
            end if;
         end;
      end loop;
      return False;
   end Source_Reference;
   function Socket_Facts (Data : E.Bytes; Socket, Source : E.Span) return Boolean is
      FD : constant E.Span := F (Data, Socket, "fd");
      function Call (Name : String; Option, Size : Integer) return Boolean is
         Item : constant E.Span := F (Data, Socket, Name);
      begin
         return Same_Value (Data, Data, F (Data, Item, "fd"), FD) and then
           Same_Value (Data, Data, F (Data, Item, "source"), Source) and then
           Integer_Is (Data, F (Data, Item, "result"), 0) and then Integer_Is (Data, F (Data, Item, "errno"), 0) and then
           (if Option /= 0 then Integer_Is (Data, F (Data, Item, "level"), 1) and then
              Integer_Is (Data, F (Data, Item, "option"), Option) and then
              Integer_Is (Data, F (Data, Item, "requested"), Size) and then
              R.Archive_Bytes_Valid (Data, F (Data, Item, "raw")) and then
              R.Archive_Bytes (Data, F (Data, Item, "raw"))'Length = E.Count (Size)
            else R.Archive_Bytes_Valid (Data, F (Data, Item, "raw")));
      end Call;
      Stat : constant E.Span := F (Data, Socket, "fstat");
      Id : constant E.Span := F (Data, Stat, "identity");
   begin
      return A.Valid (Data, Socket) and then Nonnegative (Data, FD) and then
        Same_Value (Data, Data, F (Data, Socket, "source"), Source) and then
        Same_Value (Data, Data, F (Data, Stat, "fd"), FD) and then
        Same_Value (Data, Data, F (Data, Stat, "source"), Source) and then
        Integer_Is (Data, F (Data, Stat, "result"), 0) and then Integer_Is (Data, F (Data, Stat, "errno"), 0) and then
        Nonnegative (Data, F (Data, Id, "device")) and then Nonnegative (Data, F (Data, Id, "inode")) and then
        Nonnegative (Data, F (Data, Id, "mode")) and then CP.Number (Data, F (Data, Id, "mode")) / 4096 mod 16 = 12 and then
        Nonnegative (Data, F (Data, Id, "uid")) and then Nonnegative (Data, F (Data, Id, "gid")) and then
        R.Archive_Bytes_Valid (Data, F (Data, Id, "fdinfo")) and then
        Call ("peercred", 17, 12) and then Call ("domain", 39, 4) and then Call ("type", 3, 4) and then Call ("peername", 0, 0) and then
        R.Archive_Bytes (Data, F (Data, F (Data, Socket, "domain"), "raw")) = E.Bytes'(1, 0, 0, 0) and then
        R.Archive_Bytes (Data, F (Data, F (Data, Socket, "type"), "raw")) = E.Bytes'(1, 0, 0, 0);
   end Socket_Facts;
   function Socket_Valid (Data : E.Bytes; Socket, Document, Source : E.Span) return Boolean is
     (R.Archive_Text_Is (Data, F (Data, Document, "schema"), "worldline.custody-role-socket-v1") and then
      Same_Value (Data, Data, Socket, F (Data, Document, "socket")) and then
      Socket_Facts (Data, Socket, Source));
   function Requester_Socket
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Data : E.Bytes; Socket, Source : E.Span)
      return Boolean is
      Document : constant E.Span := Request (Value, Index);
      Peer : constant E.Span := SF (Value.Arena, Document, "peer");
      Id : constant E.Span := F (Data, F (Data, Socket, "fstat"), "identity");
   begin
      if not Socket_Facts (Data, Socket, Source) or else
         not V.Valid_Hex_Field (Value.Arena, SF (Value.Arena, Peer, "rawUcred"), "value") or else
         not R.Archive_Bytes_Valid (Data, F (Data, F (Data, Socket, "peercred"), "raw")) then return False; end if;
      return AP.Scoped_Archive_Operation_Matches (Value.Arena, Data, SF (Value.Arena, SF (Value.Arena, Peer, "socketIdentity"), "device"), F (Data, Id, "device")) and then
        AP.Scoped_Archive_Operation_Matches (Value.Arena, Data, SF (Value.Arena, SF (Value.Arena, Peer, "socketIdentity"), "inode"), F (Data, Id, "inode")) and then
        AP.Scoped_Archive_Operation_Matches (Value.Arena, Data, SF (Value.Arena, SF (Value.Arena, Peer, "socketIdentity"), "mode"), F (Data, Id, "mode")) and then
        R.Archive_Bytes (Data, F (Data, F (Data, Socket, "peercred"), "raw")) =
          V.Hex_Value (Value.Arena, SF (Value.Arena, Peer, "rawUcred"), "value") and then
        Same_Value (Data, Data, F (Data, Socket, "source"), Source);
   end Requester_Socket;
   function Stream
     (Data : E.Bytes; Frame_Node, IO, Source, Channel : E.Span; Sending : Boolean)
      return Boolean is
      Parts : constant E.Span := F (Data, IO, "parts");
   begin
      if not R.Archive_Bytes_Valid (Data, Frame_Node) or else
         not Same_Value (Data, Data, Frame_Node, F (Data, IO, "frame")) or else
         not R.Archive_Is_Sequence (Data, Parts) or else R.Archive_Length (Data, Parts) = 0 or else
         not Same_Value (Data, Data, F (Data, IO, "fd"), F (Data, Channel, "fd")) or else
         not Same_Value (Data, Data, F (Data, IO, "source"), Source) or else
         not Integer_Is (Data, F (Data, IO, "errno"), 0) then return False; end if;
      declare Raw : constant E.Bytes := R.Archive_Bytes (Data, Frame_Node); Position : E.Count := 0; begin
         if not Nonnegative (Data, F (Data, IO, "result")) or else
            CP.Number (Data, F (Data, IO, "result")) /= Count_Number (Raw'Length) then return False; end if;
         for K in E.Count range 1 .. R.Archive_Length (Data, Parts) loop
            pragma Loop_Variant (Increases => K);
            pragma Loop_Invariant (Position <= Raw'Length);
            declare
               Part : constant E.Span := R.Archive_Index (Data, Parts, K - 1);
               Args : constant E.Span := F (Data, Part, "args");
            begin
               if not R.Archive_Text_Is (Data, F (Data, Part, "call"), (if Sending then "send" else "recv")) or else
                  not Same_Value (Data, Data, F (Data, Part, "fd"), F (Data, Channel, "fd")) or else
                  not Same_Value (Data, Data, F (Data, Args, "fd"), F (Data, Channel, "fd")) or else
                  not Same_Value (Data, Data, F (Data, Part, "source"), Source) or else
                  not Integer_Is (Data, F (Data, Args, "flags"), (if Sending then 16384 else 0)) or else
                  not Integer_Is (Data, F (Data, Part, "errno"), 0) or else
                  not R.Archive_Bytes_Valid (Data, F (Data, Part, "raw")) or else
                  not Nonnegative (Data, F (Data, Part, "result")) then return False; end if;
               declare Chunk : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Part, "raw")); begin
                  if Chunk'Length = 0 or else Chunk'Length > Raw'Length - Position or else
                     CP.Number (Data, F (Data, Part, "result")) /= Count_Number (Chunk'Length) or else
                     (for some N in E.Count range 0 .. Chunk'Length - 1 =>
                        Chunk (Chunk'First + N) /= Raw (Raw'First + Position + N)) then return False; end if;
                  if Sending then
                     if not R.Archive_Bytes_Valid (Data, F (Data, Args, "body")) then return False; end if;
                     declare Offered : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Args, "body")); begin
                        if Offered'Length /= Raw'Length - Position or else
                           (for some N in E.Count range 0 .. Offered'Length - 1 =>
                              Offered (Offered'First + N) /= Raw (Raw'First + Position + N)) then return False; end if;
                     end;
                  elsif not Nonnegative (Data, F (Data, Args, "maximum")) or else
                    CP.Number (Data, F (Data, Args, "maximum")) < Count_Number (Chunk'Length) then return False;
                  end if;
                  Position := Position + Chunk'Length;
               end;
            end;
         end loop;
         return Position = Raw'Length;
      end;
   end Stream;
   function Signed_Frame
     (Value : I.Parsed_Input; Data, Content_Data : E.Bytes;
      Frame_Node, Body_Node, Scope, Candidate, Content : E.Span;
      Kind : String; Projected : Boolean := True) return Boolean is
   begin
      if not R.Archive_Bytes_Valid (Data, Frame_Node) or else not A.Valid (Data, Body_Node) then return False; end if;
      declare
         Raw : constant E.Bytes := R.Archive_Bytes (Data, Frame_Node);
         Length : E.Count := 0;
      begin
         if Raw'Length < 40 or else Raw (Raw'First .. Raw'First + 3) /= E.Bytes'(87,76,82,89) then return False; end if;
         for K in E.Count range 4 .. 7 loop
            pragma Loop_Variant (Increases => K);
            if Length > (E.Count'Last - E.Count (Raw (Raw'First + K))) / 256 then return False; end if;
            Length := Length * 256 + E.Count (Raw (Raw'First + K));
         end loop;
         if Length /= Raw'Length - 40 or else not RJ.Frame_Mac_Matches (Value.Arena, Raw, Value.Key,
            (Raw'First, Raw'Length), "worldline.root-worker-relay-v1" & Character'Val (0)) then return False; end if;
         declare
            Frame_Body : constant E.Span := (Raw'First + 8, Length);
            function Echo (Name : String) return Boolean is
              (Same_Value (Data, Raw, F (Data, Body_Node, Name), F (Raw, Frame_Body, Name)));
            function Scope_Number (Name : String) return Boolean is
              (R.Archive_Bytes_Valid (Data, F (Data, Scope, Name)) and then
               Decimal_Quantity (Raw, F (Raw, Frame_Body, Name), R.Archive_Bytes (Data, F (Data, Scope, Name))));
            Payload : constant E.Span := F (Raw, Frame_Body, "payload");
         begin
            if not Object_Size (Raw, Frame_Body, 11) or else
               not R.Archive_Text_Is (Raw, F (Raw, Frame_Body, "type"), Kind) or else
               not (Echo ("type") and then Echo ("generation") and then Echo ("reattach_epoch") and then
                 Echo ("request") and then Echo ("subgeneration") and then Echo ("operation") and then
                 Echo ("gate") and then Echo ("sequence") and then Echo ("nonce") and then Echo ("admission_head")) or else
               not (Scope_Number ("generation") and then Scope_Number ("subgeneration") and then Scope_Number ("reattach_epoch")) or else
               not Same_Value (Data, Raw, F (Data, Scope, "request"), F (Raw, Frame_Body, "request")) or else
               not Same_Value (Data, Raw, F (Data, Scope, "operation"), F (Raw, Frame_Body, "operation")) or else
               not Same_Value (Data, Raw, F (Data, Candidate, "admission_head"), F (Raw, Frame_Body, "admission_head")) or else
               (Kind not in "PEER_HELD" | "PEER_STATUS" and then not Same_Value (Data, Raw,
                 F (Data, Candidate, "out_seq"), F (Raw, Frame_Body, "sequence"))) or else
               not Decimal (Raw, F (Raw, Frame_Body, "sequence")) or else
               not R.Archive_Text_Is (Raw, F (Raw, Frame_Body, "gate"), "") or else
               not RV.Valid_Text (Raw, F (Raw, Frame_Body, "nonce")) then return False; end if;
            declare Nonce : constant E.Bytes := RV.Text_Value (Raw, F (Raw, Frame_Body, "nonce")); begin
               if Nonce'Length /= 64 or else (for some B of Nonce => B not in 48 .. 57 | 97 .. 102) then return False; end if;
            end;
            if Projected then
               if not R.Archive_Bytes_Valid (Data, F (Data, Body_Node, "payload")) then return False; end if;
               declare Image : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Body_Node, "payload")); begin
                  if not Same_Value (Image, Raw, (Image'First, Image'Length), Payload) then return False; end if;
               end;
            elsif not Same_Value (Data, Raw, F (Data, Body_Node, "payload"), Payload) then return False;
            end if;
            if Kind = "PEER_HELD" then
               return Object_Size (Raw, Payload, 1) and then
                 A.Valid (Raw, F (Raw, Payload, "written")) and then
                 E.Decode (Raw, F (Raw, Payload, "written"), E.Operation).Form = E.Tuple_Value;
            end if;
            if Kind = "PEER_STATUS" then
               return Object_Size (Raw, Payload, 1) and then
                 Same_Value (Raw, Raw, F (Raw, Frame_Body, "sequence"), F (Raw, Payload, "next_out_seq"));
            end if;
            return Object_Size (Raw, Payload, (if Kind = "RESPONSE_WRITTEN" then 2 else 3)) and then
              Same_Value (Data, Raw, F (Data, Candidate, "out_seq"), F (Raw, Payload, "out_seq")) and then
              Same_Value (Data, Raw, F (Data, Candidate, "sha256"), F (Raw, Payload, "sha256")) and then
              (if Kind /= "RESPONSE_WRITTEN" then
                 Same_Value (Content_Data, Raw, F (Content_Data, Content, "line"), F (Raw, Payload, "line")));
         end;
      end;
   end Signed_Frame;
   function Body_Projection (Data, Original_Data : E.Bytes; Projected, Original : E.Span)
      return Boolean is
      function Member (Name : String) return Boolean is
        (Same_Value (Data, Original_Data, F (Data, Projected, Name), F (Original_Data, Original, Name)));
   begin
      if not Object_Size (Data, Projected, 11) or else not Object_Size (Original_Data, Original, 11) or else
         not (Member ("type") and then Member ("generation") and then Member ("reattach_epoch") and then
           Member ("request") and then Member ("subgeneration") and then Member ("operation") and then
           Member ("gate") and then Member ("sequence") and then Member ("nonce") and then Member ("admission_head")) or else
         not R.Archive_Bytes_Valid (Data, F (Data, Projected, "payload")) then return False; end if;
      declare Image : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Projected, "payload")); begin
         return Same_Value (Image, Original_Data, (Image'First, Image'Length), F (Original_Data, Original, "payload"));
      end;
   end Body_Projection;
   function Current_Image (Value : I.Parsed_Input; Index : Q.Byte_Count;
                           Data : E.Bytes; Item : E.Span) return Boolean is
      Emitter : constant E.Span := SF (Value.Arena,
        SF (Value.Arena, Value.Events (Index).Record_Archive, "x5"), "emitter");
   begin
      if not V.Valid_Hex_Field (Value.Arena, Emitter, "candidate") then return False; end if;
      declare Image : constant E.Bytes := V.Hex_Value (Value.Arena, Emitter, "candidate"); begin
         return Same_Value (Image, Data, (Image'First, Image'Length), Item);
      end;
   end Current_Image;
   function Scoped_Socket_Source (Data : E.Bytes; Socket, Source : E.Span) return Boolean is
     (RJ.Same (Data, SF (Data, Socket, "source"), Source) and then
      RJ.Same (Data, SF (Data, SF (Data, Socket, "fstat"), "source"), Source) and then
      RJ.Same (Data, SF (Data, SF (Data, Socket, "peercred"), "source"), Source) and then
      RJ.Same (Data, SF (Data, SF (Data, Socket, "domain"), "source"), Source) and then
      RJ.Same (Data, SF (Data, SF (Data, Socket, "type"), "source"), Source) and then
      RJ.Same (Data, SF (Data, SF (Data, Socket, "peername"), "source"), Source));
   function Credential_PID (Raw : E.Bytes) return Valid_Big_Integer is
      Result : Valid_Big_Integer := To_Big_Integer (0);
   begin
      if Raw'Length /= 12 or else Raw (Raw'First + 3) >= 128 then return To_Big_Integer (-1); end if;
      for K in reverse E.Count range 0 .. 3 loop
         Result := Result * 256 + To_Big_Integer (Integer (Raw (Raw'First + K)));
      end loop;
      return Result;
   end Credential_PID;
   function Namespace_Receiver_Reference
     (Native_Data, Data : E.Bytes; List, Namespace_Source, Receiver_Source : E.Span) return Boolean is
      Receiver : constant E.Span := F (Data, Namespace_Source, "receiver_actor_namespace");
      Actor : constant E.Span := F (Data, Receiver, "actor");
      function Actor_Field (Inventory : E.Span; Name : String) return Boolean is
        (Same_Value (Native_Data, Data, F (Native_Data, F (Native_Data, Inventory, "current_actor"), Name),
          F (Data, Actor, Name)));
   begin
      for K in E.Count range 1 .. R.Archive_Length (Native_Data, List) loop
         pragma Loop_Variant (Increases => K);
         declare
            Item : constant E.Span := R.Archive_Index (Native_Data, List, K - 1);
            Inventory : constant E.Span := F (Native_Data, F (Native_Data, F (Native_Data, Item, "provenance"),
              "owned_descriptor_roster"), "inventory");
            Original_NS : constant E.Span := F (Native_Data, Inventory, "namespace_source");
         begin
            if Same_Value (Native_Data, Data, F (Native_Data, Inventory, "current_source"), Receiver_Source) and then
               Actor_Field (Inventory, "boot") and then Actor_Field (Inventory, "pid") and then
               Actor_Field (Inventory, "start_tick") and then Actor_Field (Inventory, "credentials") and then
               Same_Value (Data, Data, F (Data, Receiver, "source"), Receiver_Source) and then
               Same_Value (Native_Data, Data,
                 F (Native_Data, F (Native_Data, Original_NS, "root_context"), "original_root_frame"),
                 F (Data, F (Data, Namespace_Source, "root_context"), "original_root_frame"))
            then return True; end if;
         end;
      end loop;
      return False;
   end Namespace_Receiver_Reference;
   function Native_Credentials
     (Data, Credential_Data, Origin_Data : E.Bytes; List, Credentials, Sender_Actor,
      Worker_Origin : E.Span; Worker_Sender : Boolean;
      Namespace_Source : E.Span := (1, 0))
      return Boolean is
   begin
      if not R.Archive_Bytes_Valid (Credential_Data, Credentials) then return False; end if;
      for K in E.Count range 1 .. R.Archive_Length (Data, List) loop
         pragma Loop_Variant (Increases => K);
         declare
            Item : constant E.Span := R.Archive_Index (Data, List, K - 1);
            Inventory : constant E.Span := F (Data, F (Data, F (Data, Item, "provenance"),
              "owned_descriptor_roster"), "inventory");
            Actor : constant E.Span := F (Data, Inventory, "current_actor");
         begin
            if R.Archive_Bytes_Valid (Data, F (Data, Actor, "credentials")) and then
               R.Archive_Integer_Valid (Data, F (Data, Actor, "pid")) and then
               R.Archive_Integer_Valid (Data, F (Data, Actor, "start_tick")) and then
               CP.Number (Data, F (Data, Actor, "pid")) > 0 and then
               CP.Number (Data, F (Data, Actor, "start_tick")) >= 0 and then
               Same_Value (Data, Credential_Data, F (Data, Actor, "boot"), F (Credential_Data, Sender_Actor, "boot")) and then
               Same_Value (Data, Credential_Data, F (Data, Actor, "pid"), F (Credential_Data, Sender_Actor, "pid")) and then
               Same_Value (Data, Credential_Data, F (Data, Actor, "start_tick"), F (Credential_Data, Sender_Actor, "start_tick")) and then
               Same_Value (Data, Credential_Data, F (Data, Actor, "credentials"), F (Credential_Data, Sender_Actor, "credentials")) and then
               RE.Stat_Field (Credential_Data, F (Credential_Data, Sender_Actor, "stat"), 1) =
                 CP.Number (Credential_Data, F (Credential_Data, Sender_Actor, "pid")) and then
               RE.Stat_Field (Credential_Data, F (Credential_Data, Sender_Actor, "stat"), 22) =
                 CP.Number (Credential_Data, F (Credential_Data, Sender_Actor, "start_tick")) and then
               RE.Stat_Field (Data, F (Data, Actor, "stat"), 1) = CP.Number (Data, F (Data, Actor, "pid")) and then
               RE.Stat_Field (Data, F (Data, Actor, "stat"), 22) = CP.Number (Data, F (Data, Actor, "start_tick"))
            then
               declare
                  Received : constant E.Bytes := R.Archive_Bytes (Credential_Data, Credentials);
                  Sent : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Actor, "credentials"));
                  Broker : constant E.Span := F (Data, Inventory, "sender_role_roster");
               begin
                  if Received'Length /= 12 or else Sent'Length /= 12 or else
                     Credential_PID (Sent) /= CP.Number (Data, F (Data, Actor, "pid")) or else
                     (for some N in E.Count range 4 .. 11 => Received (Received'First + N) /= Sent (Sent'First + N))
                  then return False; end if;
                  if Worker_Sender then
                     -- Native inventory keeps its checked scoped projection
                     -- in roles and the unchanged full broker list in root_roles.
                     -- The original broker, not namespace getpid(), owns PIDFD.
                     return Same_Value (Data, Origin_Data, F (Data, Broker, "root_roles"),
                         F (Origin_Data, Worker_Origin, "roles")) and then
                       Same_Value (Data, Origin_Data, F (Data, Broker, "source"), F (Origin_Data, Worker_Origin, "source")) and then
                       Same_Value (Data, Origin_Data, F (Data, Broker, "actor"), F (Origin_Data, Worker_Origin, "actor")) and then
                       Same_Value (Data, Origin_Data, F (Data, Broker, "worker_host_pid"), F (Origin_Data, Worker_Origin, "worker_host_pid")) and then
                       Same_Value (Data, Origin_Data, F (Data, Broker, "worker_pidfd"), F (Origin_Data, Worker_Origin, "worker_pidfd")) and then
                       Nonnegative (Data, F (Data, Broker, "worker_host_pid")) and then
                       RE.Pidfd_Pid (Data, F (Data, F (Data, Broker, "worker_pidfd"), "fdinfo")) =
                         CP.Number (Data, F (Data, Broker, "worker_host_pid")) and then
                       Credential_PID (Received) = CP.Number (Data, F (Data, Broker, "worker_host_pid"));
                  end if;
                  if Namespace_Source.Length > 0 then
                     return NP.SCM_Credentials_Match (Credential_Data,
                       F (Credential_Data, Sender_Actor, "credentials"), Credentials, Sender_Actor,
                       F (Credential_Data, F (Credential_Data, Namespace_Source, "receiver_actor_namespace"), "actor"),
                       Namespace_Source);
                  end if;
                  -- Without namespace measurements only literal same-PID
                  -- credentials can join; no generic PID0/peercred fallback.
                  return Credential_PID (Received) = CP.Number (Data, F (Data, Actor, "pid"));
               end;
            end if;
         end;
      end loop;
      return False;
   end Native_Credentials;
   function Write_Sources (Data : E.Bytes; Writes, Socket, Source : E.Span) return Boolean is
   begin
      if not R.Archive_Is_Sequence (Data, Writes) or else R.Archive_Length (Data, Writes) = 0 then return False; end if;
      for K in E.Count range 1 .. R.Archive_Length (Data, Writes) loop
         pragma Loop_Variant (Increases => K);
         declare Item : constant E.Span := R.Archive_Index (Data, Writes, K - 1); begin
            if not R.Archive_Text_Is (Data, F (Data, Item, "call"), "write") or else
               not Same_Value (Data, Data, F (Data, Item, "fd"), F (Data, Socket, "fd")) or else
               not Same_Value (Data, Data, F (Data, Item, "source"), Source) or else
               not R.Archive_Bytes_Valid (Data, F (Data, Item, "offered")) or else
               not R.Archive_Integer_Valid (Data, F (Data, Item, "result")) or else
               not R.Archive_Integer_Valid (Data, F (Data, Item, "errno")) or else
               (if Integer_Is (Data, F (Data, Item, "result"), -1) then
                  CP.Number (Data, F (Data, Item, "errno")) <= 0 or else not R.Archive_Is_None (Data, F (Data, Item, "raw"))
                else not Nonnegative (Data, F (Data, Item, "result")) or else
                  not Integer_Is (Data, F (Data, Item, "errno"), 0) or else not R.Archive_Bytes_Valid (Data, F (Data, Item, "raw")))
            then return False; end if;
         end;
      end loop;
      return True;
   end Write_Sources;
   function Origin_Endpoint
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Native_Data, Data : E.Bytes; List, Channel, Source : E.Span;
      Duplicate : E.Span := (1, 0)) return Boolean is
   begin
      for K in E.Count range 1 .. R.Archive_Length (Native_Data, List) loop
         pragma Loop_Variant (Increases => K);
         declare
            Item : constant E.Span := R.Archive_Index (Native_Data, List, K - 1);
            Inventory : constant E.Span := F (Native_Data, F (Native_Data, F (Native_Data, Item, "provenance"),
              "owned_descriptor_roster"), "inventory");
            Native_Source : constant E.Span := F (Native_Data, Inventory, "current_source");
            Roles : constant E.Span := F (Native_Data, Inventory, "roles");
         begin
            if Same_Value (Native_Data, Data, Native_Source, Source) and then
               Native_Origin (Value, Index, Before, Native_Data, List, Native_Source, (1, 0)) and then
               R.Archive_Is_Sequence (Native_Data, Roles) then
               for N in E.Count range 1 .. R.Archive_Length (Native_Data, Roles) loop
                  pragma Loop_Variant (Increases => N);
                  declare Role : constant E.Span := R.Archive_Index (Native_Data, Roles, N - 1); begin
                     if Enrolled_Endpoint (Native_Data, Data, Inventory, Role, Channel, Source, Duplicate)
                     then return True; end if;
                  end;
               end loop;
            end if;
         end;
      end loop;
      return False;
   end Origin_Endpoint;
   function Peer_Status_Reference
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Data : E.Bytes; Candidate : E.Span) return Boolean is
      Scope : constant E.Span := F (Data, Candidate, "scope");
      Source : constant E.Span := F (Data, Candidate, "source");
      Relay : constant E.Span := F (Data, Candidate, "relay");
      Worker_Channel : constant E.Span := F (Data, Relay, "channel");
      Front_Channel : constant E.Span := F (Data, Relay, "front_channel");
      Worker_Source : constant E.Span := F (Data, F (Data, Relay, "request_send"), "source");
      Request_Body : constant E.Span := F (Data, Relay, "request_body");
      Response_Body : constant E.Span := F (Data, Relay, "response_body");
      function Echo (Name : String) return Boolean is
        (Same_Value (Data, Data, F (Data, Request_Body, Name), F (Data, Response_Body, Name)));
   begin
      if not Object_Size (Data, Candidate, 7) or else
         (Current_Image (Value, Index, Data, Candidate) and then
          not Quantity (Value.Arena, Data, F (Data, Scope, "reattach_epoch"), Before.Reattach_Epoch)) or else
         E.Decode (Data, F (Data, Candidate, "written"), E.Operation).Form /= E.Tuple_Value or else
         not A.Valid (Data, F (Data, Candidate, "written")) or else
         not R.Archive_Bytes_Valid (Data, F (Data, Relay, "report_raw")) or else
         not R.Archive_Bytes_Valid (Data, F (Data, Relay, "writer_native")) or else
         not R.Archive_Bytes_Valid (Data, F (Data, Relay, "worker_native")) or else
         not (Echo ("generation") and then Echo ("reattach_epoch") and then Echo ("request") and then
           Echo ("subgeneration") and then Echo ("operation") and then Echo ("gate") and then
           Echo ("nonce") and then Echo ("admission_head"))
      then return False; end if;
      declare
         Raw : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Relay, "report_raw"));
         Packet : constant E.Span := (Raw'First, Raw'Length);
         Report : constant E.Span := F (Raw, Packet, "report");
         Native : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Relay, "writer_native"));
         Native_List : constant E.Span := (Native'First, Native'Length);
         Worker_Native : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Relay, "worker_native"));
         Worker_List : constant E.Span := (Worker_Native'First, Worker_Native'Length);
      begin
         -- The signed body is authenticated here, but its position is not
         -- authority. Root_Output_Sequence separately folds every actual write.
         return R.Archive_Text_Is (Raw, F (Raw, Packet, "schema"), "worldline.live-subject-service-v1") and then
           R.Archive_Text_Is (Raw, F (Raw, Packet, "kind"), "PEER_STATUS_REPORT") and then
           Same_Value (Raw, Data, F (Raw, Report, "source"), Source) and then
           Same_Value (Raw, Data, F (Raw, Report, "actor"), F (Data, Relay, "writer_actor")) and then
           Same_Value (Raw, Data, F (Raw, Report, "channel"), Front_Channel) and then
           Same_Value (Raw, Data, F (Raw, Report, "channel_document"), F (Data, Relay, "front_channel_document")) and then
           Same_Value (Raw, Data, F (Raw, Report, "frame"), F (Data, Relay, "response_frame")) and then
           Same_Value (Raw, Data, F (Raw, Report, "written"), F (Data, Candidate, "written")) and then
           Same_Value (Raw, Data, F (Raw, Report, "request_receive"), F (Data, Relay, "request_receive")) and then
           Same_Value (Raw, Data, F (Raw, Report, "peer_status_send"), F (Data, Relay, "peer_status_send")) and then
           Same_Value (Native, Raw, Native_List, F (Raw, Report, "native")) and then
           Body_Projection (Data, Raw, Response_Body, F (Raw, Report, "body")) and then
           Socket_Valid (Data, Worker_Channel, F (Data, Relay, "channel_document"), Worker_Source) and then
           Origin_Endpoint (Value, Index, Before, Worker_Native, Data, Worker_List, Worker_Channel, Worker_Source,
             F (Data, Relay, "channel_duplicate")) and then
           Socket_Valid (Data, Front_Channel, F (Data, Relay, "front_channel_document"), Source) and then
           Origin_Endpoint (Value, Index, Before, Native, Data, Native_List, Front_Channel, Source) and then
           Stable_Identity (Data, Data, F (Data, F (Data, Relay, "writer_actor"), "channel"),
             F (Data, F (Data, Front_Channel, "fstat"), "identity")) and then
           Signed_Frame (Value, Data, Data, F (Data, Relay, "request_frame"), Request_Body,
             Scope, Candidate, Candidate, "PEER_HELD") and then
           Signed_Frame (Value, Data, Data, F (Data, Relay, "response_frame"), Response_Body,
             Scope, Candidate, Candidate, "PEER_STATUS") and then
           Stream (Data, F (Data, Relay, "request_frame"), F (Data, Relay, "request_send"),
             Worker_Source, Worker_Channel, True) and then
           Stream (Data, F (Data, Relay, "request_frame"), F (Data, Relay, "request_receive"),
             Source, Front_Channel, False) and then
           Stream (Data, F (Data, Relay, "response_frame"), F (Data, Relay, "peer_status_send"),
             Source, Front_Channel, True) and then
           Stream (Data, F (Data, Relay, "response_frame"), F (Data, Relay, "peer_status_receive"),
             Worker_Source, Worker_Channel, False) and then
           Namespace_Receiver_Reference (Worker_Native, Data, Worker_List,
             F (Data, Relay, "relay_namespace_source"), Worker_Source) and then
           Same_Value (Raw, Data, F (Raw, Report, "sender_actor_namespace"),
             F (Data, F (Data, Relay, "relay_namespace_source"), "sender_actor_namespace")) and then
           Native_Credentials (Native, Data, Data, Native_List, F (Data, Relay, "report_sender"),
             F (Data, Relay, "writer_actor"), (1, 0), False, F (Data, Relay, "relay_namespace_source"));
      end;
   end Peer_Status_Reference;
   function Prefix_Reference
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : J.Journal_Proof; Candidate_Data : E.Bytes; Candidate : E.Span)
      return Boolean is
      Data : E.Bytes renames Candidate_Data;
      Scope : constant E.Span := F (Data, Candidate, "scope");
      Source : constant E.Span := F (Data, Candidate, "source");
      Written : constant E.Span := F (Data, Candidate, "written");
   begin
      return SE.Output_Context_Reference (Value, Index, Before, Subjects, Subject, Proof) and then
        Object_Size (Data, Candidate, 6) and then
        R.Archive_Text_Is (Data, F (Data, Candidate, "type"), "OUTPUT_PREFIX") and then
        Scope_Domain (Value, Index, Before, Subject, Data, Scope) and then
        Quantity (Value.Arena, Data, F (Data, Scope, "reattach_epoch"), Before.Reattach_Epoch) and then
        Admission (Value, Index, Subject, Data, Candidate) /= 0 and then
        Text_Reference (Value.Arena, Data, F (Data, Candidate, "request"), Value.Events (Index).Subject) and then
        AP.Scoped_Archive_Operation_Matches (Value.Arena, Data, Scoped_Source (Value, Index), Source) and then
        A.Valid (Data, Written) and then E.Decode (Data, Written, E.Finalization).Form = E.Tuple_Value;
   end Prefix_Reference;
   function Frame_Reference
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : J.Journal_Proof; Candidate_Data : E.Bytes; Candidate : E.Span)
      return Boolean is
      Data : E.Bytes renames Candidate_Data;
      Scope : constant E.Span := F (Data, Candidate, "scope");
      Source : constant E.Span := F (Data, Candidate, "source");
      Relay : constant E.Span := F (Data, Candidate, "relay");
   begin
      if not SE.Output_Context_Reference (Value, Index, Before, Subjects, Subject, Proof) or else
         not A.Valid (Data, Candidate) or else not Scope_Domain (Value, Index, Before, Subject, Data, Scope) or else
         Admission (Value, Index, Subject, Data, Candidate) = 0 or else
         not Text_Reference (Value.Arena, Data, F (Data, Candidate, "request"), Value.Events (Index).Subject) or else
         (Current_Image (Value, Index, Data, Candidate) and then
          not Quantity (Value.Arena, Data, F (Data, Scope, "reattach_epoch"), Before.Reattach_Epoch))
      then return False; end if;
      if R.Archive_Text_Is (Data, F (Data, Candidate, "type"), "PEER_STATUS") then
         return Peer_Status_Reference (Value, Index, Before, Data, Candidate);
      end if;
      if not (R.Archive_Text_Is (Data, F (Data, Candidate, "type"), "PROGRESS_BYTES") or else
              R.Archive_Text_Is (Data, F (Data, Candidate, "type"), "RESPONSE_BYTES")) then return False; end if;
      if Relay.Length = 0 then
         return (not Current_Image (Value, Index, Data, Candidate) or else
           AP.Scoped_Archive_Operation_Matches (Value.Arena, Data, Scoped_Source (Value, Index), Source)) and then
           Source_Reference (Value, Index, Before, Subject, Data, Source);
      end if;
      if not R.Archive_Bytes_Valid (Data, F (Data, Relay, "report_raw")) then return False; end if;
      declare
         Raw : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Relay, "report_raw"));
         Packet : constant E.Span := (Raw'First, Raw'Length);
         Saved : constant E.Span := F (Raw, Packet, "candidate");
         Worker_Source : constant E.Span := F (Data, F (Data, Relay, "output_send"), "source");
         Channel : constant E.Span := F (Data, Relay, "channel");
         Worker_Channel : constant E.Span := F (Data, Relay, "worker_channel");
         Kind : constant String := (if R.Archive_Text_Is (Data, F (Data, Candidate, "type"), "PROGRESS_BYTES") then "PROGRESS_BYTES" else "RESPONSE_BYTES");
      begin
         return R.Archive_Text_Is (Raw, F (Raw, Packet, "schema"), "worldline.live-subject-service-v1") and then
           R.Archive_Text_Is (Raw, F (Raw, Packet, "kind"), "OUTPUT_SOURCE") and then
           Same_Value (Raw, Data, F (Raw, Saved, "source"), Worker_Source) and then
           Same_Value (Raw, Data, F (Raw, Packet, "send"), F (Data, Relay, "output_send")) and then
           Same_Value (Raw, Data, F (Raw, Packet, "worker_channel"), Worker_Channel) and then
           Same_Value (Raw, Data, F (Raw, Packet, "actor"), F (Data, Relay, "worker_actor")) and then
           Same_Value (Raw, Data, F (Raw, Packet, "worker_channel_document"), F (Data, Relay, "worker_channel_document")) and then
           Stable_Identity (Data, Data, F (Data, F (Data, Relay, "worker_actor"), "channel"),
             F (Data, F (Data, Worker_Channel, "fstat"), "identity")) and then
           Same_Value (Raw, Data, F (Raw, Saved, "scope"), Scope) and then
           Same_Value (Raw, Data, F (Raw, Saved, "production_scope"), F (Data, Candidate, "production_scope")) and then
           Same_Value (Raw, Data, F (Raw, Saved, "line"), F (Data, Candidate, "line")) and then
           Same_Value (Raw, Data, F (Raw, Saved, "out_seq"), F (Data, Candidate, "out_seq")) and then
           Same_Value (Raw, Data, F (Raw, Saved, "sha256"), F (Data, Candidate, "sha256")) and then
           Socket_Valid (Data, Channel, F (Data, Relay, "channel_document"), Source) and then
           Socket_Valid (Data, Worker_Channel, F (Data, Relay, "worker_channel_document"), Worker_Source) and then
           Native_Origin (Value, Index, Before, Raw, F (Raw, Packet, "native"),
             F (Raw, Saved, "source"), F (Raw, Packet, "worker_channel"), F (Raw, Packet, "channel_duplicate")) and then
           Source_Reference (Value, Index, Before, Subject, Data, Source) and then
           Endpoint_Reference (Value, Index, Data, Channel, Source) and then
           Requester_Socket (Value, Index, Data, F (Data, Relay, "front_socket"), Source) and then
           Signed_Frame (Value, Data, Data, F (Data, Relay, "frame"), F (Data, Relay, "body"),
             Scope, Candidate, Candidate, Kind) and then
           Stream (Data, F (Data, Relay, "frame"), F (Data, Relay, "output_send"), Worker_Source, Worker_Channel, True) and then
           Stream (Data, F (Data, Relay, "frame"), F (Data, Relay, "output_receive"), Source, Channel, False) and then
           Native_Credentials (Raw, Data, Raw, F (Raw, Packet, "native"), F (Data, Relay, "report_sender"),
             F (Data, Relay, "worker_actor"), F (Raw, Packet, "worker_origin"), True);
      end;
   end Frame_Reference;
   function Front_Written_Reference
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Data, Produced_Data : E.Bytes; Acknowledgement, Produced : E.Span) return Boolean is
      Relay : constant E.Span := F (Data, Acknowledgement, "relay");
      Scope : constant E.Span := F (Data, Acknowledgement, "scope");
      Source : constant E.Span := F (Data, Acknowledgement, "source");
      Channel : constant E.Span := F (Data, Relay, "front_channel");
      Worker_Channel : constant E.Span := F (Data, Relay, "channel");
      Socket : constant E.Span := F (Data, Relay, "front_socket");
   begin
      -- Front records its actual write/send before any Worker receive occurs.
      -- The sealed OUTPUT_SOURCE and saved real Front writer tuple are its
      -- distinct profile; never fabricate OUTPUT_WRITTEN_REPORT/receive facts.
      if not R.Archive_Bytes_Valid (Data, F (Data, Relay, "report_raw")) or else
         not R.Archive_Bytes_Valid (Data, F (Data, Relay, "worker_native")) or else
         not R.Archive_Bytes_Valid (Data, F (Data, Relay, "writer_native")) then return False; end if;
      declare
         Raw : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Relay, "report_raw"));
         Packet : constant E.Span := (Raw'First, Raw'Length);
         Saved : constant E.Span := F (Raw, Packet, "candidate");
         Worker_Source : constant E.Span := F (Raw, Saved, "source");
         Worker_Native : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Relay, "worker_native"));
         Worker_List : constant E.Span := (Worker_Native'First, Worker_Native'Length);
         Writer_Native : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Relay, "writer_native"));
         Writer_List : constant E.Span := (Writer_Native'First, Writer_Native'Length);
         Kind : constant String := (if R.Archive_Text_Is (Produced_Data, F (Produced_Data, Produced, "type"),
           "PROGRESS_BYTES") then "PROGRESS_BYTES" else "RESPONSE_BYTES");
      begin
         return R.Archive_Text_Is (Raw, F (Raw, Packet, "schema"), "worldline.live-subject-service-v1") and then
           R.Archive_Text_Is (Raw, F (Raw, Packet, "kind"), "OUTPUT_SOURCE") and then
           F (Data, Relay, "written_receive").Length = 0 and then
           Same_Value (Worker_Native, Raw, Worker_List, F (Raw, Packet, "native")) and then
           Same_Value (Raw, Data, F (Raw, Packet, "worker_channel"), Worker_Channel) and then
           Same_Value (Raw, Data, F (Raw, Packet, "worker_channel_document"), F (Data, Relay, "channel_document")) and then
           Same_Value (Raw, Data, F (Raw, Packet, "channel_duplicate"), F (Data, Relay, "channel_duplicate")) and then
           Same_Value (Raw, Data, F (Raw, Packet, "actor"), F (Data, Relay, "worker_actor")) and then
           Same_Value (Raw, Data, F (Raw, Packet, "send"), F (Data, Relay, "output_send")) and then
           Same_Value (Raw, Data, F (Raw, Saved, "scope"), Scope) and then
           Same_Value (Raw, Data, F (Raw, Saved, "production_scope"), F (Data, Acknowledgement, "production_scope")) and then
           Same_Value (Raw, Produced_Data, F (Raw, Saved, "line"), F (Produced_Data, Produced, "line")) and then
           Same_Value (Raw, Data, F (Raw, Saved, "out_seq"), F (Data, Acknowledgement, "out_seq")) and then
           Same_Value (Raw, Data, F (Raw, Saved, "sha256"), F (Data, Acknowledgement, "sha256")) and then
           Same_Value (Data, Data, F (Data, Relay, "frame"), F (Data, Relay, "request_frame")) and then
           Same_Value (Data, Data, F (Data, Relay, "body"), F (Data, Relay, "request_body")) and then
           Native_Origin (Value, Index, Before, Raw, F (Raw, Packet, "native"), Worker_Source,
             F (Raw, Packet, "worker_channel"), F (Raw, Packet, "channel_duplicate")) and then
           Socket_Valid (Data, Channel, F (Data, Relay, "front_channel_document"), Source) and then
           Origin_Endpoint (Value, Index, Before, Writer_Native, Data, Writer_List, Channel, Source) and then
           Stable_Identity (Data, Data, F (Data, F (Data, Relay, "writer_actor"), "channel"),
             F (Data, F (Data, Channel, "fstat"), "identity")) and then
           Requester_Socket (Value, Index, Data, Socket, Source) and then
           Write_Sources (Data, F (Data, Acknowledgement, "write"), Socket, Source) and then
           Signed_Frame (Value, Data, Produced_Data, F (Data, Relay, "request_frame"), F (Data, Relay, "request_body"),
             Scope, Acknowledgement, Produced, Kind) and then
           Signed_Frame (Value, Data, Produced_Data, F (Data, Relay, "response_frame"), F (Data, Relay, "response_body"),
             Scope, Acknowledgement, Produced, "RESPONSE_WRITTEN") and then
           Stream (Data, F (Data, Relay, "request_frame"), F (Data, Relay, "output_send"),
             F (Data, F (Data, Relay, "output_send"), "source"), Worker_Channel, True) and then
           Same_Value (Raw, Data, Worker_Source, F (Data, F (Data, Relay, "output_send"), "source")) and then
           Socket_Valid (Data, Worker_Channel, F (Data, Relay, "channel_document"),
             F (Data, F (Data, Relay, "output_send"), "source")) and then
           Stream (Data, F (Data, Relay, "request_frame"), F (Data, Relay, "output_receive"), Source, Channel, False) and then
           Stream (Data, F (Data, Relay, "response_frame"), F (Data, Relay, "written_send"), Source, Channel, True) and then
           Native_Credentials (Writer_Native, Data, Data, Writer_List,
             F (Data, F (Data, Relay, "writer_actor"), "credentials"), F (Data, Relay, "writer_actor"),
             (1, 0), False) and then
           Native_Credentials (Raw, Data, Raw, F (Raw, Packet, "native"), F (Data, Relay, "report_sender"),
             F (Data, Relay, "worker_actor"), F (Raw, Packet, "worker_origin"), True);
      end;
   end Front_Written_Reference;
   function Acknowledgement_Reference
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : J.Journal_Proof; Acknowledgement_Data, Produced_Data : E.Bytes;
      Acknowledgement, Produced : E.Span)
      return Boolean is
      Data : E.Bytes renames Acknowledgement_Data;
      Scope : constant E.Span := F (Data, Acknowledgement, "scope");
      Source : constant E.Span := F (Data, Acknowledgement, "source");
      Relay : constant E.Span := F (Data, Acknowledgement, "relay");
   begin
      if not Frame_Reference (Value, Index, Before, Subjects, Subject, Proof, Produced_Data, Produced) or else
         not Scope_Domain (Value, Index, Before, Subject, Data, Scope) or else
         (Current_Image (Value, Index, Data, Acknowledgement) and then
          not Quantity (Value.Arena, Data, F (Data, Scope, "reattach_epoch"), Before.Reattach_Epoch)) or else
         not R.Archive_Text_Is (Data, F (Data, Acknowledgement, "type"), "RESPONSE_WRITTEN") or else
         not Same_Value (Data, Produced_Data, F (Data, Acknowledgement, "production_scope"), F (Produced_Data, Produced, "scope")) or else
         not Same_Value (Data, Produced_Data, F (Data, Acknowledgement, "request"), F (Produced_Data, Produced, "request")) or else
         not Same_Value (Data, Produced_Data, F (Data, Acknowledgement, "out_seq"), F (Produced_Data, Produced, "out_seq")) or else
         not Same_Value (Data, Produced_Data, F (Data, Acknowledgement, "sha256"), F (Produced_Data, Produced, "sha256"))
      then return False; end if;
      if Admission (Value, Index, Subject, Data, Acknowledgement) = 0 then return False; end if;
      if Relay.Length = 0 then
         if Current_Image (Value, Index, Data, Acknowledgement) and then Subject.Value.Mode = M.Relay then
            return False;
         end if;
         if (Current_Image (Value, Index, Data, Acknowledgement) and then
             not AP.Scoped_Archive_Operation_Matches (Value.Arena, Data, Scoped_Source (Value, Index), Source)) or else
            not Source_Reference (Value, Index, Before, Subject, Data, Source) then return False; end if;
         for K in Value.Events'First .. Index - 1 loop
            pragma Loop_Variant (Increases => K);
            declare
               Event : constant D.Decoded_Event := D.Decode (Value.Arena, Value.Events (K));
               Profile : constant E.Span := Facts (Value, K);
               Socket : constant E.Span := SF (Value.Arena, Profile, "worker_socket");
               Front : constant E.Span := SF (Value.Arena, Profile, "front_socket");
            begin
               if Event.Status = D.Decoded and then Event.Value.Kind in M.Request_Queued_Event | M.Request_Intake_Event and then
                  Event.Value.Kind_Of_Subject = M.Request and then
                  Q.Compare (Value.Arena, Event.Value.Generation, Subject.Value.Generation) = Q.Equal and then
                  Q.Compare (Value.Arena, Event.Value.Subgeneration, Subject.Value.Subgeneration) = Q.Equal and then
                  M.L.Same (Value.Arena, Event.Value.Subject, Subject.Value.Subject) and then
                  Raw_Same (Value.Arena, Value.Arena, Value.Events (K).Operation, Value.Events (Index).Operation) then
                  declare
                     Active : constant E.Span := (if Event.Value.Appending_Actor = M.Front then Front else Socket);
                     Document : constant E.Span := (if Event.Value.Appending_Actor = M.Front then Request (Value, K)
                       else SF (Value.Arena, SF (Value.Arena, Profile, "transfer"), "worker_document"));
                  begin
                     if RJ.Socket_Matches (Value.Arena, Active, Document) and then
                        Scoped_Socket_Source (Value.Arena, Active, Scoped_Source (Value, K)) and then
                        AP.Scoped_Archive_Operation_Matches (Value.Arena, Data, Scoped_Source (Value, K), Source) then
                        declare Writes : constant E.Span := F (Data, Acknowledgement, "write"); begin
                           if not R.Archive_Is_Sequence (Data, Writes) or else R.Archive_Length (Data, Writes) = 0 then return False; end if;
                           for N in E.Count range 1 .. R.Archive_Length (Data, Writes) loop
                              pragma Loop_Variant (Increases => N);
                              declare Part : constant E.Span := R.Archive_Index (Data, Writes, N - 1); begin
                                 if not R.Archive_Text_Is (Data, F (Data, Part, "call"), "write") or else
                                    not AP.Scoped_Archive_Operation_Matches (Value.Arena, Data, SF (Value.Arena, Active, "fd"), F (Data, Part, "fd")) or else
                                    not Same_Value (Data, Data, Source, F (Data, Part, "source")) then return False; end if;
                              end;
                           end loop;
                           return True;
                        end;
                     end if;
                  end;
               end if;
            end;
         end loop;
         return False;
      end if;
      if not R.Archive_Bytes_Valid (Data, F (Data, Relay, "report_raw")) or else
         not R.Archive_Bytes_Valid (Data, F (Data, Relay, "writer_native")) or else
         not R.Archive_Bytes_Valid (Data, F (Data, Relay, "worker_native")) then return False; end if;
      declare
         Raw : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Relay, "report_raw"));
         Packet : constant E.Span := (Raw'First, Raw'Length);
         Report : constant E.Span := F (Raw, Packet, "report");
         Worker_Source : constant E.Span := F (Data, F (Data, Relay, "output_send"), "source");
         Channel : constant E.Span := F (Data, Relay, "channel");
         Front_Channel : constant E.Span := F (Data, Relay, "front_channel");
         Front_Socket : constant E.Span := F (Data, Relay, "front_socket");
         Worker_Native : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Relay, "worker_native"));
         Worker_List : constant E.Span := (Worker_Native'First, Worker_Native'Length);
         Writer_Native : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Relay, "writer_native"));
         Writer_List : constant E.Span := (Writer_Native'First, Writer_Native'Length);
         Kind : constant String := (if R.Archive_Text_Is (Produced_Data, F (Produced_Data, Produced, "type"), "PROGRESS_BYTES") then "PROGRESS_BYTES" else "RESPONSE_BYTES");
      begin
         if R.Archive_Text_Is (Raw, F (Raw, Packet, "kind"), "OUTPUT_SOURCE") then
            return Front_Written_Reference (Value, Index, Before, Data, Produced_Data, Acknowledgement, Produced);
         end if;
         return R.Archive_Text_Is (Raw, F (Raw, Packet, "schema"), "worldline.live-subject-service-v1") and then
           R.Archive_Text_Is (Raw, F (Raw, Packet, "kind"), "OUTPUT_WRITTEN_REPORT") and then
           Same_Value (Raw, Data, F (Raw, Report, "source"), Source) and then
           Same_Value (Raw, Data, F (Raw, Report, "actor"), F (Data, Relay, "writer_actor")) and then
           Same_Value (Writer_Native, Raw, Writer_List, F (Raw, Report, "native")) and then
           Stable_Identity (Data, Data, F (Data, F (Data, Relay, "writer_actor"), "channel"),
             F (Data, F (Data, Front_Channel, "fstat"), "identity")) and then
           Same_Value (Raw, Data, F (Raw, Report, "channel"), Front_Channel) and then
           Same_Value (Raw, Data, F (Raw, Report, "channel_document"), F (Data, Relay, "front_channel_document")) and then
           Same_Value (Raw, Data, F (Raw, Report, "front_socket"), Front_Socket) and then
           Same_Value (Raw, Data, F (Raw, Report, "write"), F (Data, Acknowledgement, "write")) and then
           Same_Value (Raw, Data, F (Raw, Report, "output_receive"), F (Data, Relay, "output_receive")) and then
           Same_Value (Raw, Data, F (Raw, Report, "written_send"), F (Data, Relay, "written_send")) and then
           Same_Value (Raw, Data, F (Raw, Report, "frame"), F (Data, Relay, "response_frame")) and then
           Socket_Valid (Data, Channel, F (Data, Relay, "channel_document"), Worker_Source) and then
           Origin_Endpoint (Value, Index, Before, Worker_Native, Data, Worker_List, Channel, Worker_Source,
             F (Data, Relay, "channel_duplicate")) and then
           Socket_Valid (Data, Front_Channel, F (Data, Relay, "front_channel_document"), Source) and then
           Native_Origin (Value, Index, Before, Raw, F (Raw, Report, "native"), F (Raw, Report, "source"), F (Raw, Report, "channel")) and then
           Requester_Socket (Value, Index, Data, Front_Socket, Source) and then
           Write_Sources (Data, F (Data, Acknowledgement, "write"), Front_Socket, Source) and then
           Signed_Frame (Value, Data, Produced_Data, F (Data, Relay, "request_frame"), F (Data, Relay, "request_body"),
             Scope, Acknowledgement, Produced, Kind) and then
           Signed_Frame (Value, Data, Produced_Data, F (Data, Relay, "response_frame"), F (Data, Relay, "response_body"),
             Scope, Acknowledgement, Produced, "RESPONSE_WRITTEN") and then
           Body_Projection (Data, Raw, F (Data, Relay, "response_body"), F (Raw, Report, "body")) and then
           Stream (Data, F (Data, Relay, "request_frame"), F (Data, Relay, "output_send"), Worker_Source, Channel, True) and then
           Stream (Data, F (Data, Relay, "request_frame"), F (Data, Relay, "output_receive"), Source, Front_Channel, False) and then
           Stream (Data, F (Data, Relay, "response_frame"), F (Data, Relay, "written_send"), Source, Front_Channel, True) and then
           Stream (Data, F (Data, Relay, "response_frame"), F (Data, Relay, "written_receive"), Worker_Source, Channel, False) and then
           Namespace_Receiver_Reference (Worker_Native, Data, Worker_List,
             F (Data, Relay, "relay_namespace_source"), Worker_Source) and then
           Same_Value (Raw, Data, F (Raw, Report, "sender_actor_namespace"),
             F (Data, F (Data, Relay, "relay_namespace_source"), "sender_actor_namespace")) and then
           Native_Credentials (Raw, Data, Data, F (Raw, Report, "native"), F (Data, Relay, "report_sender"),
             F (Data, Relay, "writer_actor"), (1, 0), False, F (Data, Relay, "relay_namespace_source"));
      end;
   end Acknowledgement_Reference;
end Worldline.Emitter_Channel_Evidence;

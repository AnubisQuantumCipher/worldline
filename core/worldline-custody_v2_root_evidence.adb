with Ada.Characters.Latin_1;
with Interfaces;
with SPARK.Big_Integers;
with Worldline.Retained_Evidence_Replay;
with Worldline.Custody_V2_Domain_Hmac;
with Canonical_Artifacts;
with Worldline.Custody_V2_Machine_Evidence;
with Worldline.Custody_V2_Prepared;
with Worldline.Custody_V2_Operation_Journal;
with Worldline.Runner_Lifecycle;
with Worldline.Custody_V2_Archive_Projection;
with Worldline.Custody_V2_Root_Values;
with Worldline.Scoped_Capture_Projection;
with Worldline.Custody_V2_Mutation_Decision;
with Worldline.Scoped_Capture_Namespace_Projection;
with Worldline.Custody_V2_Closed_State;
package body Worldline.Custody_V2_Root_Evidence with SPARK_Mode is
   package V renames Worldline.Custody_V2_Root_Values;
   package CV renames L.V;
   package S renames V.S;
   package R renames Worldline.Retained_Evidence_Replay;
   package H renames Worldline.Custody_V2_Domain_Hmac;
   package C renames D.C;
   package O renames R.A;
   use SPARK.Big_Integers;
   use type Q.Byte_Count;
   use type Q.Byte;
   use type Q.Byte_Array;
   use type Q.Ordering;
   use type D.Decode_Status;
   use type L.Decode_Status;
   use type L.Original_Format;
   use type M.Event_Kind;
   use type M.Subject_Kind;
   use type M.Root_Phase;
   use type M.Cause_Class;
   use type R.Replay_State;
   use type R.Scoped_Entry;
   use type R.Operation_Entry;
   use type R.J.Status;
   use type R.J.Admission_Mode;
   use type R.J.L.Operation;
   use type O.Command;
   use type O.Decision;
   use type Interfaces.Unsigned_32;
   use type Canonical_Artifacts.Genesis_Correspondence;
   use type R.H.Decision;
   use type P.Event_Family;
   use type M.Digest;
   LF : constant Character := Ada.Characters.Latin_1.LF;
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     renames V.Record_Field;
   function SF (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
     renames R.Archive_Field;
   function Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (V.Valid (Data, Left) and then V.Valid (Data, Right) and then
      S.A.Same_Encoding (Data, Left, Right));
   function Text (Data : E.Bytes; Item : E.Span; Word : String) return Boolean is
     (V.Text_Is (Data, Item, Word));
   function Present (Data : E.Bytes; Item : E.Span) return Boolean is
     (V.Valid (Data, Item) and then not V.Is_Null (Data, Item));
   function Scoped_Matches_Raw (Data : E.Bytes; Scoped, Raw : E.Span) return Boolean is
     (Worldline.Custody_V2_Archive_Projection.Scoped_Archive_Operation_Matches
        (Data, Data, Scoped, Raw));
   function Extent_Number (Length : E.Count) return Valid_Big_Integer is
      Remaining : E.Count := Length;
      Factor : Valid_Big_Integer := To_Big_Integer (1);
      Result : Valid_Big_Integer := To_Big_Integer (0);
   begin
      while Remaining /= 0 loop
         pragma Loop_Variant (Decreases => Remaining);
         Result := Result + To_Big_Integer (Integer (Remaining mod 256)) * Factor;
         Remaining := Remaining / 256; Factor := Factor * 256;
      end loop;
      return Result;
   end Extent_Number;
   function Number (Data : E.Bytes; Item : E.Span) return Valid_Big_Integer is
   begin
      if V.Is_Integer (Data, Item) then
         declare Raw : constant E.Bytes := V.Magnitude_Value (Data, Item); begin
            return M.L.Exact_Value (Raw, (V.Negative (Data, Item), Raw'First, Raw'Length));
         end;
      elsif CV.Is_Integer (Data, Item) then
         declare Raw : constant E.Bytes := CV.Magnitude_Value (Data, Item); begin
            return M.L.Exact_Value (Raw, (CV.Negative (Data, Item), Raw'First, Raw'Length));
         end;
      else return To_Big_Integer (-1); end if;
   end Number;
   function Base_Quantity_Matches (Data : E.Bytes; Raw, Scoped : E.Span) return Boolean is
      Expected : Valid_Big_Integer;
   begin
      if CV.Is_Integer (Data, Scoped) then Expected := Number (Data, Scoped);
      elsif CV.Valid_Bytes (Data, Scoped) then
         declare Bytes : constant E.Bytes := CV.Bytes_Value (Data, Scoped); begin
            Expected := M.L.Exact_Value (Bytes, (False, Bytes'First, Bytes'Length));
         end;
      else return False; end if;
      if V.Is_Integer (Data, Raw) then return Number (Data, Raw) = Expected;
      elsif V.Valid_Bytes (Data, Raw) then
         declare Bytes : constant E.Bytes := V.Bytes_Value (Data, Raw); begin
            return M.L.Exact_Value (Bytes, (False, Bytes'First, Bytes'Length)) = Expected;
         end;
      else return False; end if;
   end Base_Quantity_Matches;
   function Num (Data : E.Bytes; Item : E.Span; Expected : Integer) return Boolean is
     (V.Is_Integer (Data, Item) and then Number (Data, Item) = To_Big_Integer (Expected));
   function Bytes_Text (Data : E.Bytes; Item : E.Span; Word : String) return Boolean is
   begin
      if not V.Valid_Bytes (Data, Item) then return False; end if;
      declare Raw : constant E.Bytes := V.Bytes_Value (Data, Item); begin
         return Raw'Length = Word'Length and then
           (for all I in Word'Range => Raw (Raw'First + Q.Byte_Count (I - Word'First)) =
             Q.Byte (Character'Pos (Word (I))));
      end;
   end Bytes_Text;
   function Has (Data : E.Bytes; Item : E.Span; Fields : String) return Boolean is
      Start : Positive := Fields'First;
   begin
      if not V.Valid (Data, Item) then return False; end if;
      for I in Fields'Range loop
         if Fields (I) = ',' then
            if I = Start or else not Present (Data, F (Data, Item, Fields (Start .. I - 1))) then return False; end if;
            Start := I + 1;
         end if;
      end loop;
      return Start <= Fields'Last and then Present (Data, F (Data, Item, Fields (Start .. Fields'Last)));
   end Has;
   function Identity (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (Has (Data, Left, "device,inode,mode,uid,gid,fdinfo") and then
      Has (Data, Right, "device,inode,mode,uid,gid,fdinfo") and then
      Same (Data, F (Data, Left, "device"), F (Data, Right, "device")) and then
      Same (Data, F (Data, Left, "inode"), F (Data, Right, "inode")) and then
      Same (Data, F (Data, Left, "mode"), F (Data, Right, "mode")) and then
      Same (Data, F (Data, Left, "uid"), F (Data, Right, "uid")) and then
      Same (Data, F (Data, Left, "gid"), F (Data, Right, "gid")));
   function Receipt (Data : E.Bytes; Item, Source : E.Span; Call : String;
                     Result : Integer := 0) return Boolean is
     (Text (Data, F (Data, Item, "call"), Call) and then
      V.Valid (Data, F (Data, Item, "args")) and then
      Same (Data, F (Data, Item, "source"), Source) and then
      Num (Data, F (Data, Item, "result"), Result) and then
      Num (Data, F (Data, Item, "errno"), 0));
   function X5 (Value : L.Parsed_Input; Index : Q.Byte_Count) return E.Span is
     (if Index in Value.Events'Range then
        SF (Value.Arena, Value.Events (Index).Record_Archive, "x5") else (1, 0));
   function Raw_Profile (Value : L.Parsed_Input; Index : Q.Byte_Count) return E.Span is
     (if Index in Value.Extras'Range and then Value.Extras (Index).Root_Evidence_Encoding = L.Operation_Original
      then Value.Extras (Index).Root_Evidence_Payload else (1, 0));
   function Original (Value : L.Parsed_Input; Index : Q.Byte_Count) return E.Span is
     (if Index in Value.Extras'Range and then Value.Extras (Index).Original_Encoding = L.Operation_Original
      then Value.Extras (Index).Original_Payload else (1, 0));
   function Reference_Index
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Ref : E.Span;
      Kind : M.Event_Kind) return Q.Byte_Count
   is
      Data : E.Bytes renames Value.Arena;
   begin
      if Index not in Value.Events'Range or else not V.Valid_Text (Data, Ref) then return 0; end if;
      for I in Value.Events'First .. Index - 1 loop
         pragma Loop_Variant (Increases => I);
         declare
            Decoded : constant D.Decoded_Event := D.Decode (Data, Value.Events (I));
            Consumer : constant D.Decoded_Event := D.Decode (Data, Value.Events (Index));
            Same_Context : constant Boolean :=
              C.S.A.Same_Encoding (Data, SF (Data, Value.Events (I).Base_Archive, "operation"),
                                       SF (Data, Value.Events (Index).Base_Archive, "operation")) and then
              C.S.A.Same_Encoding (Data, SF (Data, Value.Events (I).Base_Archive, "generation"),
                                       SF (Data, Value.Events (Index).Base_Archive, "generation"));
            Successor_Context : constant Boolean :=
              Decoded.Status = D.Decoded and then Consumer.Status = D.Decoded and then
              Consumer.Value.Kind = M.Front_Owned_Event and then
              Kind in M.Front_Reconstruction_Event | M.Historical_Settlement_Event and then
              Q.Span_Valid (Data, Decoded.Value.Generation) and then
              Q.Span_Valid (Data, Consumer.Value.Generation) and then
              M.L.Exact_Value (Data, Consumer.Value.Generation) =
                M.L.Exact_Value (Data, Decoded.Value.Generation) + 1;
         begin
            if Decoded.Status = D.Decoded and then Decoded.Value.Kind = Kind and then
               V.Text_Matches (Data, Ref, Value.Events (I).Event_Id) and then
               (Same_Context or else Successor_Context) then return I; end if;
         end;
      end loop;
      return 0;
   end Reference_Index;
   function Root_Reference_Index
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Ref : E.Span;
      Kind : M.Event_Kind; Before : M.Root_State) return Q.Byte_Count
   is
      Data : E.Bytes renames Value.Arena;
   begin
      if Index not in Value.Events'Range or else not V.Valid_Text (Data, Ref) or else
         not Q.Span_Valid (Data, Before.Generation) then return 0; end if;
      for I in Value.Events'First .. Index - 1 loop
         pragma Loop_Variant (Increases => I);
         declare Event : constant D.Decoded_Event := D.Decode (Data, Value.Events (I)); begin
            if Event.Status = D.Decoded and then Event.Value.Kind = Kind and then
               Event.Value.Kind_Of_Subject = M.Root and then
               Q.Span_Valid (Data, Event.Value.Generation) and then
               Q.Compare (Data, Event.Value.Generation, Before.Generation) = Q.Equal and then
               M.L.Optional_Same (Data, Event.Value.Operation, Before.Operation) and then
               V.Text_Matches (Data, Ref, Value.Events (I).Event_Id)
            then return I; end if;
         end;
      end loop;
      return 0;
   end Root_Reference_Index;
   function Prior (Value : L.Parsed_Input; Index : Q.Byte_Count; Ref : E.Span;
                   Kind : M.Event_Kind) return Boolean is
     (Reference_Index (Value, Index, Ref, Kind) /= 0);
   function Native_Item (Value : L.Parsed_Input; Index : Q.Byte_Count; Role : String)
      return E.Span
   is
      Items : constant E.Span :=
        (if Index in Value.Extras'Range and then Value.Extras (Index).Native_Observations_Encoding = L.Operation_Original
         then Value.Extras (Index).Native_Observations_Payload else (1, 0));
      Found : E.Span := (1, 0);
   begin
      if not V.Is_Sequence (Value.Arena, Items) then return Found; end if;
      for I in E.Count range 1 .. V.Count (Value.Arena, Items) loop
         declare Item : constant E.Span := V.Element (Value.Arena, Items, I - 1); begin
            if Text (Value.Arena, F (Value.Arena, Item, "role"), Role) then
               if Found.Length /= 0 then return (1, 0); end if;
               Found := Item;
            end if;
         end;
      end loop;
      return Found;
   end Native_Item;
   function Capture (Value : L.Parsed_Input; Index : Q.Byte_Count; Role : String)
      return E.Span
   is
      Items : constant E.Span := F (Value.Arena, Raw_Profile (Value, Index), "captures");
      Found : E.Span := (1, 0);
   begin
      if not V.Is_Sequence (Value.Arena, Items) then return Found; end if;
      for I in E.Count range 1 .. V.Count (Value.Arena, Items) loop
         declare Item : constant E.Span := V.Element (Value.Arena, Items, I - 1); begin
            if Text (Value.Arena, F (Value.Arena, Item, "role"), Role) then
               if Found.Length /= 0 then return (1, 0); end if;
               Found := F (Value.Arena, Item, "provenance");
            end if;
         end;
      end loop;
      return Found;
   end Capture;
   function Native_Inventory (Value : L.Parsed_Input; Index : Q.Byte_Count;
                              Role : String) return E.Span
   is
      Data : E.Bytes renames Value.Arena;
      Provenance : constant E.Span := Capture (Value, Index, Role);
      Packet : E.Span := F (Data, Provenance, "owned_descriptor_roster");
   begin
      if not Present (Data, Packet) then Packet := F (Data, Provenance, "complete_scoped_capture"); end if;
      if not Present (Data, Packet) then Packet := Provenance; end if;
      return F (Data, Packet, "inventory");
   end Native_Inventory;
   function Native_Capture_Joined
     (Data : E.Bytes; Observation, Material, Provenance : E.Span; Role : String)
      return Boolean
   is
      Obs : E.Span renames Observation;
   begin
      if Role = "root-admission" or else Role = "root-execution" then
         declare Native : constant R.Root_Replay_Result := R.Reestablish_Root_Observation (Data, Obs); begin
            return Native.State = R.Native_Redecided and then
              Native.Mode = R.J.Root_Controller_Admission and then
              Native.Native_Status = R.J.Root_Ready_Conjunction and then
              R.Root_Material_Matches (Data, Obs, Material) and then
              R.Root_Capture_Matches (Data, Obs, Provenance) and then
              Worldline.Scoped_Capture_Projection.Scoped_Capture_Matches (Data, Obs, Provenance);
         end;
      elsif Role = "scoped-check" or else Role = "scoped-validate" or else Role = "scoped-classify" then
         declare Native : constant R.Scoped_Replay_Result := R.Reestablish_Scoped_Observation (Data, Obs); begin
            return Native.State = R.Native_Redecided and then
              ((Role = "scoped-check" and then Native.Roster_Entry = R.Check_Entry) or else
               (Role = "scoped-validate" and then Native.Roster_Entry = R.Validate_Entry) or else
               (Role = "scoped-classify" and then Native.Roster_Entry = R.Classify_Entry)) and then
              R.Scoped_Material_Matches (Data, Obs, Material) and then
              Worldline.Scoped_Capture_Projection.Scoped_Capture_Matches (Data, Obs, Provenance);
         end;
      else return False; end if;
   end Native_Capture_Joined;
   function Native_Capture_Joined
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Role : String)
      return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Item : constant E.Span := Native_Item (Value, Index, Role);
      Provenance : constant E.Span := Capture (Value, Index, Role);
   begin
      return Value.Status = L.Parsed and then Index in Value.Events'Range and then
        Same (Data, Provenance, F (Data, Item, "provenance")) and then
        Native_Capture_Joined (Data, F (Data, Item, "observation"),
          F (Data, Item, "material"), Provenance, Role) and then
        (if Role = "root-admission" or else Role = "root-execution" then
          Same (Data, F (Data, Provenance, "original_request"),
                      F (Data, Raw_Profile (Value, Index), "request")) else True);
   end Native_Capture_Joined;
   function Root_Ready (Value : L.Parsed_Input; Index : Q.Byte_Count; Role : String)
      return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Item : constant E.Span := Native_Item (Value, Index, Role);
      Obs : constant E.Span := F (Data, Item, "observation");
      Native : constant R.Root_Replay_Result := R.Reestablish_Root_Observation (Data, Obs);
   begin
      return Native.State = R.Native_Redecided and then
        Native.Mode = R.J.Root_Controller_Admission and then
        Native.Native_Status = R.J.Root_Ready_Conjunction and then
        Native_Capture_Joined (Value, Index, Role) and then
        Native.Id (O.Operation_Id).Present and then
        C.G.Origin_Matches (Data, Value.Events (Index).Operation,
                           Native.Id (O.Operation_Id).Value);
   end Root_Ready;
   function Scoped
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Role : String;
      Scoped_Item : R.Scoped_Entry; Status : Interfaces.Unsigned_32;
      Command : R.J.L.Operation := R.J.L.Unknown_Operation;
      Require_Command : Boolean := False) return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Item : constant E.Span := Native_Item (Value, Index, Role);
      Obs : constant E.Span := F (Data, Item, "observation");
      Native : constant R.Scoped_Replay_Result := R.Reestablish_Scoped_Observation (Data, Obs);
   begin
      if Index not in Value.Events'Range then return False; end if;
      return Native.State = R.Native_Redecided and then Native.Roster_Entry = Scoped_Item and then
        Native.Native_Status = Status and then
        (not Require_Command or else Native.Original_Command = Command) and then
        Native_Capture_Joined (Value, Index, Role) and then
        ((Scoped_Item = R.Validate_Entry and then Native.Original_Command = R.J.L.Unknown_Operation) or else
         (CV.Valid_Hex_Field (Data, SF (Data, Value.Events (Index).Base_Archive, "operation"), "value") and then
          R.Scoped_Identity_Matches (Data, Obs,
            CV.Hex_Value (Data, SF (Data, Value.Events (Index).Base_Archive, "operation"), "value"))));
   end Scoped;
   function Operation
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Item : E.Span;
      Command : O.Command; Status : O.Decision) return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Obs : constant E.Span := SF (Data, Item, "observation");
      Material : constant E.Span := SF (Data, Item, "material");
      Event : constant E.Span := SF (Data, Item, "event");
      Native : constant R.Operation_Replay_Result := R.Reestablish_Operation_Observation (Data, Obs);
      Events : constant E.Span := SF (Data, X5 (Value, Index), "operation_journal_events");
      Found : Boolean := False;
   begin
      if Index not in Value.Events'Range or else not CV.Is_Sequence (Data, Events) then return False; end if;
      for I in E.Count range 1 .. CV.Count (Data, Events) loop
         if S.A.Same_Encoding (Data, Event, CV.Element (Data, Events, I - 1)) then Found := True; end if;
      end loop;
      return Found and then Native.State = R.Native_Redecided and then
        Native.Roster_Entry = R.Authority_Entry and then Native.Command = Command and then
        Native.Native_Status = Status and then Native.Id (O.Operation_Id).Present and then
        C.G.Origin_Matches (Data, Value.Events (Index).Operation, Native.Id (O.Operation_Id).Value) and then
        R.Operation_Capture_Matches (Data, Obs, Material, Event);
   end Operation;
   function Operation_Item (Value : L.Parsed_Input; Index : Q.Byte_Count; Event : E.Span)
      return E.Span
   is
      Items : constant E.Span := SF (Value.Arena, X5 (Value, Index), "operation_authority_observations");
      Found : E.Span := (1, 0);
   begin
      if not CV.Is_Sequence (Value.Arena, Items) then return Found; end if;
      for I in E.Count range 1 .. CV.Count (Value.Arena, Items) loop
         declare Item : constant E.Span := CV.Element (Value.Arena, Items, I - 1); begin
            if Scoped_Matches_Raw (Value.Arena, SF (Value.Arena, Item, "event"), Event) then
               if Found.Length /= 0 then return (1, 0); end if;
               Found := Item;
            end if;
         end;
      end loop;
      return Found;
   end Operation_Item;
   function Poll (Data : E.Bytes; Item, Source : E.Span; Terminal : Boolean)
      return Boolean
   is
      Args : constant E.Span := F (Data, Item, "args");
      Mask : constant E.Span := F (Data, Item, "revents");
   begin
      return Receipt (Data, Item, Source, "poll", (if Terminal then 1 else 0)) and then
        Num (Data, F (Data, Args, "events"), 25) and then
        Num (Data, F (Data, Args, "timeout"), 0) and then
        V.Is_Integer (Data, F (Data, Args, "fd")) and then
        Number (Data, F (Data, Args, "fd")) >= 0 and then
        (if Terminal then Num (Data, Mask, 1) or else Num (Data, Mask, 16) or else
                          Num (Data, Mask, 17)
         else Num (Data, Mask, 0));
   end Poll;
   function Decimal (Raw : E.Bytes; First, Last : E.Count)
      return Valid_Big_Integer
   is
      Result : Valid_Big_Integer := To_Big_Integer (0);
   begin
      if First not in Raw'Range or else Last not in Raw'Range or else First > Last
      then return To_Big_Integer (-1); end if;
      for I in First .. Last loop
         if Raw (I) not in Character'Pos ('0') .. Character'Pos ('9') then
            return To_Big_Integer (-1);
         end if;
         Result := Result * 10 + To_Big_Integer (Integer (Raw (I) - Character'Pos ('0')));
      end loop;
      return Result;
   end Decimal;
   function Scalar_Bytes (Data : E.Bytes; Item : E.Span) return E.Bytes is
     (if V.Valid_Bytes (Data, Item) then V.Bytes_Value (Data, Item)
      else CV.Bytes_Value (Data, Item))
      with Pre => V.Valid_Bytes (Data, Item) or else CV.Valid_Bytes (Data, Item);
   function Stat_Field (Data : E.Bytes; Item : E.Span; Field : Positive)
      return Valid_Big_Integer
   is
      Closing : E.Count := 0;
      Ordinal : Positive := 3;
      Start : E.Count := 0;
   begin
      if not (V.Valid_Bytes (Data, Item) or else CV.Valid_Bytes (Data, Item)) then return To_Big_Integer (-1); end if;
      declare Raw : constant E.Bytes := Scalar_Bytes (Data, Item); begin
         for I in Raw'Range loop
            if Raw (I) = Character'Pos (')') then Closing := I; end if;
         end loop;
         if Closing = 0 or else Closing = Raw'Last then return To_Big_Integer (-1); end if;
         if Field = 1 then
            for I in Raw'Range loop
               if Raw (I) = Character'Pos (' ') then return Decimal (Raw, Raw'First, I - 1); end if;
            end loop;
            return To_Big_Integer (-1);
         end if;
         for I in Closing + 1 .. Raw'Last loop
            if Raw (I) /= Character'Pos (' ') and then Raw (I) /= Character'Pos (LF) then
               if Start = 0 then Start := I; end if;
            elsif Start /= 0 then
               if Ordinal = Field then return Decimal (Raw, Start, I - 1); end if;
               if Ordinal = Positive'Last then return To_Big_Integer (-1); end if;
               Ordinal := Ordinal + 1; Start := 0;
            end if;
         end loop;
         if Start /= 0 and then Ordinal = Field then return Decimal (Raw, Start, Raw'Last); end if;
      end;
      return To_Big_Integer (-1);
   end Stat_Field;
   function Pidfd_Pid (Data : E.Bytes; Item : E.Span) return Valid_Big_Integer is
      Found : Boolean := False;
      Result : Valid_Big_Integer := To_Big_Integer (-1);
   begin
      if not (V.Valid_Bytes (Data, Item) or else CV.Valid_Bytes (Data, Item)) then return Result; end if;
      declare
         Raw : constant E.Bytes := Scalar_Bytes (Data, Item);
         Start : E.Count := Raw'First;
      begin
         for I in Raw'Range loop
            if Raw (I) = Character'Pos (LF) then
               if I - Start >= 6 and then Raw (Start) = Character'Pos ('P') and then
                  Raw (Start + 1) = Character'Pos ('i') and then
                  Raw (Start + 2) = Character'Pos ('d') and then
                  Raw (Start + 3) = Character'Pos (':') and then
                  Raw (Start + 4) = Character'Pos (Ada.Characters.Latin_1.HT)
               then
                  if Found then return To_Big_Integer (-1); end if;
                  Found := True; Result := Decimal (Raw, Start + 5, I - 1);
               end if;
               if I < Raw'Last then Start := I + 1; end if;
            end if;
         end loop;
      end;
      return Result;
   end Pidfd_Pid;
   function Process_Live
     (Data : E.Bytes; Item, Source : E.Span; Opened_Pid : E.Span := (1, 0)) return Boolean
   is
      Recorded : constant E.Span := F (Data, Item, "recorded");
      Opened : constant E.Span := F (Data, Item, "pidfd_open");
   begin
      return Has (Data, Recorded, "boot,pid,start_tick") and then
        Same (Data, F (Data, Recorded, "boot"), F (Data, Item, "current_boot")) and then
        V.Is_Integer (Data, F (Data, Recorded, "pid")) and then
        V.Is_Integer (Data, F (Data, Recorded, "start_tick")) and then
        Number (Data, F (Data, Recorded, "pid")) > 0 and then
        Number (Data, F (Data, Recorded, "start_tick")) >= 0 and then
        V.Valid_Bytes (Data, F (Data, Item, "pidfd_info")) and then
        V.Valid_Bytes (Data, F (Data, Item, "stat")) and then
        Text (Data, F (Data, Opened, "call"), "pidfd_open") and then
        Same (Data, F (Data, Opened, "source"), Source) and then
        Same (Data, F (Data, F (Data, Opened, "args"), "pid"),
          (if Opened_Pid.Length = 0 then F (Data, Recorded, "pid") else Opened_Pid)) and then
        Num (Data, F (Data, F (Data, Opened, "args"), "flags"), 0) and then
        V.Is_Integer (Data, F (Data, Opened, "result")) and then
        Number (Data, F (Data, Opened, "result")) >= 0 and then
        Num (Data, F (Data, Opened, "errno"), 0) and then
        Same (Data, F (Data, F (Data, F (Data, Item, "poll"), "args"), "fd"),
                    F (Data, Opened, "result")) and then
        Poll (Data, F (Data, Item, "poll"), Source, False) and then
        Pidfd_Pid (Data, F (Data, Item, "pidfd_info")) = Number (Data, F (Data, Recorded, "pid")) and then
        Stat_Field (Data, F (Data, Item, "stat"), 1) = Number (Data, F (Data, Recorded, "pid")) and then
        Stat_Field (Data, F (Data, Item, "stat"), 22) = Number (Data, F (Data, Recorded, "start_tick"));
   end Process_Live;
   function Process_Gone (Data : E.Bytes; Item, Source : E.Span; Live_Front : Boolean)
      return Boolean
   is
      Recorded : constant E.Span := F (Data, Item, "recorded");
      Opened : constant E.Span := F (Data, Item, "pidfd_open");
   begin
      if not Has (Data, Recorded, "boot,pid") or else
         not V.Is_Integer (Data, F (Data, Recorded, "pid")) or else
         Number (Data, F (Data, Recorded, "pid")) <= 0 then return False; end if;
      if Live_Front then
         return Identity (Data, F (Data, Item, "origin"), F (Data, Item, "current")) and then
           Poll (Data, F (Data, Item, "poll"), Source, True);
      end if;
      if V.Valid_Bytes (Data, F (Data, Recorded, "boot")) and then
         V.Valid_Bytes (Data, F (Data, Item, "current_boot")) and then
         not Same (Data, F (Data, Recorded, "boot"), F (Data, Item, "current_boot"))
      then return True; end if;
      if not Same (Data, F (Data, Recorded, "boot"), F (Data, Item, "current_boot")) or else
         not Text (Data, F (Data, Opened, "call"), "pidfd_open") or else
         not Same (Data, F (Data, Opened, "source"), Source) or else
         not Same (Data, F (Data, F (Data, Opened, "args"), "pid"), F (Data, Recorded, "pid")) or else
         not Num (Data, F (Data, F (Data, Opened, "args"), "flags"), 0)
      then return False; end if;
      if Num (Data, F (Data, Opened, "result"), -1) and then
         Num (Data, F (Data, Opened, "errno"), 3) then return True; end if;
      return V.Is_Integer (Data, F (Data, Recorded, "start_tick")) and then
        V.Is_Integer (Data, F (Data, Opened, "result")) and then
        Number (Data, F (Data, Opened, "result")) >= 0 and then
        Num (Data, F (Data, Opened, "errno"), 0) and then
        Same (Data, F (Data, F (Data, F (Data, Item, "poll"), "args"), "fd"),
                    F (Data, Opened, "result")) and then
        Poll (Data, F (Data, Item, "poll"), Source, False) and then
        Pidfd_Pid (Data, F (Data, Item, "pidfd_info")) = Number (Data, F (Data, Recorded, "pid")) and then
        Stat_Field (Data, F (Data, Item, "stat"), 1) = Number (Data, F (Data, Recorded, "pid")) and then
        Stat_Field (Data, F (Data, Item, "stat"), 22) >= 0 and then
        Stat_Field (Data, F (Data, Item, "stat"), 22) /= Number (Data, F (Data, Recorded, "start_tick"));
   end Process_Gone;
   function Actor_Identity (Data : E.Bytes; Left, Right : E.Span) return Boolean;
   function Worker_Live_Joined
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Item : E.Span;
      Before : M.Root_State) return Boolean;
   function Raw_Role_Socket
     (Data : E.Bytes; Socket, Document, Source : E.Span) return Boolean
   is
      Original : constant E.Span := F (Data, Document, "socket");
      function Call_Joined (Name : String; Option, Size : Integer) return Boolean is
         Now : constant E.Span := F (Data, Socket, Name);
         Old : constant E.Span := F (Data, Original, Name);
      begin
         if not Text (Data, F (Data, Now, "call"), (if Option = 0 then "getpeername" else "getsockopt")) or else
            not Same (Data, F (Data, Now, "call"), F (Data, Old, "call")) or else
            not V.Is_Integer (Data, F (Data, Now, "result")) or else
            not V.Is_Integer (Data, F (Data, Now, "errno")) or else
            not Same (Data, F (Data, Now, "fd"), F (Data, Socket, "fd")) or else
            not Same (Data, F (Data, Now, "source"), Source) or else
            not Same (Data, F (Data, Now, "result"), F (Data, Old, "result")) or else
            not Same (Data, F (Data, Now, "errno"), F (Data, Old, "errno")) then return False; end if;
         if Option /= 0 and then
            (not Num (Data, F (Data, Now, "level"), 1) or else
             not Num (Data, F (Data, Now, "option"), Option) or else
             not Num (Data, F (Data, Now, "requested"), Size) or else
             not V.Valid_Bytes (Data, F (Data, Now, "raw")) or else
             not V.Is_Integer (Data, F (Data, Now, "length")) or else
             Number (Data, F (Data, Now, "length")) /= Extent_Number (V.Bytes_Value (Data, F (Data, Now, "raw"))'Length) or else
             not Same (Data, F (Data, Now, "length"), F (Data, Old, "length"))) then return False; end if;
         if Num (Data, F (Data, Now, "result"), -1) then
            return Number (Data, F (Data, Now, "errno")) > 0 and then
              V.Valid_Bytes (Data, F (Data, Now, "raw")) and then
              V.Valid_Bytes (Data, F (Data, Old, "raw")) and then
              Same (Data, F (Data, Now, "raw"), F (Data, Old, "raw"));
         end if;
         if not Num (Data, F (Data, Now, "result"), 0) or else
            not Num (Data, F (Data, Now, "errno"), 0) or else
            not V.Valid_Bytes (Data, F (Data, Now, "raw")) or else
            not V.Valid_Bytes (Data, F (Data, Old, "raw")) then return False; end if;
         if Name /= "peercred" then return Same (Data, F (Data, Now, "raw"), F (Data, Old, "raw")); end if;
         declare
            Actual : constant E.Bytes := V.Bytes_Value (Data, F (Data, Now, "raw"));
            Prior : constant E.Bytes := V.Bytes_Value (Data, F (Data, Old, "raw"));
         begin
            return Actual'Length = 12 and then Prior'Length = 12 and then
              (for all I in E.Count range 4 .. 11 => Actual (Actual'First + I) = Prior (Prior'First + I));
         end;
      end Call_Joined;
   begin
      return Text (Data, F (Data, Document, "schema"), "worldline.custody-role-socket-v1") and then
        Identity (Data, F (Data, F (Data, Socket, "fstat"), "identity"),
          F (Data, F (Data, Original, "fstat"), "identity")) and then
        Text (Data, F (Data, F (Data, Socket, "fstat"), "call"), "fstat") and then
        Same (Data, F (Data, F (Data, F (Data, Socket, "fstat"), "args"), "fd"), F (Data, Socket, "fd")) and then
        Same (Data, F (Data, Socket, "source"), Source) and then
        Same (Data, F (Data, F (Data, Socket, "fstat"), "fd"), F (Data, Socket, "fd")) and then
        Num (Data, F (Data, F (Data, Socket, "fstat"), "result"), 0) and then
        Num (Data, F (Data, F (Data, Socket, "fstat"), "errno"), 0) and then
        Same (Data, F (Data, F (Data, Socket, "fstat"), "source"), Source) and then
        Call_Joined ("peercred", 17, 12) and then Call_Joined ("domain", 39, 4) and then
        Call_Joined ("type", 3, 4) and then Call_Joined ("peername", 0, 0);
   end Raw_Role_Socket;
   function Raw_Roles_Joined
     (Data : E.Bytes; Actual, Original, Broker, Source : E.Span) return Boolean
   is
      Sender : constant E.Span := F (Data, Broker, "root_roles");
      Broker_Source : constant E.Span := F (Data, Broker, "source");
      Broker_Actor : constant E.Span := F (Data, Broker, "actor");
      Count : constant E.Count := V.Count (Data, Original);
   begin
      if not V.Is_Sequence (Data, Actual) or else not V.Is_Sequence (Data, Original) or else
         not V.Is_Sequence (Data, Sender) or else Count = 0 or else
         V.Count (Data, Actual) /= Count or else V.Count (Data, Sender) /= Count then return False; end if;
      for I in E.Count range 0 .. Count - 1 loop
         pragma Loop_Variant (Increases => I);
         declare
            A : constant E.Span := V.Element (Data, Actual, I);
            O : constant E.Span := V.Element (Data, Original, I);
            B : constant E.Span := V.Element (Data, Sender, I);
            K : constant E.Span := F (Data, B, "kcmp");
            Args : constant E.Span := F (Data, K, "args");
            Fl : constant E.Span := F (Data, A, "flock");
            Mode : constant Valid_Big_Integer := Number (Data, F (Data, F (Data, A, "origin"), "mode"));
         begin
            if not Same (Data, F (Data, A, "role"), F (Data, O, "role")) or else
               not Same (Data, F (Data, B, "role"), F (Data, O, "role")) or else
               not Identity (Data, F (Data, A, "origin"), F (Data, O, "identity")) or else
               not Identity (Data, F (Data, A, "current"), F (Data, A, "origin")) or else
               not Identity (Data, F (Data, B, "origin"), F (Data, O, "identity")) or else
               not Identity (Data, F (Data, B, "current"), F (Data, A, "current")) or else
               not Same (Data, F (Data, A, "front_fd"), F (Data, O, "fd")) or else
               not Same (Data, F (Data, B, "front_fd"), F (Data, O, "fd")) or else
               not Same (Data, F (Data, A, "worker_fd"), F (Data, B, "worker_fd")) or else
               not Receipt (Data, F (Data, A, "fstat"), Source, "fstat") or else
               not Same (Data, F (Data, F (Data, F (Data, A, "fstat"), "args"), "fd"), F (Data, A, "worker_fd")) or else
               not Identity (Data, F (Data, F (Data, A, "fstat"), "identity"), F (Data, A, "current")) or else
               not Same (Data, F (Data, A, "front_actor"), F (Data, O, "front_actor")) or else
               not Same (Data, F (Data, B, "front_actor"), F (Data, O, "front_actor")) or else
               not Identity (Data, F (Data, B, "worker_pidfd"), F (Data, O, "worker_pidfd")) or else
               not Same (Data, F (Data, B, "lock_path"), F (Data, O, "lock_path")) or else
               not Actor_Identity (Data, Broker_Actor, F (Data, O, "front_actor")) or else
               not Identity (Data, F (Data, A, "worker_pidfd"), F (Data, O, "worker_pidfd")) or else
               not Identity (Data, F (Data, Broker, "worker_pidfd"), F (Data, O, "worker_pidfd")) or else
               not Receipt (Data, K, Broker_Source, "kcmp") or else
               not Num (Data, F (Data, Args, "type"), 0) or else
               not Same (Data, F (Data, Args, "idx1"), F (Data, O, "fd")) or else
               not Same (Data, F (Data, Args, "idx2"), F (Data, A, "worker_fd")) or else
               Stat_Field (Data, F (Data, Broker_Actor, "stat"), 1) /= Number (Data, F (Data, Args, "pid1")) or else
               Pidfd_Pid (Data, F (Data, F (Data, O, "worker_pidfd"), "fdinfo")) /= Number (Data, F (Data, Args, "pid2")) or else
               not Same (Data, F (Data, Args, "pid2"), F (Data, Broker, "worker_host_pid")) or else
               not Same (Data, F (Data, A, "lock_path"), F (Data, O, "lock_path"))
            then return False; end if;
            if Mode < 0 then return False; end if;
            if Mode / 4_096 mod 16 = 12 then
               if not Raw_Role_Socket (Data, F (Data, A, "socket"), F (Data, O, "socket_document"), Source) or else
                  not Same (Data, F (Data, F (Data, A, "socket"), "fd"), F (Data, A, "worker_fd")) then return False; end if;
            elsif not V.Is_Null (Data, F (Data, A, "socket")) or else
                  not V.Is_Null (Data, F (Data, O, "socket_document")) then return False; end if;
            if not V.Is_Null (Data, F (Data, O, "lock_path")) then
               if not Receipt (Data, Fl, Source, "flock") or else
                  not Num (Data, F (Data, F (Data, Fl, "args"), "operation"), 6) or else
                  not Same (Data, F (Data, F (Data, Fl, "args"), "fd"), F (Data, A, "worker_fd")) then return False; end if;
            elsif not V.Is_Null (Data, Fl) then return False; end if;
            for J in E.Count range 0 .. I - 1 loop
               pragma Loop_Variant (Increases => J);
               if Same (Data, F (Data, A, "role"), F (Data, V.Element (Data, Actual, J), "role")) or else
                  Same (Data, F (Data, A, "front_fd"), F (Data, V.Element (Data, Actual, J), "front_fd")) or else
                  Same (Data, F (Data, A, "worker_fd"), F (Data, V.Element (Data, Actual, J), "worker_fd")) then return False; end if;
            end loop;
         end;
      end loop;
      return True;
   end Raw_Roles_Joined;
   function Scoped_Roles_Joined
     (Data : E.Bytes; Original, Actual, Inventory : E.Span) return Boolean
   is
      Scoped_Original : constant E.Span := F (Data, F (Data, Inventory, "frame"), "original_roles");
      Scoped_Actual : constant E.Span := F (Data, Inventory, "roles");
      Scoped_Broker : constant E.Span := F (Data, F (Data, Inventory, "sender_role_roster"), "roles");
      Root_Broker : constant E.Span := F (Data, F (Data, Inventory, "sender_role_roster"), "root_roles");
      Seen : E.Count := 0;
      function Scoped_Name (Root_Name, Name : E.Span) return Boolean is
      begin
         if not V.Valid_Text (Data, Root_Name) or else not V.Valid_Text (Data, Name) then return False; end if;
         declare
            R : constant E.Bytes := V.Text_Value (Data, Root_Name);
            S : constant E.Bytes := V.Text_Value (Data, Name);
            Prefix : constant String := "scoped/";
         begin
            return R'Length >= Prefix'Length and then R'Length - Prefix'Length = S'Length and then
              (for all I in Prefix'Range => R (R'First + E.Count (I - 1)) = Character'Pos (Prefix (I))) and then
              (for all I in E.Count range 1 .. S'Length =>
                R (R'First + Prefix'Length + I - 1) = S (S'First + I - 1));
         end;
      end Scoped_Name;
      function Has_Scoped_Prefix (Name : E.Span) return Boolean is
      begin
         if not V.Valid_Text (Data, Name) then return False; end if;
         declare
            Bytes : constant E.Bytes := V.Text_Value (Data, Name);
            Prefix : constant String := "scoped/";
         begin
            return Bytes'Length >= Prefix'Length and then
              (for all I in Prefix'Range => Bytes (Bytes'First + E.Count (I - 1)) = Character'Pos (Prefix (I)));
         end;
      end Has_Scoped_Prefix;
   begin
      if not V.Is_Sequence (Data, Scoped_Original) or else not V.Is_Sequence (Data, Scoped_Actual) or else
         not V.Is_Sequence (Data, Scoped_Broker) or else
         V.Count (Data, Scoped_Original) /= V.Count (Data, Scoped_Actual) or else
         V.Count (Data, Scoped_Original) /= V.Count (Data, Scoped_Broker) then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Original) loop
         declare
            O : constant E.Span := V.Element (Data, Original, I - 1);
            A : constant E.Span := V.Element (Data, Actual, I - 1);
            B : constant E.Span := V.Element (Data, Root_Broker, I - 1);
            Found : Boolean := False;
         begin
            for J in E.Count range 1 .. V.Count (Data, Scoped_Original) loop
               declare
                  SO : constant E.Span := V.Element (Data, Scoped_Original, J - 1);
                  SA : constant E.Span := V.Element (Data, Scoped_Actual, J - 1);
                  SB : constant E.Span := V.Element (Data, Scoped_Broker, J - 1);
               begin
                  if Scoped_Name (F (Data, O, "role"), F (Data, SO, "role")) then
                     if Found or else not Same (Data, F (Data, O, "fd"), F (Data, SO, "fd")) or else
                        not Identity (Data, F (Data, O, "identity"), F (Data, SO, "identity")) or else
                        not Same (Data, F (Data, A, "worker_fd"), F (Data, SA, "worker_fd")) or else
                        not Identity (Data, F (Data, A, "current"), F (Data, SA, "current")) or else
                        not Same (Data, F (Data, B, "kcmp"), F (Data, SB, "kcmp")) then return False; end if;
                     Found := True;
                     Seen := Seen + 1;
                  end if;
               end;
            end loop;
            if Has_Scoped_Prefix (F (Data, O, "role")) and then not Found then return False; end if;
         end;
      end loop;
      return Seen = V.Count (Data, Scoped_Original);
   end Scoped_Roles_Joined;
   function Raw_Right_Matches (Data : E.Bytes; Raw, Descriptor : E.Span) return Boolean is
   begin
      if not V.Valid_Bytes (Data, Raw) or else not V.Is_Integer (Data, Descriptor) then return False; end if;
      declare
         Bytes : constant E.Bytes := V.Bytes_Value (Data, Raw);
         Value : Valid_Big_Integer := To_Big_Integer (0);
         Factor : Valid_Big_Integer := To_Big_Integer (1);
      begin
         if Bytes'Length /= 4 or else Bytes (Bytes'Last) >= 128 then return False; end if;
         for B of Bytes loop
            Value := Value + To_Big_Integer (Integer (B)) * Factor;
            Factor := Factor * 256;
         end loop;
         return Value = Number (Data, Descriptor);
      end;
   end Raw_Right_Matches;
   function Raw_Control_Matches (Data : E.Bytes; Part : E.Span) return Boolean is
      Controls : constant E.Span := F (Data, Part, "controls");
      Rights_Found, Credentials_Found : Boolean := False;
   begin
      if not V.Is_Sequence (Data, Controls) or else V.Count (Data, Controls) /= 2 or else
         not V.Valid_Bytes (Data, F (Data, Part, "sender")) then return False; end if;
      if V.Bytes_Value (Data, F (Data, Part, "sender"))'Length /= 12 then return False; end if;
      for I in E.Count range 0 .. 1 loop
         declare Item : constant E.Span := V.Element (Data, Controls, I); begin
            if not V.Is_Sequence (Data, Item) or else V.Count (Data, Item) /= 3 or else
               not Num (Data, V.Element (Data, Item, 0), 1) then return False; end if;
            if Num (Data, V.Element (Data, Item, 1), 1) then
               if Rights_Found or else not Same (Data, V.Element (Data, Item, 2), F (Data, Part, "rights")) then return False; end if;
               Rights_Found := True;
            elsif Num (Data, V.Element (Data, Item, 1), 2) then
               if Credentials_Found or else not Same (Data, V.Element (Data, Item, 2), F (Data, Part, "sender")) then return False; end if;
               Credentials_Found := True;
            else return False; end if;
         end;
      end loop;
      return Rights_Found and then Credentials_Found;
   end Raw_Control_Matches;
   function Raw_Transfer_Joined
     (Data : E.Bytes; Transfer, Original, Original_Send, Sender_Source, Receiver_Source,
      Current_Actor, Namespace_Source : E.Span) return Boolean
   is
      Actual : constant E.Span := F (Data, Transfer, "roles");
      Sent : constant E.Span := F (Data, Transfer, "send");
      Received : constant E.Span := F (Data, Transfer, "receive");
      Send_Parts : constant E.Span := F (Data, Sent, "parts");
      Receive_Parts : constant E.Span := F (Data, Received, "parts");
      Sender_Channel : constant E.Span := F (Data, Transfer, "send_channel");
      Receiver_Channel : constant E.Span := F (Data, Transfer, "receive_channel");
      Count : constant E.Count := V.Count (Data, Original);
      function Stream_Matches (Stream, Parts : E.Span) return Boolean is
      begin
         if not V.Valid_Bytes (Data, F (Data, Stream, "frame")) or else
            not V.Valid_Bytes (Data, F (Data, Stream, "rights")) or else
            not V.Is_Integer (Data, F (Data, Stream, "result")) then return False; end if;
         declare
            Frame : constant E.Bytes := V.Bytes_Value (Data, F (Data, Stream, "frame"));
            Rights : constant E.Bytes := V.Bytes_Value (Data, F (Data, Stream, "rights"));
         begin
            if Frame'Length /= Count or else Rights'Length / 4 /= Count or else Rights'Length mod 4 /= 0 or else
               Number (Data, F (Data, Stream, "result")) /= Extent_Number (Count) or else
               not Num (Data, F (Data, Stream, "errno"), 0) then return False; end if;
            for I in E.Count range 0 .. Count - 1 loop
               declare Part : constant E.Span := V.Element (Data, Parts, I); begin
                  if not V.Valid_Bytes (Data, F (Data, Part, "rights")) then return False; end if;
                  declare Part_Rights : constant E.Bytes := V.Bytes_Value (Data, F (Data, Part, "rights")); begin
                     if Frame (Frame'First + I) /= Character'Pos ('F') or else Part_Rights'Length /= 4 or else
                        not (for all J in E.Count range 0 .. 3 =>
                          Rights (Rights'First + I * 4 + J) = Part_Rights (Part_Rights'First + J)) or else
                        not Same (Data, F (Data, Part, "fd"), F (Data, Stream, "fd")) then return False; end if;
                  end;
               end;
            end loop;
            return True;
         end;
      end Stream_Matches;
   begin
      if Count = 0 or else not V.Is_Sequence (Data, Original) or else
         not V.Is_Sequence (Data, Actual) or else V.Count (Data, Actual) /= Count or else
         not V.Is_Sequence (Data, Send_Parts) or else V.Count (Data, Send_Parts) /= Count or else
         not V.Is_Sequence (Data, Receive_Parts) or else V.Count (Data, Receive_Parts) /= Count or else
         not V.Is_Sequence (Data, Original_Send) or else V.Count (Data, Original_Send) /= Count or else
         not Raw_Role_Socket (Data, Sender_Channel, F (Data, Transfer, "send_channel_document"),
           F (Data, Sender_Channel, "source")) or else
         not Raw_Role_Socket (Data, Receiver_Channel, F (Data, Transfer, "receive_channel_document"), Receiver_Source) or else
         not Same (Data, F (Data, Sent, "fd"), F (Data, Sender_Channel, "fd")) or else
         not Same (Data, F (Data, Received, "fd"), F (Data, Receiver_Channel, "fd")) or else
         not Same (Data, F (Data, Sent, "source"), Sender_Source) or else
         not Same (Data, F (Data, Received, "source"), Receiver_Source) or else
         not Same (Data, F (Data, Transfer, "frame"), F (Data, Sent, "frame")) or else
         not Same (Data, F (Data, Transfer, "frame"), F (Data, Received, "frame")) or else
         not Num (Data, F (Data, Sent, "flags"), 16_384) or else
         not Num (Data, F (Data, Received, "flags"), 0) or else
         not Num (Data, F (Data, Received, "input_flags"), 1_073_741_824) then return False; end if;
      for I in E.Count range 0 .. Count - 1 loop
         declare
            Send : constant E.Span := V.Element (Data, Send_Parts, I);
            Receive : constant E.Span := V.Element (Data, Receive_Parts, I);
            Old_Role : constant E.Span := V.Element (Data, Original, I);
            Current_Role : constant E.Span := V.Element (Data, Actual, I);
            Old_Send : constant E.Span := V.Element (Data, Original_Send, I);
         begin
            if not Receipt (Data, Send, Sender_Source, "sendmsg", 1) or else
               not Receipt (Data, Receive, Receiver_Source, "recvmsg", 1) or else
               not Bytes_Text (Data, F (Data, Send, "frame"), "F") or else
               not Bytes_Text (Data, F (Data, Receive, "frame"), "F") or else
               not Same (Data, F (Data, Send, "raw"), F (Data, Send, "frame")) or else
               not Same (Data, F (Data, Receive, "raw"), F (Data, Receive, "frame")) or else
               not Raw_Right_Matches (Data, F (Data, Send, "rights"), F (Data, Old_Role, "fd")) or else
               not Raw_Right_Matches (Data, F (Data, Receive, "rights"), F (Data, Current_Role, "worker_fd")) or else
               not Raw_Control_Matches (Data, Send) or else not Raw_Control_Matches (Data, Receive) or else
               not Worldline.Scoped_Capture_Namespace_Projection.SCM_Credentials_Match
                 (Data, Send, Receive, F (Data, Old_Role, "front_actor"), Current_Actor, Namespace_Source) or else
               not Same (Data, F (Data, Receive, "sender"), F (Data, Transfer, "received_sender")) or else
               not Same (Data, F (Data, Send, "sender"), F (Data, F (Data, Old_Role, "front_actor"), "credentials")) or else
               not Num (Data, F (Data, Send, "flags"), 16_384) or else
               not Num (Data, F (Data, Receive, "flags"), 0) or else
               not Num (Data, F (Data, Receive, "input_flags"), 1_073_741_824) or else
               not Same (Data, F (Data, Send, "fd"), F (Data, Old_Send, "fd")) or else
               not Same (Data, F (Data, Send, "frame"), F (Data, Old_Send, "frame")) or else
               not Same (Data, F (Data, Send, "rights"), F (Data, Old_Send, "rights")) or else
               not Same (Data, F (Data, Send, "sender"), F (Data, Old_Send, "sender")) or else
               not Same (Data, F (Data, Send, "source"), F (Data, Old_Send, "source")) or else
               not Same (Data, F (Data, Send, "controls"), F (Data, Old_Send, "controls")) or else
               not Same (Data, F (Data, Send, "args"), F (Data, Old_Send, "args")) or else
               not Same (Data, F (Data, F (Data, Send, "args"), "channel"),
                 F (Data, F (Data, Sender_Channel, "fstat"), "identity")) or else
               not Same (Data, F (Data, F (Data, Receive, "args"), "channel"),
                 F (Data, F (Data, Receiver_Channel, "fstat"), "identity")) or else
               not Same (Data, F (Data, F (Data, Send, "args"), "peer"), F (Data, F (Data, Sender_Channel, "peercred"), "raw")) or else
               not Same (Data, F (Data, F (Data, Receive, "args"), "peer"), F (Data, F (Data, Receiver_Channel, "peercred"), "raw")) or else
               not Same (Data, F (Data, F (Data, Send, "args"), "body"), F (Data, Send, "frame")) or else
               not Same (Data, F (Data, F (Data, Receive, "args"), "body"), F (Data, Receive, "frame")) or else
               not V.Is_Sequence (Data, F (Data, F (Data, Send, "args"), "rights")) or else
               V.Count (Data, F (Data, F (Data, Send, "args"), "rights")) /= 1 or else
               not V.Is_Sequence (Data, F (Data, F (Data, Receive, "args"), "rights")) or else
               V.Count (Data, F (Data, F (Data, Receive, "args"), "rights")) /= 1 or else
               not Same (Data, V.Element (Data, F (Data, F (Data, Send, "args"), "rights"), 0), F (Data, Old_Role, "fd")) or else
               not Same (Data, V.Element (Data, F (Data, F (Data, Receive, "args"), "rights"), 0), F (Data, Current_Role, "worker_fd"))
            then return False; end if;
         end;
      end loop;
      return Stream_Matches (Sent, Send_Parts) and then Stream_Matches (Received, Receive_Parts);
   end Raw_Transfer_Joined;
   function Prior_Root_Index
     (Value : L.Parsed_Input; Index, Context_Index : Q.Byte_Count; Kind : M.Event_Kind)
      return Q.Byte_Count
   is
      Data : E.Bytes renames Value.Arena;
      Found : Q.Byte_Count := 0;
   begin
      if Index not in Value.Events'Range or else Context_Index not in Value.Events'Range or else
         Index <= Value.Events'First then return 0; end if;
      for I in Value.Events'First .. Index - 1 loop
         declare Event : constant D.Decoded_Event := D.Decode (Data, Value.Events (I)); begin
            if Event.Status = D.Decoded and then Event.Value.Kind = Kind and then
               Event.Value.Kind_Of_Subject = M.Root and then
               S.A.Same_Encoding (Data, SF (Data, Value.Events (I).Base_Archive, "operation"),
                 SF (Data, Value.Events (Context_Index).Base_Archive, "operation")) and then
               S.A.Same_Encoding (Data, SF (Data, Value.Events (I).Base_Archive, "generation"),
                 SF (Data, Value.Events (Context_Index).Base_Archive, "generation"))
            then Found := I; end if;
         end;
      end loop;
      return Found;
   end Prior_Root_Index;
   function Full_Root_Roster_Joined
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Provenance, Inventory : E.Span)
      return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Intake : constant E.Span := F (Data, F (Data, Provenance, "owner"), "subject_intake");
      Transfer : constant E.Span := F (Data, Intake, "transfer");
      Original_Roles : constant E.Span := F (Data, Transfer, "roster");
      Broker : constant E.Span := F (Data, Inventory, "sender_role_roster");
      Source : constant E.Span := F (Data, Inventory, "current_source");
      Sender : constant Q.Byte_Count := Prior_Root_Index (Value, Index, Index, M.Transfer_Sent_Event);
      Sender_Profile : constant E.Span := Raw_Profile (Value, Sender);
      Broker_Source : constant E.Span := F (Data, Broker, "source");
      Old_Source : constant E.Span := F (Data, Sender_Profile, "source");
      Send_Source : constant E.Span := F (Data, F (Data, Transfer, "send"), "source");
      Sent_Frame : constant E.Span := F (Data, Original (Value, Sender), "frame");
      Namespace_Source : constant E.Span := F (Data, Inventory, "namespace_source");
      Namespace_Context : constant E.Span := F (Data, Namespace_Source, "root_context");
      Receiver_Actor : constant E.Span := F (Data, F (Data, Namespace_Source, "receiver_actor_namespace"), "actor");
      Execution : constant Q.Byte_Count := Reference_Index
        (Value, Index, F (Data, F (Data, Namespace_Context, "execution_event"), "event_id"), M.Execution_Native_Event);
   begin
      return Sender /= 0 and then Native_Capture_Joined (Value, Index, "root-admission") and then
        Worldline.Scoped_Capture_Projection.Role_Roster_Matches (Data, Inventory) and then
        Same (Data, F (Data, Broker_Source, "envelope_path"), F (Data, Old_Source, "envelope_path")) and then
        Same (Data, F (Data, Broker_Source, "envelope_bytes_hex"), F (Data, Old_Source, "envelope_bytes_hex")) and then
        Same (Data, F (Data, Broker_Source, "interpreter"), F (Data, Old_Source, "interpreter")) and then
        Actor_Identity (Data, F (Data, Broker, "actor"), F (Data, Sender_Profile, "actor")) and then
        (if Present (Data, Namespace_Context) then
          Execution /= 0 and then
          Same (Data, F (Data, Namespace_Context, "original_root_frame"), Sent_Frame) and then
          Same (Data, F (Data, Namespace_Context, "current_transfer"), Transfer) and then
          Same (Data, F (Data, F (Data, Namespace_Context, "execution_event"), "record"), Original (Value, Execution))
         else True) and then
        Same (Data, F (Data, Receiver_Actor, "boot"), F (Data, F (Data, Inventory, "current_actor"), "boot")) and then
        Same (Data, F (Data, Receiver_Actor, "pid"), F (Data, F (Data, Inventory, "current_actor"), "pid")) and then
        Same (Data, F (Data, Receiver_Actor, "start_tick"), F (Data, F (Data, Inventory, "current_actor"), "start_tick")) and then
        Same (Data, Original_Roles, F (Data, F (Data, Sent_Frame, "subject_custody"), "roles")) and then
        Same (Data, F (Data, Send_Source, "envelope_path"), F (Data, Old_Source, "envelope_path")) and then
        Same (Data, F (Data, Send_Source, "envelope_bytes_hex"), F (Data, Old_Source, "envelope_bytes_hex")) and then
        Same (Data, F (Data, Send_Source, "interpreter"), F (Data, Old_Source, "interpreter")) and then
        Raw_Roles_Joined (Data, F (Data, Transfer, "roles"), Original_Roles, Broker, Source) and then
        Scoped_Roles_Joined (Data, Original_Roles, F (Data, Transfer, "roles"), Inventory) and then
        Raw_Transfer_Joined (Data, Transfer, Original_Roles,
          F (Data, F (Data, Original (Value, Sender), "actual_send"), "send"), Send_Source, Source,
          Receiver_Actor, Namespace_Source);
   end Full_Root_Roster_Joined;
   function Broker_Lock_Joined
     (Data : E.Bytes; Now, Provenance, Inventory : E.Span) return Boolean
   is
      Intake : constant E.Span := F (Data, F (Data, Provenance, "owner"), "subject_intake");
      Original : constant E.Span := F (Data, F (Data, Intake, "transfer"), "roster");
      Current : constant E.Span := F (Data, F (Data, Intake, "transfer"), "roles");
      Broker : constant E.Span := F (Data, Inventory, "sender_role_roster");
      Sender : constant E.Span := F (Data, Broker, "root_roles");
      Found : Boolean := False;
   begin
      if not V.Is_Sequence (Data, Original) or else not V.Is_Sequence (Data, Current) or else
         not V.Is_Sequence (Data, Sender) or else V.Count (Data, Original) /= V.Count (Data, Current) or else
         V.Count (Data, Sender) /= V.Count (Data, Original) then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Original) loop
         declare
            Old_Role : constant E.Span := V.Element (Data, Original, I - 1);
            Current_Role : constant E.Span := V.Element (Data, Current, I - 1);
            Sender_Role : constant E.Span := V.Element (Data, Sender, I - 1);
         begin
            if Same (Data, F (Data, Old_Role, "lock_path"), F (Data, Now, "path")) then
               if Found or else
                  not Identity (Data, F (Data, Old_Role, "identity"), F (Data, Now, "origin")) or else
                  not Identity (Data, F (Data, Current_Role, "current"), F (Data, Now, "current")) or else
                  not Same (Data, F (Data, Current_Role, "flock"), F (Data, Now, "flock")) or else
                  not Same (Data, F (Data, Sender_Role, "kcmp"), F (Data, Now, "ofd")) or else
                  not Receipt (Data, F (Data, Now, "ofd"), F (Data, Broker, "source"), "kcmp")
               then return False; end if;
               Found := True;
            end if;
         end;
      end loop;
      return Found;
   end Broker_Lock_Joined;
   function Escrow_Lock_Joined
     (Value : L.Parsed_Input; Index, Execution : Q.Byte_Count; Now : E.Span) return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Closed : constant Q.Byte_Count := Prior_Root_Index
        (Value, Index, Execution, M.Front_Close_Intent_Event);
      Sent : constant Q.Byte_Count := Prior_Root_Index
        (Value, Index, Execution, M.Transfer_Sent_Event);
      Old_Locks : constant E.Span := F (Data, Raw_Profile (Value, Closed), "locks");
      Roles : constant E.Span := F (Data, F (Data, F (Data, Original (Value, Sent), "frame"), "subject_custody"), "roles");
      Duplicates : constant E.Span := F (Data, F (Data, Raw_Profile (Value, Sent), "transfer"), "duplicates");
      Current_Duplicates : constant E.Span := F (Data, Now, "duplicates");
      Opened : E.Span := (1, 0);
      Role : E.Span := (1, 0);
      Found : Boolean := False;
      function Fresh_Acquisition_Joined return Boolean is
         Dup : constant E.Span := F (Data, Now, "current_acquisition");
         Kernel : constant E.Span := F (Data, Dup, "ofd");
         Inventory : constant E.Span := F (Data, Dup, "before");
         Pid : constant E.Span := F (Data, F (Data, Raw_Profile (Value, Index), "actor"), "pid");
         Source : constant E.Span := F (Data, Raw_Profile (Value, Index), "source");
         Held : Boolean := False;
         Retained : Boolean := False;
      begin
         if Same (Data, Dup, Opened) then return True; end if;
         if not Text (Data, F (Data, Dup, "call"), "dup") or else
            not Same (Data, F (Data, F (Data, Dup, "args"), "fd"), F (Data, Role, "fd")) or else
            not V.Is_Integer (Data, F (Data, Dup, "result")) or else
            Number (Data, F (Data, Dup, "result")) < 0 or else
            not Same (Data, F (Data, Dup, "api_result"), F (Data, Dup, "result")) or else
            not Num (Data, F (Data, Dup, "errno"), 0) or else
            not Same (Data, F (Data, Dup, "source"), Source) or else
            not Identity (Data, F (Data, Dup, "identity"), F (Data, Now, "origin")) or else
            not Same (Data, F (Data, Dup, "proc_link"), F (Data, Opened, "proc_link")) or else
            not V.Valid_Bytes (Data, F (Data, Dup, "proc_fdinfo")) or else
            not Receipt (Data, Kernel, Source, "kcmp") or else
            not Num (Data, F (Data, F (Data, Kernel, "args"), "type"), 0) or else
            not Same (Data, F (Data, F (Data, Kernel, "args"), "pid1"), Pid) or else
            not Same (Data, F (Data, F (Data, Kernel, "args"), "pid2"), Pid) or else
            not Same (Data, F (Data, F (Data, Kernel, "args"), "idx1"), F (Data, Role, "fd")) or else
            not Same (Data, F (Data, F (Data, Kernel, "args"), "idx2"), F (Data, Dup, "result")) or else
            not V.Is_Sequence (Data, Inventory)
         then return False; end if;
         for I in E.Count range 1 .. V.Count (Data, Inventory) loop
            declare Before_Fd : constant E.Span := V.Element (Data, Inventory, I - 1); begin
               if Same (Data, F (Data, Before_Fd, "fd"), F (Data, Role, "fd")) then
                  if Held or else
                     not Identity (Data, F (Data, Before_Fd, "identity"), F (Data, Now, "origin")) or else
                     not Same (Data, F (Data, Before_Fd, "link"), F (Data, Opened, "proc_link")) or else
                     not V.Valid_Bytes (Data, F (Data, Before_Fd, "fdinfo"))
                  then return False; end if;
                  Held := True;
               end if;
            end;
         end loop;
         for I in E.Count range 1 .. V.Count (Data, Current_Duplicates) loop
            declare Edge : constant E.Span := V.Element (Data, Current_Duplicates, I - 1); begin
               if Same (Data, F (Data, Edge, "receipt"), Dup) and then
                  Same (Data, F (Data, Edge, "ofd"), Kernel) then Retained := True; end if;
            end;
         end loop;
         return Held and then Retained;
      end Fresh_Acquisition_Joined;
   begin
      if Closed = 0 or else Sent <= Closed or else
         not V.Is_Sequence (Data, Old_Locks) or else not V.Is_Sequence (Data, Roles) or else
         not V.Is_Sequence (Data, Duplicates) or else not V.Is_Sequence (Data, Current_Duplicates)
      then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Old_Locks) loop
         declare Old : constant E.Span := V.Element (Data, Old_Locks, I - 1); begin
            if Same (Data, F (Data, Old, "path"), F (Data, Now, "path")) then
               if Present (Data, Opened) or else not Identity (Data, F (Data, Old, "origin"), F (Data, Now, "origin"))
               then return False; end if;
               Opened := F (Data, Old, "open");
            end if;
         end;
      end loop;
      for I in E.Count range 1 .. V.Count (Data, Roles) loop
         declare Item : constant E.Span := V.Element (Data, Roles, I - 1); begin
            if Same (Data, F (Data, Item, "lock_path"), F (Data, Now, "path")) and then
               Same (Data, F (Data, Item, "fd"), F (Data, F (Data, F (Data, Now, "flock"), "args"), "fd"))
            then
               if Present (Data, Role) then return False; end if;
               Role := Item;
            end if;
         end;
      end loop;
      if not Present (Data, Role) or else not Same (Data, Opened, F (Data, Now, "open")) or else
         not Text (Data, F (Data, Opened, "call"), "open") or else
         not Same (Data, F (Data, F (Data, Opened, "args"), "path"), F (Data, Now, "path")) or else
         not Num (Data, F (Data, Opened, "errno"), 0) or else
         not V.Is_Integer (Data, F (Data, Opened, "result")) or else
         Number (Data, F (Data, Opened, "result")) < 0 or else
         not Identity (Data, F (Data, Opened, "identity"), F (Data, Now, "origin")) or else
         not Identity (Data, F (Data, Role, "identity"), F (Data, Now, "current"))
      then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Duplicates) loop
         declare
            Edge : constant E.Span := V.Element (Data, Duplicates, I - 1);
            Dup : constant E.Span := F (Data, Edge, "receipt");
            Kernel : constant E.Span := F (Data, Edge, "ofd");
            Inventory : constant E.Span := F (Data, Dup, "before");
            Source : constant E.Span := F (Data, Dup, "source");
            Pid : constant E.Span := F (Data, F (Data, Raw_Profile (Value, Closed), "actor"), "pid");
            Held : Boolean := False;
            Retained : Boolean := False;
         begin
            if Same (Data, F (Data, F (Data, Dup, "args"), "fd"), F (Data, Opened, "result")) and then
               Same (Data, F (Data, Dup, "result"), F (Data, Role, "fd"))
            then
               if Found or else not Text (Data, F (Data, Dup, "call"), "dup") or else
                  not Same (Data, F (Data, Dup, "api_result"), F (Data, Dup, "result")) or else
                  not Num (Data, F (Data, Dup, "errno"), 0) or else
                  not Same (Data, Source, F (Data, Opened, "source")) or else
                  not Identity (Data, F (Data, Dup, "identity"), F (Data, Role, "identity")) or else
                  not Same (Data, F (Data, Dup, "proc_link"), F (Data, Opened, "proc_link")) or else
                  not V.Valid_Bytes (Data, F (Data, Dup, "proc_fdinfo")) or else
                  not Same (Data, Kernel, F (Data, Dup, "ofd")) or else
                  not Receipt (Data, Kernel, Source, "kcmp") or else
                  not Num (Data, F (Data, F (Data, Kernel, "args"), "type"), 0) or else
                  not Same (Data, F (Data, F (Data, Kernel, "args"), "pid1"), Pid) or else
                  not Same (Data, F (Data, F (Data, Kernel, "args"), "pid2"), Pid) or else
                  not Same (Data, F (Data, F (Data, Kernel, "args"), "idx1"), F (Data, Opened, "result")) or else
                  not Same (Data, F (Data, F (Data, Kernel, "args"), "idx2"), F (Data, Role, "fd")) or else
                  not V.Is_Sequence (Data, Inventory)
               then return False; end if;
               for J in E.Count range 1 .. V.Count (Data, Inventory) loop
                  declare Before_Fd : constant E.Span := V.Element (Data, Inventory, J - 1); begin
                     if Same (Data, F (Data, Before_Fd, "fd"), F (Data, Opened, "result")) then
                        if Held or else
                           not Identity (Data, F (Data, Before_Fd, "identity"), F (Data, Opened, "identity")) or else
                           not Same (Data, F (Data, Before_Fd, "link"), F (Data, Opened, "proc_link")) or else
                           not V.Valid_Bytes (Data, F (Data, Before_Fd, "fdinfo"))
                        then return False; end if;
                        Held := True;
                     end if;
                  end;
               end loop;
               for J in E.Count range 1 .. V.Count (Data, Current_Duplicates) loop
                  if Same (Data, Edge, V.Element (Data, Current_Duplicates, J - 1)) then Retained := True; end if;
               end loop;
               if not Held or else not Retained then return False; end if;
               Found := True;
            end if;
         end;
      end loop;
      return Found and then Fresh_Acquisition_Joined;
   end Escrow_Lock_Joined;
   function Locks_Joined
     (Value : L.Parsed_Input; Index : Q.Byte_Count;
      Roster, Locks, Source, Actor : E.Span;
      Fresh : Boolean := False; Ofd : Boolean := True;
      Provenance : E.Span := (1, 0); Inventory : E.Span := (1, 0);
      Acquisition_Event : Q.Byte_Count := 0)
      return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Broker_Checked : constant Boolean :=
        Ofd and then Present (Data, Provenance) and then Present (Data, Inventory) and then
        Full_Root_Roster_Joined (Value, Index, Provenance, Inventory);
   begin
      if not V.Is_Sequence (Data, Roster) or else not V.Is_Sequence (Data, Locks) or else
         V.Count (Data, Roster) = 0 or else V.Count (Data, Roster) /= V.Count (Data, Locks)
      then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Roster) loop
         declare
            Old : constant E.Span := V.Element (Data, Roster, I - 1);
            Now : constant E.Span := V.Element (Data, Locks, I - 1);
            Opened : constant E.Span := F (Data, Now, "open");
            Fl : constant E.Span := F (Data, Now, "flock");
            Kcmp : constant E.Span := F (Data, Now, "ofd");
            Named_Open : constant E.Span := F (Data, Now, "named_open");
            Named_Close : constant E.Span := F (Data, Now, "named_close");
         begin
            if not Same (Data, F (Data, Old, "path"), F (Data, Now, "path")) or else
               not Identity (Data, F (Data, Old, "identity"), F (Data, Now, "origin")) or else
               not Identity (Data, F (Data, Now, "origin"), F (Data, Now, "current")) or else
               not Identity (Data, F (Data, Now, "current"), F (Data, Now, "named")) or else
               not (Receipt (Data, Fl, Source, "flock") or else
                 (Broker_Checked and then
                  Receipt (Data, Fl, F (Data, Inventory, "current_source"), "flock") and then
                  Broker_Lock_Joined (Data, Now, Provenance, Inventory))) or else
               not Num (Data, F (Data, F (Data, Fl, "args"), "operation"), 6)
            then return False; end if;
            if not Text (Data, F (Data, Named_Open, "call"), "open") or else
               not (Same (Data, F (Data, Named_Open, "source"), Source) or else
                 (Broker_Checked and then
                  Same (Data, F (Data, Named_Open, "source"), F (Data, Inventory, "current_source")))) or else
               not Same (Data, F (Data, F (Data, Named_Open, "args"), "path"), F (Data, Now, "path")) or else
               not Num (Data, F (Data, F (Data, Named_Open, "args"), "flags"), 655360) or else
               not V.Is_Integer (Data, F (Data, Named_Open, "result")) or else
               Number (Data, F (Data, Named_Open, "result")) < 0 or else
               not Num (Data, F (Data, Named_Open, "errno"), 0) or else
               not Receipt (Data, Named_Close, F (Data, Named_Open, "source"), "close") or else
               not Same (Data, F (Data, F (Data, Named_Close, "args"), "fd"), F (Data, Named_Open, "result"))
            then return False; end if;
            if Fresh and then not
               ((Text (Data, F (Data, Opened, "call"), "open") and then
                 Same (Data, F (Data, Opened, "source"), Source) and then
                 Same (Data, F (Data, F (Data, Opened, "args"), "path"), F (Data, Now, "path")) and then
                 V.Is_Integer (Data, F (Data, Opened, "result")) and then
                 Number (Data, F (Data, Opened, "result")) >= 0 and then
                 Num (Data, F (Data, Opened, "errno"), 0) and then
                 Same (Data, F (Data, F (Data, Fl, "args"), "fd"), F (Data, Opened, "result"))) or else
                Escrow_Lock_Joined (Value, Index, Acquisition_Event, Now))
            then return False; end if;
            if Ofd and then
               (not Num (Data, F (Data, F (Data, Kcmp, "args"), "type"), 0) or else
                not Has (Data, F (Data, Kcmp, "args"), "pid1,pid2,idx1,idx2") or else
                not ((Receipt (Data, Kcmp, Source, "kcmp") and then
                  Same (Data, F (Data, F (Data, Kcmp, "args"), "pid1"), F (Data, Actor, "pid")) and then
                  Same (Data, F (Data, F (Data, Kcmp, "args"), "pid2"), F (Data, Actor, "pid")) and then
                  Same (Data, F (Data, F (Data, Kcmp, "args"), "idx1"), F (Data, F (Data, Fl, "args"), "fd")) and then
                  Same (Data, F (Data, F (Data, Kcmp, "args"), "idx2"), F (Data, F (Data, Fl, "args"), "fd"))) or else
                  (Broker_Checked and then Broker_Lock_Joined (Data, Now, Provenance, Inventory))))
            then return False; end if;
            for J in E.Count range 1 .. I - 1 loop
               if Same (Data, F (Data, Now, "path"),
                  F (Data, V.Element (Data, Locks, J - 1), "path")) then return False; end if;
            end loop;
         end;
      end loop;
      return True;
   end Locks_Joined;
   function Worker_Gone
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State)
      return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Ecr : constant E.Span := F (Data, Profile, "ecr");
      Source : constant E.Span := F (Data, Profile, "source");
      Worker : constant E.Span := F (Data, Ecr, "worker");
      Init : constant E.Span := F (Data, Ecr, "namespace_init");
      Held : constant Q.Byte_Count := Root_Reference_Index
        (Value, Index, F (Data, Ecr, "held_event"), M.Held_Event, Before);
      Execution : constant Q.Byte_Count := Root_Reference_Index
        (Value, Index, F (Data, Ecr, "execution_event"), M.Execution_Native_Event, Before);
      Live_Front : constant Boolean := Text (Data, F (Data, Ecr, "regime"), "front-live");
      Restart : constant Boolean := Text (Data, F (Data, Ecr, "regime"), "front-restart");
   begin
      if Value.Status /= L.Parsed or else Index not in Value.Events'Range or else
         not Q.Span_Valid (Data, Before.Generation) or else Held = 0 or else Execution = 0 or else
         not (Live_Front or else Restart) or else
         not Scoped_Matches_Raw (Data, SF (Data, X5 (Value, Index), "source_identity"), Source) or else
         not Same (Data, F (Data, Worker, "recorded"),
                    F (Data, Raw_Profile (Value, Execution), "worker_identity")) or else
         not Same (Data, F (Data, Init, "recorded"),
                    F (Data, Raw_Profile (Value, Held), "init_identity")) or else
         (Live_Front and then
          (not Identity (Data, F (Data, Worker, "origin"),
             F (Data, Raw_Profile (Value, Execution), "worker_pidfd_origin")) or else
           not Identity (Data, F (Data, Init, "origin"),
             V.Element (Data, F (Data, Original (Value, Held), "descriptors"), 1)))) or else
         not Process_Gone (Data, Worker, Source, Live_Front)
      then return False; end if;
      if not Process_Gone (Data, Init, Source, Live_Front) then
         if not Restart or else
            not Poll (Data, F (Data, Raw_Profile (Value, Held), "init_held_poll"),
                           F (Data, Raw_Profile (Value, Held), "source"), True) or else
            not V.Is_Null (Data, F (Data, F (Data, Init, "recorded"), "start_tick"))
         then return False; end if;
      end if;
      return Locks_Joined (Value, Index,
        F (Data, F (Data, Raw_Profile (Value, Execution), "owner_before"), "held_locks"),
        F (Data, Ecr, "locks"), Source, F (Data, Profile, "actor"),
        Fresh => Restart, Ofd => Live_Front, Acquisition_Event => Execution);
   end Worker_Gone;
   function Worker_Liveness_Of
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State)
      return Worker_Liveness
   is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Ecr : constant E.Span := F (Data, Profile, "ecr");
      Source : constant E.Span := F (Data, Profile, "source");
      Worker : constant E.Span := F (Data, Ecr, "worker");
      Execution : constant Q.Byte_Count := Root_Reference_Index
        (Value, Index, F (Data, Ecr, "execution_event"), M.Execution_Native_Event, Before);
   begin
      if Worker_Gone (Value, Index, Before) then return Known_Gone; end if;
      if Value.Status /= L.Parsed or else Index not in Value.Events'Range or else
         Execution = 0 or else
         not Scoped_Matches_Raw (Data, SF (Data, X5 (Value, Index), "source_identity"), Source) or else
         not Same (Data, F (Data, Worker, "recorded"),
                    F (Data, Raw_Profile (Value, Execution), "worker_identity"))
      then return Uncertain; end if;
      if Text (Data, F (Data, Ecr, "regime"), "front-restart") and then
         Process_Live (Data, Worker, Source)
      then return Known_Live; end if;
      if Text (Data, F (Data, Ecr, "regime"), "front-live") and then
         Identity (Data, F (Data, Worker, "origin"),
           F (Data, Raw_Profile (Value, Execution), "worker_pidfd_origin")) and then
         Identity (Data, F (Data, Worker, "origin"), F (Data, Worker, "current")) and then
         Pidfd_Pid (Data, F (Data, F (Data, Worker, "current"), "fdinfo")) =
           Number (Data, F (Data, F (Data, Worker, "recorded"), "pid")) and then
         Poll (Data, F (Data, Worker, "poll"), Source, False)
      then return Known_Live; end if;
      return Uncertain;
   end Worker_Liveness_Of;
   function Line_Text (Data : E.Bytes; Item : E.Span; Ordinal : Positive;
                       Word : String) return Boolean
   is
      Current : Positive := 1;
   begin
      if not V.Valid_Bytes (Data, Item) then return False; end if;
      declare Raw : constant E.Bytes := V.Bytes_Value (Data, Item);
         Start : E.Count := Raw'First;
      begin
         for I in Raw'Range loop
            if Raw (I) = Character'Pos (LF) then
               if Current = Ordinal then
                  return I - Start = Word'Length and then
                    (for all J in Word'Range =>
                      Raw (Start + Q.Byte_Count (J - Word'First)) = Q.Byte (Character'Pos (Word (J))));
               end if;
               if Current = Positive'Last then return False; end if;
               Current := Current + 1;
               if I < Raw'Last then Start := I + 1; end if;
            end if;
         end loop;
      end;
      return False;
   end Line_Text;
   function Line_Value (Data : E.Bytes; Item : E.Span; Ordinal : Positive;
                        Expected : E.Span) return Boolean
   is
      Current : Positive := 1;
   begin
      if not V.Valid_Bytes (Data, Item) or else
         not (V.Valid_Text (Data, Expected) or else V.Is_Integer (Data, Expected))
      then return False; end if;
      declare Raw : constant E.Bytes := V.Bytes_Value (Data, Item);
         Start : E.Count := Raw'First;
      begin
         for I in Raw'Range loop
            if Raw (I) = Character'Pos (LF) then
               if Current = Ordinal then
                  if V.Is_Integer (Data, Expected) then
                     return Start < I and then
                       (I - Start = 1 or else Raw (Start) /= Character'Pos ('0')) and then
                       Decimal (Raw, Start, I - 1) = Number (Data, Expected);
                  end if;
                  declare Text_Raw : constant E.Bytes := V.Text_Value (Data, Expected); begin
                     return I - Start = Text_Raw'Length and then
                       (for all J in Text_Raw'Range => Text_Raw (J) = Raw (Start + J - Text_Raw'First));
                  end;
               end if;
               if Current = Positive'Last then return False; end if;
               Current := Current + 1;
               if I < Raw'Last then Start := I + 1; end if;
            end if;
         end loop;
      end;
      return False;
   end Line_Value;
   function Lines (Data : E.Bytes; Item : E.Span; Count : E.Count) return Boolean is
      Found : E.Count := 0;
   begin
      if not V.Valid_Bytes (Data, Item) then return False; end if;
      declare Raw : constant E.Bytes := V.Bytes_Value (Data, Item); begin
         if Raw'Length = 0 or else Raw (Raw'Last) /= Character'Pos (LF) then return False; end if;
         for B of Raw loop
            if B = Character'Pos (LF) then Found := Found + 1; end if;
         end loop;
      end;
      return Found = Count;
   end Lines;
   function Wait_Terminal (Data : E.Bytes; Item : E.Span) return Boolean is
   begin
      if not V.Is_Integer (Data, Item) or else Number (Data, Item) < 0 or else
         Number (Data, Item) > 65_535 then return False; end if;
      declare Status : constant Integer := To_Integer (Number (Data, Item)); begin
         return Status mod 128 = 0 or else Status mod 128 in 1 .. 126;
      end;
   end Wait_Terminal;
   function Closed_NS (Value : L.Parsed_Input; Index : Q.Byte_Count) return Boolean is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Item : constant E.Span := F (Data, Profile, "closed_ns");
      Source : constant E.Span := F (Data, Profile, "source");
      Held_Index : constant Q.Byte_Count := Reference_Index
        (Value, Index, F (Data, Item, "held_event"), M.Held_Event);
      Frame : constant E.Span := F (Data, Item, "frame");
      Ack : constant E.Span := F (Data, Item, "ack");
      Wait : constant E.Span := F (Data, Item, "namespace_wait");
      Held : constant E.Span :=
        (if Held_Index /= 0 then F (Data, Raw_Profile (Value, Held_Index), "held") else (1, 0));
   begin
      return Held_Index /= 0 and then Lines (Data, Frame, 6) and then
        Line_Text (Data, Frame, 1, "WL-ROOT-WORKER-SUPERVISOR-v1") and then
        Line_Text (Data, Frame, 2, "CLOSED") and then
        Line_Value (Data, Frame, 3, F (Data, F (Data, Held, "dispatch"), "ticket")) and then
        Line_Value (Data, Frame, 4, F (Data, Held, "init_pid")) and then
        Line_Value (Data, Frame, 5, F (Data, Item, "raw_main_wait")) and then
        Wait_Terminal (Data, F (Data, Item, "raw_main_wait")) and then
        Line_Text (Data, Frame, 6, "ECHILD") and then
        Identity (Data, F (Data, Wait, "origin"), V.Element (Data, F (Data, Held, "descriptors"), 1)) and then
        Identity (Data, F (Data, Wait, "origin"), F (Data, Wait, "current")) and then
        Poll (Data, F (Data, Wait, "poll"), Source, True) and then
        Receipt (Data, Ack, Source, "send", 1) and then
        Bytes_Text (Data, F (Data, F (Data, Ack, "args"), "body"), "A") and then
        Same (Data, F (Data, Item, "frame"), F (Data, Original (Value, Index), "frame")) and then
        Same (Data, F (Data, Item, "raw_main_wait"), F (Data, Original (Value, Index), "raw_main_wait"));
   end Closed_NS;
   function Raw_Manager_Zero (Data : E.Bytes; Item : E.Span) return Boolean is
      Seen : Boolean := False;
   begin
      if not Has (Data, Item, "argv,stdout,stderr,returncode") or else
         not Num (Data, F (Data, Item, "returncode"), 0) or else
         not V.Valid_Bytes (Data, F (Data, Item, "stdout")) then return False; end if;
      declare Raw : constant E.Bytes := V.Bytes_Value (Data, F (Data, Item, "stdout"));
         Start : E.Count := Raw'First;
      begin
         for I in Raw'Range loop
            if Raw (I) = Character'Pos (LF) then
               if I - Start >= 8 and then Raw (Start) = Character'Pos ('M') and then
                  Raw (Start + 1) = Character'Pos ('a') and then Raw (Start + 2) = Character'Pos ('i') and then
                  Raw (Start + 3) = Character'Pos ('n') and then Raw (Start + 4) = Character'Pos ('P') and then
                  Raw (Start + 5) = Character'Pos ('I') and then Raw (Start + 6) = Character'Pos ('D') and then
                  Raw (Start + 7) = Character'Pos ('=')
               then
                  if Seen or else I - Start /= 9 or else Raw (Start + 8) /= Character'Pos ('0') then return False; end if;
                  Seen := True;
               end if;
               if I < Raw'Last then Start := I + 1; end if;
            end if;
         end loop;
      end;
      return Seen;
   end Raw_Manager_Zero;
   function Closed_Outer (Value : L.Parsed_Input; Index : Q.Byte_Count) return Boolean is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Item : constant E.Span := F (Data, Profile, "closed_outer");
      Source : constant E.Span := F (Data, Profile, "source");
      NS : constant Q.Byte_Count := Reference_Index
        (Value, Index, F (Data, Item, "namespace_event"), M.Closed_NS_Event);
      Helper : constant E.Span := F (Data, Item, "helper_wait");
      Launcher : constant E.Span := F (Data, Item, "launcher_wait");
      Held_Index : constant Q.Byte_Count :=
        (if NS /= 0 then Reference_Index (Value, Index,
          F (Data, F (Data, Raw_Profile (Value, NS), "closed_ns"), "held_event"), M.Held_Event) else 0);
      Properties : constant E.Span :=
        (if Held_Index /= 0 then F (Data, Original (Value, Held_Index), "properties") else (1, 0));
   begin
      return NS /= 0 and then Held_Index /= 0 and then
        Worldline.Scoped_Capture_Projection.Property (Data, F (Data, Item, "manager"), "Id",
          V.Bytes_Key_Field (Data, Properties, "Id")) and then
        Worldline.Scoped_Capture_Projection.Property (Data, F (Data, Item, "manager"), "InvocationID",
          V.Bytes_Key_Field (Data, Properties, "InvocationID")) and then
        Worldline.Scoped_Capture_Projection.Property (Data, F (Data, Item, "manager"), "ControlGroup",
          V.Bytes_Key_Field (Data, Properties, "ControlGroup")) and then
        Identity (Data, F (Data, Helper, "origin"),
          F (Data, Raw_Profile (Value, Held_Index), "helper_pidfd_origin")) and then
        Identity (Data, F (Data, Helper, "origin"), F (Data, Helper, "current")) and then
        Poll (Data, F (Data, Helper, "poll"), Source, True) and then
        Poll (Data, F (Data, F (Data, Item, "namespace_wait"), "poll"), Source, True) and then
        Text (Data, F (Data, Launcher, "call"), "waitpid") and then
        Same (Data, F (Data, Launcher, "source"), Source) and then
        Has (Data, F (Data, Launcher, "args"), "pid,options") and then
        Num (Data, F (Data, F (Data, Launcher, "args"), "options"), 0) and then
        Same (Data, F (Data, Launcher, "result"), F (Data, F (Data, Launcher, "args"), "pid")) and then
        Num (Data, F (Data, Launcher, "errno"), 0) and then
        Wait_Terminal (Data, F (Data, Launcher, "status")) and then
        Raw_Manager_Zero (Data, F (Data, Item, "manager")) and then
        Same (Data, F (Data, Item, "manager"), F (Data, Original (Value, Index), "manager")) and then
        Same (Data, F (Data, Item, "actual_launcher_wait"), F (Data, Original (Value, Index), "actual_launcher_wait"));
   end Closed_Outer;
   function Closed_Raw (Value : L.Parsed_Input; Index : Q.Byte_Count) return Boolean is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Item : constant E.Span := F (Data, Profile, "closed_raw");
      Source : constant E.Span := F (Data, Profile, "source");
      Streams : constant E.Span := F (Data, Item, "streams");
      Out_Seen, Err_Seen : Boolean := False;
   begin
      if not V.Is_Sequence (Data, Streams) or else V.Count (Data, Streams) /= 2 or else
         not Same (Data, F (Data, Item, "result"), F (Data, Original (Value, Index), "complete_raw"))
      then return False; end if;
      for I in E.Count range 1 .. 2 loop
         declare
            Stream : constant E.Span := V.Element (Data, Streams, I - 1);
            Raw : constant E.Span := F (Data, Stream, "raw");
            Fsync : constant E.Span := F (Data, Stream, "fsync");
            EOF_Read : constant E.Span := F (Data, Stream, "eof");
         begin
            if Text (Data, F (Data, Stream, "stream"), "stdout") and then not Out_Seen then Out_Seen := True;
            elsif Text (Data, F (Data, Stream, "stream"), "stderr") and then not Err_Seen then Err_Seen := True;
            else return False; end if;
            if not V.Valid_Bytes (Data, Raw) or else
               not V.Is_Integer (Data, F (Data, Stream, "bytes")) or else
               Number (Data, F (Data, Stream, "bytes")) /= Extent_Number (V.Bytes_Value (Data, Raw)'Length) or else
               not Has (Data, Stream, "identity,path") or else
               not Receipt (Data, EOF_Read, Source, "read") or else
               not Receipt (Data, Fsync, Source, "fsync") or else
               not Same (Data, F (Data, F (Data, EOF_Read, "args"), "fd"), F (Data, Stream, "read_fd")) or else
               not Same (Data, F (Data, F (Data, Fsync, "args"), "fd"), F (Data, Stream, "write_fd"))
            then return False; end if;
         end;
      end loop;
      return Out_Seen and then Err_Seen;
   end Closed_Raw;
   function Owners_Closed (Data : E.Bytes; Owner_Roster, Closed, Source : E.Span)
      return Boolean
   is
      Owners : constant E.Span := F (Data, Owner_Roster, "owners");
   begin
      if not V.Is_Sequence (Data, Owners) or else not V.Is_Sequence (Data, Closed) or else
         V.Count (Data, Owners) = 0 or else V.Count (Data, Owners) /= V.Count (Data, Closed)
      then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Owners) loop
         declare
            Original_Owner : constant E.Span := V.Element (Data, Owners, I - 1);
            Closed_Owner : constant E.Span := V.Element (Data, Closed, I - 1);
            Close : constant E.Span := F (Data, Closed_Owner, "close");
         begin
            if not Same (Data, F (Data, Original_Owner, "owner"), F (Data, Closed_Owner, "owner"))
            then return False; end if;
            if Text (Data, F (Data, Close, "call"), "close") then
               if not Receipt (Data, Close, Source, "close") or else
                  not Same (Data, F (Data, F (Data, Close, "args"), "fd"), F (Data, Original_Owner, "fd"))
               then return False; end if;
            elsif Text (Data, F (Data, Close, "call"), "owner.close") then
               if not Text (Data, F (Data, Original_Owner, "api"), "owner.close") or else
                  not Same (Data, F (Data, Close, "source"), Source) or else
                  not V.Is_Null (Data, F (Data, Close, "result")) or else
                  not Same (Data, F (Data, F (Data, Close, "args"), "owner"), F (Data, Original_Owner, "owner"))
               then return False; end if;
               declare
                  Descriptors : constant E.Span := F (Data, F (Data, Close, "args"), "descriptors");
                  Readbacks : constant E.Span := F (Data, Close, "readback");
               begin
                  if not V.Is_Sequence (Data, Descriptors) or else not V.Is_Sequence (Data, Readbacks) or else
                     V.Count (Data, Descriptors) /= V.Count (Data, Readbacks) then return False; end if;
                  for J in E.Count range 1 .. V.Count (Data, Descriptors) loop
                     pragma Loop_Variant (Increases => J);
                     declare
                        Prior_FD : constant E.Span := V.Element (Data, Descriptors, J - 1);
                        Readback : constant E.Span := V.Element (Data, Readbacks, J - 1);
                     begin
                        if not V.Is_Integer (Data, F (Data, Prior_FD, "fd")) or else
                           Number (Data, F (Data, Prior_FD, "fd")) < 0 or else
                           not Text (Data, F (Data, Readback, "call"), "fcntl") or else
                           not Same (Data, F (Data, Readback, "source"), Source) or else
                           not Same (Data, F (Data, F (Data, Readback, "args"), "fd"), F (Data, Prior_FD, "fd")) or else
                           not Num (Data, F (Data, F (Data, Readback, "args"), "command"), 1)
                        then return False; end if;
                        if Num (Data, F (Data, Readback, "result"), -1) and then
                           Num (Data, F (Data, Readback, "errno"), 9) then null;
                        elsif V.Is_Integer (Data, F (Data, Readback, "result")) and then
                           Number (Data, F (Data, Readback, "result")) >= 0 and then
                           Num (Data, F (Data, Readback, "errno"), 0) and then
                           Identity (Data, F (Data, Prior_FD, "identity"), F (Data, Readback, "identity"))
                        then null;
                        else return False; end if;
                     end;
                  end loop;
               end;
            else return False; end if;
         end;
      end loop;
      return True;
   end Owners_Closed;
   function Quiescent (Data : E.Bytes; Item : E.Span) return Boolean is
      Background : constant E.Span := F (Data, Item, "background");
      Acquisitions : constant E.Span := F (Data, Item, "acquisitions");
   begin
      if not V.Is_Sequence (Data, Background) or else V.Count (Data, Background) /= 0 or else
         not V.Is_Sequence (Data, Acquisitions) then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Acquisitions) loop
         pragma Loop_Variant (Increases => I);
         declare
            Acquisition : constant E.Span := V.Element (Data, Acquisitions, I - 1);
            Observed : constant E.Span := F (Data, Acquisition, "observation");
            Raw : constant E.Span := F (Data, Acquisition, "observation_raw");
         begin
            if not Has (Data, Acquisition, "job,observation,observation_raw") or else
               not V.Valid_Bytes (Data, Raw) then return False; end if;
            declare
               JSON : constant E.Bytes := V.Bytes_Value (Data, Raw);
               Whole : constant E.Span := (JSON'First, JSON'Length);
            begin
               if Canonical_Artifacts.Scoped_Archive_JSON_Matches (JSON, Data, Whole, Observed) /=
                    Canonical_Artifacts.Typed_Tree_Matches_Source_Custody_Open or else
                  not Worldline.Runner_Lifecycle.Quiescent (JSON, Whole) then return False; end if;
            end;
         end;
      end loop;
      return True;
   end Quiescent;
   function MAC (Value : L.Parsed_Input; Raw, Mac_Text : E.Span; Domain : String)
      return Boolean
   is
      Data : E.Bytes renames Value.Arena;
   begin
      if not V.Valid_Bytes (Data, Raw) or else not V.Valid_Hex_Field (Data, Mac_Text, "value") or else
         not E.C.P.Valid (Data, Value.Key) then return False; end if;
      declare
         Message : constant E.Bytes := V.Bytes_Value (Data, Raw);
         Expected : constant E.Bytes := V.Hex_Value (Data, Mac_Text, "value");
      begin
         if Expected'Length /= C.SHA.Digest'Length then return False; end if;
         declare
            Digest : constant C.SHA.Digest := H.Mac
              (Data, Message, Value.Key, (Message'First, Message'Length), Domain);
         begin
            return (for all I in Digest'Range =>
              Q.Byte (Digest (I)) = Expected (Expected'First + E.Count (I - Digest'First)));
         end;
      end;
   end MAC;
   function Raw_Archive_Equal (Data : E.Bytes; Raw, Encoded : E.Span) return Boolean is
   begin
      if not V.Valid_Bytes (Data, Raw) or else not V.Valid (Data, Encoded) then return False; end if;
      declare Bytes : constant E.Bytes := V.Bytes_Value (Data, Raw); begin
         if Bytes'Length = Encoded.Length and then
            (for all I in Bytes'Range => Bytes (I) = Data (Encoded.First + I - Bytes'First))
         then return True; end if;
         return Worldline.Custody_V2_Archive_Projection.Scoped_Archive_Operation_Matches
           (Bytes, Data, (Bytes'First, Bytes'Length), Encoded);
      end;
   end Raw_Archive_Equal;
   function Prepared (Value : L.Parsed_Input; Index : Q.Byte_Count) return Boolean is
      Data : E.Bytes renames Value.Arena;
      Item : constant E.Span := F (Data, Raw_Profile (Value, Index), "prepared");
      Reserved : constant E.Span := F (Data, Item, "reserved");
      Intent : constant E.Span := F (Data, Item, "intent");
      Events : constant E.Span := SF (Data, X5 (Value, Index), "operation_journal_events");
      Reserve_Pos, Intent_Pos : E.Count := 0;
   begin
      if not CV.Is_Sequence (Data, Events) or else
         not Text (Data, F (Data, Reserved, "cause"), "RESERVED") or else
         not Text (Data, F (Data, Intent, "cause"), "EFFECT_INTENT") or else
         not Same (Data, F (Data, Reserved, "capture"), F (Data, Intent, "capture"))
      then return False; end if;
      for I in E.Count range 1 .. CV.Count (Data, Events) loop
         if Scoped_Matches_Raw (Data, CV.Element (Data, Events, I - 1), Reserved) then
            if Reserve_Pos /= 0 then return False; end if; Reserve_Pos := I;
         end if;
         if Scoped_Matches_Raw (Data, CV.Element (Data, Events, I - 1), Intent) then
            if Intent_Pos /= 0 then return False; end if; Intent_Pos := I;
         end if;
      end loop;
      return Reserve_Pos /= 0 and then Intent_Pos > Reserve_Pos and then
        Worldline.Custody_V2_Prepared.Workload (R.Reestablish_Operation_Observation (Data,
          SF (Data, Operation_Item (Value, Index, Reserved), "observation")).Action) and then
        Operation (Value, Index, Operation_Item (Value, Index, Reserved), O.Reserve_Use, O.Reserved_New) and then
        Operation (Value, Index, Operation_Item (Value, Index, Intent), O.Reserve_Use, O.Reserved_Replay);
   end Prepared;
   function Held (Value : L.Parsed_Input; Index : Q.Byte_Count) return Boolean is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Item : constant E.Span := F (Data, Profile, "held");
      Frame : constant E.Span := F (Data, Item, "frame");
      Machine : constant E.Span := F (Data, Profile, "machine");
   begin
      return Same (Data, Item, Original (Value, Index)) and then
        Has (Data, Item, "peer,init_pid,helper_pid,pidfd_info,namespace_identity,helper_pidfd_info,properties,manager,helper_proc,descriptors,source,dispatch") and then
        Same (Data, F (Data, Item, "source"), F (Data, Profile, "source")) and then
        Lines (Data, Frame, 4) and then
        Line_Text (Data, Frame, 1, "WL-ROOT-WORKER-SUPERVISOR-v1") and then
        Line_Text (Data, Frame, 2, "HELD") and then
        Line_Value (Data, Frame, 3, F (Data, F (Data, Item, "dispatch"), "ticket")) and then
        Line_Value (Data, Frame, 4, F (Data, Item, "init_pid")) and then
        Pidfd_Pid (Data, F (Data, Item, "pidfd_info")) = Number (Data, F (Data, Item, "init_pid")) and then
        V.Is_Sequence (Data, F (Data, Item, "descriptors")) and then
        V.Count (Data, F (Data, Item, "descriptors")) = 7 and then
        Scoped (Value, Index, "scoped-classify", R.Classify_Entry,
                R.J.L.Liveness'Pos (R.J.L.Live)) and then
        Scoped (Value, Index, "scoped-validate", R.Validate_Entry, 1) and then
        Text (Data, F (Data, Machine, "stage"), "DISPATCH") and then
        Worldline.Custody_V2_Machine_Evidence.Joined (Data, Machine);
   end Held;
   function Send_All (Data : E.Bytes; Receipts, Expected, Source : E.Span) return Boolean is
   begin
      if not V.Is_Sequence (Data, Receipts) or else not V.Is_Sequence (Data, Expected) or else
         V.Count (Data, Receipts) = 0 or else V.Count (Data, Receipts) /= V.Count (Data, Expected)
      then return False; end if;
      for I in E.Count range 1 .. V.Count (Data, Expected) loop
         declare
            Item : constant E.Span := V.Element (Data, Receipts, I - 1);
            Args : constant E.Span := F (Data, Item, "args");
            Rights : constant E.Span := F (Data, Args, "rights");
         begin
            if not Receipt (Data, Item, Source, "sendmsg", 1) or else
               not Bytes_Text (Data, F (Data, Args, "body"), "F") or else
               not V.Is_Sequence (Data, Rights) or else V.Count (Data, Rights) /= 1 or else
               not Same (Data, V.Element (Data, Rights, 0), F (Data, V.Element (Data, Expected, I - 1), "fd")) or else
               not Has (Data, Args, "channel,peer,flags") then return False; end if;
         end;
      end loop;
      return True;
   end Send_All;
   function Seed_Current (Value : L.Parsed_Input; Index : Q.Byte_Count) return Boolean is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Seed : constant E.Span := F (Data, Profile, "seed");
      Prefix : constant E.Span := F (Data, Seed, "prefix");
      Consumer : constant D.Decoded_Event := D.Decode (Data, Value.Events (Index));
   begin
      if Consumer.Status /= D.Decoded or else not V.Is_Sequence (Data, Prefix) or else
         V.Count (Data, Prefix) /= Index - Value.Events'First or else
         not Same (Data, F (Data, Seed, "owner"), F (Data, Profile, "owner_current"))
      then return False; end if;
      for I in Value.Events'First .. Index - 1 loop
         if not V.Text_Matches (Data, V.Element (Data, Prefix, I - Value.Events'First),
                                    Value.Events (I).Event_Id) then return False; end if;
      end loop;
      return True;
   end Seed_Current;
   function Credential_Pid (Data : E.Bytes; Item : E.Span) return Valid_Big_Integer is
      Result : Valid_Big_Integer := To_Big_Integer (0);
      Factor : Valid_Big_Integer := To_Big_Integer (1);
   begin
      if not V.Valid_Bytes (Data, Item) then return To_Big_Integer (-1); end if;
      declare Raw : constant E.Bytes := V.Bytes_Value (Data, Item); begin
         if Raw'Length /= 12 then return To_Big_Integer (-1); end if;
         for I in E.Count range 0 .. 3 loop
            Result := Result + To_Big_Integer (Integer (Raw (Raw'First + I))) * Factor;
            Factor := Factor * 256;
         end loop;
         if Raw (Raw'First + 3) >= 128 or else
            (for some I in E.Count range 4 .. 7 => Raw (Raw'First + I) /= 0)
         then return To_Big_Integer (-1); end if;
      end;
      return Result;
   end Credential_Pid;
   function Report (Value : L.Parsed_Input; Index : Q.Byte_Count;
                    Kind : M.Event_Kind) return Boolean is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Item : constant E.Span := F (Data, Profile, "report");
      Event : constant E.Span := F (Data, Item, "event");
      Execution : constant Q.Byte_Count := Reference_Index
        (Value, Index, F (Data, Item, "execution_event"), M.Execution_Native_Event);
      Receive : constant E.Span := F (Data, Item, "receive");
      Worker : constant E.Span := F (Data, Item, "worker");
      Source : constant E.Span := F (Data, Profile, "source");
   begin
      return Execution /= 0 and then
        Same (Data, F (Data, Event, "record"), Original (Value, Index)) and then
        Text (Data, F (Data, Event, "kind"), D.Kind_Name (Kind)) and then
        V.Text_Matches (Data, F (Data, Event, "operation"), Value.Events (Index).Operation) and then
        Raw_Archive_Equal (Data, F (Data, Item, "raw"), Event) and then
        Same (Data, Worker, F (Data, Raw_Profile (Value, Execution), "worker_identity")) and then
        Credential_Pid (Data, F (Data, Item, "sender_credentials")) = Number (Data, F (Data, Worker, "pid")) and then
        Same (Data, F (Data, Item, "request"), F (Data, Profile, "request")) and then
        Same (Data, F (Data, Item, "request"), F (Data, Raw_Profile (Value, Execution), "request")) and then
        Same (Data, F (Data, Item, "use"), F (Data, Profile, "use")) and then
        Same (Data, F (Data, Item, "use"), F (Data, Raw_Profile (Value, Execution), "use")) and then
        Same (Data, F (Data, Original (Value, Index), "original_request"), F (Data, Item, "request")) and then
        Receipt (Data, Receive, Source, "recvmsg", 1) and then
        Bytes_Text (Data, F (Data, F (Data, Receive, "args"), "body"), "F") and then
        Same (Data, F (Data, F (Data, Receive, "args"), "channel"), F (Data, Item, "channel")) and then
        Same (Data, F (Data, Receive, "sender_credentials"), F (Data, Item, "sender_credentials")) and then
        Num (Data, F (Data, Receive, "msg_flags"), 0) and then
        Has (Data, Item, "sealed_memfd") and then
        Num (Data, F (Data, F (Data, Item, "sealed_memfd"), "seals"), 15);
   end Report;
   function Commit_Frame (Data : E.Bytes; Frame, Measurement, Witness : E.Span)
      return Boolean
   is
   begin
      if not V.Valid_Bytes (Data, Frame) or else not V.Valid_Bytes (Data, Measurement) or else
         not V.Valid_Bytes (Data, Witness) then return False; end if;
      declare
         Raw : constant E.Bytes := V.Bytes_Value (Data, Frame);
         Measured : constant E.Bytes := V.Bytes_Value (Data, Measurement);
         Retained : constant E.Bytes := V.Bytes_Value (Data, Witness);
         Header : constant String := "WL-ROOT-WORKER-COMMIT-v1" & LF;
         Pos : E.Count := Raw'First;
         Start : E.Count;
      begin
         if Raw'Length < Header'Length or else Measured'Length = 0 or else Retained'Length = 0 or else
            not (for all I in Header'Range =>
              Raw (Raw'First + E.Count (I - Header'First)) = Q.Byte (Character'Pos (Header (I))))
         then return False; end if;
         Pos := Pos + Header'Length; Start := Pos;
         while Pos in Raw'Range and then Raw (Pos) /= Character'Pos (LF) loop
            pragma Loop_Variant (Increases => Pos);
            if Pos = Raw'Last then return False; end if; Pos := Pos + 1;
         end loop;
         if Pos not in Raw'Range or else Pos = Start or else
            (Pos - Start > 1 and then Raw (Start) = Character'Pos ('0'))
         then return False; end if;
         --  The length comparison below is independent of host integer casts.
         declare Expected : Valid_Big_Integer := To_Big_Integer (0);
            Remaining : E.Count := Measured'Length;
            Factor : Valid_Big_Integer := To_Big_Integer (1);
         begin
            while Remaining /= 0 loop
               pragma Loop_Variant (Decreases => Remaining);
               Expected := Expected + To_Big_Integer (Integer (Remaining mod 256)) * Factor;
               Remaining := Remaining / 256; Factor := Factor * 256;
            end loop;
            if Decimal (Raw, Start, Pos - 1) /= Expected then return False; end if;
         end;
         if Pos = Raw'Last or else Measured'Length > Raw'Last - Pos then return False; end if;
         Pos := Pos + 1;
         if not (for all I in Measured'Range => Measured (I) = Raw (Pos + I - Measured'First))
         then return False; end if;
         if Measured'Length > Raw'Last - Pos then return False; end if;
         Pos := Pos + Measured'Length; Start := Pos;
         while Pos in Raw'Range and then Raw (Pos) /= Character'Pos (LF) loop
            pragma Loop_Variant (Increases => Pos);
            if Pos = Raw'Last then return False; end if; Pos := Pos + 1;
         end loop;
         if Pos /= Raw'Last or else Pos = Start or else
            (Pos - Start > 1 and then Raw (Start) = Character'Pos ('0')) then return False; end if;
         declare Expected : Valid_Big_Integer := To_Big_Integer (0);
            Remaining : E.Count := Retained'Length;
            Factor : Valid_Big_Integer := To_Big_Integer (1);
         begin
            while Remaining /= 0 loop
               pragma Loop_Variant (Decreases => Remaining);
               Expected := Expected + To_Big_Integer (Integer (Remaining mod 256)) * Factor;
               Remaining := Remaining / 256; Factor := Factor * 256;
            end loop;
            return Decimal (Raw, Start, Pos - 1) = Expected;
         end;
      end;
   end Commit_Frame;
   function Ack_Receive_Frame (Data : E.Bytes; Receive : E.Span) return Boolean is
      Transport : constant E.Span := F (Data, Receive, "transport");
   begin
      if not V.Valid_Bytes (Data, F (Data, Transport, "raw")) or else
         not V.Valid_Bytes (Data, F (Data, Receive, "body")) or else
         not V.Valid_Bytes (Data, F (Data, Receive, "sender_credentials")) then return False; end if;
      declare
         Raw : constant E.Bytes := V.Bytes_Value (Data, F (Data, Transport, "raw"));
         Payload : constant E.Bytes := V.Bytes_Value (Data, F (Data, Receive, "body"));
         Peer : constant E.Bytes := V.Bytes_Value (Data, F (Data, Receive, "sender_credentials"));
         Header : constant String := "WL-ROOT-WORKER-ACK-RECEIPT-v1" & LF;
         Pos : E.Count := Raw'First;
         Start : E.Count;
         Expected : Valid_Big_Integer;
      begin
         if Raw'Length < Header'Length or else Peer'Length /= 12 or else
            not (for all I in Header'Range =>
              Raw (Raw'First + E.Count (I - Header'First)) = Q.Byte (Character'Pos (Header (I))))
         then return False; end if;
         Pos := Pos + Header'Length;
         for I in 1 .. 3 loop
            Start := Pos;
            while Pos in Raw'Range and then Raw (Pos) /= Character'Pos (LF) loop
               pragma Loop_Variant (Increases => Pos);
               if Pos = Raw'Last then return False; end if;
               Pos := Pos + 1;
            end loop;
            if Pos not in Raw'Range or else Pos = Start or else
               (Pos - Start > 1 and then Raw (Start) = Character'Pos ('0')) then return False; end if;
            Expected := (if I = 1 then Number (Data, F (Data, Receive, "result"))
              elsif I = 2 then Number (Data, F (Data, Receive, "msg_flags"))
              else Number (Data, F (Data, F (Data, Receive, "args"), "fd")));
            if Expected < 0 or else Decimal (Raw, Start, Pos - 1) /= Expected or else Pos = Raw'Last
            then return False; end if;
            Pos := Pos + 1;
         end loop;
         if Raw'Last - Pos + 1 < Peer'Length or else
            Raw'Last - Pos + 1 - Peer'Length /= Payload'Length then return False; end if;
         if not (for all I in Peer'Range => Peer (I) = Raw (Pos + I - Peer'First)) then return False; end if;
         Pos := Pos + Peer'Length;
         return (for all I in Payload'Range => Payload (I) = Raw (Pos + I - Payload'First));
      end;
   end Ack_Receive_Frame;
   function Ack (Value : L.Parsed_Input; Index : Q.Byte_Count) return Boolean is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Item : constant E.Span := F (Data, Profile, "ack");
      Execution : constant Q.Byte_Count := Reference_Index
        (Value, Index, F (Data, Item, "execution_event"), M.Execution_Native_Event);
      Witness : constant E.Span := F (Data, Item, "witness");
      Send : constant E.Span := F (Data, Item, "send");
      Receive : constant E.Span := F (Data, Item, "receive");
      Source : constant E.Span := F (Data, Profile, "source");
      Before_Exec : constant E.Span :=
        F (Data, F (Data, Raw_Profile (Value, Execution), "execution"), "before_exec");
      Measured : constant E.Span := F (Data, Before_Exec, "measured");
      Retained_Event : constant E.Span := F (Data, Original (Value, Index), "event");
      Receiver_Context : constant E.Span := F (Data, Receive, "context");
      Execution_Profile : constant E.Span := Raw_Profile (Value, Execution);
   begin
      if Execution = 0 or else not V.Valid_Bytes (Data, F (Data, Item, "frame")) then return False; end if;
      declare Length : constant E.Count := V.Bytes_Value (Data, F (Data, Item, "frame"))'Length; begin
         return Commit_Frame (Data, F (Data, Item, "frame"), F (Data, Item, "measured_frame"), F (Data, Item, "witness_raw")) and then
           Raw_Archive_Equal (Data, F (Data, Item, "witness_raw"), Witness) and then
           Same (Data, F (Data, Witness, "record"), Original (Value, Execution)) and then
           V.Text_Matches (Data, F (Data, Witness, "event_id"), Value.Events (Execution).Event_Id) and then
           Same (Data, F (Data, Retained_Event, "record"), Original (Value, Execution)) and then
           V.Text_Matches (Data, F (Data, Retained_Event, "event_id"), Value.Events (Execution).Event_Id) and then
           Same (Data, F (Data, Original (Value, Index), "ack"), F (Data, Item, "frame")) and then
           Same (Data, F (Data, Item, "ticket"), F (Data, Before_Exec, "ticket")) and then
           V.Valid_Bytes (Data, F (Data, Item, "measured_frame")) and then
           V.Valid_Hex_Field (Data, Measured, "raw_frame") and then
           V.Bytes_Value (Data, F (Data, Item, "measured_frame")) = V.Hex_Value (Data, Measured, "raw_frame") and then
           Text (Data, F (Data, Witness, "kind"), "EXECUTION_NATIVE") and then
           V.Text_Matches (Data, F (Data, Witness, "operation"), Value.Events (Index).Operation) and then
           Same (Data, F (Data, Item, "request"), F (Data, Raw_Profile (Value, Execution), "request")) and then
           Same (Data, F (Data, Item, "peer"), F (Data, F (Data, Profile, "actor"), "credentials")) and then
           Same (Data, F (Data, F (Data, Send, "args"), "body"), F (Data, Item, "frame")) and then
           Same (Data, F (Data, Receive, "body"), F (Data, Item, "frame")) and then
           Same (Data, F (Data, Receive, "sender_credentials"), F (Data, Item, "peer")) and then
           Ack_Receive_Frame (Data, Receive) and then
           Same (Data, F (Data, F (Data, Receive, "transport"), "channel"),
             F (Data, F (Data, Send, "args"), "channel")) and then
           Credential_Pid (Data, F (Data, F (Data, Receive, "transport"), "sender_credentials")) =
             Number (Data, F (Data, F (Data, Execution_Profile, "worker_identity"), "pid")) and then
           Same (Data, F (Data, F (Data, Receiver_Context, "worker"), "recorded"),
             F (Data, Execution_Profile, "worker_identity")) and then
           Process_Live (Data, F (Data, Receiver_Context, "worker"), Source) and then
           Identity (Data, F (Data, Receive, "worker_pidfd"),
             F (Data, Execution_Profile, "worker_pidfd_origin")) and then
           Same (Data, F (Data, Receiver_Context, "namespace_identity"), F (Data, Receive, "namespace_identity")) and then
           Same (Data, F (Data, Receive, "namespace_identity"),
             F (Data, F (Data, F (Data, Original (Value, Execution), "physical"), "held"), "namespace_identity")) and then
           Text (Data, F (Data, Send, "call"), "sendmsg") and then
           Text (Data, F (Data, Receive, "call"), "recvmsg") and then
           Same (Data, F (Data, Send, "source"), Source) and then
           Same (Data, F (Data, Receive, "source"), Source) and then
           V.Is_Integer (Data, F (Data, Send, "result")) and then
           V.Is_Integer (Data, F (Data, Receive, "result")) and then
           Number (Data, F (Data, Send, "result")) = Number (Data, F (Data, Receive, "result")) and then
           Number (Data, F (Data, Send, "result")) = Extent_Number (Length) and then
           Num (Data, F (Data, Send, "errno"), 0) and then Num (Data, F (Data, Receive, "errno"), 0) and then
           Num (Data, F (Data, Receive, "msg_flags"), 0) and then Length > 0;
      end;
   end Ack;
   function Reattach (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State)
      return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Item : constant E.Span := F (Data, Profile, "reattach");
      Hello : constant E.Span := F (Data, Item, "hello");
      Challenge : constant E.Span := F (Data, Item, "challenge");
      Proof : constant E.Span := F (Data, Item, "proof");
      Ready : constant E.Span := F (Data, Item, "ready");
      HB : constant E.Span := F (Data, Hello, "body");
      CB : constant E.Span := F (Data, Challenge, "body");
      PB : constant E.Span := F (Data, Proof, "body");
      RB : constant E.Span := F (Data, Ready, "body");
      Domain : constant String := "worldline.root-worker-reattach-v1" & Ada.Characters.Latin_1.NUL;
      function Message (Msg : E.Span; Kind : String) return Boolean is
        (Text (Data, F (Data, F (Data, Msg, "body"), "kind"), Kind) and then
         V.Text_Matches (Data, F (Data, F (Data, Msg, "body"), "operation"), Value.Events (Index).Operation) and then
         Base_Quantity_Matches (Data, F (Data, F (Data, Msg, "body"), "generation"),
                    SF (Data, Value.Events (Index).Base_Archive, "generation")) and then
         Raw_Archive_Equal (Data, F (Data, Msg, "raw"), F (Data, Msg, "body")) and then
         MAC (Value, F (Data, Msg, "raw"), F (Data, Msg, "mac"), Domain));
   begin
      if not Q.Span_Valid (Data, Before.Reattach_Epoch) then return False; end if;
      return Message (Hello, "HELLO") and then Message (Challenge, "CHALLENGE") and then
        Message (Proof, "PROOF") and then Message (Ready, "READY") and then
        V.Is_Integer (Data, F (Data, HB, "seen_epoch")) and then
        Number (Data, F (Data, HB, "seen_epoch")) = M.L.Exact_Value (Data, Before.Reattach_Epoch) and then
        V.Is_Integer (Data, F (Data, CB, "current_epoch")) and then
        Number (Data, F (Data, CB, "current_epoch")) = M.L.Exact_Value (Data, Before.Reattach_Epoch) and then
        V.Is_Integer (Data, F (Data, PB, "epoch")) and then
        Number (Data, F (Data, PB, "epoch")) = M.L.Exact_Value (Data, Before.Reattach_Epoch) + 1 and then
        Same (Data, F (Data, PB, "epoch"), F (Data, RB, "epoch")) and then
        Base_Quantity_Matches (Data, F (Data, PB, "epoch"),
          SF (Data, SF (Data, X5 (Value, Index), "primitive_inputs"), "reattach_epoch")) and then
        V.Valid_Bytes (Data, F (Data, HB, "nonce_f")) and then V.Bytes_Value (Data, F (Data, HB, "nonce_f"))'Length > 0 and then
        V.Valid_Bytes (Data, F (Data, CB, "nonce_w")) and then V.Bytes_Value (Data, F (Data, CB, "nonce_w"))'Length > 0 and then
        Same (Data, F (Data, HB, "nonce_f"), F (Data, CB, "nonce_f")) and then
        Same (Data, F (Data, HB, "nonce_f"), F (Data, PB, "nonce_f")) and then
        Same (Data, F (Data, CB, "nonce_w"), F (Data, PB, "nonce_w")) and then
        not Same (Data, F (Data, HB, "nonce_f"), F (Data, CB, "nonce_w")) and then
        Credential_Pid (Data, F (Data, Item, "peer")) > 0 and then
        Worker_Live_Joined (Value, Index, F (Data, Item, "worker"), Before) and then
        Has (Data, Item, "channel") and then
        Same (Data, F (Data, Item, "channel"), F (Data, F (Data, Profile, "actor"), "channel"));
   end Reattach;
   function Scoped_Commit (Value : L.Parsed_Input; Index : Q.Byte_Count;
                           Item : E.Span; Command : R.J.L.Operation) return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Obs : constant E.Span := F (Data, Item, "observation");
      Native : constant R.Scoped_Replay_Result := R.Reestablish_Scoped_Observation (Data, Obs);
      Op : constant E.Span := SF (Data, Value.Events (Index).Base_Archive, "operation");
      Provenance : constant E.Span := F (Data, Item, "provenance");
   begin
      return Native.State = R.Native_Redecided and then Native.Roster_Entry = R.Check_Entry and then
        Worldline.Scoped_Capture_Projection.Scoped_Capture_Matches (Data, Obs, Provenance) and then
        Native.Native_Status = R.S.Status'Pos (R.S.Ready) and then
        Native.Original_Command = Command and then
        R.Scoped_Material_Matches (Data, Obs, F (Data, Item, "material")) and then
        CV.Valid_Hex_Field (Data, Op, "value") and then
        R.Scoped_Identity_Matches (Data, Obs, CV.Hex_Value (Data, Op, "value")) and then
        V.Valid_Bytes (Data, F (Data, Item, "raw")) and then
        Canonical_Artifacts.Operation_Archive_JSON_Matches
          (V.Bytes_Value (Data, F (Data, Item, "raw")), Data,
           (1, V.Bytes_Value (Data, F (Data, Item, "raw"))'Length), F (Data, Item, "event")) and then
        Scoped_Matches_Raw (Data, F (Data, F (Data, Item, "event"), "packet"), F (Data, Item, "material")) and then
        Scoped_Matches_Raw (Data, F (Data, F (Data, Item, "event"), "native"), Obs);
   end Scoped_Commit;
   function Historical (Value : L.Parsed_Input; Index : Q.Byte_Count; Item : E.Span)
      return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Native : constant R.Operation_Replay_Result :=
        R.Reestablish_Operation_Observation (Data, F (Data, Item, "observation"));
      Event : constant E.Span := F (Data, Item, "event");
      Command : constant O.Command := Native.Command;
      Status : constant O.Decision := Native.Native_Status;
   begin
      return Native.State = R.Native_Redecided and then
        ((Native.Roster_Entry = R.Authority_Entry and then
          ((Command = O.Quarantine_Use and then Status = O.Quarantined_New) or else
           (Command in O.Settle_Use | O.Replay_Use and then Status in O.Settled_New | O.Settled_Replay) or else
           (Command in O.Release_Use | O.Replay_Use and then Status in O.Released_New | O.Released_Replay))) or else
         (Native.Roster_Entry = R.Historical_Completion_Entry and then Native.Historical_Status /= R.H.Refused)) and then
        -- Operation_Capture_Matches includes the complete material join.
        R.Operation_Capture_Matches (Data, F (Data, Item, "observation"), F (Data, Item, "material"), Event) and then
        Same (Data, Event, F (Data, Original (Value, Index), "complete_native_settlement")) and then
        Same (Data, F (Data, Item, "result"), F (Data, Original (Value, Index), "result")) and then
        Same (Data, F (Data, Item, "use"), F (Data, Raw_Profile (Value, Index), "use"));
   end Historical;
   function Cause_Class_Of (Value : L.Parsed_Input; Index : Q.Byte_Count)
      return M.Cause_Class
   is
      Item : constant E.Span := F (Value.Arena, Raw_Profile (Value, Index), "cause");
      Class : constant E.Span := F (Value.Arena, Item, "class");
   begin
      if Text (Value.Arena, Class, "CChannel") then return M.C_Channel;
      elsif Text (Value.Arena, Class, "CDeadline") then return M.C_Deadline;
      elsif Text (Value.Arena, Class, "CAppend") then return M.C_Append;
      else return M.C_Evidence; end if;
   end Cause_Class_Of;
   function Actor_Identity (Data : E.Bytes; Left, Right : E.Span) return Boolean is
      function Genuine (Actor : E.Span) return Boolean is
        (Has (Data, Actor, "boot,pid,start_tick,stat,credentials") and then
         V.Is_Integer (Data, F (Data, Actor, "pid")) and then
         V.Is_Integer (Data, F (Data, Actor, "start_tick")) and then
         Number (Data, F (Data, Actor, "pid")) > 0 and then
         Number (Data, F (Data, Actor, "start_tick")) >= 0 and then
         Credential_Pid (Data, F (Data, Actor, "credentials")) = Number (Data, F (Data, Actor, "pid")) and then
         Stat_Field (Data, F (Data, Actor, "stat"), 1) = Number (Data, F (Data, Actor, "pid")) and then
         Stat_Field (Data, F (Data, Actor, "stat"), 22) = Number (Data, F (Data, Actor, "start_tick")));
   begin
      return Genuine (Left) and then Genuine (Right) and then
        Same (Data, F (Data, Left, "boot"), F (Data, Right, "boot")) and then
        Same (Data, F (Data, Left, "pid"), F (Data, Right, "pid")) and then
        Same (Data, F (Data, Left, "start_tick"), F (Data, Right, "start_tick"));
   end Actor_Identity;
   function Worker_Append_Report_Joined
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Captured : E.Span;
      Before : M.Root_State) return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Report : constant E.Span := F (Data, Profile, "worker_report");
      Event : constant E.Span := F (Data, Report, "event");
      Transport : constant E.Span := F (Data, Report, "transport");
      Receive : constant E.Span := F (Data, Transport, "receive");
      Worker : constant E.Span := F (Data, Report, "worker");
      Actor : constant E.Span := F (Data, Report, "worker_actor");
      Pidfd : constant E.Span := F (Data, Report, "worker_pidfd");
      Saved_Actor : constant E.Span := F (Data, F (Data, F (Data, Captured, "candidate"), "x5"), "actor_identity");
      Execution : constant Q.Byte_Count := Root_Reference_Index
        (Value, Index, F (Data, Report, "execution_event"), M.Execution_Native_Event, Before);
      Original_Execution : constant E.Span := Original (Value, Execution);
      Measured : constant E.Span := F (Data, Original_Execution, "measured");
      Origin : constant E.Span := F (Data, Raw_Profile (Value, Execution), "worker_pidfd_origin");
   begin
      return Execution /= 0 and then
        Same (Data, Worker, F (Data, Raw_Profile (Value, Execution), "worker_identity")) and then
        Text (Data, F (Data, Event, "kind"), "UNKNOWN") and then
        V.Text_Matches (Data, F (Data, Event, "operation"), Value.Events (Index).Operation) and then
        Same (Data, F (Data, Event, "record"), Original (Value, Index)) and then
        Same (Data, F (Data, Event, "append_uncertainty"),
          F (Data, F (Data, F (Data, Profile, "cause"), "raw"), "append")) and then
        Raw_Archive_Equal (Data, F (Data, Report, "raw"), Event) and then
        Same (Data, F (Data, Report, "raw"), F (Data, Transport, "raw")) and then
        Num (Data, F (Data, F (Data, Transport, "sealed_memfd"), "seals"), 15) and then
        Receipt (Data, Receive, F (Data, Profile, "source"), "recvmsg", 1) and then
        Bytes_Text (Data, F (Data, F (Data, Receive, "args"), "body"), "F") and then
        Same (Data, F (Data, F (Data, Receive, "args"), "channel"), F (Data, Transport, "channel")) and then
        Same (Data, F (Data, Receive, "sender_credentials"), F (Data, Transport, "sender_credentials")) and then
        Num (Data, F (Data, Receive, "msg_flags"), 0) and then
        Raw_Control_Matches (Data, Receive) and then
        Same (Data, F (Data, Receive, "sender"), F (Data, Transport, "sender_credentials")) and then
        Num (Data, F (Data, Receive, "input_flags"), 1_073_741_824) and then
        Raw_Right_Matches (Data, F (Data, Receive, "rights"),
          F (Data, F (Data, Transport, "sealed_memfd"), "fd")) and then
        V.Is_Sequence (Data, F (Data, F (Data, Receive, "args"), "rights")) and then
        V.Count (Data, F (Data, F (Data, Receive, "args"), "rights")) = 1 and then
        Same (Data, V.Element (Data, F (Data, F (Data, Receive, "args"), "rights"), 0),
          F (Data, F (Data, Transport, "sealed_memfd"), "fd")) and then
        Same (Data, F (Data, F (Data, Receive, "args"), "peer"),
          F (Data, F (Data, Transport, "channel_source"), "peer")) and then
        Identity (Data, F (Data, Transport, "channel"),
          F (Data, F (Data, Transport, "channel_source"), "identity")) and then
        Identity (Data, F (Data, Transport, "channel"), F (Data, F (Data, Profile, "actor"), "channel")) and then
        Credential_Pid (Data, F (Data, Transport, "sender_credentials")) = Number (Data, F (Data, Worker, "pid")) and then
        Identity (Data, F (Data, Pidfd, "origin"), Origin) and then
        Identity (Data, F (Data, Pidfd, "origin"), F (Data, Pidfd, "current")) and then
        Pidfd_Pid (Data, F (Data, Origin, "fdinfo")) = Number (Data, F (Data, Worker, "pid")) and then
        Same (Data, F (Data, F (Data, F (Data, Pidfd, "poll"), "args"), "fd"), F (Data, Pidfd, "fd")) and then
        (Poll (Data, F (Data, Pidfd, "poll"), F (Data, Profile, "source"), False) or else
         Poll (Data, F (Data, Pidfd, "poll"), F (Data, Profile, "source"), True)) and then
        Actor_Identity (Data, Actor, Actor) and then
        Same (Data, F (Data, Actor, "boot"), F (Data, Worker, "boot")) and then
        Same (Data, F (Data, Actor, "pid"), F (Data, Worker, "pid")) and then
        Same (Data, F (Data, Actor, "start_tick"), F (Data, Worker, "start_tick")) and then
        V.Valid_Hex_Field (Data, Measured, "raw_sender_credentials") and then
        V.Bytes_Value (Data, F (Data, Actor, "credentials")) =
          V.Hex_Value (Data, Measured, "raw_sender_credentials") and then
        Same (Data, F (Data, Actor, "pid"), F (Data, Measured, "host_pid")) and then
        Actor_Identity (Data, Saved_Actor, Saved_Actor) and then
        Same (Data, F (Data, Saved_Actor, "boot"), F (Data, Actor, "boot")) and then
        Same (Data, F (Data, Saved_Actor, "start_tick"), F (Data, Actor, "start_tick")) and then
        Same (Data, F (Data, Saved_Actor, "pid"), F (Data, Measured, "namespace_pid"));
   end Worker_Append_Report_Joined;
   function Host_Read_Joined
     (Data : E.Bytes; Calls, Expected, Host_Proc, Target, Source : E.Span;
      Fdinfo : Boolean) return Boolean
   is
      Opened : constant E.Span := V.Element (Data, Calls, 0);
      Closed : constant E.Span := (if V.Count (Data, Calls) = 0 then (1, 0) else
        V.Element (Data, Calls, V.Count (Data, Calls) - 1));
      File_Fd : constant E.Span := F (Data, Opened, "result");
      Path : constant E.Span := F (Data, F (Data, Opened, "args"), "path");
      Offset : E.Count := 0;
   begin
      if not V.Is_Sequence (Data, Calls) or else V.Count (Data, Calls) < 3 or else
         not V.Valid_Bytes (Data, Expected) or else not V.Valid_Text (Data, Path) or else
         not V.Is_Integer (Data, Target) or else Number (Data, Target) < 0 or else
         not Text (Data, F (Data, Opened, "call"), "openat") or else
         not Same (Data, F (Data, Opened, "source"), Source) or else
         not Same (Data, F (Data, F (Data, Opened, "args"), "dirfd"), Host_Proc) or else
         not Num (Data, F (Data, F (Data, Opened, "args"), "flags"), 655360) or else
         not Num (Data, F (Data, Opened, "errno"), 0) or else
         not V.Is_Integer (Data, File_Fd) or else Number (Data, File_Fd) < 0 or else
         not Receipt (Data, Closed, Source, "close") or else
         not Same (Data, F (Data, F (Data, Closed, "args"), "fd"), File_Fd)
      then return False; end if;
      declare
         Raw_Path : constant E.Bytes := V.Text_Value (Data, Path);
         Prefix : constant String := (if Fdinfo then "self/fdinfo/" else "");
         Suffix : constant String := (if Fdinfo then "" else "/stat");
      begin
         if Raw_Path'Length <= Prefix'Length + Suffix'Length or else
            not (for all J in Prefix'Range =>
              Raw_Path (Raw_Path'First + E.Count (J - Prefix'First)) = Q.Byte (Character'Pos (Prefix (J)))) or else
            not (for all J in Suffix'Range =>
              Raw_Path (Raw_Path'Last - E.Count (Suffix'Last - J)) = Q.Byte (Character'Pos (Suffix (J)))) or else
            Decimal (Raw_Path, Raw_Path'First + Prefix'Length, Raw_Path'Last - Suffix'Length) /= Number (Data, Target) or else
            (Raw_Path'Length > Prefix'Length + Suffix'Length + 1 and then
             Raw_Path (Raw_Path'First + Prefix'Length) = Character'Pos ('0'))
         then return False; end if;
      end;
      declare Full : constant E.Bytes := V.Bytes_Value (Data, Expected); begin
         for I in E.Count range 1 .. V.Count (Data, Calls) - 2 loop
            declare
               Item : constant E.Span := V.Element (Data, Calls, I);
               Raw : constant E.Span := F (Data, Item, "raw");
            begin
               if not Text (Data, F (Data, Item, "call"), "read") or else
                  not Same (Data, F (Data, Item, "source"), Source) or else
                  not Same (Data, F (Data, F (Data, Item, "args"), "fd"), File_Fd) or else
                  not V.Is_Integer (Data, F (Data, F (Data, Item, "args"), "count")) or else
                  Number (Data, F (Data, F (Data, Item, "args"), "count")) <= 0 or else
                  not Num (Data, F (Data, Item, "errno"), 0) or else
                  not V.Valid_Bytes (Data, Raw) or else
                  not Same (Data, Raw, F (Data, Item, "api_result"))
               then return False; end if;
               declare Chunk : constant E.Bytes := V.Bytes_Value (Data, Raw); begin
                  if Number (Data, F (Data, Item, "result")) /= Extent_Number (Chunk'Length) or else
                     Extent_Number (Chunk'Length) > Number (Data, F (Data, F (Data, Item, "args"), "count")) or else
                     Offset > Full'Length or else Chunk'Length > Full'Length - Offset or else
                     ((Chunk'Length = 0) /= (I = V.Count (Data, Calls) - 2)) or else
                     not (for all J in Chunk'Range =>
                       Chunk (J) = Full (Full'First + Offset + J - Chunk'First))
                  then return False; end if;
                  Offset := Offset + Chunk'Length;
               end;
            end;
         end loop;
         return Offset = Full'Length;
      end;
   end Host_Read_Joined;
   function Worker_Live_Joined
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Item : E.Span;
      Before : M.Root_State) return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Context : constant E.Span := F (Data, Item, "namespace_context");
      Actor : constant E.Span := F (Data, Context, "actor");
      Recorded : constant E.Span := F (Data, Item, "recorded");
      Execution : constant Q.Byte_Count := Root_Reference_Index
        (Value, Index, F (Data, Context, "execution_event"), M.Execution_Native_Event, Before);
      Transfer : constant Q.Byte_Count := Prior_Root_Index (Value, Index, Execution, M.Transfer_Sent_Event);
      Measured : constant E.Span := F (Data, Original (Value, Execution), "measured");
   begin
      if not Present (Data, Context) then
         return Process_Live (Data, Item, F (Data, Profile, "source"));
      end if;
      return Execution /= 0 and then Transfer > Execution and then
        Same (Data, F (Data, Context, "execution"), Original (Value, Execution)) and then
        Same (Data, Recorded, F (Data, Raw_Profile (Value, Execution), "worker_identity")) and then
        Actor_Identity (Data, Actor, F (Data, Profile, "actor")) and then
        Same (Data, F (Data, Actor, "boot"), F (Data, Recorded, "boot")) and then
        Same (Data, F (Data, Actor, "start_tick"), F (Data, Recorded, "start_tick")) and then
        Same (Data, F (Data, Actor, "pid"), F (Data, Measured, "namespace_pid")) and then
        Same (Data, F (Data, Recorded, "pid"), F (Data, Measured, "host_pid")) and then
        Identity (Data, F (Data, Context, "host_proc"),
          F (Data, F (Data, F (Data, Original (Value, Transfer), "frame"), "origin_descriptors"), "host_proc")) and then
        V.Is_Integer (Data, F (Data, Context, "host_proc_fd")) and then
        Number (Data, F (Data, Context, "host_proc_fd")) >= 0 and then
        Host_Read_Joined (Data, F (Data, F (Data, Context, "reads"), "pidfd_info"),
          F (Data, Item, "pidfd_info"), F (Data, Context, "host_proc_fd"),
          F (Data, F (Data, Item, "pidfd_open"), "result"), F (Data, Profile, "source"), True) and then
        Host_Read_Joined (Data, F (Data, F (Data, Context, "reads"), "stat"),
          F (Data, Item, "stat"), F (Data, Context, "host_proc_fd"),
          F (Data, Recorded, "pid"), F (Data, Profile, "source"), False) and then
        Receipt (Data, F (Data, Item, "pidfd_close"), F (Data, Profile, "source"), "close") and then
        Same (Data, F (Data, F (Data, F (Data, Item, "pidfd_close"), "args"), "fd"),
          F (Data, F (Data, Item, "pidfd_open"), "result")) and then
        Process_Live (Data, Item, F (Data, Profile, "source"), F (Data, Actor, "pid"));
   end Worker_Live_Joined;
   function Cause_Joined
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State) return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Item : constant E.Span := F (Data, Raw_Profile (Value, Index), "cause");
      Raw : constant E.Span := F (Data, Item, "raw");
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Source : constant E.Span := F (Data, Item, "source");
      Origin_Profile : E.Span := Profile;
      Origin_Index : Q.Byte_Count := Index;
      Current : constant D.Decoded_Event := D.Decode (Data, Value.Events (Index));
      Origin_Found : Boolean := False;
      function Failed (Receipt : E.Span) return Boolean is
        (Has (Data, Receipt, "call,args,result,errno,source") and then
         Same (Data, F (Data, Receipt, "source"), Source) and then
         Num (Data, F (Data, Receipt, "result"), -1) and then
         V.Is_Integer (Data, F (Data, Receipt, "errno")) and then Number (Data, F (Data, Receipt, "errno")) > 0);
   begin
      if Current.Status /= D.Decoded then return False; end if;
      if Current.Value.Kind = M.Reconciled_Event then
         for I in Value.Events'First .. Index - 1 loop
            pragma Loop_Variant (Increases => I);
            declare Earlier : constant D.Decoded_Event := D.Decode (Data, Value.Events (I)); begin
               if Earlier.Status = D.Decoded and then Earlier.Value.Kind = M.Unknown_Event and then
                  S.A.Same_Encoding (Data, Value.Extras (I).Cause_Archive, Value.Extras (Index).Cause_Archive)
               then Origin_Profile := Raw_Profile (Value, I); Origin_Index := I; Origin_Found := True; end if;
            end;
         end loop;
         if not Origin_Found then return False; end if;
      end if;
      if not Has (Data, Item, "class,operation,generation,source,raw") or else
         (Cause_Class_Of (Value, Index) /= M.C_Append and then
          not Same (Data, Source, F (Data, Origin_Profile, "source"))) or else
         not Scoped_Matches_Raw (Data, Value.Extras (Index).Cause_Archive, Item) or else
         not V.Text_Matches (Data, F (Data, Item, "operation"), Value.Events (Index).Operation) or else
         not Base_Quantity_Matches (Data, F (Data, Item, "generation"), SF (Data, Value.Events (Index).Base_Archive, "generation"))
      then return False; end if;
      case Cause_Class_Of (Value, Index) is
         when M.C_Channel =>
            return Failed (Raw) and then
              (Text (Data, F (Data, Raw, "call"), "sendmsg") or else
               Text (Data, F (Data, Raw, "call"), "recvmsg") or else
               Text (Data, F (Data, Raw, "call"), "connect")) and then
              Same (Data, F (Data, F (Data, Raw, "args"), "channel"),
                         F (Data, F (Data, Origin_Profile, "actor"), "channel"));
         when M.C_Deadline =>
            return Receipt (Data, F (Data, Raw, "clock"), Source, "clock_gettime") and then
              V.Is_Integer (Data, F (Data, F (Data, Raw, "clock"), "nanoseconds")) and then
              V.Is_Integer (Data, F (Data, Raw, "deadline")) and then
              Number (Data, F (Data, F (Data, Raw, "clock"), "nanoseconds")) >= Number (Data, F (Data, Raw, "deadline")) and then
              Has (Data, Raw, "channel,worker");
         when M.C_Append =>
            declare
               Captured : constant E.Span := F (Data, Profile, "append_uncertainty");
               Attempt : constant E.Span := F (Data, Captured, "attempted_event");
               Proposed : constant E.Span := F (Data, Raw, "failed_event");
               Error : constant E.Span := F (Data, Captured, "error");
               function Field_Same (Name : String) return Boolean is
                 (Same (Data, F (Data, Proposed, Name), F (Data, Attempt, Name)));
            begin
               return Raw_Archive_Equal (Data, F (Data, Raw, "append"), Captured) and then
                 Same (Data, Source, F (Data, F (Data, F (Data, Captured, "candidate"), "x5"), "source_identity")) and then
                 (if Present (Data, F (Data, Origin_Profile, "worker_report")) then
                   Worker_Append_Report_Joined (Value, Origin_Index, Captured, Before)
                  else Actor_Identity (Data, F (Data, Origin_Profile, "actor"),
                    F (Data, F (Data, F (Data, Captured, "candidate"), "x5"), "actor_identity"))) and then
                 Has (Data, Captured, "operation,kind,subject_kind,subject,input,before,candidate,actor,native_delta,native_status,native_position,attempted_event,applied_rows,error") and then
                 V.Valid_Bytes (Data, F (Data, Captured, "input")) and then
                 V.Valid_Bytes (Data, F (Data, Captured, "before")) and then
                 V.Type_Is (Data, F (Data, Captured, "native_delta"), "dict") and then
                 V.Valid_Bytes (Data, F (Data, Captured, "applied_rows")) and then
                 Same (Data, F (Data, Captured, "candidate"), F (Data, Attempt, "retained_record")) and then
                 Same (Data, F (Data, Captured, "actor"), F (Data, Attempt, "actor")) and then
                 Same (Data, F (Data, Captured, "operation"), F (Data, Attempt, "operation")) and then
                 Same (Data, F (Data, Item, "operation"), F (Data, Captured, "operation")) and then
                 Same (Data, F (Data, Item, "generation"), F (Data, Attempt, "generation")) and then
                 Same (Data, F (Data, Captured, "kind"), F (Data, Attempt, "kind")) and then
                 Same (Data, F (Data, Captured, "subject_kind"), F (Data, Attempt, "subject_kind")) and then
                 Same (Data, F (Data, Captured, "subject"), F (Data, Attempt, "subject")) and then
                 Field_Same ("generation") and then Field_Same ("operation") and then
                 Field_Same ("subject_kind") and then Field_Same ("subject") and then
                 Field_Same ("subgeneration") and then Field_Same ("kind") and then
                 V.Valid_Text (Data, F (Data, Error, "type")) and then
                 V.Valid_Text (Data, F (Data, Error, "module")) and then
                 V.Valid_Text (Data, F (Data, Error, "message")) and then
                 V.Is_Sequence (Data, F (Data, Error, "args")) and then
                 V.Is_Sequence (Data, F (Data, Error, "notes")) and then
                 V.Valid (Data, F (Data, Error, "errno")) and then
                 V.Valid (Data, F (Data, Error, "filename")) and then
                 V.Valid (Data, F (Data, Error, "filename2")) and then
                 V.Valid (Data, F (Data, Error, "sqlite_errorcode")) and then
                 V.Valid (Data, F (Data, Error, "sqlite_errorname")) and then
                 Raw_Archive_Equal (Data, F (Data, Raw, "record"), F (Data, Attempt, "retained_record")) and then
                 V.Valid_Hex_Field (Data, Proposed, "record_digest") and then
                 C.G.Origin_Matches
                   (V.Text_Value (Data, F (Data, Proposed, "record_digest")),
                    (1, V.Text_Value (Data, F (Data, Proposed, "record_digest"))'Length),
                    C.G.Hash (V.Bytes_Value (Data, F (Data, Raw, "record")),
                      (1, V.Bytes_Value (Data, F (Data, Raw, "record"))'Length)));
            end;
         when M.C_Evidence =>
            return Text (Data, F (Data, Item, "class"), "CEvidence") and then
              Has (Data, Raw, "expected,actual") and then
              not Same (Data, F (Data, Raw, "expected"), F (Data, Raw, "actual")) and then
              Same (Data, F (Data, Raw, "actual"), F (Data, Profile, "failed_material"));
      end case;
   end Cause_Joined;
   function Replay_Matches (Value : L.Parsed_Input; Index : Q.Byte_Count;
                            Identity : E.Span; Candidate : Q.Byte_Count) return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Base : constant E.Span := Value.Events (Candidate).Base_Archive;
      function Field_Same (Name : String) return Boolean is
        (if Name = "generation" then Base_Quantity_Matches (Data, F (Data, Identity, Name), SF (Data, Base, Name))
         else Scoped_Matches_Raw (Data, SF (Data, Base, Name), F (Data, Identity, Name)));
   begin
      return Candidate < Index and then
        Field_Same ("generation") and then Field_Same ("operation") and then
        Field_Same ("subject_kind") and then Field_Same ("subject") and then
        Field_Same ("subgeneration") and then Field_Same ("kind") and then
        V.Valid_Hex_Field (Data, F (Data, Identity, "record_digest"), "value") and then
        C.G.Origin_Matches (V.Text_Value (Data, F (Data, Identity, "record_digest")),
          (1, V.Text_Value (Data, F (Data, Identity, "record_digest"))'Length),
          C.G.Hash (Data, Value.Events (Candidate).Record_Archive));
   end Replay_Matches;
   function Reconciled (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State)
      return Boolean
      with Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 2)
   is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Item : constant E.Span := F (Data, Profile, "reconciled");
      Cause : constant E.Span := F (Data, Profile, "cause");
      Route : constant E.Span := F (Data, Item, "route");
      Reattached : constant Q.Byte_Count := Root_Reference_Index
        (Value, Index, F (Data, Item, "reattach_event"), M.Worker_Reattached_Event, Before);
      Failed : constant E.Span := F (Data, F (Data, Cause, "raw"), "failed_event");
      Unknown_Pos : Q.Byte_Count := 0;
      Found : Boolean := False;
   begin
      if not Before.Unknown_Cause.Present or else not Cause_Joined (Value, Index, Before) or else
         C.G.Hash (Data, Value.Extras (Index).Cause_Archive) /= Before.Unknown_Cause.Value or else
         not Same (Data, F (Data, Item, "cause"), Cause) then return False; end if;
      for I in Value.Events'First .. Index - 1 loop
         declare Event : constant D.Decoded_Event := D.Decode (Data, Value.Events (I)); begin
            if Event.Status = D.Decoded and then Event.Value.Kind = M.Unknown_Event and then
               S.A.Same_Encoding (Data, SF (Data, Value.Events (I).Base_Archive, "generation"),
                                       SF (Data, Value.Events (Index).Base_Archive, "generation")) and then
               S.A.Same_Encoding (Data, Value.Extras (I).Cause_Archive, Value.Extras (Index).Cause_Archive)
            then Unknown_Pos := I; end if;
            if Cause_Class_Of (Value, Index) = M.C_Append and then Replay_Matches (Value, Index, Failed, I)
            then Found := True; end if;
         end;
      end loop;
      if Text (Data, Route, "custody-returned") then return Worker_Gone (Value, Index, Before); end if;
      case Cause_Class_Of (Value, Index) is
         when M.C_Channel | M.C_Deadline =>
            return Text (Data, Route, "reattach") and then Unknown_Pos /= 0 and then
              Reattached > Unknown_Pos and then
              Worker_Live_Joined (Value, Index, F (Data, Item, "worker"), Before) and then
              Same (Data, F (Data, F (Data, Item, "worker"), "recorded"),
                         F (Data, Raw_Profile (Value, Reattached), "worker_identity"));
         when M.C_Append =>
            return ((Text (Data, Route, "append-persisted") and then Found) or else
                    (Text (Data, Route, "append-retry") and then not Found and then
                     Worldline.Custody_V2_Mutation_Decision.Attempt_Matches
                       (Data, F (Data, Profile, "append_uncertainty"), Value.Source_Input) and then
                     Same (Data, F (Data, F (Data, Item, "retry"), "proposed"), Failed) and then
                     Same
                       (Data, F (Data, F (Data, F (Data, F (Data, Profile, "append_uncertainty"), "candidate"), "x5"), "actor_identity"),
                        F (Data, F (Data, Item, "retry"), "original_owner")) and then
                     Same (Data, F (Data, F (Data, Item, "retry"), "source"), F (Data, Profile, "source")))) and then
              (not M.Is_Worker_Phase (Before.Before_Unknown) or else
               Worker_Live_Joined (Value, Index, F (Data, Item, "worker"), Before));
         when M.C_Evidence =>
            return Text (Data, Route, "corroborated") and then
              ((Root_Ready (Value, Index, "root-admission") and then
                Same (Data, F (Data, Item, "corroborated_material"),
                           F (Data, Native_Item (Value, Index, "root-admission"), "material"))) or else
               (Scoped (Value, Index, "scoped-validate", R.Validate_Entry, 1) and then
                (Scoped (Value, Index, "scoped-classify", R.Classify_Entry, R.J.L.Liveness'Pos (R.J.L.Live)) or else
                 Scoped (Value, Index, "scoped-classify", R.Classify_Entry, R.J.L.Liveness'Pos (R.J.L.Reaped)) or else
                 Scoped (Value, Index, "scoped-classify", R.Classify_Entry, R.J.L.Liveness'Pos (R.J.L.Never_Launched))) and then
                Same (Data, F (Data, Item, "corroborated_material"),
                           F (Data, Native_Item (Value, Index, "scoped-classify"), "material"))));
      end case;
   end Reconciled;
   function Roster_Report_Joined (Value : L.Parsed_Input; Index : Q.Byte_Count)
      return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Receiver : constant E.Span := F (Data, Profile, "receiver_report");
      Report : constant E.Span := F (Data, Receiver, "report");
      Event : constant E.Span := F (Data, Receiver, "event");
      Evidence : constant E.Span := F (Data, Report, "evidence");
      Transport : constant E.Span := F (Data, Receiver, "transport");
      Receive : constant E.Span := F (Data, Transport, "receive");
      Inventory : constant E.Span := Native_Inventory (Value, Index, "root-admission");
      Broker : constant E.Span := F (Data, Inventory, "sender_role_roster");
   begin
      return Same (Data, Original (Value, Index), F (Data, Report, "original")) and then
        Has (Data, Original (Value, Index), "complete_received_roster,sender_transcript,sender_role_roster") and then
        Same (Data, F (Data, Original (Value, Index), "sender_role_roster"),
          F (Data, F (Data, Profile, "roster"), "sender_role_roster")) and then
        Same (Data, F (Data, Evidence, "roster"), F (Data, Profile, "roster")) and then
        Same (Data, F (Data, Evidence, "locks"), F (Data, Profile, "locks")) and then
        Same (Data, F (Data, Evidence, "transfer_event"), F (Data, Profile, "transfer_event")) and then
        Same (Data, F (Data, Report, "native"), Value.Extras (Index).Native_Observations_Payload) and then
        Text (Data, F (Data, Event, "kind"), "ROSTER_EVIDENCE") and then
        V.Text_Matches (Data, F (Data, Event, "operation"), Value.Events (Index).Operation) and then
        Same (Data, F (Data, Event, "record"), Original (Value, Index)) and then
        Same (Data, F (Data, Event, "receiver_report"), Report) and then
        Raw_Archive_Equal (Data, F (Data, Receiver, "raw"), Event) and then
        Same (Data, F (Data, Receiver, "raw"), F (Data, Transport, "raw")) and then
        Num (Data, F (Data, F (Data, Transport, "sealed_memfd"), "seals"), 15) and then
        Receipt (Data, Receive, F (Data, Profile, "source"), "recvmsg", 1) and then
        Bytes_Text (Data, F (Data, F (Data, Receive, "args"), "body"), "F") and then
        Same (Data, F (Data, F (Data, Receive, "args"), "channel"), F (Data, Transport, "channel")) and then
        Same (Data, F (Data, Receive, "sender_credentials"), F (Data, Transport, "sender_credentials")) and then
        Num (Data, F (Data, Receive, "msg_flags"), 0) and then
        Credential_Pid (Data, F (Data, Transport, "sender_credentials")) =
          Number (Data, F (Data, Broker, "worker_host_pid")) and then
        Pidfd_Pid (Data, F (Data, F (Data, Broker, "worker_pidfd"), "fdinfo")) =
          Number (Data, F (Data, Broker, "worker_host_pid"));
   end Roster_Report_Joined;
   function Witness_Terminal_Joined
     (Value : L.Parsed_Input; Index : Q.Byte_Count;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof) return Boolean
   is
      Data : E.Bytes renames Value.Arena;
      Witness : constant E.Span := F (Data, Raw_Profile (Value, Index), "witness");
      Terminal : constant E.Span := F (Data, Witness, "terminal");
      Terminal_Index : constant Q.Byte_Count := Reference_Index
        (Value, Index, F (Data, Terminal, "event_id"), M.Handler_Terminal_Event);
   begin
      return Terminal_Index /= 0 and then
        Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Terminal_Index, Proof) and then
        Worldline.Custody_V2_Closed_State.Event_Record_Matches (Value, Terminal_Index, Data, Terminal);
   end Witness_Terminal_Joined;
   -- A failed handoff is not a fabricated Handler_Terminal. Every reference
   -- here is independently authenticated in the same root generation/use.
   function Failed_Witness_State
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof) return E.Span
   is
      Data : E.Bytes renames Value.Arena;
      Witness : constant E.Span := F (Data, Raw_Profile (Value, Index), "witness");
      Failure : constant E.Span := F (Data, Witness, "failure_event");
      Aborted : constant Q.Byte_Count := Root_Reference_Index
        (Value, Index, F (Data, Failure, "event_id"), M.Handoff_Abort_Event, Before);
      Escrow : constant Q.Byte_Count := Root_Reference_Index
        (Value, Index, F (Data, Failure, "event_id"), M.Front_Retained_Escrow_Event, Before);
      Failed_Index : constant Q.Byte_Count := (if Aborted /= 0 then Aborted else Escrow);
      Execution : constant E.Span := F (Data, Witness, "execution_event");
      Execution_Index : constant Q.Byte_Count := Root_Reference_Index
        (Value, Index, F (Data, Execution, "event_id"), M.Execution_Native_Event, Before);
      Intent : constant E.Span := F (Data, Witness, "handoff_intent");
      Intent_Index : constant Q.Byte_Count := Root_Reference_Index
        (Value, Index, F (Data, Intent, "event_id"), M.Handoff_Intent_Event, Before);
      Frame : constant E.Span := F (Data, Original (Value, Intent_Index), "value");
      State : constant E.Span := F (Data, Raw_Profile (Value, Failed_Index), "owner_current");
   begin
      if not Text (Data, F (Data, Witness, "failure_schema"), "worldline.failed-root-physical-closure-v1") or else
         Failed_Index = 0 or else Execution_Index = 0 or else Intent_Index = 0 or else
         Execution_Index >= Intent_Index or else Intent_Index >= Failed_Index or else
         not Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Failed_Index, Proof) or else
         not Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Execution_Index, Proof) or else
         not Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Intent_Index, Proof) or else
         not Worldline.Custody_V2_Closed_State.Event_Record_Matches (Value, Failed_Index, Data, Failure) or else
         not Worldline.Custody_V2_Closed_State.Event_Record_Matches (Value, Execution_Index, Data, Execution) or else
         not Worldline.Custody_V2_Closed_State.Event_Record_Matches (Value, Intent_Index, Data, Intent) or else
         not Same (Data, State, F (Data, Witness, "failure_owner_state")) or else
         not Same (Data, F (Data, Witness, "original_request"), F (Data, Frame, "original_request")) or else
         not Same (Data, F (Data, Witness, "original_use"), F (Data, Frame, "original_native_use")) or else
         not Same (Data, F (Data, F (Data, Witness, "historical_root_native"), "record"), F (Data, Frame, "root_native")) or else
         not Present (Data, State)
      then return (1, 0); end if;
      -- No acknowledged worker can be treated as a failed pre-handler owner.
      for I in Value.Events'Range loop
         if I >= Intent_Index and then I < Index then
         declare Event : constant D.Decoded_Event := D.Decode (Data, Value.Events (I)); begin
            if Event.Status = D.Decoded and then Event.Value.Kind in
               M.Custody_Ack_Event | M.Handler_Terminal_Event | M.Original_Result_Event and then
               Event.Value.Kind_Of_Subject = M.Root and then
               Q.Span_Valid (Data, Event.Value.Generation) and then
               Q.Compare (Data, Event.Value.Generation, Before.Generation) = Q.Equal and then
               M.L.Optional_Same (Data, Event.Value.Operation, Before.Operation)
            then return (1, 0); end if;
         end;
         end if;
      end loop;
      return State;
   end Failed_Witness_State;

   function Closed_Witness_State
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof) return E.Span
   is
      Data : E.Bytes renames Value.Arena;
      Witness : constant E.Span := F (Data, Raw_Profile (Value, Index), "witness");
   begin
      if Witness_Terminal_Joined (Value, Index, Proof) then
         return F (Data, F (Data, F (Data, F (Data, Witness, "terminal"), "record"), "value"), "owner_state");
      end if;
      return Failed_Witness_State (Value, Index, Before, Proof);
   end Closed_Witness_State;

   function Closed_Owner_Plan
     (Value : L.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof) return E.Span
   is
      Data : E.Bytes renames Value.Arena;
      Selected : Q.Byte_Count := 0;
      Plan : E.Span := (1, 0);
   begin
      if Value.Status /= L.Parsed or else Index not in Value.Events'Range or else
         not Q.Span_Valid (Data, Before.Generation) then return Plan; end if;
      for I in Value.Events'First .. Index - 1 loop
         declare Event : constant D.Decoded_Event := D.Decode (Data, Value.Events (I)); begin
            if Event.Status = D.Decoded and then Event.Value.Kind = M.Transfer_Sent_Event and then
               Event.Value.Kind_Of_Subject = M.Root and then
               Q.Span_Valid (Data, Event.Value.Generation) and then
               Q.Compare (Data, Event.Value.Generation, Before.Generation) = Q.Equal and then
               M.L.Optional_Same (Data, Event.Value.Operation, Before.Operation)
            then Selected := I; end if;
         end;
      end loop;
      if Selected = 0 and then Present (Data, Failed_Witness_State (Value, Index, Before, Proof)) then
         declare
            Witness : constant E.Span := F (Data, Raw_Profile (Value, Index), "witness");
            Intent : constant Q.Byte_Count := Root_Reference_Index
              (Value, Index, F (Data, F (Data, Witness, "handoff_intent"), "event_id"), M.Handoff_Intent_Event, Before);
         begin
            Plan := F (Data, F (Data, F (Data, Original (Value, Intent), "value"), "root_plan"), "raw");
            if V.Valid_Bytes (Data, Plan) then return Plan; else return (1, 0); end if;
         end;
      end if;
      if Selected = 0 or else
         not Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Selected, Proof)
      then return Plan; end if;
      Plan := F (Data, F (Data, F (Data, Original (Value, Selected), "frame"), "root_plan"), "raw");
      if V.Valid_Bytes (Data, Plan) then
         return Plan;
      else
         return (1, 0);
      end if;
   end Closed_Owner_Plan;
   function Join
     (Value : L.Parsed_Input; Index : Q.Byte_Count;
      Before : M.Root_State; Subjects : M.Subject_State_Array;
      Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof) return Join_Status
   is
      pragma Unreferenced (Subjects, Subject);
      Data : E.Bytes renames Value.Arena;
      Profile : constant E.Span := Raw_Profile (Value, Index);
      Source : constant E.Span := F (Data, Profile, "source");
      Actor : constant E.Span := F (Data, Profile, "actor");
      Owner_Before : constant E.Span := F (Data, Profile, "owner_before");
      Owner_Current : constant E.Span := F (Data, Profile, "owner_current");
      Decoded : D.Decoded_Event;
      Joined : Boolean := False;
      Owner_Plan : E.Span := (1, 0);
      function Ref (Name : String; Kind : M.Event_Kind) return Boolean is
        (Prior (Value, Index, F (Data, Profile, Name), Kind));
      function Full_Locks (Fresh : Boolean := False; Ofd : Boolean := True) return Boolean is
        (Locks_Joined (Value, Index, F (Data, Owner_Before, "held_locks"),
          F (Data, Profile, "locks"), Source, Actor, Fresh, Ofd,
          Capture (Value, Index, "root-admission"),
          Native_Inventory (Value, Index, "root-admission")));
   begin
      if Value.Status /= L.Parsed or else Index not in Value.Events'Range or else
         not L.Parsed_Spans_Valid (Value) then return Evidence_Refused; end if;
      Decoded := D.Decode (Data, Value.Events (Index));
      if Decoded.Status /= D.Decoded or else
         P.Family (Decoded.Value.Kind) in P.Request_Transition | P.Descriptor_Transition or else
         not S.Text_Is (Data, SF (Data, X5 (Value, Index), "schema"), "worldline.custody-x5-event-v2") or else
         not Text (Data, F (Data, Profile, "schema"), "worldline.custody-root-raw-v1") or else
         not V.Valid (Data, Original (Value, Index)) or else
         not Scoped_Matches_Raw (Data, SF (Data, X5 (Value, Index), "source_identity"), Source) or else
         not Scoped_Matches_Raw (Data, SF (Data, X5 (Value, Index), "actor_identity"), Actor) or else
         not Has (Data, Actor, "boot,pid,start_tick,stat,credentials,channel") or else
         not V.Is_Integer (Data, F (Data, Actor, "pid")) or else
         not V.Is_Integer (Data, F (Data, Actor, "start_tick")) or else
         not V.Valid_Bytes (Data, F (Data, Actor, "stat")) or else
         Number (Data, F (Data, Actor, "pid")) <= 0 or else
         Number (Data, F (Data, Actor, "start_tick")) < 0 or else
         Credential_Pid (Data, F (Data, Actor, "credentials")) /= Number (Data, F (Data, Actor, "pid")) or else
         Stat_Field (Data, F (Data, Actor, "stat"), 1) /= Number (Data, F (Data, Actor, "pid")) or else
         Stat_Field (Data, F (Data, Actor, "stat"), 22) /= Number (Data, F (Data, Actor, "start_tick")) or else
         not Worldline.Custody_V2_Operation_Journal.Authenticated (Value, Index, Proof)
      then return Evidence_Refused; end if;
      case Decoded.Value.Kind is
         when M.Prepared_Event => Joined := Prepared (Value, Index);
         when M.Held_Event => Joined := Held (Value, Index);
         when M.Running_Event =>
            Joined := Ref ("held_event", M.Held_Event) and then
              Same (Data, F (Data, F (Data, Original (Value, Index), "resource_event"), "packet"),
                F (Data, F (Data, Profile, "running"), "material")) and then
              Scoped_Commit (Value, Index, F (Data, Profile, "running"), R.J.L.Record_Running);
         when M.Execution_Native_Event =>
            Joined := Ref ("running_event", M.Running_Event) and then
              Root_Ready (Value, Index, "root-execution") and then
              Same (Data, F (Data, Original (Value, Index), "material"),
                F (Data, Native_Item (Value, Index, "root-execution"), "material")) and then
              Same (Data, F (Data, Original (Value, Index), "native"),
                F (Data, Native_Item (Value, Index, "root-execution"), "observation")) and then
              Same (Data, F (Data, Original (Value, Index), "original_request"),
                F (Data, Profile, "request")) and then
              Same (Data, F (Data, F (Data, Profile, "execution"), "material"),
                         F (Data, Native_Item (Value, Index, "root-execution"), "material")) and then
              Same (Data, F (Data, F (Data, Profile, "execution"), "observation"),
                         F (Data, Native_Item (Value, Index, "root-execution"), "observation")) and then
              Has (Data, F (Data, F (Data, Profile, "execution"), "before_exec"),
                   "measured,process,request,dispatch,ticket,channel,source") and then
              Same (Data, F (Data, F (Data, F (Data, Profile, "execution"), "before_exec"), "measured"),
                F (Data, Original (Value, Index), "measured")) and then
              Same (Data, F (Data, F (Data, F (Data, Profile, "execution"), "before_exec"), "process"),
                F (Data, Original (Value, Index), "process")) and then
              Same (Data, F (Data, F (Data, F (Data, Profile, "execution"), "before_exec"), "request"),
                F (Data, Original (Value, Index), "original_request")) and then
              Same (Data, F (Data, F (Data, F (Data, Profile, "execution"), "before_exec"), "source"), Source);
         when M.Execution_Ack_Event => Joined := Ack (Value, Index);
         when M.Handoff_Intent_Event =>
            Joined := Ref ("execution_ack_event", M.Execution_Ack_Event) and then
              Root_Ready (Value, Index, "root-admission") and then Full_Locks and then
              Same (Data, F (Data, Original (Value, Index), "value"), F (Data, Profile, "handoff")) and then
              Has (Data, F (Data, Profile, "handoff"),
                   "schema,installation,descriptor,genesis,operation,original_request,original_native_use,root_native,worker,locks,channel,source,root_plan,origin_descriptors") and then
              Same (Data, F (Data, F (Data, Profile, "handoff"), "source"), Source) and then
              Same (Data, F (Data, F (Data, Profile, "handoff"), "original_request"), F (Data, Profile, "request")) and then
              Same (Data, F (Data, F (Data, Profile, "handoff"), "original_native_use"), F (Data, Profile, "use"));
         when M.Front_Close_Intent_Event =>
            Joined := Ref ("handoff_event", M.Handoff_Intent_Event) and then
              Same (Data, F (Data, Original (Value, Index), "quiescence"), F (Data, Profile, "quiescence")) and then
              Same (Data, F (Data, Original (Value, Index), "owner_before"), Owner_Before) and then
              Quiescent (Data, F (Data, Profile, "quiescence")) and then Full_Locks;
         when M.Front_Closed_Event =>
            Joined := Ref ("front_close_event", M.Front_Close_Intent_Event) and then
              Same (Data, F (Data, Original (Value, Index), "owners_closed"), F (Data, Profile, "owners_closed")) and then
              Same (Data, F (Data, Original (Value, Index), "owner_state"), Owner_Current) and then
              Owners_Closed (Data, Owner_Before, F (Data, Profile, "owners_closed"), Source) and then
              Full_Locks and then Seed_Current (Value, Index);
         when M.Transfer_Sent_Event =>
            Joined := Ref ("front_closed_event", M.Front_Closed_Event) and then Full_Locks and then
              Same (Data, F (Data, Original (Value, Index), "frame"),
                F (Data, F (Data, Profile, "transfer"), "frame")) and then
              Same (Data, F (Data, Original (Value, Index), "actual_send"),
                F (Data, F (Data, Profile, "transfer"), "actual_send")) and then
              Seed_Current (Value, Index) and then
              Send_All (Data, F (Data, F (Data, Profile, "transfer"), "receipts"),
                              F (Data, F (Data, Profile, "transfer"), "descriptors"), Source);
         when M.Roster_Evidence_Event =>
            Joined := Ref ("transfer_event", M.Transfer_Sent_Event) and then Full_Locks and then
              Root_Ready (Value, Index, "root-admission") and then Roster_Report_Joined (Value, Index) and then
              Has (Data, F (Data, Profile, "roster"), "received_locks,origin_descriptors,sender,channel");
         when M.Custody_Ack_Event =>
            Joined := Ref ("transfer_event", M.Transfer_Sent_Event) and then Full_Locks and then
              Seed_Current (Value, Index) and then Root_Ready (Value, Index, "root-admission") and then
              Same (Data, F (Data, Original (Value, Index), "native_material"),
                F (Data, Native_Item (Value, Index, "root-admission"), "material")) and then
              Same (Data, F (Data, Original (Value, Index), "native"),
                F (Data, Native_Item (Value, Index, "root-admission"), "observation")) and then
              Same (Data, F (Data, F (Data, Original (Value, Index), "frame"), "original_request"),
                F (Data, Profile, "request")) and then
              Same (Data, F (Data, F (Data, Original (Value, Index), "frame"), "original_native_use"),
                F (Data, Profile, "use")) and then
              Has (Data, Original (Value, Index), "frame,native_material,native,received_sender,actual_received_locks");
         when M.Abandon_Event =>
            Joined := Ref ("transfer_event", M.Transfer_Sent_Event) and then Full_Locks and then
              Seed_Current (Value, Index);
         when M.Front_Retained_Escrow_Event =>
            Joined := Ref ("abandon_event", M.Abandon_Event) and then Full_Locks and then
              Identity (Data, F (Data, F (Data, Profile, "escrow"), "origin"),
                              F (Data, F (Data, Profile, "escrow"), "current"));
         when M.Handoff_Abort_Event =>
            declare Abort_Record : constant E.Span := F (Data, Profile, "abort"); begin
               if S.Text_Is (Data, SF (Data, SF (Data, X5 (Value, Index), "primitive_inputs"), "abort_class"), "Never_Dispatched") then
                  Joined := Text (Data, F (Data, F (Data, Abort_Record, "launch_journal"), "phase"), "NEVER_DISPATCHED") and then
                    Scoped (Value, Index, "scoped-classify", R.Classify_Entry, R.J.L.Liveness'Pos (R.J.L.Never_Launched)) and then
                    Scoped_Commit (Value, Index, F (Data, Abort_Record, "release"), R.J.L.Release_Hold);
               else
                  Joined := S.Text_Is (Data, SF (Data, SF (Data, X5 (Value, Index), "primitive_inputs"), "abort_class"), "Dispatched") and then
                    Has (Data, F (Data, Abort_Record, "launch_journal"), "dispatch,held,source") and then
                    Full_Locks and then Scoped (Value, Index, "scoped-validate", R.Validate_Entry, 1);
               end if;
            end;
         when M.Original_Progress_Event | M.Original_Result_Event =>
            Joined := Report (Value, Index, Decoded.Value.Kind);
         when M.Handler_Terminal_Event =>
            Joined := Report (Value, Index, Decoded.Value.Kind) and then
              Has (Data, F (Data, Original (Value, Index), "value"),
                   "result,failures,owner_state,native_event,original_native_use") and then
              Same (Data, F (Data, F (Data, Original (Value, Index), "value"), "original_native_use"), F (Data, Profile, "use")) and then
              Root_Ready (Value, Index, "root-admission");
         when M.Worker_Relinquish_Event =>
            Joined := Ref ("terminal_event", M.Handler_Terminal_Event) and then
              Same (Data, Original (Value, Index), F (Data, Profile, "relinquish")) and then
              Owners_Closed (Data, Owner_Before, F (Data, F (Data, Profile, "relinquish"), "owners_closed"), Source) and then
              Root_Ready (Value, Index, "root-admission") and then Full_Locks;
         when M.Worker_Reattached_Event => Joined := Reattach (Value, Index, Before);
         when M.Custody_Returned_Event => Joined := Worker_Gone (Value, Index, Before);
         when M.Closed_NS_Event => Joined := Closed_NS (Value, Index);
         when M.Closed_Outer_Event => Joined := Closed_Outer (Value, Index);
         when M.Closed_Raw_Event => Joined := Closed_Raw (Value, Index);
         when M.Closed_Witness_Event =>
            Owner_Plan := Closed_Owner_Plan (Value, Index, Before, Proof);
            Joined := Ref ("namespace_event", M.Closed_NS_Event) and then Ref ("outer_event", M.Closed_Outer_Event) and then
              Ref ("raw_event", M.Closed_Raw_Event) and then
              Same (Data, F (Data, Original (Value, Index), "complete_native_closed"), F (Data, Profile, "witness")) and then
              Present (Data, Closed_Witness_State (Value, Index, Before, Proof)) and then
              Same (Data,
                Closed_Witness_State (Value, Index, Before, Proof),
                F (Data, F (Data, F (Data, Profile, "witness"), "actual_state_correspondence"), "before")) and then
              V.Valid_Bytes (Data, Owner_Plan) and then
              Worldline.Custody_V2_Closed_State.Matches
                (Data,
                 Closed_Witness_State (Value, Index, Before, Proof),
                 F (Data, F (Data, F (Data, Profile, "witness"), "actual_state_correspondence"), "current"),
                 Value.Source_Input, Value.Key, Owner_Plan) and then
              Scoped (Value, Index, "scoped-classify", R.Classify_Entry, R.J.L.Liveness'Pos (R.J.L.Reaped)) and then
              Scoped (Value, Index, "scoped-validate", R.Validate_Entry, 1) and then
              Same (Data, F (Data, F (Data, Profile, "witness"), "classification_input"),
                         F (Data, Native_Item (Value, Index, "scoped-classify"), "material")) and then
              Same (Data, F (Data, F (Data, Profile, "witness"), "packet"),
                         F (Data, Native_Item (Value, Index, "scoped-validate"), "material")) and then
              Has (Data, F (Data, Profile, "witness"),
                   "physical,original_row,terminal,terminal_transport,owned_closed,outer_wait,complete_raw,original_use,original_request,complete_custody_history");
         when M.Physical_Settled_Event =>
            Joined := Ref ("witness_event", M.Closed_Witness_Event) and then
              Same (Data, F (Data, Original (Value, Index), "complete_resource_settlement"),
                F (Data, Profile, "settlement")) and then
              Scoped_Commit (Value, Index, F (Data, F (Data, Profile, "settlement"), "terminal"), R.J.L.Record_Terminal) and then
              (Scoped_Commit (Value, Index, F (Data, F (Data, Profile, "settlement"), "release"), R.J.L.Release_Hold) or else
               Scoped_Commit (Value, Index, F (Data, F (Data, Profile, "settlement"), "charge"), R.J.L.Charge_Budget));
         when M.Historical_Settlement_Event =>
            Joined := Historical (Value, Index, F (Data, Profile, "historical")) and then
              Same (Data, F (Data, Original (Value, Index), "complete_native_settlement"),
                F (Data, F (Data, Profile, "historical"), "event")) and then
              Same (Data, F (Data, Original (Value, Index), "result"),
                F (Data, F (Data, Profile, "historical"), "result")) and then
              (Ref ("returned_event", M.Custody_Returned_Event) or else Ref ("abort_event", M.Handoff_Abort_Event));
         when M.Front_Reconstruction_Event =>
            Joined := Ref ("settlement_event", M.Historical_Settlement_Event) and then
              Full_Locks and then
              Same (Data, F (Data, Original (Value, Index), "fresh_state"), Owner_Current) and then
              Same (Data, F (Data, Original (Value, Index), "source"), Source) and then
              Same (Data, F (Data, F (Data, Profile, "reconstruction"), "fresh_state"), Owner_Current) and then
              Same (Data, F (Data, Owner_Current, "source"), Source) and then
              Has (Data, F (Data, Profile, "reconstruction"), "descriptor,genesis,policy,source,escrow_claims") and then
              Scoped (Value, Index, "scoped-validate", R.Validate_Entry, 1);
         when M.Front_Owned_Event =>
            Joined := (Ref ("reconstruction_event", M.Front_Reconstruction_Event) or else
                       Ref ("settlement_event", M.Historical_Settlement_Event)) and then
              Same (Data, Original (Value, Index), F (Data, Profile, "front_owned")) and then
              Same (Data, F (Data, F (Data, Profile, "front_owned"), "new_owner"), Owner_Current) and then
              Has (Data, F (Data, Profile, "front_owned"), "old_end,new_owner") and then
              Full_Locks and then Scoped (Value, Index, "scoped-validate", R.Validate_Entry, 1);
         when M.Unknown_Event => Joined := Cause_Joined (Value, Index, Before);
         when M.Reconciled_Event => Joined := Reconciled (Value, Index, Before);
         when M.Request_Queued_Event | M.Request_Transfer_Intent_Event | M.Request_Intake_Event |
              M.Request_Abandon_Event | M.Request_Responded_Event | M.Request_Lost_Event |
              M.Drain_Stop_Intent_Event | M.Drain_Freeze_Event | M.Drain_Ofd_Evidence_Event |
              M.Drain_Intake_Event | M.Drain_Abandon_Event | M.Drain_Released_Event | M.Drain_Reclaimed_Event =>
            return Evidence_Refused;
      end case;
      return (if Joined then Evidence_Joined else Evidence_Refused);
   end Join;
   function Join
     (Value : L.Parsed_Input; Index : Q.Byte_Count;
      Before : M.Root_State; Subjects : M.Subject_State_Array;
      Subject : P.Optional_Subject) return Join_Status
   is
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof;
   begin
      if Value.Status /= L.Parsed or else Index not in Value.Events'Range then return Evidence_Refused; end if;
      Worldline.Custody_V2_Operation_Journal.Establish (Value, Proof);
      return Join (Value, Index, Before, Subjects, Subject, Proof);
   end Join;
   function Closed_Proof_Reference
     (Value : L.Parsed_Input; Index : Q.Byte_Count;
      Before : M.Root_State; Subjects : M.Subject_State_Array;
      Subject : P.Optional_Subject;
      Proof : Worldline.Custody_V2_Operation_Journal.Journal_Proof)
      return Closed_State_References
   is
      Data : E.Bytes renames Value.Arena;
      Refused : constant Closed_State_References := (others => <>);
   begin
      if Value.Status /= L.Parsed or else Index not in Value.Events'Range then return Refused; end if;
      declare
         Event : constant D.Decoded_Event := D.Decode (Data, Value.Events (Index));
         Witness : constant E.Span := F (Data, Raw_Profile (Value, Index), "witness");
         Correspondence : constant E.Span := F (Data, Witness, "actual_state_correspondence");
         Terminal_State : constant E.Span := Closed_Witness_State (Value, Index, Before, Proof);
         Current_State : constant E.Span := F (Data, Correspondence, "current");
      begin
         if Event.Status /= D.Decoded or else Event.Value.Kind /= M.Closed_Witness_Event or else
            Event.Value.Kind_Of_Subject /= M.Root or else
            Join (Value, Index, Before, Subjects, Subject, Proof) /= Evidence_Joined or else
            not Present (Data, Terminal_State) or else not Present (Data, Current_State) or else
            not Same (Data, Terminal_State, F (Data, Correspondence, "before")) then return Refused; end if;
         return (Status => Evidence_Joined,
                 Terminal_Owner_State => Terminal_State,
                 Current_Owner_State => Current_State);
      end;
   end Closed_Proof_Reference;
end Worldline.Custody_V2_Root_Evidence;

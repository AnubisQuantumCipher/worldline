with SPARK.Big_Integers;
with Worldline.Scoped_Capture_Projection;
with Worldline.Recovery_Archive;

package body Worldline.Scoped_Capture_Namespace_Projection with SPARK_Mode is
   package P renames Worldline.Scoped_Capture_Projection;
   use SPARK.Big_Integers;
   use type E.Count;
   use type E.Span;
   use type E.Bytes;
   use type E.Value_Kind;
   use type E.Q.Byte;
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span renames P.Raw_Source_Field;
   function Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (Worldline.Recovery_Archive.Ordered_Source_Value_Matches
       (Data, Data, Left, Right, False, False));
   function Num (Data : E.Bytes; Item : E.Span) return Valid_Big_Integer renames P.Number;
   -- One entity per field name shared by a validity guard and its later read
   -- (the prover treats two equal literals as distinct terms).
   Raw_Name : constant String := "raw";
   Stat_Name : constant String := "stat";
   Status_Name : constant String := "status";
   function Field_Same (Data : E.Bytes; A, B : E.Span; Name : String) return Boolean is
     (Same (Data, F (Data, A, Name), F (Data, B, Name)));
   function Bytes_Is (Data : E.Bytes; Item : E.Span; Value : String) return Boolean is
   begin
      if not R.Archive_Bytes_Valid (Data, Item) then return False; end if;
      declare Raw : constant E.Bytes := R.Archive_Bytes (Data, Item); begin
         return Raw'Length = E.Count (Value'Length) and then
           (for all I in Value'Range => Raw (Raw'First + E.Count (I - Value'First)) = Character'Pos (Value (I)));
      end;
   end Bytes_Is;
   function Credentials (Data : E.Bytes; Item : E.Span) return E.Span is
     (if R.Archive_Bytes_Valid (Data, Item) then Item else F (Data, Item, "sender"));
   function Credential (Data : E.Bytes; Item : E.Span; Part : Positive) return Valid_Big_Integer is
      Result : Big_Integer := To_Big_Integer (0);
   begin
      if Part > 3 or else not R.Archive_Bytes_Valid (Data, Item) then return To_Big_Integer (-1); end if;
      declare Raw : constant E.Bytes := R.Archive_Bytes (Data, Item); begin
         if Raw'Length /= 12 then return To_Big_Integer (-1); end if;
         for I in reverse E.Count range 0 .. 3 loop
            Result := Result * To_Big_Integer (256) + To_Big_Integer
              (Integer (Raw (Raw'First + E.Count (Part - 1) * 4 + I)));
         end loop;
         if Part = 1 and then Result >= To_Big_Integer (2) ** 31 then
            Result := Result - To_Big_Integer (2) ** 32;
         end if;
      end;
      return Result;
   end Credential;
   function Text_Payload (Data : E.Bytes; Item : E.Span) return E.Byte_View is
      V : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      if V.Form = E.Text_Value and then E.Bytes_Valid (Data, V.Payload) then
         return V.Payload;
      else
         return (Encoded => (1, 0), Level => 0);
      end if;
   end Text_Payload;
   function Namespace_Node (Data : E.Bytes; Node : E.Span; Kind : String) return Boolean is
      Link_View : constant E.Byte_View := Text_Payload (Data, F (Data, Node, "link"));
      Identity : constant E.Span := F (Data, Node, "identity");
   begin
      if not E.Bytes_Valid (Data, Link_View) then return False; end if;
      declare Link : constant E.Bytes := E.Materialize (Data, Link_View); begin
         if Link'Length <= E.Count (Kind'Length) + 3
           or else not (for all I in Kind'Range => Link (Link'First + E.Count (I - Kind'First)) = Character'Pos (Kind (I)))
           or else Link (Link'First + E.Count (Kind'Length)) /= 58
           or else Link (Link'First + E.Count (Kind'Length) + 1) /= 91
           or else Link (Link'Last) /= 93
           or else not R.Archive_Integer_Valid (Data, F (Data, Identity, "device"))
           or else not R.Archive_Integer_Valid (Data, F (Data, Identity, "inode"))
           or else Num (Data, F (Data, Identity, "device")) < To_Big_Integer (0)
         then return False; end if;
         return P.Decimal (Link, (Link'First + E.Count (Kind'Length) + 2,
                  Link'Length - E.Count (Kind'Length) - 3)) = Num (Data, F (Data, Identity, "inode"))
           and then Num (Data, F (Data, Identity, "inode")) > To_Big_Integer (0);
      end;
   end Namespace_Node;
   function Identity_Same (Data : E.Bytes; A, B : E.Span) return Boolean is
     (R.Archive_Integer_Valid (Data, F (Data, A, "device"))
      and then R.Archive_Integer_Valid (Data, F (Data, A, "inode"))
      and then Field_Same (Data, A, B, "device") and then Field_Same (Data, A, B, "inode"));
   function Node_Same (Data : E.Bytes; A, B : E.Span) return Boolean is
     (Field_Same (Data, A, B, "link") and then Identity_Same (Data, F (Data, A, "identity"), F (Data, B, "identity")));
   function Node (Data : E.Bytes; Source : E.Span; Name : String) return E.Span is
     (F (Data, F (Data, Source, "namespaces"), Name));
   function Stable_Proc (Data : E.Bytes; Before, After : E.Span) return Boolean
     with Global => null,
       Post => (if Stable_Proc'Result then
         R.Archive_Bytes_Valid (Data, F (Data, Before, Stat_Name)) and then
         R.Archive_Bytes_Valid (Data, F (Data, After, Stat_Name)) and then
         R.Archive_Bytes_Valid (Data, F (Data, Before, Status_Name)) and then
         R.Archive_Bytes_Valid (Data, F (Data, After, Status_Name)))
   is
      Before_Stat : constant E.Span := F (Data, Before, Stat_Name);
      After_Stat : constant E.Span := F (Data, After, Stat_Name);
      Before_Status : constant E.Span := F (Data, Before, Status_Name);
      After_Status : constant E.Span := F (Data, After, Status_Name);
   begin
      if not R.Archive_Bytes_Valid (Data, Before_Stat)
        or else not R.Archive_Bytes_Valid (Data, After_Stat)
        or else not R.Archive_Bytes_Valid (Data, Before_Status)
        or else not R.Archive_Bytes_Valid (Data, After_Status)
      then return False; end if;
      declare
         A : constant E.Bytes := R.Archive_Bytes (Data, Before_Status);
         B : constant E.Bytes := R.Archive_Bytes (Data, After_Status);
         SA_Raw : constant E.Bytes := R.Archive_Bytes (Data, Before_Stat);
         SB_Raw : constant E.Bytes := R.Archive_Bytes (Data, After_Stat);
         PA : constant Big_Integer := P.Stat_Number (SA_Raw, 1);
         PP : constant Big_Integer := P.Stat_Number (SA_Raw, 4);
         Start : constant Big_Integer := P.Stat_Number (SA_Raw, 22);
         NA : constant E.Span := P.Line (A, "NSpid", 58);
         NB : constant E.Span := P.Line (B, "NSpid", 58);
      begin
         if PA <= To_Big_Integer (0) or else PP < To_Big_Integer (0) or else Start < To_Big_Integer (0)
           or else P.Stat_Number (SB_Raw, 1) /= PA or else P.Stat_Number (SB_Raw, 4) /= PP
           or else P.Stat_Number (SB_Raw, 22) /= Start
           or else P.Decimal (A, P.Word (A, P.Line (A, "Pid", 58), 1)) /= PA
           or else P.Decimal (B, P.Word (B, P.Line (B, "Pid", 58), 1)) /= PA
           or else P.Decimal (A, P.Word (A, P.Line (A, "PPid", 58), 1)) /= PP
           or else P.Decimal (B, P.Word (B, P.Line (B, "PPid", 58), 1)) /= PP
           or else NA.Length = 0 or else not E.C.P.Valid (A, NA) or else not E.C.P.Valid (B, NB)
           or else NA.Length /= NB.Length
           or else not (for all I in E.Count range 0 .. NA.Length - 1 =>
             A (NA.First + I) = B (NB.First + I))
           or else P.Word (A, P.Line (A, "Uid", 58), 5).Length /= 0
           or else P.Word (B, P.Line (B, "Uid", 58), 5).Length /= 0
           or else P.Word (A, P.Line (A, "Gid", 58), 5).Length /= 0
           or else P.Word (B, P.Line (B, "Gid", 58), 5).Length /= 0
         then return False; end if;
         for I in 1 .. 4 loop
            declare U : constant Big_Integer := P.Decimal (A, P.Word (A, P.Line (A, "Uid", 58), I));
                    G : constant Big_Integer := P.Decimal (A, P.Word (A, P.Line (A, "Gid", 58), I)); begin
               if U < To_Big_Integer (0) or else G < To_Big_Integer (0)
                 or else U /= P.Decimal (B, P.Word (B, P.Line (B, "Uid", 58), I))
                 or else G /= P.Decimal (B, P.Word (B, P.Line (B, "Gid", 58), I))
               then return False; end if;
            end;
         end loop;
      end;
      return True;
   end Stable_Proc;
   function Actor_Source (Data : E.Bytes; Actor, Source : E.Span) return Boolean is
      Raw : constant E.Span := F (Data, Source, "raw");
      After : constant E.Span := F (Data, Source, "after");
   begin
      if not R.Archive_Text_Is (Data, F (Data, Source, "schema"), "worldline.scoped-actor-namespace-source-v1")
        or else not Field_Same (Data, Actor, F (Data, Source, "actor"), "pid")
        or else not Field_Same (Data, Actor, F (Data, Source, "actor"), "start_tick")
        or else not Field_Same (Data, Actor, F (Data, Source, "actor"), "credentials")
        or else not Same (Data, F (Data, Actor, "boot"), F (Data, Source, "boot"))
        or else not R.Archive_Bytes_Valid (Data, F (Data, Actor, Stat_Name))
        or else not R.Archive_Bytes_Valid (Data, F (Data, Raw, "uid_map"))
        or else not R.Archive_Bytes_Valid (Data, F (Data, Raw, "gid_map"))
        or else not Stable_Proc (Data, Raw, After)
        or else (F (Data, Actor, "status").Length > 0 and then not Stable_Proc (Data, Actor, Raw))
        or else (F (Data, Actor, "uid_map").Length > 0 and then not Field_Same (Data, Actor, Raw, "uid_map"))
        or else (F (Data, Actor, "gid_map").Length > 0 and then not Field_Same (Data, Actor, Raw, "gid_map"))
        or else not Field_Same (Data, Raw, After, "uid_map") or else not Field_Same (Data, Raw, After, "gid_map")
        or else not Namespace_Node (Data, Node (Data, Source, "pid"), "pid")
        or else not Namespace_Node (Data, Node (Data, Source, "user"), "user")
        or else (F (Data, Actor, "namespaces").Length > 0 and then
          (not Node_Same (Data, Node (Data, Actor, "pid"), Node (Data, Source, "pid"))
           or else not Node_Same (Data, Node (Data, Actor, "user"), Node (Data, Source, "user"))))
      then return False; end if;
      declare Stat : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Raw, Stat_Name));
              Original_Stat : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Actor, Stat_Name));
              Status : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Raw, Status_Name)); begin
         return Num (Data, F (Data, Actor, "pid")) = P.Stat_Number (Stat, 1)
           and then Num (Data, F (Data, Actor, "start_tick")) = P.Stat_Number (Stat, 22)
           and then P.Stat_Number (Original_Stat, 1) = P.Stat_Number (Stat, 1)
           and then P.Stat_Number (Original_Stat, 22) = P.Stat_Number (Stat, 22)
           and then Credential (Data, F (Data, Actor, "credentials"), 1) = Num (Data, F (Data, Actor, "pid"))
           and then Credential (Data, F (Data, Actor, "credentials"), 2) = P.Decimal (Status, P.Word (Status, P.Line (Status, "Uid", 58), 1))
           and then Credential (Data, F (Data, Actor, "credentials"), 3) = P.Decimal (Status, P.Word (Status, P.Line (Status, "Gid", 58), 1));
      end;
   end Actor_Source;
   -- Linux uid_map/gid_map: complete newline-separated triples, with disjoint
   -- inside and outside intervals. The only bounds are the actual uint32 UAPI.
   function Map_Line_End (Raw : E.Bytes; Start : E.Count) return E.Count
     with Global => null,
       Pre => Start >= Raw'First and then Raw'Last < E.Count'Last,
       Post => Map_Line_End'Result >= Start and then
         (if Start <= Raw'Last then Map_Line_End'Result <= Raw'Last + 1
          else Map_Line_End'Result = Start) and then
         (if Map_Line_End'Result <= Raw'Last then Raw (Map_Line_End'Result) = 10) and then
         (for all K in Start .. Map_Line_End'Result - 1 => Raw (K) /= 10)
   is
      Finish : E.Count := Start;
   begin
      while Finish <= Raw'Last and then Raw (Finish) /= 10 loop
         pragma Loop_Invariant (Finish in Start .. Raw'Last);
         pragma Loop_Invariant (for all K in Start .. Finish - 1 => Raw (K) /= 10);
         pragma Loop_Variant (Increases => Finish);
         Finish := Finish + 1;
      end loop;
      return Finish;
   end Map_Line_End;
   function Map_Valid (Raw : E.Bytes) return Boolean
     with Global => null,
       Post => (if Map_Valid'Result then Raw'First >= 0 and then Raw'Last < E.Count'Last
         and then (Raw'Length = 0 or else Raw (Raw'Last) = 10))
   is
      Start : E.Count;
      Limit : constant Big_Integer := To_Big_Integer (2) ** 32 - To_Big_Integer (1);
   begin
      -- Totalized: an empty map whose lower bound lies below E.Count raised at
      -- the original Start initialization; a map ending at E.Count'Last was
      -- either refused or raised (Finish + 1). Both now refuse; every other
      -- input takes the original path unchanged.
      if Raw'Length = 0 then return Raw'First >= 0; end if;
      if Raw'Last = E.Count'Last then return False; end if;
      Start := Raw'First;
      while Start <= Raw'Last loop
         pragma Loop_Variant (Increases => Start);
         pragma Loop_Invariant (Start >= Raw'First);
         pragma Loop_Invariant (Start = Raw'First or else Raw (Start - 1) = 10);
         declare Finish : constant E.Count := Map_Line_End (Raw, Start);
                 Line : constant E.Span := (Start, Finish - Start);
                 A : constant Big_Integer := P.Decimal (Raw, P.Word (Raw, Line, 1));
                 B : constant Big_Integer := P.Decimal (Raw, P.Word (Raw, Line, 2));
                 N : constant Big_Integer := P.Decimal (Raw, P.Word (Raw, Line, 3));
                 Prior : E.Count := Raw'First; begin
            if Finish > Raw'Last or else A < To_Big_Integer (0) or else B < To_Big_Integer (0)
              or else N <= To_Big_Integer (0) or else A + N > Limit or else B + N > Limit
              or else P.Word (Raw, Line, 4).Length /= 0 then return False; end if;
            while Prior < Start loop
               pragma Loop_Variant (Increases => Prior);
               pragma Loop_Invariant (Prior >= Raw'First);
               declare Stop : constant E.Count := Map_Line_End (Raw, Prior);
                       Other : constant E.Span := (Prior, Stop - Prior);
                       C : constant Big_Integer := P.Decimal (Raw, P.Word (Raw, Other, 1));
                       D : constant Big_Integer := P.Decimal (Raw, P.Word (Raw, Other, 2));
                       M : constant Big_Integer := P.Decimal (Raw, P.Word (Raw, Other, 3)); begin
                  if (A < C + M and then C < A + N) or else (B < D + M and then D < B + N) then return False; end if;
                  pragma Assert (Raw (Start - 1) = 10);
                  pragma Assert (Stop < Start);
                  Prior := Stop + 1;
               end;
            end loop;
            Start := Finish + 1;
         end;
      end loop;
      return True;
   end Map_Valid;
   function Map_Value (Raw : E.Bytes; Value, Overflow : Valid_Big_Integer) return Valid_Big_Integer
     with Global => null, Pre => Raw'First >= 0 and then Raw'Last < E.Count'Last
       and then (Raw'Length = 0 or else Raw (Raw'Last) = 10)
   is
      Start : E.Count := Raw'First;
   begin
      while Start <= Raw'Last loop
         pragma Loop_Variant (Increases => Start);
         pragma Loop_Invariant (Start >= Raw'First);
         declare Finish : constant E.Count := Map_Line_End (Raw, Start);
                 Line : constant E.Span := (Start, Finish - Start);
                 A : constant Big_Integer := P.Decimal (Raw, P.Word (Raw, Line, 1));
                 B : constant Big_Integer := P.Decimal (Raw, P.Word (Raw, Line, 2));
                 N : constant Big_Integer := P.Decimal (Raw, P.Word (Raw, Line, 3)); begin
            if Value >= A and then Value < A + N then return B + Value - A; end if;
            Start := Finish + 1;
         end;
      end loop;
      return Overflow;
   end Map_Value;
   function ID_Matches (Data : E.Bytes; Sent, Received, Sender, Receiver, View : E.Span;
                        Map_Name, Overflow_Name : String; Part : Positive) return Boolean is
      Map_Item : constant E.Span := F (Data, F (Data, View, "raw"), Map_Name);
      Overflow_Item : constant E.Span := F (Data, Receiver, Overflow_Name);
      Sender_Status : constant E.Span := F (Data, F (Data, Sender, Raw_Name), Status_Name);
      View_Status_Item : constant E.Span := F (Data, F (Data, View, Raw_Name), Status_Name);
      A : constant Big_Integer := Credential (Data, Sent, Part);
      B : constant Big_Integer := Credential (Data, Received, Part);
   begin
      if A < To_Big_Integer (0) or else B < To_Big_Integer (0)
        or else not R.Archive_Bytes_Valid (Data, Map_Item)
        or else not R.Archive_Bytes_Valid (Data, Sender_Status)
        or else not R.Archive_Bytes_Valid (Data, View_Status_Item)
        or else not Field_Same (Data, F (Data, View, "raw"), F (Data, View, "after"), Map_Name)
        or else not Node_Same (Data, Node (Data, Sender, "user"), Node (Data, View, "user"))
        or else not Node_Same (Data, Node (Data, Receiver, "user"), F (Data, View, "reader_user_namespace"))
      then return False; end if;
      declare
         Map_Raw : constant E.Bytes := R.Archive_Bytes (Data, Map_Item);
         Original_Status : constant E.Bytes := R.Archive_Bytes (Data, Sender_Status);
         View_Status : constant E.Bytes := R.Archive_Bytes (Data, View_Status_Item);
         Name : constant String := (if Part = 2 then "Uid" else "Gid");
         Identity_Map : constant Boolean := Node_Same (Data, Node (Data, Sender, "user"), Node (Data, Receiver, "user"));
         Overflow : Big_Integer := To_Big_Integer (-1);
      begin
         if not Map_Valid (Map_Raw) then return False; end if;
         if Identity_Map then
            if A /= B or else not Same (Data, Map_Item, F (Data, F (Data, Sender, "raw"), Map_Name)) then return False; end if;
         else
            if not R.Archive_Bytes_Valid (Data, Overflow_Item) then return False; end if;
            declare Raw : constant E.Bytes := R.Archive_Bytes (Data, Overflow_Item);
                    -- An empty operand reads as the empty word either way; this
                    -- form is also defined when its lower bound is outside E.Count.
                    Whole : constant E.Span := (if Raw'Length = 0 then (1, 0) else (Raw'First, Raw'Length)); begin
               Overflow := P.Decimal (Raw, P.Word (Raw, Whole, 1));
               if Overflow < To_Big_Integer (0) or else Overflow >= To_Big_Integer (2) ** 32
                 or else P.Word (Raw, Whole, 2).Length /= 0
                 or else B /= Map_Value (Map_Raw, A, Overflow)
               then return False; end if;
            end;
         end if;
         for I in 1 .. 4 loop
            declare
               Original_ID : constant Big_Integer := P.Decimal (Original_Status, P.Word (Original_Status, P.Line (Original_Status, Name, 58), I));
               Observed_ID : constant Big_Integer := P.Decimal (View_Status, P.Word (View_Status, P.Line (View_Status, Name, 58), I));
            begin
               if Original_ID < To_Big_Integer (0) or else Observed_ID /=
                 (if Identity_Map then Original_ID else Map_Value (Map_Raw, Original_ID, Overflow))
               then return False; end if;
            end;
         end loop;
         return True;
      end;
   end ID_Matches;
   function Last_PID (Raw : E.Bytes) return Valid_Big_Integer is
      Item : constant E.Span := P.Line (Raw, "NSpid", 58);
      Position : E.Count := 0;
      Last : Big_Integer := To_Big_Integer (-1);
   begin
      if not E.C.P.Valid (Raw, Item) then return Last; end if;
      while Position < Item.Length loop
         pragma Loop_Variant (Increases => Position);
         while Position < Item.Length and then Raw (Item.First + Position) in 9 | 32 loop
            pragma Loop_Invariant (Position in Position'Loop_Entry .. Item.Length); pragma Loop_Variant (Increases => Position);
            Position := Position + 1;
         end loop;
         declare Start : constant E.Count := Position; begin
            while Position < Item.Length and then Raw (Item.First + Position) not in 9 | 32 loop
               pragma Loop_Invariant (Position in Start .. Item.Length); pragma Loop_Variant (Increases => Position);
               Position := Position + 1;
            end loop;
            if Position > Start then
               Last := P.Decimal (Raw, (Item.First + Start, Position - Start));
               if Last <= To_Big_Integer (0) then return To_Big_Integer (-1); end if;
            end if;
         end;
      end loop;
      return Last;
   end Last_PID;
   function Root_PID_Matches (Data : E.Bytes; Sent, Received, Sender, Receiver, Context : E.Span) return Boolean is
      Frame : constant E.Span := F (Data, Context, "original_root_frame");
      Transfer : constant E.Span := F (Data, F (Data, Frame, "subject_custody"), "transfer");
      Current_Transfer : constant E.Span := F (Data, Context, "current_transfer");
      Process : constant E.Span := F (Data, Context, "process");
      Original : constant E.Span := F (Data, Context, "original_process");
      Source : constant E.Span := F (Data, Context, "process_source");
      Raw : constant E.Span := F (Data, Source, "raw");
      Measured : constant E.Span := F (Data, Context, "measured");
      Execution : constant E.Span := F (Data, F (Data, F (Data, F (Data, Frame, "worker"), "execution_ack"), "record"), "event");
      Record_Item : constant E.Span := F (Data, Execution, "record");
      Origins : constant E.Span := F (Data, Frame, "origin_descriptors");
      Held : constant E.Span := F (Data, Context, "worker_namespace_identity");
      Host : constant Big_Integer := Num (Data, F (Data, Process, "host_pid"));
      Local : constant Big_Integer := Num (Data, F (Data, Measured, "namespace_pid"));
      S_Node : constant E.Span := Node (Data, Sender, "pid");
      R_Node : constant E.Span := Node (Data, Receiver, "pid");
      Worker : E.Span;
   begin
      if not R.Archive_Record_Is (Data, Process, "ProcessObservation")
        or else not R.Archive_Record_Is (Data, Original, "ProcessObservation")
        or else not Field_Same (Data, Transfer, Current_Transfer, "origin_pid_ns")
        or else not Field_Same (Data, Transfer, Current_Transfer, "origin_user_ns")
        or else not Field_Same (Data, Transfer, Current_Transfer, "held_pid_ns")
        or else not Node_Same (Data, Node (Data, Sender, "user"), Node (Data, Receiver, "user"))
        or else not Same (Data, F (Data, Transfer, "origin_user_ns"), F (Data, Node (Data, Sender, "user"), "link"))
        or else not Same (Data, Measured, F (Data, Record_Item, "measured"))
        or else not Same (Data, Original, F (Data, Record_Item, "process"))
        or else not Same (Data, Execution, F (Data, Context, "execution_event"))
        or else not Identity_Same (Data, Held, F (Data, Origins, "worker_namespace"))
        or else not Identity_Same (Data, Held, F (Data, Source, "namespace_identity"))
        or else not Identity_Same (Data, Held, F (Data, F (Data, F (Data, Frame, "worker"), "held"), "namespace_identity"))
        or else not Identity_Same (Data, F (Data, Context, "worker_pidfd_identity"), F (Data, Origins, "worker_pidfd"))
        or else not Identity_Same (Data, F (Data, Context, "worker_pidfd_identity"), F (Data, Source, "worker_pidfd_identity"))
        or else not Identity_Same (Data, F (Data, Context, "host_proc_identity"), F (Data, Origins, "host_proc"))
        or else not Identity_Same (Data, F (Data, Context, "host_proc_identity"), F (Data, Source, "host_proc_identity"))
        or else not P.Namespace_Matches (Data, F (Data, Process, "namespace"), Held)
        or else not Field_Same (Data, Process, Original, "namespace")
        or else not Field_Same (Data, Process, Original, "host_pid")
        or else not Field_Same (Data, Process, Original, "start_tick")
        or else not Field_Same (Data, Process, Original, "real_uid")
        or else not Field_Same (Data, Process, Original, "effective_uid")
        or else not Field_Same (Data, Process, Original, "saved_uid")
        or else not Field_Same (Data, Process, Original, "real_gid")
        or else not Field_Same (Data, Process, Original, "effective_gid")
        or else not Field_Same (Data, Process, Original, "saved_gid")
        or else Host <= To_Big_Integer (0) or else Local <= To_Big_Integer (0)
        or else Host /= Num (Data, F (Data, Measured, "host_pid"))
        or else not P.Id_Hex (Data, F (Data, Context, "measured_sender_bytes"), F (Data, Measured, "raw_sender_credentials"))
        or else Credential (Data, F (Data, Context, "measured_sender_bytes"), 1) /= Host
        or else Credential (Data, F (Data, Context, "measured_sender_bytes"), 2) /= Num (Data, F (Data, Measured, "sender_real_uid"))
        or else Credential (Data, F (Data, Context, "measured_sender_bytes"), 3) /= Num (Data, F (Data, Measured, "sender_real_gid"))
        or else not Stable_Proc (Data, Raw, F (Data, Source, "after"))
        or else not Same (Data, F (Data, Process, "raw_status"), F (Data, Raw, "status"))
        or else not Same (Data, F (Data, Process, "raw_stat"), F (Data, Raw, "stat"))
        or else not Same (Data, F (Data, Process, "raw_cgroup"), F (Data, Raw, "cgroup"))
        or else not Same (Data, F (Data, Process, "raw_maps"), F (Data, Raw, "maps"))
        or else not Same (Data, F (Data, Process, "raw_cmdline"), F (Data, Raw, "cmdline"))
        or else not Bytes_Is (Data, F (Data, Process, "pidfd_wait"), "PIDFD_LIVE")
      then return False; end if;
      declare Status : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Raw, Status_Name));
              Stat : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Raw, Stat_Name)); begin
         if Last_PID (Status) /= Local or else P.Stat_Number (Stat, 1) /= Host
           or else P.Stat_Number (Stat, 22) /= Num (Data, F (Data, Process, "start_tick"))
           or else P.Decimal (Status, P.Word (Status, P.Line (Status, "NSpid", 58), 1)) /= Host
           or else P.Stat_Number (Stat, 4) /= Num (Data, F (Data, Process, "parent_pid"))
           or else P.Decimal (Status, P.Word (Status, P.Line (Status, "Uid", 58), 1)) /= Num (Data, F (Data, Process, "real_uid"))
           or else P.Decimal (Status, P.Word (Status, P.Line (Status, "Uid", 58), 2)) /= Num (Data, F (Data, Process, "effective_uid"))
           or else P.Decimal (Status, P.Word (Status, P.Line (Status, "Uid", 58), 3)) /= Num (Data, F (Data, Process, "saved_uid"))
           or else P.Decimal (Status, P.Word (Status, P.Line (Status, "Gid", 58), 1)) /= Num (Data, F (Data, Process, "real_gid"))
           or else P.Decimal (Status, P.Word (Status, P.Line (Status, "Gid", 58), 2)) /= Num (Data, F (Data, Process, "effective_gid"))
           or else P.Decimal (Status, P.Word (Status, P.Line (Status, "Gid", 58), 3)) /= Num (Data, F (Data, Process, "saved_gid"))
           or else Num (Data, F (Data, Process, "real_uid")) /= Num (Data, F (Data, Measured, "sender_real_uid"))
           or else Num (Data, F (Data, Process, "real_gid")) /= Num (Data, F (Data, Measured, "sender_real_gid"))
         then return False; end if;
      end;
      if Identity_Same (Data, F (Data, R_Node, "identity"), Held)
        and then Identity_Same (Data, F (Data, S_Node, "identity"), Held)
      then
         Worker := Sender;
         if not Same (Data, F (Data, Transfer, "held_pid_ns"), F (Data, S_Node, "link"))
           or else Credential (Data, Sent, 1) /= Local or else Credential (Data, Received, 1) /= Local
         then return False; end if;
      elsif Identity_Same (Data, F (Data, R_Node, "identity"), Held) then
         Worker := Receiver;
         if not Same (Data, F (Data, Transfer, "origin_pid_ns"), F (Data, S_Node, "link"))
           or else not Same (Data, F (Data, Transfer, "held_pid_ns"), F (Data, R_Node, "link"))
           or else Credential (Data, Sent, 1) /= Num (Data, F (Data, F (Data, Sender, "actor"), "pid"))
           or else Credential (Data, Received, 1) /= To_Big_Integer (0)
         then return False; end if;
      elsif Identity_Same (Data, F (Data, S_Node, "identity"), Held) then
         Worker := Sender;
         if not Same (Data, F (Data, Transfer, "origin_pid_ns"), F (Data, R_Node, "link"))
           or else not Same (Data, F (Data, Transfer, "held_pid_ns"), F (Data, S_Node, "link"))
           or else Credential (Data, Sent, 1) /= Local or else Credential (Data, Received, 1) /= Host
         then return False; end if;
      else return False; end if;
      return Num (Data, F (Data, F (Data, Worker, "actor"), "pid")) = Local
        and then Num (Data, F (Data, F (Data, Worker, "actor"), "start_tick")) = Num (Data, F (Data, Process, "start_tick"))
        and then (R.Archive_Is_None (Data, F (Data, Current_Transfer, "reader_pid_ns"))
          or else Same (Data, F (Data, Current_Transfer, "reader_pid_ns"), F (Data, Node (Data, Worker, "pid"), "link")))
        and then (R.Archive_Is_None (Data, F (Data, Current_Transfer, "reader_user_ns"))
          or else Same (Data, F (Data, Current_Transfer, "reader_user_ns"), F (Data, Node (Data, Worker, "user"), "link")));
   end Root_PID_Matches;
   function SCM_Credentials_Match
     (Data : E.Bytes; Send, Receive, OriginalActor, CurrentActor, NamespaceSource : E.Span) return Boolean
   is
      Sent : constant E.Span := Credentials (Data, Send);
      Received : constant E.Span := Credentials (Data, Receive);
      Sender : constant E.Span := F (Data, NamespaceSource, "sender_actor_namespace");
      Receiver : constant E.Span := F (Data, NamespaceSource, "receiver_actor_namespace");
      View : constant E.Span := F (Data, NamespaceSource, "sender_view");
   begin
      if not R.Archive_Text_Is (Data, F (Data, NamespaceSource, "schema"), "worldline.scoped-scm-namespace-source-v1")
        or else not Actor_Source (Data, OriginalActor, Sender) or else not Actor_Source (Data, CurrentActor, Receiver)
        or else not Same (Data, F (Data, OriginalActor, "boot"), F (Data, CurrentActor, "boot"))
        or else not Same (Data, Sent, F (Data, OriginalActor, "credentials"))
        or else Credential (Data, Received, 1) < To_Big_Integer (0)
        or else not Stable_Proc (Data, F (Data, View, Raw_Name), F (Data, View, "after"))
        or else not Namespace_Node (Data, Node (Data, View, "pid"), "pid")
        or else not Namespace_Node (Data, Node (Data, View, "user"), "user")
        or else not Node_Same (Data, Node (Data, View, "pid"), Node (Data, Sender, "pid"))
        or else not ID_Matches (Data, Sent, Received, Sender, Receiver, View, "uid_map", "overflow_uid", 2)
        or else not ID_Matches (Data, Sent, Received, Sender, Receiver, View, "gid_map", "overflow_gid", 3)
      then return False; end if;
      declare
         Raw : constant E.Span := F (Data, View, Raw_Name);
         Status : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Raw, Status_Name));
         Stat : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Raw, Stat_Name));
      begin
         if Last_PID (Status) /= Num (Data, F (Data, OriginalActor, "pid"))
           or else P.Stat_Number (Stat, 22) /= Num (Data, F (Data, OriginalActor, "start_tick"))
           or else (not R.Archive_Is_None (Data, F (Data, NamespaceSource, "root_context"))
             and then Identity_Same (Data, F (Data, Node (Data, Sender, "pid"), "identity"),
               F (Data, F (Data, NamespaceSource, "root_context"), "worker_namespace_identity"))
             and then P.Stat_Number (Stat, 1) /= Num (Data, F (Data, F (Data, F (Data, NamespaceSource, "root_context"), "process"), "host_pid")))
           or else (R.Archive_Is_None (Data, F (Data, NamespaceSource, "root_context"))
             and then P.Stat_Number (Stat, 1) /= Num (Data, F (Data, OriginalActor, "pid")))
           or else Credential (Data, Received, 2) /= P.Decimal (Status, P.Word (Status, P.Line (Status, "Uid", 58), 1))
           or else Credential (Data, Received, 3) /= P.Decimal (Status, P.Word (Status, P.Line (Status, "Gid", 58), 1))
         then return False; end if;
      end;
      if Node_Same (Data, Node (Data, Sender, "pid"), Node (Data, Receiver, "pid")) then
         return Credential (Data, Sent, 1) = Credential (Data, Received, 1)
           and then Credential (Data, Sent, 1) > To_Big_Integer (0)
           and then (R.Archive_Is_None (Data, F (Data, NamespaceSource, "root_context"))
             or else Root_PID_Matches (Data, Sent, Received, Sender, Receiver, F (Data, NamespaceSource, "root_context")));
      else return Root_PID_Matches (Data, Sent, Received, Sender, Receiver, F (Data, NamespaceSource, "root_context")); end if;
   end SCM_Credentials_Match;
   function FD_Bytes_Match (Data : E.Bytes; Rights, FD : E.Span) return Boolean is
      Value : Big_Integer := To_Big_Integer (0);
   begin
      if not R.Archive_Bytes_Valid (Data, Rights) or else not R.Archive_Integer_Valid (Data, FD) then return False; end if;
      declare Raw : constant E.Bytes := R.Archive_Bytes (Data, Rights); begin
         if Raw'Length /= 4 then return False; end if;
         for I in reverse E.Count range 0 .. 3 loop
            Value := Value * To_Big_Integer (256) + To_Big_Integer (Integer (Raw (Raw'First + I)));
         end loop;
      end;
      return Value < To_Big_Integer (2) ** 31 and then Value = Num (Data, FD);
   end FD_Bytes_Match;
   function FD_Receipt_Matches (Data : E.Bytes; Item, FD, Ucred : E.Span; Sending : Boolean) return Boolean is
      Controls : constant E.Span := F (Data, Item, "controls");
      Rights : constant E.Span := F (Data, Item, "rights");
      Have_Rights : Boolean := False;
      Have_Credentials : Boolean := False;
      Flags : constant Big_Integer := Num (Data, F (Data, Item, "flags"));
   begin
      if not R.Archive_Text_Is (Data, F (Data, Item, "call"), (if Sending then "sendmsg" else "recvmsg"))
        or else Num (Data, F (Data, Item, "result")) /= To_Big_Integer (1)
        or else Num (Data, F (Data, Item, "errno")) /= To_Big_Integer (0)
        or else not Bytes_Is (Data, F (Data, Item, "frame"), "F")
        or else not FD_Bytes_Match (Data, Rights, FD)
        or else not Same (Data, F (Data, Item, "sender"), Ucred)
        or else not R.Archive_Is_Sequence (Data, Controls) or else R.Archive_Length (Data, Controls) /= 2
        or else (Sending and then Flags /= To_Big_Integer (16384))
        or else (not Sending and then
          (Num (Data, F (Data, Item, "input_flags")) /= To_Big_Integer (1073741824)
           or else Flags < To_Big_Integer (0)
           or else (Flags / To_Big_Integer (32)) mod To_Big_Integer (2) /= To_Big_Integer (0)
           or else (Flags / To_Big_Integer (8)) mod To_Big_Integer (2) /= To_Big_Integer (0)))
      then return False; end if;
      for I in E.Count range 0 .. 1 loop
         declare Control : constant E.Span := R.Archive_Index (Data, Controls, I);
                 Kind : constant Big_Integer := Num (Data, R.Archive_Index (Data, Control, 1)); begin
            if not R.Archive_Is_Sequence (Data, Control) or else R.Archive_Length (Data, Control) /= 3
              or else Num (Data, R.Archive_Index (Data, Control, 0)) /= To_Big_Integer (1)
            then return False; end if;
            if Kind = To_Big_Integer (1) then
               if Have_Rights or else not Same (Data, R.Archive_Index (Data, Control, 2), Rights) then return False; end if;
               Have_Rights := True;
            elsif Kind = To_Big_Integer (2) then
               if Have_Credentials or else not Same (Data, R.Archive_Index (Data, Control, 2), Ucred) then return False; end if;
               Have_Credentials := True;
            else return False; end if;
         end;
      end loop;
      return Have_Rights and then Have_Credentials;
   end FD_Receipt_Matches;
   function Reverse_Host_Matches (Data : E.Bytes; Inventory, Broker : E.Span) return Boolean is
      Reverse_Item : constant E.Span := F (Data, Broker, "reverse_host_broker");
      Namespace : constant E.Span := F (Data, Inventory, "namespace_source");
      Context : constant E.Span := F (Data, Namespace, "root_context");
      Sender : constant E.Span := F (Data, Namespace, "sender_actor_namespace");
      Receiver : constant E.Span := F (Data, Namespace, "receiver_actor_namespace");
      Actor : constant E.Span := F (Data, Broker, "actor");
      Current : constant E.Span := F (Data, Inventory, "current_actor");
      Process : constant E.Span := F (Data, Reverse_Item, "sender_process");
      Source : constant E.Span := F (Data, Reverse_Item, "sender_process_source");
      Raw : constant E.Span := F (Data, Source, "raw");
      Primary : constant E.Span := F (Data, Context, "process");
      Transfer : constant E.Span := F (Data, Reverse_Item, "transfer");
      Header : constant E.Span := F (Data, Transfer, "header");
      Roles : constant E.Span := F (Data, Broker, "roles");
      Actual_Roles : constant E.Span := F (Data, Inventory, "roles");
      Sent_Map : constant E.Span := F (Data, Transfer, "send_receipts");
      Received_Map : constant E.Span := F (Data, Transfer, "receive_receipts");
      Host : constant Big_Integer := Num (Data, F (Data, Reverse_Item, "sender_host_pid"));
   begin
      if not Actor_Source (Data, Actor, Sender)
        or else not Actor_Source (Data, Current, Receiver)
        or else not Actor_Source (Data, F (Data, Reverse_Item, "receiver_actor"), Receiver)
        or else not Actor_Source (Data, F (Data, Transfer, "sender_actor"), Sender)
        or else not Actor_Source (Data, F (Data, Transfer, "receiver_actor"), Receiver)
        or else not Actor_Source (Data, F (Data, Header, "actor"), Sender)
        or else not Same (Data, F (Data, Header, "frame"), F (Data, Inventory, "frame"))
        or else not P.Archive_Image_Matches (Data, F (Data, Transfer, "header_raw"), F (Data, Transfer, "header_message"))
        or else not Same (Data, F (Data, F (Data, Transfer, "header_message"), "root_sync"), Header)
        or else not P.Archive_Image_Matches (Data, F (Data, Transfer, "trailer_raw"), F (Data, Transfer, "trailer_message"))
        or else not Same (Data, F (Data, F (Data, F (Data, Transfer, "trailer_message"), "transfer"), "send"), Sent_Map)
        or else not Same (Data, F (Data, F (Data, F (Data, Transfer, "trailer_message"), "transfer"), "actor"), F (Data, Transfer, "sender_actor"))
        or else not Same (Data, F (Data, F (Data, F (Data, Transfer, "trailer_message"), "transfer"), "source"), F (Data, Transfer, "sender_source"))
        or else not Same (Data, F (Data, F (Data, F (Data, Transfer, "trailer_message"), "transfer"), "channel"), F (Data, Transfer, "send_channel"))
        or else not Same (Data, F (Data, F (Data, F (Data, Transfer, "trailer_message"), "transfer"), "channel_document"), F (Data, Transfer, "send_channel_document"))
        or else not Same (Data, Sent_Map, F (Data, Inventory, "sender_receipts"))
        or else not Same (Data, Received_Map, F (Data, Inventory, "receive_receipts"))
        or else not Same (Data, F (Data, Context, "worker_namespace_identity"), F (Data, Source, "namespace_identity"))
        or else not Identity_Same (Data, F (Data, Context, "worker_pidfd_identity"), F (Data, Source, "worker_pidfd_identity"))
        or else not Identity_Same (Data, F (Data, Context, "host_proc_identity"), F (Data, Source, "host_proc_identity"))
        or else not Identity_Same (Data, F (Data, Node (Data, Sender, "pid"), "identity"), F (Data, Context, "worker_namespace_identity"))
        or else not R.Archive_Record_Is (Data, Process, "ProcessObservation")
        or else not Stable_Proc (Data, Raw, F (Data, Source, "after"))
        or else not Stable_Proc (Data, Raw, F (Data, F (Data, Context, "process_source"), "raw"))
        or else not Field_Same (Data, Process, Primary, "namespace")
        or else not Field_Same (Data, Process, Primary, "host_pid")
        or else not Field_Same (Data, Process, Primary, "start_tick")
        or else not Field_Same (Data, Process, Primary, "real_uid")
        or else not Field_Same (Data, Process, Primary, "effective_uid")
        or else not Field_Same (Data, Process, Primary, "saved_uid")
        or else not Field_Same (Data, Process, Primary, "real_gid")
        or else not Field_Same (Data, Process, Primary, "effective_gid")
        or else not Field_Same (Data, Process, Primary, "saved_gid")
        or else Host <= To_Big_Integer (0) or else Host /= Num (Data, F (Data, Process, "host_pid"))
        or else Num (Data, F (Data, Broker, "worker_host_pid")) /= Num (Data, F (Data, Current, "pid"))
        or else not R.Archive_Is_Sequence (Data, Roles) or else not R.Archive_Is_Sequence (Data, Actual_Roles)
        or else R.Archive_Length (Data, Roles) = 0
        or else R.Archive_Length (Data, Roles) /= R.Archive_Length (Data, Actual_Roles)
        or else not SCM_Credentials_Match (Data, F (Data, Actor, "credentials"),
          F (Data, Transfer, "raw_ucred"), Actor, Current, Namespace)
      then return False; end if;
      declare
         Item : constant E.Span := F (Data, Reverse_Item, "sender_process_item");
         Entries : constant E.Span := F (Data, F (Data, Inventory, "frame"), "rows");
         Selected : E.Span := (1, 0);
      begin
         if not R.Archive_Is_Sequence (Data, Entries) or else R.Archive_Length (Data, Entries) = 0 then return False; end if;
         for I in E.Count range 0 .. R.Archive_Length (Data, Entries) - 1 loop
            declare Roster_Entry : constant E.Span := R.Archive_Index (Data, Entries, I); begin
               if R.Archive_Text_Is (Data, F (Data, Roster_Entry, "kind"), "ROOT")
                 and then Same (Data, F (Data, Item, "descriptor"), F (Data, F (Data, Roster_Entry, "roles"), "worker_pidfd"))
               then
                  if Selected.Length > 0 then return False; end if;
                  Selected := Roster_Entry;
               end if;
            end;
         end loop;
         if Selected.Length = 0
           or else not Same (Data, F (Data, Item, "observation"), Process)
           or else not Same (Data, F (Data, Item, "raw"), Source)
           or else not P.Process_Source_Matches (Data, Item, Inventory,
             P.Member_Value (Data, F (Data, Inventory, "current_descriptors"), F (Data, F (Data, Selected, "roles"), "worker_namespace")),
             F (Data, F (Data, Selected, "row"), "actual_unit"), F (Data, F (Data, Selected, "row"), "invocation"))
         then return False; end if;
      end;
      for I in E.Count range 0 .. R.Archive_Length (Data, Roles) - 1 loop
         declare
            Role : constant E.Span := R.Archive_Index (Data, Roles, I);
            Name : constant E.Span := F (Data, Role, "role");
            Actual : E.Span := (1, 0);
            KCMP : constant E.Span := F (Data, Role, "kcmp");
            Args : constant E.Span := F (Data, KCMP, "args");
            Sent : constant E.Span := P.Member_Value (Data, Sent_Map, Name);
            Received : constant E.Span := P.Member_Value (Data, Received_Map, Name);
         begin
            if I > 0 then
               for J in E.Count range 0 .. I - 1 loop
                  if Same (Data, Name, F (Data, R.Archive_Index (Data, Roles, J), "role")) then return False; end if;
               end loop;
            end if;
            for J in E.Count range 0 .. R.Archive_Length (Data, Actual_Roles) - 1 loop
               declare Candidate : constant E.Span := R.Archive_Index (Data, Actual_Roles, J); begin
                  if Same (Data, Name, F (Data, Candidate, "role")) then
                     if Actual.Length > 0 then return False; end if;
                     Actual := Candidate;
                  end if;
               end;
            end loop;
            if Actual.Length = 0 or else not Field_Same (Data, Role, Actual, "front_fd")
              or else not Field_Same (Data, Role, Actual, "worker_fd")
              or else not Same (Data, F (Data, Role, "origin"), F (Data, Actual, "origin"))
              or else not Same (Data, F (Data, Role, "current"), F (Data, Actual, "current"))
              or else not R.Archive_Text_Is (Data, F (Data, KCMP, "call"), "kcmp")
              or else Num (Data, F (Data, Args, "pid1")) /= Host
              or else Num (Data, F (Data, Args, "pid2")) /= Num (Data, F (Data, Current, "pid"))
              or else Num (Data, F (Data, Args, "type")) /= To_Big_Integer (0)
              or else not Same (Data, F (Data, Args, "idx1"), F (Data, Role, "front_fd"))
              or else not Same (Data, F (Data, Args, "idx2"), F (Data, Role, "worker_fd"))
              or else Num (Data, F (Data, KCMP, "result")) /= To_Big_Integer (0)
              or else Num (Data, F (Data, KCMP, "errno")) /= To_Big_Integer (0)
              or else Sent.Length = 0 or else not R.Archive_Is_Sequence (Data, Received)
              or else R.Archive_Length (Data, Received) /= 1
            then return False; end if;
            if not FD_Receipt_Matches (Data, Sent,
                 F (Data, Role, "front_fd"), F (Data, Actor, "credentials"), True)
              or else not FD_Receipt_Matches (Data, R.Archive_Index (Data, Received, 0),
                 F (Data, Role, "worker_fd"), F (Data, Transfer, "raw_ucred"), False)
            then return False; end if;
         end;
      end loop;
      return Same (Data, F (Data, Transfer, "raw_ucred"), F (Data, Transfer, "header_sender"))
        and then Same (Data, F (Data, Transfer, "raw_ucred"), F (Data, Transfer, "trailer_sender"));
   end Reverse_Host_Matches;
end Worldline.Scoped_Capture_Namespace_Projection;

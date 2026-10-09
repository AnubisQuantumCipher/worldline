with Worldline.Custody_V2_Delta_Grammar;
with Worldline.Custody_V2_Root_Evidence;
with Interfaces;
with Worldline.Custody_V2_Owner_Correspondence;
with Worldline.Custody_V2_Operation_Journal;
with Worldline.Retained_Evidence_Replay;
with Worldline.Startup_Admission;
with Worldline.Custody_V2_Root_Values;
with Worldline.Custody_V2_Archive_Projection;
with Worldline.Scoped_Capture_Projection;
package body Worldline.Custody_V2_Mutation_Decision with SPARK_Mode is
   package V renames I.V;
   package T renames V.S;
   package C renames F.C;
   package S renames F.S;
   package M renames F.M;
   package A renames F.A;
   package R renames A.R;
   package J renames F.J;
   package P renames F.P;
   package OC renames Worldline.Custody_V2_Owner_Correspondence;
   package OJ renames Worldline.Custody_V2_Operation_Journal;
   package ER renames Worldline.Retained_Evidence_Replay;
   use type Q.Byte;
   use type I.Decode_Status;
   use type I.Original_Format;
   use type F.Fold_Status;
   use type F.Status;
   use type M.Event_Kind;
   use type M.Request_Phase;
   use type M.Digest;
   use type M.Root_Phase;
   use type M.Subject_Kind;
   use type M.Actor;
   use type M.Descriptor_Phase;
   use type Q.Ordering;
   use type OJ.Head_Disposition;
   use type R.Replay_Status;
   use type S.SQL_Class;
   use type ER.Replay_State;
   use type ER.Scoped_Entry;
   use type Interfaces.Unsigned_32;
   package OV renames Worldline.Custody_V2_Root_Values;
   package AP renames Worldline.Custody_V2_Archive_Projection;
   package CP renames Worldline.Scoped_Capture_Projection;
   package RE renames Worldline.Custody_V2_Root_Evidence;
   use type RE.Join_Status;
   use type SE.Cleanup_Kind;
   use type SE.Join_Status;

   function Raw (Cell : S.SQL_Cell) return D.Raw_Cell is
     (case Cell.Kind is
        when S.SQL_Null => (S.SQL_Null, False, (1, 0)),
        when S.SQL_Integer => (S.SQL_Integer, Cell.Integer_Value.Negative,
          (Cell.Integer_Value.First, Cell.Integer_Value.Length)),
        when others => (Cell.Kind, False, (Cell.Bytes.First, Cell.Bytes.Length)));
   function Span (Cell : S.SQL_Cell) return E.Span is
     (if Cell.Kind in S.SQL_Text | S.SQL_Blob | S.SQL_Real then
        (Cell.Bytes.First, Cell.Bytes.Length) else (1, 0));
   function Text (Data : E.Bytes; Item : E.Span; Name : String) return Boolean is
     (S.Text_Is (Data, (Kind => S.SQL_Text, Bytes => (Item.First, Item.Length)), Name));
   function Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (S.Same_Span (Data, (Left.First, Left.Length), (Right.First, Right.Length)));
   function Digest_Image (Hash : M.Digest) return String is
      Hex_Digits : constant String := "0123456789abcdef";
      Image : String (1 .. 64);
   begin
      for B in Hash'Range loop
         pragma Loop_Variant (Increases => B);
         Image (1 + (B - Hash'First) * 2) := Hex_Digits (1 + Natural (Hash (B) / 16));
         Image (2 + (B - Hash'First) * 2) := Hex_Digits (1 + Natural (Hash (B) mod 16));
      end loop;
      return Image;
   end Digest_Image;
   function Significant_Length (Data : E.Bytes; Value : Q.Quantity) return E.Count
     with Global => null is
      Length : E.Count := Value.Length;
   begin
      if not Q.Span_Valid (Data, Value) or else Q.Is_Negative (Data, Value) then return 0; end if;
      while Length > 0 and then Q.Digit (Data, Value, Length - 1) = 0 loop
         pragma Loop_Variant (Decreases => Length);
         Length := Length - 1;
      end loop;
      return Length;
   end Significant_Length;
   function Successor_Length (Data : E.Bytes; Value : Q.Quantity) return E.Count
     with Global => null is
      Length : constant E.Count := Significant_Length (Data, Value);
   begin
      if not Q.Span_Valid (Data, Value) or else Q.Is_Negative (Data, Value) then return 0; end if;
      if Length = 0 then return 1; end if;
      for Offset in E.Count range 0 .. Length - 1 loop
         pragma Loop_Variant (Increases => Offset);
         if Q.Digit (Data, Value, Offset) /= 255 then return Length; end if;
      end loop;
      return (if Length = E.Count'Last then 0 else Length + 1);
   end Successor_Length;
   procedure Append_Successor
     (Arena : in out E.Bytes; Before : Q.Quantity; Needed : E.Count;
      Used : in out E.Count; Item : out E.Span; Complete : out Boolean)
     with Global => null, Always_Terminates is
      Carry : Boolean := True;
   begin
      Item := (1, 0); Complete := False;
      if not Q.Span_Valid (Arena, Before) or else Q.Is_Negative (Arena, Before)
        or else Used > Arena'Length or else Needed = 0 or else Needed > Arena'Length - Used
        or else (Before.Length > 0 and then
          (Before.First < Arena'First or else Before.First - Arena'First > Used or else
           Before.Length > Used - (Before.First - Arena'First))) then return; end if;
      Item := (Arena'First + Used, Needed);
      for Offset in E.Count range 0 .. Needed - 1 loop
         pragma Loop_Variant (Increases => Offset);
         declare B : constant Q.Byte :=
           (if Offset < Before.Length then Q.Byte (Q.Digit (Arena, Before, Offset)) else 0);
         begin
            if Carry and then B = 255 then Arena (Item.First + Offset) := 0;
            elsif Carry then Arena (Item.First + Offset) := B + 1; Carry := False;
            else Arena (Item.First + Offset) := B; end if;
         end;
      end loop;
      -- This is the genuine inherited predicate, not an imported contract or
      -- caller assertion. Mathematical proof remains in the same-source gate.
      Complete := A.L.T.Is_Successor (Arena, Before, (False, Item.First, Item.Length));
      if Complete then Used := Used + Needed; else Item := (1, 0); end if;
   end Append_Successor;
   procedure Successor_LE
     (Data : E.Bytes; Output : out E.Bytes; Needed : out E.Count;
      Complete : out Boolean) is
      Before : constant Q.Quantity := (False, Data'First, Data'Length);
      Length : constant E.Count := Successor_Length (Data, Before);
   begin
      Output := (others => 0); Needed := 0; Complete := False;
      if Length = 0 or else Length > E.Count'Last - Data'Length then return; end if;
      declare
         Arena : E.Bytes (1 .. Data'Length + Length);
         Used : E.Count := Data'Length;
         Item : E.Span;
         Produced : Boolean;
      begin
         for Offset in E.Count range 1 .. Data'Length loop
            pragma Loop_Variant (Increases => Offset);
            Arena (Offset) := Data (Data'First + (Offset - 1));
         end loop;
         Arena (Data'Length + 1 .. Arena'Last) := (others => 0);
         Append_Successor (Arena, (False, 1, Data'Length), Length, Used, Item, Produced);
         if not Produced then return; end if;
         Needed := Item.Length;
         for Offset in E.Count range 1 .. E.Count'Min (Needed, Output'Length) loop
            pragma Loop_Variant (Increases => Offset);
            Output (Output'First + (Offset - 1)) := Arena (Item.First + (Offset - 1));
         end loop;
         Complete := Needed <= Output'Length;
      end;
   end Successor_LE;
   procedure Before_Context
     (Value : I.Parsed_Input; State : out F.Fold_State;
      History : in out R.Retained_Events; Proof : out OJ.Journal_Proof;
      Result : out F.Observation)
     with Global => null, Always_Terminates,
       Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 12) is
      Native : ER.Scoped_Replay_Result;
      Owner_Matches, Contains_Unknown, Current_Matches, Preparations_Done : Boolean;
      Head : OJ.Head_Disposition;
   begin
      F.Fold (Value, State, History, Proof, Result);
      if Result.State /= F.History_Folded then return; end if;
      OC.Context_Decide (Value, Owner_Matches, Native, Contains_Unknown);
      if not Owner_Matches then Result := (F.Fold_Refused, F.Owner_Roster_Refused, 0); return; end if;
      OJ.Startup_Decide (Value, Proof, Current_Matches, Head, Preparations_Done);
      if not Current_Matches or else Head = OJ.Refused then
         Result := (F.Fold_Refused, F.Owner_Roster_Refused, 0); return;
      end if;
      if Native.State /= ER.Native_Redecided or else
        (Native.Roster_Entry = ER.Validate_Entry and then Native.Native_Status /= 1) or else
        (Native.Roster_Entry = ER.Check_Entry and then Native.Native_Status /=
          Interfaces.Unsigned_32 (ER.S.Status'Pos (ER.S.Ready))) or else
        Native.Roster_Entry = ER.Classify_Entry then
         Result := (F.Fold_Refused, F.Join_Not_Ready, 0); return;
      end if;
      if Contains_Unknown or else
        (for some Root of State.Roots (1 .. State.Root_Count) => Root.Phase = M.Unknown) then
         Result.Reason := F.Retain_Unknown;
      elsif Head /= OJ.Stable or else not Preparations_Done then
         Result.Reason := F.Recover_Retained;
      elsif (State.Logical_S0 or else State.Roots (State.Current).Phase = M.Front_Owned)
        and then State.Roots (State.Current).Owners_Open and then
        Worldline.Startup_Admission.All_Required_Admissions_Consumed (Value) then
         Result.Reason := F.Front_Startup;
      else Result.Reason := F.Recover_Retained;
      end if;
   end Before_Context;
   procedure Render_Context
     (Value : I.Parsed_Input; State : F.Fold_State;
      Root_Index, Subject_Index : E.Count; Load_Status : F.Status;
      Generation, Subgeneration : E.Span; Next_Subgeneration, Next_Epoch : C.Optional_Span;
      Output : out E.Bytes; Length : out D.Length_Result; Complete : out Boolean)
     with Global => null, Always_Terminates is
      Hex_Digits : constant String := "0123456789abcdef";
      procedure Put (Text : String) is
         Start : constant E.Count := Length.Needed;
      begin
         if not Length.Valid then return; end if;
         if Text'Length > E.Count'Last - Start then Length.Valid := False; return; end if;
         Length.Needed := Start + Text'Length;
         for N in E.Count range 1 .. E.Count'Min (Text'Length, Output'Length - E.Count'Min (Start, Output'Length)) loop
            pragma Loop_Variant (Increases => N);
            Output (Output'First + Start + (N - 1)) := Character'Pos (Text (Text'First + Natural (N - 1)));
         end loop;
      end Put;
      procedure Byte (B : Q.Byte) is
         Start : constant E.Count := Length.Needed;
      begin
         if not Length.Valid then return; end if;
         if Start = E.Count'Last then Length.Valid := False; return; end if;
         Length.Needed := Start + 1;
         if Start < Output'Length then Output (Output'First + Start) := B; end if;
      end Byte;
      procedure Number (N : E.Count) is
         Buffer : String (1 .. E.Count'Width);
         First : Positive := Buffer'Last;
         Rest : E.Count := N;
      begin
         loop
            pragma Loop_Variant (Decreases => Rest);
            Buffer (First) := Character'Val (Character'Pos ('0') + Rest mod 10);
            Rest := Rest / 10;
            exit when Rest = 0;
            First := First - 1;
         end loop;
         Put (Buffer (First .. Buffer'Last));
      end Number;
      procedure Hex (Item : E.Span) is
      begin
         if not E.C.P.Valid (Value.Arena, Item) then Length.Valid := False; return; end if;
         Put ("""");
         if Item.Length > 0 then
            for Offset in E.Count range 0 .. Item.Length - 1 loop
               pragma Loop_Variant (Increases => Offset);
               declare B : constant Q.Byte := Value.Arena (Item.First + Offset); begin
                  Byte (Character'Pos (Hex_Digits (1 + Natural (B / 16))));
                  Byte (Character'Pos (Hex_Digits (1 + Natural (B mod 16))));
               end;
            end loop;
         end if;
         Put ("""");
      end Hex;
      procedure Optional_Hex (Item : C.Optional_Span) is
      begin
         if Item.Present then Hex (Item.Value); else Put ("null"); end if;
      end Optional_Hex;
      procedure Cell (Item : S.SQL_Cell) is
         Raw_Item : constant D.Raw_Cell := Raw (Item);
      begin
         Put ("["); Number (S.SQL_Class'Pos (Item.Kind)); Put (",");
         Put ((if Raw_Item.Negative then "true" else "false")); Put (",");
         Hex (Raw_Item.Payload); Put ("]");
      end Cell;
      procedure Root_Row (Index : E.Count) is
         Row : S.Root_Columns renames State.Raw_Roots (Index).Columns;
      begin
         Put ("["); Cell (Row.Generation); Put (","); Cell (Row.Operation);
         Put (","); Cell (Row.Phase); Put (","); Cell (Row.Before_Unknown);
         Put (","); Cell (Row.Owners_Open); Put (","); Cell (Row.Abort_Kind);
         Put (","); Cell (Row.Launched); Put (","); Cell (Row.Closure_NS);
         Put (","); Cell (Row.Closure_Outer); Put (","); Cell (Row.Closure_Raw);
         Put (","); Cell (Row.Witness); Put (","); Cell (Row.Settled);
         Put (","); Cell (Row.Released_Unlaunched); Put (","); Cell (Row.Unknown_Cause);
         Put (","); Cell (Row.Reattach_Epoch); Put (","); Cell (Row.Head_Event); Put ("]");
      end Root_Row;
      procedure Subject_Row (Index : E.Count) is
         Row : S.Subject_Columns renames State.Raw_Subjects (Index).Columns;
      begin
         Put ("["); Cell (Row.Generation); Put (","); Cell (Row.Kind_Of_Subject);
         Put (","); Cell (Row.Subject); Put (","); Cell (Row.Subgeneration);
         Put (","); Cell (Row.Phase); Put (","); Cell (Row.Mode);
         Put (","); Cell (Row.Position); Put (","); Cell (Row.Carried_From);
         Put (","); Cell (Row.Head_Event); Put ("]");
      end Subject_Row;
      procedure Head (Present : Boolean; Digest : M.Digest) is
      begin
         if Present then Put ("""" & Digest_Image (Digest) & """"); else Put ("null"); end if;
      end Head;
   begin
      Output := (others => 0); Length := (True, 0); Complete := False;
      Put ("{""current_root"":");
      if State.Logical_S0 then Put ("null"); else Root_Row (State.Current); end if;
      Put (",""current_root_index"":"); Number ((if State.Logical_S0 then 0 else State.Current));
      Put (",""event_generation"":"); Hex (Generation);
      Put (",""event_subgeneration"":"); Hex (Subgeneration);
      Put (",""generation"":"); Hex ((State.Roots (Root_Index).Generation.First, State.Roots (Root_Index).Generation.Length));
      Put (",""load_status"":"); Number (F.Status'Pos (Load_Status));
      Put (",""logical_s0"":"); Put ((if State.Logical_S0 then "true" else "false"));
      Put (",""next_reattach_epoch"":"); Optional_Hex (Next_Epoch);
      Put (",""next_subgeneration"":"); Optional_Hex (Next_Subgeneration);
      Put (",""owners_open"":"); Put ((if State.Roots (Root_Index).Owners_Open then "true" else "false"));
      Put (",""predecessor_root"":"); Head (not State.Logical_S0, State.Roots (Root_Index).Head);
      Put (",""predecessor_subject"":");
      Head (Subject_Index /= 0, (if Subject_Index = 0 then Worldline.Zero_Hash else State.Subjects (Subject_Index).Head));
      Put (",""reattach_epoch"":"); Hex ((State.Roots (Root_Index).Reattach_Epoch.First, State.Roots (Root_Index).Reattach_Epoch.Length));
      Put (",""root"":"); if State.Logical_S0 then Put ("null"); else Root_Row (Root_Index); end if;
      Put (",""root_index"":"); Number ((if State.Logical_S0 then 0 else Root_Index));
      Put (",""root_phase"":""");
      declare Name : constant E.Span := Span (Value.Symbols.Root (State.Roots (Root_Index).Phase)); begin
         if Name.Length > 0 then
            for N in E.Count range 0 .. Name.Length - 1 loop
               pragma Loop_Variant (Increases => N);
               Byte (Value.Arena (Name.First + N));
            end loop;
         end if;
      end;
      Put (""",""roots"":[");
      for N in E.Count range 1 .. State.Root_Count loop
         pragma Loop_Variant (Increases => N);
         if N > 1 then Put (","); end if; Root_Row (N);
      end loop;
      Put ("],""schema"":""worldline.custody-context-view-v2"",""subject"":");
      if Subject_Index = 0 then Put ("null"); else Subject_Row (Subject_Index); end if;
      Put (",""subject_index"":"); Number (Subject_Index);
      Put (",""subjects"":[");
      for N in E.Count range 1 .. State.Subject_Count loop
         pragma Loop_Variant (Increases => N);
         if N > 1 then Put (","); end if; Subject_Row (N);
      end loop;
      Put ("]}");
      if not Length.Valid then Length.Needed := 0; end if;
      Complete := Length.Valid and then Length.Needed <= Output'Length;
   end Render_Context;

   procedure Context_View (Data : E.Bytes; Output : out E.Bytes;
                           Result : out Context_Observation) is
      Envelope : constant E.Span := (Data'First, Data'Length);
      Before : constant E.Span := T.Field (Data, Envelope, "before");
      Candidate : constant E.Span := T.Field (Data, Envelope, "candidate");
      Root_Generation : constant E.Span := T.Field (Data, Candidate, "root_generation");
      Purpose : constant E.Span := T.Field (Data, Envelope, "query_purpose");
      Read_Only_Query : constant Boolean :=
        T.Text_Is (Data, Purpose, "OUTPUT") or else
        T.Text_Is (Data, Purpose, "CLEANUP") or else
        T.Text_Is (Data, Purpose, "SERVING") or else
        T.Text_Is (Data, Purpose, "CLOSED_OWNER");
      Size : constant I.Sizes := I.Counts (Data, Before);
      Arena_Size : E.Count := Size.Arena;
      Good : Boolean := True;
      Gen_Max, Subgen_Max, Epoch_Max : E.Count := 1;
      procedure Add (N : E.Count) is
      begin
         if N > E.Count'Last - Arena_Size then Good := False; else Arena_Size := Arena_Size + N; end if;
      end Add;
   begin
      Output := (others => 0); Result := (F.Fold_Refused, F.Input_Malformed, 0, 0, 0);
      if Size.Status /= I.Parsed or else Size.Events = E.Count'Last or else
        not T.Text_Is (Data, T.Field (Data, Envelope, "schema"), "worldline.custody-mutation-v2") or else
        not V.Type_Is (Data, Candidate, "dict") or else
        (T.Valid (Data, Purpose) and then not Read_Only_Query and then
           not T.Text_Is (Data, Purpose, "MUTATION"))
      then return; end if;
      for N in E.Count range 1 .. Size.Roots loop
         pragma Loop_Variant (Increases => N);
         Gen_Max := E.Count'Max (Gen_Max, I.SQL_Byte_Count (Data,
           V.Element (Data, V.Element (Data, T.Field (Data, Before, "roots"), N - 1), 0)));
         Epoch_Max := E.Count'Max (Epoch_Max, I.SQL_Byte_Count (Data,
           V.Element (Data, V.Element (Data, T.Field (Data, Before, "roots"), N - 1), 14)));
      end loop;
      for N in E.Count range 1 .. Size.Subjects loop
         pragma Loop_Variant (Increases => N);
         Subgen_Max := E.Count'Max (Subgen_Max, I.SQL_Byte_Count (Data,
           V.Element (Data, V.Element (Data, T.Field (Data, Before, "subjects"), N - 1), 3)));
      end loop;
      if Gen_Max = E.Count'Last or else Subgen_Max = E.Count'Last or else Epoch_Max = E.Count'Last then return; end if;
      Add (Gen_Max + 1); Add (Subgen_Max + 1); Add (Subgen_Max + 1); Add (Epoch_Max + 1);
      Add (I.SQL_Byte_Count (Data, T.Field (Data, Candidate, "operation")));
      Add (I.SQL_Byte_Count (Data, T.Field (Data, Candidate, "kind")));
      Add (I.SQL_Byte_Count (Data, T.Field (Data, Candidate, "actor")));
      Add (I.SQL_Byte_Count (Data, T.Field (Data, Candidate, "subject_kind")));
      Add (I.SQL_Byte_Count (Data, T.Field (Data, Candidate, "subject")));
      Add (I.SQL_Byte_Count (Data, Root_Generation));
      if not Good then return; end if;
      declare
         Value : I.Parsed_Input (Arena_Size, Size.Events + 1, Size.Heads,
           Size.Roots, Size.Subjects, Size.Alternatives, Size.Blobs);
         State : F.Fold_State (E.Count'Max (1, Size.Roots), Size.Subjects);
         Blank : constant M.Event_Record :=
           (Kind => M.Prepared_Event, Generation | Subgeneration => (False, 1, 0),
            Operation | Subject => (Present => False), Kind_Of_Subject => M.Root,
            Appending_Actor => M.Front, Record_Digest | Event_Id => Worldline.Zero_Hash);
         History : R.Retained_Events (1 .. Size.Events) :=
           (others => (Event => Blank, Previous | Mac => Worldline.Zero_Hash,
             Record_Bytes | Base_Archive => (Present => False)));
         Folded : F.Observation;
         Proof : OJ.Journal_Proof;
         Used : E.Count;
         Selector : M.Event_Record := Blank;
         Operation, Kind_Name, Actor_Name, Subject_Kind, Subject : E.Span := (1, 0);
         RI, SI : E.Count := 0;
         Admission : E.Count := 0;
         Admission_Required, Admission_Found : Boolean := False;
         Generation, Subgeneration : E.Span := (1, 0);
         Next_Subgeneration, Next_Epoch : C.Optional_Span := (Present => False);
         Kind_Found, Actor_Found, Subject_Found, Produced, Complete : Boolean := False;
         Length : D.Length_Result;
         procedure Refuse (Reason : F.Status) is
         begin Result := (F.Fold_Refused, Reason, 0, 0, 0); end Refuse;
         procedure Text_Field (Name : String; Item : out E.Span) is
            Cell : S.SQL_Cell;
            Status : I.Decode_Status;
         begin
            I.Append_SQL_Cell (Value.Arena, T.Field (Value.Arena,
              (Candidate.First - Data'First + 1, Candidate.Length), Name), Used, Cell, Status);
            if Status /= I.Parsed or else Cell.Kind /= S.SQL_Text then Good := False; end if;
            Item := Span (Cell);
         end Text_Field;
         function Returned (Generation : Q.Quantity) return Boolean is
           (for some Event of History => Event.Event.Kind = M.Custody_Returned_Event and then
              Q.Compare (Value.Arena, Event.Event.Generation, Generation) = Q.Equal);
         function Root_Of (Index : E.Count) return E.Count is
         begin
            for N in E.Count range 1 .. State.Root_Count loop
               pragma Loop_Variant (Increases => N);
               if Q.Compare (Value.Arena, State.Roots (N).Generation, State.Subjects (Index).Generation) = Q.Equal then return N; end if;
            end loop;
            return 0;
         end Root_Of;
         function Own_Operation (Index : E.Count) return Boolean is
            Current : E.Count := Index;
            Remaining : E.Count := State.Subject_Count;
         begin
            while Remaining > 0 loop
               pragma Loop_Variant (Decreases => Remaining);
               Remaining := Remaining - 1;
               for N in reverse History'Range loop
                  pragma Loop_Variant (Decreases => N);
                  if History (N).Event.Kind_Of_Subject = Selector.Kind_Of_Subject and then
                    A.L.Optional_Same (Value.Arena, History (N).Event.Subject, Selector.Subject) and then
                    Q.Compare (Value.Arena, History (N).Event.Generation, State.Subjects (Current).Generation) = Q.Equal then
                     return A.L.Optional_Same (Value.Arena, History (N).Event.Operation, Selector.Operation);
                  end if;
               end loop;
               if not State.Subjects (Current).Carried_From.Present then return False; end if;
               declare Earlier : E.Count := 0; begin
                  for N in E.Count range 1 .. State.Subject_Count loop
                     pragma Loop_Variant (Increases => N);
                     if State.Subjects (N).Kind = Selector.Kind_Of_Subject and then
                       A.L.Optional_Same (Value.Arena, State.Subjects (N).Subject, Selector.Subject) and then
                       Q.Compare (Value.Arena, State.Subjects (N).Generation, State.Subjects (Current).Carried_From.Value) = Q.Equal then Earlier := N; end if;
                  end loop;
                  if Earlier = 0 then return False; end if;
                  Current := Earlier;
               end;
            end loop;
            return False;
         end Own_Operation;
         procedure Find_Admission is
            Record_Node : constant E.Span := T.Field (Value.Arena,
              (Candidate.First - Data'First + 1, Candidate.Length), "record");
            Original_Node : constant E.Span := T.Field (Value.Arena, Record_Node, "original");
         begin
            if not T.Text_Is (Data, Purpose, "OUTPUT") or else
               not V.Valid_Bytes (Value.Arena, Original_Node) then return; end if;
            declare
               Raw : constant E.Bytes := V.Bytes_Value (Value.Arena, Original_Node);
               Item : constant E.Span := OV.Record_Field (Raw, (Raw'First, Raw'Length), "admission_head");
            begin
               if not OV.Valid_Text (Raw, Item) then return; end if;
               declare Id : constant E.Bytes := OV.Text_Value (Raw, Item); begin
                  if Id'Length = 0 then return; end if;
                  Admission_Required := True;
                  for N in History'Range loop
                     pragma Loop_Variant (Increases => N);
                     if Value.Events (N).Event_Id.Length = Id'Length and then
                       (for all J in E.Count range 1 .. Id'Length =>
                         Id (Id'First + J - 1) = Value.Arena (Value.Events (N).Event_Id.First + J - 1)) and then
                       History (N).Event.Kind in M.Request_Queued_Event | M.Request_Intake_Event and then
                       History (N).Event.Kind_Of_Subject = M.Request and then
                       A.L.Optional_Same (Value.Arena, History (N).Event.Subject, Selector.Subject) and then
                       A.L.Optional_Same (Value.Arena, History (N).Event.Operation, Selector.Operation)
                     then
                        if Admission_Found then Admission_Found := False; return; end if;
                        Admission := N; Admission_Found := True;
                     end if;
                  end loop;
               end;
            end;
         end Find_Admission;
      begin
         I.Decode_Grown (Data, Before, Value, Used);
         if Value.Status /= I.Parsed then return; end if;
         Before_Context (Value, State, History, Proof, Folded);
         if Folded.State /= F.History_Folded then
            Result := (F.Fold_Refused, Folded.Reason, Folded.Position, 0, 0); return;
         end if;
         Text_Field ("operation", Operation); Text_Field ("kind", Kind_Name);
         Text_Field ("actor", Actor_Name); Text_Field ("subject_kind", Subject_Kind); Text_Field ("subject", Subject);
         if not Good then return; end if;
         Selector.Operation := (True, (Operation.First, Operation.Length));
         Selector.Subject := (True, (Subject.First, Subject.Length));
         for Kind in M.Event_Kind loop
            pragma Loop_Variant (Increases => Kind);
            if Text (Value.Arena, Kind_Name, F.D.Kind_Name (Kind)) then Selector.Kind := Kind; Kind_Found := True; end if;
         end loop;
         for Actor in M.Actor loop
            pragma Loop_Variant (Increases => Actor);
            if Text (Value.Arena, Actor_Name, (case Actor is when M.Front => "FRONT", when M.Worker => "WORKER", when M.Collector => "COLLECTOR", when M.Reconciler => "RECONCILER")) then
               Selector.Appending_Actor := Actor; Actor_Found := True;
            end if;
         end loop;
         for Kind in M.Subject_Kind loop
            pragma Loop_Variant (Increases => Kind);
            if Text (Value.Arena, Subject_Kind, (case Kind is when M.Root => "ROOT", when M.Request => "REQUEST", when M.Descriptor => "DESCRIPTOR")) then
               Selector.Kind_Of_Subject := Kind; Subject_Found := True;
            end if;
         end loop;
         if not Kind_Found or else not Actor_Found or else not Subject_Found then return; end if;
         Find_Admission;
         if Admission_Required and then not Admission_Found then Refuse (F.Subject_Unknown); return; end if;
         RI := State.Current;
         if T.Valid (Data, Root_Generation) then
            -- Factual saved attempted-event magnitude, never a Python-selected
            -- phase/owner/op/generation default. Only these original root
            -- uncertainty families use a subject's independent OwnOp.
            if Selector.Kind_Of_Subject /= M.Root or else
               Selector.Kind not in M.Unknown_Event | M.Reconciled_Event then return; end if;
            declare
               Cell : S.SQL_Cell;
               Status : I.Decode_Status;
            begin
               I.Append_SQL_Cell (Value.Arena,
                 (Root_Generation.First - Data'First + 1, Root_Generation.Length), Used, Cell, Status);
               if Status /= I.Parsed or else Cell.Kind /= S.SQL_Blob then return; end if;
               RI := 0;
               for N in E.Count range 1 .. State.Root_Count loop
                  pragma Loop_Variant (Increases => N);
                  if Same (Value.Arena, Span (Cell),
                    (State.Roots (N).Generation.First, State.Roots (N).Generation.Length)) then
                     if RI /= 0 then Refuse (F.Ambiguous_History); return; end if;
                     RI := N;
                  end if;
               end loop;
               if RI = 0 then Refuse (F.Wrong_Generation); return; end if;
            end;
         end if;
         if Selector.Kind_Of_Subject = M.Root then
            if not T.Valid (Data, Root_Generation) and then P.Is_Physical (Selector.Kind) and then not State.Logical_S0 and then
              not A.L.Optional_Same (Value.Arena, State.Roots (RI).Operation, Selector.Operation) then
               RI := 0;
               for N in E.Count range 1 .. State.Root_Count loop
                  pragma Loop_Variant (Increases => N);
                  if (Read_Only_Query or else State.Roots (N).Phase = M.Ended) and then
                    A.L.Optional_Same (Value.Arena, State.Roots (N).Operation, Selector.Operation) then
                     if RI /= 0 then Refuse (F.Ambiguous_History); return; end if;
                     RI := N;
                  end if;
               end loop;
               if RI = 0 then Refuse (F.Wrong_Generation); return; end if;
            end if;
         else
            for N in E.Count range 1 .. State.Subject_Count loop
               pragma Loop_Variant (Increases => N);
               if State.Subjects (N).Kind = Selector.Kind_Of_Subject and then
                 A.L.Optional_Same (Value.Arena, State.Subjects (N).Subject, Selector.Subject) and then Own_Operation (N) and then
                 (not Admission_Required or else
                    (Q.Compare (Value.Arena, State.Subjects (N).Generation, History (Admission).Event.Generation) = Q.Equal and then
                     Q.Compare (Value.Arena, State.Subjects (N).Subgeneration, History (Admission).Event.Subgeneration) = Q.Equal)) then
                  declare
                     Root : constant E.Count := Root_Of (N);
                     Before_Subject : constant P.Optional_Subject := (True, State.Subjects (N));
                     From_Allowed : constant Boolean :=
                       Read_Only_Query or else
                       (if Selector.Kind_Of_Subject = M.Request then P.Request_From_Clause (Before_Subject, Selector.Kind) and then
                          P.Request_Fixed_Actor_Clause (Before_Subject, Selector.Kind, Selector.Appending_Actor)
                        else P.Descriptor_From_Clause (Before_Subject, Selector.Kind) and then
                          P.Descriptor_Fixed_Actor_Clause (Selector.Kind, Selector.Appending_Actor));
                  begin
                     if Root /= 0 and then From_Allowed and then
                       (Read_Only_Query or else Root = State.Current or else
                        (P.Is_Physical (Selector.Kind) and then State.Roots (Root).Phase = M.Ended) or else
                        (Selector.Kind in M.Request_Lost_Event | M.Request_Abandon_Event | M.Drain_Reclaimed_Event and then
                         not Returned (State.Subjects (N).Generation))) then
                        if Read_Only_Query and then not Admission_Required and then Root = State.Current then
                           SI := N; RI := Root;
                        elsif Read_Only_Query and then not Admission_Required and then SI /= 0 and then RI = State.Current then
                           null;
                        else
                           if SI /= 0 then Refuse (F.Ambiguous_History); return; end if;
                           SI := N; RI := Root;
                        end if;
                     end if;
                  end;
               end if;
            end loop;
            if SI = 0 and then Selector.Kind not in M.Request_Queued_Event | M.Drain_Stop_Intent_Event then
               Refuse (F.Subject_Unknown); return;
            end if;
         end if;
         Generation := (State.Roots (RI).Generation.First, State.Roots (RI).Generation.Length);
         Subgeneration := Span (Value.Symbols.Zero_Magnitude);
         if Selector.Kind = M.Front_Owned_Event then
            RI := State.Current;
            Append_Successor (Value.Arena, State.Roots (RI).Generation,
              Successor_Length (Value.Arena, State.Roots (RI).Generation), Used, Generation, Produced);
            if not Produced then return; end if;
         end if;
         if SI /= 0 then
            if Selector.Kind = M.Request_Transfer_Intent_Event and then State.Subjects (SI).Request = M.Abandoned then
               Append_Successor (Value.Arena, State.Subjects (SI).Subgeneration,
                 Successor_Length (Value.Arena, State.Subjects (SI).Subgeneration), Used, Subgeneration, Produced);
               if not Produced then return; end if;
            elsif Selector.Kind /= M.Request_Transfer_Intent_Event then
               Subgeneration := (State.Subjects (SI).Subgeneration.First, State.Subjects (SI).Subgeneration.Length);
            end if;
         end if;
         if Selector.Kind = M.Worker_Reattached_Event then
            declare Epoch : E.Span; begin
               Append_Successor (Value.Arena, State.Roots (RI).Reattach_Epoch,
                 Successor_Length (Value.Arena, State.Roots (RI).Reattach_Epoch), Used, Epoch, Produced);
               if not Produced then return; end if;
               Next_Epoch := (True, Epoch);
            end;
         elsif Selector.Kind = M.Drain_Abandon_Event and then SI /= 0 then
            declare Next : E.Span; begin
               Append_Successor (Value.Arena, State.Subjects (SI).Subgeneration,
                 Successor_Length (Value.Arena, State.Subjects (SI).Subgeneration), Used, Next, Produced);
               if not Produced then return; end if;
               Next_Subgeneration := (True, Next);
            end;
         end if;
         Value.Arena_Used := Used;
         Render_Context (Value, State, RI, SI, Folded.Reason, Generation, Subgeneration,
           Next_Subgeneration, Next_Epoch, Output, Length, Complete);
         if not Length.Valid or else Length.Needed = 0 then return; end if;
         Result := (F.History_Folded, Folded.Reason, 0, Length.Needed,
           (if Complete then Length.Needed else 0));
      end;
   end Context_View;

   procedure Retry_Reference
     (Data : E.Bytes; Candidate, Retry : E.Span; Value : I.Parsed_Input;
      State : F.Fold_State; History : R.Retained_Events; Root_Index : E.Count;
      Matches : out Boolean; Replay_Position : out E.Count)
   is
   begin
      Matches := False; Replay_Position := 0;
      if Root_Index not in State.Roots'Range then return; end if;
      for Index in History'Range loop
         pragma Loop_Variant (Increases => Index);
         if History (Index).Event.Kind = M.Reconciled_Event and then
           History (Index).Event.Event_Id = State.Roots (Root_Index).Head and then
           Value.Extras (Index).Root_Evidence_Encoding = I.Operation_Original then
            declare
               Raw : E.Bytes renames Value.Arena;
               Profile : constant E.Span := Value.Extras (Index).Root_Evidence_Payload;
               Captured : constant E.Span := OV.Record_Field (Raw, Profile, "append_uncertainty");
               Route : constant E.Span := OV.Record_Field (Raw,
                 OV.Record_Field (Raw, Profile, "reconciled"), "route");
               Saved : constant E.Span := OV.Record_Field (Raw, Captured, "candidate");
               Record_Node : constant E.Span := T.Field (Data, Candidate, "record");
               function Selector_Matches (Name : String) return Boolean is
                 (AP.Scoped_Archive_Operation_Matches
                   (Data, Raw, T.Field (Data, Candidate, Name),
                    OV.Record_Field (Raw, Captured, Name)));
            begin
               if not AP.Scoped_Archive_Operation_Matches
                 (Data, Raw, Retry, Captured, AP.Original_Image) or else
                 not Selector_Matches ("operation") or else not Selector_Matches ("kind") or else
                 not Selector_Matches ("subject_kind") or else not Selector_Matches ("subject") or else
                 not Selector_Matches ("actor") then return; end if;
               if OV.Text_Is (Raw, Route, "append-persisted") then
                  declare
                     Attempted : constant E.Span := OV.Record_Field (Raw, Captured, "attempted_event");
                  begin
                     for Earlier in History'First .. Index - 1 loop
                        pragma Loop_Variant (Increases => Earlier);
                        if OV.Text_Matches (Raw, OV.Record_Field (Raw, Attempted, "event_id"),
                           Value.Events (Earlier).Event_Id) and then
                           AP.Scoped_Archive_Operation_Matches
                             (Raw, Raw, Value.Events (Earlier).Record_Archive, Saved) then
                           Matches := True; Replay_Position := Earlier; return;
                        end if;
                     end loop;
                  end;
                  return;
               end if;
               if not OV.Text_Is (Raw, Route, "append-retry") or else
                  not AP.Scoped_Archive_Operation_Matches
                    (Data, Raw, T.Field (Data, Record_Node, "original"),
                     OV.Record_Field (Raw, Saved, "original")) or else
                  not AP.Scoped_Archive_Operation_Matches
                    (Data, Raw, T.Field (Data, T.Field (Data, Record_Node, "x5"), "actor_identity"),
                     OV.Record_Field (Raw, OV.Record_Field (Raw, Saved, "x5"), "actor_identity"))
               then return; end if;
               -- Full authenticated fold already redecided this reconciliation;
               -- fresh candidate still reaches original current Legal/Next.
               Matches := True; return;
            end;
         end if;
      end loop;
   end Retry_Reference;
   type Decision_Mode is (Mutation_Delta, Retry_Delta, Cleanup_Route, Serving_Route, Closed_Route, Output_Route);
   procedure Decide_Staged
     (Data : E.Bytes; Output : out E.Bytes; Result : out Observation;
      Mode : Decision_Mode; Cleanup : out Cleanup_Observation;
      Serving : out SE.Join_Status; Emitter : out OS.Output_Observation;
      Query : OS.Query_Kind := OS.Allocate)
      with Subprogram_Variant => (Decreases => Data'Length, Decreases => 13),
        Post => Emitter.Written <= Output'Length and then
          (if Emitter.Kind = OS.Refused then Emitter.Needed = 0 and then Emitter.Written = 0) and then
          (if Emitter.Kind /= OS.Refused then Emitter.Needed > 0 and then
             Emitter.Written = (if Emitter.Needed <= Output'Length then Emitter.Needed else 0))
   is
      Envelope : constant E.Span := (Data'First, Data'Length);
      Before : constant E.Span := T.Field (Data, Envelope, "before");
      Candidate : constant E.Span := T.Field (Data, Envelope, "candidate");
      Record_Node : constant E.Span := T.Field (Data, Candidate, "record");
      Size : constant I.Sizes := I.Counts (Data, Before);
      Arena_Size : E.Count := Size.Arena;
      Good : Boolean := True;
      Generation_Max, Subgeneration_Max, Epoch_Max : E.Count := 1;
      Root_Capacity : E.Count := E.Count'Max (1, Size.Roots);
      Subject_Capacity : E.Count := Size.Subjects;
      function Is_Kind (Name : String) return Boolean is
        (V.S.Text_Is (Data, T.Field (Data, Candidate, "kind"), Name));
      procedure Add (N : E.Count) is
      begin
         if N > E.Count'Last - Arena_Size then Good := False;
         else Arena_Size := Arena_Size + N; end if;
      end Add;
      function Field_Size (Name : String) return E.Count is
        (I.SQL_Byte_Count (Data, T.Field (Data, Candidate, Name)));
   begin
      Output := (others => 0);
      Result := (Refused, F.Input_Malformed, 0, 0, 0);
      Cleanup := (others => <>);
      Serving := SE.Evidence_Refused;
      Emitter := (others => <>);
      if Size.Status /= I.Parsed or else not V.Type_Is (Data, Candidate, "dict")
        or else not V.S.Text_Is (Data, T.Field (Data, Envelope, "schema"),
          "worldline.custody-mutation-v2") or else not T.Valid (Data, Record_Node)
        or else not V.Type_Is (Data, Record_Node, "dict") then return; end if;
      if Size.Events = E.Count'Last or else Size.Alternatives > E.Count'Last / 7
        or else Size.Blobs > E.Count'Last / 3 then return; end if;
      -- Storage geometry only. These decoded names never authorize a step.
      if Is_Kind ("FRONT_OWNED") then
         if Size.Roots = E.Count'Last or else Size.Subjects > E.Count'Last / 2 then return; end if;
         Root_Capacity := Size.Roots + 1; Subject_Capacity := Size.Subjects * 2;
      elsif Is_Kind ("REQUEST_QUEUED") or else Is_Kind ("DRAIN_STOP_INTENT") then
         if Subject_Capacity = E.Count'Last then return; end if;
         Subject_Capacity := Subject_Capacity + 1;
      end if;
      if Root_Capacity > E.Count'Last / 16 or else
        Subject_Capacity > E.Count'Last / 9 then return; end if;
      -- Extents come from the retained magnitudes, not their numeric values.
      -- An extra digit covers carry; this is not a public integer/count cap.
      for N in E.Count range 1 .. Size.Roots loop
         pragma Loop_Variant (Increases => N);
         Generation_Max := E.Count'Max (Generation_Max, I.SQL_Byte_Count (Data,
           V.Element (Data, V.Element (Data, T.Field (Data, Before, "roots"), N - 1), 0)));
         Epoch_Max := E.Count'Max (Epoch_Max, I.SQL_Byte_Count (Data,
           V.Element (Data, V.Element (Data, T.Field (Data, Before, "roots"), N - 1), 14)));
      end loop;
      for N in E.Count range 1 .. Size.Subjects loop
         pragma Loop_Variant (Increases => N);
         Subgeneration_Max := E.Count'Max (Subgeneration_Max, I.SQL_Byte_Count (Data,
           V.Element (Data, V.Element (Data, T.Field (Data, Before, "subjects"), N - 1), 3)));
      end loop;
      if Generation_Max = E.Count'Last or else Subgeneration_Max = E.Count'Last
        or else Epoch_Max = E.Count'Last then return; end if;
      Generation_Max := Generation_Max + 1; Subgeneration_Max := Subgeneration_Max + 1;
      Epoch_Max := Epoch_Max + 1;
      Add (Field_Size ("operation")); Add (Field_Size ("kind")); Add (Field_Size ("actor"));
      Add (Field_Size ("subject_kind")); Add (Field_Size ("subject"));
      Add (I.Event_Extra_Byte_Count (Data, Record_Node));
      if Is_Kind ("FRONT_OWNED") then Add (Generation_Max); end if;
      if Is_Kind ("REQUEST_TRANSFER_INTENT") then Add (Subgeneration_Max); end if;
      if Is_Kind ("WORKER_REATTACHED") then Add (Epoch_Max); end if;
      if Is_Kind ("DRAIN_ABANDON") then Add (Subgeneration_Max); end if;
      -- Three complete digest texts, predecessor digest text, EVENT and the
      -- alternative name. All later archive lengths use the original encoder.
      Add (256); Add (12);
      declare
         Dummy_Row : constant C.Event_Row :=
           (Event_Id | Previous | Mac => (Data'First, 64),
            Generation => (Data'First, Generation_Max),
            Subgeneration => (Data'First, Subgeneration_Max),
            Operation => (Data'First, Field_Size ("operation")),
            Kind => (Data'First, Field_Size ("kind")),
            Actor => (Data'First, Field_Size ("actor")),
            Subject_Kind => (Data'First, Field_Size ("subject_kind")),
            Subject => (Data'First, Field_Size ("subject")),
            Record_Archive => Record_Node, Base_Archive => (1, 0));
         Base_Size : constant D.Length_Result := D.Base_Length (Data, Dummy_Row);
         Head_Size : constant D.Length_Result := D.Head_Length (Data, (Data'First, 64),
           (Data'First, I.SQL_Byte_Count (Data, T.Field (Data, Before, "genesis_row"))));
      begin
         if not Base_Size.Valid or else not Head_Size.Valid then return; end if;
         Add (Base_Size.Needed); Add (Head_Size.Needed);
      end;
      if not Good then return; end if;
      declare
         Value : I.Parsed_Input (Arena_Size, Size.Events + 1, Size.Heads,
           Size.Roots, Size.Subjects, Size.Alternatives, Size.Blobs);
         State : F.Fold_State (Root_Capacity, Subject_Capacity);
         Folded : F.Observation;
         Proof : OJ.Journal_Proof;
         Used : E.Count;
         New_Index : constant E.Count := Size.Events + 1;
         Row : C.Event_Row := (others => (1, 0));
         Cell : S.SQL_Cell;
         Decode_Result : I.Decode_Status;
         Extra : I.Event_Extra;
         Complete, Applied : Boolean;
         Length : D.Length_Result;
         Head_Message, Head_Mac, Head_Kind, Alternative_Name : E.Span := (1, 0);
         Kind : M.Event_Kind := M.Prepared_Event;
         Kind_Found : Boolean := False;
         Root_Index, Subject_Index : E.Count := 0;
         Dummy : constant M.Event_Record :=
           (Kind => M.Prepared_Event, Generation | Subgeneration => (False, 1, 0),
            Operation | Subject => (Present => False), Kind_Of_Subject => M.Root,
            Appending_Actor => M.Front, Record_Digest | Event_Id => Worldline.Zero_Hash);
         History : R.Retained_Events (1 .. Size.Events) :=
           (others => (Event => Dummy, Previous | Mac => Worldline.Zero_Hash,
             Record_Bytes | Base_Archive => (Present => False)));
         procedure Fail (Why : F.Status; Position : E.Count := 0) is
         begin Result := (Refused, Why, Position, 0, 0); end Fail;
         procedure Put_Text (Name : String; Item : out E.Span) is
            Node : constant E.Span := T.Field (Value.Arena,
              (Candidate.First - Data'First + 1, Candidate.Length), Name);
         begin
            I.Append_SQL_Cell (Value.Arena, Node, Used, Cell, Decode_Result);
            if Decode_Result /= I.Parsed or else Cell.Kind /= S.SQL_Text then Good := False; end if;
            Item := Span (Cell);
         end Put_Text;
         procedure Intern (Name : String; Item : out E.Span) is
         begin
            if Name'Length > Value.Arena_Count - Used then Good := False; Item := (1, 0); return; end if;
            Item := (Used + 1, Name'Length);
            for N in Name'Range loop
               pragma Loop_Variant (Increases => N);
               Value.Arena (Item.First + E.Count (N - Name'First)) := Character'Pos (Name (N));
            end loop;
            Used := Used + Name'Length;
         end Intern;
         procedure Digest_Text (Hash : M.Digest; Item : out E.Span) is
            Hex_Digits : constant String := "0123456789abcdef";
         begin
            Item := (1, 0);
            if Value.Arena_Count - Used < 64 then Good := False; return; end if;
            Item := (Used + 1, 64);
            for B in Hash'Range loop
               pragma Loop_Variant (Increases => B);
               Value.Arena (Item.First + E.Count (B - Hash'First) * 2) :=
                 Character'Pos (Hex_Digits (1 + Natural (Hash (B) / 16)));
               Value.Arena (Item.First + E.Count (B - Hash'First) * 2 + 1) :=
                 Character'Pos (Hex_Digits (1 + Natural (Hash (B) mod 16)));
            end loop;
            Used := Used + 64;
         end Digest_Text;
         procedure Successor (Before_Value : Q.Quantity; Item : out E.Span) is
            Produced : Boolean;
         begin
            Append_Successor (Value.Arena, Before_Value,
              Successor_Length (Value.Arena, Before_Value), Used, Item, Produced);
            Good := Good and then Produced;
         end Successor;
      begin
         I.Decode_Grown (Data, Before, Value, Used);
         if Value.Status /= I.Parsed then return; end if;
         Before_Context (Value, State, History, Proof, Folded);
         if Folded.State /= F.History_Folded then Fail (Folded.Reason, Folded.Position); return; end if;
         Put_Text ("operation", Row.Operation); Put_Text ("kind", Row.Kind);
         Put_Text ("actor", Row.Actor); Put_Text ("subject_kind", Row.Subject_Kind);
         Put_Text ("subject", Row.Subject);
         Row.Record_Archive := (Record_Node.First - Data'First + 1, Record_Node.Length);
         I.Append_Event_Extras (Value.Arena, Row.Record_Archive, Used, Extra, Decode_Result);
         if not Good or else Decode_Result /= I.Parsed then return; end if;
         for K in M.Event_Kind loop
            pragma Loop_Variant (Increases => K);
            if Text (Value.Arena, Row.Kind, F.D.Kind_Name (K)) then Kind := K; Kind_Found := True; end if;
         end loop;
         if not Kind_Found then return; end if;
         -- F.6 retry precedes CAS and fresh-event derivation. Match the entire
         -- immutable storedrecord, never original-only payload or refreshed x5.
         if Mode in Mutation_Delta | Retry_Delta then
         declare
            Found : E.Count := 0;
            Hash : constant M.Digest := C.G.Hash (Value.Arena, Row.Record_Archive);
         begin
            for N in History'Range loop
               pragma Loop_Variant (Increases => N);
               if History (N).Event.Record_Digest = Hash and then
                 Same (Value.Arena, Row.Record_Archive, Value.Events (N).Record_Archive) and then
                 Same (Value.Arena, Row.Operation, Value.Events (N).Operation) and then
                 Same (Value.Arena, Row.Kind, Value.Events (N).Kind) and then
                 Same (Value.Arena, Row.Actor, Value.Events (N).Actor) and then
                 Same (Value.Arena, Row.Subject_Kind, Value.Events (N).Subject_Kind) and then
                 Same (Value.Arena, Row.Subject, Value.Events (N).Subject) then
                  if Found /= 0 then Fail (F.Ambiguous_History); return; end if;
                  declare Replay : constant R.Replay_Result := R.Resolve
                    (Value.Arena, History, R.Key (History (N).Event)); begin
                     if Replay.Status /= R.Found or else Replay.Position /= N then
                        Fail (F.Ambiguous_History); return;
                     end if;
                  end;
                  Found := N;
               end if;
            end loop;
            if Found /= 0 then Result := (Replay_Unchanged, F.Recover_Retained, Found, 0, 0); return; end if;
         end;
         end if;
         -- The authenticated root predecessor identifies a historical root for
         -- original cleanup/lost/reclaim domains; absent/stale refs reach Legal.
         Root_Index := State.Current;
         declare
            X5 : constant E.Span := V.Record_Field (Value.Arena, Row.Record_Archive, "x5");
            Predecessor : constant E.Span := V.Record_Field (Value.Arena, X5, "predecessor_root");
         begin
            for N in E.Count range 1 .. State.Root_Count loop
               pragma Loop_Variant (Increases => N);
               if C.S.Text_Is (Value.Arena, Predecessor,
                 Digest_Image (State.Roots (N).Head)) then Root_Index := N; end if;
            end loop;
         end;
         if Mode = Retry_Delta then
            declare
               Matches : Boolean;
               Replay_Position : E.Count;
            begin
               Retry_Reference (Data, Candidate, T.Field (Data, Envelope, "retry_attempt"),
                                Value, State, History, Root_Index, Matches, Replay_Position);
               if not Matches then Fail (F.Evidence_Missing); return; end if;
               if Replay_Position /= 0 then
                  Result := (Replay_Unchanged, F.Recover_Retained, Replay_Position, 0, 0); return;
               end if;
            end;
         end if;
         if Kind = M.Front_Owned_Event then
            Root_Index := State.Current; Successor (State.Roots (Root_Index).Generation, Row.Generation);
         else Row.Generation := (State.Roots (Root_Index).Generation.First, State.Roots (Root_Index).Generation.Length); end if;
         Row.Subgeneration := Span (Value.Symbols.Zero_Magnitude);
         for N in E.Count range 1 .. State.Subject_Count loop
            pragma Loop_Variant (Increases => N);
            if Same (Value.Arena, Row.Generation, (State.Subjects (N).Generation.First, State.Subjects (N).Generation.Length))
              and then State.Raw_Subjects (N).Present and then
              Same (Value.Arena, Row.Subject_Kind, Span (State.Raw_Subjects (N).Columns.Kind_Of_Subject)) and then
              Same (Value.Arena, Row.Subject, Span (State.Raw_Subjects (N).Columns.Subject)) then Subject_Index := N; end if;
         end loop;
         if Subject_Index /= 0 then
            if Kind = M.Request_Transfer_Intent_Event and then State.Subjects (Subject_Index).Request = M.Abandoned then
               Successor (State.Subjects (Subject_Index).Subgeneration, Row.Subgeneration);
            elsif Kind /= M.Request_Transfer_Intent_Event then
               Row.Subgeneration := (State.Subjects (Subject_Index).Subgeneration.First,
                 State.Subjects (Subject_Index).Subgeneration.Length);
            end if;
         end if;
         if Kind = M.Worker_Reattached_Event then
            declare Epoch : E.Span; begin
               Successor (State.Roots (Root_Index).Reattach_Epoch, Epoch);
               if Extra.Reattach_Epoch.Kind /= S.SQL_Blob or else
                 not Same (Value.Arena, Epoch, Span (Extra.Reattach_Epoch)) then
                  Fail (F.Join_Not_Ready); return;
               end if;
               Extra.Reattach_Epoch := (Kind => S.SQL_Blob, Bytes => (Epoch.First, Epoch.Length));
            end;
         elsif Kind = M.Drain_Abandon_Event and then Subject_Index /= 0 then
            declare Subgeneration : E.Span; begin
               Successor (State.Subjects (Subject_Index).Subgeneration, Subgeneration);
               if Extra.Next_Subgeneration.Kind /= S.SQL_Blob or else
                 not Same (Value.Arena, Subgeneration, Span (Extra.Next_Subgeneration)) then
                  Fail (F.Join_Not_Ready); return;
               end if;
               Extra.Next_Subgeneration := (Kind => S.SQL_Blob,
                 Bytes => (Subgeneration.First, Subgeneration.Length));
            end;
         end if;
         if Size.Events = 0 then Digest_Text (C.G.Hash (Value.Arena, Value.Genesis_Row), Row.Previous);
         else Row.Previous := Value.Events (Size.Events).Event_Id; end if;
         Length := D.Base_Length (Value.Arena, Row);
         if not Good or else not Length.Valid or else Length.Needed > Value.Arena_Count - Used then return; end if;
         Row.Base_Archive := (Used + 1, Length.Needed);
         D.Append_Base (Value.Arena, Row, Used, Length, Complete);
         if not Complete then return; end if;
         declare Digests : constant D.Event_Digest_Result := D.Event_Digests (Value.Arena, Value.Key, Row.Base_Archive); begin
            if not Digests.Present then return; end if;
            Digest_Text (Digests.Event_Id, Row.Event_Id); Digest_Text (Digests.Mac, Row.Mac);
         end;
         Length := D.Head_Length (Value.Arena, Row.Event_Id, Value.Genesis_Row);
         if not Good or else not Length.Valid or else Length.Needed > Value.Arena_Count - Used then return; end if;
         Head_Message := (Used + 1, Length.Needed);
         D.Append_Event_Head (Value.Arena, Row.Event_Id, Value.Genesis_Row, Used, Length, Complete);
         if not Complete then return; end if;
         Digest_Text (C.G.Mac (Value.Arena, Value.Key, Head_Message), Head_Mac);
         Intern ("EVENT", Head_Kind);
         Value.Events (New_Index) := Row; Value.Extras (New_Index) := Extra;
         Value.Arena_Used := Used;
         if not Good then return; end if;
         OJ.Establish (Value, Proof);
         if not OJ.Authenticated (Value, New_Index, Proof) then Fail (F.Join_Not_Ready); return; end if;
         if Mode = Cleanup_Route then
            if Kind not in M.Request_Lost_Event | M.Drain_Reclaimed_Event then return; end if;
            declare
               Subject : constant P.Optional_Subject :=
                 (if Subject_Index = 0 then (Present => False)
                  else (Present => True, Value => State.Subjects (Subject_Index)));
               Choice : constant SE.Cleanup_Kind := SE.Cleanup_Kind_Of
                 (Value, New_Index, State.Roots (Root_Index), Subject, Proof);
            begin
               Cleanup := (F.History_Folded,
                 (if Choice = SE.Retain_Unknown then F.Retain_Unknown else F.Recover_Retained),
                 Choice, 0);
            end;
            return;
         end if;
         if Mode = Serving_Route then
            if Kind /= M.Request_Responded_Event then return; end if;
            declare
               Subject : constant P.Optional_Subject :=
                 (if Subject_Index = 0 then (Present => False)
                  else (Present => True, Value => State.Subjects (Subject_Index)));
            begin
               Serving := SE.Serving_Join
                 (Value, New_Index, State.Roots (Root_Index),
                  State.Subjects, Subject, Proof);
               Result.Reason := (if Serving = SE.Evidence_Joined
                 then F.Recover_Retained else F.Join_Not_Ready);
               Result.Position := New_Index;
            end;
            return;
         end if;
         if Mode = Closed_Route then
            if Kind /= M.Closed_Witness_Event then return; end if;
            declare
               Subject : constant P.Optional_Subject :=
                 (if Subject_Index = 0 then (Present => False)
                  else (Present => True, Value => State.Subjects (Subject_Index)));
               References : constant RE.Closed_State_References := RE.Closed_Proof_Reference
                 (Value, New_Index, State.Roots (Root_Index), State.Subjects, Subject, Proof);
            begin
               -- Cached Root.Join already redecides the complete authenticated
               -- terminal/current owner-state relation exactly once.
               if References.Status = RE.Evidence_Joined then
                  Serving := SE.Evidence_Joined;
               end if;
               Result.Reason := (if Serving = SE.Evidence_Joined
                 then F.Recover_Retained else F.Join_Not_Ready);
               Result.Position := New_Index;
            end;
            return;
         end if;
         if Mode = Output_Route then
            declare
               Subject : constant P.Optional_Subject :=
                 (if Subject_Index = 0 then (Present => False)
                  else (Present => True, Value => State.Subjects (Subject_Index)));
            begin
               OS.Evaluate (Value, New_Index, State.Roots (Root_Index),
                 State.Subjects, Subject, Proof, Query, Output, Emitter);
            end;
            return;
         end if;
         F.Apply_Legal (Value, New_Index, State, History, Value.Alternatives, Proof,
                        Result.Reason, Applied);
         if not Applied then Fail (Result.Reason); return; end if;
         if J.Has_Alternative (Kind) and then Size.Alternatives = E.Count'Last / 7 then
            Fail (F.Input_Malformed); return;
         end if;
         declare
            New_Alternative : constant Boolean := J.Has_Alternative (Kind);
            Alternative_Count : constant E.Count := Size.Alternatives + (if New_Alternative then 1 else 0);
            Roots : D.Cells (1 .. State.Root_Count * 16);
            Subjects : D.Cells (1 .. State.Subject_Count * 9);
            Alternatives : D.Cells (1 .. Alternative_Count * 7);
            Blobs : D.Cells (1 .. Size.Blobs * 3);
            Event : constant D.Event_Columns :=
              ((S.SQL_Text, False, Row.Event_Id), (S.SQL_Text, False, Row.Previous),
               (S.SQL_Blob, False, Row.Generation), (S.SQL_Text, False, Row.Operation),
               (S.SQL_Text, False, Row.Subject_Kind), (S.SQL_Text, False, Row.Subject),
               (S.SQL_Blob, False, Row.Subgeneration), (S.SQL_Text, False, Row.Kind),
               (S.SQL_Text, False, Row.Actor), (S.SQL_Blob, False, Row.Record_Archive),
               (S.SQL_Blob, False, Row.Base_Archive), (S.SQL_Text, False, Row.Mac));
            Head : constant D.Head_Columns :=
              (Raw (Value.Head_SQL (1, 1)), (S.SQL_Text, False, Head_Kind),
               (S.SQL_Text, False, Row.Event_Id), (S.SQL_Null, False, (1, 0)),
               (S.SQL_Text, False, Head_Mac));
         begin
            for N in E.Count range 1 .. State.Root_Count loop
               pragma Loop_Variant (Increases => N);
               Roots ((N - 1) * 16 + 1 .. N * 16) :=
                 (Raw (State.Raw_Roots (N).Columns.Generation), Raw (State.Raw_Roots (N).Columns.Operation),
                  Raw (State.Raw_Roots (N).Columns.Phase), Raw (State.Raw_Roots (N).Columns.Before_Unknown),
                  Raw (State.Raw_Roots (N).Columns.Owners_Open), Raw (State.Raw_Roots (N).Columns.Abort_Kind),
                  Raw (State.Raw_Roots (N).Columns.Launched), Raw (State.Raw_Roots (N).Columns.Closure_NS),
                  Raw (State.Raw_Roots (N).Columns.Closure_Outer), Raw (State.Raw_Roots (N).Columns.Closure_Raw),
                  Raw (State.Raw_Roots (N).Columns.Witness), Raw (State.Raw_Roots (N).Columns.Settled),
                  Raw (State.Raw_Roots (N).Columns.Released_Unlaunched), Raw (State.Raw_Roots (N).Columns.Unknown_Cause),
                  Raw (State.Raw_Roots (N).Columns.Reattach_Epoch), Raw (State.Raw_Roots (N).Columns.Head_Event));
            end loop;
            for N in E.Count range 1 .. State.Subject_Count loop
               pragma Loop_Variant (Increases => N);
               Subjects ((N - 1) * 9 + 1 .. N * 9) :=
                 (Raw (State.Raw_Subjects (N).Columns.Generation), Raw (State.Raw_Subjects (N).Columns.Kind_Of_Subject),
                  Raw (State.Raw_Subjects (N).Columns.Subject), Raw (State.Raw_Subjects (N).Columns.Subgeneration),
                  Raw (State.Raw_Subjects (N).Columns.Phase), Raw (State.Raw_Subjects (N).Columns.Mode),
                  Raw (State.Raw_Subjects (N).Columns.Position), Raw (State.Raw_Subjects (N).Columns.Carried_From),
                  Raw (State.Raw_Subjects (N).Columns.Head_Event));
            end loop;
            for N in E.Count range 1 .. Size.Alternatives loop
               pragma Loop_Variant (Increases => N);
               for Col in Positive range 1 .. 7 loop Alternatives ((N - 1) * 7 + E.Count (Col)) := Raw (Value.Alternative_SQL (N, Col)); end loop;
            end loop;
            if New_Alternative then
               Intern ((case J.Set_Of (Kind) is when A.Ack_Set => "ACK", when A.Request_Set => "REQUEST", when A.Drain_Set => "DRAIN"), Alternative_Name);
               Alternatives (Size.Alternatives * 7 + 1 .. Alternative_Count * 7) :=
                 ((S.SQL_Blob, False, Row.Generation), (S.SQL_Text, False, Row.Operation),
                  (S.SQL_Text, False, Row.Subject_Kind), (S.SQL_Text, False, Row.Subject),
                  (S.SQL_Blob, False, Row.Subgeneration), (S.SQL_Text, False, Alternative_Name), (S.SQL_Text, False, Row.Event_Id));
            end if;
            for N in E.Count range 1 .. Size.Blobs loop
               pragma Loop_Variant (Increases => N);
               for Col in Positive range 1 .. 3 loop Blobs ((N - 1) * 3 + E.Count (Col)) := Raw (Value.Blob_SQL (N, Col)); end loop;
            end loop;
            if not Good then Fail (F.Input_Malformed); return; end if;
            D.Encode_Delta (Value.Arena, Event, Roots, Subjects, Alternatives, Blobs, Head, Head_Message, Output, Length, Complete);
            if not Length.Valid or else Length.Needed = 0 then Fail (F.Input_Malformed); return; end if;
            Result := (Ready_Apply, F.Front_Startup, 0, Length.Needed,
              (if Complete then Length.Needed else 0));
         end;
      end;
   end Decide_Staged;
   procedure Decide (Data : E.Bytes; Output : out E.Bytes;
                     Result : out Observation) is
      Cleanup : Cleanup_Observation;
      Serving : SE.Join_Status;
      Emitter : OS.Output_Observation;
   begin
      Decide_Staged (Data, Output, Result, Mutation_Delta, Cleanup, Serving, Emitter);
   end Decide;
   procedure Cleanup_Decide (Data : E.Bytes; Result : out Cleanup_Observation) is
      Output : E.Bytes (1 .. 0);
      Mutation : Observation;
      Serving : SE.Join_Status;
      Emitter : OS.Output_Observation;
   begin
      Decide_Staged (Data, Output, Mutation, Cleanup_Route, Result, Serving, Emitter);
      if Result.State = F.History_Folded then return; end if;
      if Mutation.State = Replay_Unchanged then
         Result := (F.History_Folded, F.Recover_Retained, SE.No_Event, Mutation.Position);
      else
         Result := (F.Fold_Refused, Mutation.Reason, SE.Retain_Unknown, Mutation.Position);
      end if;
   end Cleanup_Decide;
   procedure Serving_Decide (Data : E.Bytes; Result : out Serving_Observation) is
      Output : E.Bytes (1 .. 0);
      Mutation : Observation;
      Cleanup : Cleanup_Observation;
      Serving : SE.Join_Status;
      Emitter : OS.Output_Observation;
   begin
      Decide_Staged (Data, Output, Mutation, Serving_Route, Cleanup, Serving, Emitter);
      Result := (Serving, Mutation.Reason, Mutation.Position);
   end Serving_Decide;
   procedure Closed_Decide (Data : E.Bytes; Result : out Serving_Observation) is
      Output : E.Bytes (1 .. 0);
      Mutation : Observation;
      Cleanup : Cleanup_Observation;
      Serving : SE.Join_Status;
      Emitter : OS.Output_Observation;
   begin
      Decide_Staged (Data, Output, Mutation, Closed_Route, Cleanup, Serving, Emitter);
      Result := (Serving, Mutation.Reason, Mutation.Position);
   end Closed_Decide;
   procedure Retry_Decide (Data : E.Bytes; Output : out E.Bytes;
                           Result : out Observation) is
      Cleanup : Cleanup_Observation;
      Serving : SE.Join_Status;
      Emitter : OS.Output_Observation;
   begin
      Decide_Staged (Data, Output, Result, Retry_Delta, Cleanup, Serving, Emitter);
   end Retry_Decide;
   procedure Output_Query (Data : E.Bytes; Output : out E.Bytes;
                           Result : out OS.Output_Observation; Query : OS.Query_Kind)
     with Post => Result.Written <= Output'Length and then
       (if Result.Kind = OS.Refused then Result.Needed = 0 and then Result.Written = 0) and then
       (if Result.Kind /= OS.Refused then Result.Needed > 0 and then
          Result.Written = (if Result.Needed <= Output'Length then Result.Needed else 0))
   is
      Mutation : Observation;
      Cleanup : Cleanup_Observation;
      Serving : SE.Join_Status;
   begin
      Decide_Staged (Data, Output, Mutation, Output_Route, Cleanup, Serving, Result, Query);
   end Output_Query;
   procedure Output_Next (Data : E.Bytes; Output : out E.Bytes;
                          Result : out OS.Output_Observation) is
   begin
      Output_Query (Data, Output, Result, OS.Allocate);
   end Output_Next;
   procedure Output_Replay (Data : E.Bytes; Output : out E.Bytes;
                            Result : out OS.Output_Observation) is
   begin
      Output_Query (Data, Output, Result, OS.Replay);
   end Output_Replay;
   procedure Output_Written (Data : E.Bytes; Output : out E.Bytes;
                             Result : out OS.Output_Observation) is
   begin
      Output_Query (Data, Output, Result, OS.Confirm_Written);
   end Output_Written;
   procedure Output_Prefix (Data : E.Bytes; Output : out E.Bytes;
                            Result : out OS.Output_Observation) is
   begin
      Output_Query (Data, Output, Result, OS.Observe_Written);
   end Output_Prefix;
   function Attempt_Matches
     (Data : E.Bytes; Attempt, Containing_Input : E.Span) return Boolean
   is
      Input_Node : constant E.Span := OV.Record_Field (Data, Attempt, "input");
      Before_Node : constant E.Span := OV.Record_Field (Data, Attempt, "before");
      Candidate : constant E.Span := OV.Record_Field (Data, Attempt, "candidate");
      Native_Delta : constant E.Span := OV.Record_Field (Data, Attempt, "native_delta");
      function Number_Matches (Item : E.Span; Wanted : E.Count) return Boolean is
         Remaining : E.Count := Wanted;
      begin
         if not OV.Is_Integer (Data, Item) or else OV.Negative (Data, Item) then return False; end if;
         declare
            Magnitude : constant E.Byte_View := E.Decode (Data, Item, E.Operation).Payload;
         begin
            if not AP.Borrow_Valid (Data, Magnitude) then return False; end if;
            for N in E.Count range 1 .. AP.Byte_Length (Data, Magnitude) loop
               pragma Loop_Variant (Increases => N);
               if AP.Byte_At (Data, Magnitude, N - 1) /= Q.Byte (Remaining mod 256) then return False; end if;
               Remaining := Remaining / 256;
            end loop;
         end;
         return Remaining = 0;
      end Number_Matches;
   begin
      if not E.C.P.Valid (Data, Containing_Input) or else
         not OV.Type_Is (Data, Attempt, "dict") or else
         not OV.Valid_Bytes (Data, Input_Node) or else
         not OV.Valid_Bytes (Data, Before_Node) or else
         not OV.Type_Is (Data, Native_Delta, "dict") then return False; end if;
      declare
         Input : constant E.Bytes := OV.Bytes_Value (Data, Input_Node);
         Input_Root : constant E.Span := (Input'First, Input'Length);
         Input_Before : constant E.Span := T.Field (Input, Input_Root, "before");
         Input_Record : constant E.Span := T.Field (Input,
           T.Field (Input, Input_Root, "candidate"), "record");
         -- Render_Delta emits fixed ASCII keys/schema and cells
         -- [class 0..4, Boolean, hex payload]; SQL magnitudes/text stay bytes.
         -- This is not a bound for arbitrary JSON decimal or Unicode leaves.
         -- The exact captured native-delta grammar supplies storage, no cap.
         Output : E.Bytes (1 .. Native_Delta.Length);
         Result : Observation;
      begin
         -- A retained byte-image is structurally smaller than the containing
         -- authenticated load archive. This bounds recursion by real source,
         -- without any limit on accepted archive nesting or row count.
         if Input'Length >= Containing_Input.Length or else
            not T.Valid (Input, Input_Root) or else
            not T.Valid (Input, Input_Before) or else
            not AP.Bytes_Equal (Input, Data, (Input_Before, 0),
              E.Decode (Data, Before_Node, E.Operation).Payload) or else
            not AP.Scoped_Archive_Operation_Matches
              (Input, Data, Input_Record, Candidate) then return False; end if;
         Decide (Input, Output, Result);
         if Result.State /= Ready_Apply or else Result.Written = 0 or else
            Result.Written /= Result.Needed or else
            not Number_Matches (OV.Record_Field (Data, Attempt, "native_status"), E.Count (Status_Code (Result))) or else
            not Number_Matches (OV.Record_Field (Data, Attempt, "native_position"), Result.Position)
         then return False; end if;
         -- Native Render_Delta is canonical JSON; borrow both complete images.
         -- No concatenation, second allocation/copy, or summed-extent refusal.
         declare
            Matched : constant Boolean := E.C.Operation_Archive_JSON_Matches
              (Output, Data, (Output'First, Result.Written), Native_Delta);
            Bound : constant Worldline.Custody_V2_Delta_Grammar.Bound_Result :=
              Worldline.Custody_V2_Delta_Grammar.Bound (Data, Native_Delta) with Ghost;
         begin
            -- A/B/C scalar JACKAL receipts are not this code proof. The actual
            -- restricted typed grammar and the complete canonical matcher are
            -- the caller obligations; no ghost status is used as authority.
            pragma Assert (if Matched then Bound.Valid and then
              Bound.JSON_Length = Result.Written and then
              Bound.JSON_Length <= Native_Delta.Length);
            return Matched;
         end;
      end;
   end Attempt_Matches;
end Worldline.Custody_V2_Mutation_Decision;

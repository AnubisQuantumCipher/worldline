with Interfaces;
with Canonical_Artifacts;
with Worldline.Custody_V2_Root_Evidence;
with Worldline.Custody_V2_Subject_Evidence;
with Worldline.Custody_V2_Owner_Correspondence;
with Worldline.Root_Custody_Row_Views;
with Worldline.Retained_Evidence_Replay;
with Worldline.Startup_Admission;
package body Worldline.Custody_V2_Fold_Engine with SPARK_Mode is
   package N renames I.N;
   package V renames I.V;
   package RV renames Worldline.Root_Custody_Row_Views;
   package RE renames Worldline.Custody_V2_Root_Evidence;
   package SE renames Worldline.Custody_V2_Subject_Evidence;
   package OC renames Worldline.Custody_V2_Owner_Correspondence;
   use type OJ.Head_Disposition;
   package ER renames Worldline.Retained_Evidence_Replay;
   use type I.Decode_Status;
   use type D.Decode_Status;
   use type F.Status;
   use type H.Status;
   use type M.Event_Kind;
   use type M.Subject_Kind;
   use type M.Root_Phase;
   use type M.Request_Phase;
   use type M.Descriptor_Phase;
   use type M.Transfer_Mode;
   use type M.Abort_Class;
   use type M.Actor;
   use type M.Owner;
   use type M.Digest;
   use type Q.Ordering;
   use type Q.Byte;
   use type S.SQL_Class;
   use type S.Name_Status;
   use type P.Event_Family;
   use type A.R.Replay_Status;
   use type A.Decision_Status;
   use type RE.Join_Status;
   use type SE.Join_Status;
   use type ER.Replay_State;
   use type ER.Scoped_Entry;
   use type Canonical_Artifacts.Genesis_Correspondence;
   use type Interfaces.Unsigned_32;
   function Root_Index (Value : I.Parsed_Input; State : Fold_State;
                        Event : M.Event_Record) return Q.Byte_Count is
   begin
      if Event.Kind = M.Front_Owned_Event then return State.Current; end if;
      if State.Logical_S0 and then State.Current in State.Roots'Range and then
         Q.Compare (Value.Arena, State.Roots (State.Current).Generation,
                    Event.Generation) = Q.Equal then return State.Current; end if;
      for R in Q.Byte_Count range 1 .. State.Root_Count loop
         pragma Loop_Variant (Increases => R);
         if Q.Compare (Value.Arena, State.Roots (R).Generation, Event.Generation) = Q.Equal
         then return R; end if;
      end loop;
      return 0;
   end Root_Index;

   function Subject_Index (Value : I.Parsed_Input; State : Fold_State;
                           Event : M.Event_Record) return Q.Byte_Count is
   begin
      for T in Q.Byte_Count range 1 .. State.Subject_Count loop
         pragma Loop_Variant (Increases => T);
         if State.Subjects (T).Kind = Event.Kind_Of_Subject and then
            Q.Compare (Value.Arena, State.Subjects (T).Generation, Event.Generation) = Q.Equal
            and then A.L.Optional_Same (Value.Arena, State.Subjects (T).Subject, Event.Subject)
         then return T; end if;
      end loop;
      return 0;
   end Subject_Index;

   function Hex (Digest : M.Digest) return String is
      Hex_Digits : constant String := "0123456789abcdef";
      Text : String (1 .. 64);
   begin
      for B in Digest'Range loop
         pragma Loop_Variant (Increases => B);
         Text (1 + (B - Digest'First) * 2) := Hex_Digits (1 + Integer (Digest (B) / 16));
         Text (2 + (B - Digest'First) * 2) := Hex_Digits (1 + Integer (Digest (B) mod 16));
      end loop;
      return Text;
   end Hex;

   function Head_Reference
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Name : String;
      Present : Boolean; Head : M.Digest) return Boolean
   is
      X5 : constant C.E.Span := V.Record_Field (Value.Arena, Value.Events (Index).Record_Archive, "x5");
      Ref : constant C.E.Span := V.Record_Field (Value.Arena, X5, Name);
   begin
      if not Present then return V.Is_Null (Value.Arena, Ref); end if;
      if not C.S.Text_Is (Value.Arena, Ref, Hex (Head)) then return False; end if;
      for Earlier in Value.Events'Range loop
         pragma Loop_Variant (Increases => Earlier);
         if Earlier < Index and then C.G.Origin_Matches
           (Value.Arena, Value.Events (Earlier).Event_Id, Head) then return True; end if;
      end loop;
      return False;
   end Head_Reference;

   function Rows_Match (Value : I.Parsed_Input; State : Fold_State) return Boolean is
   begin
      if State.Root_Count > State.Root_Capacity or else
         State.Subject_Count > State.Subject_Capacity then return False; end if;
      return F.Compare (Value.Arena, State.Raw_Roots (1 .. State.Root_Count), Value.Roots,
        State.Raw_Subjects (1 .. State.Subject_Count), Value.Subjects).State =
        F.Complete_Rows_Equal_Not_A_Fold_Claim;
   end Rows_Match;
   function Raw_Alternatives_Exact
     (Value : I.Parsed_Input; History : A.R.Retained_Events) return Boolean
   is
      Joined : Boolean;
   begin
      if not J.Alternatives_Exact (Value.Arena, History, Value.Alternatives) then return False; end if;
      for Row in Value.Alternatives'Range loop
         pragma Loop_Variant (Increases => Row);
         Joined := False;
         for Event in History'Range loop
            pragma Loop_Variant (Increases => Event);
            if J.Row_Joined (Value.Arena, Value.Alternatives (Row), History (Event).Event) then
               Joined := S.Same_Cell (Value.Arena, Value.Alternative_SQL (Row, 1), Value.Event_SQL (Event, 4))
                 and then S.Same_Cell (Value.Arena, Value.Alternative_SQL (Row, 2), Value.Event_SQL (Event, 5))
                 and then S.Same_Cell (Value.Arena, Value.Alternative_SQL (Row, 3), Value.Event_SQL (Event, 6))
                 and then S.Same_Cell (Value.Arena, Value.Alternative_SQL (Row, 4), Value.Event_SQL (Event, 7))
                 and then S.Same_Cell (Value.Arena, Value.Alternative_SQL (Row, 5), Value.Event_SQL (Event, 8))
                 and then S.Same_Cell (Value.Arena, Value.Alternative_SQL (Row, 7), Value.Event_SQL (Event, 2))
                 and then S.Text_Is (Value.Arena, Value.Alternative_SQL (Row, 6),
                   (case J.Set_Of (History (Event).Event.Kind) is
                      when A.Ack_Set => "ACK",
                      when A.Request_Set => "REQUEST",
                      when A.Drain_Set => "DRAIN"));
               exit;
            end if;
         end loop;
         if not Joined then return False; end if;
      end loop;
      return True;
   end Raw_Alternatives_Exact;

   function Legal_Decoded
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Event : M.Event_Record; State : Fold_State;
      History : A.R.Retained_Events; Alternatives : A.Alternative_Rows;
      Proof : OJ.Journal_Proof)
      return Status
      with Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 6)
   is
   begin
      if Value.Status /= I.Parsed or else Index not in Value.Events'Range or else
         State.Current not in State.Roots'Range or else State.Root_Count > State.Root_Capacity
         or else State.Subject_Count > State.Subject_Capacity then return Input_Malformed; end if;
      declare
            RI : constant Q.Byte_Count := Root_Index (Value, State, Event);
            TI : constant Q.Byte_Count := Subject_Index (Value, State, Event);
            Family : constant P.Event_Family := P.Family (Event.Kind);
            Subject : constant P.Optional_Subject :=
              (if TI = 0 then (Present => False) else (Present => True, Value => State.Subjects (TI)));
         begin
            if RI not in State.Roots'Range then return Wrong_Generation; end if;
            declare
               Before : constant M.Root_State := State.Roots (RI);
               Current : constant M.Root_State := State.Roots (State.Current);
               Ref : constant A.C.Root_Reference :=
                 (Current.Generation, Current.Operation, Current.Head);
            begin
               if Event.Kind = M.Front_Owned_Event then
                  if RI /= State.Current or else not P.New_Generation_Successor_Clause
                    (Value.Arena, Before, Event) then return Wrong_Generation; end if;
               elsif Q.Compare (Value.Arena, Event.Generation, Current.Generation) /= Q.Equal then
                  if not ((P.Is_Physical (Event.Kind) and then Before.Phase = M.Ended) or else
                    (Event.Kind in M.Request_Lost_Event | M.Request_Abandon_Event | M.Drain_Reclaimed_Event
                     and then not (for some Earlier of History =>
                       Earlier.Event.Kind = M.Custody_Returned_Event and then
                       Q.Compare (Value.Arena, Earlier.Event.Generation, Event.Generation) = Q.Equal)))
                  then return Wrong_Generation; end if;
               end if;
               if Event.Kind_Of_Subject = M.Root and then
                  Event.Kind not in M.Prepared_Event | M.Front_Owned_Event and then
                  not A.L.Optional_Same (Value.Arena, Before.Operation, Event.Operation)
               then return Join_Not_Ready; end if;
               if A.R.Resolve (Value.Arena, History, A.R.Key (Event)).Status /= A.R.No_Replay
               then return Ambiguous_History; end if;
               if not J.Alternative_Free (Value.Arena, History, Event)
               then return Alternative_Taken; end if;
               if not Head_Reference (Value, Index, "predecessor_root", not State.Logical_S0, Before.Head)
                 or else not Head_Reference (Value, Index, "predecessor_subject", Subject.Present,
                   (if Subject.Present then Subject.Value.Head else Worldline.Zero_Hash))
               then return CAS_Stale; end if;
               if Family in P.Request_Transition | P.Descriptor_Transition then
                  if Event.Kind_Of_Subject = M.Root then return Subject_Unknown; end if;
                  if Family = P.Request_Transition then
                     if Event.Kind_Of_Subject /= M.Request or else
                        not P.Request_From_Clause (Subject, Event.Kind) then return Illegal_Request_Transition; end if;
                     if not P.Request_Fixed_Actor_Clause (Subject, Event.Kind, Event.Appending_Actor)
                     then return Wrong_Actor; end if;
                     if not P.Request_Subgeneration_Clause (Value.Arena, Subject, Event)
                     then return Join_Not_Ready; end if;
                  else
                     if Event.Kind_Of_Subject /= M.Descriptor or else
                        not P.Descriptor_From_Clause (Subject, Event.Kind) then return Illegal_Descriptor_Transition; end if;
                     if not P.Descriptor_Fixed_Actor_Clause (Event.Kind, Event.Appending_Actor)
                     then return Wrong_Actor; end if;
                     if Subject.Present and then
                        Q.Compare (Value.Arena, Subject.Value.Subgeneration, Event.Subgeneration) /= Q.Equal
                     then return Join_Not_Ready; end if;
                     if Event.Kind = M.Drain_Abandon_Event and then
                        (not Subject.Present or else Value.Extras (Index).Next_Subgeneration.Kind /= S.SQL_Blob
                         or else not P.Descriptor_Abandon_Successor_Clause (Value.Arena,
                           Subject.Value, Event, S.Blob_Quantity (Value.Extras (Index).Next_Subgeneration)))
                     then return Join_Not_Ready; end if;
                  end if;
                  case Event.Kind is
                     when M.Request_Queued_Event =>
                        if Before.Phase = M.Front_Owned and then Before.Owners_Open then return Cross_Condition; end if;
                     when M.Request_Transfer_Intent_Event | M.Drain_Stop_Intent_Event =>
                        if not P.Transfer_Root_Clause (Before) or else
                           A.C.Original_Owner_Equation (Before) /= M.Worker then return Cross_Condition; end if;
                     when M.Request_Intake_Event | M.Drain_Intake_Event =>
                        if not M.Is_Worker_Phase (Before.Phase) or else not
                          (for some Earlier of History => Earlier.Event.Kind = M.Custody_Ack_Event and then
                             Q.Compare (Value.Arena, Earlier.Event.Generation, Event.Generation) = Q.Equal and then
                             A.L.Optional_Same (Value.Arena, Earlier.Event.Operation, Before.Operation))
                        then return Cross_Condition; end if;
                     when M.Request_Responded_Event =>
                        if Subject.Present and then Subject.Value.Request = M.Queued and then
                           A.C.Original_Owner_Equation (Before) /= M.Front then return Cross_Condition; end if;
                     when others => null;
                  end case;
                  if SE.Join (Value, Index, Before, State.Subjects (1 .. State.Subject_Count), Subject, Proof) /= SE.Evidence_Joined
                  then return Evidence_Missing; end if;
                  if Event.Kind = M.Request_Abandon_Event then
                     declare
                        ER : constant A.Expected_Root := (Before.Generation, Before.Operation,
                          Before.Head, Before.Phase, Before.Owners_Open, Before.Reattach_Epoch);
                        ET : constant D.RA.Expected_Request :=
                          (Subject.Value.Generation, Subject.Value.Subject, Subject.Value.Subgeneration,
                           Subject.Value.Head, Subject.Value.Request);
                     begin
                        if not D.RA.Legal (Value.Arena,
                          State.Roots (1 .. Q.Byte_Count'Max (1, State.Root_Count)),
                          State.Subjects (1 .. State.Subject_Count), History, Alternatives, ER, ET, Event)
                        then return Illegal_Request_Transition; end if;
                     end;
                  end if;
               else
                  if Event.Kind_Of_Subject /= M.Root or else not Event.Subject.Present or else
                     Event.Subject.Value.Length /= 0 or else not Q.Is_Zero (Value.Arena, Event.Subgeneration)
                  then return Subject_Unknown; end if;
                  if not P.Root_From_Clause (Before, Event.Kind) then return Illegal_Root_Transition; end if;
                  if Event.Kind = M.Unknown_Event then
                     if not P.Unknown_Actor_Clause (Value.Arena,
                       State.Roots (1 .. Q.Byte_Count'Max (1, State.Root_Count)), Ref, Event.Appending_Actor)
                     then return Wrong_Actor; end if;
                  elsif not P.Fixed_Root_Actor_Clause (Before, Event.Kind, Event.Appending_Actor)
                  then return Wrong_Actor; end if;
                  if P.Is_Physical (Event.Kind) and then not P.Physical_Flag_Clause (Before, Event.Kind)
                  then return Cross_Condition; end if;
                  if Event.Kind in M.Closed_Witness_Event | M.Custody_Returned_Event and then
                     not P.Subject_Barrier (Value.Arena, State.Subjects (1 .. State.Subject_Count), Before.Generation)
                  then return Barrier_Subjects_Open; end if;
                  if Event.Kind = M.Worker_Reattached_Event and then
                    (Value.Extras (Index).Reattach_Epoch.Kind /= S.SQL_Blob or else
                     not P.Reattach_Successor_Clause (Value.Arena, Before,
                       S.Blob_Quantity (Value.Extras (Index).Reattach_Epoch)))
                  then return Join_Not_Ready; end if;
                  if Event.Kind = M.Unknown_Event and then
                     not S.Digest_Text (Value.Arena, Value.Extras (Index).Unknown_Cause)
                  then return Evidence_Missing; end if;
                  if Event.Kind = M.Handoff_Abort_Event and then
                     S.Read_Abort_Class_Name (Value.Arena, Value.Extras (Index).Abort_Class).Status /= S.Exact_Name
                  then return Evidence_Missing; end if;
                  if RE.Join (Value, Index, Before, State.Subjects (1 .. State.Subject_Count), Subject, Proof) /= RE.Evidence_Joined
                  then return Evidence_Missing; end if;
                  if Event.Kind = M.Abandon_Event then
                     declare
                        Expected : constant A.Expected_Root := (Before.Generation, Before.Operation,
                          Before.Head, Before.Phase, Before.Owners_Open, Before.Reattach_Epoch);
                     begin
                        if not A.Legal_Abandon (Value.Arena,
                          State.Roots (1 .. Q.Byte_Count'Max (1, State.Root_Count)),
                          History, Alternatives, Expected, Event) then return Illegal_Root_Transition; end if;
                     end;
                  end if;
               end if;
               return Front_Startup;
            end;
         end;
   end Legal_Decoded;
   function Legal
     (Value : I.Parsed_Input; Index : Q.Byte_Count; State : Fold_State;
      History : A.R.Retained_Events; Alternatives : A.Alternative_Rows;
      Proof : OJ.Journal_Proof) return Status
   is
   begin
      if Index not in Value.Events'Range then return Input_Malformed; end if;
      declare
         Event : constant D.Decoded_Event := D.Decode (Value.Arena, Value.Events (Index));
      begin
         if Event.Status /= D.Decoded then return Input_Malformed; end if;
         return Legal_Decoded (Value, Index, Event.Value, State, History, Alternatives, Proof);
      end;
   end Legal;

   procedure Next_Decoded
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Event : M.Event_Record;
      State : in out Fold_State; Applied : out Boolean)
   is
   begin
      Applied := False;
      if Index not in Value.Events'Range then return; end if;
      declare
            Raw : constant C.Event_Row := Value.Events (Index);
            RI : constant Q.Byte_Count := Root_Index (Value, State, Event);
            TI : Q.Byte_Count := Subject_Index (Value, State, Event);
            Family : constant P.Event_Family := P.Family (Event.Kind);
            Mode : M.Transfer_Mode := M.None;
         begin
            if RI not in State.Roots'Range then return; end if;
            if Family in P.Request_Transition | P.Descriptor_Transition then
               if Event.Kind = M.Request_Transfer_Intent_Event then
                  if S.Read_Transfer_Mode_Name (Value.Arena, Value.Extras (Index).Transfer_Mode).Status /= S.Exact_Name
                  then return; end if;
                  Mode := S.Read_Transfer_Mode_Name (Value.Arena, Value.Extras (Index).Transfer_Mode).Value;
                  if Mode = M.None then return; end if;
               end if;
               if TI = 0 then
                  if State.Subject_Count = State.Subject_Capacity then return; end if;
                  TI := State.Subject_Count + 1;
                  State.Subjects (TI) := (Kind => Event.Kind_Of_Subject, Generation => Event.Generation,
                    Subject => Event.Subject, Subgeneration => Event.Subgeneration,
                    Request => M.Queued, Descriptor => M.Stop_Intent, Mode => M.None,
                    Position => (Present => False), Carried_From => (Present => False), Head => Event.Event_Id);
                  State.Raw_Subjects (TI) := (Present => True,
                    Columns => N.New_Subject (Raw, Event.Kind_Of_Subject, Value.Symbols));
                  State.Subject_Count := TI;
               elsif Event.Kind = M.Request_Transfer_Intent_Event then
                  State.Subjects (TI) := P.Request_Transfer_Image (State.Subjects (TI), Event, Mode);
               elsif Event.Kind = M.Drain_Abandon_Event then
                  if Value.Extras (Index).Next_Subgeneration.Kind /= S.SQL_Blob then return; end if;
                  State.Subjects (TI) := P.Descriptor_Abandon_Image (State.Subjects (TI), Event,
                    S.Blob_Quantity (Value.Extras (Index).Next_Subgeneration));
               elsif Event.Kind = M.Drain_Freeze_Event then
                  if Value.Extras (Index).Position.Kind /= S.SQL_Blob then return; end if;
                  State.Subjects (TI) := P.Descriptor_Freeze_Image (State.Subjects (TI), Event,
                    S.Blob_Quantity (Value.Extras (Index).Position));
               elsif Family = P.Request_Transition then
                  State.Subjects (TI) := P.Request_Phase_Image (State.Subjects (TI), Event);
               else
                  State.Subjects (TI) := P.Descriptor_Phase_Image (State.Subjects (TI), Event);
               end if;
               State.Raw_Subjects (TI) := (Present => True, Columns =>
                 N.Subject_Image (State.Raw_Subjects (TI).Columns, Event.Kind, Raw, Value.Symbols,
                   Mode, Value.Extras (Index).Position, Value.Extras (Index).Next_Subgeneration));
            elsif Event.Kind = M.Front_Owned_Event then
               if State.Root_Count = State.Root_Capacity then return; end if;
               declare
                  Old_Subject_Count : constant Q.Byte_Count := State.Subject_Count;
                  Carry_Count : Q.Byte_Count := 0;
               begin
                  for T in Q.Byte_Count range 1 .. Old_Subject_Count loop
                     pragma Loop_Variant (Increases => T);
                     if State.Subjects (T).Kind = M.Request and then
                        Q.Compare (Value.Arena, State.Subjects (T).Generation, State.Roots (RI).Generation) = Q.Equal
                        and then State.Subjects (T).Request in M.Queued | M.Abandoned
                     then Carry_Count := Carry_Count + 1; end if;
                  end loop;
                  if Carry_Count > State.Subject_Capacity - State.Subject_Count then return; end if;
                  State.Roots (RI) := P.Root_End_Image (State.Roots (RI), Event);
                  State.Raw_Roots (RI) := (Present => True,
                    Columns => N.End_Image (State.Raw_Roots (RI).Columns, Raw, Value.Symbols));
                  State.Root_Count := State.Root_Count + 1;
                  State.Current := State.Root_Count;
                  State.Roots (State.Current) := (Generation => Event.Generation, Operation => (Present => False),
                    Phase => M.Front_Owned, Before_Unknown => M.Front_Owned, Owners_Open => True,
                    Abort_Kind => M.Dispatched, Physical => (others => False), Unknown_Cause => (Present => False),
                    Reattach_Epoch => S.Blob_Quantity (Value.Symbols.Zero_Magnitude), Head => Event.Event_Id);
                  State.Raw_Roots (State.Current) := (Present => True, Columns => N.New_Generation (Raw, Value.Symbols));
                  for T in Q.Byte_Count range 1 .. Old_Subject_Count loop
                     pragma Loop_Variant (Increases => T);
                     if State.Subjects (T).Kind = M.Request and then
                        Q.Compare (Value.Arena, State.Subjects (T).Generation, State.Roots (RI).Generation) = Q.Equal
                        and then State.Subjects (T).Request in M.Queued | M.Abandoned then
                        State.Subject_Count := State.Subject_Count + 1;
                        State.Subjects (State.Subject_Count) := P.Carried_Request_Fields_Image
                          (State.Subjects (T), Event, S.Blob_Quantity (Value.Symbols.Zero_Magnitude));
                        State.Raw_Subjects (State.Subject_Count) := (Present => True,
                          Columns => N.Carried_Image (State.Raw_Subjects (T).Columns, Raw, Value.Symbols));
                     end if;
                  end loop;
               end;
            else
               declare
                  Abort_Kind : constant M.Abort_Class :=
                    (if Event.Kind = M.Handoff_Abort_Event then
                       S.Read_Abort_Class_Name (Value.Arena, Value.Extras (Index).Abort_Class).Value
                     else State.Roots (RI).Abort_Kind);
               begin
                  if State.Logical_S0 then
                     if State.Root_Capacity = 0 then return; end if;
                     State.Root_Count := 1;
                     State.Raw_Roots (1) := (Present => True, Columns =>
                       (Generation => (Kind => S.SQL_Blob, Bytes =>
                          (State.Roots (1).Generation.First, State.Roots (1).Generation.Length)),
                        Operation => Value.Symbols.Empty_Text, Phase => Value.Symbols.Root (M.Front_Owned),
                        Before_Unknown => (Kind => S.SQL_Null), Owners_Open => Value.Symbols.One,
                        Abort_Kind => (Kind => S.SQL_Null), Launched => Value.Symbols.Zero,
                        Closure_NS => Value.Symbols.Zero, Closure_Outer => Value.Symbols.Zero,
                        Closure_Raw => Value.Symbols.Zero, Witness => Value.Symbols.Zero,
                        Settled => Value.Symbols.Zero, Released_Unlaunched => Value.Symbols.Zero,
                        Unknown_Cause => (Kind => S.SQL_Null), Reattach_Epoch => Value.Symbols.Zero_Magnitude,
                        Head_Event => (Kind => S.SQL_Null)));
                     State.Logical_S0 := False;
                  end if;
                  if Event.Kind = M.Unknown_Event then
                     State.Roots (RI) := P.Unknown_Image (State.Roots (RI), Event,
                       RV.Decode_Digest (Value.Arena, Value.Extras (Index).Unknown_Cause));
                  elsif Event.Kind = M.Reconciled_Event then
                     State.Roots (RI) := P.Reconciled_Image (State.Roots (RI), Event);
                  elsif Event.Kind = M.Worker_Reattached_Event then
                     State.Roots (RI) := P.Reattached_Image (State.Roots (RI), Event,
                       S.Blob_Quantity (Value.Extras (Index).Reattach_Epoch));
                  elsif Event.Kind = M.Handoff_Abort_Event then
                     State.Roots (RI) := P.Abort_Phase_Image (State.Roots (RI), Event, Abort_Kind);
                     if Abort_Kind = M.Never_Dispatched then
                        State.Roots (RI).Physical.Released_Unlaunched := True;
                     end if;
                  else
                     State.Roots (RI) := P.Single_Root_Image (State.Roots (RI), Event);
                  end if;
                  State.Raw_Roots (RI) := (Present => True, Columns =>
                    N.Root_Image (Value.Arena, State.Raw_Roots (RI).Columns, Event.Kind, Raw,
                      Value.Symbols, Abort_Kind, Value.Extras (Index).Reattach_Epoch,
                      Value.Extras (Index).Unknown_Cause));
               end;
            end if;
            Applied := True;
         end;
   end Next_Decoded;
   procedure Next (Value : I.Parsed_Input; Index : Q.Byte_Count;
                   State : in out Fold_State; Applied : out Boolean)
   is
   begin
      Applied := False;
      if Index not in Value.Events'Range then return; end if;
      declare
         Event : constant D.Decoded_Event := D.Decode (Value.Arena, Value.Events (Index));
      begin
         if Event.Status /= D.Decoded then return; end if;
         Next_Decoded (Value, Index, Event.Value, State, Applied);
      end;
   end Next;
   procedure Apply_Legal
     (Value : I.Parsed_Input; Index : Q.Byte_Count; State : in out Fold_State;
      History : A.R.Retained_Events; Alternatives : A.Alternative_Rows;
      Proof : OJ.Journal_Proof; Reason : out Status; Applied : out Boolean)
   is
   begin
      Applied := False;
      Reason := Input_Malformed;
      if Value.Status /= I.Parsed or else Index not in Value.Events'Range then return; end if;
      declare
         Event : constant D.Decoded_Event := D.Decode (Value.Arena, Value.Events (Index));
      begin
         if Event.Status /= D.Decoded then return; end if;
         Reason := Legal_Decoded (Value, Index, Event.Value, State, History, Alternatives, Proof);
         if Reason /= Front_Startup then return; end if;
         Next_Decoded (Value, Index, Event.Value, State, Applied);
         if not Applied then Reason := Stored_Rows_Differ; end if;
      end;
   end Apply_Legal;


      -- Rejected-path initialization only. H.Materialize overwrites the whole
      -- authenticated extent before any scratch row is used by Legal/Next.
      Blank : constant A.R.Retained_Event :=
        (Event => (Kind => M.Prepared_Event, Generation => (False, 1, 0),
           Operation => (Present => False), Kind_Of_Subject => M.Root,
           Subject => (Present => False), Subgeneration => (False, 1, 0),
           Appending_Actor => M.Front, Record_Digest => Worldline.Zero_Hash,
           Event_Id => Worldline.Zero_Hash),
         Previous => Worldline.Zero_Hash, Mac => Worldline.Zero_Hash,
         Record_Bytes => (Present => False), Base_Archive => (Present => False));
   procedure Fold_Prefix_Core
     (Value : I.Parsed_Input; Through : Q.Byte_Count; State : out Fold_State;
      History : in out A.R.Retained_Events; Proof : out OJ.Journal_Proof;
      Result : out Observation; Initial_Proof : OJ.Journal_Proof)
      with Subprogram_Variant => (Decreases => Value.Source_Input.Length, Decreases => 7)
   is
      Origin : M.Digest := Worldline.Zero_Hash;
   begin
      Result := (Fold_Refused, Input_Malformed, 0);
      Proof := Initial_Proof;
      State.Root_Count := 0; State.Subject_Count := 0; State.Current := 0; State.Logical_S0 := True;
      State.Raw_Roots := (others => (Present => False));
      State.Raw_Subjects := (others => (Present => False));
      -- Initialized rejected-path scratch is never a durable S0 or evidence.
      State.Roots := (others =>
        (Generation => (False, 1, 0), Operation => (Present => False),
         Phase => M.Front_Owned, Before_Unknown => M.Front_Owned, Owners_Open => False,
         Abort_Kind => M.Dispatched, Physical => (others => False),
         Unknown_Cause => (Present => False), Reattach_Epoch => (False, 1, 0),
         Head => Worldline.Zero_Hash));
      State.Subjects := (others =>
        (Kind => M.Request, Generation => (False, 1, 0), Subject => (Present => False),
         Subgeneration => (False, 1, 0), Request => M.Queued, Descriptor => M.Front_Held,
         Mode => M.None, Position => (Present => False), Carried_From => (Present => False),
         Head => Worldline.Zero_Hash));
      if Value.Status /= I.Parsed or else Through > Value.Decoded_Event_Count or else
         Value.Decoded_Event_Count > Value.Event_Count or else
         History'First /= 1 or else History'Length /= Value.Decoded_Event_Count or else
         State.Root_Capacity < Q.Byte_Count'Max (1, Value.Root_Count)
         or else State.Subject_Capacity < Value.Subject_Count or else not I.Parsed_Spans_Valid (Value)
      then return; end if;
      if Canonical_Artifacts.Genesis_Archive_Matches (Value.Arena, Value.Genesis_File, Value.Genesis_Row) /=
         Canonical_Artifacts.Typed_Tree_Matches_Source_Custody_Open then
         Result.Reason := Genesis_Correspondence; return;
      end if;
      Origin := C.G.Hash (Value.Arena, Value.Genesis_Row);
      declare
         Seed : constant M.Root_State :=
           (Generation => Value.Symbols.One.Integer_Value, Operation => (Present => False),
            Phase => M.Front_Owned, Before_Unknown => M.Front_Owned, Owners_Open => True,
            Abort_Kind => M.Dispatched, Physical => (others => False), Unknown_Cause => (Present => False),
            Reattach_Epoch => S.Blob_Quantity (Value.Symbols.Zero_Magnitude), Head => Origin);
         Alternatives : A.Alternative_Rows (1 .. Value.Alternative_Count) :=
           (others => (Generation => Seed.Generation, Operation => (Present => False),
             Kind_Of_Subject => M.Root, Subject => (Present => False), Subgeneration => Seed.Reattach_Epoch,
             Set => A.Ack_Set, Event_Id => Worldline.Zero_Hash));
         Alternative_Count : Q.Byte_Count := 0;
         Auth : H.Observation;
         Applied : Boolean;
      begin
         State.Roots (1) := Seed;
         State.Current := 1;
         H.Materialize (Value.Arena, Value.Key, Value.Genesis_Row, Value.Genesis_Message,
           Value.Genesis_Mac, Value.Events (1 .. Value.Decoded_Event_Count),
           Value.Heads, History, Auth);
         if Auth.State /= H.Authenticated_History_Genesis_JSON_And_Fold_Open then
            Result.Reason := Archive_Chain_Refused; Result.Position := Auth.Position; return;
         end if;
         if not Raw_Alternatives_Exact (Value, History) then
            Result.Reason := Stored_Rows_Differ; return;
         end if;
         if not OJ.Established (Value, Proof) then OJ.Establish (Value, Proof); end if;
         for Index in Q.Byte_Count range 1 .. Through loop
            pragma Loop_Variant (Increases => Index);
            pragma Loop_Invariant (State.Root_Count <= State.Root_Capacity);
            pragma Loop_Invariant (State.Subject_Count <= State.Subject_Capacity);
            pragma Loop_Invariant (Alternative_Count <= Alternatives'Length);
            Result.Position := Index;
            if Value.Event_SQL (Index, 1).Kind /= S.SQL_Integer or else
               (Index > Value.Events'First and then
                Q.Compare (Value.Arena, Value.Event_SQL (Index - 1, 1).Integer_Value,
                  Value.Event_SQL (Index, 1).Integer_Value) /= Q.Less) then
               Result.Reason := Input_Malformed; return;
            end if;
            Result.Reason := Legal_Decoded (Value, Index, History (Index).Event, State,
              History (Value.Events'First .. Index - 1), Alternatives (1 .. Alternative_Count), Proof);
            if Result.Reason /= Front_Startup then return; end if;
            Next_Decoded (Value, Index, History (Index).Event, State, Applied);
            if not Applied then Result.Reason := Stored_Rows_Differ; return; end if;
            if J.Has_Alternative (History (Index).Event.Kind) then
               if Alternative_Count = Alternatives'Length then Result.Reason := Stored_Rows_Differ; return; end if;
               Alternative_Count := Alternative_Count + 1;
               Alternatives (Alternative_Count) := (History (Index).Event.Generation,
                 History (Index).Event.Operation, History (Index).Event.Kind_Of_Subject,
                 History (Index).Event.Subject, History (Index).Event.Subgeneration,
                 J.Set_Of (History (Index).Event.Kind), History (Index).Event.Event_Id);
            end if;
         end loop;
         if Through = Value.Decoded_Event_Count and then
            (State.Root_Count /= Value.Root_Count or else State.Subject_Count /= Value.Subject_Count
             or else not Rows_Match (Value, State)) then
            Result.Reason := Stored_Rows_Differ; return;
         end if;
         Result := (History_Folded, Front_Startup, 0);
      end;
   end Fold_Prefix_Core;
   procedure Fold_Prefix
     (Value : I.Parsed_Input; Through : Q.Byte_Count; State : out Fold_State;
      History : in out A.R.Retained_Events; Proof : out OJ.Journal_Proof;
      Result : out Observation)
   is
      Initial_Proof : OJ.Journal_Proof;
   begin
      Fold_Prefix_Core (Value, Through, State, History, Proof, Result, Initial_Proof);
   end Fold_Prefix;
   procedure Fold_Prefix
     (Value : I.Parsed_Input; Through : Q.Byte_Count; State : out Fold_State;
      Result : out Observation)
   is
      History : A.R.Retained_Events (1 .. Value.Decoded_Event_Count) := (others => Blank);
      Proof : OJ.Journal_Proof;
   begin
      Fold_Prefix (Value, Through, State, History, Proof, Result);
   end Fold_Prefix;
   procedure Fold (Value : I.Parsed_Input; State : out Fold_State;
                   Proof : out OJ.Journal_Proof; Result : out Observation) is
      History : A.R.Retained_Events (1 .. Value.Decoded_Event_Count) := (others => Blank);
   begin
      Fold_Prefix (Value, Value.Decoded_Event_Count, State, History, Proof, Result);
   end Fold;
   procedure Fold (Value : I.Parsed_Input; State : out Fold_State;
                   History : in out A.R.Retained_Events; Proof : out OJ.Journal_Proof;
                   Result : out Observation) is
   begin
      Fold_Prefix (Value, Value.Decoded_Event_Count, State, History, Proof, Result);
   end Fold;

   function Finish_Load
     (Value : I.Parsed_Input; State : Fold_State; Proof : OJ.Journal_Proof;
      Folded : Observation) return Observation
   is
      Result : Observation := Folded;
   begin
      if Result.State /= History_Folded then return Result; end if;
      declare
         Native : ER.Scoped_Replay_Result;
         Owner_Matches, Contains_Unknown : Boolean;
         Current_Matches, Preparations_Done : Boolean;
         Head : OJ.Head_Disposition;
      begin
         OC.Context_Decide (Value, Owner_Matches, Native, Contains_Unknown);
         if not Owner_Matches then return (Fold_Refused, Owner_Roster_Refused, 0); end if;
         OJ.Startup_Decide (Value, Proof, Current_Matches, Head, Preparations_Done);
         if not Current_Matches or else Head = OJ.Refused then
            return (Fold_Refused, Owner_Roster_Refused, 0);
         end if;
         if Native.State /= ER.Native_Redecided or else
            (Native.Roster_Entry = ER.Validate_Entry and then Native.Native_Status /= 1) or else
            (Native.Roster_Entry = ER.Check_Entry and then Native.Native_Status /=
               Interfaces.Unsigned_32 (ER.S.Status'Pos (ER.S.Ready))) or else
            Native.Roster_Entry = ER.Classify_Entry then
            return (Fold_Refused, Join_Not_Ready, 0);
         end if;
         if Contains_Unknown or else
            (for some Root of State.Roots (1 .. State.Root_Count) => Root.Phase = M.Unknown)
         then Result.Reason := Retain_Unknown;
         elsif Head /= OJ.Stable or else not Preparations_Done
         then Result.Reason := Recover_Retained;
         elsif (State.Logical_S0 or else State.Roots (State.Current).Phase = M.Front_Owned)
            and then State.Roots (State.Current).Owners_Open and then
            Worldline.Startup_Admission.All_Required_Admissions_Consumed (Value)
         then Result.Reason := Front_Startup;
         else Result.Reason := Recover_Retained;
         end if;
      end;
      return Result;
   end Finish_Load;
   function Load_Decide (Value : I.Parsed_Input) return Observation is
      State : Fold_State (Q.Byte_Count'Max (1, Value.Root_Count), Value.Subject_Count);
      Result : Observation;
      Proof : OJ.Journal_Proof;
   begin
      Fold (Value, State, Proof, Result);
      return Finish_Load (Value, State, Proof, Result);
   end Load_Decide;
   function Load_Decide
     (Value : I.Parsed_Input; Owner_Context : OJ.O.Prepared_History;
      Resource_Context : OJ.K.Prepared_History) return Observation
   is
      State : Fold_State (Q.Byte_Count'Max (1, Value.Root_Count), Value.Subject_Count);
      History : A.R.Retained_Events (1 .. Value.Decoded_Event_Count) := (others => Blank);
      Result : Observation;
      Initial_Proof, Proof : OJ.Journal_Proof;
   begin
      OJ.Establish (Value, Owner_Context, Resource_Context, Initial_Proof);
      if not OJ.Established (Value, Initial_Proof) then
         return (Fold_Refused, Owner_Roster_Refused, 0);
      end if;
      Fold_Prefix_Core (Value, Value.Decoded_Event_Count, State, History,
                        Proof, Result, Initial_Proof);
      return Finish_Load (Value, State, Proof, Result);
   end Load_Decide;
end Worldline.Custody_V2_Fold_Engine;

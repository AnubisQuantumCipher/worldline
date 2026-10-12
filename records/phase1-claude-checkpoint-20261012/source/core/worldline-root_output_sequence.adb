with Canonical_Artifacts;
with Worldline.Operation_Archive;
with Worldline.Retained_Evidence_Replay;
with Worldline.Emitter_Ordinal;
with Worldline.Custody_V2_Mutation_Decision;
with Worldline.Emitter_Channel_Evidence;
package body Worldline.Root_Output_Sequence with SPARK_Mode is
   package V renames I.V;
   package S renames V.S;
   package A renames Worldline.Operation_Archive;
   package R renames Worldline.Retained_Evidence_Replay;
   package O renames Worldline.Emitter_Ordinal;
   package C renames Canonical_Artifacts;
   package MD renames Worldline.Custody_V2_Mutation_Decision;
   package CE renames Worldline.Emitter_Channel_Evidence;
   use type E.Span;
   use type E.Bytes;
   use type E.Value_Kind;
   use type Q.Byte;
   use type C.JSON_Kind;
   use type C.Genesis_Correspondence;
   use type M.Subject_Kind;
   use type M.Transfer_Mode;
   function F (Data : E.Bytes; Item : E.Span; Name : String) return E.Span
      renames R.Archive_Field;
   function Equal_Bytes (Left_Data, Right_Data : E.Bytes; Left, Right : E.Span)
      return Boolean is
     (C.P.Valid (Left_Data, Left) and then C.P.Valid (Right_Data, Right) and then
      Left.Length = Right.Length and then
      (for all K in E.Count range 1 .. Left.Length =>
         Left_Data (Left.First + K - 1) = Right_Data (Right.First + K - 1)));
   function Text_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return A.Valid (Data, Item) and then View.Form = E.Text_Value and then
         E.Bytes_Valid (Data, View.Payload);
   end Text_Valid;
   function Text (Data : E.Bytes; Item : E.Span) return E.Bytes is
     (E.Materialize (Data, E.Decode (Data, Item, E.Operation).Payload))
      with Pre => Text_Valid (Data, Item);
   function Object_Size (Data : E.Bytes; Item : E.Span; Count : E.Count)
      return Boolean is
      View : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return A.Valid (Data, Item) and then View.Form = E.Object_Value and then
         E.Array_Length (Data, View.Children) = Count;
   end Object_Size;
   function Scope_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
   begin
      return Object_Size (Data, Item, 6) and then
         R.Archive_Bytes_Valid (Data, F (Data, Item, "generation")) and then
         (Text_Valid (Data, F (Data, Item, "root_operation")) or else
          R.Archive_Is_None (Data, F (Data, Item, "root_operation"))) and then
         Text_Valid (Data, F (Data, Item, "operation")) and then
         Text_Valid (Data, F (Data, Item, "request")) and then
         R.Archive_Bytes_Valid (Data, F (Data, Item, "subgeneration")) and then
         R.Archive_Bytes_Valid (Data, F (Data, Item, "reattach_epoch"));
   end Scope_Valid;
   function Same_Natural (Left_Data, Right_Data : E.Bytes; Left, Right : E.Span)
      return Boolean is
   begin
      if not R.Archive_Bytes_Valid (Left_Data, Left) or else
         not R.Archive_Bytes_Valid (Right_Data, Right) then return False; end if;
      return O.Same_Value (R.Archive_Bytes (Left_Data, Left),
                           R.Archive_Bytes (Right_Data, Right));
   end Same_Natural;
   function Same_Scope (Left_Data, Right_Data : E.Bytes; Left, Right : E.Span)
      return Boolean is
   begin
      return Scope_Valid (Left_Data, Left) and then Scope_Valid (Right_Data, Right) and then
         Same_Natural (Left_Data, Right_Data, F (Left_Data, Left, "generation"),
                        F (Right_Data, Right, "generation")) and then
         Same_Natural (Left_Data, Right_Data, F (Left_Data, Left, "subgeneration"),
                        F (Right_Data, Right, "subgeneration")) and then
         Equal_Bytes (Left_Data, Right_Data, F (Left_Data, Left, "root_operation"),
                       F (Right_Data, Right, "root_operation")) and then
         Equal_Bytes (Left_Data, Right_Data, F (Left_Data, Left, "operation"),
                       F (Right_Data, Right, "operation")) and then
         Equal_Bytes (Left_Data, Right_Data, F (Left_Data, Left, "request"),
                       F (Right_Data, Right, "request"));
   end Same_Scope;
   function Unsigned_LE (Left, Right : E.Bytes) return Boolean is
      L : E.Count := Left'Length;
      R_Length : E.Count := Right'Length;
   begin
      while L > 0 and then Left (Left'First + L - 1) = 0 loop
         pragma Loop_Variant (Decreases => L);
         L := L - 1;
      end loop;
      while R_Length > 0 and then Right (Right'First + R_Length - 1) = 0 loop
         pragma Loop_Variant (Decreases => R_Length);
         R_Length := R_Length - 1;
      end loop;
      if L /= R_Length then return L < R_Length; end if;
      while L > 0 loop
         pragma Loop_Variant (Decreases => L);
         if Left (Left'First + L - 1) /= Right (Right'First + L - 1) then
            return Left (Left'First + L - 1) < Right (Right'First + L - 1);
         end if;
         L := L - 1;
      end loop;
      return True;
   end Unsigned_LE;
   function Digest_Matches (Data : E.Bytes; Line, Digest : E.Span) return Boolean is
      Hex_Digits : constant String := "0123456789abcdef";
   begin
      if not R.Archive_Bytes_Valid (Data, Line) or else not Text_Valid (Data, Digest)
      then return False; end if;
      declare
         Raw : constant E.Bytes := R.Archive_Bytes (Data, Line);
         Hex : constant E.Bytes := Text (Data, Digest);
         Hash : constant I.C.SHA.Digest := I.C.G.Hash (Raw, (Raw'First, Raw'Length));
      begin
         if Hex'Length /= Hash'Length * 2 then return False; end if;
         for K in Hash'Range loop
            pragma Loop_Variant (Increases => K);
            if Hex (Hex'First + E.Count (K - Hash'First) * 2) /=
               Character'Pos (Hex_Digits (1 + Natural (Hash (K) / 16))) or else
               Hex (Hex'First + E.Count (K - Hash'First) * 2 + 1) /=
               Character'Pos (Hex_Digits (1 + Natural (Hash (K) mod 16))) then return False; end if;
         end loop;
         return True;
      end;
   end Digest_Matches;
   function JSON_Members (Data : E.Bytes; Item : E.Span) return E.Count is
      Node : constant C.JSON_Node := C.JSON_Prefix (Data, Item, 0);
      Offset : E.Count := 1;
      Count : E.Count := 0;
      Key, Child : C.JSON_Node;
   begin
      if not Node.Valid or else Node.After /= Item.Length or else
         Node.Form /= C.Object_JSON_Value then return 0; end if;
      while Offset < Item.Length - 1 loop
         pragma Loop_Variant (Decreases => Item.Length - Offset);
         Key := C.JSON_Prefix (Data, Item, Offset);
         if not Key.Valid or else Key.After >= Item.Length then return 0; end if;
         Child := C.JSON_Prefix (Data, Item, Key.After + 1);
         if not Child.Valid or else Child.After <= Offset then return 0; end if;
         Count := Count + 1;
         Offset := Child.After;
         if Offset < Item.Length - 1 then Offset := Offset + 1; end if;
      end loop;
      return Count;
   end JSON_Members;
   function Line_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
      Progress : constant Boolean := R.Archive_Text_Is (Data, F (Data, Item, "type"), "PROGRESS_BYTES");
   begin
      if not R.Archive_Bytes_Valid (Data, F (Data, Item, "line")) then return False; end if;
      declare
         Raw : constant E.Bytes := R.Archive_Bytes (Data, F (Data, Item, "line"));
      begin
         if Raw'Length = 0 or else Raw (Raw'Last) /= 10 then return False; end if;
         declare
            Image : constant E.Span := (Raw'First, Raw'Length - 1);
         begin
            return C.Canonical_JSON_Valid (Raw, Image) and then
               JSON_Members (Raw, Image) = (if Progress then 3 else 4) and then
               C.Canonical_JSON_Field (Raw, Image, "id").Length > 0 and then
               (if Progress then
                  C.Canonical_JSON_Field (Raw, Image, "event").Length > 0 and then
                  C.Canonical_JSON_Field (Raw, Image, "data").Length > 0
                else C.Canonical_JSON_Field (Raw, Image, "ok").Length > 0 and then
                  C.Canonical_JSON_Field (Raw, Image, "result").Length > 0 and then
                  C.Canonical_JSON_Field (Raw, Image, "error").Length > 0);
         end;
      end;
   end Line_Valid;
   function Line_Request_Joined
     (Value : I.Parsed_Input; Index : E.Count; Item_Data : E.Bytes; Item : E.Span)
      return Boolean is
      Data : E.Bytes renames Value.Arena;
   begin
      if Index not in Value.Events'Range or else not R.Archive_Bytes_Valid
         (Item_Data, F (Item_Data, Item, "line")) then return False; end if;
      declare
         X5 : constant E.Span := F (Data, Value.Events (Index).Record_Archive, "x5");
         Request : constant E.Span := F (Data, F (Data, X5, "subject_evidence"), "request");
         Raw : constant E.Bytes := R.Archive_Bytes (Item_Data, F (Item_Data, Item, "line"));
      begin
         if Raw'Length = 0 or else Raw (Raw'Last) /= 10 then return False; end if;
         return C.Scoped_Archive_JSON_Matches (Raw, Data,
            C.Canonical_JSON_Field (Raw, (Raw'First, Raw'Length - 1), "id"),
            F (Data, Request, "requestId")) = C.Typed_Tree_Matches_Source_Custody_Open;
      end;
   end Line_Request_Joined;
   function Production_Valid (Data : E.Bytes; Item : E.Span; Has_Ordinal : Boolean;
                              Extra_Fields : E.Count := 0) return Boolean is
   begin
      return Object_Size (Data, Item, (if Has_Ordinal then 8 else 7) + Extra_Fields) and then
         Text_Valid (Data, F (Data, Item, "request")) and then
         Text_Valid (Data, F (Data, Item, "admission_head")) and then
         (R.Archive_Text_Is (Data, F (Data, Item, "type"), "PROGRESS_BYTES") or else
          R.Archive_Text_Is (Data, F (Data, Item, "type"), "RESPONSE_BYTES")) and then
         Digest_Matches (Data, F (Data, Item, "line"), F (Data, Item, "sha256")) and then
         Line_Valid (Data, Item) and then A.Valid (Data, F (Data, Item, "source")) and then
         Scope_Valid (Data, F (Data, Item, "scope")) and then
         (not Has_Ordinal or else Text_Valid (Data, F (Data, Item, "out_seq")));
   end Production_Valid;
   function Sequence_Text (Data : E.Bytes; Item : E.Span) return Boolean is
   begin
      if not Text_Valid (Data, Item) then return False; end if;
      declare Digit_Bytes : constant E.Bytes := Text (Data, Item); begin
         return Digit_Bytes'Length > 0 and then
            (Digit_Bytes'Length = 1 or else Digit_Bytes (Digit_Bytes'First) /= Character'Pos ('0')) and then
            (for all B of Digit_Bytes => B in Character'Pos ('0') .. Character'Pos ('9'));
      end;
   end Sequence_Text;
   function Value_At_Most (Data : E.Bytes; Item : E.Span; Maximum : E.Count)
      return V.Count_Result is
      Value : E.Count := 0;
   begin
      if not R.Archive_Integer_Valid (Data, Item) or else
         R.Archive_Integer_Negative (Data, Item) then return (Present => False); end if;
      declare Bytes : constant E.Bytes := R.Archive_Integer_Magnitude (Data, Item); begin
         for K in reverse Bytes'Range loop
            pragma Loop_Variant (Decreases => K);
            pragma Loop_Invariant (Value <= Maximum);
            if E.Count (Bytes (K)) > Maximum or else
               Value > (Maximum - E.Count (Bytes (K))) / 256 then return (Present => False); end if;
            Value := Value * 256 + E.Count (Bytes (K));
         end loop;
      end;
      return (Present => True, Value => Value);
   end Value_At_Most;
   function Write_Wait_Valid (Data : E.Bytes; Part : E.Span) return Boolean is
      Wait : constant E.Span := F (Data, Part, "wait");
   begin
      if not R.Archive_Is_Sequence (Data, Wait) or else
         R.Archive_Length (Data, Wait) /= 1 then return False; end if;
      declare
         Poll : constant E.Span := R.Archive_Index (Data, Wait, 0);
         Events : constant E.Span := F (Data, Poll, "events");
      begin
         if not Object_Size (Data, Poll, 3) or else
            not R.Archive_Text_Is (Data, F (Data, Poll, "call"), "poll") or else
            not Equal_Bytes (Data, Data, F (Data, Poll, "source"), F (Data, Part, "source")) or else
            not R.Archive_Is_Sequence (Data, Events) then return False; end if;
         for K in E.Count range 1 .. R.Archive_Length (Data, Events) loop
            pragma Loop_Variant (Increases => K);
            declare
               Event : constant E.Span := R.Archive_Index (Data, Events, K - 1);
               Flags : constant E.Span := R.Archive_Index (Data, Event, 1);
            begin
               if not R.Archive_Is_Sequence (Data, Event) or else
                  R.Archive_Length (Data, Event) /= 2 or else
                  not Equal_Bytes (Data, Data, R.Archive_Index (Data, Event, 0), F (Data, Part, "fd")) or else
                  not R.Archive_Integer_Valid (Data, Flags) or else
                  R.Archive_Integer_Negative (Data, Flags) then return False; end if;
            end;
         end loop;
         return True;
      end;
   end Write_Wait_Valid;
   function Writes_Complete (Ack_Data, Produced_Data : E.Bytes;
                             Ack, Produced : E.Span) return Boolean is
      Writes : constant E.Span := F (Ack_Data, Ack, "write");
      Through : E.Count := 0;
      FD : E.Span := (1, 0);
   begin
      if not R.Archive_Is_Sequence (Ack_Data, Writes) or else
         not R.Archive_Bytes_Valid (Produced_Data, F (Produced_Data, Produced, "line"))
      then return False; end if;
      declare
         Whole : constant E.Bytes := R.Archive_Bytes (Produced_Data, F (Produced_Data, Produced, "line"));
      begin
         for K in E.Count range 1 .. R.Archive_Length (Ack_Data, Writes) loop
            pragma Loop_Variant (Increases => K);
            pragma Loop_Invariant (Through <= Whole'Length);
            -- The actual writer stops at the complete line. A later receipt
            -- cannot describe another call in this same successful write.
            if Through = Whole'Length then return False; end if;
            declare
               Part : constant E.Span := R.Archive_Index (Ack_Data, Writes, K - 1);
               Offered : constant E.Span := F (Ack_Data, Part, "offered");
               Raw : constant E.Span := F (Ack_Data, Part, "raw");
               Result : constant E.Span := F (Ack_Data, Part, "result");
               Errno : constant E.Span := F (Ack_Data, Part, "errno");
               Wait : constant E.Span := F (Ack_Data, Part, "wait");
               Count : constant V.Count_Result := Value_At_Most (Ack_Data, Result, Whole'Length - Through);
            begin
               if not Object_Size (Ack_Data, Part, (if Wait.Length > 0 then 8 else 7)) or else
                  not R.Archive_Text_Is (Ack_Data, F (Ack_Data, Part, "call"), "write") or else
                  not R.Archive_Integer_Valid (Ack_Data, F (Ack_Data, Part, "fd")) or else
                  not Equal_Bytes (Ack_Data, Ack_Data, F (Ack_Data, Part, "source"), F (Ack_Data, Ack, "source")) or else
                  not R.Archive_Bytes_Valid (Ack_Data, Offered) then return False; end if;
               if K = 1 then FD := F (Ack_Data, Part, "fd");
               elsif not Equal_Bytes (Ack_Data, Ack_Data, FD, F (Ack_Data, Part, "fd")) then return False; end if;
               declare Offered_Bytes : constant E.Bytes := R.Archive_Bytes (Ack_Data, Offered); begin
                  if Offered_Bytes'Length /= Whole'Length - Through or else
                     not (for all N in E.Count range 1 .. Offered_Bytes'Length =>
                        Offered_Bytes (Offered_Bytes'First + N - 1) = Whole (Whole'First + Through + N - 1))
                  then return False; end if;
               end;
               if not Count.Present then
                  if not R.Archive_Integer_Valid (Ack_Data, Result) or else
                     not R.Archive_Integer_Negative (Ack_Data, Result) or else
                     not O.Same_Value (R.Archive_Integer_Magnitude (Ack_Data, Result), (1 => 1)) or else
                     not R.Archive_Is_None (Ack_Data, Raw) or else
                     not R.Archive_Integer_Valid (Ack_Data, Errno) or else
                     R.Archive_Integer_Negative (Ack_Data, Errno) or else
                     O.Same_Value (R.Archive_Integer_Magnitude (Ack_Data, Errno), (1 => 0))
                  then return False; end if;
                  -- Only the actual BlockingIOError branch retries. A bare
                  -- OSError receipt aborts and cannot produce a written ACK.
                  if Wait.Length = 0 or else not Write_Wait_Valid (Ack_Data, Part) then return False; end if;
               else
                  if Count.Value = 0 or else Wait.Length > 0 or else not R.Archive_Integer_Valid (Ack_Data, Errno) or else
                     R.Archive_Integer_Negative (Ack_Data, Errno) or else
                     not O.Same_Value (R.Archive_Integer_Magnitude (Ack_Data, Errno), (1 => 0)) or else
                     not R.Archive_Bytes_Valid (Ack_Data, Raw) then return False; end if;
                  declare Actual : constant E.Bytes := R.Archive_Bytes (Ack_Data, Raw); begin
                     if Actual'Length /= Count.Value or else
                        not (for all N in E.Count range 1 .. Actual'Length =>
                           Actual (Actual'First + N - 1) = Whole (Whole'First + Through + N - 1))
                     then return False; end if;
                  end;
                  Through := Through + Count.Value;
               end if;
            end;
         end loop;
         return Through = Whole'Length;
      end;
   end Writes_Complete;
   function Replay_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
      Relay : constant E.Span := F (Data, Item, "relay");
   begin
      return Production_Valid (Data, Item, True, (if Relay.Length > 0 then 2 else 1)) and then
         Sequence_Text (Data, F (Data, Item, "out_seq")) and then
         Scope_Valid (Data, F (Data, Item, "production_scope")) and then
         Same_Scope (Data, Data, F (Data, Item, "scope"), F (Data, Item, "production_scope")) and then
         (Relay.Length = 0 or else A.Valid (Data, Relay));
   end Replay_Valid;
   function Replay_Matches (Produced_Data, Candidate_Data : E.Bytes;
                            Produced, Candidate : E.Span) return Boolean is
   begin
      return Equal_Bytes (Produced_Data, Candidate_Data, F (Produced_Data, Produced, "request"), F (Candidate_Data, Candidate, "request")) and then
         Equal_Bytes (Produced_Data, Candidate_Data, F (Produced_Data, Produced, "admission_head"), F (Candidate_Data, Candidate, "admission_head")) and then
         Equal_Bytes (Produced_Data, Candidate_Data, F (Produced_Data, Produced, "type"), F (Candidate_Data, Candidate, "type")) and then
         Equal_Bytes (Produced_Data, Candidate_Data, F (Produced_Data, Produced, "line"), F (Candidate_Data, Candidate, "line")) and then
         Equal_Bytes (Produced_Data, Candidate_Data, F (Produced_Data, Produced, "sha256"), F (Candidate_Data, Candidate, "sha256")) and then
         Equal_Bytes (Produced_Data, Candidate_Data, F (Produced_Data, Produced, "out_seq"), F (Candidate_Data, Candidate, "out_seq")) and then
         Equal_Bytes (Produced_Data, Candidate_Data, F (Produced_Data, Produced, "scope"), F (Candidate_Data, Candidate, "production_scope"));
   end Replay_Matches;
   function Written_Valid (Data : E.Bytes; Item : E.Span)
      return Boolean is
      Relay : constant E.Span := F (Data, Item, "relay");
   begin
      return Object_Size (Data, Item, 9 + (if Relay.Length > 0 then 1 else 0)) and then
         Text_Valid (Data, F (Data, Item, "request")) and then
         Text_Valid (Data, F (Data, Item, "admission_head")) and then
         R.Archive_Text_Is (Data, F (Data, Item, "type"), "RESPONSE_WRITTEN") and then
         Sequence_Text (Data, F (Data, Item, "out_seq")) and then
         Text_Valid (Data, F (Data, Item, "sha256")) and then
         R.Archive_Is_Sequence (Data, F (Data, Item, "write")) and then
         A.Valid (Data, F (Data, Item, "source")) and then
         Same_Scope (Data, Data, F (Data, Item, "scope"), F (Data, Item, "production_scope")) and then
         (Relay.Length = 0 or else A.Valid (Data, Relay));
   end Written_Valid;
   function Raw_Text_Is (Data : E.Bytes; Item : E.Span; Text : String) return Boolean is
     (C.P.Valid (Data, Item) and then Item.Length = Text'Length and then
      (for all K in Text'Range => Data (Item.First + E.Count (K - Text'First)) = Character'Pos (Text (K))));
   procedure Next_Output (Data : E.Bytes; Output : out E.Bytes;
                          Result : out Output_Observation) is
   begin
      MD.Output_Next (Data, Output, Result);
   end Next_Output;
   procedure Replay_Output (Data : E.Bytes; Output : out E.Bytes;
                            Result : out Output_Observation) is
   begin
      MD.Output_Replay (Data, Output, Result);
   end Replay_Output;
   procedure Written_Output (Data : E.Bytes; Output : out E.Bytes;
                             Result : out Output_Observation) is
   begin
      MD.Output_Written (Data, Output, Result);
   end Written_Output;
   procedure Prefix_Output (Data : E.Bytes; Output : out E.Bytes;
                            Result : out Output_Observation) is
   begin
      MD.Output_Prefix (Data, Output, Result);
   end Prefix_Output;
   procedure Evaluate
     (Value : I.Parsed_Input; Index : Q.Byte_Count; Before : M.Root_State;
      Subjects : M.Subject_State_Array; Subject : P.Optional_Subject;
      Proof : J.Journal_Proof; Query : Query_Kind; Output : out E.Bytes;
      Result : out Output_Observation)
   is
      Data : E.Bytes renames Value.Arena;
   begin
      Output := (others => 0);
      Result := (others => <>);
      if Index not in Value.Events'Range or else not Subject.Present or else
         Subject.Value.Kind /= M.Request or else not J.Established (Value, Proof) or else
         not J.Authenticated (Value, Index, Proof) then return; end if;
      declare
         X5 : constant E.Span := F (Data, Value.Events (Index).Record_Archive, "x5");
         Emitter : constant E.Span := F (Data, X5, "emitter");
      begin
         if not S.Valid (Data, Emitter) or else S.Member_Count (Data, Emitter) /= 2 or else
            not V.Valid_Hex_Field (Data, Emitter, "records") or else
            not V.Valid_Hex_Field (Data, Emitter, "candidate") then return; end if;
         declare
            Records_Data : constant E.Bytes := V.Hex_Value (Data, Emitter, "records");
            Candidate_Data : constant E.Bytes := V.Hex_Value (Data, Emitter, "candidate");
            Records : constant E.Span := (Records_Data'First, Records_Data'Length);
            Candidate : constant E.Span := (Candidate_Data'First, Candidate_Data'Length);
            Scope : constant E.Span := F (Candidate_Data, Candidate, "scope");
            Record_Count : constant E.Count := R.Archive_Length (Records_Data, Records);
            Capacity : E.Count := 1;
            Context : constant E.Span := F (Data, Value.Owner_Roster, "operation_context");
            Events : constant E.Span := F (Data, F (Data, Context, "journal"), "events");
            Reference : Boolean := False;
         begin
            if not A.Valid (Records_Data, Records) or else
               E.Decode (Records_Data, Records, E.Operation).Form /= E.Tuple_Value or else
               not A.Valid (Candidate_Data, Candidate) or else not Scope_Valid (Candidate_Data, Scope)
            then return; end if;
            if Query = Allocate then
               Reference := SE.Output_Reference (Value, Index, Before, Subjects, Subject, Proof);
               if not Production_Valid (Candidate_Data, Candidate, False) or else
                  not Line_Request_Joined (Value, Index, Candidate_Data, Candidate) then return; end if;
            elsif Query = Replay then
               Reference := CE.Frame_Reference (Value, Index, Before, Subjects, Subject, Proof,
                                                Candidate_Data, Candidate);
               if not Replay_Valid (Candidate_Data, Candidate) then return; end if;
            elsif Query = Observe_Written then
               Reference := CE.Prefix_Reference (Value, Index, Before, Subjects, Subject, Proof,
                                                 Candidate_Data, Candidate);
            end if;
            if Query /= Confirm_Written and then not Reference then return; end if;
            -- An extent is taken from complete decimal encodings, never from a
            -- fixed numerical word. One more byte accommodates the successor.
            for K in E.Count range 1 .. Record_Count loop
               pragma Loop_Variant (Increases => K);
               declare Item : constant E.Span := R.Archive_Index (Records_Data, Records, K - 1); begin
                  if not Production_Valid (Records_Data, Item, True) or else
                     not Sequence_Text (Records_Data, F (Records_Data, Item, "out_seq")) then return; end if;
                  if Same_Scope (Records_Data, Candidate_Data, F (Records_Data, Item, "scope"), Scope) then
                     Capacity := E.Count'Max (Capacity, Text (Records_Data, F (Records_Data, Item, "out_seq"))'Length);
                  end if;
               end;
            end loop;
            if Capacity = E.Count'Last then return; end if;
            Capacity := Capacity + 1;
            declare
               Extent : constant E.Count := Capacity;
               A_Magnitude, B_Magnitude, A_Written, B_Written : E.Bytes (1 .. Extent) := (others => 0);
               Selected : E.Bytes (1 .. Extent) := (others => 0);
               Use_A, Written_A : Boolean := True;
               Used, Written_Used, Selected_Used : E.Count := 1;
               Seen : E.Count := 0;
               Previous, Last_Epoch : E.Span := (1, 0);
               Validated_Boundaries : E.Span := (1, 0);
               Validated_Through : E.Count := 0;
               Selected_Record : E.Span := (1, 0);
               Good : Boolean := True;
               function Ordinal_Matches (Item_Data : E.Bytes; Item : E.Span;
                                         Written : Boolean := False) return Boolean is
               begin
                  if not Sequence_Text (Item_Data, Item) then return False; end if;
                  declare Digit_Bytes : constant E.Bytes := Text (Item_Data, Item); begin
                     if Written then
                        if Written_A then return O.Canonical_Decimal_Matches (Digit_Bytes, A_Written (1 .. Written_Used));
                        else return O.Canonical_Decimal_Matches (Digit_Bytes, B_Written (1 .. Written_Used)); end if;
                     elsif Use_A then return O.Canonical_Decimal_Matches (Digit_Bytes, A_Magnitude (1 .. Used));
                     else return O.Canonical_Decimal_Matches (Digit_Bytes, B_Magnitude (1 .. Used)); end if;
                  end;
               end Ordinal_Matches;
               -- One procedure per counter: the written ordinal and the
               -- produced magnitude advance through disjoint buffer pairs.
               procedure Advance_Written is
                  Needed : E.Count;
                  Complete : Boolean;
               begin
                  if Written_A then O.Successor (A_Written (1 .. Written_Used), B_Written, Needed, Complete);
                  else O.Successor (B_Written (1 .. Written_Used), A_Written, Needed, Complete); end if;
                  Written_A := not Written_A;
                  Written_Used := Needed;
                  Good := Good and then Complete;
               end Advance_Written;
               procedure Advance is
                  Needed : E.Count;
                  Complete : Boolean;
               begin
                  if Use_A then O.Successor (A_Magnitude (1 .. Used), B_Magnitude, Needed, Complete);
                  else O.Successor (B_Magnitude (1 .. Used), A_Magnitude, Needed, Complete); end if;
                  Use_A := not Use_A;
                  Used := Needed;
                  Good := Good and then Complete;
               end Advance;
               procedure Remember (Item : E.Span) is
               begin
                  Selected_Record := Item; Selected_Used := Used;
                  for K in E.Count range 1 .. Used loop
                     pragma Loop_Variant (Increases => K);
                     Selected (K) := (if Use_A then A_Magnitude (K) else B_Magnitude (K));
                  end loop;
               end Remember;
               function Produced_For (Ack_Data : E.Bytes; Ack : E.Span) return E.Span is
                  Found : E.Span := (1, 0);
               begin
                  for K in E.Count range 1 .. Seen loop
                     pragma Loop_Variant (Increases => K);
                     declare Item : constant E.Span := R.Archive_Index (Records_Data, Records, K - 1); begin
                        if Same_Scope (Records_Data, Ack_Data, F (Records_Data, Item, "scope"),
                                        F (Ack_Data, Ack, "production_scope")) and then
                           Equal_Bytes (Records_Data, Ack_Data, F (Records_Data, Item, "out_seq"),
                                        F (Ack_Data, Ack, "out_seq")) then
                           if Found.Length > 0 then return (1, 0); end if;
                           Found := Item;
                        end if;
                     end;
                  end loop;
                  return Found;
               end Produced_For;
               function Prior_Ack (Ack_Data : E.Bytes; Ack : E.Span) return Boolean is
               begin
                  for K in E.Count range 1 .. Validated_Through loop
                     pragma Loop_Variant (Increases => K);
                     declare Boundary : constant E.Span := V.Element (Data, Validated_Boundaries, K - 1); begin
                        if S.Text_Is (Data, F (Data, Boundary, "name"), "REQUEST_OUTPUT_WRITTEN") and then
                           V.Valid_Hex_Field (Data, Boundary, "value") then
                           declare
                              Raw : constant E.Bytes := V.Hex_Value (Data, Boundary, "value");
                              Image : constant E.Span := (Raw'First, Raw'Length);
                           begin
                              -- This cursor contains only acknowledgments
                              -- whose full native source/line/order was replayed.
                              if Same_Scope (Raw, Ack_Data, F (Raw, Image, "scope"), F (Ack_Data, Ack, "scope")) and then
                                 Equal_Bytes (Raw, Ack_Data, F (Raw, Image, "out_seq"), F (Ack_Data, Ack, "out_seq")) then return True; end if;
                           end;
                        elsif S.Text_Is (Data, F (Data, Boundary, "name"), "REQUEST_OUTPUT_PEER_STATUS") and then
                           V.Valid_Hex_Field (Data, Boundary, "value") then
                           declare
                              Raw : constant E.Bytes := V.Hex_Value (Data, Boundary, "value");
                              Image : constant E.Span := (Raw'First, Raw'Length);
                              Prefix : constant E.Span := F (Raw, Image, "written");
                           begin
                              -- An earlier fully redecided PEER_STATUS retains
                              -- the actual writes, never merely a claimed count.
                              for N in E.Count range 1 .. R.Archive_Length (Raw, Prefix) loop
                                 pragma Loop_Variant (Increases => N);
                                 declare Previous_Ack : constant E.Span := R.Archive_Index (Raw, Prefix, N - 1); begin
                                    if Same_Scope (Raw, Ack_Data, F (Raw, Previous_Ack, "scope"), F (Ack_Data, Ack, "scope")) and then
                                       Equal_Bytes (Raw, Ack_Data, F (Raw, Previous_Ack, "out_seq"), F (Ack_Data, Ack, "out_seq")) then return True; end if;
                                 end;
                              end loop;
                           end;
                        end if;
                     end;
                  end loop;
                  return False;
               end Prior_Ack;
               procedure Written_Record (Ack_Data : E.Bytes; Ack : E.Span) is
                  Produced : constant E.Span := Produced_For (Ack_Data, Ack);
               begin
                  if Produced.Length = 0 or else not Written_Valid (Ack_Data, Ack) or else
                     not Equal_Bytes (Ack_Data, Records_Data, F (Ack_Data, Ack, "request"),
                                      F (Records_Data, Produced, "request")) or else
                     not Equal_Bytes (Ack_Data, Records_Data, F (Ack_Data, Ack, "admission_head"),
                                      F (Records_Data, Produced, "admission_head")) or else
                     not Equal_Bytes (Ack_Data, Records_Data, F (Ack_Data, Ack, "sha256"),
                                      F (Records_Data, Produced, "sha256")) or else
                     not Equal_Bytes (Ack_Data, Records_Data, F (Ack_Data, Ack, "production_scope"),
                                      F (Records_Data, Produced, "scope")) or else
                     not Writes_Complete (Ack_Data, Records_Data, Ack, Produced) or else
                     not CE.Acknowledgement_Reference (Value, Index, Before, Subjects, Subject, Proof,
                                                       Ack_Data, Records_Data, Ack, Produced)
                  then Good := False; return; end if;
                  if Ordinal_Matches (Ack_Data, F (Ack_Data, Ack, "out_seq"), True) then
                     Advance_Written;
                  else
                     -- Duplicate acknowledgments must refer to an earlier
                     -- genuine write, not manufacture a gap or new byte effect.
                     if not Prior_Ack (Ack_Data, Ack) then
                        Good := False; return;
                     end if;
                  end if;
               end Written_Record;
               function Worker_Prefix_Joined (Status_Data : E.Bytes; Status : E.Span)
                  return Boolean is
                  Request_Body : constant E.Span := F (Status_Data, F (Status_Data, Status, "relay"), "request_body");
                  Payload : constant E.Span := F (Status_Data, Request_Body, "payload");
               begin
                  if not R.Archive_Bytes_Valid (Status_Data, Payload) then return False; end if;
                  declare
                     Raw : constant E.Bytes := R.Archive_Bytes (Status_Data, Payload);
                     Image : constant E.Span := (Raw'First, Raw'Length);
                     Written : constant E.Span := F (Raw, Image, "written");
                     Seen : E.Count := 0;
                  begin
                     if not Object_Size (Raw, Image, 1) or else
                        not R.Archive_Is_Sequence (Raw, Written) then return False; end if;
                     -- PEER_HELD contains the actual worker's retained ACK
                     -- prefix at send time, not the different Front report
                     -- profiles and not a count. Authenticate its order against
                     -- the already redecided original journal. Later ACKs may
                     -- have arrived between that genuine send and this query.
                     for K in E.Count range 1 .. Validated_Through loop
                        pragma Loop_Variant (Increases => K);
                        pragma Loop_Invariant (Seen <= R.Archive_Length (Raw, Written));
                        declare Boundary : constant E.Span := V.Element (Data, Validated_Boundaries, K - 1); begin
                           if S.Text_Is (Data, F (Data, Boundary, "name"), "REQUEST_OUTPUT_WRITTEN") and then
                              Seen < R.Archive_Length (Raw, Written) then
                              if not V.Valid_Hex_Field (Data, Boundary, "value") then return False; end if;
                              declare
                                 Previous : constant E.Bytes := V.Hex_Value (Data, Boundary, "value");
                                 Written_Entry : constant E.Span := R.Archive_Index (Raw, Written, Seen);
                              begin
                                 if not Equal_Bytes (Previous, Raw, (Previous'First, Previous'Length), Written_Entry)
                                 then return False; end if;
                              end;
                              Seen := Seen + 1;
                           end if;
                        end;
                     end loop;
                     return Seen = R.Archive_Length (Raw, Written);
                  end;
               end Worker_Prefix_Joined;
               procedure Written_Prefix (Prefix_Data : E.Bytes; Prefix : E.Span) is
                  Prior_Written : constant E.Bytes :=
                    (if Written_A then A_Written (1 .. Written_Used)
                     else B_Written (1 .. Written_Used));
               begin
                  if not R.Archive_Is_Sequence (Prefix_Data, Prefix) then Good := False; return; end if;
                  -- Derive the complete prefix from actual writes, starting at
                  -- zero. Previously authenticated knowledge is a lower bound,
                  -- never a replacement for any presented write's full proof.
                  A_Written (1) := 0;
                  Written_A := True;
                  Written_Used := 1;
                  for K in E.Count range 1 .. R.Archive_Length (Prefix_Data, Prefix) loop
                     pragma Loop_Variant (Increases => K);
                     declare Ack : constant E.Span := R.Archive_Index (Prefix_Data, Prefix, K - 1); begin
                        -- A full prefix has exactly one actual ACK at each
                        -- ordinal. Duplicate or unordered entries cannot use
                        -- the journal's idempotent single-ACK path.
                        if not Ordinal_Matches (Prefix_Data, F (Prefix_Data, Ack, "out_seq"), True)
                        then Good := False; return; end if;
                        Written_Record (Prefix_Data, Ack);
                        if not Good then return; end if;
                     end;
                  end loop;
                  if Written_A then
                     Good := Good and then Unsigned_LE (Prior_Written, A_Written (1 .. Written_Used));
                  else
                     Good := Good and then Unsigned_LE (Prior_Written, B_Written (1 .. Written_Used));
                  end if;
               end Written_Prefix;
               procedure Peer_Status_Record (Status_Data : E.Bytes; Status : E.Span) is
                  Written : constant E.Span := F (Status_Data, Status, "written");
                  Relay : constant E.Span := F (Status_Data, Status, "relay");
                  Response_Body : constant E.Span := F (Status_Data, Relay, "response_body");
                  Payload : constant E.Span := F (Status_Data, Response_Body, "payload");
               begin
                  if not Object_Size (Status_Data, Status, 7) or else
                     not R.Archive_Text_Is (Status_Data, F (Status_Data, Status, "type"), "PEER_STATUS") or else
                     not Same_Scope (Status_Data, Candidate_Data, F (Status_Data, Status, "scope"), Scope) or else
                     not R.Archive_Is_Sequence (Status_Data, Written) or else
                     not R.Archive_Text_Is (Status_Data, F (Status_Data, Response_Body, "type"), "PEER_STATUS") or else
                     not R.Archive_Bytes_Valid (Status_Data, Payload) or else
                     not Worker_Prefix_Joined (Status_Data, Status) or else
                     not CE.Frame_Reference (Value, Index, Before, Subjects, Subject, Proof, Status_Data, Status)
                  then Good := False; return; end if;
                  Written_Prefix (Status_Data, Written);
                  if not Good then return; end if;
                  declare
                     Raw : constant E.Bytes := R.Archive_Bytes (Status_Data, Payload);
                     Image : constant E.Span := (Raw'First, Raw'Length);
                  begin
                     if not Object_Size (Raw, Image, 1) or else
                        not Ordinal_Matches (Raw, F (Raw, Image, "next_out_seq"), True) or else
                        not Ordinal_Matches (Status_Data, F (Status_Data, Response_Body, "sequence"), True) then Good := False; return; end if;
                  end;
               end Peer_Status_Record;
            begin
               for Event_Ordinal in E.Count range 1 .. V.Count (Data, Events) loop
                  pragma Loop_Variant (Increases => Event_Ordinal);
                  pragma Loop_Invariant (Seen <= Record_Count);
                  declare
                     Event : constant E.Span := V.Element (Data, Events, Event_Ordinal - 1);
                     Boundaries : constant E.Span := F (Data, Event, "boundaries");
                  begin
                     if S.Text_Matches (Data, F (Data, Event, "operation"), Value.Events (Index).Operation) then
                        if not V.Is_Sequence (Data, Boundaries) or else
                           V.Count (Data, Boundaries) < V.Count (Data, Previous) then return; end if;
                        for K in E.Count range 1 .. V.Count (Data, Previous) loop
                           pragma Loop_Variant (Increases => K);
                           if not Equal_Bytes (Data, Data, V.Element (Data, Boundaries, K - 1),
                                                V.Element (Data, Previous, K - 1)) then return; end if;
                        end loop;
                        for K in E.Count range V.Count (Data, Previous) + 1 .. V.Count (Data, Boundaries) loop
                           pragma Loop_Variant (Increases => K);
                           Validated_Boundaries := Boundaries;
                           Validated_Through := K - 1;
                           declare Boundary : constant E.Span := V.Element (Data, Boundaries, K - 1); begin
                              if S.Text_Is (Data, F (Data, Boundary, "name"), "REQUEST_OUTPUT") then
                                 if Seen = Record_Count or else not V.Valid_Hex_Field (Data, Boundary, "value") then return; end if;
                                 declare
                                    Raw : constant E.Bytes := V.Hex_Value (Data, Boundary, "value");
                                    Image : constant E.Span := (Raw'First, Raw'Length);
                                    Item : constant E.Span := R.Archive_Index (Records_Data, Records, Seen);
                                    Item_Scope : constant E.Span := F (Records_Data, Item, "scope");
                                 begin
                                    if not Equal_Bytes (Raw, Records_Data, Image, Item) then return; end if;
                                    Seen := Seen + 1;
                                    if Same_Scope (Records_Data, Candidate_Data, Item_Scope, Scope) then
                                       if not Line_Request_Joined (Value, Index, Records_Data, Item) then return; end if;
                                       if not Ordinal_Matches (Records_Data, F (Records_Data, Item, "out_seq")) or else
                                          not Unsigned_LE (R.Archive_Bytes (Records_Data, F (Records_Data, Item_Scope, "reattach_epoch")),
                                                           R.Archive_Bytes (Candidate_Data, F (Candidate_Data, Scope, "reattach_epoch"))) then return; end if;
                                       if Last_Epoch.Length > 0 and then
                                          not Unsigned_LE (R.Archive_Bytes (Records_Data, Last_Epoch),
                                             R.Archive_Bytes (Records_Data, F (Records_Data, Item_Scope, "reattach_epoch"))) then return; end if;
                                       Last_Epoch := F (Records_Data, Item_Scope, "reattach_epoch");
                                       if Query = Replay and then Replay_Matches (Records_Data, Candidate_Data, Item, Candidate) then
                                          if Selected_Record.Length > 0 then return; end if;
                                          Remember (Item);
                                       end if;
                                       Advance;
                                       if not Good then return; end if;
                                    end if;
                                 end;
                              elsif S.Text_Is (Data, F (Data, Boundary, "name"), "REQUEST_OUTPUT_WRITTEN") then
                                 if not V.Valid_Hex_Field (Data, Boundary, "value") then return; end if;
                                 declare Raw : constant E.Bytes := V.Hex_Value (Data, Boundary, "value");
                                         Image : constant E.Span := (Raw'First, Raw'Length); begin
                                    if not Written_Valid (Raw, Image) then return; end if;
                                    if Same_Scope (Raw, Candidate_Data, F (Raw, Image, "scope"), Scope) then
                                       Written_Record (Raw, Image);
                                       if not Good then return; end if;
                                    end if;
                                 end;
                              elsif S.Text_Is (Data, F (Data, Boundary, "name"), "REQUEST_OUTPUT_PEER_STATUS") then
                                 if not V.Valid_Hex_Field (Data, Boundary, "value") then return; end if;
                                 declare Raw : constant E.Bytes := V.Hex_Value (Data, Boundary, "value");
                                         Image : constant E.Span := (Raw'First, Raw'Length); begin
                                    if not Object_Size (Raw, Image, 7) or else
                                       not R.Archive_Text_Is (Raw, F (Raw, Image, "type"), "PEER_STATUS") or else
                                       not Scope_Valid (Raw, F (Raw, Image, "scope")) then return; end if;
                                    if Same_Scope (Raw, Candidate_Data, F (Raw, Image, "scope"), Scope) then
                                       Peer_Status_Record (Raw, Image);
                                       if not Good then return; end if;
                                    end if;
                                 end;
                              end if;
                           end;
                        end loop;
                        Previous := Boundaries;
                        Validated_Boundaries := Boundaries;
                        Validated_Through := V.Count (Data, Boundaries);
                     end if;
                  end;
               end loop;
               if Seen /= Record_Count then return; end if;
               if Query = Confirm_Written or else Query = Observe_Written then
                  if Query = Observe_Written then
                     Written_Prefix (Candidate_Data, F (Candidate_Data, Candidate, "written"));
                  elsif R.Archive_Text_Is (Candidate_Data, F (Candidate_Data, Candidate, "type"), "PEER_STATUS") then
                     Peer_Status_Record (Candidate_Data, Candidate);
                  else Written_Record (Candidate_Data, Candidate); end if;
                  if not Good then return; end if;
                  Result := (Allocated, Index, Written_Used, 0);
                  if Written_Used <= Output'Length then
                     for K in E.Count range 1 .. Written_Used loop
                        pragma Loop_Variant (Increases => K);
                        Output (Output'First + K - 1) := (if Written_A then A_Written (K) else B_Written (K));
                     end loop;
                     Result.Written := Written_Used;
                  end if;
               elsif Query = Replay then
                  if Selected_Record.Length = 0 then return; end if;
                  declare
                     Sender : constant Boolean := Subject.Value.Mode = M.Relay and then
                        Raw_Text_Is (Data, Value.Events (Index).Actor, "WORKER");
                     function Replay_Kind return Allocation_Status is
                     begin
                        if Sender then return Allocated; end if;
                        if Written_A then
                           if O.Same_Value (Selected (1 .. Selected_Used), A_Written (1 .. Written_Used)) then return Allocated;
                           elsif Unsigned_LE (Selected (1 .. Selected_Used), A_Written (1 .. Written_Used)) then return Already_Written;
                           else return Predecessor_Pending; end if;
                        else
                           if O.Same_Value (Selected (1 .. Selected_Used), B_Written (1 .. Written_Used)) then return Allocated;
                           elsif Unsigned_LE (Selected (1 .. Selected_Used), B_Written (1 .. Written_Used)) then return Already_Written;
                           else return Predecessor_Pending; end if;
                        end if;
                     end Replay_Kind;
                     Kind : constant Allocation_Status := Replay_Kind;
                  begin
                     Result := (Kind, Index, Selected_Used, 0);
                     if Selected_Used <= Output'Length then
                        for K in E.Count range 1 .. Selected_Used loop
                           pragma Loop_Variant (Increases => K);
                           Output (Output'First + K - 1) := Selected (K);
                        end loop;
                        Result.Written := Selected_Used;
                     end if;
                  end;
               else
                  Result := (Allocated, Index, Used, 0);
                  if Used <= Output'Length then
                     for K in E.Count range 1 .. Used loop
                        pragma Loop_Variant (Increases => K);
                        Output (Output'First + K - 1) := (if Use_A then A_Magnitude (K) else B_Magnitude (K));
                     end loop;
                     Result.Written := Used;
                  end if;
               end if;
            end;
         end;
      end;
   end Evaluate;
end Worldline.Root_Output_Sequence;

package body Worldline.Custody_V2_S0_Abandon with SPARK_Mode is
   use type C.Status;
   use type D.Decode_Status;
   use type H.Status;
   use type A.Decision_Status;
   procedure Materialize_S0
     (Data : C.E.Bytes; Key, Genesis_Row, Genesis_Message, Genesis_Mac_Text : C.E.Span;
      Events : C.Event_Rows; Heads : C.Head_Rows;
      Stored_Roots : D.F.S.Root_Rows; Stored_Subjects : D.F.S.Subject_Rows;
      Alternatives : A.Alternative_Rows;
      State : in out Logical_S0; Result : out S0_Status)
   is
      Chain : constant C.Result := C.Verify
        (Data, Key, Genesis_Row, Genesis_Message, Genesis_Mac_Text, Events, Heads);
   begin
      Result := S0_Refused;
      if Chain.State /= C.Archive_Chain_Matches_Genesis_JSON_And_Fold_Open or else
         Events'Length /= 0 or else Stored_Roots'Length /= 0 or else
         Stored_Subjects'Length /= 0 or else Alternatives'Length /= 0 then return; end if;
      State := (Generation => (1 => 1), Phase => M.Front_Owned,
                Owner => M.Front, Owners_Open => True,
                Reattach_Epoch => (others => 0), Head => Chain.Origin);
      Result := Logical_S0_Archives_Match_JSON_Open;
   end Materialize_S0;

   procedure Step_Abandon
     (Data : C.E.Bytes; Key, Genesis_Row, Genesis_Message, Genesis_Mac_Text : C.E.Span;
      Raw : C.Event_Rows; Heads : C.Head_Rows; Position : Q.Byte_Index;
      Roots : in out M.Root_State_Array; Alternatives : A.Alternative_Rows;
      Expected : A.Expected_Root; Result : out Step_Status)
   is
      Proposed : constant D.Decoded_Event := D.Decode (Data, Raw (Position));
   begin
      Result := Chain_Or_Decode_Refused;
      if Proposed.Status /= D.Decoded then return; end if;
      declare
         -- Initialized scratch only, never an invented retained event: every
         -- element is overwritten by Materialize before any Legal use.
         History : A.R.Retained_Events (Raw'Range) :=
           (others => (Event => Proposed.Value, Previous => (others => 0),
             Mac => (others => 0), Record_Bytes => (Present => False),
             Base_Archive => (Present => False)));
         Observation : H.Observation;
      begin
         H.Materialize (Data, Key, Genesis_Row, Genesis_Message, Genesis_Mac_Text,
                        Raw, Heads, History, Observation);
         if Observation.State /= H.Authenticated_History_Genesis_JSON_And_Fold_Open then return; end if;
         if Proposed.Value.Kind /= M.Abandon_Event then
            Result := Wrong_Event_Family; return;
         end if;
         declare
            Decision : constant A.Decision := A.Decide
              (Data, Roots, History (Raw'First .. Position - 1),
               Alternatives, Expected, History (Position).Event);
         begin
            if Decision.Status = A.Replay_Unchanged then
               Result := Replay_Unchanged;
            elsif Decision.Status = A.Append_Abandon then
               Roots := A.Next_Abandon
                 (Data, Roots, History (Raw'First .. Position - 1),
                  Alternatives, Expected, History (Position).Event);
               Result := Abandon_Value_Applied_Prestate_Fold_Open;
            else
               Result := Semantic_Refusal;
            end if;
         end;
      end;
   end Step_Abandon;
end Worldline.Custody_V2_S0_Abandon;

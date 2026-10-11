package body Worldline.Custody_V2_Request_Step with SPARK_Mode is
   use type D.Decode_Status;
   use type H.Status;
   use type M.Event_Kind;
   procedure Apply
     (Data : C.E.Bytes; Key, Genesis_Row, Genesis_Message, Genesis_Mac_Text : C.E.Span;
      Raw : C.Event_Rows; Heads : C.Head_Rows; Position : Q.Byte_Index;
      Roots : in out M.Root_State_Array; Subjects : in out M.Subject_State_Array;
      Alternatives : A.Alternative_Rows; Root : A.Expected_Root;
      Expected : RA.Expected_Request; Result : out Observation)
   is
      Proposed : constant D.Decoded_Event := D.Decode (Data, Raw (Position));
   begin
      Result := (State => Archive_Or_Decode_Refused, Position => Position);
      if Proposed.Status /= D.Decoded then return; end if;
      declare
         -- Initialized scratch is never published or used as evidence. Whole
         -- Materialize must succeed before any semantic decision is invoked.
         History : A.R.Retained_Events (Raw'Range) :=
           (others => (Event => Proposed.Value, Previous => (others => 0),
             Mac => (others => 0), Record_Bytes => (Present => False),
             Base_Archive => (Present => False)));
         Captured : H.Observation;
      begin
         H.Materialize (Data, Key, Genesis_Row, Genesis_Message, Genesis_Mac_Text,
                        Raw, Heads, History, Captured);
         if Captured.State /= H.Authenticated_History_Genesis_JSON_And_Fold_Open then
            Result := (State => Archive_Or_Decode_Refused, Position => Captured.Position);
            return;
         end if;
         if History (Position).Event.Kind /= M.Request_Abandon_Event then
            Result := (State => Wrong_Event_Family, Position => Position);
            return;
         end if;
         declare
            Decision : constant RA.Decision := RA.Decide
              (Data, Roots, Subjects, History (Raw'First .. Position - 1),
               Alternatives, Root, Expected, History (Position).Event);
         begin
            if Decision.Status = RA.Append_Request_Abandon then
               RA.Apply_Next
                 (Data, Roots, Subjects, History (Raw'First .. Position - 1),
                  Alternatives, Root, Expected, History (Position).Event);
            end if;
            Result := (State => Native_Request_Decided_Prestate_Fold_Open,
                       Position => Position, Decision => Decision);
         end;
      end;
   end Apply;
end Worldline.Custody_V2_Request_Step;

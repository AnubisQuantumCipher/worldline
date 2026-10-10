package body Worldline.Custody_V2_History with SPARK_Mode is
   use type C.Status;
   procedure Materialize
     (Data : C.E.Bytes; Key, Genesis_Row, Genesis_Message,
      Genesis_Mac_Text : C.E.Span; Raw : C.Event_Rows; Heads : C.Head_Rows;
      History : in out R.Retained_Events; Result : out Observation)
   is
      Chain : constant C.Result := C.Verify
        (Data, Key, Genesis_Row, Genesis_Message, Genesis_Mac_Text, Raw, Heads);
      Candidate : R.Retained_Events (History'Range) := History;
      Previous : M.Digest := Chain.Origin;
   begin
      Result := (Archive_Chain_Refused, Chain.Failing_Row);
      if Chain.State /= C.Archive_Chain_Matches_Genesis_JSON_And_Fold_Open then
         return;
      end if;
      -- Explicit checks discharge the local digest operation domains, not
      -- authentication: Chain above authenticates the original entire history.
      if not C.E.C.P.Valid (Data, Key) or else
         not C.E.C.P.Valid (Data, Genesis_Row) then return; end if;
      for I in Raw'Range loop
         pragma Loop_Invariant
           (Previous = (if I = Raw'First then Chain.Origin
                        else Candidate (I - 1).Event.Event_Id));
         pragma Loop_Invariant
           (for all J in Raw'First .. I - 1 =>
              C.E.C.P.Valid (Data, Raw (J).Base_Archive) and then
              Row_Matches (Data, Key, Raw (J),
                (if J = Raw'First then Chain.Origin
                 else Candidate (J - 1).Event.Event_Id), Candidate (J)));
         declare
            Item : constant D.Decoded_Event := D.Decode (Data, Raw (I));
         begin
            if Item.Status /= D.Decoded or else
               not C.E.C.P.Valid (Data, Raw (I).Base_Archive) then
               Result := (Semantic_Event_Refused, I);
               return;
            end if;
            Candidate (I) :=
              (Event => Item.Value, Previous => Previous,
               Mac => C.G.Mac (Data, Key, Raw (I).Base_Archive),
               Record_Bytes => (Present => True,
                 Value => (Raw (I).Record_Archive.First, Raw (I).Record_Archive.Length)),
               Base_Archive => (Present => True,
                 Value => (Raw (I).Base_Archive.First, Raw (I).Base_Archive.Length)));
            Previous := Item.Value.Event_Id;
         end;
      end loop;
      History := Candidate;
      Result := (Authenticated_History_Genesis_JSON_And_Fold_Open, 0);
   end Materialize;
end Worldline.Custody_V2_History;

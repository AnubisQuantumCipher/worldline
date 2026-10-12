package body Worldline.Custody_V2_Archive_Chain with SPARK_Mode is
   use type E.Q.Byte;
   use type E.Value_Kind;
   function Literal (Data : E.Bytes; Item : E.Span; Text : String) return Boolean is
     (E.C.P.Valid (Data, Item) and then Item.Length = Text'Length and then
      (for all I in Text'Range => Data (Item.First + E.Count (I - Text'First)) = Character'Pos (Text (I))));
   function Same (Data : E.Bytes; Left, Right : E.Span) return Boolean is
     (E.C.P.Valid (Data, Left) and then E.C.P.Valid (Data, Right) and then
      Left.Length = Right.Length and then
      (if Left.Length > 0 then
        (for all I in E.Count range 0 .. Left.Length - 1 => Data (Left.First + I) = Data (Right.First + I))));
   function Kind_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
     (Literal (Data, Item, "PREPARED") or else
      Literal (Data, Item, "HELD") or else
      Literal (Data, Item, "RUNNING") or else
      Literal (Data, Item, "EXECUTION_NATIVE") or else
      Literal (Data, Item, "EXECUTION_ACK") or else
      Literal (Data, Item, "HANDOFF_INTENT") or else
      Literal (Data, Item, "FRONT_CLOSE_INTENT") or else
      Literal (Data, Item, "FRONT_CLOSED") or else
      Literal (Data, Item, "TRANSFER_SENT") or else
      Literal (Data, Item, "ROSTER_EVIDENCE") or else
      Literal (Data, Item, "CUSTODY_ACK") or else
      Literal (Data, Item, "ABANDON") or else
      Literal (Data, Item, "FRONT_RETAINED_ESCROW") or else
      Literal (Data, Item, "HANDOFF_ABORT") or else
      Literal (Data, Item, "ORIGINAL_PROGRESS") or else
      Literal (Data, Item, "ORIGINAL_RESULT") or else
      Literal (Data, Item, "HANDLER_TERMINAL") or else
      Literal (Data, Item, "WORKER_RELINQUISH") or else
      Literal (Data, Item, "WORKER_REATTACHED") or else
      Literal (Data, Item, "CUSTODY_RETURNED") or else
      Literal (Data, Item, "CLOSED_NS") or else
      Literal (Data, Item, "CLOSED_OUTER") or else
      Literal (Data, Item, "CLOSED_RAW") or else
      Literal (Data, Item, "CLOSED_WITNESS") or else
      Literal (Data, Item, "PHYSICAL_SETTLED") or else
      Literal (Data, Item, "HISTORICAL_SETTLEMENT") or else
      Literal (Data, Item, "FRONT_RECONSTRUCTION") or else
      Literal (Data, Item, "FRONT_OWNED") or else
      Literal (Data, Item, "UNKNOWN") or else
      Literal (Data, Item, "RECONCILED") or else
      Literal (Data, Item, "REQUEST_QUEUED") or else
      Literal (Data, Item, "REQUEST_TRANSFER_INTENT") or else
      Literal (Data, Item, "REQUEST_INTAKE") or else
      Literal (Data, Item, "REQUEST_ABANDON") or else
      Literal (Data, Item, "REQUEST_RESPONDED") or else
      Literal (Data, Item, "REQUEST_LOST") or else
      Literal (Data, Item, "DRAIN_STOP_INTENT") or else
      Literal (Data, Item, "DRAIN_FREEZE") or else
      Literal (Data, Item, "DRAIN_OFD_EVIDENCE") or else
      Literal (Data, Item, "DRAIN_INTAKE") or else
      Literal (Data, Item, "DRAIN_ABANDON") or else
      Literal (Data, Item, "DRAIN_RELEASED") or else
      Literal (Data, Item, "DRAIN_RECLAIMED"));
   function Magnitude (Data : E.Bytes; Item : E.Span; Positive : Boolean) return Boolean is
     (E.C.P.Valid (Data, Item) and then
      (if Item.Length = 0 then not Positive else Data (Item.First + Item.Length - 1) /= 0));
   function Blob_Matches (Data : E.Bytes; Encoded, Expected : E.Span) return Boolean is
      Type_Name : constant E.View := E.Decode
        (Data, S.A.Field (Data, Encoded, "type"), E.Operation);
      Value : constant E.View := E.Decode
        (Data, S.A.Field (Data, Encoded, "value"), E.Operation);
      Hex : constant String := "0123456789abcdef";
   begin
      if not S.Valid (Data, Encoded) or else not E.Text_Is (Data, Type_Name, "bytes") or else
        Value.Form /= E.Text_Value or else not E.C.P.Valid (Data, Expected) then return False; end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Data, Value.Payload);
      begin
         if Raw'Length mod 2 /= 0 or else Raw'Length / 2 /= Expected.Length then return False; end if;
         if Expected.Length > 0 then
            for I in E.Count range 0 .. Expected.Length - 1 loop
               if Raw (Raw'First + I * 2) /= Character'Pos (Hex (Natural (Data (Expected.First + I) / 16) + 1)) or else
                 Raw (Raw'First + I * 2 + 1) /= Character'Pos (Hex (Natural (Data (Expected.First + I) mod 16) + 1)) then
                  return False;
               end if;
            end loop;
         end if;
         return True;
      end;
   end Blob_Matches;
   function Base_Matches (Data : E.Bytes; Row : Event_Row) return Boolean is
     (S.Valid (Data, Row.Base_Archive) and then S.Member_Count (Data, Row.Base_Archive) = 9 and then
      S.Member_Name_Is (Data, Row.Base_Archive, 0, "previous") and then
      S.Member_Name_Is (Data, Row.Base_Archive, 1, "generation") and then
      S.Member_Name_Is (Data, Row.Base_Archive, 2, "operation") and then
      S.Member_Name_Is (Data, Row.Base_Archive, 3, "subject_kind") and then
      S.Member_Name_Is (Data, Row.Base_Archive, 4, "subject") and then
      S.Member_Name_Is (Data, Row.Base_Archive, 5, "subgeneration") and then
      S.Member_Name_Is (Data, Row.Base_Archive, 6, "kind") and then
      S.Member_Name_Is (Data, Row.Base_Archive, 7, "actor") and then
      S.Member_Name_Is (Data, Row.Base_Archive, 8, "record") and then
      S.Text_Matches (Data, S.Field (Data, Row.Base_Archive, "previous"), Row.Previous) and then
      Blob_Matches (Data, S.Field (Data, Row.Base_Archive, "generation"), Row.Generation) and then
      S.Text_Matches (Data, S.Field (Data, Row.Base_Archive, "operation"), Row.Operation) and then
      S.Text_Matches (Data, S.Field (Data, Row.Base_Archive, "subject_kind"), Row.Subject_Kind) and then
      S.Text_Matches (Data, S.Field (Data, Row.Base_Archive, "subject"), Row.Subject) and then
      Blob_Matches (Data, S.Field (Data, Row.Base_Archive, "subgeneration"), Row.Subgeneration) and then
      S.Text_Matches (Data, S.Field (Data, Row.Base_Archive, "kind"), Row.Kind) and then
      S.Text_Matches (Data, S.Field (Data, Row.Base_Archive, "actor"), Row.Actor) and then
      S.Valid (Data, Row.Record_Archive) and then S.A.Same_Encoding (Data, S.Field (Data, Row.Base_Archive, "record"), Row.Record_Archive) and then
      Magnitude (Data, Row.Generation, True) and then Magnitude (Data, Row.Subgeneration, False) and then
      Kind_Valid (Data, Row.Kind) and then
      (Literal (Data, Row.Actor, "FRONT") or else Literal (Data, Row.Actor, "WORKER") or else
       Literal (Data, Row.Actor, "COLLECTOR") or else Literal (Data, Row.Actor, "RECONCILER")) and then
      (if Literal (Data, Row.Subject_Kind, "ROOT") then Row.Subject.Length = 0
       else (Literal (Data, Row.Subject_Kind, "REQUEST") or else Literal (Data, Row.Subject_Kind, "DESCRIPTOR"))
         and then Row.Subject.Length > 0));

   function Verify
     (Data : E.Bytes; Key, Genesis_Row, Genesis_Message, Genesis_Mac_Text : E.Span;
      Rows : Event_Rows; Heads : Head_Rows) return Result is
      Answer : Result;
   begin
      if not E.C.P.Valid (Data, Key) or else not S.Valid (Data, Genesis_Row) then return Answer; end if;
      if not S.Valid (Data, Genesis_Message) or else S.Member_Count (Data, Genesis_Message) /= 1 or else
        not S.Member_Name_Is (Data, Genesis_Message, 0, "genesis") or else
        not S.A.Same_Encoding (Data, S.Field (Data, Genesis_Message, "genesis"), Genesis_Row) then
         Answer.State := Genesis_Mismatch; return Answer;
      end if;
      if not G.Origin_Matches (Data, Genesis_Mac_Text, G.Mac (Data, Key, Genesis_Message)) then
         Answer.State := Genesis_Mac; return Answer;
      end if;
      Answer.Origin := G.Hash (Data, Genesis_Row); Answer.Head := Answer.Origin;
      for I in Rows'Range loop
         pragma Loop_Invariant (Answer.Origin = G.Hash (Data, Genesis_Row));
         pragma Loop_Invariant (for all J in Rows'First .. I - 1 => Base_Matches (Data, Rows (J)));
         Answer.Failing_Row := I;
         if not Base_Matches (Data, Rows (I)) then Answer.State := Row_Malformed; return Answer; end if;
         if not G.Origin_Matches (Data, Rows (I).Previous, Answer.Head) then Answer.State := Row_Link; return Answer; end if;
         Answer.Head := G.Hash (Data, Rows (I).Base_Archive);
         if not G.Origin_Matches (Data, Rows (I).Event_Id, Answer.Head) then Answer.State := Row_Id; return Answer; end if;
         if I > Rows'First then
            for J in Rows'First .. I - 1 loop
               if Same (Data, Rows (J).Event_Id, Rows (I).Event_Id) then Answer.State := Row_Duplicate; return Answer; end if;
            end loop;
         end if;
         if not G.Origin_Matches (Data, Rows (I).Mac, G.Mac (Data, Key, Rows (I).Base_Archive)) then
            Answer.State := Row_Mac; return Answer;
         end if;
      end loop;
      Answer.Failing_Row := 0;
      if Heads'Length /= 1 then Answer.State := Head_Kind; return Answer; end if;
      declare
         H : constant Head_Row := Heads (Heads'First);
         Selected : E.Span := (1, 0);
      begin
         if not Literal (Data, H.Name, "current") then Answer.State := Head_Value; return Answer; end if;
         if Rows'Length = 0 then
            if not Literal (Data, H.Kind, "ORIGIN") or else H.Event_Id.Present or else not H.Origin.Present then
               Answer.State := Head_Kind; return Answer;
            end if;
            Selected := H.Origin.Value;
         else
            if not Literal (Data, H.Kind, "EVENT") or else not H.Event_Id.Present or else H.Origin.Present then
               Answer.State := Head_Kind; return Answer;
            end if;
            Selected := H.Event_Id.Value;
         end if;
         if not G.Origin_Matches (Data, Selected, Answer.Head) or else not S.Valid (Data, H.Message) or else
           S.Member_Count (Data, H.Message) /= 3 or else
           not S.Member_Name_Is (Data, H.Message, 0, "head_kind") or else
           not S.Member_Name_Is (Data, H.Message, 1, "head") or else
           not S.Member_Name_Is (Data, H.Message, 2, "genesis") or else
           not S.Text_Matches (Data, S.Field (Data, H.Message, "head_kind"), H.Kind) or else
           not S.Text_Matches (Data, S.Field (Data, H.Message, "head"), Selected) or else
           not S.A.Same_Encoding (Data, S.Field (Data, H.Message, "genesis"), Genesis_Row) then
            Answer.State := Head_Value; return Answer;
         end if;
         if not G.Origin_Matches (Data, H.Mac, G.Mac (Data, Key, H.Message)) then
            Answer.State := Head_Mac; return Answer;
         end if;
      end;
      Answer.State := Archive_Chain_Matches_Genesis_JSON_And_Fold_Open;
      return Answer;
   end Verify;
end Worldline.Custody_V2_Archive_Chain;

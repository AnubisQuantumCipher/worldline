package body Worldline.Retained_V1_Migration with SPARK_Mode is
   function Context_Matches
     (Data : E.Bytes; Context : Context_Inputs; Genesis_Archive, Installation : E.Span)
      return Boolean
   is
   begin
      for Item of Context loop
         if not E.C.P.Valid (Data, Item.Raw) or else
           not Same (Data, Item.Actual_Path, Item.Retained_Path) or else
           not G.Origin_Matches (Data, Item.Retained_SHA256, G.Hash (Data, Item.Raw))
         then return False; end if;
      end loop;
      return C.S.Valid (Data, Genesis_Archive) and then
        C.S.Member_Count (Data, Genesis_Archive) = 6 and then
        C.S.Text_Is (Data, C.S.Field (Data, Genesis_Archive, "schema"),
                    "worldline.owner-provisioned-root-custody-v1") and then
        C.S.Text_Matches (Data, C.S.Field (Data, Genesis_Archive, "installation"), Installation) and then
        C.S.Text_Matches (Data, C.S.Field (Data, Genesis_Archive, "startup_descriptor_sha256"),
                         Context (Descriptor).Retained_SHA256) and then
        C.S.Text_Matches (Data, C.S.Field (Data, Genesis_Archive, "owner_plan_sha256"),
                         Context (Plan).Retained_SHA256) and then
        C.S.Text_Matches (Data, C.S.Field (Data, Genesis_Archive, "issuer_key_sha256"),
                         Context (Issuer_Key).Retained_SHA256) and then
        C.S.Field (Data, Genesis_Archive, "initial_event").Length > 0;
   end Context_Matches;
   function Decide
     (Data : E.Bytes; Context : Context_Inputs; Installation, Genesis_Archive,
      Head_Archive, Retained_Head : E.Span; Genesis : C.Genesis_Rows;
      Rows : C.Event_Rows; Heads : C.Head_Rows) return Decision
   is
      Chain : constant C.Result := C.Verify
        (Data, Context (Issuer_Key).Raw, Genesis_Archive, Head_Archive, Genesis, Rows, Heads);
   begin
      if Chain.State /= C.Retained_Chain_Matches then
         return (Retained_Chain_Refused, Chain.Failing_Row, Chain);
      end if;
      if not Context_Matches (Data, Context, Genesis_Archive, Installation) or else
        Heads'Length /= 1 or else not Same (Data, Heads (Heads'First).Event_Id, Retained_Head)
      then return (Prior_Context_Differs, 0, Chain); end if;
      for I in Rows'Range loop
         pragma Loop_Invariant
           (for all Earlier in Rows'Range =>
             (if Earlier < I then
                E.C.P.Valid (Data, Rows (Earlier).Operation) and then
                E.C.P.Valid (Data, Rows (Earlier).Kind) and then
                (if Last_For_Operation (Data, Rows, Earlier) then Terminal (Data, Rows (Earlier)))));
         if not E.C.P.Valid (Data, Rows (I).Operation) or else
           not E.C.P.Valid (Data, Rows (I).Kind) or else
           (Last_For_Operation (Data, Rows, I) and then not Terminal (Data, Rows (I)))
         then return (Operation_Not_Closed, I, Chain); end if;
      end loop;
      return (Closed_V1_Value_Source_Join_Open, 0, Chain);
   end Decide;
end Worldline.Retained_V1_Migration;

with Interfaces;
package body Worldline.Custody_V2_Provision with SPARK_Mode is
   use type E.Count;
   use type Interfaces.Unsigned_8;
   use type Canonical_Artifacts.Genesis_Correspondence;
   use type Canonical_Artifacts.Kind;
   use type C.Status;
   use type C.SHA.Digest;
   function Corresponds (Data : E.Bytes; Raw, Encoded : E.Span) return Boolean is
     (Canonical_Artifacts.Genesis_Archive_Matches (Data, Raw, Encoded) =
        Canonical_Artifacts.Typed_Tree_Matches_Source_Custody_Open);
   function Digest_Field (Data : E.Bytes; Encoded : E.Span; Name : String;
                          Raw : E.Span) return Boolean is
      Hex : constant String := "0123456789abcdef";
      Text : String (1 .. 64);
   begin
      if not E.C.P.Valid (Data, Raw) then return False; end if;
      declare
         Value : constant C.SHA.Digest := G.Hash (Data, Raw);
      begin
         for I in Value'Range loop
            Text (2 * (I - Value'First) + 1) := Hex (Integer (Value (I) / 16) + 1);
            Text (2 * (I - Value'First) + 2) := Hex (Integer (Value (I) mod 16) + 1);
         end loop;
      end;
      return S.Text_Is (Data, S.Field (Data, Encoded, Name), Text);
   end Digest_Field;
   function Same_Field (Data : E.Bytes; Left : E.Span; Left_Name : String;
                         Right : E.Span; Right_Name : String) return Boolean is
     (S.Field (Data, Left, Left_Name).Length > 0 and then
      M.Same (Data, S.Field (Data, Left, Left_Name), S.Field (Data, Right, Right_Name)));
   function Null_Field (Data : E.Bytes; Raw : E.Span; Name : String) return Boolean is
      Item : constant Canonical_Artifacts.Member := Canonical_Artifacts.Field (Data, Raw, Name);
   begin
      return Item.Found and then Item.Value.Form = Canonical_Artifacts.Null_Value;
   end Null_Field;
   function Selected_Matches
     (Data : E.Bytes; Selected : Selected_Artifacts; Journal_Path, Key : E.Span)
      return Boolean
   is
      D : constant E.Span := Selected (Descriptor).Encoded;
      P : constant E.Span := Selected (Plan).Encoded;
      V : constant E.Span := Selected (Genesis_File).Encoded;
   begin
      for Item of Selected loop
         if not Corresponds (Data, Item.Raw, Item.Encoded) or else
           not E.C.P.Valid (Data, Item.Path) or else Item.Path.Length = 0
         then return False; end if;
      end loop;
      return E.C.P.Valid (Data, Key) and then E.C.P.Valid (Data, Journal_Path) and then
        Journal_Path.Length > 0 and then
        S.Text_Is (Data, S.Field (Data, V, "schema"), "worldline.owner-provisioned-root-custody-v2") and then
        S.Member_Count (Data, V) = 7 and then Null_Field (Data, Selected (Genesis_File).Raw, "initial_event") and then
        S.Text_Is (Data, S.Field (Data, P, "schema"), "worldline.protected-root-worker-plan-v1") and then
        S.Member_Count (Data, P) = 13 and then
        S.Field (Data, P, "entry").Length > 0 and then
        S.Field (Data, P, "early_envelope").Length > 0 and then
        S.Field (Data, P, "helper").Length > 0 and then
        S.Field (Data, P, "sources").Length > 0 and then
        S.Field (Data, P, "worker_policy").Length > 0 and then
        S.Field (Data, P, "cost_key").Length > 0 and then
        S.Field (Data, P, "native_components").Length > 0 and then
        S.Field (Data, P, "child_dispatch").Length > 0 and then
        Same_Field (Data, V, "installation", D, "installation_id") and then
        Same_Field (Data, V, "installation", P, "installation") and then
        S.Text_Matches (Data, S.Field (Data, P, "startup_descriptor"), Selected (Descriptor).Path) and then
        S.Text_Matches (Data, S.Field (Data, P, "handoff_genesis"), Selected (Genesis_File).Path) and then
        S.Text_Matches (Data, S.Field (Data, P, "handoff_journal"), Journal_Path) and then
        S.Text_Matches (Data, S.Field (Data, S.Field (Data, D, "root_worker"), "owner_plan"), Selected (Plan).Path) and then
        Digest_Field (Data, V, "startup_descriptor_sha256", Selected (Descriptor).Raw) and then
        Digest_Field (Data, V, "owner_plan_sha256", Selected (Plan).Raw) and then
        Digest_Field (Data, V, "issuer_key_sha256", Key);
   end Selected_Matches;
   function Prior_Matches
     (Data : E.Bytes; Selected : Selected_Artifacts; Journal_Path : E.Span;
      Prior : M.Context_Inputs; Prior_Descriptor, Prior_Plan,
      Prior_Genesis, Retained_Head : E.Span) return Boolean
   is
      V : constant E.Span := S.Field (Data, Selected (Genesis_File).Encoded, "prior_custody");
      function Bound (Name : String; Expected : E.Span) return Boolean is
        (S.Text_Matches (Data, S.Field (Data, V, Name), Expected));
   begin
      return S.Valid (Data, V) and then S.Member_Count (Data, V) = 10 and then
        S.Member_Count (Data, Prior_Genesis) = 6 and then
        S.Text_Is (Data, S.Field (Data, Prior_Genesis, "schema"),
                   "worldline.owner-provisioned-root-custody-v1") and then
        Bound ("descriptor_path", Prior (M.Descriptor).Retained_Path) and then
        Bound ("descriptor_sha256", Prior (M.Descriptor).Retained_SHA256) and then
        Bound ("plan_path", Prior (M.Plan).Retained_Path) and then
        Bound ("plan_sha256", Prior (M.Plan).Retained_SHA256) and then
        Bound ("genesis_path", Prior (M.Genesis_File).Retained_Path) and then
        Bound ("genesis_sha256", Prior (M.Genesis_File).Retained_SHA256) and then
        Bound ("journal_path", Prior (M.Journal_File).Retained_Path) and then
        Bound ("journal_sha256", Prior (M.Journal_File).Retained_SHA256) and then
        Bound ("head_event", Retained_Head) and then
        Bound ("issuer_key_sha256", Prior (M.Issuer_Key).Retained_SHA256) and then
        not M.Same (Data, Selected (Plan).Path, Prior (M.Plan).Retained_Path) and then
        not M.Same (Data, Selected (Plan).Raw, Prior (M.Plan).Raw) and then
        not M.Same (Data, Selected (Genesis_File).Path, Prior (M.Genesis_File).Retained_Path) and then
        not M.Same (Data, Journal_Path, Prior (M.Journal_File).Retained_Path) and then
        Corresponds (Data, Prior (M.Descriptor).Raw, Prior_Descriptor) and then
        Corresponds (Data, Prior (M.Plan).Raw, Prior_Plan) and then
        E.C.P.Valid (Data, Selected (Plan).Raw) and then
        G.Hash (Data, Selected (Plan).Raw) /= G.Hash (Data, Prior (M.Plan).Raw) and then
        Corresponds (Data, Prior (M.Genesis_File).Raw, Prior_Genesis) and then
        Same_Field (Data, Prior_Descriptor, "installation_id", Selected (Descriptor).Encoded, "installation_id") and then
        Same_Field (Data, Prior_Plan, "installation", Prior_Genesis, "installation") and then
        S.Text_Matches (Data, S.Field (Data, Prior_Plan, "startup_descriptor"), Prior (M.Descriptor).Retained_Path) and then
        S.Text_Matches (Data, S.Field (Data, Prior_Plan, "handoff_journal"), Prior (M.Journal_File).Retained_Path) and then
        S.Text_Matches (Data, S.Field (Data, Prior_Plan, "handoff_genesis"), Prior (M.Genesis_File).Retained_Path);
   end Prior_Matches;
   function Decide
     (Data : E.Bytes; Selected : Selected_Artifacts; Journal_Path, Key, Mode : E.Span;
      Prior : M.Context_Inputs; Prior_Descriptor, Prior_Plan, Prior_Genesis,
      Prior_Head, Retained_Head : E.Span; Genesis : C.Genesis_Rows;
      Rows : C.Event_Rows; Heads : C.Head_Rows) return Result
   is
   begin
      if not Selected_Matches (Data, Selected, Journal_Path, Key) then
         return (Selected_Context_Refused, 0);
      end if;
      if M.Literal (Data, Mode, "NEW") then
         if Null_Field (Data, Selected (Genesis_File).Raw, "prior_custody") and then
           Genesis'Length = 0 and then Rows'Length = 0 and then Heads'Length = 0
         then return (New_Origin_Eligible, 0);
         else return (Prior_Context_Refused, 0); end if;
      end if;
      if not M.Literal (Data, Mode, "MIGRATE") or else
        not Prior_Matches (Data, Selected, Journal_Path, Prior, Prior_Descriptor,
                           Prior_Plan, Prior_Genesis, Retained_Head) or else
        not M.Same (Data, Key, Prior (M.Issuer_Key).Raw)
      then return (Prior_Context_Refused, 0); end if;
      declare
         Installation : constant E.Span := S.Field (Data, Prior_Genesis, "installation");
         -- M's installation operand is text bytes, not a scoped archive. The
         -- original context relation is evaluated with the selected literal
         -- supplied in Prior's descriptor path-free context below by checking
         -- the exact same installation archive and original chain directly.
         Chain : constant C.Result := C.Verify (Data, Key, Prior_Genesis, Prior_Head, Genesis, Rows, Heads);
      begin
         if Installation.Length = 0 or else Chain.State /= C.Retained_Chain_Matches then
            return (Retained_Chain_Refused, Chain.Failing_Row);
         end if;
         for Item of Prior loop
            if not E.C.P.Valid (Data, Item.Raw) or else
              not M.Same (Data, Item.Actual_Path, Item.Retained_Path) or else
              not G.Origin_Matches (Data, Item.Retained_SHA256, G.Hash (Data, Item.Raw))
            then return (Prior_Context_Refused, 0); end if;
         end loop;
         if not Digest_Field (Data, Prior_Genesis, "startup_descriptor_sha256", Prior (M.Descriptor).Raw) or else
           not Digest_Field (Data, Prior_Genesis, "owner_plan_sha256", Prior (M.Plan).Raw) or else
           not Digest_Field (Data, Prior_Genesis, "issuer_key_sha256", Key) or else
           Heads'Length /= 1 or else not M.Same (Data, Heads (Heads'First).Event_Id, Retained_Head)
         then return (Prior_Context_Refused, 0); end if;
         if not M.Closed_Operations (Data, Rows) then return (Operation_Not_Closed, 0); end if;
      end;
      return (Closed_V1_Migration_Eligible, 0);
   end Decide;
end Worldline.Custody_V2_Provision;

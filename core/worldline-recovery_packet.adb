with Worldline.Retained_Evidence_Replay;
with Worldline.Recovery_Material_Replay;
with Worldline.Recovery_Owner_Replay;
with Worldline.Evaluation_Authority;
with Worldline.Collapse;
with Worldline.Recovery_Syntax;
package body Worldline.Recovery_Packet with SPARK_Mode is
   package R renames Worldline.Retained_Evidence_Replay;
   package M renames Worldline.Recovery_Material_Replay;
   package O renames Worldline.Recovery_Owner_Replay;
   package H renames Worldline.Evaluation_Authority;
   use type E.Value_Kind;
   use type E.Count;
   use type C.Byte;
   use type H.Raw_Dependency;
   use type O.Status;
   function Is_Null (Data : E.Bytes; Item : E.Span) return Boolean is
     (E.Decode (Data, Item, E.Recovery).Form = E.Null_Value);
   function Projection_Matches
     (Data : E.Bytes; Packet : E.Span; Expected_Data : E.Bytes;
      Expected_Values : E.Span) return Boolean
   is
      V : constant Packet_View := Decode (Data, Packet);
      use type E.Q.Byte;
   begin
      --  Both value spans must lie inside their own arenas before any byte is
      --  compared; a packet whose values span escapes its arena cannot match.
      if not V.Valid or else not A.Valid (Data, V.Values) or else
        not A.Valid (Expected_Data, Expected_Values) or else
        not E.C.P.Valid (Data, V.Values) or else
        not E.C.P.Valid (Expected_Data, Expected_Values) or else
        not A.Record_Is (Expected_Data, Expected_Values, "worldline.core", "CollapseInput") or else
        V.Values.Length /= Expected_Values.Length then return False; end if;
      if V.Values.Length > 0 then
         for I in E.Count range 0 .. V.Values.Length - 1 loop
            if Data (V.Values.First + I) /= Expected_Data (Expected_Values.First + I) then
               return False;
            end if;
         end loop;
      end if;
      return True;
   end Projection_Matches;
   function Decode (Data : E.Bytes; Packet : E.Span) return Packet_View is
      Item : constant E.View := E.Decode (Data, Packet, E.Recovery);
      V : Packet_View;
      function F (Name : String) return E.Span is (A.Field (Data, Packet, Name));
   begin
      if Item.Form /= E.Object_Value or else not A.Valid (Data, Packet) then return V; end if;
      V.Has_Owner := A.Text_Is (Data, F ("schema"), "worldline-collapse-observation-v3-owner");
      if not ((not V.Has_Owner and then A.Text_Is
                 (Data, F ("schema"), "worldline-collapse-observation-v2") and then
                 E.Array_Length (Data, Item.Children) = 14) or else
              (V.Has_Owner and then E.Array_Length (Data, Item.Children) = 15))
      then return V; end if;
      V.Values := F ("values"); V.Primary := F ("primary"); V.Staged := F ("staged");
      V.Agent := F ("agent"); V.Agent_Record := F ("agentRecord");
      V.Inputs := F ("inputs"); V.Candidate := F ("candidate"); V.Subject := F ("subject");
      V.Witness := F ("witness"); V.Authoritative_Requirement := F ("authoritativeRequirement");
      V.Current_Requirement := F ("currentRequirementArgument");
      V.Resulting_Requirement := F ("resultingRequirement"); V.Roots := F ("authoritativeRoots");
      V.Owner := F ("owner");
      if not A.Record_Is (Data, V.Values, "worldline.core", "CollapseInput") or else
         not A.Record_Is (Data, V.Candidate, "worldline.model", "World") or else
         not A.Record_Is (Data, V.Subject, "worldline.model", "World") or else
         E.Decode (Data, V.Inputs, E.Recovery).Form /= E.Object_Value or else
         E.Decode (Data, V.Authoritative_Requirement, E.Recovery).Form /= E.Object_Value or else
         E.Decode (Data, V.Roots, E.Recovery).Form /= E.Tuple_Value or else
         V.Primary.Length = 0 or else V.Staged.Length = 0 or else V.Agent.Length = 0 or else
         V.Agent_Record.Length = 0 or else V.Witness.Length = 0 or else
         V.Current_Requirement.Length = 0 or else V.Resulting_Requirement.Length = 0 or else
         (V.Has_Owner and then not A.Record_Is
            (Data, V.Owner, "worldline.owner_collapse_data", "OwnerCollapseData"))
      then return V; end if;
      V.Valid := True;
      return V;
   end Decode;
   function Inspect
     (Data : E.Bytes; Packet : E.Span; Facts_Data : E.Bytes;
      Capsules : E.Span) return Result is
      V : constant Packet_View := Decode (Data, Packet);
      Out_Result : Result;
   begin
      if not V.Valid then return Out_Result; end if;
      if Capsules.Length > 0 and then not Worldline.Recovery_Syntax.Valid (Facts_Data, Capsules) then
         return Out_Result;
      end if;
      declare
         Values : constant R.Collapse_Values_Result := R.Decode_Recovery_Collapse_Values (Data, V.Values);
      begin
         if not Values.Present then return Out_Result; end if;
         declare
            Needed : constant H.Raw_Dependency := H.Dependencies (Values.Raw);
            Primary_Input : constant E.Span := A.Field (Data, V.Inputs, "primary");
            Staged_Input : constant E.Span := A.Field (Data, V.Inputs, "staged");
            Primary_Cursor : constant E.Span := A.Field (Data, Primary_Input, "evaluationCursor");
            Staged_Cursor : constant E.Span := A.Field (Data, Staged_Input, "evaluationCursor");
            Need_Primary : constant Boolean := H.Needs_Primary (Needed);
            Need_Staged : constant Boolean := H.Needs_Staged (Needed) and then
              A.Boolean_Is (Data, A.Field (Data, Staged_Input, "ran"), True);
            Retry : constant Boolean := V.Has_Owner and then
              A.Text_Is (Data, A.Field (Data, V.Owner, "mode"), "RETRY_EVALUATION");
            P, S : M.Replay_Result;
            Bound : C.Raw_Request := H.Without_Carried_Rosters (Values.Raw);
            Agent_Ready : Boolean;
         begin
            if Needed = H.Invalid_Collapse then return Out_Result; end if;
            if Need_Primary then
               if Retry then P := M.Owner_Selected (Data, V.Primary, V.Owner, Facts_Data, Capsules);
               else P := M.Rebuild (Data, V.Primary, V.Subject, V.Current_Requirement, Primary_Cursor,
                 Facts_Data, Capsules);
               end if;
               if not P.Valid then Out_Result.State := Selection_Conflict; return Out_Result; end if;
            elsif not Is_Null (Data, V.Primary) then
               Out_Result.State := Selection_Conflict; return Out_Result;
            end if;
            if Need_Staged then
               S := M.Rebuild (Data, V.Staged, V.Subject, V.Current_Requirement, Staged_Cursor,
                 Facts_Data, Capsules);
               if not S.Valid then Out_Result.State := Selection_Conflict; return Out_Result; end if;
            elsif not Is_Null (Data, V.Staged) then
               Out_Result.State := Selection_Conflict; return Out_Result;
            end if;
            if not M.Agent_Matches (Data, V.Subject, V.Agent, V.Agent_Record, H.Needs_Agent (Needed),
              Facts_Data, Capsules) then
               Out_Result.State := Agent_Conflict; return Out_Result;
            end if;
            Agent_Ready := M.Agent_Admitted (Data, V.Agent);
            if not Is_Null (Data, V.Agent) then
               if Need_Primary and then not M.Bind (Data, V.Primary, V.Values, V.Subject,
                 V.Candidate, V.Authoritative_Requirement, V.Resulting_Requirement, V.Roots,
                 V.Agent, V.Agent_Record, Primary_Cursor, False, Facts_Data, Capsules)
               then Out_Result.State := Source_Conflict; return Out_Result; end if;
               if Need_Staged and then not M.Bind (Data, V.Staged, V.Values, V.Subject,
                 V.Candidate, V.Authoritative_Requirement, V.Resulting_Requirement, V.Roots,
                 V.Agent, V.Agent_Record, Staged_Cursor, True, Facts_Data, Capsules)
               then Out_Result.State := Source_Conflict; return Out_Result; end if;
            end if;
            if V.Has_Owner and then not O.Matches
              (Data, V.Owner, V.Values, V.Subject, V.Primary, Primary_Cursor, Facts_Data, Capsules)
            then Out_Result.State := Owner_Conflict; return Out_Result; end if;
            -- Neither carried roster byte is consulted. The original native
            -- policies independently classify every full retained raw row.
            Bound.Roster_Complete := (if Need_Primary and then P.Promotion and then Agent_Ready then 1 else 0);
            Bound.Staged_Roster_Complete := (if Need_Staged and then S.Promotion and then Agent_Ready then 1 else 0);
            Out_Result.Collapse_Code := C.Decide_Wire (Bound);
            if Out_Result.Collapse_Code /= Worldline.Collapse.Decision'Pos (Worldline.Collapse.Authorized) then
               Out_Result.State := Native_Refused; return Out_Result;
            end if;
            if V.Has_Owner then
               declare
                  Owner_Result : constant O.Status := O.Decide
                    (Data, V.Owner, V.Values, Bound, Facts_Data, Capsules);
               begin
                  Out_Result.Owner_Code := O.Status'Pos (Owner_Result);
                  if Owner_Result /= O.Ready then
                     Out_Result.State := Native_Refused; return Out_Result;
                  end if;
               end;
            end if;
            Out_Result.State := Ready;
            return Out_Result;
         end;
      end;
   end Inspect;
   function Inspect (Data : E.Bytes; Packet : E.Span) return Result is
     (Inspect (Data, Packet, E.Bytes'(1 .. 0 => 0), (1, 0)));
   function Complete (Data : E.Bytes; Packet : E.Span) return Status is
     (Inspect (Data, Packet).State);
   function Complete
     (Data : E.Bytes; Packet : E.Span; Facts_Data : E.Bytes;
      Capsules : E.Span) return Status is
     (Inspect (Data, Packet, Facts_Data, Capsules).State);
end Worldline.Recovery_Packet;

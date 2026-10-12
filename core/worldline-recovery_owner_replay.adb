with Evaluation_History;
with Worldline.Operation_Archive;
with Worldline.Recovery_Archive;
with Worldline.Recovery_Material_Replay;
with Worldline.Retained_Evidence_Replay;
with Worldline.Collapse_Wire;

package body Worldline.Recovery_Owner_Replay with SPARK_Mode is
   package A renames Worldline.Operation_Archive;
   package RA renames Worldline.Recovery_Archive;
   package M renames Worldline.Recovery_Material_Replay;
   package V renames Worldline.Retained_Evidence_Replay;
   use type E.Count;
   use type E.Value_Kind;
   use type E.Layer;
   use type E.Bytes;
   use type E.Q.Byte;
   use type R.Decision;
   use type C.Decision;
   use type CW.Raw_Optional_Hash;
   use type CW.Raw_Optional_Counter;

   function Field (Data : E.Bytes; Item : E.Span; Name : String;
      At_Layer : E.Layer) return E.Span with Global => null is
   begin
      if At_Layer = E.Recovery then
         return RA.Field (Data, Item, Name);
      else
         return A.Field (Data, Item, Name);
      end if;
   end Field;
   function Payload_Is (Data : E.Bytes; Item : E.Byte_View; Text : String)
      return Boolean is
   begin
      if not E.Bytes_Valid (Data, Item) then return False; end if;
      declare Raw : constant E.Bytes := E.Materialize (Data, Item); begin
         return Raw'Length = Text'Length and then
           (for all I in Text'Range => Raw (Raw'First + E.Count (I - Text'First)) =
               Character'Pos (Text (I)));
      end;
   end Payload_Is;
   function Record_Is (Data : E.Bytes; Item : E.Span; Module, Name : String;
      At_Layer : E.Layer) return Boolean is
      Raw : constant E.View := E.Decode (Data, Item, At_Layer);
   begin
      return At_Layer in E.Operation | E.Recovery and then
        (if At_Layer = E.Recovery then RA.Valid (Data, Item) else A.Valid (Data, Item))
        and then Raw.Form = E.Record_Value
        and then Payload_Is (Data, Raw.Module_Name, Module)
        and then Payload_Is (Data, Raw.Record_Name, Name);
   end Record_Is;
   function Null_Is (Data : E.Bytes; Item : E.Span;
      At_Layer : E.Layer := E.Recovery) return Boolean is
     (E.Decode (Data, Item, At_Layer).Form = E.Null_Value);
   function Text_Is (Data : E.Bytes; Item : E.Span; Text : String;
      At_Layer : E.Layer := E.Recovery) return Boolean is
     (E.Text_Is (Data, E.Decode (Data, Item, At_Layer), Text));

   procedure Scalar (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out H.Identity_Span;
      Form : E.Value_Kind; At_Layer : E.Layer)
   is
      Raw : constant E.View := E.Decode (Data, Item, At_Layer);
   begin
      Value := (1, 0);
      if not Valid then return; end if;
      if Raw.Form /= Form or else (Form = E.Integer_Value and then Raw.Sign)
        or else not E.Bytes_Valid (Data, Raw.Payload) then
         Valid := False; return;
      end if;
      declare Bytes : constant E.Bytes := E.Materialize (Data, Raw.Payload); begin
         if Item.First not in Arena'Range or else
           (Bytes'Length > 0 and then Bytes'Length - 1 > Arena'Last - Item.First) then
            Valid := False; return;
         end if;
         for I in Bytes'Range loop
            Arena (Item.First + (I - Bytes'First)) := Bytes (I);
         end loop;
         Value := (Item.First, Bytes'Length);
      end;
   end Scalar;

   procedure Decode_Identity
     (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out K.Optional_Identity;
      At_Layer : E.Layer := E.Recovery)
   is
      Span : H.Identity_Span;
   begin
      --  SPARK: refusal (Valid False) exactly where the original raised Constraint_Error:
      --  a constrained actual whose discriminant differs from the one assigned.
      if Value'Constrained and then Value.Present then
         Value := (Present => True, Value => (1, 0)); Valid := False; return;
      end if;
      Value := (Present => False);
      if not Valid or else Null_Is (Data, Item, At_Layer) then return; end if;
      Scalar (Data, Item, Arena, Valid, Span, E.Text_Value, At_Layer);
      if Valid and then Value'Constrained then Valid := False; end if;
      if Valid then Value := (Present => True, Value => Span); end if;
   end Decode_Identity;
   procedure Decode_Epoch
     (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out H.Optional_Epoch;
      At_Layer : E.Layer := E.Recovery)
   is
      Span : H.Identity_Span;
   begin
      --  SPARK: refusal (Valid False) exactly where the original raised Constraint_Error:
      --  a constrained actual whose discriminant differs from the one assigned.
      if Value'Constrained and then Value.Present then
         Value := (Present => True, Value => (1, 0)); Valid := False; return;
      end if;
      Value := (Present => False);
      if not Valid or else Null_Is (Data, Item, At_Layer) then return; end if;
      Scalar (Data, Item, Arena, Valid, Span, E.Integer_Value, At_Layer);
      if Valid and then Value'Constrained then Valid := False; end if;
      if Valid then Value := (Present => True, Value => H.Epoch_Id (Span)); end if;
   end Decode_Epoch;
   procedure Cursor_Fields
     (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out H.Optional_Cursor; At_Layer : E.Layer)
   is
      Epoch : H.Optional_Epoch;
      Run : K.Optional_Identity;
   begin
      --  SPARK: refusal (Valid False) exactly where the original raised Constraint_Error:
      --  a constrained actual whose discriminant differs from the one assigned.
      if Value'Constrained and then Value.Present then
         Value := (Present => True, Value => (Sequence => (Present => False), Run => (1, 0)));
         Valid := False; return;
      end if;
      Value := (Present => False);
      Decode_Epoch (Data, Field (Data, Item, "epoch", At_Layer), Arena, Valid, Epoch, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "run", At_Layer), Arena, Valid, Run, At_Layer);
      if not Run.Present then Valid := False; end if;
      if Valid and then Value'Constrained then Valid := False; end if;
      if Valid then
         Value := (Present => True, Value =>
           (Sequence => Epoch, Run => H.Evaluation_Id (Run.Value)));
      end if;
   end Cursor_Fields;
   procedure Decode_Cursor
     (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out H.Optional_Cursor;
      At_Layer : E.Layer := E.Recovery) is
   begin
      --  SPARK: refusal (Valid False) exactly where the original raised Constraint_Error:
      --  a constrained actual whose discriminant differs from the one assigned.
      if Value'Constrained and then Value.Present then
         Value := (Present => True, Value => (Sequence => (Present => False), Run => (1, 0)));
         Valid := False; return;
      end if;
      Value := (Present => False);
      if not Valid or else Null_Is (Data, Item, At_Layer) then return; end if;
      if not Record_Is (Data, Item, "worldline.evaluation_history", "EvaluationCursor", At_Layer) then
         Valid := False; return;
      end if;
      Cursor_Fields (Data, Item, Arena, Valid, Value, At_Layer);
   end Decode_Cursor;

   procedure Decode_Grant (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out K.Owner_Grant; At_Layer : E.Layer) is
   begin
      Value := (Action => K.Retry_Evaluation, State => K.Issued,
         Grant | Use_Id | Issuer | Principal | Subject | Content | Transaction |
         Current_Requirement | Expected_Requirement | Reason | Issued_Grant |
         Reserved_Grant | Reserved_Use => (Present => False),
         Failed_Run | Prior_Head | Next_Run => (Present => False),
         Epoch => (Present => False));
      if not Valid then return; end if;
      if not Record_Is (Data, Item, "worldline.owner_transitions", "OwnerGrant", At_Layer) then
         Valid := False; return;
      end if;
      if Text_Is (Data, Field (Data, Item, "action", At_Layer), "RETRY_EVALUATION", At_Layer) then
         Value.Action := K.Retry_Evaluation;
      elsif Text_Is (Data, Field (Data, Item, "action", At_Layer), "ADOPT_REQUIREMENT", At_Layer) then
         Value.Action := K.Adopt_Requirement;
      else Valid := False; return; end if;
      if Text_Is (Data, Field (Data, Item, "state", At_Layer), "ISSUED", At_Layer) then
         Value.State := K.Issued;
      elsif Text_Is (Data, Field (Data, Item, "state", At_Layer), "RESERVED", At_Layer) then
         Value.State := K.Reserved;
      elsif Text_Is (Data, Field (Data, Item, "state", At_Layer), "CONSUMED", At_Layer) then
         Value.State := K.Consumed;
      elsif Text_Is (Data, Field (Data, Item, "state", At_Layer), "REVOKED", At_Layer) then
         Value.State := K.Revoked;
      else Valid := False; return; end if;
      Decode_Identity (Data, Field (Data, Item, "grant", At_Layer), Arena, Valid, Value.Grant, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "use_id", At_Layer), Arena, Valid, Value.Use_Id, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "issuer", At_Layer), Arena, Valid, Value.Issuer, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "principal", At_Layer), Arena, Valid, Value.Principal, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "subject", At_Layer), Arena, Valid, Value.Subject, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "content", At_Layer), Arena, Valid, Value.Content, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "transaction", At_Layer), Arena, Valid, Value.Transaction, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "current_requirement", At_Layer), Arena, Valid, Value.Current_Requirement, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "expected_requirement", At_Layer), Arena, Valid, Value.Expected_Requirement, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "reason", At_Layer), Arena, Valid, Value.Reason, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "issued_grant", At_Layer), Arena, Valid, Value.Issued_Grant, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "reserved_grant", At_Layer), Arena, Valid, Value.Reserved_Grant, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "reserved_use", At_Layer), Arena, Valid, Value.Reserved_Use, At_Layer);
      Decode_Cursor (Data, Field (Data, Item, "failed_run", At_Layer), Arena, Valid, Value.Failed_Run, At_Layer);
      Decode_Cursor (Data, Field (Data, Item, "prior_head", At_Layer), Arena, Valid, Value.Prior_Head, At_Layer);
      Decode_Cursor (Data, Field (Data, Item, "next_run", At_Layer), Arena, Valid, Value.Next_Run, At_Layer);
      Decode_Epoch (Data, Field (Data, Item, "epoch", At_Layer), Arena, Valid, Value.Epoch, At_Layer);
   end Decode_Grant;

   procedure Decode_Request
     (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out K.Request;
      At_Layer : E.Layer := E.Recovery) is
   begin
      Value := (Action => K.Retry_Evaluation,
         Peer | Owner | Trusted_Issuer | Subject | Content | Transaction |
         Current_Requirement | Resulting_Requirement => (Present => False),
         Current_Head | Attempt => (Present => False),
         Current_Epoch => (Present => False),
         Grant => (Action => K.Retry_Evaluation, State => K.Issued,
            Grant | Use_Id | Issuer | Principal | Subject | Content | Transaction |
            Current_Requirement | Expected_Requirement | Reason | Issued_Grant |
            Reserved_Grant | Reserved_Use => (Present => False),
            Failed_Run | Prior_Head | Next_Run => (Present => False),
            Epoch => (Present => False)));
      if not Valid or else Null_Is (Data, Item, At_Layer) then return; end if;
      if not Record_Is (Data, Item, "worldline.owner_transitions", "OwnerRequest", At_Layer) then
         Valid := False; return;
      end if;
      if Text_Is (Data, Field (Data, Item, "action", At_Layer), "RETRY_EVALUATION", At_Layer) then
         Value.Action := K.Retry_Evaluation;
      elsif Text_Is (Data, Field (Data, Item, "action", At_Layer), "ADOPT_REQUIREMENT", At_Layer) then
         Value.Action := K.Adopt_Requirement;
      else Valid := False; return; end if;
      Decode_Identity (Data, Field (Data, Item, "peer", At_Layer), Arena, Valid, Value.Peer, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "owner", At_Layer), Arena, Valid, Value.Owner, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "trusted_issuer", At_Layer), Arena, Valid, Value.Trusted_Issuer, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "subject", At_Layer), Arena, Valid, Value.Subject, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "content", At_Layer), Arena, Valid, Value.Content, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "transaction", At_Layer), Arena, Valid, Value.Transaction, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "current_requirement", At_Layer), Arena, Valid, Value.Current_Requirement, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "resulting_requirement", At_Layer), Arena, Valid, Value.Resulting_Requirement, At_Layer);
      Decode_Cursor (Data, Field (Data, Item, "current_head", At_Layer), Arena, Valid, Value.Current_Head, At_Layer);
      Decode_Cursor (Data, Field (Data, Item, "attempt", At_Layer), Arena, Valid, Value.Attempt, At_Layer);
      Decode_Epoch (Data, Field (Data, Item, "current_epoch", At_Layer), Arena, Valid, Value.Current_Epoch, At_Layer);
      Decode_Grant (Data, Field (Data, Item, "grant", At_Layer), Arena, Valid, Value.Grant, At_Layer);
   end Decode_Request;

   procedure Decode_Receipt
     (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out R.Use_Receipt;
      At_Layer : E.Layer := E.Recovery) is
   begin
      Value := (Consumed => (Action => K.Retry_Evaluation, State => K.Issued,
         Grant | Use_Id | Issuer | Principal | Subject | Content | Transaction |
         Current_Requirement | Expected_Requirement | Reason | Issued_Grant |
         Reserved_Grant | Reserved_Use => (Present => False),
         Failed_Run | Prior_Head | Next_Run => (Present => False),
         Epoch => (Present => False)),
         Issued_Event | Reserved_Event | Consumed_Event | Consumed_Issue |
         Consumed_Reservation => (Present => False));
      if not Valid then return; end if;
      if not Record_Is (Data, Item, "worldline.owner_retry_audit", "UseReceipt", At_Layer) then
         Valid := False; return;
      end if;
      Decode_Grant (Data, Field (Data, Item, "consumed", At_Layer), Arena, Valid, Value.Consumed, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "issued_event", At_Layer), Arena, Valid, Value.Issued_Event, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "reserved_event", At_Layer), Arena, Valid, Value.Reserved_Event, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "consumed_event", At_Layer), Arena, Valid, Value.Consumed_Event, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "consumed_issue", At_Layer), Arena, Valid, Value.Consumed_Issue, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "consumed_reservation", At_Layer), Arena, Valid, Value.Consumed_Reservation, At_Layer);
   end Decode_Receipt;

   procedure Decode_Scope
     (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out C.Full_Scope;
      At_Layer : E.Layer := E.Recovery) is
   begin
      Value := (others => (Present => False));
      if not Valid or else Null_Is (Data, Item, At_Layer) then return; end if;
      if not Record_Is (Data, Item, "worldline.owner_retry_audit", "FullScope", At_Layer) then
         Valid := False; return;
      end if;
      Decode_Identity (Data, Field (Data, Item, "subject", At_Layer), Arena, Valid, Value.Subject, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "content", At_Layer), Arena, Valid, Value.Content, At_Layer);
      Decode_Identity (Data, Field (Data, Item, "transaction", At_Layer), Arena, Valid, Value.Transaction, At_Layer);
   end Decode_Scope;

   procedure Decode_Hash
     (Data : E.Bytes; Item : E.Span; Valid : in out Boolean;
      Value : out CW.Raw_Optional_Hash; At_Layer : E.Layer := E.Recovery)
   is
      Raw : constant E.View := E.Decode (Data, Item, At_Layer);
   begin
      Value := (Present => 0, Value => (others => 0));
      if not Valid or else Raw.Form = E.Null_Value then return; end if;
      if Raw.Form /= E.Bytes_Value or else not E.Bytes_Valid (Data, Raw.Payload) then
         Valid := False; return;
      end if;
      declare Bytes : constant E.Bytes := E.Materialize (Data, Raw.Payload); begin
         if Bytes'Length /= Value.Value'Length then Valid := False; return; end if;
         Value.Present := 1;
         for I in Value.Value'Range loop
            Value.Value (I) := Bytes (Bytes'First + E.Count (I));
         end loop;
      end;
   end Decode_Hash;

   function Audit_Status (Reason : R.Decision) return Status is
   begin
      case Reason is
         when R.Input_Invalid => return Input_Invalid;
         when R.Before_Not_Authorized => return Before_Not_Authorized;
         when R.Prefix_Changed => return Prefix_Changed;
         when R.After_Invalid => return After_Invalid;
         when R.Attempt_Not_Completed_Pass => return Attempt_Not_Completed_Pass;
         when R.Use_Not_Consumed => return Use_Not_Consumed;
         when R.Current_Binding_Changed => return Current_Binding_Changed;
         when R.Ready => return Ready;
      end case;
   end Audit_Status;

   function Join_Status (Reason : C.Decision) return Status is
   begin
      case Reason is
         when C.Input_Invalid => return Input_Invalid;
         when C.Original_Collapse_Denied => return Original_Collapse_Denied;
         when C.Resulting_Requirement_Absent => return Resulting_Requirement_Absent;
         when C.Requirement_Changed => return Requirement_Changed;
         when C.Owner_Scope_Mismatch => return Owner_Scope_Mismatch;
         when C.Owner_Not_Authorized => return Owner_Not_Authorized;
         when C.Retry_Not_Admitted => return Retry_Not_Admitted;
         when C.Ready => return Ready;
      end case;
   end Join_Status;

   procedure Replay_Retry
     (Data : E.Bytes; Owner : E.Span; Arena : in out E.Bytes;
      Before, After : out H.History; Before_Final, After_Final : out H.Optional_Record;
      Audit : out R.Audit; Reason : out Status;
      Facts_Data : E.Bytes; Capsules : E.Span)
   is
      Valid : Boolean := True;
      Before_Valid, After_Valid : Boolean;
      Before_Current : H.Optional_Cursor;
      Prepared : constant E.Span := RA.Field (Data, Owner, "prepared");
   begin
      --  SPARK: the discriminants of these out components are inputs of the
      --  callees below; the caller's object already holds their default False.
      Audit.Current_Head := (Present => False);
      Audit.Current_Epoch := (Present => False);
      M.Classify_All (Data, RA.Field (Data, Owner, "before_material"),
         RA.Field (Data, Owner, "world"), RA.Field (Data, Owner, "requirement"),
         Arena, Before, Before_Final, Before_Current, Before_Valid,
         Facts_Data => Facts_Data, Capsules => Capsules);
      M.Classify_All (Data, RA.Field (Data, Owner, "after_material"),
         RA.Field (Data, Owner, "world"), RA.Field (Data, Owner, "requirement"),
         Arena, After, After_Final, Audit.Current_Head, After_Valid,
         Facts_Data => Facts_Data, Capsules => Capsules);
      Decode_Request (Data, RA.Field (Data, Owner, "request"), Arena, Valid, Audit.Before_Request);
      Decode_Receipt (Data, RA.Field (Data, Owner, "receipt"), Arena, Valid, Audit.Receipt);
      Decode_Epoch (Data, RA.Field (Data, Owner, "current_epoch"), Arena, Valid, Audit.Current_Epoch);
      Audit.Prepared_Evidence := Audit.Current_Head;
      if not Null_Is (Data, Prepared) then
         if E.Decode (Data, Prepared, E.Recovery).Form /= E.Object_Value then
            Valid := False;
         else
            Cursor_Fields (Data, Prepared, Arena, Valid, Audit.Prepared_Evidence, E.Recovery);
         end if;
      end if;
      if not Valid then Reason := Malformed;
      elsif not Before_Valid or else not After_Valid then Reason := Material_Refused;
      else Reason := Audit_Status (R.Decide
         (Arena, Before, After, Before_Final, After_Final, Audit));
      end if;
   end Replay_Retry;

   function Arena_Last (Data : E.Bytes; Owner : E.Span; Retry : Boolean)
      return E.Count with Global => null, Pre => Data'First >= 1,
        Post => Arena_Last'Result >= Data'Last is
      Needed : E.Count := E.Count'Max
        (Data'Length, M.Arena_Length (Data, RA.Field (Data, Owner, "before_material")));
   begin
      if Retry then
         Needed := E.Count'Max (Needed,
           M.Arena_Length (Data, RA.Field (Data, Owner, "after_material")));
      end if;
      --  This is an index-representation check, not an epoch/roster limit.
      --  A material arena which cannot be represented stays undersized and
      --  Classify_All returns its native material refusal.
      if Needed = 0 or else Needed - 1 > E.Count'Last - Data'First then
         return Data'Last;
      end if;
      return Data'First + (Needed - 1);
   end Arena_Last;

   function Matches
     (Data : E.Bytes; Owner, Values, Subject, Primary, Prepared : E.Span;
      Facts_Data : E.Bytes; Capsules : E.Span)
      return Boolean is
   begin
      if Null_Is (Data, Owner) then return True; end if;
      if not Record_Is (Data, Owner, "worldline.owner_collapse_data", "OwnerCollapseData", E.Recovery)
         or else not RA.Valid (Data, Values) then return False; end if;
      if Text_Is (Data, RA.Field (Data, Owner, "mode"), "RETRY_EVALUATION") then
         --  This is the original restore_packet primary-selection branch.
         --  An unused primary remains the responsibility of the native top.
         if Null_Is (Data, Primary) then return True; end if;
         if not RA.Equal (Data, Data, RA.Field (Data, Owner, "world"), Subject)
           or else not RA.Equal (Data, Data, RA.Field (Data, Owner, "after_material"),
               RA.Field (Data, Primary, "authorityMaterial"))
           or else not RA.Equal (Data, Data, RA.Field (Data, Owner, "prepared"), Prepared)
         then return False; end if;
         --  SPARK: refusal exactly where the original raised Constraint_Error: a null
         --  Data whose bounds lie outside the index subtype (Arena_Last or this Arena).
         if Data'First < 1 then return False; end if;
         declare
            Arena : E.Bytes (Data'First .. Arena_Last (Data, Owner, True)) := (others => 0);
            Before : H.History (1 .. M.Row_Count (Data, RA.Field (Data, Owner, "before_material")));
            After : H.History (1 .. M.Row_Count (Data, RA.Field (Data, Owner, "after_material")));
            Before_Final, After_Final : H.Optional_Record;
            Audit : R.Audit;
            Reason : Status;
         begin
            Replay_Retry (Data, Owner, Arena, Before, After, Before_Final,
              After_Final, Audit, Reason, Facts_Data, Capsules);
            return Reason = Ready and then
              M.Owner_Selected (Data, Primary, Owner, Facts_Data, Capsules).Valid;
         end;
      end if;
      return Text_Is (Data, RA.Field (Data, Owner, "mode"), "ADOPT_REQUIREMENT")
        or else Text_Is (Data, RA.Field (Data, Owner, "mode"), "CHECKPOINT_EQUAL");
   end Matches;

   function Same_Operands (Left, Right : CW.Raw_Request) return Boolean is
     (Left.Candidate_State = Right.Candidate_State
      and then Left.Phase = Right.Phase
      and then Left.Evaluation_Mode = Right.Evaluation_Mode
      and then Left.Conflicts = Right.Conflicts
      and then Left.Foreign_Writes = Right.Foreign_Writes
      and then Left.Expected_Parent = Right.Expected_Parent
      and then Left.Candidate_Parent = Right.Candidate_Parent
      and then Left.Expected_Subject = Right.Expected_Subject
      and then Left.Evidence_Subject = Right.Evidence_Subject
      and then Left.Expected_Base = Right.Expected_Base
      and then Left.Candidate_Base = Right.Candidate_Base
      and then Left.Expected_Delta = Right.Expected_Delta
      and then Left.Candidate_Delta = Right.Candidate_Delta
      and then Left.Expected_Root_Set = Right.Expected_Root_Set
      and then Left.Candidate_Root_Set = Right.Candidate_Root_Set
      and then Left.Expected_Staged_Root = Right.Expected_Staged_Root
      and then Left.Actual_Staged_Root = Right.Actual_Staged_Root
      and then Left.Staged_Content_Root = Right.Staged_Content_Root
      and then Left.Tested_Root = Right.Tested_Root
      and then Left.Current_Requirement = Right.Current_Requirement
      and then Left.Resulting_Requirement = Right.Resulting_Requirement
      and then Left.Evaluated_Requirement = Right.Evaluated_Requirement
      and then Left.Declared_Verifiers = Right.Declared_Verifiers
      and then Left.Executed_Verifiers = Right.Executed_Verifiers
      and then Left.Staged_Evaluated_Requirement = Right.Staged_Evaluated_Requirement
      and then Left.Staged_Executed_Verifiers = Right.Staged_Executed_Verifiers
      and then Left.Staged_Examined_Root = Right.Staged_Examined_Root
      and then Left.Expected_Checkpoint = Right.Expected_Checkpoint
      and then Left.Witnessed_Checkpoint = Right.Witnessed_Checkpoint
      and then Left.Registered_Watch_Set = Right.Registered_Watch_Set
      and then Left.Watched_Set = Right.Watched_Set
      and then Left.Generation_Before = Right.Generation_Before
      and then Left.Generation_After = Right.Generation_After);

   function Decide
     (Data : E.Bytes; Owner, Values : E.Span; Derived : CW.Raw_Request;
      Facts_Data : E.Bytes; Capsules : E.Span)
      return Status
   is
      Original : constant V.Collapse_Values_Result := V.Decode_Recovery_Collapse_Values (Data, Values);
   begin
      if Null_Is (Data, Owner) then return Ready; end if;
      if not Record_Is (Data, Owner, "worldline.owner_collapse_data", "OwnerCollapseData", E.Recovery)
         or else not Original.Present or else not Same_Operands (Original.Raw, Derived)
         or else not CW.Well_Formed (Derived) then return Malformed; end if;
      if Text_Is (Data, RA.Field (Data, Owner, "mode"), "RETRY_EVALUATION") then
         --  SPARK: refusal exactly where the original raised Constraint_Error: a null
         --  Data whose bounds lie outside the index subtype (Arena_Last or this Arena).
         if Data'First < 1 then return Malformed; end if;
         declare
            Arena : E.Bytes (Data'First .. Arena_Last (Data, Owner, True)) := (others => 0);
            Before : H.History (1 .. M.Row_Count (Data, RA.Field (Data, Owner, "before_material")));
            After : H.History (1 .. M.Row_Count (Data, RA.Field (Data, Owner, "after_material")));
            Before_Final, After_Final : H.Optional_Record;
            Audit : R.Audit;
            Scope : C.Full_Scope;
            Reason : Status;
            Valid : Boolean := True;
         begin
            Replay_Retry (Data, Owner, Arena, Before, After, Before_Final,
              After_Final, Audit, Reason, Facts_Data, Capsules);
            if Reason /= Ready then return Reason; end if;
            Decode_Scope (Data, RA.Field (Data, Owner, "scope"), Arena, Valid, Scope);
            if not Valid then return Malformed; end if;
            if Derived.Roster_Complete /= 1 or else
              not M.Owner_Promotion (Data, Owner, Facts_Data, Capsules) then
               return Original_Collapse_Denied;
            end if;
            return Join_Status (C.Authorize_Retry
              (Arena, Before, After, Before_Final, After_Final, CW.Decode (Derived), Scope, Audit));
         end;
      elsif Text_Is (Data, RA.Field (Data, Owner, "mode"), "ADOPT_REQUIREMENT")
         or else Text_Is (Data, RA.Field (Data, Owner, "mode"), "CHECKPOINT_EQUAL") then
         --  SPARK: refusal exactly where the original raised Constraint_Error: a null
         --  Data whose bounds lie outside the index subtype (Arena_Last or this Arena).
         if Data'First < 1 and then Text_Is (Data, RA.Field (Data, Owner, "mode"), "ADOPT_REQUIREMENT") then
            return Malformed;
         end if;
         declare
            Adopt : constant Boolean := Text_Is (Data, RA.Field (Data, Owner, "mode"), "ADOPT_REQUIREMENT");
            Count : constant E.Count := (if Adopt then M.Row_Count
              (Data, RA.Field (Data, Owner, "before_material")) else 0);
            Arena : E.Bytes (Data'First ..
              (if Adopt then Arena_Last (Data, Owner, False) else Data'Last)) := (others => 0);
            Rows : H.History (1 .. Count) with Relaxed_Initialization;
            Finalization : H.Optional_Record := (Present => False);
            Current : H.Optional_Cursor;
            Scope : C.Full_Scope;
            Request : K.Request;
            Optional_Adopt : C.Optional_Adopt := (Present => False);
            Resulting : CW.Raw_Optional_Hash;
            Valid, Material_Valid : Boolean := True;
         begin
            Decode_Scope (Data, RA.Field (Data, Owner, "scope"), Arena, Valid, Scope);
            Decode_Hash (Data, RA.Field (Data, Owner, "resulting"), Valid, Resulting);
            if Adopt then
               M.Classify_All (Data, RA.Field (Data, Owner, "before_material"),
                 RA.Field (Data, Owner, "world"), RA.Field (Data, Owner, "requirement"),
                 Arena, Rows, Finalization, Current, Material_Valid,
                 Facts_Data => Facts_Data, Capsules => Capsules);
               Decode_Request (Data, RA.Field (Data, Owner, "request"), Arena, Valid, Request);
               --  Python's original None request stays an absent Optional_Adopt.
               if not Null_Is (Data, RA.Field (Data, Owner, "request")) then
                  Optional_Adopt := (Present => True, Value => Request);
               end if;
            end if;
            if not Valid then return Malformed; end if;
            if not Material_Valid then return Material_Refused; end if;
            if not CW.Hash_Well_Formed (Resulting) then return Input_Invalid; end if;
            return Join_Status (C.Authorize_Checkpoint
              (Arena, Rows, Finalization, CW.Decode (Derived), CW.Requirement (Resulting), Scope, Optional_Adopt));
         end;
      else return Malformed;
      end if;
   end Decide;
end Worldline.Recovery_Owner_Replay;

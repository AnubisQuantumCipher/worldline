with Evaluation_Finalization;
with Worldline.Collapse;
with Worldline.Collapse_Wire;
with Worldline.Evaluation_Authority;
with System.Address_To_Access_Conversions;
with System.Storage_Elements;

package body Evaluation_Finalization_C with SPARK_Mode => Off is
   package F renames Evaluation_Finalization;
   package T renames F.T;
   package P renames F.P;
   package R renames F.R;
   package H renames F.H;
   package W renames F.W;
   package K renames Evaluation_Completion_C;
   package CW renames Worldline.Collapse_Wire;
   package Authority renames Worldline.Evaluation_Authority;
   use type Interfaces.C.int;
   use type Authority.Raw_Dependency;
   use type System.Address;
   use type I64;
   use type U32;
   use type U8;
   use type P.Count;
   use type F.Capture_Decision;
   use type F.Seal_Decision;
   use System.Storage_Elements;
   package Requests is new System.Address_To_Access_Conversions (Request);
   package Outputs is new System.Address_To_Access_Conversions (Result);
   package Rows is new System.Address_To_Access_Conversions (Row);
   package Plans is new System.Address_To_Access_Conversions (Required_Row);
   package Octets is new System.Address_To_Access_Conversions (P.Byte);

   function Version return U32 is (1);
   function Extent_Valid (A : System.Address; Length, Alignment : I64)
      return Boolean is
     (Length >= 0 and then Alignment > 0
      and then Length <= I64 (Storage_Offset'Last)
      and then (Length = 0 or else
        (A /= System.Null_Address
         and then To_Integer (A) mod Integer_Address (Alignment) = 0
         and then Integer_Address (Length - 1) <= Integer_Address'Last - To_Integer (A))));
   function Disjoint (L : System.Address; LL : I64; R : System.Address; RL : I64)
      return Boolean is
     (LL = 0 or else RL = 0 or else
       (if To_Integer (L) <= To_Integer (R) then
          Integer_Address (LL) <= To_Integer (R) - To_Integer (L)
        else Integer_Address (RL) <= To_Integer (L) - To_Integer (R)));
   function Array_Valid (A : System.Address; N, Stride, Alignment : I64;
                         Output : System.Address; Output_Length : I64)
      return Boolean is
     (N >= 0 and then Stride > 0
      and then N <= I64 (Storage_Offset'Last) / Stride
      and then Extent_Valid (A, N * Stride, Alignment)
      and then Disjoint (A, N * Stride, Output, Output_Length));
   function Valid (S : Span) return Boolean is (S.First >= 1 and then S.Length >= 0);
   function Valid (S : Optional_Span) return Boolean is
     (S.Present <= 1 and then (S.Present = 0 or else Valid (S.Value)));
   function Valid (S : Start_Record) return Boolean is
     (Valid (S.Store_Id) and then Valid (S.Subject) and then Valid (S.Run)
      and then Valid (S.Sequence) and then Valid (S.Requirement)
      and then Valid (S.Policy) and then Valid (S.Verifier_Plan)
      and then Valid (S.Base_Context) and then Valid (S.Required)
      and then S.Declaration <= U32 (R.Declaration'Pos (R.Declaration'Last)));
   function Valid (I : Input_Record) return Boolean is
     (Valid (I.Start) and then Valid (I.Root) and then Valid (I.Manifests));
   function Valid (X : Row) return Boolean is
     (Valid (X.Start) and then Valid (X.Check_Id) and then Valid (X.Source_Id)
      and then Valid (X.Execution) and then Valid (X.Verifier)
      and then Valid (X.Payload) and then Valid (X.Declared)
      and then X.State <= U32 (T.E.Execution_State'Pos (T.E.Execution_State'Last))
      and then X.Outcome <= U32 (T.E.Outcome'Pos (T.E.Outcome'Last)));
   function Convert (S : Span) return P.Span is
     (First => P.Index (S.First), Length => P.Count (S.Length));
   function Convert (S : Optional_Span) return T.Optional_Requirement is
     (if S.Present = 0 then (Present => False)
      else (True, T.Requirement_Identity (Convert (S.Value))));
   function Convert (X : Digest) return Worldline.Hash is
      Result : Worldline.Hash;
   begin
      for K in Result'Range loop Result (K) := X (K); end loop;
      return Result;
   end Convert;
   function Convert (S : Start_Record) return F.Start_Record is
     (Store => T.Store_Identity (Convert (S.Store_Id)),
      Subject => T.Subject_Identity (Convert (S.Subject)),
      Run => T.Run_Identity (Convert (S.Run)), Sequence => T.Epoch (Convert (S.Sequence)),
      Requirement => Convert (S.Requirement),
      Policy => T.Captured_Bytes (Convert (S.Policy)),
      Verifier_Plan => T.Captured_Bytes (Convert (S.Verifier_Plan)),
      Base_Context => T.Captured_Bytes (Convert (S.Base_Context)),
      Parent => Convert (S.Parent), Config => Convert (S.Config),
      Repository => Convert (S.Repository),
      Required => (T.Index (S.Required.First), T.Count (S.Required.Length)),
      Declaration => R.Declaration'Val (S.Declaration));
   function Convert (I : Input_Record) return F.Input_Record is
     (Start => Convert (I.Start), Root => T.Captured_Bytes (Convert (I.Root)),
      Manifests => T.Captured_Bytes (Convert (I.Manifests)),
      Filesystem => Convert (I.Filesystem), Config => Convert (I.Config),
      Repository => Convert (I.Repository));
   function Convert (X : Row) return F.Start_Row is
     (Start => Convert (X.Start), Check => T.Check_Identity (Convert (X.Check_Id)),
      Source => T.Source_Identity (Convert (X.Source_Id)),
      Execution => (if X.Execution.Present = 0 then (Present => False)
        else (True, T.Execution_Identity (Convert (X.Execution.Value)))),
      Verifier => (if X.Verifier.Present = 0 then (Present => False)
        else (True, T.Verifier_Identity (Convert (X.Verifier.Value)))),
      State => T.E.Execution_State'Val (X.State), Outcome => T.E.Outcome'Val (X.Outcome),
      Payload => T.Captured_Bytes (Convert (X.Payload)),
      Declared => T.Captured_Bytes (Convert (X.Declared)),
      Raw => X.Raw, Confinement => X.Confinement);
   function Copy_Data (Address : System.Address; Length : I64) return P.Bytes is
      Data : P.Bytes (1 .. P.Count (Length));
   begin
      for I in Data'Range loop
         Data (I) := Octets.To_Pointer (Address + Storage_Offset (I - 1)).all;
      end loop;
      return Data;
   end Copy_Data;

   function Decide (Input, Output : System.Address) return Interfaces.C.int is
      Input_Size : constant I64 := Request'Object_Size / System.Storage_Unit;
      Output_Size : constant I64 := Result'Object_Size / System.Storage_Unit;
      Row_Size : constant I64 := Row'Object_Size / System.Storage_Unit;
      Plan_Size : constant I64 := Required_Row'Object_Size / System.Storage_Unit;
   begin
      K.Diagnostic_Mark ("finalization.decide.enter");
      if not Extent_Valid (Input, Input_Size, Request'Alignment)
        or else not Extent_Valid (Output, Output_Size, Result'Alignment)
        or else not Disjoint (Input, Input_Size, Output, Output_Size)
      then
         K.Diagnostic_Mark ("finalization.decide.input-extents-rejected");
         return 255;
      end if;
      declare
         X : constant Request := Requests.To_Pointer (Input).all;
      begin
         if X.Version /= 1 or else X.Operation > 3
           or else not Extent_Valid (X.Data, X.Data_Length, P.Byte'Alignment)
           or else not Disjoint (X.Data, X.Data_Length, Output, Output_Size)
           or else not Array_Valid (X.Required, X.Required_Count, Plan_Size,
             Required_Row'Alignment, Output, Output_Size)
           or else not Array_Valid (X.Rows, X.Row_Count, Row_Size,
             Row'Alignment, Output, Output_Size)
           or else not Valid (X.Start)
           or else (X.Operation >= 1 and then not Valid (X.Inputs))
           or else (X.Operation >= 2 and then
             (not Valid (X.Post_Root) or else not Valid (X.Post_Manifests)
              or else not Valid (X.Completion.Check_Id)
              or else not Valid (X.Completion.Declared)))
           or else (X.Operation = 3 and then
             (not Valid (X.Content) or else not Valid (X.Context) or else not Valid (X.Source_Id)
              or else not Valid (X.Evidence) or else not Valid (X.Environment)))
         then
            K.Diagnostic_Mark ("finalization.decide.transport-guard-rejected");
            return 255;
         end if;
         K.Diagnostic_Mark ("finalization.decide.copy-arena");
         declare
            A : constant P.Bytes := Copy_Data (X.Data, X.Data_Length);
            Required : R.Check_Array (1 .. P.Count (X.Required_Count));
            Captured : F.Start_Rows (1 .. P.Count (X.Row_Count));
            S : constant F.Start_Record := Convert (X.Start);
            Response : Result := (Reason => 1, State => 0, Outcome => 0,
              Promotion => 0, Finalization_State => 0,
              Finalization_Outcome => 0, Identity => (others => 0));
         begin
            for K in Required'Range loop
               declare
                  Q : constant Required_Row := Plans.To_Pointer
                    (X.Required + Storage_Offset (I64 (K - 1) * Plan_Size)).all;
               begin
                  if not Valid (Q.Check_Id) or else not Valid (Q.Declared)
                  then
                     Evaluation_Completion_C.Diagnostic_Value
                       ("finalization.decide.required-rejected", I64 (K));
                     return 255;
                  end if;
                  Required (K) := (T.Check_Identity (Convert (Q.Check_Id)),
                    T.Captured_Bytes (Convert (Q.Declared)));
               end;
            end loop;
            if X.Operation = 0 then
               if F.Start_Valid (A, S, Required) then Response.Reason := 0; end if;
            elsif X.Operation = 1 then
               if F.Input_Valid (A, S, Convert (X.Inputs), Required)
               then Response.Reason := 0; end if;
            else
               for K in Captured'Range loop
                  declare
                     Q : constant Row := Rows.To_Pointer
                       (X.Rows + Storage_Offset (I64 (K - 1) * Row_Size)).all;
                  begin
                     if not Valid (Q) then
                        Evaluation_Completion_C.Diagnostic_Value
                          ("finalization.decide.row-rejected", I64 (K));
                        return 255;
                     end if;
                     Captured (K) := Convert (Q);
                  end;
               end loop;
               if X.Operation = 2 then
                  declare
                     Classified : constant F.Capture_Result := F.Classify_Capture
                       (A, S, Convert (X.Inputs), T.Captured_Bytes (Convert (X.Post_Root)),
                        T.Captured_Bytes (Convert (X.Post_Manifests)), Captured, Required,
                        (T.Check_Identity (Convert (X.Completion.Check_Id)),
                         T.Captured_Bytes (Convert (X.Completion.Declared))));
                  begin
                     if Classified.Reason = F.Capture_Observed then
                        Response.Reason := 0;
                        Response.State := U32 (W.E.Execution_State'Pos (Classified.Classification.State));
                        Response.Outcome := U32 (W.E.Outcome'Pos (Classified.Classification.Outcome));
                        Response.Promotion := Boolean'Pos (Classified.Classification.Promotion_Ready);
                     end if;
                  end;
               else
                  declare
                     Sealed : constant F.Seal_Result := F.Seal
                       (A, S, Convert (X.Inputs), T.Captured_Bytes (Convert (X.Post_Root)),
                        T.Captured_Bytes (Convert (X.Post_Manifests)), Captured, Required,
                        (T.Check_Identity (Convert (X.Completion.Check_Id)),
                         T.Captured_Bytes (Convert (X.Completion.Declared))),
                        T.Content_Identity (Convert (X.Content)),
                        (Convert (X.Environment_Root), Convert (X.Evidence_Root)),
                        (T.Captured_Bytes (Convert (X.Context)),
                         T.Captured_Bytes (Convert (X.Source_Id)),
                         T.Captured_Bytes (Convert (X.Evidence)),
                         T.Captured_Bytes (Convert (X.Environment))));
                  begin
                     if Sealed.Reason = F.Seal_Observed then
                        Response.Reason := 0;
                        Response.State := U32 (W.E.Execution_State'Pos (Sealed.Classification.State));
                        Response.Outcome := U32 (W.E.Outcome'Pos (Sealed.Classification.Outcome));
                        Response.Promotion := Boolean'Pos (Sealed.Classification.Promotion_Ready);
                        Response.Finalization_State := U32 (H.Lifecycle'Pos (Sealed.Finalization.Value.State));
                        Response.Finalization_Outcome := U32 (H.Verdict'Pos (Sealed.Finalization.Value.Outcome));
                        for K in Response.Identity'Range loop
                           Response.Identity (K) := Sealed.Identity (K);
                        end loop;
                     elsif Sealed.Reason = F.Content_Mismatch then
                        Response.Reason := 2;
                     end if;
                  end;
               end if;
            end if;
            K.Diagnostic_Value ("finalization.decide.reason", I64 (Response.Reason));
            K.Diagnostic_Value ("finalization.decide.promotion", I64 (Response.Promotion));
            Outputs.To_Pointer (Output).all := Response;
            return 0;
         end;
      end;
   exception
      when Error : others =>
         K.Diagnostic_Exception ("finalization.decide", Error);
         return 255;
   end Decide;

   -- Context-only view of the validated late binding. This projection is
   -- never dispatched to ordinary Decide/Raw_Decide and has no journal entry.
   function Final_Context_Matches
     (Input, Metadata, Collapse, Agent : System.Address; Agent_Confinement : U8)
      return Boolean is
      Native : aliased Result;
      Plan_Size : constant I64 := Required_Row'Object_Size / System.Storage_Unit;
      Row_Size : constant I64 := Row'Object_Size / System.Storage_Unit;
      type Check_Array is array (P.Index range <>) of aliased K.Check_Row
        with Convention => C;
      type Plan_Array is array (P.Index range <>) of aliased K.Required_Row
        with Convention => C;
   begin
      K.Diagnostic_Mark ("finalization.context.enter");
      if Decide (Input, Native'Address) /= 0 or else Native.Reason /= 0
        or else Native.Promotion /= 1
      then
         K.Diagnostic_Mark ("finalization.context.seal-rejected");
         return False;
      end if;
      declare
         X : constant Request := Requests.To_Pointer (Input).all;
      begin
         if X.Operation /= 3 or else not Valid (X.Start.Required)
           or else X.Start.Required.Length > X.Required_Count
           or else (X.Start.Required.Length /= 0 and then
             (X.Start.Required.First > X.Required_Count or else
              X.Start.Required.Length - 1 > X.Required_Count - X.Start.Required.First))
         then
            K.Diagnostic_Mark ("finalization.context.required-extent-rejected");
            return False;
         end if;
         declare
            Projected_Rows : aliased Check_Array (1 .. P.Count (X.Row_Count));
            Projected_Plans : aliased Plan_Array (1 .. P.Count (X.Start.Required.Length));
            Bound : constant K.Binding := (X.Start.Store_Id, X.Start.Subject,
              X.Content, X.Start.Run, X.Start.Sequence, X.Start.Requirement);
            Empty_Capture : constant K.Capture :=
              (Bound, X.Source_Id, X.Context, 0, 0);
            Projection : aliased K.Request;
         begin
            for I in Projected_Rows'Range loop
               declare
                  Original : constant Row := Rows.To_Pointer
                    (X.Rows + Storage_Offset (I64 (I - 1) * Row_Size)).all;
               begin
                  -- The original typed Start/row equality was checked above.
                  -- Here only the additive final binding is introduced.
                  Projected_Rows (I) :=
                    (Bound, Original.Check_Id, Original.Source_Id,
                     Original.Execution, Original.Verifier, Original.State,
                     Original.Outcome, Original.Payload, (others => 0), 0,
                     (others => 0), Original.Declared);
               end;
            end loop;
            for I in Projected_Plans'Range loop
               Projected_Plans (I) := Plans.To_Pointer
                 (X.Required + Storage_Offset
                   ((X.Start.Required.First - 1 + I64 (I - 1)) * Plan_Size)).all;
            end loop;
            Projection := (Version => 1, Operation => 2,
              Data => X.Data, Data_Length => X.Data_Length,
              Journal => System.Null_Address, Journal_Count => 0,
              Current => (1, X.Start.Sequence, X.Start.Run),
              Captured => (Bound, X.Source_Id, X.Context, Native.State, Native.Outcome),
              Captured_Results => Projected_Rows'Address, Captured_Count => X.Row_Count,
              Retained_Present => 0, Retained => Empty_Capture,
              Retained_Results => System.Null_Address, Retained_Count => 0,
              History => System.Null_Address, History_Count => 0,
              Required => Projected_Plans'Address, Required_Count => X.Start.Required.Length,
              Policy => X.Start.Declaration, Before_Root => X.Inputs.Root,
              After_Root => X.Post_Root, Completion => X.Completion,
              Observed_Binding => Bound);
            K.Diagnostic_Mark ("finalization.context.projected");
            declare
               Context_Result : constant Interfaces.C.int := K.Context_Matches
                 (Projection'Address, K.Metadata_Base (Metadata), Collapse,
                  Agent, Agent_Confinement);
            begin
               K.Diagnostic_Value ("finalization.context.context-result", I64 (Context_Result));
               if Context_Result /= 1 then return False; end if;
               declare
                  Metadata_Result : constant Interfaces.C.int :=
                    K.Metadata_Matches (Projection'Address, Metadata);
               begin
                  K.Diagnostic_Value
                    ("finalization.context.metadata-result", I64 (Metadata_Result));
                  return Metadata_Result = 1;
               end;
            end;
         end;
      end;
   exception
      when Error : others =>
         K.Diagnostic_Exception ("finalization.context", Error);
         return False;
   end Final_Context_Matches;

   function Decide_Mixed
     (Collapse : System.Address; Primary_Kind : U32;
      Primary, Primary_Raw, Primary_Confinement, Primary_Context : System.Address;
      Staged_Kind : U32;
      Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address;
      Agent_Confinement : U8) return U8 is
      package Collapse_Requests is new System.Address_To_Access_Conversions (CW.Raw_Request);
      package Raw_Records is new System.Address_To_Access_Conversions (W.Raw_Record);
      P_Ready, S_Ready, Agent_Ready : U8 := 0;
      function Read_Ready
        (Kind : U32; Input, Raw, Confined : System.Address; Ready : out U8)
         return Boolean is
         Ordinary : aliased K.Result;
         Finalized : aliased Result;
      begin
         Ready := 0;
         if Kind = 0 then return True; end if;
         if Kind = 1 then
            if K.Raw_Decide (Input, Raw, Confined, Ordinary'Address) /= 0
              or else Ordinary.Promotion > 1
              or else Ordinary.Reason not in
                T.Decision'Pos (T.Retain_Terminal) | T.Decision'Pos (T.Already_Retained)
            then return False; end if;
            Ready := U8 (Ordinary.Promotion);
         elsif Kind = 2 then
            if Decide (Input, Finalized'Address) /= 0 or else Finalized.Reason /= 0
              or else Finalized.Promotion > 1
            then return False; end if;
            declare
               X : constant Request := Requests.To_Pointer (Input).all;
            begin
               if X.Operation /= 3 then return False; end if;
            end;
            Ready := U8 (Finalized.Promotion);
         else return False;
         end if;
         return True;
      end Read_Ready;
      function Context_Joined
        (Kind : U32; Input, Metadata : System.Address) return Boolean is
      begin
         if Kind = 1 then
            return K.Context_Matches
              (Input, K.Metadata_Base (Metadata), Collapse, Agent, Agent_Confinement) = 1;
         elsif Kind = 2 then
            return Final_Context_Matches (Input, Metadata, Collapse, Agent, Agent_Confinement);
         else return False;
         end if;
      end Context_Joined;
   begin
      K.Diagnostic_Mark ("finalization.mixed.enter");
      if not Extent_Valid (Collapse, CW.Raw_Request'Object_Size / System.Storage_Unit,
                           CW.Raw_Request'Alignment)
      then
         K.Diagnostic_Mark ("finalization.mixed.collapse-extent-rejected");
         return CW.Invalid_Request;
      end if;
      declare
         Bound : CW.Raw_Request := Collapse_Requests.To_Pointer (Collapse).all;
         Needed : constant Authority.Raw_Dependency := Authority.Dependencies (Bound);
         Decision : U8;
      begin
         if Needed = Authority.Invalid_Collapse then
            K.Diagnostic_Mark ("finalization.mixed.dependency-rejected");
            return CW.Invalid_Request;
         end if;
         if Authority.Needs_Primary (Needed) and then
           not Read_Ready (Primary_Kind, Primary, Primary_Raw, Primary_Confinement, P_Ready)
         then
            K.Diagnostic_Mark ("finalization.mixed.primary-ready-rejected");
            return CW.Invalid_Request;
         end if;
         if Authority.Needs_Staged (Needed) and then
           not Read_Ready (Staged_Kind, Staged, Staged_Raw, Staged_Confinement, S_Ready)
         then
            K.Diagnostic_Mark ("finalization.mixed.staged-ready-rejected");
            return CW.Invalid_Request;
         end if;
         K.Diagnostic_Value ("finalization.mixed.primary-ready", I64 (P_Ready));
         K.Diagnostic_Value ("finalization.mixed.staged-ready", I64 (S_Ready));
         if Authority.Needs_Agent (Needed) and then Agent /= System.Null_Address then
            if not Extent_Valid (Agent, W.Raw_Record'Object_Size / System.Storage_Unit,
                                W.Raw_Record'Alignment)
            then
               K.Diagnostic_Mark ("finalization.mixed.agent-extent-rejected");
               return CW.Invalid_Request;
            end if;
            declare
               Owned_Agent : constant W.Raw_Record := Raw_Records.To_Pointer (Agent).all;
            begin
               Agent_Ready := W.Confined_Admit_Wire (Owned_Agent, Agent_Confinement);
               if Agent_Ready = W.Invalid_Record then
                  K.Diagnostic_Mark ("finalization.mixed.agent-record-rejected");
                  return CW.Invalid_Request;
               end if;
               if Owned_Agent.Observations (W.Source_Field) /= W.E.Origin'Pos (W.E.Agent)
               then Agent_Ready := 0; end if;
            end;
         end if;
         K.Diagnostic_Value ("finalization.mixed.agent-ready", I64 (Agent_Ready));
         if Agent_Ready = 1 then
            if P_Ready = 1 and then not Context_Joined (Primary_Kind, Primary, Primary_Context)
            then
               K.Diagnostic_Mark ("finalization.mixed.primary-context-rejected");
               return CW.Invalid_Request;
            end if;
            if S_Ready = 1 and then not Context_Joined (Staged_Kind, Staged, Staged_Context)
            then
               K.Diagnostic_Mark ("finalization.mixed.staged-context-rejected");
               return CW.Invalid_Request;
            end if;
         end if;
         Bound.Roster_Complete := (if Agent_Ready = 1 then P_Ready else 0);
         Bound.Staged_Roster_Complete := (if Agent_Ready = 1 then S_Ready else 0);
         Decision := CW.Decide_Wire (Bound);
         K.Diagnostic_Value ("finalization.mixed.collapse-decision", I64 (Decision));
         if Decision /= U8 (Worldline.Collapse.Decision'Pos (Worldline.Collapse.Authorized))
         then return Decision; end if;
         if Authority.Needs_Primary (Needed) and then Primary_Kind = 1
           and then K.Metadata_Matches (Primary, Primary_Context) /= 1
         then
            K.Diagnostic_Mark ("finalization.mixed.primary-metadata-rejected");
            return CW.Invalid_Request;
         end if;
         if Authority.Needs_Staged (Needed) and then Staged_Kind = 1
           and then K.Metadata_Matches (Staged, Staged_Context) /= 1
         then
            K.Diagnostic_Mark ("finalization.mixed.staged-metadata-rejected");
            return CW.Invalid_Request;
         end if;
         return Decision;
      end;
   exception
      when Error : others =>
         K.Diagnostic_Exception ("finalization.mixed", Error);
         return CW.Invalid_Request;
   end Decide_Mixed;

   function Layout (Kind, Field : U32) return I64 is
      S : Start_Record;
      I : Input_Record;
      Q : Row;
      X : Request;
      Y : Result;
   begin
      case Kind is
         when 1 => return (case Field is
           when 0 => Start_Record'Object_Size / System.Storage_Unit,
           when 1 => Start_Record'Alignment,
           when 2 => S.Store_Id'Position, when 3 => S.Subject'Position,
           when 4 => S.Run'Position, when 5 => S.Sequence'Position,
           when 6 => S.Requirement'Position, when 7 => S.Policy'Position,
           when 8 => S.Verifier_Plan'Position, when 9 => S.Base_Context'Position,
           when 10 => S.Parent'Position, when 11 => S.Config'Position,
           when 12 => S.Repository'Position, when 13 => S.Required'Position,
           when 14 => S.Declaration'Position, when others => I64'Last);
         when 2 => return (case Field is
           when 0 => Input_Record'Object_Size / System.Storage_Unit,
           when 1 => Input_Record'Alignment,
           when 2 => I.Start'Position, when 3 => I.Root'Position,
           when 4 => I.Manifests'Position, when 5 => I.Filesystem'Position,
           when 6 => I.Config'Position, when 7 => I.Repository'Position,
           when others => I64'Last);
         when 3 => return (case Field is
           when 0 => Row'Object_Size / System.Storage_Unit,
           when 1 => Row'Alignment,
           when 2 => Q.Start'Position, when 3 => Q.Check_Id'Position,
           when 4 => Q.Source_Id'Position, when 5 => Q.Execution'Position,
           when 6 => Q.Verifier'Position, when 7 => Q.State'Position,
           when 8 => Q.Outcome'Position, when 9 => Q.Payload'Position,
           when 10 => Q.Declared'Position, when 11 => Q.Raw'Position,
           when 12 => Q.Confinement'Position, when others => I64'Last);
         when 4 => return (case Field is
           when 0 => Request'Object_Size / System.Storage_Unit,
           when 1 => Request'Alignment,
           when 2 => X.Version'Position, when 3 => X.Operation'Position,
           when 4 => X.Data'Position, when 5 => X.Data_Length'Position,
           when 6 => X.Start'Position, when 7 => X.Inputs'Position,
           when 8 => X.Post_Root'Position, when 9 => X.Post_Manifests'Position,
           when 10 => X.Rows'Position, when 11 => X.Row_Count'Position,
           when 12 => X.Required'Position, when 13 => X.Required_Count'Position,
           when 14 => X.Completion'Position, when 15 => X.Content'Position,
           when 16 => X.Environment_Root'Position, when 17 => X.Evidence_Root'Position,
           when 18 => X.Context'Position, when 19 => X.Source_Id'Position,
           when 20 => X.Evidence'Position, when 21 => X.Environment'Position, when others => I64'Last);
         when 5 => return (case Field is
           when 0 => Result'Object_Size / System.Storage_Unit,
           when 1 => Result'Alignment,
           when 2 => Y.Reason'Position, when 3 => Y.State'Position,
           when 4 => Y.Outcome'Position, when 5 => Y.Promotion'Position,
           when 6 => Y.Finalization_State'Position, when 7 => Y.Finalization_Outcome'Position,
           when 8 => Y.Identity'Position, when others => I64'Last);
         when others => return I64'Last;
      end case;
   end Layout;
end Evaluation_Finalization_C;

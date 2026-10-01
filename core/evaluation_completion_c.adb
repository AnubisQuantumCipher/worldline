with Evaluation_Pending;
with Evaluation_Pending_V2;
with Evaluation_Completion;
with Evaluation_Completion_Roster;
with Evaluation_History;
with Worldline.Evaluation;
with System.Address_To_Access_Conversions;
with System.Storage_Elements;
package body Evaluation_Completion_C with SPARK_Mode => Off is
   package P renames Evaluation_Pending;
   package V renames Evaluation_Pending_V2;
   package T renames Evaluation_Completion;
   package H renames Evaluation_History;
   package E renames Worldline.Evaluation;
   package Roster renames Evaluation_Completion_Roster;
   use type System.Address;
   use type I64;
   use type U32;
   use type P.Count;
   use type H.Byte_Count;
   use type T.Decision;
   use System.Storage_Elements;
   package Requests is new System.Address_To_Access_Conversions (Request);
   package Outputs is new System.Address_To_Access_Conversions (Result);
   package Journals is new System.Address_To_Access_Conversions (Journal_Row);
   package Checks is new System.Address_To_Access_Conversions (Check_Row);
   package Histories is new System.Address_To_Access_Conversions (History_Row);
   package Requirements is new System.Address_To_Access_Conversions (Required_Row);
   package Octets is new System.Address_To_Access_Conversions (P.Byte);
   function ABI_Version return U32 is (1);
   function Layout_Size (Kind : U32) return I64 is
     (case Kind is
        when 1 => Span'Object_Size / System.Storage_Unit,
        when 2 => Optional_Span'Object_Size / System.Storage_Unit,
        when 3 => Cursor'Object_Size / System.Storage_Unit,
        when 4 => Binding'Object_Size / System.Storage_Unit,
        when 5 => Journal_Row'Object_Size / System.Storage_Unit,
        when 6 => Capture'Object_Size / System.Storage_Unit,
        when 7 => Facts'Object_Size / System.Storage_Unit,
        when 8 => Presence'Object_Size / System.Storage_Unit,
        when 9 => Required_Row'Object_Size / System.Storage_Unit,
        when 10 => Check_Row'Object_Size / System.Storage_Unit,
        when 11 => History_Row'Object_Size / System.Storage_Unit,
        when 12 => Request'Object_Size / System.Storage_Unit,
        when 13 => Result'Object_Size / System.Storage_Unit,
        when others => I64'Last);
   function Layout_Alignment (Kind : U32) return I64 is
     (case Kind is
        when 1 => Span'Alignment,
        when 2 => Optional_Span'Alignment,
        when 3 => Cursor'Alignment,
        when 4 => Binding'Alignment,
        when 5 => Journal_Row'Alignment,
        when 6 => Capture'Alignment,
        when 7 => Facts'Alignment,
        when 8 => Presence'Alignment,
        when 9 => Required_Row'Alignment,
        when 10 => Check_Row'Alignment,
        when 11 => History_Row'Alignment,
        when 12 => Request'Alignment,
        when 13 => Result'Alignment,
        when others => I64'Last);
   function Layout_Offset (Kind, Field : U32) return I64 is
      X_Span : Span;
      X_Optional_Span : Optional_Span;
      X_Cursor : Cursor;
      X_Binding : Binding;
      X_Journal_Row : Journal_Row;
      X_Capture : Capture;
      X_Facts : Facts;
      X_Presence : Presence;
      X_Required_Row : Required_Row;
      X_Check_Row : Check_Row;
      X_History_Row : History_Row;
      X_Request : Request;
      X_Result : Result;
   begin
      case Kind is
         when 1 => return (case Field is
            when 1 => X_Span.First'Position,
            when 2 => X_Span.Length'Position,
            when others => I64'Last);
         when 2 => return (case Field is
            when 1 => X_Optional_Span.Present'Position,
            when 2 => X_Optional_Span.Value'Position,
            when others => I64'Last);
         when 3 => return (case Field is
            when 1 => X_Cursor.Present'Position,
            when 2 => X_Cursor.Sequence'Position,
            when 3 => X_Cursor.Run'Position,
            when others => I64'Last);
         when 4 => return (case Field is
            when 1 => X_Binding.Store_Id'Position,
            when 2 => X_Binding.Subject'Position,
            when 3 => X_Binding.Content'Position,
            when 4 => X_Binding.Run'Position,
            when 5 => X_Binding.Sequence'Position,
            when 6 => X_Binding.Requirement'Position,
            when others => I64'Last);
         when 5 => return (case Field is
            when 1 => X_Journal_Row.Bound'Position,
            when 2 => X_Journal_Row.Previous'Position,
            when 3 => X_Journal_Row.Linked'Position,
            when others => I64'Last);
         when 6 => return (case Field is
            when 1 => X_Capture.Bound'Position,
            when 2 => X_Capture.Source_Id'Position,
            when 3 => X_Capture.Context'Position,
            when 4 => X_Capture.State'Position,
            when 5 => X_Capture.Outcome'Position,
            when others => I64'Last);
         when 7 => return (case Field is
            when 1 => X_Facts.Source'Position,
            when 2 => X_Facts.Status'Position,
            when 3 => X_Facts.Channel'Position,
            when 4 => X_Facts.Stage'Position,
            when 5 => X_Facts.Exit_Present'Position,
            when 6 => X_Facts.Exit_Integer'Position,
            when 7 => X_Facts.Supervisor'Position,
            when 8 => X_Facts.Supervisor_Stopped'Position,
            when 9 => X_Facts.Bundle_Present'Position,
            when 10 => X_Facts.Bundle_Is_Mapping'Position,
            when 11 => X_Facts.Bundle_Stable'Position,
            when 12 => X_Facts.Bundle_Changed'Position,
            when 13 => X_Facts.Unsatisfied_Imports'Position,
            when others => I64'Last);
         when 8 => return (case Field is
            when 1 => X_Presence.Record_Identified'Position,
            when 2 => X_Presence.Verdict_Recorded'Position,
            when 3 => X_Presence.Binding_Established'Position,
            when 4 => X_Presence.Declaration_Matches'Position,
            when 5 => X_Presence.Bundle_Identified'Position,
            when others => I64'Last);
         when 9 => return (case Field is
            when 1 => X_Required_Row.Check_Id'Position,
            when 2 => X_Required_Row.Declared'Position,
            when others => I64'Last);
         when 10 => return (case Field is
            when 1 => X_Check_Row.Bound'Position,
            when 2 => X_Check_Row.Check_Id'Position,
            when 3 => X_Check_Row.Source_Id'Position,
            when 4 => X_Check_Row.Execution'Position,
            when 5 => X_Check_Row.Verifier'Position,
            when 6 => X_Check_Row.State'Position,
            when 7 => X_Check_Row.Outcome'Position,
            when 8 => X_Check_Row.Payload'Position,
            when 9 => X_Check_Row.Observed'Position,
            when 10 => X_Check_Row.Report'Position,
            when 11 => X_Check_Row.Evidence'Position,
            when 12 => X_Check_Row.Declared'Position,
            when others => I64'Last);
         when 11 => return (case Field is
            when 1 => X_History_Row.Subject'Position,
            when 2 => X_History_Row.Content'Position,
            when 3 => X_History_Row.Requirement'Position,
            when 4 => X_History_Row.Run'Position,
            when 5 => X_History_Row.Sequence'Position,
            when 6 => X_History_Row.State'Position,
            when 7 => X_History_Row.Outcome'Position,
            when others => I64'Last);
         when 12 => return (case Field is
            when 1 => X_Request.Version'Position,
            when 2 => X_Request.Operation'Position,
            when 3 => X_Request.Data'Position,
            when 4 => X_Request.Data_Length'Position,
            when 5 => X_Request.Journal'Position,
            when 6 => X_Request.Journal_Count'Position,
            when 7 => X_Request.Current'Position,
            when 8 => X_Request.Captured'Position,
            when 9 => X_Request.Captured_Results'Position,
            when 10 => X_Request.Captured_Count'Position,
            when 11 => X_Request.Retained_Present'Position,
            when 12 => X_Request.Retained'Position,
            when 13 => X_Request.Retained_Results'Position,
            when 14 => X_Request.Retained_Count'Position,
            when 15 => X_Request.History'Position,
            when 16 => X_Request.History_Count'Position,
            when 17 => X_Request.Required'Position,
            when 18 => X_Request.Required_Count'Position,
            when 19 => X_Request.Policy'Position,
            when 20 => X_Request.Before_Root'Position,
            when 21 => X_Request.After_Root'Position,
            when 22 => X_Request.Completion'Position,
            when 23 => X_Request.Observed_Binding'Position,
            when others => I64'Last);
         when 13 => return (case Field is
            when 1 => X_Result.Reason'Position,
            when 2 => X_Result.Selected'Position,
            when 3 => X_Result.Summary_Present'Position,
            when 4 => X_Result.Summary'Position,
            when 5 => X_Result.Execution_State'Position,
            when 6 => X_Result.Outcome'Position,
            when 7 => X_Result.Promotion'Position,
            when others => I64'Last);
         when others => return I64'Last;
      end case;
   end Layout_Offset;
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
   function Valid (C : Cursor) return Boolean is
     (C.Present <= 1 and then
        (C.Present = 0 or else (Valid (C.Sequence) and then Valid (C.Run))));
   function Valid (B : Binding) return Boolean is
     (Valid (B.Store_Id) and then Valid (B.Subject) and then Valid (B.Content)
      and then Valid (B.Run) and then Valid (B.Sequence) and then Valid (B.Requirement));
   function Convert (S : Span) return P.Span is (P.Index (S.First), P.Count (S.Length));
   function Convert (S : Optional_Span) return V.Optional_Requirement is
     (if S.Present = 0 then (Present => False)
      else (True, V.Requirement_Id (Convert (S.Value))));
   function Convert (B : Binding) return T.Attempt_Binding is
     (T.Store_Identity (Convert (B.Store_Id)), T.Subject_Identity (Convert (B.Subject)),
      T.Content_Identity (Convert (B.Content)), T.Run_Identity (Convert (B.Run)),
      T.Epoch (Convert (B.Sequence)), Convert (B.Requirement));
   function Convert (C : Cursor) return T.Cursor is
     (if C.Present = 0 then (Present => False)
      else (True, T.Run_Identity (Convert (C.Run)), T.Epoch (Convert (C.Sequence))));
   function Previous (C : Cursor) return P.Cursor is
     (if C.Present = 0 then (Present => False)
      else (True, Convert (C.Sequence), Convert (C.Run)));
   function Valid (C : Capture) return Boolean is
     (Valid (C.Bound) and then Valid (C.Source_Id) and then Valid (C.Context)
      and then C.State in U32 (E.Terminal_State'Pos (E.Terminal_State'First)) ..
                          U32 (E.Terminal_State'Pos (E.Terminal_State'Last))
      and then C.Outcome <= U32 (E.Outcome'Pos (E.Outcome'Last)));
   function Convert (C : Capture) return T.Terminal_Record is
     (Convert (C.Bound), T.Source_Identity (Convert (C.Source_Id)),
      T.Captured_Bytes (Convert (C.Context)), E.Terminal_State'Val (C.State),
      E.Outcome'Val (C.Outcome));
   function Valid (F : Facts) return Boolean is
     (F.Source <= U32 (E.Origin'Pos (E.Origin'Last))
      and then F.Status <= U32 (E.Raw_Status'Pos (E.Raw_Status'Last))
      and then F.Channel <= U32 (E.Channel_State'Pos (E.Channel_State'Last))
      and then F.Stage <= U32 (E.Rejection_Stage'Pos (E.Rejection_Stage'Last))
      and then F.Supervisor <= U32 (E.Supervision_State'Pos (E.Supervision_State'Last))
      and then F.Exit_Present <= 1 and then F.Exit_Integer <= 1
      and then F.Supervisor_Stopped <= 1 and then F.Bundle_Present <= 1
      and then F.Bundle_Is_Mapping <= 1 and then F.Bundle_Stable <= 1
      and then F.Bundle_Changed <= 1 and then F.Unsatisfied_Imports <= 1
      --  Preserve the original Evaluation_Classify dependent encoding guards.
      --  These guards reject malformed transport, not an ordinary negative fact.
      and then F.Exit_Integer <= F.Exit_Present
      and then F.Bundle_Stable <= F.Bundle_Present
      and then F.Bundle_Stable <= F.Bundle_Is_Mapping
      and then F.Bundle_Changed <= F.Bundle_Present
      and then F.Bundle_Changed <= F.Bundle_Is_Mapping);
   function Convert (F : Facts) return E.Observations is
     (E.Origin'Val (F.Source), E.Raw_Status'Val (F.Status),
      E.Channel_State'Val (F.Channel), E.Rejection_Stage'Val (F.Stage),
      F.Exit_Present = 1, F.Exit_Integer = 1, E.Supervision_State'Val (F.Supervisor),
      F.Supervisor_Stopped = 1, F.Bundle_Present = 1, F.Bundle_Is_Mapping = 1,
      F.Bundle_Stable = 1, F.Bundle_Changed = 1, F.Unsatisfied_Imports = 1);
   function Valid (F : Presence) return Boolean is
     (F.Record_Identified <= 1 and then F.Verdict_Recorded <= 1
      and then F.Binding_Established <= 1 and then F.Declaration_Matches <= 1
      and then F.Bundle_Identified <= 1);
   function Convert (F : Presence) return E.Evidence_Presence is
     (F.Record_Identified = 1, F.Verdict_Recorded = 1, F.Binding_Established = 1,
      F.Declaration_Matches = 1, F.Bundle_Identified = 1);
   function Valid (C : Check_Row) return Boolean is
     (Valid (C.Bound) and then Valid (C.Check_Id) and then Valid (C.Source_Id)
      and then Valid (C.Execution) and then Valid (C.Verifier) and then Valid (C.Payload)
      and then Valid (C.Observed) and then Valid (C.Evidence) and then Valid (C.Declared)
      and then C.Report <= U32 (E.Report_Integrity'Pos (E.Report_Integrity'Last))
      and then C.State <= U32 (E.Execution_State'Pos (E.Execution_State'Last))
      and then C.Outcome <= U32 (E.Outcome'Pos (E.Outcome'Last)));
   function Convert (C : Check_Row) return T.Result_Record is
     (Convert (C.Bound), T.Check_Identity (Convert (C.Check_Id)),
      T.Source_Identity (Convert (C.Source_Id)),
      (if C.Execution.Present = 0 then (Present => False)
       else (True, T.Execution_Identity (Convert (C.Execution.Value)))),
      (if C.Verifier.Present = 0 then (Present => False)
       else (True, T.Verifier_Identity (Convert (C.Verifier.Value)))),
      E.Execution_State'Val (C.State), E.Outcome'Val (C.Outcome),
      T.Captured_Bytes (Convert (C.Payload)));
   function Valid (C : History_Row) return Boolean is
     (Valid (C.Subject) and then Valid (C.Content) and then Valid (C.Requirement)
      and then Valid (C.Run) and then Valid (C.Sequence)
      and then C.State <= U32 (H.Lifecycle'Pos (H.Lifecycle'Last))
      and then C.Outcome <= U32 (H.Verdict'Pos (H.Verdict'Last)));
   function H_Span (S : Span) return H.Identity_Span is
     (H.Byte_Index (S.First), H.Byte_Count (S.Length));
   function Convert (C : History_Row) return H.Evaluation_Record is
     ((if C.Subject.Present = 0 then (Present => False)
       else (True, H.Subject_Id (H_Span (C.Subject.Value)))),
      (if C.Content.Present = 0 then (Present => False)
       else (True, H.Content_Id (H_Span (C.Content.Value)))),
      (if C.Requirement.Present = 0 then (Present => False)
       else (True, H.Requirement_Id (H_Span (C.Requirement.Value)))),
      (if C.Run.Present = 0 then (Present => False)
       else (True, H.Evaluation_Id (H_Span (C.Run.Value)))),
      (if C.Sequence.Present = 0 then (Present => False)
       else (True, H.Epoch_Id (H_Span (C.Sequence.Value)))),
      H.Lifecycle'Val (C.State), H.Verdict'Val (C.Outcome));
   function Export_Span (S : H.Identity_Span) return Span is
     (I64 (S.First), I64 (S.Length));
   function Export_Row (C : H.Evaluation_Record) return History_Row is
     ((if C.Subject.Present then (1, Export_Span (H.Identity_Span (C.Subject.Value))) else (0, (1, 0))),
      (if C.Content.Present then (1, Export_Span (H.Identity_Span (C.Content.Value))) else (0, (1, 0))),
      (if C.Requirement.Present then (1, Export_Span (H.Identity_Span (C.Requirement.Value))) else (0, (1, 0))),
      (if C.Run.Present then (1, Export_Span (H.Identity_Span (C.Run.Value))) else (0, (1, 0))),
      (if C.Sequence.Present then (1, Export_Span (H.Identity_Span (C.Sequence.Value))) else (0, (1, 0))),
      U32 (H.Lifecycle'Pos (C.State)), U32 (H.Verdict'Pos (C.Outcome)));
   function Copy_Data (Address : System.Address; Length : I64) return P.Bytes is
      Owned : P.Bytes (1 .. P.Count (Length));
   begin
      for I in Owned'Range loop
         Owned (I) := Octets.To_Pointer (Address + Storage_Offset (I - 1)).all;
      end loop;
      return Owned;
   end Copy_Data;
   function Decide (Input, Output : System.Address) return Interfaces.C.int is
      Input_Size : constant I64 := Request'Object_Size / System.Storage_Unit;
      Output_Size : constant I64 := Result'Object_Size / System.Storage_Unit;
      J_Stride : constant I64 := Journal_Row'Object_Size / System.Storage_Unit;
      C_Stride : constant I64 := Check_Row'Object_Size / System.Storage_Unit;
      H_Stride : constant I64 := History_Row'Object_Size / System.Storage_Unit;
      S_Stride : constant I64 := Required_Row'Object_Size / System.Storage_Unit;
   begin
      if not Extent_Valid (Input, Input_Size, Request'Alignment)
        or else not Extent_Valid (Output, Output_Size, Result'Alignment)
        or else not Disjoint (Input, Input_Size, Output, Output_Size)
      then return 255; end if;
      declare
         R : constant Request := Requests.To_Pointer (Input).all;
      begin
         if R.Version /= 1 or else R.Operation > 2 or else R.Policy > U32 (Roster.Declaration'Pos (Roster.Declaration'Last)) or else R.Retained_Present > 1
           or else not Extent_Valid (R.Data, R.Data_Length, P.Byte'Alignment)
           or else not Disjoint (R.Data, R.Data_Length, Output, Output_Size)
           or else not Array_Valid (R.Journal, R.Journal_Count, J_Stride, Journal_Row'Alignment, Output, Output_Size)
           or else not Array_Valid (R.Captured_Results, R.Captured_Count, C_Stride, Check_Row'Alignment, Output, Output_Size)
           or else not Array_Valid (R.Retained_Results, R.Retained_Count, C_Stride, Check_Row'Alignment, Output, Output_Size)
           or else not Array_Valid (R.History, R.History_Count, H_Stride, History_Row'Alignment, Output, Output_Size)
           or else not Array_Valid (R.Required, R.Required_Count, S_Stride, Required_Row'Alignment, Output, Output_Size)
           or else not Valid (R.Observed_Binding)
           or else not Valid (R.Before_Root) or else not Valid (R.After_Root)
           or else not Valid (R.Completion.Check_Id) or else not Valid (R.Completion.Declared)
           or else not Valid (R.Current) or else not Valid (R.Captured)
           or else (R.Retained_Present = 1 and then not Valid (R.Retained))
         then return 255; end if;
         declare
            A : constant P.Bytes := Copy_Data (R.Data, R.Data_Length);
            J : V.Journal (1 .. P.Count (R.Journal_Count));
            Measures : Roster.Measured_Array (1 .. P.Count (R.Captured_Count));
            Captured : T.Result_Array (1 .. P.Count (R.Captured_Count));
            Retained_Results : T.Result_Array (1 .. P.Count (R.Retained_Count));
            History : H.History (1 .. H.Byte_Count (R.History_Count));
            Required : Roster.Check_Array (1 .. P.Count (R.Required_Count));
            Classified : Roster.Classification;
            Retained : constant T.Optional_Terminal :=
              (if R.Retained_Present = 0 then (Present => False)
               else (True, Convert (R.Retained)));
            Reason : T.Decision;
            Selected : P.Count;
            Response : Result := (Reason => 0, Selected => 0,
              Summary_Present => 0, Summary =>
                (Subject | Content | Requirement | Run | Sequence => (0, (1, 0)),
                 State | Outcome => 0), Execution_State => 0, Outcome => 0, Promotion => 0);
         begin
            for I in J'Range loop
               declare
                  X : constant Journal_Row := Journals.To_Pointer
                    (R.Journal + Storage_Offset (I64 (I - 1) * J_Stride)).all;
               begin
                  if not Valid (X.Bound) or else not Valid (X.Previous) or else X.Linked > 1
                  then return 255; end if;
                  J (I) := (Base =>
                    (Convert (X.Bound.Store_Id), Convert (X.Bound.Subject),
                     Convert (X.Bound.Content), Convert (X.Bound.Run),
                     Convert (X.Bound.Sequence), Previous (X.Previous),
                     (if X.Linked = 0 then P.Reserved else P.Linked)),
                    Requirement => Convert (X.Bound.Requirement));
               end;
            end loop;
            for I in Captured'Range loop
               declare
                  X : constant Check_Row := Checks.To_Pointer
                    (R.Captured_Results + Storage_Offset (I64 (I - 1) * C_Stride)).all;
               begin
                  if not Valid (X) then return 255; end if;
                  Captured (I) := Convert (X);
                  Measures (I) := (Captured (I), Convert (X.Observed),
                    E.Report_Integrity'Val (X.Report), Convert (X.Evidence),
                    T.Captured_Bytes (Convert (X.Declared)));
               end;
            end loop;
            for I in Retained_Results'Range loop
               declare
                  X : constant Check_Row := Checks.To_Pointer
                    (R.Retained_Results + Storage_Offset (I64 (I - 1) * C_Stride)).all;
               begin
                  if not Valid (X) then return 255; end if;
                  Retained_Results (I) := Convert (X);
               end;
            end loop;
            for I in History'Range loop
               declare
                  X : constant History_Row := Histories.To_Pointer
                    (R.History + Storage_Offset (I64 (I - 1) * H_Stride)).all;
               begin
                  if not Valid (X) then return 255; end if;
                  History (I) := Convert (X);
               end;
            end loop;
            for I in Required'Range loop
               declare
                  X : constant Required_Row := Requirements.To_Pointer
                    (R.Required + Storage_Offset (I64 (I - 1) * S_Stride)).all;
               begin
                  if not Valid (X.Check_Id) or else not Valid (X.Declared) then return 255; end if;
                  Required (I) := (T.Check_Identity (Convert (X.Check_Id)), T.Captured_Bytes (Convert (X.Declared)));
               end;
            end loop;
            if R.Operation /= 1 then
               Reason := T.Decide (A, J, Convert (R.Current), Convert (R.Captured),
                                   Captured, Retained, Retained_Results);
            else
               T.Apply (A, J, Convert (R.Current), Convert (R.Captured), Captured,
                        Retained, Retained_Results, History, Reason);
            end if;
            Response.Reason := U32 (T.Decision'Pos (Reason));
            if Reason in T.Retain_Terminal | T.Already_Retained then
               Selected := T.Find_Run (A, J, T.Run_Identity (Convert (R.Captured.Bound.Run)));
               Response.Selected := I64 (Selected);
               if R.Operation = 2 then
                  Classified := Roster.Classify (A, Convert (R.Captured.Bound),
                    Measures, Required, Roster.Declaration'Val (R.Policy),
                    (Convert (R.Observed_Binding), T.Captured_Bytes (Convert (R.Before_Root)),
                     T.Captured_Bytes (Convert (R.After_Root))),
                    (T.Check_Identity (Convert (R.Completion.Check_Id)),
                     T.Captured_Bytes (Convert (R.Completion.Declared))));
                  Response.Execution_State := U32 (E.Execution_State'Pos (Classified.State));
                  Response.Outcome := U32 (E.Outcome'Pos (Classified.Outcome));
                  Response.Promotion := Boolean'Pos (Classified.Promotion_Ready);
               end if;
               if R.Operation = 1 then
                  Response.Summary_Present := 1;
                  Response.Summary := Export_Row (History (H.Byte_Index (Selected)));
               end if;
            end if;
            Outputs.To_Pointer (Output).all := Response;
            return 0;
         end;
      end;
   exception
      when others => return 255;
   end Decide;
end Evaluation_Completion_C;

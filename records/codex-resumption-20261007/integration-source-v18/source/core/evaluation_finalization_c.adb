with GNAT.Current_Exception;
with Evaluation_Finalization;
with Worldline.Collapse;
with Worldline.Collapse_Wire;
with Worldline.Evaluation_Authority;
with System.Address_To_Access_Conversions;
with System.Storage_Elements;

package body Evaluation_Finalization_C with SPARK_Mode => On is
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
   use type Requests.Object_Pointer;
   use type Outputs.Object_Pointer;
   use type Rows.Object_Pointer;
   use type Plans.Object_Pointer;
   use type Octets.Object_Pointer;

   Blank_Check : constant R.Required_Check :=
     (Check => (First => 1, Length => 0),
      Declared => (First => 1, Length => 0));
   Blank_Start : constant F.Start_Record :=
     (Store => (First => 1, Length => 0),
      Subject => (First => 1, Length => 0),
      Run => (First => 1, Length => 0),
      Sequence => (First => 1, Length => 0),
      Requirement => (Present => False),
      Policy => (First => 1, Length => 0),
      Verifier_Plan => (First => 1, Length => 0),
      Base_Context => (First => 1, Length => 0),
      Parent => (others => 0), Config => (others => 0),
      Repository => (others => 0),
      Required => (First => 1, Length => 0),
      Declaration => R.Declaration'First);
   Blank_Row : constant F.Start_Row :=
     (Start => Blank_Start,
      Check => (First => 1, Length => 0),
      Source => (First => 1, Length => 0),
      Execution => (Present => False),
      Verifier => (Present => False),
      State => T.E.Execution_State'First,
      Outcome => T.E.Outcome'First,
      Payload => (First => 1, Length => 0),
      Declared => (First => 1, Length => 0),
      Raw => W.Zero_Record,
      Confinement => 0);

   procedure Read_Request (Address : System.Address; Item : out Request)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Requests.Object_Pointer := Requests.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Request;

   procedure Read_Required (Address : System.Address; Item : out Required_Row)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Plans.Object_Pointer := Plans.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Required;

   procedure Read_Row (Address : System.Address; Item : out Row)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Rows.Object_Pointer := Rows.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Row;

   procedure Write_Result (Address : System.Address; Item : Result)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Outputs.Object_Pointer := Outputs.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Result;

   procedure Copy_Data
     (Address : System.Address; Length : I64; Data : out P.Bytes)
     with Pre => Length >= 0
            and then Length <= I64 (P.Count'Last)
            and then Data'First = 1
            and then Data'Length = P.Count (Length)
            and then (Length = 0 or else Address /= System.Null_Address),
          Exceptional_Cases => (others => True)
   is
   begin
      for I in Data'Range loop
         declare
            Pointer : constant Octets.Object_Pointer :=
              Octets.To_Pointer (Address + Storage_Offset (I - 1));
         begin
            if Pointer = null then
               raise Constraint_Error;
            end if;
            Data (I) := Pointer.all;
         end;
      end loop;
   end Copy_Data;

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
        else Integer_Address (RL) <= To_Integer (L) - To_Integer (R)))
   with Pre => LL >= 0 and then RL >= 0;
   function Array_Extent (A : System.Address; N, Stride, Alignment : I64)
      return Boolean is
     (N >= 0 and then Stride > 0
      and then N <= I64 (Storage_Offset'Last) / Stride
      and then Extent_Valid (A, N * Stride, Alignment));
   function Array_Valid (A : System.Address; N, Stride, Alignment : I64;
                         Output : System.Address; Output_Length : I64)
      return Boolean is
     (Array_Extent (A, N, Stride, Alignment)
      and then Disjoint (A, N * Stride, Output, Output_Length))
   with Pre => Output_Length >= 0;
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
     (First => P.Index (S.First), Length => P.Count (S.Length))
   with Pre => Valid (S);
   function Convert (S : Optional_Span) return T.Optional_Requirement is
     (if S.Present = 0 then (Present => False)
      else (True, T.Requirement_Identity (Convert (S.Value))))
   with Pre => Valid (S);
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
      Declaration => R.Declaration'Val (S.Declaration))
   with Pre => Valid (S);
   function Convert (I : Input_Record) return F.Input_Record is
     (Start => Convert (I.Start), Root => T.Captured_Bytes (Convert (I.Root)),
      Manifests => T.Captured_Bytes (Convert (I.Manifests)),
      Filesystem => Convert (I.Filesystem), Config => Convert (I.Config),
      Repository => Convert (I.Repository))
   with Pre => Valid (I);
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
      Raw => X.Raw, Confinement => X.Confinement)
   with Pre => Valid (X);

   function Decide_Common
     (Input, Output : System.Address;
      Have_Output : Boolean;
      Observed : in out Result) return Interfaces.C.int
     with Side_Effects is
      Input_Size : constant I64 := Request'Object_Size / System.Storage_Unit;
      Output_Size : constant I64 := Result'Object_Size / System.Storage_Unit;
      Row_Size : constant I64 := Row'Object_Size / System.Storage_Unit;
      Plan_Size : constant I64 := Required_Row'Object_Size / System.Storage_Unit;
      function Output_Separated
        (A : System.Address; N, Stride, Alignment : I64) return Boolean is
        (Array_Extent (A, N, Stride, Alignment)
         and then (not Have_Output
                   or else Disjoint (A, N * Stride, Output, Output_Size)));
   begin
      K.Diagnostic_Mark ("finalization.decide.enter");
      if not Extent_Valid (Input, Input_Size, Request'Alignment)
        or else (Have_Output and then
                 (not Extent_Valid (Output, Output_Size, Result'Alignment)
                  or else not Disjoint (Input, Input_Size, Output, Output_Size)))
      then
         K.Diagnostic_Mark ("finalization.decide.input-extents-rejected");
         return 255;
      end if;
      declare
         Raw_X : Request;
      begin
         Read_Request (Input, Raw_X);
         declare
            X : constant Request := Raw_X;
            Data_Length : constant I64 := X.Data_Length;
            Required_Count : constant I64 := X.Required_Count;
            Row_Count : constant I64 := X.Row_Count;
         begin
         if X.Version /= 1 or else X.Operation > 3
           or else not Extent_Valid (X.Data, Data_Length, P.Byte'Alignment)
           or else (Have_Output and then
                    not Disjoint (X.Data, Data_Length, Output, Output_Size))
           or else not Output_Separated
             (X.Required, Required_Count, Plan_Size, Required_Row'Alignment)
           or else not Output_Separated
             (X.Rows, Row_Count, Row_Size, Row'Alignment)
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
            A : P.Bytes (1 .. P.Count (Data_Length));
            Required : R.Check_Array (1 .. P.Count (Required_Count)) :=
              (others => Blank_Check);
            Captured : F.Start_Rows (1 .. P.Count (Row_Count)) :=
              (others => Blank_Row);
            S : constant F.Start_Record := Convert (X.Start);
            Response : Result := (Reason => 1, State => 0, Outcome => 0,
              Promotion => 0, Finalization_State => 0,
              Finalization_Outcome => 0, Identity => (others => 0));
         begin
            Copy_Data (X.Data, Data_Length, A);
            for K in Required'Range loop
               declare
                  Q : Required_Row;
               begin
                  Read_Required
                    (X.Required + Storage_Offset (I64 (K - 1) * Plan_Size), Q);
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
                     Q : Row;
                  begin
                     Read_Row
                       (X.Rows + Storage_Offset (I64 (K - 1) * Row_Size), Q);
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
            Observed := Response;
            if Have_Output then
               Write_Result (Output, Response);
            end if;
            return 0;
         end;
         end;
      end;
   exception
      when others =>
         declare
            Handler_Diagnostic_Enabled : Boolean := False;
         begin
            Handler_Diagnostic_Enabled := K.Diagnostic_Enabled;
            if Handler_Diagnostic_Enabled then
               begin
                  K.Diagnostic_Exception
                    ("finalization.decide",
                     GNAT.Current_Exception.Exception_Information);
               exception
                  when others => K.Diagnostic_Capture_Failed;
               end;
            end if;
         end;
         return 255;
   end Decide_Common;

   function Decide (Input, Output : System.Address) return Interfaces.C.int is
      Observed : Result := (Reason => 1, State => 0, Outcome => 0, Promotion => 0,
                            Finalization_State => 0, Finalization_Outcome => 0,
                            Identity => (others => 0));
      Status : Interfaces.C.int;
   begin
      Status := Decide_Common (Input, Output, True, Observed);
      return Status;
   end Decide;

   -- Context-only view of the validated late binding. This projection is
   -- never dispatched to ordinary Decide/Raw_Decide and has no journal entry.
   function Final_Context_Matches
     (Input, Metadata, Collapse, Agent : System.Address; Agent_Confinement : U8)
      return Boolean
     with Side_Effects is
      Native : Result := (Reason => 1, State => 0, Outcome => 0, Promotion => 0,
                          Finalization_State => 0, Finalization_Outcome => 0,
                          Identity => (others => 0));
      Plan_Size : constant I64 := Required_Row'Object_Size / System.Storage_Unit;
      Row_Size : constant I64 := Row'Object_Size / System.Storage_Unit;
   begin
      K.Diagnostic_Mark ("finalization.context.enter");
      declare
         Status : Interfaces.C.int;
      begin
         Status := Decide_Common (Input, System.Null_Address, False, Native);
         if Status /= 0 or else Native.Reason /= 0 or else Native.Promotion /= 1
         then
         K.Diagnostic_Mark ("finalization.context.seal-rejected");
         return False;
         end if;
      end;
      declare
         Raw_X : Request;
      begin
         Read_Request (Input, Raw_X);
         declare
            X : constant Request := Raw_X;
            Row_Count : constant I64 := X.Row_Count;
            Required_Length : constant I64 := X.Start.Required.Length;
            Required_First : constant I64 := X.Start.Required.First;
         begin
         if X.Operation /= 3 or else not Valid (X.Start.Required)
           or else Row_Count < 0 or else Required_Length < 0
           or else Required_Length > X.Required_Count
           or else (Required_Length /= 0 and then
             (Required_First > X.Required_Count or else
              Required_Length - 1 > X.Required_Count - Required_First))
         then
            K.Diagnostic_Mark ("finalization.context.required-extent-rejected");
            return False;
         end if;
         declare
            Empty_Span : constant Span := (First => 1, Length => 0);
            Empty_Opt : constant Optional_Span := (Present => 0, Value => Empty_Span);
            Empty_Binding : constant K.Binding :=
              (Empty_Span, Empty_Span, Empty_Span, Empty_Span, Empty_Span, Empty_Opt);
            Empty_Facts : constant K.Facts := (others => 0);
            Empty_Presence : constant K.Presence := (others => 0);
            Empty_Check : constant K.Check_Row :=
              (Empty_Binding, Empty_Span, Empty_Span, Empty_Opt, Empty_Opt,
               0, 0, Empty_Span, Empty_Facts, 0, Empty_Presence, Empty_Span);
            Empty_Plan : constant K.Required_Row := (Check_Id => Empty_Span,
                                                     Declared => Empty_Span);
            Projected_Rows : K.Check_Row_Array (1 .. I64 (P.Count (Row_Count))) :=
              (others => Empty_Check);
            Projected_Plans : K.Required_Row_Array
              (1 .. I64 (P.Count (Required_Length))) := (others => Empty_Plan);
            Bound : constant K.Binding := (X.Start.Store_Id, X.Start.Subject,
              X.Content, X.Start.Run, X.Start.Sequence, X.Start.Requirement);
            Empty_Capture : constant K.Capture :=
              (Bound, X.Source_Id, X.Context, 0, 0);
            Projection : K.Request;
         begin
            for I in Projected_Rows'Range loop
               declare
                  Original : Row;
               begin
                  Read_Row
                    (X.Rows + Storage_Offset (I64 (I - 1) * Row_Size), Original);
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
               declare
                  Plan : Required_Row;
               begin
                  Read_Required
                    (X.Required + Storage_Offset
                       ((Required_First - 1 + I64 (I - 1)) * Plan_Size), Plan);
                  Projected_Plans (I) := Plan;
               end;
            end loop;
            Projection := (Version => 1, Operation => 2,
              Data => X.Data, Data_Length => X.Data_Length,
              Journal => System.Null_Address, Journal_Count => 0,
              Current => (1, X.Start.Sequence, X.Start.Run),
              Captured => (Bound, X.Source_Id, X.Context, Native.State, Native.Outcome),
              Captured_Results => System.Null_Address, Captured_Count => X.Row_Count,
              Retained_Present => 0, Retained => Empty_Capture,
              Retained_Results => System.Null_Address, Retained_Count => 0,
              History => System.Null_Address, History_Count => 0,
              Required => System.Null_Address, Required_Count => X.Start.Required.Length,
              Policy => X.Start.Declaration, Before_Root => X.Inputs.Root,
              After_Root => X.Post_Root, Completion => X.Completion,
              Observed_Binding => Bound);
            K.Diagnostic_Mark ("finalization.context.projected");
            declare
               Context_Base : constant System.Address := K.Metadata_Base (Metadata);
               Context_Result : Interfaces.C.int;
            begin
               Context_Result := K.Context_Matches_Projected
                 (Projection, Projected_Rows, Projected_Plans, Context_Base,
                  Collapse, Agent, Agent_Confinement);
               K.Diagnostic_Value ("finalization.context.context-result", I64 (Context_Result));
               if Context_Result /= 1 then return False; end if;
               declare
                  Metadata_Result : Interfaces.C.int;
               begin
                  Metadata_Result := K.Metadata_Matches_Projected
                    (Projection, Projected_Rows, Metadata);
                  K.Diagnostic_Value
                    ("finalization.context.metadata-result", I64 (Metadata_Result));
                  return Metadata_Result = 1;
               end;
            end;
         end;
         end;
      end;
   exception
      when others =>
         declare
            Handler_Diagnostic_Enabled : Boolean := False;
         begin
            Handler_Diagnostic_Enabled := K.Diagnostic_Enabled;
            if Handler_Diagnostic_Enabled then
               begin
                  K.Diagnostic_Exception
                    ("finalization.context",
                     GNAT.Current_Exception.Exception_Information);
               exception
                  when others => K.Diagnostic_Capture_Failed;
               end;
            end if;
         end;
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
      use type Collapse_Requests.Object_Pointer;
      use type Raw_Records.Object_Pointer;
      P_Ready, S_Ready, Agent_Ready : U8 := 0;
      procedure Read_Collapse (Address : System.Address; Item : out CW.Raw_Request)
        with Exceptional_Cases => (others => True)
      is
         Pointer : constant Collapse_Requests.Object_Pointer :=
           Collapse_Requests.To_Pointer (Address);
      begin
         if Pointer = null then
            raise Constraint_Error;
         end if;
         Item := Pointer.all;
      end Read_Collapse;
      procedure Read_Agent (Address : System.Address; Item : out W.Raw_Record)
        with Exceptional_Cases => (others => True)
      is
         Pointer : constant Raw_Records.Object_Pointer :=
           Raw_Records.To_Pointer (Address);
      begin
         if Pointer = null then
            raise Constraint_Error;
         end if;
         Item := Pointer.all;
      end Read_Agent;
      type Readiness_Result is record
         Valid : Boolean;
         Ready : U8;
      end record;
      function Read_Ready
        (Kind : U32; Input, Raw, Confined : System.Address)
         return Readiness_Result
        with Side_Effects is
         Ordinary : K.Result := (Reason => 0, Selected => 0,
           Summary_Present => 0, Summary =>
             (Subject | Content | Requirement | Run | Sequence => (0, (1, 0)),
              State | Outcome => 0),
           Execution_State => 0, Outcome => 0, Promotion => 0);
         Finalized : Result := (Reason => 1, State => 0, Outcome => 0, Promotion => 0,
                                Finalization_State => 0, Finalization_Outcome => 0,
                                Identity => (others => 0));
         Ready_State : Readiness_Result := (Valid => True, Ready => 0);
      begin
         if Kind = 0 then return Ready_State; end if;
         if Kind = 1 then
            declare
               Ordinary_Status : Interfaces.C.int;
            begin
               Ordinary_Status := K.Raw_Decide_Observed (Input, Raw, Confined, Ordinary);
               if Ordinary_Status /= 0
                 or else Ordinary.Promotion > 1
                 or else Ordinary.Reason not in
                   T.Decision'Pos (T.Retain_Terminal) | T.Decision'Pos (T.Already_Retained)
               then return (Valid => False, Ready => Ready_State.Ready); end if;
            end;
            Ready_State.Ready := U8 (Ordinary.Promotion);
         elsif Kind = 2 then
            declare
               Final_Status : Interfaces.C.int;
            begin
               Final_Status := Decide_Common (Input, System.Null_Address, False, Finalized);
               if Final_Status /= 0 or else Finalized.Reason /= 0
                 or else Finalized.Promotion > 1
               then return (Valid => False, Ready => Ready_State.Ready); end if;
            end;
            declare
               X : Request;
            begin
               Read_Request (Input, X);
               if X.Operation /= 3 then return (Valid => False, Ready => Ready_State.Ready); end if;
            end;
            Ready_State.Ready := U8 (Finalized.Promotion);
         else return (Valid => False, Ready => Ready_State.Ready);
         end if;
         return Ready_State;
      exception
         when others =>
            return (Valid => False, Ready => 0);
      end Read_Ready;
      function Context_Joined
        (Kind : U32; Input, Metadata : System.Address) return Boolean
        with Side_Effects is
         Status : Interfaces.C.int;
         Joined : Boolean;
         Base : System.Address;
      begin
         if Kind = 1 then
            Base := K.Metadata_Base (Metadata);
            Status := K.Context_Matches
              (Input, Base, Collapse, Agent, Agent_Confinement);
            return Status = 1;
         elsif Kind = 2 then
            Joined := Final_Context_Matches
              (Input, Metadata, Collapse, Agent, Agent_Confinement);
            return Joined;
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
         Bound : CW.Raw_Request;
         Needed : Authority.Raw_Dependency;
         Decision : U8;
      begin
         Read_Collapse (Collapse, Bound);
         Needed := Authority.Dependencies (Bound);
         if Needed = Authority.Invalid_Collapse then
            K.Diagnostic_Mark ("finalization.mixed.dependency-rejected");
            return CW.Invalid_Request;
         end if;
         if Authority.Needs_Primary (Needed) then
            declare
               Observed : Readiness_Result;
            begin
               Observed := Read_Ready
                 (Primary_Kind, Primary, Primary_Raw, Primary_Confinement);
               P_Ready := Observed.Ready;
               if not Observed.Valid then
                  K.Diagnostic_Mark ("finalization.mixed.primary-ready-rejected");
                  return CW.Invalid_Request;
               end if;
            end;
         end if;
         if Authority.Needs_Staged (Needed) then
            declare
               Observed : Readiness_Result;
            begin
               Observed := Read_Ready
                 (Staged_Kind, Staged, Staged_Raw, Staged_Confinement);
               S_Ready := Observed.Ready;
               if not Observed.Valid then
                  K.Diagnostic_Mark ("finalization.mixed.staged-ready-rejected");
                  return CW.Invalid_Request;
               end if;
            end;
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
               Owned_Agent : W.Raw_Record;
            begin
               Read_Agent (Agent, Owned_Agent);
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
            if P_Ready = 1 then
               declare
                  Joined : Boolean;
               begin
                  Joined := Context_Joined (Primary_Kind, Primary, Primary_Context);
                  if not Joined then
                     K.Diagnostic_Mark ("finalization.mixed.primary-context-rejected");
                     return CW.Invalid_Request;
                  end if;
               end;
            end if;
            if S_Ready = 1 then
               declare
                  Joined : Boolean;
               begin
                  Joined := Context_Joined (Staged_Kind, Staged, Staged_Context);
                  if not Joined then
                     K.Diagnostic_Mark ("finalization.mixed.staged-context-rejected");
                     return CW.Invalid_Request;
                  end if;
               end;
            end if;
         end if;
         Bound.Roster_Complete := (if Agent_Ready = 1 then P_Ready else 0);
         Bound.Staged_Roster_Complete := (if Agent_Ready = 1 then S_Ready else 0);
         Decision := CW.Decide_Wire (Bound);
         K.Diagnostic_Value ("finalization.mixed.collapse-decision", I64 (Decision));
         if Decision /= U8 (Worldline.Collapse.Decision'Pos (Worldline.Collapse.Authorized))
         then return Decision; end if;
         if Authority.Needs_Primary (Needed) and then Primary_Kind = 1 then
            declare
               Metadata_Status : Interfaces.C.int;
            begin
               Metadata_Status := K.Metadata_Matches (Primary, Primary_Context);
               if Metadata_Status /= 1 then
                  K.Diagnostic_Mark ("finalization.mixed.primary-metadata-rejected");
                  return CW.Invalid_Request;
               end if;
            end;
         end if;
         if Authority.Needs_Staged (Needed) and then Staged_Kind = 1 then
            declare
               Metadata_Status : Interfaces.C.int;
            begin
               Metadata_Status := K.Metadata_Matches (Staged, Staged_Context);
               if Metadata_Status /= 1 then
                  K.Diagnostic_Mark ("finalization.mixed.staged-metadata-rejected");
                  return CW.Invalid_Request;
               end if;
            end;
         end if;
         return Decision;
      end;
   exception
      when others =>
         declare
            Handler_Diagnostic_Enabled : Boolean := False;
         begin
            Handler_Diagnostic_Enabled := K.Diagnostic_Enabled;
            if Handler_Diagnostic_Enabled then
               begin
                  K.Diagnostic_Exception
                    ("finalization.mixed",
                     GNAT.Current_Exception.Exception_Information);
               exception
                  when others => K.Diagnostic_Capture_Failed;
               end;
            end if;
         end;
         return CW.Invalid_Request;
   end Decide_Mixed;

   function Layout_Start (Field : U32) return I64 is
      Empty_Span : constant Span := (First => 1, Length => 0);
      Empty_Opt : constant Optional_Span := (Present => 0, Value => Empty_Span);
      Empty_Digest : constant Digest := (others => 0);
      S : constant Start_Record :=
        (Store_Id | Subject | Run | Sequence => Empty_Span,
         Requirement => Empty_Opt,
         Policy | Verifier_Plan | Base_Context => Empty_Span,
         Parent | Config | Repository => Empty_Digest,
         Required => Empty_Span, Declaration => 0);
   begin
      pragma Compile_Time_Error (S.Store_Id'Position /= 0, "Start.Store_Id");
      pragma Compile_Time_Error (S.Subject'Position /= 16, "Start.Subject");
      pragma Compile_Time_Error (S.Run'Position /= 32, "Start.Run");
      pragma Compile_Time_Error (S.Sequence'Position /= 48, "Start.Sequence");
      pragma Compile_Time_Error (S.Requirement'Position /= 64, "Start.Requirement");
      pragma Compile_Time_Error (S.Policy'Position /= 88, "Start.Policy");
      pragma Compile_Time_Error (S.Verifier_Plan'Position /= 104, "Start.Verifier_Plan");
      pragma Compile_Time_Error (S.Base_Context'Position /= 120, "Start.Base_Context");
      pragma Compile_Time_Error (S.Parent'Position /= 136, "Start.Parent");
      pragma Compile_Time_Error (S.Config'Position /= 168, "Start.Config");
      pragma Compile_Time_Error (S.Repository'Position /= 200, "Start.Repository");
      pragma Compile_Time_Error (S.Required'Position /= 232, "Start.Required");
      pragma Compile_Time_Error (S.Declaration'Position /= 248, "Start.Declaration");
      return (case Field is
        when 0 => Start_Record'Object_Size / System.Storage_Unit,
        when 1 => Start_Record'Alignment,
        when 2 => 0, when 3 => 16, when 4 => 32, when 5 => 48,
        when 6 => 64, when 7 => 88, when 8 => 104, when 9 => 120,
        when 10 => 136, when 11 => 168, when 12 => 200, when 13 => 232,
        when 14 => 248, when others => I64'Last);
   end Layout_Start;

   function Layout_Input (Field : U32) return I64 is
      Empty_Span : constant Span := (First => 1, Length => 0);
      Empty_Opt : constant Optional_Span := (Present => 0, Value => Empty_Span);
      Empty_Digest : constant Digest := (others => 0);
      S : constant Start_Record :=
        (Store_Id | Subject | Run | Sequence => Empty_Span,
         Requirement => Empty_Opt,
         Policy | Verifier_Plan | Base_Context => Empty_Span,
         Parent | Config | Repository => Empty_Digest,
         Required => Empty_Span, Declaration => 0);
      I : constant Input_Record :=
        (Start => S, Root | Manifests => Empty_Span,
         Filesystem | Config | Repository => Empty_Digest);
   begin
      pragma Compile_Time_Error (I.Start'Position /= 0, "Input.Start");
      pragma Compile_Time_Error (I.Root'Position /= 256, "Input.Root");
      pragma Compile_Time_Error (I.Manifests'Position /= 272, "Input.Manifests");
      pragma Compile_Time_Error (I.Filesystem'Position /= 288, "Input.Filesystem");
      pragma Compile_Time_Error (I.Config'Position /= 320, "Input.Config");
      pragma Compile_Time_Error (I.Repository'Position /= 352, "Input.Repository");
      return (case Field is
        when 0 => Input_Record'Object_Size / System.Storage_Unit,
        when 1 => Input_Record'Alignment,
        when 2 => 0, when 3 => 256, when 4 => 272, when 5 => 288,
        when 6 => 320, when 7 => 352, when others => I64'Last);
   end Layout_Input;

   function Layout_Row (Field : U32) return I64 is
      Empty_Span : constant Span := (First => 1, Length => 0);
      Empty_Opt : constant Optional_Span := (Present => 0, Value => Empty_Span);
      Empty_Digest : constant Digest := (others => 0);
      S : constant Start_Record :=
        (Store_Id | Subject | Run | Sequence => Empty_Span,
         Requirement => Empty_Opt,
         Policy | Verifier_Plan | Base_Context => Empty_Span,
         Parent | Config | Repository => Empty_Digest,
         Required => Empty_Span, Declaration => 0);
      Q : constant Row :=
        (Start => S, Check_Id | Source_Id => Empty_Span,
         Execution | Verifier => Empty_Opt, State => 0, Outcome => 0,
         Payload | Declared => Empty_Span, Raw => W.Zero_Record,
         Confinement => 0);
   begin
      pragma Compile_Time_Error (Q.Start'Position /= 0, "Row.Start");
      pragma Compile_Time_Error (Q.Check_Id'Position /= 256, "Row.Check_Id");
      pragma Compile_Time_Error (Q.Source_Id'Position /= 272, "Row.Source_Id");
      pragma Compile_Time_Error (Q.Execution'Position /= 288, "Row.Execution");
      pragma Compile_Time_Error (Q.Verifier'Position /= 312, "Row.Verifier");
      pragma Compile_Time_Error (Q.State'Position /= 336, "Row.State");
      pragma Compile_Time_Error (Q.Outcome'Position /= 340, "Row.Outcome");
      pragma Compile_Time_Error (Q.Payload'Position /= 344, "Row.Payload");
      pragma Compile_Time_Error (Q.Declared'Position /= 360, "Row.Declared");
      pragma Compile_Time_Error (Q.Raw'Position /= 376, "Row.Raw");
      pragma Compile_Time_Error (Q.Confinement'Position /= 410, "Row.Confinement");
      return (case Field is
        when 0 => Row'Object_Size / System.Storage_Unit,
        when 1 => Row'Alignment,
        when 2 => 0, when 3 => 256, when 4 => 272, when 5 => 288,
        when 6 => 312, when 7 => 336, when 8 => 340, when 9 => 344,
        when 10 => 360, when 11 => 376, when 12 => 410, when others => I64'Last);
   end Layout_Row;

   function Layout_Request (Field : U32) return I64 is
      Empty_Span : constant Span := (First => 1, Length => 0);
      Empty_Opt : constant Optional_Span := (Present => 0, Value => Empty_Span);
      Empty_Digest : constant Digest := (others => 0);
      S : constant Start_Record :=
        (Store_Id | Subject | Run | Sequence => Empty_Span,
         Requirement => Empty_Opt,
         Policy | Verifier_Plan | Base_Context => Empty_Span,
         Parent | Config | Repository => Empty_Digest,
         Required => Empty_Span, Declaration => 0);
      I : constant Input_Record :=
        (Start => S, Root | Manifests => Empty_Span,
         Filesystem | Config | Repository => Empty_Digest);
      X : constant Request :=
        (Version => 0, Operation => 0, Data => System.Null_Address,
         Data_Length => 0, Start => S, Inputs => I,
         Post_Root | Post_Manifests => Empty_Span,
         Rows => System.Null_Address, Row_Count => 0,
         Required => System.Null_Address, Required_Count => 0,
         Completion => (Check_Id => Empty_Span, Declared => Empty_Span),
         Content => Empty_Span,
         Environment_Root | Evidence_Root => Empty_Digest,
         Context | Source_Id | Evidence | Environment => Empty_Span);
   begin
      pragma Compile_Time_Error (X.Version'Position /= 0, "Request.Version");
      pragma Compile_Time_Error (X.Operation'Position /= 4, "Request.Operation");
      pragma Compile_Time_Error (X.Data'Position /= 8, "Request.Data");
      pragma Compile_Time_Error (X.Data_Length'Position /= 16, "Request.Data_Length");
      pragma Compile_Time_Error (X.Start'Position /= 24, "Request.Start");
      pragma Compile_Time_Error (X.Inputs'Position /= 280, "Request.Inputs");
      pragma Compile_Time_Error (X.Post_Root'Position /= 664, "Request.Post_Root");
      pragma Compile_Time_Error (X.Post_Manifests'Position /= 680, "Request.Post_Manifests");
      pragma Compile_Time_Error (X.Rows'Position /= 696, "Request.Rows");
      pragma Compile_Time_Error (X.Row_Count'Position /= 704, "Request.Row_Count");
      pragma Compile_Time_Error (X.Required'Position /= 712, "Request.Required");
      pragma Compile_Time_Error (X.Required_Count'Position /= 720, "Request.Required_Count");
      pragma Compile_Time_Error (X.Completion'Position /= 728, "Request.Completion");
      pragma Compile_Time_Error (X.Content'Position /= 760, "Request.Content");
      pragma Compile_Time_Error (X.Environment_Root'Position /= 776, "Request.Environment_Root");
      pragma Compile_Time_Error (X.Evidence_Root'Position /= 808, "Request.Evidence_Root");
      pragma Compile_Time_Error (X.Context'Position /= 840, "Request.Context");
      pragma Compile_Time_Error (X.Source_Id'Position /= 856, "Request.Source_Id");
      pragma Compile_Time_Error (X.Evidence'Position /= 872, "Request.Evidence");
      pragma Compile_Time_Error (X.Environment'Position /= 888, "Request.Environment");
      return (case Field is
        when 0 => Request'Object_Size / System.Storage_Unit,
        when 1 => Request'Alignment,
        when 2 => 0, when 3 => 4, when 4 => 8, when 5 => 16,
        when 6 => 24, when 7 => 280, when 8 => 664, when 9 => 680,
        when 10 => 696, when 11 => 704, when 12 => 712, when 13 => 720,
        when 14 => 728, when 15 => 760, when 16 => 776, when 17 => 808,
        when 18 => 840, when 19 => 856, when 20 => 872, when 21 => 888,
        when others => I64'Last);
   end Layout_Request;

   function Layout_Result (Field : U32) return I64 is
      Empty_Digest : constant Digest := (others => 0);
      Y : constant Result :=
        (Reason => 0, State => 0, Outcome => 0, Promotion => 0,
         Finalization_State => 0, Finalization_Outcome => 0,
         Identity => Empty_Digest);
      Units : constant I64 := Result'Object_Size / System.Storage_Unit;
   begin
      pragma Compile_Time_Error (Y.Reason'Position /= 0, "Result.Reason");
      pragma Compile_Time_Error (Y.State'Position /= 4, "Result.State");
      pragma Compile_Time_Error (Y.Outcome'Position /= 8, "Result.Outcome");
      pragma Compile_Time_Error (Y.Promotion'Position /= 12, "Result.Promotion");
      pragma Compile_Time_Error
        (Y.Finalization_State'Position /= 16, "Result.Finalization_State");
      pragma Compile_Time_Error
        (Y.Finalization_Outcome'Position /= 20, "Result.Finalization_Outcome");
      pragma Compile_Time_Error (Y.Identity'Position /= 24, "Result.Identity");
      return (case Field is
        when 0 => Units,
        when 1 => Result'Alignment,
        when 2 => 0, when 3 => 4, when 4 => 8, when 5 => 12,
        when 6 => 16, when 7 => 20, when 8 => 24, when others => I64'Last);
   end Layout_Result;

   pragma Compile_Time_Error
     (I64 (Storage_Offset'Last) /= I64'Last,
      "layout sentinel must stay I64'Last");
   function Layout (Kind, Field : U32) return I64 is
     (case Kind is
        when 1 => Layout_Start (Field),
        when 2 => Layout_Input (Field),
        when 3 => Layout_Row (Field),
        when 4 => Layout_Request (Field),
        when 5 => Layout_Result (Field),
        when others => I64'Last);
end Evaluation_Finalization_C;

with Worldline.Evaluation_Wire;
package body Evaluation_Finalization with SPARK_Mode is
   --  The content-erasure lemma compares derived identity records. Their
   --  predefined equality is inherited and already part of those types; these
   --  clauses only make that operator visible. They do not change any contract.
   use type T.Attempt_Binding;
   use type T.Captured_Bytes;
   use type T.Check_Identity;
   use type T.Optional_Execution;
   use type T.Optional_Verifier;
   use type T.Source_Identity;
   use type Worldline.Evaluation_Wire.Raw_Record;

   function Record_Start
     (A : T.Bytes; S : Start_Record; Plans : R.Check_Array;
      Before : Optional_Start) return Start_Update
   is
      Decision : constant Write_Decision := Start_Reference (A, S, Plans, Before);
   begin
      if Decision = Insert then
         return (Decision => Decision, Updated => (Present => True, Value => S));
      end if;
      return (Decision => Decision, Updated => Before);
   end Record_Start;

   function Record_Input
     (A : T.Bytes; S : Start_Record; I : Input_Record; Plans : R.Check_Array;
      Before : Optional_Input) return Input_Update
   is
      Decision : constant Write_Decision := Input_Reference (A, S, I, Plans, Before);
   begin
      if Decision = Insert then
         return (Decision => Decision, Updated => (Present => True, Value => I));
      end if;
      return (Decision => Decision, Updated => Before);
   end Record_Input;

   function Bind_Rows (S : Start_Record; Content : T.Content_Identity;
                       Rows : Start_Rows) return R.Measured_Array is
      Result : R.Measured_Array (Rows'Range) with Relaxed_Initialization;
   begin
      for K in Rows'Range loop
         Result (K) := Bind_Row (S, Content, Rows (K));
         pragma Loop_Invariant
           (for all J in Rows'First .. K => Result (J)'Initialized);
         pragma Loop_Invariant
           (for all J in Rows'First .. K =>
              Result (J) = Bind_Row (S, Content, Rows (J)));
      end loop;
      pragma Assert (Result'Initialized);
      return Result;
   end Bind_Rows;

   function Classify_Capture
     (A : T.Bytes; S : Start_Record; I : Input_Record;
      Post_Root, Post_Manifests : T.Captured_Bytes; Rows : Start_Rows;
      Plans : R.Check_Array;
      Completion : R.Required_Check) return Capture_Result is
   begin
      if not Capture_Valid
        (A, S, I, Post_Root, Post_Manifests, Rows, Plans, Completion)
      then
         return (Capture_Invalid, No_Classification);
      elsif not Input_Unchanged (A, I, Post_Root, Post_Manifests) then
         return (Capture_Observed, No_Classification);
      end if;
      return (Capture_Observed, R.Classify
        (A, Bound_To (S, (1, 0)), Bind_Rows (S, (1, 0), Rows), Requirements (S, Plans),
         S.Declaration, (Bound_To (S, (1, 0)), I.Root, Post_Root), Completion));
   end Classify_Capture;

   function Content_Matches
     (A : T.Bytes; Content : T.Content_Identity; Digest : Worldline.Hash)
      return Boolean is
      Prefix : constant String := "sha256:";
      Hex : constant String := "0123456789abcdef";
   begin
      if not P.Valid (A, T.Span (Content))
        or else Content.Length /= Prefix'Length + Digest'Length * 2
      then
         return False;
      end if;
      for K in Prefix'Range loop
         if A (Content.First + T.Count (K - Prefix'First)) /=
           P.Byte (Character'Pos (Prefix (K)))
         then
            return False;
         end if;
         pragma Loop_Invariant
           (for all J in Prefix'First .. K =>
             A (Content.First + T.Count (J - Prefix'First)) =
               P.Byte (Character'Pos (Prefix (J))));
      end loop;
      for K in Digest'Range loop
         if A ((Content.First + Prefix'Length) + T.Count (K - Digest'First) * 2) /=
           P.Byte (Character'Pos (Hex (Integer (Digest (K)) / 16 + Hex'First)))
           or else
           A (((Content.First + Prefix'Length) + T.Count (K - Digest'First) * 2) + 1) /=
           P.Byte (Character'Pos (Hex (Integer (Digest (K)) mod 16 + Hex'First)))
         then
            return False;
         end if;
         pragma Loop_Invariant
           (for all J in Digest'First .. K =>
             A ((Content.First + Prefix'Length) + T.Count (J - Digest'First) * 2) =
               P.Byte (Character'Pos (Hex (Integer (Digest (J)) / 16 + Hex'First)))
             and then
             A (((Content.First + Prefix'Length) + T.Count (J - Digest'First) * 2) + 1) =
               P.Byte (Character'Pos (Hex (Integer (Digest (J)) mod 16 + Hex'First))));
      end loop;
      return True;
   end Content_Matches;

   function Payload_Spans (Rows : Start_Rows) return Canonical_Artifacts.Span_Array is
      Result : Canonical_Artifacts.Span_Array (Rows'Range) with Relaxed_Initialization;
   begin
      for K in Rows'Range loop
         Result (K) := P.Span (Rows (K).Payload);
         pragma Loop_Invariant
           (for all J in Rows'First .. K => Result (J)'Initialized);
         pragma Loop_Invariant
           (for all J in Rows'First .. K => Result (J) = P.Span (Rows (J).Payload));
      end loop;
      pragma Assert (Result'Initialized);
      return Result;
   end Payload_Spans;

   function Seal_Reference
     (A : T.Bytes; S : Start_Record; I : Input_Record;
      Post_Root, Post_Manifests : T.Captured_Bytes; Rows : Start_Rows;
      Plans : R.Check_Array;
      Completion : R.Required_Check; Content : T.Content_Identity;
      Components : Final_Components; Artifacts : Artifact_References) return Seal_Result is
      Identity : constant Worldline.Hash := Final_Identity (S, I, Components);
      Classified : R.Classification;
   begin
      if not Capture_Valid
        (A, S, I, Post_Root, Post_Manifests, Rows, Plans, Completion)
        or else not Artifacts_Valid (A, Artifacts)
        or else not Artifact_Binding (A, Rows, Components, Artifacts)
      then
         return (Seal_Invalid, Worldline.Zero_Hash, No_Classification, (Present => False));
      elsif not Content_Matches (A, Content, Identity) then
         return (Content_Mismatch, Worldline.Zero_Hash, No_Classification, (Present => False));
      end if;
      if Input_Unchanged (A, I, Post_Root, Post_Manifests) then
         Classified := R.Reference
           (A, Bound_To (S, Content), Bind_Rows (S, Content, Rows), Requirements (S, Plans),
            S.Declaration, (Bound_To (S, Content), I.Root, Post_Root), Completion);
      else
         Classified := No_Classification;
      end if;
      if Classified.State /= E.Completed and then
        (for some K in Rows'Range => R.Old.Names_Completion (A, Rows (K).Check))
      then
         return (Seal_Invalid, Worldline.Zero_Hash, No_Classification, (Present => False));
      end if;
      return (Seal_Observed, Identity, Classified,
        (True, History_Projection (S, Content, Classified)));
   end Seal_Reference;

   --  Ghost-only proof structure; no contract, decision or stored value
   --  changes. Selected is the last matching row, so rows with equal Check
   --  spans select the same index.
   procedure Lemma_Selected_Same
     (A : T.Bytes; L, Rt : R.Measured_Array; Check : T.Check_Identity)
     with Ghost, Global => null,
       Pre => L'First = Rt'First and then L'Last = Rt'Last
         and then (for all K in L'Range => L (K).Item.Check = Rt (K).Item.Check),
       Post => R.Selected (A, L, Check) = R.Selected (A, Rt, Check);
   procedure Lemma_Selected_Same
     (A : T.Bytes; L, Rt : R.Measured_Array; Check : T.Check_Identity)
   is
      SL : constant T.Count := R.Selected (A, L, Check);
      SR : constant T.Count := R.Selected (A, Rt, Check);
   begin
      pragma Assert
        (if SL /= 0 then P.Same (A, T.Span (Rt (SL).Item.Check), T.Span (Check)));
      pragma Assert
        (if SR /= 0 then P.Same (A, T.Span (L (SR).Item.Check), T.Span (Check)));
   end Lemma_Selected_Same;

   --  The classifier reads the content coordinate only through reflexive
   --  Same_Binding of one Bound_To value with itself. Any valid Content and
   --  the erased (1, 0) coordinate therefore classify identically.
   --  Each local proof stage has a checked contract and retains its original
   --  assertion expressions. No fact is assumed or check omitted. All
   --  bodies and every call-site precondition remain full strict obligations.
   procedure Lemma_Content_Rows
     (A : T.Bytes; B1, B0 : T.Attempt_Binding;
      M1, M0 : R.Measured_Array)
     with Ghost, Global => null, Always_Terminates,
       Pre => M1'First = M0'First and then M1'Last = M0'Last
         and then (for all K in M1'Range =>
           M1 (K).Item.Binding = B1 and M0 (K).Item.Binding = B0
           and M1 (K).Item.Check = M0 (K).Item.Check
           and M1 (K).Item.Source = M0 (K).Item.Source
           and M1 (K).Item.Execution = M0 (K).Item.Execution
           and M1 (K).Item.Verifier = M0 (K).Item.Verifier
           and M1 (K).Item.State = M0 (K).Item.State
           and M1 (K).Item.Outcome = M0 (K).Item.Outcome
           and M1 (K).Item.Payload = M0 (K).Item.Payload
           and M1 (K).Raw = M0 (K).Raw
           and M1 (K).Confinement = M0 (K).Confinement
           and M1 (K).Declared = M0 (K).Declared)
         and then T.Same_Binding (A, B1, B1) = T.Same_Binding (A, B0, B0),
       Post => (for all K in M1'Range =>
           R.Row_Bound (A, M1 (K), B1) = R.Row_Bound (A, M0 (K), B0))
         and then (for all K in M1'Range =>
           R.Matches_Classification (M1 (K)) = R.Matches_Classification (M0 (K)));
   procedure Lemma_Content_Rows
     (A : T.Bytes; B1, B0 : T.Attempt_Binding;
      M1, M0 : R.Measured_Array)
   is
   begin
      pragma Assert
        (for all K in M1'Range =>
           R.Row_Bound (A, M1 (K), B1) = R.Row_Bound (A, M0 (K), B0));
      pragma Assert
        (for all K in M1'Range =>
           R.Matches_Classification (M1 (K)) = R.Matches_Classification (M0 (K)));
   end Lemma_Content_Rows;

   procedure Lemma_Content_Completion
     (A : T.Bytes; B1, B0 : T.Attempt_Binding;
      M1, M0 : R.Measured_Array; C1, C0 : R.Context_Measurement;
      Completion : R.Required_Check)
     with Ghost, Global => null, Always_Terminates,
       Pre => M1'First = M0'First and then M1'Last = M0'Last
         and then (for all K in M1'Range =>
           M1 (K).Item.Binding = B1 and M0 (K).Item.Binding = B0
           and M1 (K).Item.Check = M0 (K).Item.Check
           and M1 (K).Item.Source = M0 (K).Item.Source
           and M1 (K).Item.Execution = M0 (K).Item.Execution
           and M1 (K).Item.Verifier = M0 (K).Item.Verifier
           and M1 (K).Item.State = M0 (K).Item.State
           and M1 (K).Item.Outcome = M0 (K).Item.Outcome
           and M1 (K).Item.Payload = M0 (K).Item.Payload
           and M1 (K).Raw = M0 (K).Raw
           and M1 (K).Confinement = M0 (K).Confinement
           and M1 (K).Declared = M0 (K).Declared)
         and then (for all K in M1'Range =>
           R.Row_Bound (A, M1 (K), B1) = R.Row_Bound (A, M0 (K), B0))
         and then (R.Old.Context_Matches (A, B1, C1) = R.Old.Context_Matches (A, B0, C0)),
       Post => R.Evaluation_Completed (A, B1, M1, C1, Completion)
         = R.Evaluation_Completed (A, B0, M0, C0, Completion);
   procedure Lemma_Content_Completion
     (A : T.Bytes; B1, B0 : T.Attempt_Binding;
      M1, M0 : R.Measured_Array; C1, C0 : R.Context_Measurement;
      Completion : R.Required_Check)
   is
   begin
      pragma Assert
        (R.Evaluation_Completed (A, B1, M1, C1, Completion)
         = R.Evaluation_Completed (A, B0, M0, C0, Completion));
   end Lemma_Content_Completion;

   procedure Lemma_Content_Failure
     (A : T.Bytes; B1, B0 : T.Attempt_Binding;
      M1, M0 : R.Measured_Array; Req : R.Check_Array;
      C1, C0 : R.Context_Measurement; Completion : R.Required_Check)
     with Ghost, Global => null, Always_Terminates,
       Pre => M1'First = M0'First and then M1'Last = M0'Last
         and then (for all K in M1'Range =>
           M1 (K).Item.Binding = B1 and M0 (K).Item.Binding = B0
           and M1 (K).Item.Check = M0 (K).Item.Check
           and M1 (K).Item.Source = M0 (K).Item.Source
           and M1 (K).Item.Execution = M0 (K).Item.Execution
           and M1 (K).Item.Verifier = M0 (K).Item.Verifier
           and M1 (K).Item.State = M0 (K).Item.State
           and M1 (K).Item.Outcome = M0 (K).Item.Outcome
           and M1 (K).Item.Payload = M0 (K).Item.Payload
           and M1 (K).Raw = M0 (K).Raw
           and M1 (K).Confinement = M0 (K).Confinement
           and M1 (K).Declared = M0 (K).Declared)
         and then (for all K in M1'Range =>
           R.Row_Bound (A, M1 (K), B1) = R.Row_Bound (A, M0 (K), B0))
         and then (R.Evaluation_Completed (A, B1, M1, C1, Completion)
         = R.Evaluation_Completed (A, B0, M0, C0, Completion)),
       Post => (for all Q in Req'Range =>
           R.Failure_For_Check_Reference (A, B1, M1, Req (Q).Check)
           = R.Failure_For_Check_Reference (A, B0, M0, Req (Q).Check))
         and then (R.Genuine_Required_Failure (A, B1, M1, Req, C1, Completion)
         = R.Genuine_Required_Failure (A, B0, M0, Req, C0, Completion));
   procedure Lemma_Content_Failure
     (A : T.Bytes; B1, B0 : T.Attempt_Binding;
      M1, M0 : R.Measured_Array; Req : R.Check_Array;
      C1, C0 : R.Context_Measurement; Completion : R.Required_Check)
   is
   begin
      pragma Assert
        (for all Q in Req'Range =>
           R.Failure_For_Check_Reference (A, B1, M1, Req (Q).Check)
           = R.Failure_For_Check_Reference (A, B0, M0, Req (Q).Check));
      pragma Assert
        (R.Genuine_Required_Failure (A, B1, M1, Req, C1, Completion)
         = R.Genuine_Required_Failure (A, B0, M0, Req, C0, Completion));
   end Lemma_Content_Failure;

   procedure Lemma_Content_Promotion
     (A : T.Bytes; B1, B0 : T.Attempt_Binding;
      M1, M0 : R.Measured_Array; Req : R.Check_Array; Policy : R.Declaration;
      C1, C0 : R.Context_Measurement; Completion : R.Required_Check)
     with Ghost, Global => null, Always_Terminates,
       Pre => M1'First = M0'First and then M1'Last = M0'Last
         and then (for all K in M1'Range =>
           M1 (K).Item.Binding = B1 and M0 (K).Item.Binding = B0
           and M1 (K).Item.Check = M0 (K).Item.Check
           and M1 (K).Item.Source = M0 (K).Item.Source
           and M1 (K).Item.Execution = M0 (K).Item.Execution
           and M1 (K).Item.Verifier = M0 (K).Item.Verifier
           and M1 (K).Item.State = M0 (K).Item.State
           and M1 (K).Item.Outcome = M0 (K).Item.Outcome
           and M1 (K).Item.Payload = M0 (K).Item.Payload
           and M1 (K).Raw = M0 (K).Raw
           and M1 (K).Confinement = M0 (K).Confinement
           and M1 (K).Declared = M0 (K).Declared)
         and then (for all K in M1'Range =>
           R.Row_Bound (A, M1 (K), B1) = R.Row_Bound (A, M0 (K), B0))
         and then (for all K in M1'Range =>
           R.Matches_Classification (M1 (K)) = R.Matches_Classification (M0 (K)))
         and then (R.Evaluation_Completed (A, B1, M1, C1, Completion)
         = R.Evaluation_Completed (A, B0, M0, C0, Completion))
         and then (for all Q in Req'Range =>
           (R.Selected (A, M1, Req (Q).Check) /= 0
            and then R.Required_Evidence
              (A, M1 (R.Selected (A, M1, Req (Q).Check)), Req (Q)))
           = (R.Selected (A, M0, Req (Q).Check) /= 0
            and then R.Required_Evidence
              (A, M0 (R.Selected (A, M0, Req (Q).Check)), Req (Q)))),
       Post => R.Promotion_Roster (A, B1, M1, Req, Policy, C1, Completion)
         = R.Promotion_Roster (A, B0, M0, Req, Policy, C0, Completion);
   procedure Lemma_Content_Promotion
     (A : T.Bytes; B1, B0 : T.Attempt_Binding;
      M1, M0 : R.Measured_Array; Req : R.Check_Array; Policy : R.Declaration;
      C1, C0 : R.Context_Measurement; Completion : R.Required_Check)
   is
   begin
      pragma Assert
        (R.Promotion_Roster (A, B1, M1, Req, Policy, C1, Completion)
         = R.Promotion_Roster (A, B0, M0, Req, Policy, C0, Completion));
   end Lemma_Content_Promotion;

   procedure Lemma_Content_Erasure
     (A : T.Bytes; S : Start_Record; I : Input_Record;
      Post_Root : T.Captured_Bytes; Rows : Start_Rows;
      Plans : R.Check_Array; Completion : R.Required_Check;
      Content : T.Content_Identity)
     with Ghost, Global => null,
       Pre => P.Valid (A, T.Span (Content)),
       Post => R.Reference
           (A, Bound_To (S, Content), Bind_Rows (S, Content, Rows),
            Requirements (S, Plans), S.Declaration,
            (Bound_To (S, Content), I.Root, Post_Root), Completion)
         = R.Reference
           (A, Bound_To (S, (1, 0)), Bind_Rows (S, (1, 0), Rows),
            Requirements (S, Plans), S.Declaration,
            (Bound_To (S, (1, 0)), I.Root, Post_Root), Completion);
   procedure Lemma_Content_Erasure
     (A : T.Bytes; S : Start_Record; I : Input_Record;
      Post_Root : T.Captured_Bytes; Rows : Start_Rows;
      Plans : R.Check_Array; Completion : R.Required_Check;
      Content : T.Content_Identity)
   is
      B1 : constant T.Attempt_Binding := Bound_To (S, Content);
      B0 : constant T.Attempt_Binding := Bound_To (S, (1, 0));
      M1 : constant R.Measured_Array := Bind_Rows (S, Content, Rows);
      M0 : constant R.Measured_Array := Bind_Rows (S, (1, 0), Rows);
      C1 : constant R.Context_Measurement := (B1, I.Root, Post_Root);
      C0 : constant R.Context_Measurement := (B0, I.Root, Post_Root);
      Req : constant R.Check_Array := Requirements (S, Plans);
   begin
      pragma Assert (P.Same (A, T.Span (Content), T.Span (Content)));
      pragma Assert (P.Same (A, P.Span'(1, 0), P.Span'(1, 0)));
      pragma Assert (T.Same_Binding (A, B1, B1) = T.Same_Binding (A, B0, B0));
      pragma Assert (M1'First = M0'First and then M1'Last = M0'Last);
      pragma Assert
        (for all K in M1'Range =>
           M1 (K).Item.Binding = B1 and M0 (K).Item.Binding = B0
           and M1 (K).Item.Check = M0 (K).Item.Check
           and M1 (K).Item.Source = M0 (K).Item.Source
           and M1 (K).Item.Execution = M0 (K).Item.Execution
           and M1 (K).Item.Verifier = M0 (K).Item.Verifier
           and M1 (K).Item.State = M0 (K).Item.State
           and M1 (K).Item.Outcome = M0 (K).Item.Outcome
           and M1 (K).Item.Payload = M0 (K).Item.Payload
           and M1 (K).Raw = M0 (K).Raw
           and M1 (K).Confinement = M0 (K).Confinement
           and M1 (K).Declared = M0 (K).Declared);
      Lemma_Content_Rows (A, B1, B0, M1, M0);
      pragma Assert
        (R.Old.Context_Matches (A, B1, C1) = R.Old.Context_Matches (A, B0, C0));
      Lemma_Content_Completion (A, B1, B0, M1, M0, C1, C0, Completion);
      Lemma_Content_Failure (A, B1, B0, M1, M0, Req, C1, C0, Completion);
      for Q in Req'Range loop
         Lemma_Selected_Same (A, M1, M0, Req (Q).Check);
         pragma Loop_Invariant
           (for all J in Req'First .. Q =>
              R.Selected (A, M1, Req (J).Check) = R.Selected (A, M0, Req (J).Check));
      end loop;
      pragma Assert
        (for all Q in Req'Range =>
           (R.Selected (A, M1, Req (Q).Check) /= 0
            and then R.Required_Evidence
              (A, M1 (R.Selected (A, M1, Req (Q).Check)), Req (Q)))
           = (R.Selected (A, M0, Req (Q).Check) /= 0
            and then R.Required_Evidence
              (A, M0 (R.Selected (A, M0, Req (Q).Check)), Req (Q))));
      Lemma_Content_Promotion
        (A, B1, B0, M1, M0, Req, S.Declaration, C1, C0, Completion);
   end Lemma_Content_Erasure;

   function Seal
     (A : T.Bytes; S : Start_Record; I : Input_Record;
      Post_Root, Post_Manifests : T.Captured_Bytes; Rows : Start_Rows;
      Plans : R.Check_Array;
      Completion : R.Required_Check; Content : T.Content_Identity;
      Components : Final_Components; Artifacts : Artifact_References) return Seal_Result is
      Identity : constant Worldline.Hash := Final_Identity (S, I, Components);
      Classified : R.Classification;
   begin
      if not Capture_Valid
        (A, S, I, Post_Root, Post_Manifests, Rows, Plans, Completion)
        or else not Artifacts_Valid (A, Artifacts)
        or else not Artifact_Binding (A, Rows, Components, Artifacts)
      then
         return (Seal_Invalid, Worldline.Zero_Hash, No_Classification, (Present => False));
      elsif not Content_Matches (A, Content, Identity) then
         return (Content_Mismatch, Worldline.Zero_Hash, No_Classification, (Present => False));
      end if;
      if Input_Unchanged (A, I, Post_Root, Post_Manifests) then
         Classified := R.Classify
           (A, Bound_To (S, Content), Bind_Rows (S, Content, Rows), Requirements (S, Plans),
            S.Declaration, (Bound_To (S, Content), I.Root, Post_Root), Completion);
         pragma Assert
           (Classified = R.Reference
             (A, Bound_To (S, Content), Bind_Rows (S, Content, Rows), Requirements (S, Plans),
              S.Declaration, (Bound_To (S, Content), I.Root, Post_Root), Completion));
         Lemma_Content_Erasure
           (A, S, I, Post_Root, Rows, Plans, Completion, Content);
         pragma Assert
           (Classified = R.Reference
             (A, Bound_To (S, (1, 0)), Bind_Rows (S, (1, 0), Rows), Requirements (S, Plans),
              S.Declaration, (Bound_To (S, (1, 0)), I.Root, Post_Root), Completion));
      else
         Classified := No_Classification;
      end if;
      if Classified.State /= E.Completed and then
        (for some K in Rows'Range => R.Old.Names_Completion (A, Rows (K).Check))
      then
         return (Seal_Invalid, Worldline.Zero_Hash, No_Classification, (Present => False));
      end if;
      return (Seal_Observed, Identity, Classified,
        (True, History_Projection (S, Content, Classified)));
   end Seal;
end Evaluation_Finalization;

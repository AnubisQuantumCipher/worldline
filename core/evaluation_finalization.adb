package body Evaluation_Finalization with SPARK_Mode is

   procedure Record_Start
     (A : T.Bytes; S : Start_Record; Plans : R.Check_Array; Current : in out Optional_Start;
      Decision : out Write_Decision) is
   begin
      Decision := Start_Reference (A, S, Plans, Current);
      if Decision = Insert then
         Current := (Present => True, Value => S);
      end if;
   end Record_Start;

   procedure Record_Input
     (A : T.Bytes; S : Start_Record; I : Input_Record; Plans : R.Check_Array;
      Current : in out Optional_Input; Decision : out Write_Decision) is
   begin
      Decision := Input_Reference (A, S, I, Plans, Current);
      if Decision = Insert then
         Current := (Present => True, Value => I);
      end if;
   end Record_Input;

   function Bind_Rows (S : Start_Record; Content : T.Content_Identity;
                       Rows : Start_Rows) return R.Measured_Array is
      Result : R.Measured_Array (Rows'Range);
   begin
      for K in Rows'Range loop
         Result (K) := Bind_Row (S, Content, Rows (K));
         pragma Loop_Invariant
           (for all J in Rows'First .. K =>
              Result (J) = Bind_Row (S, Content, Rows (J)));
      end loop;
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
         if A (Content.First + Prefix'Length + T.Count (K - Digest'First) * 2) /=
           P.Byte (Character'Pos (Hex (Integer (Digest (K)) / 16 + Hex'First)))
           or else
           A (Content.First + Prefix'Length + T.Count (K - Digest'First) * 2 + 1) /=
           P.Byte (Character'Pos (Hex (Integer (Digest (K)) mod 16 + Hex'First)))
         then
            return False;
         end if;
         pragma Loop_Invariant
           (for all J in Digest'First .. K =>
             A (Content.First + Prefix'Length + T.Count (J - Digest'First) * 2) =
               P.Byte (Character'Pos (Hex (Integer (Digest (J)) / 16 + Hex'First)))
             and then
             A (Content.First + Prefix'Length + T.Count (J - Digest'First) * 2 + 1) =
               P.Byte (Character'Pos (Hex (Integer (Digest (J)) mod 16 + Hex'First))));
      end loop;
      return True;
   end Content_Matches;

   function Payload_Spans (Rows : Start_Rows) return Canonical_Artifacts.Span_Array is
      Result : Canonical_Artifacts.Span_Array (Rows'Range);
   begin
      for K in Rows'Range loop
         Result (K) := P.Span (Rows (K).Payload);
         pragma Loop_Invariant
           (for all J in Rows'First .. K => Result (J) = P.Span (Rows (J).Payload));
      end loop;
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

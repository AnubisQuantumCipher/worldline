package body Worldline.Native_Execution_Views with SPARK_Mode is
   package A renames D.A;
   package E renames X.E;
   package J renames Y.J;
   use type Interfaces.Unsigned_8;
   use type Interfaces.Unsigned_32;
   use type T.A.Grant;
   use type T.A.Use_Row;
   use type T.A.C.Chain_Row;
   function Scoped_Check
     (Raw : N.Raw_Packet;
      Data : Q.Byte_Array;
      History : N.Raw_History_Array;
      Proposed_History : N.Raw_History_Array;
      Rows : W.Raw_Row_Array;
      Proposed_Rows : W.Raw_Row_Array;
      Projection : N.Raw_Projection_Array;
      Proposed_Projection : N.Raw_Projection_Array;
      Buckets : N.Raw_Bucket_Array;
      Proposed_Buckets : N.Raw_Bucket_Array;
      Actual_Buckets : N.Raw_Bucket_Array;
      Observed : W.Raw_Native_Array;
      Facts : N.Raw_Facts_Array) return Result is
   begin
      if not N.Well_Formed (Data, Raw, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts) then return Rejected; end if;
      return (True, N.Decide (Data, Raw, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts).Status);
   end Scoped_Check;
   function Scoped_Validate
     (Raw : N.Raw_Packet;
      Data : Q.Byte_Array;
      History : N.Raw_History_Array;
      Proposed_History : N.Raw_History_Array;
      Rows : W.Raw_Row_Array;
      Proposed_Rows : W.Raw_Row_Array;
      Projection : N.Raw_Projection_Array;
      Proposed_Projection : N.Raw_Projection_Array;
      Buckets : N.Raw_Bucket_Array;
      Proposed_Buckets : N.Raw_Bucket_Array;
      Actual_Buckets : N.Raw_Bucket_Array;
      Observed : W.Raw_Native_Array;
      Facts : N.Raw_Facts_Array) return Result is
   begin
      if not N.Well_Formed (Data, Raw, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts) then return Rejected; end if;
      return (True, N.Validate (Data, Raw, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts).Status);
   end Scoped_Validate;
   function Scoped_Classify
     (Raw : N.Raw_Packet;
      Data : Q.Byte_Array;
      History : N.Raw_History_Array;
      Proposed_History : N.Raw_History_Array;
      Rows : W.Raw_Row_Array;
      Proposed_Rows : W.Raw_Row_Array;
      Projection : N.Raw_Projection_Array;
      Proposed_Projection : N.Raw_Projection_Array;
      Buckets : N.Raw_Bucket_Array;
      Proposed_Buckets : N.Raw_Bucket_Array;
      Actual_Buckets : N.Raw_Bucket_Array;
      Observed : W.Raw_Native_Array;
      Facts : N.Raw_Facts_Array) return Result is
   begin
      if not N.Well_Formed (Data, Raw, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts) then return Rejected; end if;
      return (True, N.Classify_Selected (Data, Raw, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts).Status);
   end Scoped_Classify;
   function Observation_Classify
     (Raw : O.Raw_Input;
      Data : Q.Byte_Array) return Result is
   begin
      return (True, O.L.Liveness'Pos (O.Classify (Data, Raw)));
   end Observation_Classify;
   function Observation_Current
     (Raw : O.Raw_Input;
      Data : Q.Byte_Array) return Result is
   begin
      return (True, Boolean'Pos (O.Current (Data, Raw)));
   end Observation_Current;
   function Observation_Genesis_Current
     (Raw : O.Raw_Input;
      Data : Q.Byte_Array) return Result is
   begin
      return (True, Boolean'Pos (O.Genesis_Current (Data, Raw)));
   end Observation_Genesis_Current;
   function Actor_Expected
     (Raw : D.Raw_Packet;
      Data : Q.Byte_Array;
      History : N.Raw_History_Array;
      Proposed_History : N.Raw_History_Array;
      Rows : W.Raw_Row_Array;
      Proposed_Rows : W.Raw_Row_Array;
      Projection : N.Raw_Projection_Array;
      Proposed_Projection : N.Raw_Projection_Array;
      Buckets : N.Raw_Bucket_Array;
      Proposed_Buckets : N.Raw_Bucket_Array;
      Actual_Buckets : N.Raw_Bucket_Array;
      Observed : W.Raw_Native_Array;
      Facts : N.Raw_Facts_Array;
      Capabilities : D.Raw_Capability_Array;
      Groups : D.Raw_Group_Array;
      Proc_Groups : D.Raw_Group_Array) return Result is
   begin
      if not (N.Well_Formed (Data, Raw.Ledger, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts)
        and then D.Well_Formed (Data, Raw.Captured)
        and then (for all I in Capabilities'Range => D.Well_Formed (Data, Capabilities (I)))
        and then (for all I in Groups'Range => W.Well_Formed (Data, Groups (I)))
        and then (for all I in Proc_Groups'Range => W.Well_Formed (Data, Proc_Groups (I)))) then return Rejected; end if;
      return (True, A.Status'Pos (A.Reference (Data, N.Decode (Data, Raw.Ledger.Before_State), N.Decode_History (Data, History),
         W.Decode_Rows (Data, Rows), N.Decode_Projection (Data, Projection),
         N.Decode_Bucket (Data, Buckets), W.Decode_Native (Data, Observed),
         N.Decode_Facts (Data, Facts), N.Decode (Data, Raw.Ledger.Current),
         D.Decode (Data, Raw.Captured), D.Decode_Capabilities (Data, Capabilities),
         D.Decode_Groups (Data, Groups), D.Decode_Groups (Data, Proc_Groups))));
   end Actor_Expected;
   function Actor_Check
     (Raw : D.Raw_Packet;
      Data : Q.Byte_Array;
      History : N.Raw_History_Array;
      Proposed_History : N.Raw_History_Array;
      Rows : W.Raw_Row_Array;
      Proposed_Rows : W.Raw_Row_Array;
      Projection : N.Raw_Projection_Array;
      Proposed_Projection : N.Raw_Projection_Array;
      Buckets : N.Raw_Bucket_Array;
      Proposed_Buckets : N.Raw_Bucket_Array;
      Actual_Buckets : N.Raw_Bucket_Array;
      Observed : W.Raw_Native_Array;
      Facts : N.Raw_Facts_Array;
      Capabilities : D.Raw_Capability_Array;
      Groups : D.Raw_Group_Array;
      Proc_Groups : D.Raw_Group_Array) return Result is
   begin
      if not (N.Well_Formed (Data, Raw.Ledger, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts)
        and then D.Well_Formed (Data, Raw.Captured)
        and then (for all I in Capabilities'Range => D.Well_Formed (Data, Capabilities (I)))
        and then (for all I in Groups'Range => W.Well_Formed (Data, Groups (I)))
        and then (for all I in Proc_Groups'Range => W.Well_Formed (Data, Proc_Groups (I)))) then return Rejected; end if;
      return (True, A.Status'Pos (A.Check (Data, N.Decode (Data, Raw.Ledger.Before_State), N.Decode_History (Data, History),
         W.Decode_Rows (Data, Rows), N.Decode_Projection (Data, Projection),
         N.Decode_Bucket (Data, Buckets), W.Decode_Native (Data, Observed),
         N.Decode_Facts (Data, Facts), N.Decode (Data, Raw.Ledger.Current),
         D.Decode (Data, Raw.Captured), D.Decode_Capabilities (Data, Capabilities),
         D.Decode_Groups (Data, Groups), D.Decode_Groups (Data, Proc_Groups))));
   end Actor_Check;
   function Operation_Expected
     (Authority : T.Raw_Input;
      Authority_Data : Q.Byte_Array;
      Authority_Grants : Raw_Grant_Array;
      Authority_Uses : Raw_Use_Array;
      Authority_Receipts : Raw_Chain_Array;
      Authority_Events : Raw_Chain_Array) return Result is
      Grants : T.A.Grants (Authority_Grants'Range);
      Uses : T.A.Uses (Authority_Uses'Range);
      Receipts : T.A.C.Retained_Rows (Authority_Receipts'Range);
      Events : T.A.C.Retained_Rows (Authority_Events'Range);
   begin
      if not (T.Well_Formed (Authority)
        and then T.Recovery_Well_Formed (Authority_Data, Authority.Facts)
        and then (for all I in Authority_Grants'Range => T.Well_Formed (Authority_Grants (I)))
        and then (for all I in Authority_Uses'Range => T.Well_Formed (Authority_Uses (I)))
        and then (for all I in Authority_Receipts'Range => T.C.Well_Formed (Authority_Receipts (I)))
        and then (for all I in Authority_Events'Range => T.C.Well_Formed (Authority_Events (I)))) then return Rejected; end if;
      for I in Grants'Range loop
         Grants (I) := T.Decode (Authority_Grants (I));
         pragma Loop_Invariant (for all K in Grants'First .. I => Grants (K) = T.Decode (Authority_Grants (K)));
      end loop;
      for I in Uses'Range loop
         Uses (I) := T.Decode (Authority_Uses (I));
         pragma Loop_Invariant (for all K in Uses'First .. I => Uses (K) = T.Decode (Authority_Uses (K)));
      end loop;
      for I in Receipts'Range loop
         Receipts (I) := T.C.Decode (Authority_Receipts (I));
         pragma Loop_Invariant (for all K in Receipts'First .. I => Receipts (K) = T.C.Decode (Authority_Receipts (K)));
      end loop;
      for I in Events'Range loop
         Events (I) := T.C.Decode (Authority_Events (I));
         pragma Loop_Invariant (for all K in Events'First .. I => Events (K) = T.C.Decode (Authority_Events (K)));
      end loop;
      return (True, T.A.Decision'Pos (T.A.Reference (Authority_Data,
         Grants, Uses, T.Decode (Authority.Bound), T.Decode (Authority.Now).Value,
         T.A.Command'Val (Authority.Mode), T.Decode (Authority_Data, Authority.Facts), Receipts, Events)));
   end Operation_Expected;
   function Operation_Decide
     (Authority : T.Raw_Input;
      Authority_Data : Q.Byte_Array;
      Authority_Grants : Raw_Grant_Array;
      Authority_Uses : Raw_Use_Array;
      Authority_Receipts : Raw_Chain_Array;
      Authority_Events : Raw_Chain_Array) return Result is
      Grants : T.A.Grants (Authority_Grants'Range);
      Uses : T.A.Uses (Authority_Uses'Range);
      Receipts : T.A.C.Retained_Rows (Authority_Receipts'Range);
      Events : T.A.C.Retained_Rows (Authority_Events'Range);
   begin
      if not (T.Well_Formed (Authority)
        and then T.Recovery_Well_Formed (Authority_Data, Authority.Facts)
        and then (for all I in Authority_Grants'Range => T.Well_Formed (Authority_Grants (I)))
        and then (for all I in Authority_Uses'Range => T.Well_Formed (Authority_Uses (I)))
        and then (for all I in Authority_Receipts'Range => T.C.Well_Formed (Authority_Receipts (I)))
        and then (for all I in Authority_Events'Range => T.C.Well_Formed (Authority_Events (I)))) then return Rejected; end if;
      for I in Grants'Range loop
         Grants (I) := T.Decode (Authority_Grants (I));
         pragma Loop_Invariant (for all K in Grants'First .. I => Grants (K) = T.Decode (Authority_Grants (K)));
      end loop;
      for I in Uses'Range loop
         Uses (I) := T.Decode (Authority_Uses (I));
         pragma Loop_Invariant (for all K in Uses'First .. I => Uses (K) = T.Decode (Authority_Uses (K)));
      end loop;
      for I in Receipts'Range loop
         Receipts (I) := T.C.Decode (Authority_Receipts (I));
         pragma Loop_Invariant (for all K in Receipts'First .. I => Receipts (K) = T.C.Decode (Authority_Receipts (K)));
      end loop;
      for I in Events'Range loop
         Events (I) := T.C.Decode (Authority_Events (I));
         pragma Loop_Invariant (for all K in Events'First .. I => Events (K) = T.C.Decode (Authority_Events (K)));
      end loop;
      return (True, T.A.Decision'Pos (T.A.Decide (Authority_Data,
         Grants, Uses, T.Decode (Authority.Bound), T.Decode (Authority.Now).Value,
         T.A.Command'Val (Authority.Mode), T.Decode (Authority_Data, Authority.Facts), Receipts, Events)));
   end Operation_Decide;
   function Execution_Expected
     (Raw : D.Raw_Packet;
      Data : Q.Byte_Array;
      History : N.Raw_History_Array;
      Proposed_History : N.Raw_History_Array;
      Rows : W.Raw_Row_Array;
      Proposed_Rows : W.Raw_Row_Array;
      Projection : N.Raw_Projection_Array;
      Proposed_Projection : N.Raw_Projection_Array;
      Buckets : N.Raw_Bucket_Array;
      Proposed_Buckets : N.Raw_Bucket_Array;
      Actual_Buckets : N.Raw_Bucket_Array;
      Observed : W.Raw_Native_Array;
      Facts : N.Raw_Facts_Array;
      Capabilities : D.Raw_Capability_Array;
      Groups : D.Raw_Group_Array;
      Proc_Groups : D.Raw_Group_Array;
      Authority : T.Raw_Input;
      Authority_Data : Q.Byte_Array;
      Authority_Grants : Raw_Grant_Array;
      Authority_Uses : Raw_Use_Array;
      Authority_Receipts : Raw_Chain_Array;
      Authority_Events : Raw_Chain_Array;
      Crosswalk : X.Raw_Crosswalk) return Result is
      Grants : T.A.Grants (Authority_Grants'Range);
      Uses : T.A.Uses (Authority_Uses'Range);
      Receipts : T.A.C.Retained_Rows (Authority_Receipts'Range);
      Events : T.A.C.Retained_Rows (Authority_Events'Range);
   begin
      if not (N.Well_Formed (Data, Raw.Ledger, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts)
        and then D.Well_Formed (Data, Raw.Captured)
        and then (for all I in Capabilities'Range => D.Well_Formed (Data, Capabilities (I)))
        and then (for all I in Groups'Range => W.Well_Formed (Data, Groups (I)))
        and then (for all I in Proc_Groups'Range => W.Well_Formed (Data, Proc_Groups (I)))
        and then T.Well_Formed (Authority)
        and then T.Recovery_Well_Formed (Authority_Data, Authority.Facts)
        and then (for all I in Authority_Grants'Range => T.Well_Formed (Authority_Grants (I)))
        and then (for all I in Authority_Uses'Range => T.Well_Formed (Authority_Uses (I)))
        and then (for all I in Authority_Receipts'Range => T.C.Well_Formed (Authority_Receipts (I)))
        and then (for all I in Authority_Events'Range => T.C.Well_Formed (Authority_Events (I)))
        and then Authority.Mode = T.A.Command'Pos (T.A.Authorize_Execution)
        and then X.Well_Formed (Data, Crosswalk)) then return Rejected; end if;
      for I in Grants'Range loop
         Grants (I) := T.Decode (Authority_Grants (I));
         pragma Loop_Invariant (for all K in Grants'First .. I => Grants (K) = T.Decode (Authority_Grants (K)));
      end loop;
      for I in Uses'Range loop
         Uses (I) := T.Decode (Authority_Uses (I));
         pragma Loop_Invariant (for all K in Uses'First .. I => Uses (K) = T.Decode (Authority_Uses (K)));
      end loop;
      for I in Receipts'Range loop
         Receipts (I) := T.C.Decode (Authority_Receipts (I));
         pragma Loop_Invariant (for all K in Receipts'First .. I => Receipts (K) = T.C.Decode (Authority_Receipts (K)));
      end loop;
      for I in Events'Range loop
         Events (I) := T.C.Decode (Authority_Events (I));
         pragma Loop_Invariant (for all K in Events'First .. I => Events (K) = T.C.Decode (Authority_Events (K)));
      end loop;
      return (True, E.Status'Pos (E.Reference (Data, Authority_Data, N.Decode (Data, Raw.Ledger.Before_State), N.Decode_History (Data, History),
         W.Decode_Rows (Data, Rows), N.Decode_Projection (Data, Projection),
         N.Decode_Bucket (Data, Buckets), W.Decode_Native (Data, Observed),
         N.Decode_Facts (Data, Facts), N.Decode (Data, Raw.Ledger.Current),
         D.Decode (Data, Raw.Captured), D.Decode_Capabilities (Data, Capabilities),
         D.Decode_Groups (Data, Groups), D.Decode_Groups (Data, Proc_Groups),
         X.Decode (Data, Crosswalk), Grants, Uses, T.Decode (Authority.Bound),
         T.Decode (Authority.Now).Value, T.Decode (Authority_Data, Authority.Facts), Receipts, Events)));
   end Execution_Expected;
   function Execution_Decide
     (Raw : D.Raw_Packet;
      Data : Q.Byte_Array;
      History : N.Raw_History_Array;
      Proposed_History : N.Raw_History_Array;
      Rows : W.Raw_Row_Array;
      Proposed_Rows : W.Raw_Row_Array;
      Projection : N.Raw_Projection_Array;
      Proposed_Projection : N.Raw_Projection_Array;
      Buckets : N.Raw_Bucket_Array;
      Proposed_Buckets : N.Raw_Bucket_Array;
      Actual_Buckets : N.Raw_Bucket_Array;
      Observed : W.Raw_Native_Array;
      Facts : N.Raw_Facts_Array;
      Capabilities : D.Raw_Capability_Array;
      Groups : D.Raw_Group_Array;
      Proc_Groups : D.Raw_Group_Array;
      Authority : T.Raw_Input;
      Authority_Data : Q.Byte_Array;
      Authority_Grants : Raw_Grant_Array;
      Authority_Uses : Raw_Use_Array;
      Authority_Receipts : Raw_Chain_Array;
      Authority_Events : Raw_Chain_Array;
      Crosswalk : X.Raw_Crosswalk) return Result is
      Grants : T.A.Grants (Authority_Grants'Range);
      Uses : T.A.Uses (Authority_Uses'Range);
      Receipts : T.A.C.Retained_Rows (Authority_Receipts'Range);
      Events : T.A.C.Retained_Rows (Authority_Events'Range);
   begin
      if not (N.Well_Formed (Data, Raw.Ledger, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts)
        and then D.Well_Formed (Data, Raw.Captured)
        and then (for all I in Capabilities'Range => D.Well_Formed (Data, Capabilities (I)))
        and then (for all I in Groups'Range => W.Well_Formed (Data, Groups (I)))
        and then (for all I in Proc_Groups'Range => W.Well_Formed (Data, Proc_Groups (I)))
        and then T.Well_Formed (Authority)
        and then T.Recovery_Well_Formed (Authority_Data, Authority.Facts)
        and then (for all I in Authority_Grants'Range => T.Well_Formed (Authority_Grants (I)))
        and then (for all I in Authority_Uses'Range => T.Well_Formed (Authority_Uses (I)))
        and then (for all I in Authority_Receipts'Range => T.C.Well_Formed (Authority_Receipts (I)))
        and then (for all I in Authority_Events'Range => T.C.Well_Formed (Authority_Events (I)))
        and then Authority.Mode = T.A.Command'Pos (T.A.Authorize_Execution)
        and then X.Well_Formed (Data, Crosswalk)) then return Rejected; end if;
      for I in Grants'Range loop
         Grants (I) := T.Decode (Authority_Grants (I));
         pragma Loop_Invariant (for all K in Grants'First .. I => Grants (K) = T.Decode (Authority_Grants (K)));
      end loop;
      for I in Uses'Range loop
         Uses (I) := T.Decode (Authority_Uses (I));
         pragma Loop_Invariant (for all K in Uses'First .. I => Uses (K) = T.Decode (Authority_Uses (K)));
      end loop;
      for I in Receipts'Range loop
         Receipts (I) := T.C.Decode (Authority_Receipts (I));
         pragma Loop_Invariant (for all K in Receipts'First .. I => Receipts (K) = T.C.Decode (Authority_Receipts (K)));
      end loop;
      for I in Events'Range loop
         Events (I) := T.C.Decode (Authority_Events (I));
         pragma Loop_Invariant (for all K in Events'First .. I => Events (K) = T.C.Decode (Authority_Events (K)));
      end loop;
      return (True, E.Status'Pos (E.Decide (Data, Authority_Data, N.Decode (Data, Raw.Ledger.Before_State), N.Decode_History (Data, History),
         W.Decode_Rows (Data, Rows), N.Decode_Projection (Data, Projection),
         N.Decode_Bucket (Data, Buckets), W.Decode_Native (Data, Observed),
         N.Decode_Facts (Data, Facts), N.Decode (Data, Raw.Ledger.Current),
         D.Decode (Data, Raw.Captured), D.Decode_Capabilities (Data, Capabilities),
         D.Decode_Groups (Data, Groups), D.Decode_Groups (Data, Proc_Groups),
         X.Decode (Data, Crosswalk), Grants, Uses, T.Decode (Authority.Bound),
         T.Decode (Authority.Now).Value, T.Decode (Authority_Data, Authority.Facts), Receipts, Events)));
   end Execution_Decide;
   function Child_Expected
     (Raw : D.Raw_Packet;
      Data : Q.Byte_Array;
      History : N.Raw_History_Array;
      Proposed_History : N.Raw_History_Array;
      Rows : W.Raw_Row_Array;
      Proposed_Rows : W.Raw_Row_Array;
      Projection : N.Raw_Projection_Array;
      Proposed_Projection : N.Raw_Projection_Array;
      Buckets : N.Raw_Bucket_Array;
      Proposed_Buckets : N.Raw_Bucket_Array;
      Actual_Buckets : N.Raw_Bucket_Array;
      Observed : W.Raw_Native_Array;
      Facts : N.Raw_Facts_Array;
      Capabilities : D.Raw_Capability_Array;
      Groups : D.Raw_Group_Array;
      Proc_Groups : D.Raw_Group_Array;
      Authority : T.Raw_Input;
      Authority_Data : Q.Byte_Array;
      Authority_Grants : Raw_Grant_Array;
      Authority_Uses : Raw_Use_Array;
      Authority_Receipts : Raw_Chain_Array;
      Authority_Events : Raw_Chain_Array;
      Crosswalk : X.Raw_Crosswalk;
      Child : Y.Raw_Input;
      Tasks : Y.Raw_Task_Array;
      Processes : Y.Raw_Process_Array;
      Namespaces : Y.Raw_Namespace_Array) return Result is
      Grants : T.A.Grants (Authority_Grants'Range);
      Uses : T.A.Uses (Authority_Uses'Range);
      Receipts : T.A.C.Retained_Rows (Authority_Receipts'Range);
      Events : T.A.C.Retained_Rows (Authority_Events'Range);
   begin
      if not (N.Well_Formed (Data, Raw.Ledger, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts)
        and then T.Well_Formed (Authority)
        and then T.Recovery_Well_Formed (Authority_Data, Authority.Facts)
        and then (for all I in Authority_Grants'Range => T.Well_Formed (Authority_Grants (I)))
        and then (for all I in Authority_Uses'Range => T.Well_Formed (Authority_Uses (I)))
        and then (for all I in Authority_Receipts'Range => T.C.Well_Formed (Authority_Receipts (I)))
        and then (for all I in Authority_Events'Range => T.C.Well_Formed (Authority_Events (I)))
        and then Authority.Mode = T.A.Command'Pos (T.A.Authorize_Execution)
        and then X.Well_Formed (Data, Crosswalk)
        and then Y.Well_Formed (Data, Child)
        and then (if Child.Mode /= J.Admission_Mode'Pos (J.Root_Controller_Admission) then
          (for all I in Tasks'Range => Y.Well_Formed (Data, Tasks (I)))
          and then (for all I in Processes'Range => Y.Well_Formed (Data, Processes (I)))
          and then (for all I in Namespaces'Range => Y.Well_Formed (Data, Namespaces (I))))
        and then (if Child.Mode = J.Admission_Mode'Pos (J.Child_Admission) then
          D.Well_Formed (Data, Raw.Captured)
          and then (for all I in Capabilities'Range => D.Well_Formed (Data, Capabilities (I)))
          and then (for all I in Groups'Range => W.Well_Formed (Data, Groups (I)))
          and then (for all I in Proc_Groups'Range => W.Well_Formed (Data, Proc_Groups (I))))) then return Rejected; end if;
      for I in Grants'Range loop
         Grants (I) := T.Decode (Authority_Grants (I));
         pragma Loop_Invariant (for all K in Grants'First .. I => Grants (K) = T.Decode (Authority_Grants (K)));
      end loop;
      for I in Uses'Range loop
         Uses (I) := T.Decode (Authority_Uses (I));
         pragma Loop_Invariant (for all K in Uses'First .. I => Uses (K) = T.Decode (Authority_Uses (K)));
      end loop;
      for I in Receipts'Range loop
         Receipts (I) := T.C.Decode (Authority_Receipts (I));
         pragma Loop_Invariant (for all K in Receipts'First .. I => Receipts (K) = T.C.Decode (Authority_Receipts (K)));
      end loop;
      for I in Events'Range loop
         Events (I) := T.C.Decode (Authority_Events (I));
         pragma Loop_Invariant (for all K in Events'First .. I => Events (K) = T.C.Decode (Authority_Events (K)));
      end loop;
      if Child.Mode = J.Admission_Mode'Pos (J.Root_Controller_Admission) then
         return (True, J.Status'Pos (J.Root_Admission_Reference (Data, Authority_Data, N.Decode (Data, Raw.Ledger.Before_State), N.Decode_History (Data, History),
         W.Decode_Rows (Data, Rows), N.Decode_Projection (Data, Projection),
         N.Decode_Bucket (Data, Buckets), W.Decode_Native (Data, Observed),
         N.Decode_Facts (Data, Facts), N.Decode (Data, Raw.Ledger.Current),
         X.Decode (Data, Crosswalk), Grants, Uses, T.Decode (Authority.Bound),
         T.Decode (Authority.Now).Value, T.Decode (Authority_Data, Authority.Facts), Receipts, Events,
         Y.Decode (Data, Child.Controller))));
      elsif Child.Mode = J.Admission_Mode'Pos (J.Task_Reservation_Admission) then
         return (True, J.Status'Pos (J.Task_Admission_Reference (Data, Authority_Data, N.Decode (Data, Raw.Ledger.Before_State), N.Decode_History (Data, History),
         W.Decode_Rows (Data, Rows), N.Decode_Projection (Data, Projection),
         N.Decode_Bucket (Data, Buckets), W.Decode_Native (Data, Observed),
         N.Decode_Facts (Data, Facts), N.Decode (Data, Raw.Ledger.Current),
         X.Decode (Data, Crosswalk), Grants, Uses, T.Decode (Authority.Bound),
         T.Decode (Authority.Now).Value, T.Decode (Authority_Data, Authority.Facts), Receipts, Events,
         Y.Decode (Data, Child.Controller), N.Decode (Data, Raw.Ledger.Proposed_State),
         N.Decode_History (Data, Proposed_History), W.Decode_Rows (Data, Proposed_Rows),
         N.Decode_Projection (Data, Proposed_Projection), N.Decode_Bucket (Data, Proposed_Buckets),
         N.Decode_Bucket (Data, Actual_Buckets), N.Decode (Data, Raw.Ledger.Request),
         Y.Decode (Data, Child.Child_Task), Y.Decode_Task (Data, Tasks))));
      else
         return (True, J.Status'Pos (J.Reference (Data, Authority_Data, N.Decode (Data, Raw.Ledger.Before_State), N.Decode_History (Data, History),
         W.Decode_Rows (Data, Rows), N.Decode_Projection (Data, Projection),
         N.Decode_Bucket (Data, Buckets), W.Decode_Native (Data, Observed),
         N.Decode_Facts (Data, Facts), N.Decode (Data, Raw.Ledger.Current),
         X.Decode (Data, Crosswalk), Grants, Uses, T.Decode (Authority.Bound),
         T.Decode (Authority.Now).Value, T.Decode (Authority_Data, Authority.Facts), Receipts, Events,
         Y.Decode (Data, Child.Controller), D.Decode (Data, Raw.Captured), D.Decode_Capabilities (Data, Capabilities),
         D.Decode_Groups (Data, Groups), D.Decode_Groups (Data, Proc_Groups),
         Y.Decode (Data, Child.Child_Task), Y.Decode_Task (Data, Tasks),
         Y.Decode_Process (Data, Processes), Y.Decode_Namespace (Data, Namespaces))));
      end if;
   end Child_Expected;
   function Child_Decide
     (Raw : D.Raw_Packet;
      Data : Q.Byte_Array;
      History : N.Raw_History_Array;
      Proposed_History : N.Raw_History_Array;
      Rows : W.Raw_Row_Array;
      Proposed_Rows : W.Raw_Row_Array;
      Projection : N.Raw_Projection_Array;
      Proposed_Projection : N.Raw_Projection_Array;
      Buckets : N.Raw_Bucket_Array;
      Proposed_Buckets : N.Raw_Bucket_Array;
      Actual_Buckets : N.Raw_Bucket_Array;
      Observed : W.Raw_Native_Array;
      Facts : N.Raw_Facts_Array;
      Capabilities : D.Raw_Capability_Array;
      Groups : D.Raw_Group_Array;
      Proc_Groups : D.Raw_Group_Array;
      Authority : T.Raw_Input;
      Authority_Data : Q.Byte_Array;
      Authority_Grants : Raw_Grant_Array;
      Authority_Uses : Raw_Use_Array;
      Authority_Receipts : Raw_Chain_Array;
      Authority_Events : Raw_Chain_Array;
      Crosswalk : X.Raw_Crosswalk;
      Child : Y.Raw_Input;
      Tasks : Y.Raw_Task_Array;
      Processes : Y.Raw_Process_Array;
      Namespaces : Y.Raw_Namespace_Array) return Result is
      Grants : T.A.Grants (Authority_Grants'Range);
      Uses : T.A.Uses (Authority_Uses'Range);
      Receipts : T.A.C.Retained_Rows (Authority_Receipts'Range);
      Events : T.A.C.Retained_Rows (Authority_Events'Range);
   begin
      if not (N.Well_Formed (Data, Raw.Ledger, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts)
        and then T.Well_Formed (Authority)
        and then T.Recovery_Well_Formed (Authority_Data, Authority.Facts)
        and then (for all I in Authority_Grants'Range => T.Well_Formed (Authority_Grants (I)))
        and then (for all I in Authority_Uses'Range => T.Well_Formed (Authority_Uses (I)))
        and then (for all I in Authority_Receipts'Range => T.C.Well_Formed (Authority_Receipts (I)))
        and then (for all I in Authority_Events'Range => T.C.Well_Formed (Authority_Events (I)))
        and then Authority.Mode = T.A.Command'Pos (T.A.Authorize_Execution)
        and then X.Well_Formed (Data, Crosswalk)
        and then Y.Well_Formed (Data, Child)
        and then (if Child.Mode /= J.Admission_Mode'Pos (J.Root_Controller_Admission) then
          (for all I in Tasks'Range => Y.Well_Formed (Data, Tasks (I)))
          and then (for all I in Processes'Range => Y.Well_Formed (Data, Processes (I)))
          and then (for all I in Namespaces'Range => Y.Well_Formed (Data, Namespaces (I))))
        and then (if Child.Mode = J.Admission_Mode'Pos (J.Child_Admission) then
          D.Well_Formed (Data, Raw.Captured)
          and then (for all I in Capabilities'Range => D.Well_Formed (Data, Capabilities (I)))
          and then (for all I in Groups'Range => W.Well_Formed (Data, Groups (I)))
          and then (for all I in Proc_Groups'Range => W.Well_Formed (Data, Proc_Groups (I))))) then return Rejected; end if;
      for I in Grants'Range loop
         Grants (I) := T.Decode (Authority_Grants (I));
         pragma Loop_Invariant (for all K in Grants'First .. I => Grants (K) = T.Decode (Authority_Grants (K)));
      end loop;
      for I in Uses'Range loop
         Uses (I) := T.Decode (Authority_Uses (I));
         pragma Loop_Invariant (for all K in Uses'First .. I => Uses (K) = T.Decode (Authority_Uses (K)));
      end loop;
      for I in Receipts'Range loop
         Receipts (I) := T.C.Decode (Authority_Receipts (I));
         pragma Loop_Invariant (for all K in Receipts'First .. I => Receipts (K) = T.C.Decode (Authority_Receipts (K)));
      end loop;
      for I in Events'Range loop
         Events (I) := T.C.Decode (Authority_Events (I));
         pragma Loop_Invariant (for all K in Events'First .. I => Events (K) = T.C.Decode (Authority_Events (K)));
      end loop;
      if Child.Mode = J.Admission_Mode'Pos (J.Root_Controller_Admission) then
         return (True, J.Status'Pos (J.Root_Admission (Data, Authority_Data, N.Decode (Data, Raw.Ledger.Before_State), N.Decode_History (Data, History),
         W.Decode_Rows (Data, Rows), N.Decode_Projection (Data, Projection),
         N.Decode_Bucket (Data, Buckets), W.Decode_Native (Data, Observed),
         N.Decode_Facts (Data, Facts), N.Decode (Data, Raw.Ledger.Current),
         X.Decode (Data, Crosswalk), Grants, Uses, T.Decode (Authority.Bound),
         T.Decode (Authority.Now).Value, T.Decode (Authority_Data, Authority.Facts), Receipts, Events,
         Y.Decode (Data, Child.Controller))));
      elsif Child.Mode = J.Admission_Mode'Pos (J.Task_Reservation_Admission) then
         return (True, J.Status'Pos (J.Task_Admission (Data, Authority_Data, N.Decode (Data, Raw.Ledger.Before_State), N.Decode_History (Data, History),
         W.Decode_Rows (Data, Rows), N.Decode_Projection (Data, Projection),
         N.Decode_Bucket (Data, Buckets), W.Decode_Native (Data, Observed),
         N.Decode_Facts (Data, Facts), N.Decode (Data, Raw.Ledger.Current),
         X.Decode (Data, Crosswalk), Grants, Uses, T.Decode (Authority.Bound),
         T.Decode (Authority.Now).Value, T.Decode (Authority_Data, Authority.Facts), Receipts, Events,
         Y.Decode (Data, Child.Controller), N.Decode (Data, Raw.Ledger.Proposed_State),
         N.Decode_History (Data, Proposed_History), W.Decode_Rows (Data, Proposed_Rows),
         N.Decode_Projection (Data, Proposed_Projection), N.Decode_Bucket (Data, Proposed_Buckets),
         N.Decode_Bucket (Data, Actual_Buckets), N.Decode (Data, Raw.Ledger.Request),
         Y.Decode (Data, Child.Child_Task), Y.Decode_Task (Data, Tasks))));
      else
         return (True, J.Status'Pos (J.Decide (Data, Authority_Data, N.Decode (Data, Raw.Ledger.Before_State), N.Decode_History (Data, History),
         W.Decode_Rows (Data, Rows), N.Decode_Projection (Data, Projection),
         N.Decode_Bucket (Data, Buckets), W.Decode_Native (Data, Observed),
         N.Decode_Facts (Data, Facts), N.Decode (Data, Raw.Ledger.Current),
         X.Decode (Data, Crosswalk), Grants, Uses, T.Decode (Authority.Bound),
         T.Decode (Authority.Now).Value, T.Decode (Authority_Data, Authority.Facts), Receipts, Events,
         Y.Decode (Data, Child.Controller), D.Decode (Data, Raw.Captured), D.Decode_Capabilities (Data, Capabilities),
         D.Decode_Groups (Data, Groups), D.Decode_Groups (Data, Proc_Groups),
         Y.Decode (Data, Child.Child_Task), Y.Decode_Task (Data, Tasks),
         Y.Decode_Process (Data, Processes), Y.Decode_Namespace (Data, Namespaces))));
      end if;
   end Child_Decide;
end Worldline.Native_Execution_Views;

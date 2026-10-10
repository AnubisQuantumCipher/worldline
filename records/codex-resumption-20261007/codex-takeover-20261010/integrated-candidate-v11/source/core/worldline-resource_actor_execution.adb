with SPARK.Big_Integers;
package body Worldline.Resource_Actor_Execution with SPARK_Mode is
   function Reference (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      Actor : K.Observation; Capabilities : K.Capability_Array;
      Groups, Proc_Groups : K.Group_Array; W : Crosswalk;
      Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows) return Status
 is
   begin
      if K.Check (Resource_Data, State, History, Rows, Projection, Buckets,
         Observed, Facts, Current, Actor, Capabilities, Groups, Proc_Groups) /= K.Ready_Conjunct
      then return Actor_Refused; end if;
      if A.Decide (Authority_Data, Grants, Uses, Original, Now,
         A.Authorize_Execution, Evidence, Receipts, Events) /= A.Execution_Ready
      then return Authority_Refused; end if;
      if not Original_Holds (Resource_Data, Authority_Data, Original, Actor)
      then return Original_Binding_Mismatch; end if;
      if not Current_Holds (Resource_Data, Authority_Data, Evidence.Owner_Resolution, Current)
      then return Current_Binding_Mismatch; end if;
      if not Crosswalk_Valid (Resource_Data, W)
        or else not S.Current_Valid (Resource_Data, State, History, W.Resource_Current)
        or else not Same_Current (Resource_Data, Current, W.Resource_Current)
        or else not A.R.Same (W.Operation_Policy, Evidence.Owner_Resolution.Id (A.Policy))
        or else not A.R.Same (W.Operation_Root_Set, Evidence.Owner_Resolution.Id (A.Root_Set))
        or else not L.Same (Resource_Data, Actor.Executable_Plan, W.Selected_Plan)
        or else not L.Same (Resource_Data, Actor.Original_Requester, W.Original_Requester)
      then return Crosswalk_Mismatch; end if;
      if not Original.Peer.Present or else not K.Number (Resource_Data, Actor.Requester_Uid)
        or else L.Exact_Value (Resource_Data, Actor.Requester_Uid) /= UID_Values.To_Big_Integer (Original.Peer.Value)
      then return Requester_Mismatch; end if;
      -- Retained rows keep their original policy scope. A genuine live actor
      -- must still occupy this actual machine/boot; no context relabelling.
      if not (for some I in Rows'Range => L.Same_Binding (Resource_Data, Rows (I).Bound, Actor.Bound)
        and then L.Same (Resource_Data, Rows (I).Scope.Host, Current.Scope.Host)
        and then L.Same (Resource_Data, Rows (I).Scope.Boot, Current.Scope.Boot))
      then return Physical_Origin_Mismatch; end if;
      return Ready_Value_Conjunction;
   end Reference;
   function Decide (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      Actor : K.Observation; Capabilities : K.Capability_Array;
      Groups, Proc_Groups : K.Group_Array; W : Crosswalk;
      Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows) return Status
 is
   begin
      if K.Check (Resource_Data, State, History, Rows, Projection, Buckets,
         Observed, Facts, Current, Actor, Capabilities, Groups, Proc_Groups) /= K.Ready_Conjunct
      then return Actor_Refused; end if;
      if A.Decide (Authority_Data, Grants, Uses, Original, Now,
         A.Authorize_Execution, Evidence, Receipts, Events) /= A.Execution_Ready
      then return Authority_Refused; end if;
      if not Original_Holds (Resource_Data, Authority_Data, Original, Actor)
      then return Original_Binding_Mismatch; end if;
      if not Current_Holds (Resource_Data, Authority_Data, Evidence.Owner_Resolution, Current)
      then return Current_Binding_Mismatch; end if;
      if not Crosswalk_Valid (Resource_Data, W)
        or else not S.Current_Valid (Resource_Data, State, History, W.Resource_Current)
        or else not Same_Current (Resource_Data, Current, W.Resource_Current)
        or else not A.R.Same (W.Operation_Policy, Evidence.Owner_Resolution.Id (A.Policy))
        or else not A.R.Same (W.Operation_Root_Set, Evidence.Owner_Resolution.Id (A.Root_Set))
        or else not L.Same (Resource_Data, Actor.Executable_Plan, W.Selected_Plan)
        or else not L.Same (Resource_Data, Actor.Original_Requester, W.Original_Requester)
      then return Crosswalk_Mismatch; end if;
      if not Original.Peer.Present or else not K.Number (Resource_Data, Actor.Requester_Uid)
        or else L.Exact_Value (Resource_Data, Actor.Requester_Uid) /= UID_Values.To_Big_Integer (Original.Peer.Value)
      then return Requester_Mismatch; end if;
      -- Retained rows keep their original policy scope. A genuine live actor
      -- must still occupy this actual machine/boot; no context relabelling.
      if not (for some I in Rows'Range => L.Same_Binding (Resource_Data, Rows (I).Bound, Actor.Bound)
        and then L.Same (Resource_Data, Rows (I).Scope.Host, Current.Scope.Host)
        and then L.Same (Resource_Data, Rows (I).Scope.Boot, Current.Scope.Boot))
      then return Physical_Origin_Mismatch; end if;
      return Ready_Value_Conjunction;
   end Decide;
end Worldline.Resource_Actor_Execution;

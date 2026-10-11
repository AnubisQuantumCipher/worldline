package body Worldline.Resource_Child_Execution with SPARK_Mode is
   function Root_Admission_Reference (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      W : E.Crosswalk; Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows;
      Controller : Root_Controller) return Status is
   begin
      if not S.Valid (Resource_Data, State, History, Rows, Projection, Buckets, Current)
        or else not S.Native_Valid (Resource_Data, State, History, Rows, Observed, Facts)
      then return Ledger_Refused; end if;
      if A.Decide (Authority_Data, Grants, Uses, Original, Now, A.Authorize_Execution, Evidence, Receipts, Events) /= A.Execution_Ready
      then return Authority_Refused; end if;
      if not E.Current_Holds (Resource_Data, Authority_Data, Evidence.Owner_Resolution, Current)
        or else not E.Crosswalk_Valid (Resource_Data, W)
        or else not S.Current_Valid (Resource_Data, State, History, W.Resource_Current)
        or else not E.Same_Current (Resource_Data, Current, W.Resource_Current)
        or else not A.R.Same (W.Operation_Policy, Evidence.Owner_Resolution.Id (A.Policy))
        or else not A.R.Same (W.Operation_Root_Set, Evidence.Owner_Resolution.Id (A.Root_Set))
        or else not L.Same (Resource_Data, W.Original_Request, Controller.Id (R_raw_request))
        or else not L.Same (Resource_Data, W.Original_Requester, Controller.Id (R_requester))
        or else not L.Same (Resource_Data, W.Current_Source, Controller.Id (R_current_source))
        or else not L.Same (Resource_Data, Controller.Id (R_store_genesis), Current.Store_Genesis)
        or else not L.Same (Resource_Data, W.Selected_Plan, Controller.Id (R_handler_plan))
      then return Current_Refused; end if;
      if not Original_Root_Holds (Resource_Data, Authority_Data, Original, Controller)
        or else not Root_Controller_Holds (Resource_Data, State, History, Rows, Observed, Facts, Current, Controller)
        or else not Original.Peer.Present
        or else not Number_Valid (Resource_Data, Controller.Requester_Uid)
        or else L.Exact_Value (Resource_Data, Controller.Requester_Uid) /= E.UID_Values.To_Big_Integer (Original.Peer.Value)
        or else not L.Same (Resource_Data, Controller.Bound.Owner, Controller.Id (R_requester))
      then return Controller_Refused; end if;
      return Root_Ready_Conjunction;
   end Root_Admission_Reference;
   function Root_Admission (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      W : E.Crosswalk; Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows;
      Controller : Root_Controller) return Status is
   begin
      if not S.Valid (Resource_Data, State, History, Rows, Projection, Buckets, Current)
        or else not S.Native_Valid (Resource_Data, State, History, Rows, Observed, Facts)
      then return Ledger_Refused; end if;
      if A.Decide (Authority_Data, Grants, Uses, Original, Now, A.Authorize_Execution, Evidence, Receipts, Events) /= A.Execution_Ready
      then return Authority_Refused; end if;
      if not E.Current_Holds (Resource_Data, Authority_Data, Evidence.Owner_Resolution, Current)
        or else not E.Crosswalk_Valid (Resource_Data, W)
        or else not S.Current_Valid (Resource_Data, State, History, W.Resource_Current)
        or else not E.Same_Current (Resource_Data, Current, W.Resource_Current)
        or else not A.R.Same (W.Operation_Policy, Evidence.Owner_Resolution.Id (A.Policy))
        or else not A.R.Same (W.Operation_Root_Set, Evidence.Owner_Resolution.Id (A.Root_Set))
        or else not L.Same (Resource_Data, W.Original_Request, Controller.Id (R_raw_request))
        or else not L.Same (Resource_Data, W.Original_Requester, Controller.Id (R_requester))
        or else not L.Same (Resource_Data, W.Current_Source, Controller.Id (R_current_source))
        or else not L.Same (Resource_Data, Controller.Id (R_store_genesis), Current.Store_Genesis)
        or else not L.Same (Resource_Data, W.Selected_Plan, Controller.Id (R_handler_plan))
      then return Current_Refused; end if;
      if not Original_Root_Holds (Resource_Data, Authority_Data, Original, Controller)
        or else not Root_Controller_Holds (Resource_Data, State, History, Rows, Observed, Facts, Current, Controller)
        or else not Original.Peer.Present
        or else not Number_Valid (Resource_Data, Controller.Requester_Uid)
        or else L.Exact_Value (Resource_Data, Controller.Requester_Uid) /= E.UID_Values.To_Big_Integer (Original.Peer.Value)
        or else not L.Same (Resource_Data, Controller.Bound.Owner, Controller.Id (R_requester))
      then return Controller_Refused; end if;
      return Root_Ready_Conjunction;
   end Root_Admission;
   function Reference (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      W : E.Crosswalk; Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows;
      Controller : Root_Controller; Actor : K.Observation; Capabilities : K.Capability_Array;
      Groups, Proc_Groups : K.Group_Array; Child_Task : Task_Origin; Tasks : Task_Array;
      Processes : Process_Array; Namespaces : Namespace_Array) return Status is
   begin
      declare Root_Result : constant Status := Root_Admission (Resource_Data, Authority_Data, State, History, Rows, Projection, Buckets, Observed, Facts, Current, W, Grants, Uses, Original, Now, Evidence, Receipts, Events, Controller);
      begin if Root_Result /= Root_Ready_Conjunction then return Root_Result; end if; end;
      if K.Check (Resource_Data, State, History, Rows, Projection, Buckets, Observed, Facts, Current, Actor, Capabilities, Groups, Proc_Groups) /= K.Ready_Conjunct
      then return Actor_Refused; end if;
      if not Original.Peer.Present or else not Number_Valid (Resource_Data, Actor.Requester_Uid)
        or else L.Exact_Value (Resource_Data, Actor.Requester_Uid) /= E.UID_Values.To_Big_Integer (Original.Peer.Value)
        or else not Number_Same (Resource_Data, Actor.Requester_Gid, Controller.Requester_Gid)
        or else not Child_Holds (Resource_Data, Original, Controller, Actor, Child_Task, Tasks)
      then return Task_Refused; end if;
      if not Parent_Holds (Resource_Data, Rows, Controller, Child_Task) then return Parent_Refused; end if;
      if not Process_Ancestry (Resource_Data, Controller, Actor, Processes) then return Process_Ancestry_Refused; end if;
      if not Namespace_Ancestry (Resource_Data, Controller, Actor, Namespaces) then return Namespace_Ancestry_Refused; end if;
      return Child_Ready_Conjunction;
   end Reference;
   function Decide (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      W : E.Crosswalk; Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows;
      Controller : Root_Controller; Actor : K.Observation; Capabilities : K.Capability_Array;
      Groups, Proc_Groups : K.Group_Array; Child_Task : Task_Origin; Tasks : Task_Array;
      Processes : Process_Array; Namespaces : Namespace_Array) return Status is
   begin
      declare Root_Result : constant Status := Root_Admission (Resource_Data, Authority_Data, State, History, Rows, Projection, Buckets, Observed, Facts, Current, W, Grants, Uses, Original, Now, Evidence, Receipts, Events, Controller);
      begin if Root_Result /= Root_Ready_Conjunction then return Root_Result; end if; end;
      if K.Check (Resource_Data, State, History, Rows, Projection, Buckets, Observed, Facts, Current, Actor, Capabilities, Groups, Proc_Groups) /= K.Ready_Conjunct
      then return Actor_Refused; end if;
      if not Original.Peer.Present or else not Number_Valid (Resource_Data, Actor.Requester_Uid)
        or else L.Exact_Value (Resource_Data, Actor.Requester_Uid) /= E.UID_Values.To_Big_Integer (Original.Peer.Value)
        or else not Number_Same (Resource_Data, Actor.Requester_Gid, Controller.Requester_Gid)
        or else not Child_Holds (Resource_Data, Original, Controller, Actor, Child_Task, Tasks)
      then return Task_Refused; end if;
      if not Parent_Holds (Resource_Data, Rows, Controller, Child_Task) then return Parent_Refused; end if;
      if not Process_Ancestry (Resource_Data, Controller, Actor, Processes) then return Process_Ancestry_Refused; end if;
      if not Namespace_Ancestry (Resource_Data, Controller, Actor, Namespaces) then return Namespace_Ancestry_Refused; end if;
      return Child_Ready_Conjunction;
   end Decide;
   procedure Root_Refines_Original (Resource_Data, Authority_Data : Q.Byte_Array;
      Original : A.Binding; R : Root_Controller; Actor : K.Observation) is
   begin
      pragma Assert (if L.Same_Binding (Resource_Data, R.Bound, Actor.Bound) then
        Original_Root_Holds (Resource_Data, Authority_Data, Original, R) =
        E.Original_Holds (Resource_Data, Authority_Data, Original, Actor));
   end Root_Refines_Original;
   function Task_Admission_Reference (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      W : E.Crosswalk; Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows;
      Controller : Root_Controller; Proposed : S.State; Proposed_History : S.History_Array;
      Proposed_Rows : L.Row_Array; Proposed_Projection : S.Projection_Array;
      Proposed_Buckets, Actual_Buckets : S.Bucket_Array; Request : S.Intent;
      Child_Task : Task_Origin; Tasks : Task_Array) return Status is
   begin
      declare Root_Result : constant Status := Root_Admission (Resource_Data, Authority_Data, State, History, Rows, Projection, Buckets, Observed, Facts, Current, W, Grants, Uses, Original, Now, Evidence, Receipts, Events, Controller);
      begin if Root_Result /= Root_Ready_Conjunction then return Root_Result; end if; end;
      if Request.Kind /= S.Ordinary or else Request.Original.Kind /= L.Reserve
        or else not Task_Request_Holds (Resource_Data, Original, Controller, Child_Task, Tasks, Request)
      then return Task_Refused; end if;
      if S.Check (Resource_Data, State, History, Rows, Projection, Buckets,
        Proposed, Proposed_History, Proposed_Rows, Proposed_Projection, Proposed_Buckets,
        Observed, Facts, Actual_Buckets, Current, Request) /= S.Ready
      then return Task_Transition_Refused; end if;
      return Task_Ready_Conjunction;
   end Task_Admission_Reference;
   function Task_Admission (Resource_Data, Authority_Data : Q.Byte_Array;
      State : S.State; History : S.History_Array; Rows : L.Row_Array;
      Projection : S.Projection_Array; Buckets : S.Bucket_Array;
      Observed : L.Native_Array; Facts : S.Facts_Array; Current : S.Current_Observation;
      W : E.Crosswalk; Grants : A.Grants; Uses : A.Uses; Original : A.Binding;
      Now : Q.Quantity; Evidence : A.Evidence; Receipts, Events : A.C.Retained_Rows;
      Controller : Root_Controller; Proposed : S.State; Proposed_History : S.History_Array;
      Proposed_Rows : L.Row_Array; Proposed_Projection : S.Projection_Array;
      Proposed_Buckets, Actual_Buckets : S.Bucket_Array; Request : S.Intent;
      Child_Task : Task_Origin; Tasks : Task_Array) return Status is
   begin
      declare Root_Result : constant Status := Root_Admission (Resource_Data, Authority_Data, State, History, Rows, Projection, Buckets, Observed, Facts, Current, W, Grants, Uses, Original, Now, Evidence, Receipts, Events, Controller);
      begin if Root_Result /= Root_Ready_Conjunction then return Root_Result; end if; end;
      if Request.Kind /= S.Ordinary or else Request.Original.Kind /= L.Reserve
        or else not Task_Request_Holds (Resource_Data, Original, Controller, Child_Task, Tasks, Request)
      then return Task_Refused; end if;
      if S.Check (Resource_Data, State, History, Rows, Projection, Buckets,
        Proposed, Proposed_History, Proposed_Rows, Proposed_Projection, Proposed_Buckets,
        Observed, Facts, Actual_Buckets, Current, Request) /= S.Ready
      then return Task_Transition_Refused; end if;
      return Task_Ready_Conjunction;
   end Task_Admission;
end Worldline.Resource_Child_Execution;

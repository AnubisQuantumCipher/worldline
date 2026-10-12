with Worldline.Native_Execution_Views;
package Worldline.Native_Execution_Capture with SPARK_Mode is
   package V renames Worldline.Native_Execution_Views;
   package N renames V.N;
   package W renames V.W;
   package O renames V.O;
   package Q renames V.Q;
   package D renames V.D;
   package X renames V.X;
   package Y renames V.Y;
   package T renames V.T;
   subtype Raw_Grant_Array is V.Raw_Grant_Array;
   subtype Raw_Use_Array is V.Raw_Use_Array;
   subtype Raw_Chain_Array is V.Raw_Chain_Array;
   subtype Result is V.Result;
   use type V.Result;
   --  Every observer denotes the authentic caller's complete live immutable
   --  allocation for this call. Only the sole Off CAPI may construct views.
   --  No observer escapes. All records, arenas and rosters are captured once
   --  before the original typed decision; no output aliases an observer here.
   function Scoped_Check
     (Raw_View : not null access constant N.Raw_Packet;
      Data_View : not null access constant Q.Byte_Array;
      History_View : not null access constant N.Raw_History_Array;
      Proposed_History_View : not null access constant N.Raw_History_Array;
      Rows_View : not null access constant W.Raw_Row_Array;
      Proposed_Rows_View : not null access constant W.Raw_Row_Array;
      Projection_View : not null access constant N.Raw_Projection_Array;
      Proposed_Projection_View : not null access constant N.Raw_Projection_Array;
      Buckets_View : not null access constant N.Raw_Bucket_Array;
      Proposed_Buckets_View : not null access constant N.Raw_Bucket_Array;
      Actual_Buckets_View : not null access constant N.Raw_Bucket_Array;
      Observed_View : not null access constant W.Raw_Native_Array;
      Facts_View : not null access constant N.Raw_Facts_Array) return Result
     with Global => null,
       Post => Scoped_Check'Result = V.Scoped_Check (Raw_View.all, Data_View.all, History_View.all, Proposed_History_View.all, Rows_View.all, Proposed_Rows_View.all, Projection_View.all, Proposed_Projection_View.all, Buckets_View.all, Proposed_Buckets_View.all, Actual_Buckets_View.all, Observed_View.all, Facts_View.all);
   function Scoped_Validate
     (Raw_View : not null access constant N.Raw_Packet;
      Data_View : not null access constant Q.Byte_Array;
      History_View : not null access constant N.Raw_History_Array;
      Proposed_History_View : not null access constant N.Raw_History_Array;
      Rows_View : not null access constant W.Raw_Row_Array;
      Proposed_Rows_View : not null access constant W.Raw_Row_Array;
      Projection_View : not null access constant N.Raw_Projection_Array;
      Proposed_Projection_View : not null access constant N.Raw_Projection_Array;
      Buckets_View : not null access constant N.Raw_Bucket_Array;
      Proposed_Buckets_View : not null access constant N.Raw_Bucket_Array;
      Actual_Buckets_View : not null access constant N.Raw_Bucket_Array;
      Observed_View : not null access constant W.Raw_Native_Array;
      Facts_View : not null access constant N.Raw_Facts_Array) return Result
     with Global => null,
       Post => Scoped_Validate'Result = V.Scoped_Validate (Raw_View.all, Data_View.all, History_View.all, Proposed_History_View.all, Rows_View.all, Proposed_Rows_View.all, Projection_View.all, Proposed_Projection_View.all, Buckets_View.all, Proposed_Buckets_View.all, Actual_Buckets_View.all, Observed_View.all, Facts_View.all);
   function Scoped_Classify
     (Raw_View : not null access constant N.Raw_Packet;
      Data_View : not null access constant Q.Byte_Array;
      History_View : not null access constant N.Raw_History_Array;
      Proposed_History_View : not null access constant N.Raw_History_Array;
      Rows_View : not null access constant W.Raw_Row_Array;
      Proposed_Rows_View : not null access constant W.Raw_Row_Array;
      Projection_View : not null access constant N.Raw_Projection_Array;
      Proposed_Projection_View : not null access constant N.Raw_Projection_Array;
      Buckets_View : not null access constant N.Raw_Bucket_Array;
      Proposed_Buckets_View : not null access constant N.Raw_Bucket_Array;
      Actual_Buckets_View : not null access constant N.Raw_Bucket_Array;
      Observed_View : not null access constant W.Raw_Native_Array;
      Facts_View : not null access constant N.Raw_Facts_Array) return Result
     with Global => null,
       Post => Scoped_Classify'Result = V.Scoped_Classify (Raw_View.all, Data_View.all, History_View.all, Proposed_History_View.all, Rows_View.all, Proposed_Rows_View.all, Projection_View.all, Proposed_Projection_View.all, Buckets_View.all, Proposed_Buckets_View.all, Actual_Buckets_View.all, Observed_View.all, Facts_View.all);
   function Observation_Classify
     (Raw_View : not null access constant O.Raw_Input;
      Data_View : not null access constant Q.Byte_Array) return Result
     with Global => null,
       Post => Observation_Classify'Result = V.Observation_Classify (Raw_View.all, Data_View.all);
   function Observation_Current
     (Raw_View : not null access constant O.Raw_Input;
      Data_View : not null access constant Q.Byte_Array) return Result
     with Global => null,
       Post => Observation_Current'Result = V.Observation_Current (Raw_View.all, Data_View.all);
   function Observation_Genesis_Current
     (Raw_View : not null access constant O.Raw_Input;
      Data_View : not null access constant Q.Byte_Array) return Result
     with Global => null,
       Post => Observation_Genesis_Current'Result = V.Observation_Genesis_Current (Raw_View.all, Data_View.all);
   function Actor_Check
     (Raw_View : not null access constant D.Raw_Packet;
      Data_View : not null access constant Q.Byte_Array;
      History_View : not null access constant N.Raw_History_Array;
      Proposed_History_View : not null access constant N.Raw_History_Array;
      Rows_View : not null access constant W.Raw_Row_Array;
      Proposed_Rows_View : not null access constant W.Raw_Row_Array;
      Projection_View : not null access constant N.Raw_Projection_Array;
      Proposed_Projection_View : not null access constant N.Raw_Projection_Array;
      Buckets_View : not null access constant N.Raw_Bucket_Array;
      Proposed_Buckets_View : not null access constant N.Raw_Bucket_Array;
      Actual_Buckets_View : not null access constant N.Raw_Bucket_Array;
      Observed_View : not null access constant W.Raw_Native_Array;
      Facts_View : not null access constant N.Raw_Facts_Array;
      Capabilities_View : not null access constant D.Raw_Capability_Array;
      Groups_View : not null access constant D.Raw_Group_Array;
      Proc_Groups_View : not null access constant D.Raw_Group_Array) return Result
     with Global => null,
       Post => Actor_Check'Result = V.Actor_Check (Raw_View.all, Data_View.all, History_View.all, Proposed_History_View.all, Rows_View.all, Proposed_Rows_View.all, Projection_View.all, Proposed_Projection_View.all, Buckets_View.all, Proposed_Buckets_View.all, Actual_Buckets_View.all, Observed_View.all, Facts_View.all, Capabilities_View.all, Groups_View.all, Proc_Groups_View.all);
   function Operation_Decide
     (Authority_View : not null access constant T.Raw_Input;
      Authority_Data_View : not null access constant Q.Byte_Array;
      Authority_Grants_View : not null access constant Raw_Grant_Array;
      Authority_Uses_View : not null access constant Raw_Use_Array;
      Authority_Receipts_View : not null access constant Raw_Chain_Array;
      Authority_Events_View : not null access constant Raw_Chain_Array) return Result
     with Global => null,
       Post => Operation_Decide'Result = V.Operation_Decide (Authority_View.all, Authority_Data_View.all, Authority_Grants_View.all, Authority_Uses_View.all, Authority_Receipts_View.all, Authority_Events_View.all);
   function Execution_Decide
     (Raw_View : not null access constant D.Raw_Packet;
      Data_View : not null access constant Q.Byte_Array;
      History_View : not null access constant N.Raw_History_Array;
      Proposed_History_View : not null access constant N.Raw_History_Array;
      Rows_View : not null access constant W.Raw_Row_Array;
      Proposed_Rows_View : not null access constant W.Raw_Row_Array;
      Projection_View : not null access constant N.Raw_Projection_Array;
      Proposed_Projection_View : not null access constant N.Raw_Projection_Array;
      Buckets_View : not null access constant N.Raw_Bucket_Array;
      Proposed_Buckets_View : not null access constant N.Raw_Bucket_Array;
      Actual_Buckets_View : not null access constant N.Raw_Bucket_Array;
      Observed_View : not null access constant W.Raw_Native_Array;
      Facts_View : not null access constant N.Raw_Facts_Array;
      Capabilities_View : not null access constant D.Raw_Capability_Array;
      Groups_View : not null access constant D.Raw_Group_Array;
      Proc_Groups_View : not null access constant D.Raw_Group_Array;
      Authority_View : not null access constant T.Raw_Input;
      Authority_Data_View : not null access constant Q.Byte_Array;
      Authority_Grants_View : not null access constant Raw_Grant_Array;
      Authority_Uses_View : not null access constant Raw_Use_Array;
      Authority_Receipts_View : not null access constant Raw_Chain_Array;
      Authority_Events_View : not null access constant Raw_Chain_Array;
      Crosswalk_View : not null access constant X.Raw_Crosswalk) return Result
     with Global => null,
       Post => Execution_Decide'Result = V.Execution_Decide (Raw_View.all, Data_View.all, History_View.all, Proposed_History_View.all, Rows_View.all, Proposed_Rows_View.all, Projection_View.all, Proposed_Projection_View.all, Buckets_View.all, Proposed_Buckets_View.all, Actual_Buckets_View.all, Observed_View.all, Facts_View.all, Capabilities_View.all, Groups_View.all, Proc_Groups_View.all, Authority_View.all, Authority_Data_View.all, Authority_Grants_View.all, Authority_Uses_View.all, Authority_Receipts_View.all, Authority_Events_View.all, Crosswalk_View.all);
   function Child_Decide
     (Raw_View : not null access constant D.Raw_Packet;
      Data_View : not null access constant Q.Byte_Array;
      History_View : not null access constant N.Raw_History_Array;
      Proposed_History_View : not null access constant N.Raw_History_Array;
      Rows_View : not null access constant W.Raw_Row_Array;
      Proposed_Rows_View : not null access constant W.Raw_Row_Array;
      Projection_View : not null access constant N.Raw_Projection_Array;
      Proposed_Projection_View : not null access constant N.Raw_Projection_Array;
      Buckets_View : not null access constant N.Raw_Bucket_Array;
      Proposed_Buckets_View : not null access constant N.Raw_Bucket_Array;
      Actual_Buckets_View : not null access constant N.Raw_Bucket_Array;
      Observed_View : not null access constant W.Raw_Native_Array;
      Facts_View : not null access constant N.Raw_Facts_Array;
      Capabilities_View : not null access constant D.Raw_Capability_Array;
      Groups_View : not null access constant D.Raw_Group_Array;
      Proc_Groups_View : not null access constant D.Raw_Group_Array;
      Authority_View : not null access constant T.Raw_Input;
      Authority_Data_View : not null access constant Q.Byte_Array;
      Authority_Grants_View : not null access constant Raw_Grant_Array;
      Authority_Uses_View : not null access constant Raw_Use_Array;
      Authority_Receipts_View : not null access constant Raw_Chain_Array;
      Authority_Events_View : not null access constant Raw_Chain_Array;
      Crosswalk_View : not null access constant X.Raw_Crosswalk;
      Child_View : not null access constant Y.Raw_Input;
      Tasks_View : not null access constant Y.Raw_Task_Array;
      Processes_View : not null access constant Y.Raw_Process_Array;
      Namespaces_View : not null access constant Y.Raw_Namespace_Array) return Result
     with Global => null,
       Post => Child_Decide'Result = V.Child_Decide (Raw_View.all, Data_View.all, History_View.all, Proposed_History_View.all, Rows_View.all, Proposed_Rows_View.all, Projection_View.all, Proposed_Projection_View.all, Buckets_View.all, Proposed_Buckets_View.all, Actual_Buckets_View.all, Observed_View.all, Facts_View.all, Capabilities_View.all, Groups_View.all, Proc_Groups_View.all, Authority_View.all, Authority_Data_View.all, Authority_Grants_View.all, Authority_Uses_View.all, Authority_Receipts_View.all, Authority_Events_View.all, Crosswalk_View.all, Child_View.all, Tasks_View.all, Processes_View.all, Namespaces_View.all);
end Worldline.Native_Execution_Capture;

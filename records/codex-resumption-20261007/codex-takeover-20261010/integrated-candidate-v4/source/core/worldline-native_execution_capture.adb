package body Worldline.Native_Execution_Capture with SPARK_Mode is
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
      Facts_View : not null access constant N.Raw_Facts_Array) return Result is
      Raw : constant N.Raw_Packet := Raw_View.all;
      Data : constant Q.Byte_Array := Data_View.all;
      History : constant N.Raw_History_Array := History_View.all;
      Proposed_History : constant N.Raw_History_Array := Proposed_History_View.all;
      Rows : constant W.Raw_Row_Array := Rows_View.all;
      Proposed_Rows : constant W.Raw_Row_Array := Proposed_Rows_View.all;
      Projection : constant N.Raw_Projection_Array := Projection_View.all;
      Proposed_Projection : constant N.Raw_Projection_Array := Proposed_Projection_View.all;
      Buckets : constant N.Raw_Bucket_Array := Buckets_View.all;
      Proposed_Buckets : constant N.Raw_Bucket_Array := Proposed_Buckets_View.all;
      Actual_Buckets : constant N.Raw_Bucket_Array := Actual_Buckets_View.all;
      Observed : constant W.Raw_Native_Array := Observed_View.all;
      Facts : constant N.Raw_Facts_Array := Facts_View.all;
   begin
      return V.Scoped_Check (Raw, Data, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts);
   end Scoped_Check;
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
      Facts_View : not null access constant N.Raw_Facts_Array) return Result is
      Raw : constant N.Raw_Packet := Raw_View.all;
      Data : constant Q.Byte_Array := Data_View.all;
      History : constant N.Raw_History_Array := History_View.all;
      Proposed_History : constant N.Raw_History_Array := Proposed_History_View.all;
      Rows : constant W.Raw_Row_Array := Rows_View.all;
      Proposed_Rows : constant W.Raw_Row_Array := Proposed_Rows_View.all;
      Projection : constant N.Raw_Projection_Array := Projection_View.all;
      Proposed_Projection : constant N.Raw_Projection_Array := Proposed_Projection_View.all;
      Buckets : constant N.Raw_Bucket_Array := Buckets_View.all;
      Proposed_Buckets : constant N.Raw_Bucket_Array := Proposed_Buckets_View.all;
      Actual_Buckets : constant N.Raw_Bucket_Array := Actual_Buckets_View.all;
      Observed : constant W.Raw_Native_Array := Observed_View.all;
      Facts : constant N.Raw_Facts_Array := Facts_View.all;
   begin
      return V.Scoped_Validate (Raw, Data, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts);
   end Scoped_Validate;
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
      Facts_View : not null access constant N.Raw_Facts_Array) return Result is
      Raw : constant N.Raw_Packet := Raw_View.all;
      Data : constant Q.Byte_Array := Data_View.all;
      History : constant N.Raw_History_Array := History_View.all;
      Proposed_History : constant N.Raw_History_Array := Proposed_History_View.all;
      Rows : constant W.Raw_Row_Array := Rows_View.all;
      Proposed_Rows : constant W.Raw_Row_Array := Proposed_Rows_View.all;
      Projection : constant N.Raw_Projection_Array := Projection_View.all;
      Proposed_Projection : constant N.Raw_Projection_Array := Proposed_Projection_View.all;
      Buckets : constant N.Raw_Bucket_Array := Buckets_View.all;
      Proposed_Buckets : constant N.Raw_Bucket_Array := Proposed_Buckets_View.all;
      Actual_Buckets : constant N.Raw_Bucket_Array := Actual_Buckets_View.all;
      Observed : constant W.Raw_Native_Array := Observed_View.all;
      Facts : constant N.Raw_Facts_Array := Facts_View.all;
   begin
      return V.Scoped_Classify (Raw, Data, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts);
   end Scoped_Classify;
   function Observation_Classify
     (Raw_View : not null access constant O.Raw_Input;
      Data_View : not null access constant Q.Byte_Array) return Result is
      Raw : constant O.Raw_Input := Raw_View.all;
      Data : constant Q.Byte_Array := Data_View.all;
   begin
      return V.Observation_Classify (Raw, Data);
   end Observation_Classify;
   function Observation_Current
     (Raw_View : not null access constant O.Raw_Input;
      Data_View : not null access constant Q.Byte_Array) return Result is
      Raw : constant O.Raw_Input := Raw_View.all;
      Data : constant Q.Byte_Array := Data_View.all;
   begin
      return V.Observation_Current (Raw, Data);
   end Observation_Current;
   function Observation_Genesis_Current
     (Raw_View : not null access constant O.Raw_Input;
      Data_View : not null access constant Q.Byte_Array) return Result is
      Raw : constant O.Raw_Input := Raw_View.all;
      Data : constant Q.Byte_Array := Data_View.all;
   begin
      return V.Observation_Genesis_Current (Raw, Data);
   end Observation_Genesis_Current;
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
      Proc_Groups_View : not null access constant D.Raw_Group_Array) return Result is
      Raw : constant D.Raw_Packet := Raw_View.all;
      Data : constant Q.Byte_Array := Data_View.all;
      History : constant N.Raw_History_Array := History_View.all;
      Proposed_History : constant N.Raw_History_Array := Proposed_History_View.all;
      Rows : constant W.Raw_Row_Array := Rows_View.all;
      Proposed_Rows : constant W.Raw_Row_Array := Proposed_Rows_View.all;
      Projection : constant N.Raw_Projection_Array := Projection_View.all;
      Proposed_Projection : constant N.Raw_Projection_Array := Proposed_Projection_View.all;
      Buckets : constant N.Raw_Bucket_Array := Buckets_View.all;
      Proposed_Buckets : constant N.Raw_Bucket_Array := Proposed_Buckets_View.all;
      Actual_Buckets : constant N.Raw_Bucket_Array := Actual_Buckets_View.all;
      Observed : constant W.Raw_Native_Array := Observed_View.all;
      Facts : constant N.Raw_Facts_Array := Facts_View.all;
      Capabilities : constant D.Raw_Capability_Array := Capabilities_View.all;
      Groups : constant D.Raw_Group_Array := Groups_View.all;
      Proc_Groups : constant D.Raw_Group_Array := Proc_Groups_View.all;
   begin
      return V.Actor_Check (Raw, Data, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts, Capabilities, Groups, Proc_Groups);
   end Actor_Check;
   function Operation_Decide
     (Authority_View : not null access constant T.Raw_Input;
      Authority_Data_View : not null access constant Q.Byte_Array;
      Authority_Grants_View : not null access constant Raw_Grant_Array;
      Authority_Uses_View : not null access constant Raw_Use_Array;
      Authority_Receipts_View : not null access constant Raw_Chain_Array;
      Authority_Events_View : not null access constant Raw_Chain_Array) return Result is
      Authority : constant T.Raw_Input := Authority_View.all;
      Authority_Data : constant Q.Byte_Array := Authority_Data_View.all;
      Authority_Grants : constant Raw_Grant_Array := Authority_Grants_View.all;
      Authority_Uses : constant Raw_Use_Array := Authority_Uses_View.all;
      Authority_Receipts : constant Raw_Chain_Array := Authority_Receipts_View.all;
      Authority_Events : constant Raw_Chain_Array := Authority_Events_View.all;
   begin
      return V.Operation_Decide (Authority, Authority_Data, Authority_Grants, Authority_Uses, Authority_Receipts, Authority_Events);
   end Operation_Decide;
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
      Crosswalk_View : not null access constant X.Raw_Crosswalk) return Result is
      Raw : constant D.Raw_Packet := Raw_View.all;
      Data : constant Q.Byte_Array := Data_View.all;
      History : constant N.Raw_History_Array := History_View.all;
      Proposed_History : constant N.Raw_History_Array := Proposed_History_View.all;
      Rows : constant W.Raw_Row_Array := Rows_View.all;
      Proposed_Rows : constant W.Raw_Row_Array := Proposed_Rows_View.all;
      Projection : constant N.Raw_Projection_Array := Projection_View.all;
      Proposed_Projection : constant N.Raw_Projection_Array := Proposed_Projection_View.all;
      Buckets : constant N.Raw_Bucket_Array := Buckets_View.all;
      Proposed_Buckets : constant N.Raw_Bucket_Array := Proposed_Buckets_View.all;
      Actual_Buckets : constant N.Raw_Bucket_Array := Actual_Buckets_View.all;
      Observed : constant W.Raw_Native_Array := Observed_View.all;
      Facts : constant N.Raw_Facts_Array := Facts_View.all;
      Capabilities : constant D.Raw_Capability_Array := Capabilities_View.all;
      Groups : constant D.Raw_Group_Array := Groups_View.all;
      Proc_Groups : constant D.Raw_Group_Array := Proc_Groups_View.all;
      Authority : constant T.Raw_Input := Authority_View.all;
      Authority_Data : constant Q.Byte_Array := Authority_Data_View.all;
      Authority_Grants : constant Raw_Grant_Array := Authority_Grants_View.all;
      Authority_Uses : constant Raw_Use_Array := Authority_Uses_View.all;
      Authority_Receipts : constant Raw_Chain_Array := Authority_Receipts_View.all;
      Authority_Events : constant Raw_Chain_Array := Authority_Events_View.all;
      Crosswalk : constant X.Raw_Crosswalk := Crosswalk_View.all;
   begin
      return V.Execution_Decide (Raw, Data, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts, Capabilities, Groups, Proc_Groups, Authority, Authority_Data, Authority_Grants, Authority_Uses, Authority_Receipts, Authority_Events, Crosswalk);
   end Execution_Decide;
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
      Namespaces_View : not null access constant Y.Raw_Namespace_Array) return Result is
      Raw : constant D.Raw_Packet := Raw_View.all;
      Data : constant Q.Byte_Array := Data_View.all;
      History : constant N.Raw_History_Array := History_View.all;
      Proposed_History : constant N.Raw_History_Array := Proposed_History_View.all;
      Rows : constant W.Raw_Row_Array := Rows_View.all;
      Proposed_Rows : constant W.Raw_Row_Array := Proposed_Rows_View.all;
      Projection : constant N.Raw_Projection_Array := Projection_View.all;
      Proposed_Projection : constant N.Raw_Projection_Array := Proposed_Projection_View.all;
      Buckets : constant N.Raw_Bucket_Array := Buckets_View.all;
      Proposed_Buckets : constant N.Raw_Bucket_Array := Proposed_Buckets_View.all;
      Actual_Buckets : constant N.Raw_Bucket_Array := Actual_Buckets_View.all;
      Observed : constant W.Raw_Native_Array := Observed_View.all;
      Facts : constant N.Raw_Facts_Array := Facts_View.all;
      Capabilities : constant D.Raw_Capability_Array := Capabilities_View.all;
      Groups : constant D.Raw_Group_Array := Groups_View.all;
      Proc_Groups : constant D.Raw_Group_Array := Proc_Groups_View.all;
      Authority : constant T.Raw_Input := Authority_View.all;
      Authority_Data : constant Q.Byte_Array := Authority_Data_View.all;
      Authority_Grants : constant Raw_Grant_Array := Authority_Grants_View.all;
      Authority_Uses : constant Raw_Use_Array := Authority_Uses_View.all;
      Authority_Receipts : constant Raw_Chain_Array := Authority_Receipts_View.all;
      Authority_Events : constant Raw_Chain_Array := Authority_Events_View.all;
      Crosswalk : constant X.Raw_Crosswalk := Crosswalk_View.all;
      Child : constant Y.Raw_Input := Child_View.all;
      Tasks : constant Y.Raw_Task_Array := Tasks_View.all;
      Processes : constant Y.Raw_Process_Array := Processes_View.all;
      Namespaces : constant Y.Raw_Namespace_Array := Namespaces_View.all;
   begin
      return V.Child_Decide (Raw, Data, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts, Capabilities, Groups, Proc_Groups, Authority, Authority_Data, Authority_Grants, Authority_Uses, Authority_Receipts, Authority_Events, Crosswalk, Child, Tasks, Processes, Namespaces);
   end Child_Decide;
end Worldline.Native_Execution_Capture;

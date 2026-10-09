with Interfaces;
with Resource_Scoped_Run_Ledger_Wire;
with Resource_Actor_Admission_Wire;
with Worldline.Resource_Actor_Execution_Wire;
with Worldline.Resource_Child_Execution_Wire;
with Worldline.Operation_Authority_Wire;
package Worldline.Native_Execution_Views with SPARK_Mode is
   package N renames Resource_Scoped_Run_Ledger_Wire;
   package W renames N.W;
   package O renames N.O;
   package Q renames N.Q;
   package D renames Resource_Actor_Admission_Wire;
   package X renames Worldline.Resource_Actor_Execution_Wire;
   package Y renames Worldline.Resource_Child_Execution_Wire;
   package T renames Worldline.Operation_Authority_Wire;
   type Raw_Grant_Array is array (Q.Byte_Index range <>) of T.Raw_Grant;
   type Raw_Use_Array is array (Q.Byte_Index range <>) of T.Raw_Use;
   type Raw_Chain_Array is array (Q.Byte_Index range <>) of T.C.Raw_Row;
   type Result is record
      Well_Formed : Boolean;
      Status : Interfaces.Unsigned_32;
   end record;
   Rejected : constant Result := (False, 0);
   --  These value entries redecide complete original operands. They neither
   --  consume archived statuses nor grant root custody or external effects.
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
      Facts : N.Raw_Facts_Array) return Result
     with Global => null,
       Post => Scoped_Check'Result =
         (if N.Well_Formed (Data, Raw, History, Proposed_History, Rows, Proposed_Rows,
           Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts)
          then (True, N.Decide (Data, Raw, History, Proposed_History, Rows, Proposed_Rows,
            Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts).Status)
          else Rejected);
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
      Facts : N.Raw_Facts_Array) return Result
     with Global => null,
       Post => Scoped_Validate'Result =
         (if N.Well_Formed (Data, Raw, History, Proposed_History, Rows, Proposed_Rows,
           Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts)
          then (True, N.Validate (Data, Raw, History, Proposed_History, Rows, Proposed_Rows,
            Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts).Status)
          else Rejected);
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
      Facts : N.Raw_Facts_Array) return Result
     with Global => null,
       Post => Scoped_Classify'Result =
         (if N.Well_Formed (Data, Raw, History, Proposed_History, Rows, Proposed_Rows,
           Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts)
          then (True, N.Classify_Selected (Data, Raw, History, Proposed_History, Rows, Proposed_Rows,
            Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts).Status)
          else Rejected);
   function Observation_Classify
     (Raw : O.Raw_Input;
      Data : Q.Byte_Array) return Result
     with Global => null,
       Post => Observation_Classify'Result = (True, O.L.Liveness'Pos (O.Classify (Data, Raw)));
   function Observation_Current
     (Raw : O.Raw_Input;
      Data : Q.Byte_Array) return Result
     with Global => null,
       Post => Observation_Current'Result = (True, Boolean'Pos (O.Current (Data, Raw)));
   function Observation_Genesis_Current
     (Raw : O.Raw_Input;
      Data : Q.Byte_Array) return Result
     with Global => null,
       Post => Observation_Genesis_Current'Result = (True, Boolean'Pos (O.Genesis_Current (Data, Raw)));
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
      Proc_Groups : D.Raw_Group_Array) return Result
     with Ghost, Global => null;
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
      Proc_Groups : D.Raw_Group_Array) return Result
     with Global => null,
       Post => Actor_Check'Result = Actor_Expected (Raw, Data, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts, Capabilities, Groups, Proc_Groups);
   function Operation_Expected
     (Authority : T.Raw_Input;
      Authority_Data : Q.Byte_Array;
      Authority_Grants : Raw_Grant_Array;
      Authority_Uses : Raw_Use_Array;
      Authority_Receipts : Raw_Chain_Array;
      Authority_Events : Raw_Chain_Array) return Result
     with Ghost, Global => null;
   function Operation_Decide
     (Authority : T.Raw_Input;
      Authority_Data : Q.Byte_Array;
      Authority_Grants : Raw_Grant_Array;
      Authority_Uses : Raw_Use_Array;
      Authority_Receipts : Raw_Chain_Array;
      Authority_Events : Raw_Chain_Array) return Result
     with Global => null,
       Post => Operation_Decide'Result = Operation_Expected (Authority, Authority_Data, Authority_Grants, Authority_Uses, Authority_Receipts, Authority_Events);
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
      Crosswalk : X.Raw_Crosswalk) return Result
     with Ghost, Global => null;
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
      Crosswalk : X.Raw_Crosswalk) return Result
     with Global => null,
       Post => Execution_Decide'Result = Execution_Expected (Raw, Data, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts, Capabilities, Groups, Proc_Groups, Authority, Authority_Data, Authority_Grants, Authority_Uses, Authority_Receipts, Authority_Events, Crosswalk);
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
      Namespaces : Y.Raw_Namespace_Array) return Result
     with Ghost, Global => null;
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
      Namespaces : Y.Raw_Namespace_Array) return Result
     with Global => null,
       Post => Child_Decide'Result = Child_Expected (Raw, Data, History, Proposed_History, Rows, Proposed_Rows, Projection, Proposed_Projection, Buckets, Proposed_Buckets, Actual_Buckets, Observed, Facts, Capabilities, Groups, Proc_Groups, Authority, Authority_Data, Authority_Grants, Authority_Uses, Authority_Receipts, Authority_Events, Crosswalk, Child, Tasks, Processes, Namespaces);
end Worldline.Native_Execution_Views;

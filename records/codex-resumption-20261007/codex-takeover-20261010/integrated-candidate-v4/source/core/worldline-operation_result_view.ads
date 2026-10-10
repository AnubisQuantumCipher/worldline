with Worldline.Native_Execution_Views;
package Worldline.Operation_Result_View with SPARK_Mode is
   package V renames Worldline.Native_Execution_Views;
   use type V.Result;
   function Expected (Raw : V.T.Raw_Input; Data : V.Q.Byte_Array;
     Grants : V.Raw_Grant_Array; Uses : V.Raw_Use_Array;
     Receipts, Events : V.Raw_Chain_Array) return V.Result
     with Ghost, Global => null;
   function Check (Raw : V.T.Raw_Input; Data : V.Q.Byte_Array;
     Grants : V.Raw_Grant_Array; Uses : V.Raw_Use_Array;
     Receipts, Events : V.Raw_Chain_Array) return V.Result
     with Global => null,
       Post => Check'Result = Expected (Raw, Data, Grants, Uses, Receipts, Events);
end Worldline.Operation_Result_View;

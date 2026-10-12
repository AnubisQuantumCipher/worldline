package body Worldline.Resource_Child_Execution_Wire with SPARK_Mode is
   function Decode_Process (Data : Q.Byte_Array; V : Raw_Process_Array) return J.Process_Array is
      Result : J.Process_Array (V'Range) with Relaxed_Initialization;
   begin
      for I in V'Range loop
         Result (I) := Decode (Data, V (I));
         pragma Loop_Invariant (for all K in V'First .. I => Result (K)'Initialized and then Result (K) = Decode (Data, V (K)));
      end loop;
      return Result;
   end Decode_Process;
   function Decode_Task (Data : Q.Byte_Array; V : Raw_Task_Array) return J.Task_Array is
      Result : J.Task_Array (V'Range) with Relaxed_Initialization;
   begin
      for I in V'Range loop
         Result (I) := Decode (Data, V (I));
         pragma Loop_Invariant (for all K in V'First .. I => Result (K)'Initialized and then Result (K) = Decode (Data, V (K)));
      end loop;
      return Result;
   end Decode_Task;
   function Decode_Namespace (Data : Q.Byte_Array; V : Raw_Namespace_Array) return J.Namespace_Array is
      Result : J.Namespace_Array (V'Range) with Relaxed_Initialization;
   begin
      for I in V'Range loop
         Result (I) := Decode (Data, V (I));
         pragma Loop_Invariant (for all K in V'First .. I => Result (K)'Initialized and then Result (K) = Decode (Data, V (K)));
      end loop;
      return Result;
   end Decode_Namespace;
end Worldline.Resource_Child_Execution_Wire;

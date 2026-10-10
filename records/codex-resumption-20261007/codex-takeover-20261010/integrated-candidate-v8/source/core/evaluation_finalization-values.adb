package body Evaluation_Finalization.Values with SPARK_Mode is
   function Record_Start_Value
     (A : T.Bytes; S : Start_Record; Plans : R.Check_Array;
      Before : Optional_Start) return Start_Update is
   begin
      return Evaluation_Finalization.Record_Start (A, S, Plans, Before);
   end Record_Start_Value;
   function Record_Input_Value
     (A : T.Bytes; S : Start_Record; I : Input_Record;
      Plans : R.Check_Array; Before : Optional_Input) return Input_Update is
   begin
      return Evaluation_Finalization.Record_Input (A, S, I, Plans, Before);
   end Record_Input_Value;
end Evaluation_Finalization.Values;

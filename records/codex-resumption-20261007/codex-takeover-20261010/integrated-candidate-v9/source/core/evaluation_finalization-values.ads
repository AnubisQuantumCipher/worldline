-- Value facade over the human-authorized parent total functions.
-- No parent dependency on this child is introduced.
package Evaluation_Finalization.Values with SPARK_Mode is
   subtype Start_Update is Evaluation_Finalization.Start_Update;
   subtype Input_Update is Evaluation_Finalization.Input_Update;
   function Record_Start_Value
     (A : T.Bytes; S : Start_Record; Plans : R.Check_Array;
      Before : Optional_Start) return Start_Update
     with Global => null,
       Post => Record_Start_Value'Result.Decision =
         Start_Reference (A, S, Plans, Before) and then
         (if Record_Start_Value'Result.Decision = Insert then
            Record_Start_Value'Result.Updated = (True, S)
          else Record_Start_Value'Result.Updated = Before);
   function Record_Input_Value
     (A : T.Bytes; S : Start_Record; I : Input_Record;
      Plans : R.Check_Array; Before : Optional_Input) return Input_Update
     with Global => null,
       Post => Record_Input_Value'Result.Decision =
         Input_Reference (A, S, I, Plans, Before) and then
         (if Record_Input_Value'Result.Decision = Insert then
            Record_Input_Value'Result.Updated = (True, I)
          else Record_Input_Value'Result.Updated = Before);
end Evaluation_Finalization.Values;

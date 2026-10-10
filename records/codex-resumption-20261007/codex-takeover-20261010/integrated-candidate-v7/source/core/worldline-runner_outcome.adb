with Worldline.Runner_Outcome_Bytes;
package body Worldline.Runner_Outcome with SPARK_Mode is
   function Decide (Data : E.Bytes; Capture : E.Span) return String is
     (Worldline.Runner_Outcome_Bytes.Decide (Data, Capture));
end Worldline.Runner_Outcome;

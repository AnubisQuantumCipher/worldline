with Resource_Quantities;
with SPARK.Big_Integers;

package Evaluation_Epoch with SPARK_Mode is
   use Resource_Quantities;
   use SPARK.Big_Integers;
   function Same_Value (Data : Byte_Array; Left, Right : Quantity) return Boolean
     with Global => null,
          Post => Same_Value'Result =
            (Span_Valid (Data, Left) and then Span_Valid (Data, Right)
             and then Value (Data, Left) >= 0 and then Value (Data, Right) >= 0
             and then Value (Data, Left) = Value (Data, Right));
   --  Exact retained successor producer body from the separate resource
   --  transition candidate. It remains unproved here and there; its Post is
   --  a required theorem, not imported authority or an assumption.
   function Is_Successor
     (Data : Byte_Array; Before, After : Quantity) return Boolean
     with Global => null,
          Post => Is_Successor'Result =
            (Span_Valid (Data, Before) and then Span_Valid (Data, After)
             and then Value (Data, Before) >= 0 and then Value (Data, After) >= 0
             and then Value (Data, After) = Value (Data, Before) + 1);
end Evaluation_Epoch;

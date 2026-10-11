package Worldline.Policy_Source with SPARK_Mode is
   type Relation is (Historical_No_Source, Source_Matches, Source_Conflicts);
   -- A historical structured requirement is not falsely relabelled as a raw
   -- acquisition. A present source observation must correspond completely.
   function Observe (Requirement : String) return Relation with Global => null;
   function Current_Matches (Expected, Observed : String) return Boolean
     with Global => null;
end Worldline.Policy_Source;

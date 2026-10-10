package Worldline.Protected_Paths with SPARK_Mode is
   function Matches (Pattern, Path : String) return Boolean with Global => null;
   function Touched (Expected_Requirement, Delta_JSON : String) return Boolean
     with Global => null;
end Worldline.Protected_Paths;

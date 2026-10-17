with Worldline.Producer_Values;
package Worldline.Evaluation_Policy with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   -- Complete original current requirement bytes, not a supplied roster or a
   -- saved success classification. Missing source declaration is not empty.
   function Required_Count (Requirement : String) return Natural
     with Global => null;
   function Required (Requirement : String; Ordinal : Natural) return String
     with Global => null;
   function Empty_Declared (Requirement : String) return Boolean
     with Global => null,
       Post => (if Empty_Declared'Result then Required_Count (Requirement) = 0);
   function Declaration (Requirement, Check : String) return String
     with Global => null;
   function Declaration_Count (Requirement : String) return Natural
     with Global => null;
   function Declaration_Name (Requirement : String; Ordinal : Natural)
      return String with Global => null;
   -- Render only values the native producer derived. Finalization adds the
   -- fixed agent/completion/verifier declarations and preserves extra engine
   -- requirement order from the independently captured actual engine input.
   function Project (Requirement, Additional : String; Finalization : Boolean)
      return String with Global => null;
   function Policy_Same (Expected, Observed : String) return Boolean
     with Global => null;
   -- Expected source members come from frozen Start.Policy, observed members
   -- from the separately acquired post-candidate tree, never a modified label.
   function Verifiers_Modified (Expected_Requirement, Returned_Context : String)
      return Boolean with Global => null;
   type Prefix_Status is (Prefix_Complete, Prefix_Changed, Return_Missing);
   function Prefix (Rows, Invocations, Returns : String) return Prefix_Status
     with Global => null;
   function Return_Row (Rows, Invocations, Returns : String; Ordinal : Natural)
      return Natural with Global => null;
   function Capture_Plan
     (Rows, Invocations, Returns, Expected_Requirement, Returned_Context : String)
      return String with Global => null;
end Worldline.Evaluation_Policy;

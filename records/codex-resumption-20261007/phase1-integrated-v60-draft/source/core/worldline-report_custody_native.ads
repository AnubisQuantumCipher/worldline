with Worldline.Evaluation_Wire;
with Worldline.Evaluation_Report_Facts;
package Worldline.Report_Custody_Native with SPARK_Mode is
   function Observe (Expected, Acquired, Result_Record : String;
      Raw : Worldline.Evaluation_Wire.Raw_Record)
      return Worldline.Evaluation_Report_Facts.Confinement_Observation
      with Global => null;
   -- Primitive acquisition relation shared by the separately typed readonly
   -- syntax-data provider. This does not admit an evaluation report or an AST.
   function Captured (Expected, Acquired, Result_Record : String) return Boolean
      with Global => null;
end Worldline.Report_Custody_Native;

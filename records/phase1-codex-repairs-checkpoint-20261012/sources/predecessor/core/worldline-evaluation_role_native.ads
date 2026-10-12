--  Pure redecision of the complete daemon kernel role acquisition. The caller
--  separately authenticates physical custody and the acquisition source chain.
--  Expected is the independent invocation, Observed the complete acquisition
--  list, Result_Record the original result. No compatibility flag authorizes.
package Worldline.Evaluation_Role_Native with SPARK_Mode is
   function Valid (Expected, Observed, Result_Record : String) return Boolean
     with Global => null;
   --  Historical projection ONLY: the original examiner slot predicate and
   --  worker projection. These establish no acquisition, custody, confinement
   --  or current authority and are not fallbacks inside Valid.
   function Original_Observed (Result_Record, Role_Name : String) return Boolean
     with Global => null;
   function Original_Workers_Separated (Result_Record : String) return Boolean
     with Global => null;
end Worldline.Evaluation_Role_Native;

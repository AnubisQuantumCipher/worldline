with Worldline.Startup_Admission;
package Worldline.Startup_Admission_Owned with SPARK_Mode is
   package P renames Worldline.Startup_Admission;
   package E renames P.L.E;
   type Observation is record
      Status : P.Action := P.Refused;
      Position : E.Count := 0;
   end record;
   function Runtime_Decide (Data, Name : E.Bytes) return Observation with Global => null;
   function Owner_Decide (Data, Name : E.Bytes) return Observation with Global => null;
   function Runtime_Transition
     (Before, After, Name : E.Bytes; Before_Action, After_Action : E.Count)
      return Boolean with Global => null;
   function Owner_Transition
     (Before, After, Name : E.Bytes; Before_Action, After_Action : E.Count)
      return Boolean with Global => null;
end Worldline.Startup_Admission_Owned;

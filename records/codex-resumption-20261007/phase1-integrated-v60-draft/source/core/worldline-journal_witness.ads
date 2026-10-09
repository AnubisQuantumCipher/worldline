with Worldline.Custody_V2_Load_Input;
package Worldline.Journal_Witness with SPARK_Mode is
   package L renames Worldline.Custody_V2_Load_Input;
   package E renames L.E;
   type Witness_Kind is (Owner_Canonical, Resource_ACK);
   type Decision is (Ready, Refused, Input_Invalid);
   function Decide (Kind : Witness_Kind; Current, Input : E.Bytes)
      return Decision
      with Global => null;
end Worldline.Journal_Witness;

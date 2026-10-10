with Worldline.Custody_V2_Root_Values;
package Worldline.Custody_V2_Machine_Evidence with SPARK_Mode is
   package V renames Worldline.Custody_V2_Root_Values;
   package E renames V.E;
   --  Replays BOTH original complete numeric machine frames from actual
   --  resource_machine_evidence.observe_ledger/observe_policy. Transport shape
   --  never supplies admission; original typed kernels own all numeric decisions.
   function Joined (Data : E.Bytes; Machine : E.Span) return Boolean
     with Global => null,
       Post => (if Joined'Result then V.Valid (Data, Machine));
end Worldline.Custody_V2_Machine_Evidence;

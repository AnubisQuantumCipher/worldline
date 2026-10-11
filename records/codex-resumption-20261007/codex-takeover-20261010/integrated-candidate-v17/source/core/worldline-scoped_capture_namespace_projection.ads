with Worldline.Retained_Evidence_Replay;

-- Factual SCM translation only. The original root/custody material and source
-- authentication remain independent required conjuncts at the caller.
package Worldline.Scoped_Capture_Namespace_Projection with SPARK_Mode is
   package R renames Worldline.Retained_Evidence_Replay;
   package E renames R.E;
   function FD_Receipt_Matches
     (Data : E.Bytes; Item, FD, Ucred : E.Span; Sending : Boolean) return Boolean
     with Global => null;
   function SCM_Credentials_Match
     (Data : E.Bytes; Send, Receive, OriginalActor, CurrentActor,
      NamespaceSource : E.Span) return Boolean
     with Global => null;
   function Reverse_Host_Matches
     (Data : E.Bytes; Inventory, Broker : E.Span) return Boolean
     with Global => null;
end Worldline.Scoped_Capture_Namespace_Projection;

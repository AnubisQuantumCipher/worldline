with Worldline.Retained_Evidence_Replay;

-- Factual owner/raw-source correspondence only; this does not grant an operation.
-- The caller separately authenticates acquisition/custody and invokes the complete
-- original kernels. No retained disposition or producer Boolean is authority.
package Worldline.Scoped_Capture_Owner_Projection with SPARK_Mode is
   package R renames Worldline.Retained_Evidence_Replay;
   package E renames R.E;
   function Owner_Source_Matches
     (Data : E.Bytes; Packet, Projection, Owner : E.Span;
      Scoped_Transport : Boolean := False) return Boolean
     with Global => null;
end Worldline.Scoped_Capture_Owner_Projection;

with Worldline.Archive_Envelope;
--  Complete original agent terminal status/measurement/reason precedence.
--  Inputs are actual cancellation/timeout, raw supervisor and resource-provider
--  observations, and actual exit comparison protocol for nonbuiltin providers.
package Worldline.Runner_Outcome with SPARK_Mode is
   package E renames Worldline.Archive_Envelope;
   --  Runtime/retained closure path: original finalization_journal.encode bytes.
   function Decide (Data : E.Bytes; Capture : E.Span) return String
     with Global => null;
end Worldline.Runner_Outcome;

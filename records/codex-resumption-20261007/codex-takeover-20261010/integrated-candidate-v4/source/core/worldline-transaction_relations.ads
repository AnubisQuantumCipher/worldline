with Worldline.Archive_Envelope;

--  Pure relations over the original operation archive, not caller verdicts.
--  Acquisition, path confinement and protected packet custody stay separate.
package Worldline.Transaction_Relations with SPARK_Mode is
   package E renames Worldline.Archive_Envelope;
   subtype Code is Natural range 0 .. 255;
   Accepted : constant Code := 0;
   Context_Missing : constant Code := 1;
   Context_Invalid : constant Code := 2;
   Verifier_Modified : constant Code := 3;
   Evidence_Stale : constant Code := 4;
   Record_Invalid : constant Code := 5;
   Live_Manifests : constant Code := 6;
   Historical_Manifests : constant Code := 7;
   Staged_Mismatch : constant Code := 8;
   Finish_Committed : constant Code := 9;
   Abort_Prepared : constant Code := 10;
   Ambiguous : constant Code := 11;
   Roster_Incomplete : constant Code := 12;
   Invalid_Request : constant Code := 255;

   function Freshness (Data : E.Bytes; Request : E.Span) return Code
     with Global => null;
   function Execution (Data : E.Bytes; Request : E.Span) return Code
     with Global => null;
   function Record_Matches (Data : E.Bytes; Request : E.Span) return Code
     with Global => null;
   function Manifests (Data : E.Bytes; Request : E.Span) return Code
     with Global => null;
   function Marker_State (Data : E.Bytes; Request : E.Span) return Code
     with Global => null;
   --  Informational proof/generated-artifact fields are carried intact, not
   --  interpreted as proof provenance or promotion authority.
   --  Authority contains the retained original protected broker sources.
   --  New captures additionally carry Actual.postFlushPacket; historical
   --  absence does not invent packet bytes. Complete native packet redecision,
   --  immutable transaction/manifests, original receipt projection and the
   --  exact append-versus-existing causal-event branch are separate joins.
   --  Exact archive correspondence is not historical NaN object identity.
   function Committed_Result_Matches
     (Data : E.Bytes; Original, Actual, Result, Chains, Authority : E.Span) return Boolean
     with Global => null;
   function Decide (Data : E.Bytes; Request : E.Span) return Code
     with Global => null,
       Post => Decide'Result in Accepted .. Roster_Incomplete | Invalid_Request;
end Worldline.Transaction_Relations;

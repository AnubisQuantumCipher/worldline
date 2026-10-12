with Worldline.Operation_Authority;
with Worldline.Archive_Envelope;
with Worldline.Operation_Archive;
package Worldline.Operation_Result_Relations with SPARK_Mode is
   package A renames Worldline.Operation_Authority;
   package E renames Worldline.Archive_Envelope;
   package O renames Worldline.Operation_Archive;
   use type E.Count;
   type Reason is (Ready, Original_Capture_Refused, Canonical_Material_Changed,
     Transaction_Result_Refused, Same_Use_Record_Changed, Original_Full_Chain_Refused);
   -- Executable complete reference models: the archive fields, reservation
   -- redecision, independently captured result and every original payload row
   -- are interpreted in their bodies. These are not root-only predicates.
   function Capture_Source_Reference
     (Data : E.Bytes; Material : E.Span) return Boolean with Global => null;
   function Result_Source_Reference
     (Data : E.Bytes; Material : E.Span) return Boolean with Global => null;
   function Capture_Reference
     (Data : E.Bytes; Material : E.Span; Bound : A.Binding) return Boolean
     with Global => null;
   function Result_Reference
     (Data : E.Bytes; Material : E.Span; Bound : A.Binding) return Boolean
     with Global => null;
   function Payloads_Reference
     (Data : E.Bytes; Material : E.Span; Bound : A.Binding; Facts : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Boolean
     with Global => null;
   function Assessment_Reference
     (Data : E.Bytes; Bound : A.Binding; Facts : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Reason
     with Global => null;
   function Assess
     (Data : E.Bytes; Bound : A.Binding; Facts : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Reason
     with Global => null,
       Post => Assess'Result = Assessment_Reference (Data, Bound, Facts, Receipts, Events);
   -- Material is the original archive of independently captured values, not
   -- flags or precomputed authorizations. Both entire historical JSON rosters
   -- accompany their native rows; no last-row projection substitutes for them.
   function Capture_Matches
     (Data : E.Bytes; Material : E.Span; Bound : A.Binding) return Boolean
     with Global => null,
       Post => Capture_Matches'Result = Capture_Reference (Data, Material, Bound);
   function Result_Matches
     (Data : E.Bytes; Material : E.Span; Bound : A.Binding) return Boolean
     with Global => null,
       Post => Result_Matches'Result = Result_Reference (Data, Material, Bound);
   function Payloads_Match
     (Data : E.Bytes; Material : E.Span; Bound : A.Binding; Facts : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Boolean
     with Global => null,
       Post => Payloads_Match'Result =
         Payloads_Reference (Data, Material, Bound, Facts, Receipts, Events);
   function Matches
     (Data : E.Bytes; Bound : A.Binding; Facts : A.Evidence;
      Receipts, Events : A.C.Retained_Rows) return Boolean
     with Global => null,
       Post => Matches'Result =
         (Capture_Matches (Data, Facts.Effect_Material, Bound)
          and then Result_Matches (Data, Facts.Effect_Material, Bound)
          and then Payloads_Match
            (Data, Facts.Effect_Material, Bound, Facts, Receipts, Events));
end Worldline.Operation_Result_Relations;

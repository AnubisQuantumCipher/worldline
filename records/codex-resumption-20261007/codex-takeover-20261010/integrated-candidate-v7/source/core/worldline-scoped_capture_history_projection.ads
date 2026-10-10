with Worldline.Retained_Evidence_Replay;

-- Original immutable closure evidence and genuine no-owner startup facts only.
-- Acquisition/custody and the fresh current header are caller conjunctions.
package Worldline.Scoped_Capture_History_Projection with SPARK_Mode is
   package R renames Worldline.Retained_Evidence_Replay;
   package E renames R.E;
   function Historical_Source_Matches
     (Data : E.Bytes; Row, Fact, Source, Owner : E.Span) return Boolean
     with Global => null;
   function Unavailable_Source_Matches
     (Data : E.Bytes; Row, Fact, Source, Owner : E.Span) return Boolean
     with Global => null;
   -- Full owned HELD/CLOSED protocol correspondence. Fresh descriptor, manager,
   -- source and whole-roster acquisition remain the parent's conjunctions.
   function Owned_Protocol_Matches
     (Data : E.Bytes; Row, Fact, Source, Roster_Entry, History : E.Span) return Boolean
     with Global => null;
end Worldline.Scoped_Capture_History_Projection;

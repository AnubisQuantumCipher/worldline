with Worldline.Runner_Lifecycle_Bytes;
package body Worldline.Runner_Lifecycle with SPARK_Mode is
   package B renames Worldline.Runner_Lifecycle_Bytes;
   function Ended (Data : E.Bytes; Rows : E.Span) return Boolean is
     (B.Ended (Data, Rows));
   function Commands_Ended (Data : E.Bytes; Rows : E.Span) return Boolean is
     (B.Commands_Ended (Data, Rows));
   function Eof_Complete (Data : E.Bytes; Value : E.Span) return Boolean is
     (B.Eof_Complete (Data, Value));
   function Proxy_Ended (Data : E.Bytes; Proxy : E.Span) return Boolean is
     (B.Proxy_Ended (Data, Proxy));
   function Quiescent (Data : E.Bytes; Owner : E.Span) return Boolean is
     (B.Quiescent (Data, Owner));
   function Quiescent (Data : E.Bytes; Owner : E.View) return Boolean is
     (B.Quiescent (Data, Owner));
   function Finalization_Quiescent (Data : E.Bytes; Owner : E.Span) return Boolean is
     (B.Finalization_Quiescent (Data, Owner));
   function Generation_Stable (Data : E.Bytes; Owner : E.Span) return Boolean is
     (B.Generation_Stable (Data, Owner));
   function Finished (Data : E.Bytes; Owner : E.Span) return Boolean is
     (B.Finished (Data, Owner));
   function Cancellation_Membership (Data : E.Bytes; Capture : E.Span) return Boolean is
     (B.Cancellation_Membership (Data, Capture));
   function Cancellation_Membership_Valid (Data : E.Bytes; Capture : E.Span) return Boolean is
     (B.Cancellation_Membership_Valid (Data, Capture));
   function Allowed (Data : E.Bytes; Owner : E.Span; Requested : Action) return Boolean is
     (B.Allowed (Data, Owner, Requested));
end Worldline.Runner_Lifecycle;

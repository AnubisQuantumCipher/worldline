with Worldline.Archive_Envelope;
with Worldline.Runner_Lifecycle;
--  Two explicit borrowed profiles, never a guessed/weak JSON dispatch.
--  Quiescent(Data,Span) retains the original canonical root producer view.
--  All runtime/action/closure views decode finalization_journal.encode through
--  the original Archive_Envelope Finalization layer. Count-sized spans retain
--  entire original values; no String copy, numeric/roster/depth domain cap.
package Worldline.Runner_Lifecycle_Bytes with SPARK_Mode is
   package E renames Worldline.Archive_Envelope;
   function Quiescent (Data : E.Bytes; Owner : E.Span) return Boolean
     with Global => null;
   function Quiescent (Data : E.Bytes; Owner : E.View) return Boolean
     with Global => null;
   function Finalization_Quiescent (Data : E.Bytes; Owner : E.Span) return Boolean
     with Global => null;
   function Field (Data : E.Bytes; Owner : E.Span; Name : String) return E.Span
     with Global => null;
   function Text_Is (Data : E.Bytes; Item : E.Span; Text : String) return Boolean
     with Global => null;
   --  Same-buffer view of the two-buffer Equal below; it is not itself
   --  recursive, so it carries no variant of its own.
   function Equal (Data : E.Bytes; Left, Right : E.Span) return Boolean
     with Global => null;
   function Truth (Data : E.Bytes; Item : E.Span) return Boolean with Global => null;
   function Equal (Left_Data, Right_Data : E.Bytes; Left, Right : E.Span)
      return Boolean with Global => null,
        Subprogram_Variant => (Decreases => Left.Length);
   function Is_True (Data : E.Bytes; Owner : E.Span; Name : String) return Boolean
     with Global => null;
   function Is_False (Data : E.Bytes; Owner : E.Span; Name : String) return Boolean
     with Global => null;
   function Ended (Data : E.Bytes; Rows : E.Span) return Boolean
     with Global => null;
   function Commands_Ended (Data : E.Bytes; Rows : E.Span) return Boolean
     with Global => null;
   function Eof_Complete (Data : E.Bytes; Item : E.Span) return Boolean
     with Global => null;
   function Proxy_Ended (Data : E.Bytes; Item : E.Span) return Boolean
     with Global => null;
   function Finished (Data : E.Bytes; Owner : E.Span) return Boolean
     with Global => null;
   function Generation_Stable (Data : E.Bytes; Owner : E.Span) return Boolean
     with Global => null;
   function Cancellation_Membership_Valid (Data : E.Bytes; Capture : E.Span)
      return Boolean with Global => null;
   function Cancellation_Membership (Data : E.Bytes; Capture : E.Span)
      return Boolean with Global => null;
   function Allowed
     (Data : E.Bytes; Owner : E.Span; Requested : Runner_Lifecycle.Action)
      return Boolean with Global => null;
   function Text_Is (Data : E.Bytes; Item : E.View; Text : String) return Boolean
     with Global => null;
   function Text_Equal (Left_Data, Right_Data : E.Bytes; Left, Right : E.View)
      return Boolean with Global => null;
end Worldline.Runner_Lifecycle_Bytes;

with Worldline.Retained_Evidence_Replay;
with SPARK.Big_Integers;

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
private
   use type E.Count;
   use type E.Q.Byte;
   -- Factual parsers are private so a child regression unit can exercise the
   -- exact production bodies without exposing an authorization interface.
   -- Line positions are offsets, including the representable end offset.
   function Map_Line_End (Raw : E.Bytes; Start : E.Count) return E.Count
     with Global => null, Pre => Start <= Raw'Length,
       Post => Map_Line_End'Result in Start .. Raw'Length and then
         (if Map_Line_End'Result < Raw'Length then
            Raw (Raw'First + Map_Line_End'Result) = 10);
   function Map_Valid (Raw : E.Bytes) return Boolean with Global => null;
   function Map_Value
     (Raw : E.Bytes; Value, Overflow : SPARK.Big_Integers.Valid_Big_Integer)
      return SPARK.Big_Integers.Valid_Big_Integer with Global => null;
   function Last_PID (Raw : E.Bytes) return SPARK.Big_Integers.Valid_Big_Integer
     with Global => null;
end Worldline.Scoped_Capture_Namespace_Projection;

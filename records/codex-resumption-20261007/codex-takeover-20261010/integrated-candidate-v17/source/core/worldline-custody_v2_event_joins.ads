with Worldline.Custody_V2_Typed_Step;
package Worldline.Custody_V2_Event_Joins with SPARK_Mode is
   package D renames Worldline.Custody_V2_Typed_Step;
   package C renames D.C;
   package A renames D.A;
   package M renames D.M;
   package Q renames D.Q;
   package S renames C.S;
   use type Q.Byte_Count;
   use type M.Event_Kind;
   use type A.Alternative_Set;
   use type M.Subject_Kind;
   use type M.Digest;
   use type Q.Ordering;

   -- Complete F.6 alternative domain, including the DRAIN family. These
   -- relations compare retained bytes/identities; none is a Legal verdict.
   function Has_Alternative (Kind : M.Event_Kind) return Boolean is
     (Kind in M.Custody_Ack_Event | M.Abandon_Event | M.Handoff_Abort_Event |
       M.Request_Intake_Event | M.Request_Abandon_Event |
       M.Drain_Intake_Event | M.Drain_Abandon_Event) with Global => null;
   function Set_Of (Kind : M.Event_Kind) return A.Alternative_Set is
     (case Kind is
        when M.Request_Intake_Event | M.Request_Abandon_Event => A.Request_Set,
        when M.Drain_Intake_Event | M.Drain_Abandon_Event => A.Drain_Set,
        when others => A.Ack_Set) with Global => null;
   function Row_Joined
     (Data : C.E.Bytes; Row : A.Alternative_Row; Event : M.Event_Record)
      return Boolean is
     (Has_Alternative (Event.Kind) and then Row.Set = Set_Of (Event.Kind) and then
      Row.Event_Id = Event.Event_Id and then
      Q.Compare (Data, Row.Generation, Event.Generation) = Q.Equal and then
      M.L.Optional_Same (Data, Row.Operation, Event.Operation) and then
      Row.Kind_Of_Subject = Event.Kind_Of_Subject and then
      M.L.Optional_Same (Data, Row.Subject, Event.Subject) and then
      Q.Compare (Data, Row.Subgeneration, Event.Subgeneration) = Q.Equal)
      with Global => null;
   function Same_Key
     (Data : C.E.Bytes; Left, Right : A.Alternative_Row) return Boolean is
     (Left.Set = Right.Set and then
      Q.Compare (Data, Left.Generation, Right.Generation) = Q.Equal and then
      M.L.Optional_Same (Data, Left.Operation, Right.Operation) and then
      Left.Kind_Of_Subject = Right.Kind_Of_Subject and then
      M.L.Optional_Same (Data, Left.Subject, Right.Subject) and then
      Q.Compare (Data, Left.Subgeneration, Right.Subgeneration) = Q.Equal)
      with Global => null;
   function Alternatives_Exact
     (Data : C.E.Bytes; Events : A.R.Retained_Events;
      Rows : A.Alternative_Rows) return Boolean is
     (A.Rows_Valid (Data, Rows) and then
      (for all I in Rows'Range =>
         (for all J in Rows'Range =>
            (if I /= J then not Same_Key (Data, Rows (I), Rows (J)) and then
               Rows (I).Event_Id /= Rows (J).Event_Id))) and then
      (for all Row of Rows =>
         (for some Item of Events => Row_Joined (Data, Row, Item.Event))) and then
      (for all Item of Events =>
         (if Has_Alternative (Item.Event.Kind) then
            (for some Row of Rows => Row_Joined (Data, Row, Item.Event)))))
      with Global => null;
   function Alternative_Free
     (Data : C.E.Bytes; Prior : A.R.Retained_Events;
      Proposed : M.Event_Record) return Boolean is
     (not Has_Alternative (Proposed.Kind) or else
      (for all Item of Prior =>
         (if Has_Alternative (Item.Event.Kind) and then
             Set_Of (Item.Event.Kind) = Set_Of (Proposed.Kind) and then
             A.Same_Alternative (Data, Item.Event, Proposed)
          then Item.Event.Kind = Proposed.Kind))) with Global => null;

   -- Authenticated event references must be earlier than their consumer,
   -- and join the complete archive, not merely its kind or copied status.
   -- Reference is the original nested event object as encoded by archive.
   function Reference_Matches
     (Data : C.E.Bytes; Reference : C.E.Span; Raw : C.Event_Row)
      return Boolean with Global => null;
   function Prior_Reference
     (Data : C.E.Bytes; Reference : C.E.Span; Events : C.Event_Rows;
      Consumer : Q.Byte_Index; Required : M.Event_Kind;
      Generation, Operation : C.E.Span) return Boolean with Global => null;
end Worldline.Custody_V2_Event_Joins;

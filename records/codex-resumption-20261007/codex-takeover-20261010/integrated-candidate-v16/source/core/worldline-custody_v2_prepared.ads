with Worldline.Custody_V2_Typed_Step;
with Worldline.Operation_Authority;
package Worldline.Custody_V2_Prepared with SPARK_Mode is
   package D renames Worldline.Custody_V2_Typed_Step;
   package C renames D.C;
   package M renames D.M;
   package Q renames D.Q;
   package O renames Worldline.Operation_Authority;
   package P renames D.A.P;
   use type O.Operation;
   use type O.Decision;
   use type M.Event_Kind;
   use type M.Subject_Kind;
   use type M.Actor;
   use type M.Root_Phase;
   use type Q.Ordering;
   use type Q.Byte_Count;
   use type M.Root_State;
   use type M.Physical_Flags;
   function Workload (Op : O.Operation) return Boolean is
     (Op in O.Fork_World | O.Race_Worlds | O.Revalidate | O.Simulate |
            O.Run_Ghost | O.Enable_Ghost | O.Add_Root | O.Initialize)
      with Global => null;
   -- Real native redecision of complete original snapshots. No supplied
   -- RESERVED_NEW/REPLAY flag. Authentication/raw-snapshot decoding separate.
   function Operation_Heads_Reestablished
     (Data : Q.Byte_Array; Grants : O.Grants; Before_Uses, Intent_Uses : O.Uses;
      Bound : O.Binding; Reserve_Now, Intent_Now : Q.Quantity;
      Reserve_Evidence, Intent_Evidence : O.Evidence;
      Reserve_Receipts, Reserve_Events, Intent_Receipts, Intent_Events : O.C.Retained_Rows)
      return Boolean is
     (Workload (Bound.Action) and then
      O.Decide (Data, Grants, Before_Uses, Bound, Reserve_Now, O.Reserve_Use,
        Reserve_Evidence, Reserve_Receipts, Reserve_Events) = O.Reserved_New and then
      O.Decide (Data, Grants, Intent_Uses, Bound, Intent_Now, O.Reserve_Use,
        Intent_Evidence, Intent_Receipts, Intent_Events) = O.Reserved_Replay)
     with Global => null;
   function Root_Event_Join
     (Data : C.E.Bytes; Before : M.Root_State; Raw : C.Event_Row;
      Event : M.Event_Record; Bound : O.Binding) return Boolean is
     (Event.Kind = M.Prepared_Event and then Event.Kind_Of_Subject = M.Root and then
      Event.Appending_Actor = M.Front and then Before.Phase = M.Front_Owned and then
      Before.Owners_Open and then Q.Span_Valid (Data, Before.Generation) and then
      Q.Span_Valid (Data, Event.Generation) and then
      Q.Compare (Data, Before.Generation, Event.Generation) = Q.Equal and then
      Event.Subject.Present and then Event.Subject.Value.Length = 0 and then
      Bound.Id (O.Operation_Id).Present and then
      C.G.Origin_Matches (Data, Raw.Operation, Bound.Id (O.Operation_Id).Value))
     with Global => null;
   procedure Try_Next
     (Data : C.E.Bytes; Raw : C.Event_Row; Before : M.Root_State;
      Grants : O.Grants; Before_Uses, Intent_Uses : O.Uses; Bound : O.Binding;
      Reserve_Now, Intent_Now : Q.Quantity; Reserve_Evidence, Intent_Evidence : O.Evidence;
      Reserve_Receipts, Reserve_Events, Intent_Receipts, Intent_Events : O.C.Retained_Rows;
      After : out M.Root_State; Value_Join : out Boolean)
     with Global => null, Always_Terminates,
       Post => (if not Value_Join then After = Before)
         and then (if Value_Join then After.Phase = M.Prepared and then
                    After.Owners_Open = Before.Owners_Open and then
                    After.Physical = Before.Physical);
end Worldline.Custody_V2_Prepared;

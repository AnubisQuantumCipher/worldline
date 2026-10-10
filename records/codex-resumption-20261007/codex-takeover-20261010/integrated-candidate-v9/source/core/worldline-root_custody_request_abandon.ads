with Worldline.Root_Custody_Abandon;

--  REQUEST_ABANDON semantic row. Native X4/X5 and authentic same-transaction
--  caller/actor/raw correspondence remain mandatory external obligations.
package Worldline.Root_Custody_Request_Abandon with SPARK_Mode is
   package A renames Worldline.Root_Custody_Abandon;
   package R renames A.R;
   package M renames A.M;
   package Q renames A.Q;
   package L renames A.L;
   use type Q.Byte_Count;
   use type Q.Ordering;
   use type M.Root_Phase;
   use type M.Request_Phase;
   use type M.Event_Kind;
   use type M.Subject_Kind;
   use type M.Actor;
   use type M.Subject_State;
   use type M.Root_State_Array;
   use type A.Alternative_Set;
   use type R.Replay_Status;
   use type Worldline.Hash;

   type Expected_Request is record
      Generation : Q.Quantity;
      Subject : M.Identity;
      Subgeneration : Q.Quantity;
      Head : M.Digest;
      Phase : M.Request_Phase;
   end record;
   function Subject_Bound
     (Data : Q.Byte_Array; Item : M.Subject_State; Expected : Expected_Request)
      return Boolean is
     (Item.Kind = M.Request and then
      Q.Compare (Data, Item.Generation, Expected.Generation) = Q.Equal and then
      L.Same (Data, Item.Subject, Expected.Subject)) with Global => null;
   function Subject_CAS
     (Data : Q.Byte_Array; Item : M.Subject_State; Expected : Expected_Request)
      return Boolean is
     (Subject_Bound (Data, Item, Expected) and then Item.Head = Expected.Head and then
      Item.Request = Expected.Phase and then
      Q.Compare (Data, Item.Subgeneration, Expected.Subgeneration) = Q.Equal)
   with Global => null;
   function Request_Kind (Kind : M.Event_Kind) return Boolean is
     (Kind in M.Request_Intake_Event | M.Request_Abandon_Event) with Global => null;
   function Alternative_Joined
     (Data : Q.Byte_Array; Row : A.Alternative_Row; Event : M.Event_Record)
      return Boolean is
     (Row.Set = A.Request_Set and then Request_Kind (Event.Kind) and then
      Row.Event_Id = Event.Event_Id and then
      Q.Compare (Data, Row.Generation, Event.Generation) = Q.Equal and then
      L.Optional_Same (Data, Row.Operation, Event.Operation) and then
      Row.Kind_Of_Subject = Event.Kind_Of_Subject and then
      L.Optional_Same (Data, Row.Subject, Event.Subject) and then
      Q.Compare (Data, Row.Subgeneration, Event.Subgeneration) = Q.Equal)
   with Global => null;
   function Table_Corresponds
     (Data : Q.Byte_Array; Events : R.Retained_Events; Rows : A.Alternative_Rows)
      return Boolean is
     ((for all Item of Events => (if Request_Kind (Item.Event.Kind) then
         (for some Row of Rows => Alternative_Joined (Data, Row, Item.Event)))) and then
      (for all Row of Rows => (if Row.Set = A.Request_Set then
         (for some Item of Events => Alternative_Joined (Data, Row, Item.Event)))))
   with Global => null;
   function Alternative_Allowed
     (Data : Q.Byte_Array; Events : R.Retained_Events; Proposed : M.Event_Record)
      return Boolean is
     (for all Item of Events =>
        (if Request_Kind (Item.Event.Kind) and then
            A.Same_Alternative (Data, Item.Event, Proposed)
         then Item.Event.Kind = Proposed.Kind)) with Global => null;

   function Subjects_Valid
     (Data : Q.Byte_Array; Subjects : M.Subject_State_Array;
      Expected : Expected_Request) return Boolean is
     (A.C.Generation_Valid (Data, Expected.Generation) and then
      Q.Span_Valid (Data, Expected.Subgeneration) and then
      L.Id_Valid (Data, Expected.Subject) and then
      (for all Item of Subjects => Item.Kind /= M.Root and then
         A.C.Generation_Valid (Data, Item.Generation) and then
         Q.Span_Valid (Data, Item.Subgeneration) and then L.Id_Valid (Data, Item.Subject))
      and then
      (for all I in Subjects'Range => (for all J in Subjects'Range =>
         (if I /= J and then Subjects (I).Kind = Subjects (J).Kind and then
             Q.Compare (Data, Subjects (I).Generation, Subjects (J).Generation) = Q.Equal
          then not L.Same (Data, Subjects (I).Subject, Subjects (J).Subject)))))
   with Global => null;

   function Event_Bound
     (Data : Q.Byte_Array; Root : A.Expected_Root; Expected : Expected_Request;
      Proposed : M.Event_Record) return Boolean is
     (Proposed.Kind_Of_Subject = M.Request and then
      Q.Compare (Data, Root.Generation, Expected.Generation) = Q.Equal and then
      Q.Compare (Data, Expected.Generation, Proposed.Generation) = Q.Equal and then
      Q.Compare (Data, Expected.Subgeneration, Proposed.Subgeneration) = Q.Equal and then
      L.Same (Data, Expected.Subject, Proposed.Subject)) with Global => null;
   --  Operation belongs to the retained request transfer event. It is NOT
   --  silently equated to the WL operation that started the root generation.
   function Transfer_Head_Joined
     (Data : Q.Byte_Array; Events : R.Retained_Events;
      Expected : Expected_Request; Proposed : M.Event_Record) return Boolean is
     (for some Item of Events => Item.Event.Event_Id = Expected.Head and then
        Item.Event.Kind = M.Request_Transfer_Intent_Event and then
        A.Same_Alternative (Data, Item.Event, Proposed)) with Global => null;

   --  XC-7: current generation OR historical request cleanup before that
   --  generation's CUSTODY_RETURNED. Do not discard old Ended rows globally.
   function Generation_Allowed
     (Data : Q.Byte_Array; Roots : M.Root_State_Array; Events : R.Retained_Events;
      Root : A.Expected_Root) return Boolean is
     ((for some Item of Roots => A.Bound (Data, Item, Root) and then
         Item.Phase /= M.Ended) or else
      (for all Item of Events =>
         not (Item.Event.Kind = M.Custody_Returned_Event and then
              Q.Compare (Data, Item.Event.Generation, Root.Generation) = Q.Equal)))
   with Global => null;

   function Legal
     (Data : Q.Byte_Array; Roots : M.Root_State_Array; Subjects : M.Subject_State_Array;
      Events : R.Retained_Events; Rows : A.Alternative_Rows;
      Root : A.Expected_Root; Expected : Expected_Request; Proposed : M.Event_Record)
      return Boolean is
     (Proposed.Kind = M.Request_Abandon_Event and then
      R.Resolve (Data, Events, R.Key (Proposed)).Status = R.No_Replay and then
      A.Fresh_Inputs_Valid (Data, Roots, Root, Proposed) and then
      Subjects_Valid (Data, Subjects, Expected) and then A.Rows_Valid (Data, Rows) and then
      Table_Corresponds (Data, Events, Rows) and then
      Alternative_Allowed (Data, Events, Proposed) and then
      (for some Item of Roots => A.CAS_Matches (Data, Item, Root)) and then
      (for some Item of Subjects => Subject_CAS (Data, Item, Expected)) and then
      Event_Bound (Data, Root, Expected, Proposed) and then
      Generation_Allowed (Data, Roots, Events, Root) and then
      Expected.Phase = M.Transfer_Intent and then
      Transfer_Head_Joined (Data, Events, Expected, Proposed) and then
      Proposed.Appending_Actor in M.Front | M.Reconciler)
   with Global => null;

   type Decision_Status is
     (Replay_Unchanged, Append_Request_Abandon, Invalid_Operands, Ambiguous_History,
      History_Table_Mismatch, Alternative_Taken, CAS_Stale,
      Generation_Join_Failed, Phase_Not_Permitted, Transfer_Head_Mismatch,
      Actor_Not_Permitted);
   type Decision (Status : Decision_Status := Invalid_Operands) is record
      case Status is
         when Replay_Unchanged => Event_Position : Q.Byte_Index;
         when others => null;
      end case;
   end record;
   function Decide
     (Data : Q.Byte_Array; Roots : M.Root_State_Array; Subjects : M.Subject_State_Array;
      Events : R.Retained_Events; Rows : A.Alternative_Rows;
      Root : A.Expected_Root; Expected : Expected_Request; Proposed : M.Event_Record)
      return Decision
   with Global => null, Pre => Proposed.Kind = M.Request_Abandon_Event,
     Post => (Decide'Result.Status = Append_Request_Abandon) =
       Legal (Data, Roots, Subjects, Events, Rows, Root, Expected, Proposed) and then
       (Decide'Result.Status = Replay_Unchanged) =
          (R.Resolve (Data, Events, R.Key (Proposed)).Status = R.Found) and then
       (if Decide'Result.Status = Replay_Unchanged then
          Decide'Result.Event_Position in Events'Range and then
          R.Matches (Data, Events (Decide'Result.Event_Position), R.Key (Proposed)));

   procedure Apply_Next
     (Data : Q.Byte_Array; Roots : in out M.Root_State_Array;
      Subjects : in out M.Subject_State_Array;
      Events : R.Retained_Events; Rows : A.Alternative_Rows;
      Root : A.Expected_Root; Expected : Expected_Request; Proposed : M.Event_Record)
   with Global => null, Always_Terminates,
     Pre => Legal (Data, Roots, Subjects, Events, Rows, Root, Expected, Proposed),
     Post => Roots = Roots'Old and then
       (for all I in Subjects'Range => Subjects (I) =
          (if Subject_Bound (Data, Subjects'Old (I), Expected) then
              (Subjects'Old (I) with delta Request => M.Abandoned, Head => Proposed.Event_Id)
           else Subjects'Old (I)));
   --  No increment on abandon: s+1 occurs on the next TRANSFER_INTENT.
   --  No socket send/close, child stop, resource release, owner or root change.
end Worldline.Root_Custody_Request_Abandon;

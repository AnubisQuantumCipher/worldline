with Worldline.Root_Custody_Context;

--  Pure, decidable VALUE clauses and single-row images. NOT the complete
--  Legal/Next authority entry: native evidence and generation-wide updates
--  must still be composed. No Ready/authenticated/caller-verdict operands.
--  Termination remains REQUIRED for every precondition-satisfying input:
--  these ordinary side-effect-free SPARK functions have the intrinsic
--  termination obligation documented by this toolchain's E0016. Explicit
--  per-function Always_Terminates is illegal here; no obligation is waived.
package Worldline.Root_Custody_Phase_Values with SPARK_Mode is
   package C renames Worldline.Root_Custody_Context;
   package M renames C.M;
   package Q renames M.Q;
   package L renames M.L;
   use type Q.Ordering;
   use type C.Context_Status;
   use type M.Root_Phase;
   use type M.Request_Phase;
   use type M.Descriptor_Phase;
   use type M.Subject_Kind;
   use type M.Actor;
   use type M.Event_Kind;
   use type M.Owner;
   use type M.Root_State;
   use type Worldline.Hash;

   type Event_Family is
     (Root_Transition, Physical_Transition, Request_Transition,
      Descriptor_Transition, Original_Progress_Observation, Reconciliation);
   function Family (Kind : M.Event_Kind) return Event_Family is
     (case Kind is
        when M.Closed_NS_Event | M.Closed_Outer_Event | M.Closed_Raw_Event |
             M.Closed_Witness_Event | M.Physical_Settled_Event => Physical_Transition,
        when M.Request_Queued_Event | M.Request_Transfer_Intent_Event |
             M.Request_Intake_Event | M.Request_Abandon_Event |
             M.Request_Responded_Event | M.Request_Lost_Event => Request_Transition,
        when M.Drain_Stop_Intent_Event | M.Drain_Freeze_Event |
             M.Drain_Ofd_Evidence_Event | M.Drain_Intake_Event |
             M.Drain_Abandon_Event | M.Drain_Released_Event |
             M.Drain_Reclaimed_Event => Descriptor_Transition,
        when M.Original_Progress_Event => Original_Progress_Observation,
        when M.Reconciled_Event => Reconciliation,
        when others => Root_Transition)
   with Global => null;

   function Is_Physical (Kind : M.Event_Kind) return Boolean is
     (Kind in M.Closed_NS_Event | M.Closed_Outer_Event | M.Closed_Raw_Event |
        M.Closed_Witness_Event | M.Physical_Settled_Event)
   with Global => null;

   --  XC-5 and XC-6 over the complete supplied subjects; no global current
   --  generation filter discards historical physical-event subjects.
   function Subject_Barrier
     (Data : Q.Byte_Array; Subjects : M.Subject_State_Array;
      Generation : Q.Quantity) return Boolean is
     (C.Generation_Valid (Data, Generation) and then
      (for all Item of Subjects =>
         Q.Span_Valid (Data, Item.Generation) and then
         (if Q.Compare (Data, Item.Generation, Generation) = Q.Equal then
            (case Item.Kind is
               when M.Root => False,
               when M.Request => Item.Request not in M.Transfer_Intent | M.Intake,
               when M.Descriptor => Item.Descriptor not in
                 M.Stop_Intent | M.Frozen | M.Ofd_Evidence | M.Intake))))
   with Global => null;

   --  Original phase-table conjunct only. It does not decide CAS, replay,
   --  current generation, actor, native evidence, CxP or request/child joins.
   --  Original_Progress is phase-preserving but its exact global v2 phase
   --  acceptance remains separate from the observed receiving windows.
   function Root_From_Clause
     (State : M.Root_State; Kind : M.Event_Kind) return Boolean is
     (case Kind is
        when M.Prepared_Event => State.Phase = M.Front_Owned,
        when M.Held_Event => State.Phase = M.Prepared,
        when M.Running_Event => State.Phase = M.Held,
        when M.Execution_Native_Event => State.Phase = M.Running,
        when M.Execution_Ack_Event => State.Phase = M.Execution_Native,
        when M.Handoff_Intent_Event => State.Phase = M.Execution_Ack,
        when M.Front_Close_Intent_Event => State.Phase = M.Handoff_Intent,
        when M.Front_Closed_Event => State.Phase = M.Front_Close_Intent,
        when M.Transfer_Sent_Event => State.Phase = M.Front_Closed,
        when M.Roster_Evidence_Event => State.Phase = M.Transfer_Sent,
        when M.Custody_Ack_Event | M.Abandon_Event =>
          State.Phase in M.Transfer_Sent | M.Roster_Evidence,
        when M.Front_Retained_Escrow_Event => State.Phase = M.Abandoned,
        when M.Handoff_Abort_Event => State.Phase in
          M.Prepared | M.Held | M.Running | M.Execution_Native |
          M.Execution_Ack | M.Handoff_Intent | M.Front_Close_Intent | M.Front_Closed,
        when M.Original_Result_Event => State.Phase = M.Worker_Owned,
        when M.Handler_Terminal_Event => State.Phase = M.Original_Result,
        when M.Worker_Relinquish_Event => State.Phase = M.Handler_Terminal,
        when M.Worker_Reattached_Event =>
          M.Is_Worker_Phase (State.Phase) or else
          (State.Phase = M.Unknown and then M.Is_Worker_Phase (State.Before_Unknown)),
        when M.Custody_Returned_Event =>
          M.Is_Worker_Phase (State.Phase) or else
          State.Phase = M.Front_Retained_Escrow or else
          (State.Phase = M.Unknown and then
             (M.Is_Worker_Phase (State.Before_Unknown) or else
              State.Before_Unknown = M.Front_Retained_Escrow)),
        when M.Historical_Settlement_Event =>
          State.Phase in M.Custody_Returned | M.Handoff_Aborted,
        when M.Front_Reconstruction_Event =>
          State.Phase = M.Historical_Settlement and then not State.Owners_Open,
        when M.Front_Owned_Event => State.Phase = M.Front_Reconstruction or else
          (State.Phase = M.Historical_Settlement and then State.Owners_Open),
        when M.Unknown_Event => State.Phase /= M.Ended,
        when M.Reconciled_Event => State.Phase = M.Unknown,
        when M.Closed_NS_Event | M.Closed_Outer_Event | M.Closed_Raw_Event |
             M.Closed_Witness_Event | M.Physical_Settled_Event =>
          State.Physical.Launched,
        when M.Original_Progress_Event => True,
        when others => False)
   with Global => null;

   --  Only table actor clause. Unknown needs contextual CURRENT owner supplied
   --  by the full native roster selection, not a Boolean or Owner operand.
   function Fixed_Root_Actor_Clause
     (State : M.Root_State; Kind : M.Event_Kind; Caller : M.Actor)
      return Boolean is
     (case Kind is
        when M.Prepared_Event | M.Held_Event | M.Running_Event |
             M.Execution_Native_Event | M.Execution_Ack_Event |
             M.Handoff_Intent_Event | M.Front_Close_Intent_Event |
             M.Front_Closed_Event | M.Transfer_Sent_Event |
             M.Roster_Evidence_Event | M.Front_Retained_Escrow_Event |
             M.Handoff_Abort_Event | M.Front_Owned_Event => Caller = M.Front,
        when M.Custody_Ack_Event | M.Original_Result_Event |
             M.Handler_Terminal_Event | M.Worker_Relinquish_Event |
             M.Worker_Reattached_Event | M.Original_Progress_Event => Caller = M.Worker,
        when M.Abandon_Event => Caller in M.Front | M.Reconciler,
        when M.Custody_Returned_Event => Caller in M.Collector | M.Reconciler,
        when M.Historical_Settlement_Event =>
          (if State.Phase = M.Handoff_Aborted and then State.Owners_Open
           then Caller = M.Front else Caller = M.Collector),
        when M.Front_Reconstruction_Event => Caller = M.Collector,
        when M.Reconciled_Event => Caller = M.Reconciler,
        when M.Closed_NS_Event | M.Closed_Outer_Event | M.Closed_Raw_Event |
             M.Closed_Witness_Event | M.Physical_Settled_Event =>
          Caller = (if State.Owners_Open or else State.Phase in
                      M.Abandoned | M.Front_Retained_Escrow | M.Handoff_Aborted
                    then M.Front else M.Collector),
        when M.Unknown_Event => True, -- no fixed actor: contextual clause below
        when others => False)
   with Global => null;

   function Unknown_Actor_Clause
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Current : C.Root_Reference; Caller : M.Actor) return Boolean is
     (Caller = M.Reconciler or else
      (C.Current_Store_Owner (Data, Roots, Current).Status = C.Projected and then
       C.Current_Store_Owner (Data, Roots, Current).Value = M.Actor_Owner (Caller)))
   with Global => null;

   function Physical_Flag_Clause
     (State : M.Root_State; Kind : M.Event_Kind) return Boolean is
     (State.Physical.Launched and then
      (case Kind is
         when M.Closed_NS_Event | M.Closed_Raw_Event => True,
         when M.Closed_Outer_Event => State.Physical.NS,
         when M.Closed_Witness_Event =>
           State.Physical.NS and then State.Physical.Outer and then State.Physical.Raw,
         when M.Physical_Settled_Event => State.Physical.Witness,
         when others => False))
   with Global => null;

   function Transfer_Root_Clause (State : M.Root_State) return Boolean is
     (State.Phase in M.Worker_Owned | M.Original_Result | M.Handler_Terminal)
   with Global => null;

   type Optional_Subject (Present : Boolean := False) is record
      case Present is
         when True => Value : M.Subject_State;
         when False => null;
      end case;
   end record;

   function Request_From_Clause
     (Before : Optional_Subject; Kind : M.Event_Kind) return Boolean is
     (case Kind is
        when M.Request_Queued_Event => not Before.Present,
        when M.Request_Transfer_Intent_Event => Before.Present and then
          Before.Value.Kind = M.Request and then
          Before.Value.Request in M.Queued | M.Abandoned,
        when M.Request_Intake_Event | M.Request_Abandon_Event =>
          Before.Present and then Before.Value.Kind = M.Request and then
          Before.Value.Request = M.Transfer_Intent,
        when M.Request_Responded_Event => Before.Present and then
          Before.Value.Kind = M.Request and then
          Before.Value.Request in M.Queued | M.Intake,
        when M.Request_Lost_Event => Before.Present and then
          Before.Value.Kind = M.Request and then Before.Value.Request = M.Intake,
        when others => False)
   with Global => null;

   function Descriptor_From_Clause
     (Before : Optional_Subject; Kind : M.Event_Kind) return Boolean is
     (case Kind is
        when M.Drain_Stop_Intent_Event => not Before.Present or else
          (Before.Value.Kind = M.Descriptor and then Before.Value.Descriptor = M.Front_Held),
        when M.Drain_Freeze_Event => Before.Present and then
          Before.Value.Kind = M.Descriptor and then Before.Value.Descriptor = M.Stop_Intent,
        when M.Drain_Ofd_Evidence_Event => Before.Present and then
          Before.Value.Kind = M.Descriptor and then Before.Value.Descriptor = M.Frozen,
        when M.Drain_Intake_Event => Before.Present and then
          Before.Value.Kind = M.Descriptor and then Before.Value.Descriptor = M.Ofd_Evidence,
        when M.Drain_Abandon_Event => Before.Present and then
          Before.Value.Kind = M.Descriptor and then Before.Value.Descriptor in
            M.Stop_Intent | M.Frozen | M.Ofd_Evidence,
        when M.Drain_Released_Event => Before.Present and then
          Before.Value.Kind = M.Descriptor and then Before.Value.Descriptor = M.Intake,
        when M.Drain_Reclaimed_Event => Before.Present and then
          Before.Value.Kind = M.Descriptor and then Before.Value.Descriptor in M.Intake | M.Released,
        when others => False)
   with Global => null;

   function Request_Fixed_Actor_Clause
     (Before : Optional_Subject; Kind : M.Event_Kind; Caller : M.Actor)
      return Boolean is
     (case Kind is
        when M.Request_Queued_Event | M.Request_Transfer_Intent_Event => Caller = M.Front,
        when M.Request_Intake_Event => Caller = M.Worker,
        when M.Request_Abandon_Event => Caller in M.Front | M.Reconciler,
        when M.Request_Lost_Event => Caller = M.Collector,
        when M.Request_Responded_Event => Before.Present and then
          (if Before.Value.Request = M.Queued then Caller = M.Front
           elsif Before.Value.Request = M.Intake then Caller = M.Worker
           else False),
        when others => False)
   with Global => null;

   function Descriptor_Fixed_Actor_Clause
     (Kind : M.Event_Kind; Caller : M.Actor) return Boolean is
     (case Kind is
        when M.Drain_Stop_Intent_Event | M.Drain_Freeze_Event |
             M.Drain_Ofd_Evidence_Event | M.Drain_Released_Event => Caller = M.Front,
        when M.Drain_Intake_Event => Caller = M.Worker,
        when M.Drain_Abandon_Event => Caller in M.Front | M.Reconciler,
        when M.Drain_Reclaimed_Event => Caller in M.Collector | M.Reconciler,
        when others => False)
   with Global => null;

   --  Total original case equation; original callable Pre remains below.
   function Original_Request_Target_Equation (Kind : M.Event_Kind) return M.Request_Phase is
     (case Kind is
        when M.Request_Queued_Event => M.Queued,
        when M.Request_Transfer_Intent_Event => M.Transfer_Intent,
        when M.Request_Intake_Event => M.Intake,
        when M.Request_Abandon_Event => M.Abandoned,
        when M.Request_Responded_Event => M.Responded,
        when M.Request_Lost_Event => M.Lost,
        when others => M.Queued)
   with Global => null;

   function Request_Target (Kind : M.Event_Kind) return M.Request_Phase is
     (Original_Request_Target_Equation (Kind))
   with Pre => Family (Kind) = Request_Transition,
        Global => null;

   --  Total original case equation; original callable Pre remains below.
   function Original_Descriptor_Target_Equation (Kind : M.Event_Kind) return M.Descriptor_Phase is
     (case Kind is
        when M.Drain_Stop_Intent_Event => M.Stop_Intent,
        when M.Drain_Freeze_Event => M.Frozen,
        when M.Drain_Ofd_Evidence_Event => M.Ofd_Evidence,
        when M.Drain_Intake_Event => M.Intake,
        when M.Drain_Abandon_Event => M.Front_Held,
        when M.Drain_Released_Event => M.Released,
        when M.Drain_Reclaimed_Event => M.Reclaimed,
        when others => M.Front_Held)
   with Global => null;

   function Descriptor_Target (Kind : M.Event_Kind) return M.Descriptor_Phase is
     (Original_Descriptor_Target_Equation (Kind))
   with Pre => Family (Kind) = Descriptor_Transition,
        Global => null;
   --  The original receiving code accepts progress before ORIGINAL_RESULT
   --  and while awaiting HANDLER_TERMINAL. This observes those positive paths;
   --  it is not a rejection policy for other future composed relation cases.
   function Original_Progress_Receiving_Window
     (State : M.Root_State) return Boolean is
     (State.Phase in M.Worker_Owned | M.Original_Result)
   with Global => null;

   function Single_Root_Image_Event (Kind : M.Event_Kind) return Boolean is
     (Family (Kind) in Root_Transition | Physical_Transition |
        Original_Progress_Observation and then
      Kind not in M.Handoff_Abort_Event | M.Worker_Reattached_Event |
        M.Front_Owned_Event | M.Unknown_Event)
   with Global => null;

   function Root_Target
     (Before : M.Root_State; Kind : M.Event_Kind) return M.Root_Phase is
     (case Kind is
        when M.Prepared_Event => M.Prepared,
        when M.Held_Event => M.Held,
        when M.Running_Event => M.Running,
        when M.Execution_Native_Event => M.Execution_Native,
        when M.Execution_Ack_Event => M.Execution_Ack,
        when M.Handoff_Intent_Event => M.Handoff_Intent,
        when M.Front_Close_Intent_Event => M.Front_Close_Intent,
        when M.Front_Closed_Event => M.Front_Closed,
        when M.Transfer_Sent_Event => M.Transfer_Sent,
        when M.Roster_Evidence_Event => M.Roster_Evidence,
        when M.Custody_Ack_Event => M.Worker_Owned,
        when M.Abandon_Event => M.Abandoned,
        when M.Front_Retained_Escrow_Event => M.Front_Retained_Escrow,
        when M.Original_Result_Event => M.Original_Result,
        when M.Handler_Terminal_Event => M.Handler_Terminal,
        when M.Worker_Relinquish_Event => M.Worker_Relinquish,
        when M.Custody_Returned_Event => M.Custody_Returned,
        when M.Historical_Settlement_Event => M.Historical_Settlement,
        when M.Front_Reconstruction_Event => M.Front_Reconstruction,
        when others => Before.Phase)
   with Pre => Single_Root_Image_Event (Kind), Global => null;

   --  Full component equality contract: unchanged components are preserved.
   --  The Pre selects an internal image fragment, not an authority admission.
   function Single_Root_Image
     (Before : M.Root_State; Event : M.Event_Record) return M.Root_State
   with Pre => Single_Root_Image_Event (Event.Kind),
     Global => null,
     Post => Single_Root_Image'Result =
       (Before with delta
          Phase => Root_Target (Before, Event.Kind),
          Operation => (if Event.Kind = M.Prepared_Event then Event.Operation
                        else Before.Operation),
          Head => Event.Event_Id,
          Owners_Open => (if Event.Kind = M.Front_Closed_Event then False
                          else Before.Owners_Open),
          Physical =>
            (Before.Physical with delta
               Launched => Before.Physical.Launched or Event.Kind = M.Held_Event,
               NS => Before.Physical.NS or Event.Kind = M.Closed_NS_Event,
               Outer => Before.Physical.Outer or Event.Kind = M.Closed_Outer_Event,
               Raw => Before.Physical.Raw or Event.Kind = M.Closed_Raw_Event,
               Witness => Before.Physical.Witness or Event.Kind = M.Closed_Witness_Event,
               Settled => Before.Physical.Settled or Event.Kind = M.Physical_Settled_Event));

   function Unknown_Image
     (Before : M.Root_State; Event : M.Event_Record; Cause_Digest : M.Digest)
      return M.Root_State is
     (Before with delta Phase => M.Unknown,
        Before_Unknown => (if Before.Phase = M.Unknown then Before.Before_Unknown
                           else Before.Phase),
        Unknown_Cause => (Present => True, Value => Cause_Digest), Head => Event.Event_Id)
   with Pre => Event.Kind = M.Unknown_Event,
        Global => null;

   function Reattached_Image
     (Before : M.Root_State; Event : M.Event_Record; Epoch : Q.Quantity)
      return M.Root_State is
     (Before with delta Reattach_Epoch => Epoch, Head => Event.Event_Id)
   with Pre => Event.Kind = M.Worker_Reattached_Event,
        Global => null;

   --  Numeric successor relation reuses the complete existing byte-domain
   --  implementation. Output-arena production and raw epoch binding stay open.
   function Reattach_Successor_Clause
     (Data : Q.Byte_Array; Before : M.Root_State; Epoch : Q.Quantity)
      return Boolean is (L.T.Is_Successor (Data, Before.Reattach_Epoch, Epoch))
   with Global => null;

   function Reconciled_Image
     (Before : M.Root_State; Event : M.Event_Record) return M.Root_State is
     (Before with delta Phase => Before.Before_Unknown, Head => Event.Event_Id)
   with Pre => Event.Kind = M.Reconciled_Event and then Before.Phase = M.Unknown,
        Global => null;

   --  This image preserves all resource flags. The separately committed
   --  Never_Dispatched Held_Capacity effect is NOT assumed or manufactured.
   function Abort_Phase_Image
     (Before : M.Root_State; Event : M.Event_Record; Abort_Kind : M.Abort_Class)
      return M.Root_State is
     (Before with delta Phase => M.Handoff_Aborted, Abort_Kind => Abort_Kind,
        Head => Event.Event_Id)
   with Pre => Event.Kind = M.Handoff_Abort_Event,
        Global => null;

   function Root_End_Image
     (Before : M.Root_State; Event : M.Event_Record) return M.Root_State is
     (Before with delta Phase => M.Ended, Head => Event.Event_Id)
   with Pre => Event.Kind = M.Front_Owned_Event,
        Global => null;

   function Request_Phase_Image
     (Before : M.Subject_State; Event : M.Event_Record) return M.Subject_State is
     (Before with delta Request => Request_Target (Event.Kind), Head => Event.Event_Id)
   with Pre => Family (Event.Kind) = Request_Transition,
        Global => null;

   function Descriptor_Phase_Image
     (Before : M.Subject_State; Event : M.Event_Record) return M.Subject_State is
     (Before with delta Descriptor => Descriptor_Target (Event.Kind), Head => Event.Event_Id)
   with Pre => Family (Event.Kind) = Descriptor_Transition,
        Global => null;
   function Replay_Matches
     (Data : Q.Byte_Array; Left, Right : M.Replay_Identity) return Boolean is
     (Q.Compare (Data, Left.Generation, Right.Generation) = Q.Equal and then
      L.Optional_Same (Data, Left.Operation, Right.Operation) and then
      Left.Kind_Of_Subject = Right.Kind_Of_Subject and then
      L.Optional_Same (Data, Left.Subject, Right.Subject) and then
      Q.Compare (Data, Left.Subgeneration, Right.Subgeneration) = Q.Equal and then
      Left.Kind = Right.Kind and then Left.Record_Digest = Right.Record_Digest)
   with Global => null;

   function Request_Subgeneration_Clause
     (Data : Q.Byte_Array; Before : Optional_Subject;
      Event : M.Event_Record) return Boolean is
     (Q.Span_Valid (Data, Event.Subgeneration) and then
      not Q.Is_Negative (Data, Event.Subgeneration) and then
      (if not Before.Present then
         Event.Kind = M.Request_Queued_Event and then Q.Is_Zero (Data, Event.Subgeneration)
       elsif Event.Kind = M.Request_Transfer_Intent_Event and then
             Before.Value.Request = M.Abandoned then
         L.T.Is_Successor (Data, Before.Value.Subgeneration, Event.Subgeneration)
       elsif Event.Kind = M.Request_Transfer_Intent_Event and then
             Before.Value.Request = M.Queued then
         Q.Is_Zero (Data, Event.Subgeneration)
       else Q.Compare (Data, Before.Value.Subgeneration, Event.Subgeneration) = Q.Equal))
   with Global => null;

   function Request_Transfer_Image
     (Before : M.Subject_State; Event : M.Event_Record;
      Mode : M.Transfer_Mode) return M.Subject_State is
     (Before with delta Request => M.Transfer_Intent,
        Subgeneration => Event.Subgeneration, Mode => Mode, Head => Event.Event_Id)
   with Pre => Event.Kind = M.Request_Transfer_Intent_Event,
        Global => null;

   function Descriptor_Abandon_Image
     (Before : M.Subject_State; Event : M.Event_Record;
      Next_Subgeneration : Q.Quantity) return M.Subject_State is
     (Before with delta Descriptor => M.Front_Held,
        Subgeneration => Next_Subgeneration, Head => Event.Event_Id)
   with Pre => Event.Kind = M.Drain_Abandon_Event,
        Global => null;

   function Descriptor_Abandon_Successor_Clause
     (Data : Q.Byte_Array; Before : M.Subject_State; Event : M.Event_Record;
      Next_Subgeneration : Q.Quantity) return Boolean is
     (Q.Compare (Data, Before.Subgeneration, Event.Subgeneration) = Q.Equal and then
      L.T.Is_Successor (Data, Before.Subgeneration, Next_Subgeneration))
   with Global => null;

   function Descriptor_Freeze_Image
     (Before : M.Subject_State; Event : M.Event_Record;
      Position : Q.Quantity) return M.Subject_State is
     (Before with delta Descriptor => M.Frozen,
        Position => (Present => True, Value => Position), Head => Event.Event_Id)
   with Pre => Event.Kind = M.Drain_Freeze_Event,
        Global => null;

   function New_Generation_Successor_Clause
     (Data : Q.Byte_Array; Before : M.Root_State; Event : M.Event_Record)
      return Boolean is
     (Event.Kind = M.Front_Owned_Event and then
      L.T.Is_Successor (Data, Before.Generation, Event.Generation))
   with Global => null;

   --  Only explicitly stated carry fields; full newly-created row defaults
   --  and per-request creation event identity remain an integration obligation.
   function Carried_Request_Fields_Image
     (Before : M.Subject_State; Event : M.Event_Record;
      Zero_Subgeneration : Q.Quantity) return M.Subject_State is
     (Before with delta Generation => Event.Generation, Request => M.Queued,
        Subgeneration => Zero_Subgeneration, Carried_From =>
          (Present => True, Value => Before.Generation), Head => Event.Event_Id)
   with Pre => Event.Kind = M.Front_Owned_Event and then Before.Kind = M.Request
        and then Before.Request in M.Queued | M.Abandoned,
        Global => null;
end Worldline.Root_Custody_Phase_Values;

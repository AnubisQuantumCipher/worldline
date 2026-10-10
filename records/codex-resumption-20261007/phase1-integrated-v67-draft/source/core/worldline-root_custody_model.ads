with Resource_Quantities;
with Resource_Run_Ledger;

--  Additive source-only extraction of the state vocabulary carried by v8.
--  No wire representation, decoder, permission, transition or proof claim.
--  Termination remains REQUIRED for every precondition-satisfying input:
--  these ordinary side-effect-free SPARK functions have the intrinsic
--  termination obligation documented by this toolchain's E0016. Explicit
--  per-function Always_Terminates is illegal here; no obligation is waived.
package Worldline.Root_Custody_Model with SPARK_Mode is
   package Q renames Resource_Quantities;
   package L renames Resource_Run_Ledger;

   subtype Identity is L.Identity;
   subtype Quantity is Q.Quantity;
   subtype Optional_Quantity is Q.Optional_Quantity;
   subtype Digest is Worldline.Hash;
   use type Worldline.Hash;

   --  Presence never depends on digest bytes. A present zero digest stays
   --  distinct from absence; meaningful equality requires both operands present.
   type Optional_Digest (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True  => Value : Digest;
      end case;
   end record;

   type Actor is (Front, Worker, Collector, Reconciler);
   type Owner is (Front, Worker, Collector, Reconciler, None);
   type Subject_Kind is (Root, Request, Descriptor);
   type Root_Phase is
     (Front_Owned, Prepared, Held, Running, Execution_Native, Execution_Ack,
      Handoff_Intent, Front_Close_Intent, Front_Closed, Transfer_Sent,
      Roster_Evidence, Worker_Owned, Original_Result, Handler_Terminal,
      Worker_Relinquish, Abandoned, Front_Retained_Escrow, Handoff_Aborted,
      Custody_Returned, Historical_Settlement, Front_Reconstruction,
      Ended, Unknown);
   type Abort_Class is (Never_Dispatched, Dispatched);
   type Request_Phase is
     (Queued, Transfer_Intent, Intake, Abandoned, Responded, Lost);
   type Descriptor_Phase is
     (Front_Held, Stop_Intent, Frozen, Ofd_Evidence, Intake, Abandoned,
      Released, Reclaimed);
   type Transfer_Mode is (None, Fresh, Relay);

   type Physical_Flags is record
      Launched, NS, Outer, Raw, Witness, Settled, Released_Unlaunched : Boolean;
   end record;

   type Root_State is record
      Generation     : Quantity;
      Operation      : Identity;
      Phase          : Root_Phase;
      Before_Unknown : Root_Phase;
      Owners_Open    : Boolean;
      --  The design's pseudocode field "Abort" is an Ada reserved word.
      --  Only the Ada component spelling changes, not the DDL/wire meaning.
      Abort_Kind     : Abort_Class;
      Physical       : Physical_Flags;
      Unknown_Cause  : Optional_Digest;
      Reattach_Epoch : Quantity;
      Head           : Digest;
   end record;

   type Subject_State is record
      Kind          : Subject_Kind;
      Generation    : Quantity;
      Subject       : Identity;
      Subgeneration : Quantity;
      Request       : Request_Phase;
      Descriptor    : Descriptor_Phase;
      Mode          : Transfer_Mode;
      Position      : Optional_Quantity;
      Carried_From  : Optional_Quantity;
      Head          : Digest;
   end record;

   --  The model keeps the full original records, including irrelevant inactive
   --  fields. Well-formedness and semantic byte equality belong to the native
   --  decoders/decisions. No predicate silently narrows their accepted domain.
   type Root_State_Array is array (Q.Byte_Index range <>) of Root_State;
   type Subject_State_Array is array (Q.Byte_Index range <>) of Subject_State;

   --  Exact event-name domain of the carried V5-J.2 DDL. Suffixes only avoid
   --  confusion with state literals. These enumeration positions are NOT ABI
   --  codes; the eventual decoder must implement the specified name relation.
   type Event_Kind is
     (Prepared_Event, Held_Event, Running_Event, Execution_Native_Event,
      Execution_Ack_Event, Handoff_Intent_Event, Front_Close_Intent_Event,
      Front_Closed_Event, Transfer_Sent_Event, Roster_Evidence_Event,
      Custody_Ack_Event, Abandon_Event, Front_Retained_Escrow_Event,
      Handoff_Abort_Event, Original_Progress_Event, Original_Result_Event,
      Handler_Terminal_Event, Worker_Relinquish_Event, Worker_Reattached_Event,
      Custody_Returned_Event, Closed_NS_Event, Closed_Outer_Event,
      Closed_Raw_Event, Closed_Witness_Event, Physical_Settled_Event,
      Historical_Settlement_Event, Front_Reconstruction_Event, Front_Owned_Event,
      Unknown_Event, Reconciled_Event, Request_Queued_Event,
      Request_Transfer_Intent_Event, Request_Intake_Event, Request_Abandon_Event,
      Request_Responded_Event, Request_Lost_Event, Drain_Stop_Intent_Event,
      Drain_Freeze_Event, Drain_Ofd_Evidence_Event, Drain_Intake_Event,
      Drain_Abandon_Event, Drain_Released_Event, Drain_Reclaimed_Event);

   --  V5-F.6 replay identity, including the record digest: no shortened key.
   type Replay_Identity is record
      Generation    : Quantity;
      Operation     : Identity;
      Kind_Of_Subject : Subject_Kind;
      Subject       : Identity;
      Subgeneration : Quantity;
      Kind          : Event_Kind;
      Record_Digest : Digest;
   end record;

   --  Complete X-5 EventRec semantic fields. Its native evidence roster
   --  remains a separate operand; this record does not authenticate itself.
   type Event_Record is record
      Kind            : Event_Kind;
      Generation      : Quantity;
      Operation       : Identity;
      Kind_Of_Subject : Subject_Kind;
      Subject         : Identity;
      Subgeneration   : Quantity;
      Appending_Actor : Actor;
      Record_Digest   : Digest;
      Event_Id        : Digest;
   end record;

   type Mutation is (M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11);
   type Mutation_Operand is record
      Calling_Actor   : Actor;
      Kind            : Mutation;
      Kind_Of_Subject : Subject_Kind;
      Subject         : Identity;
      Generation      : Quantity;
   end record;

   type Optional_Replay_Identity (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True  => Value : Replay_Identity;
      end case;
   end record;

   type Cause_Class is (C_Channel, C_Deadline, C_Append, C_Evidence);
   type Cause_Record (Class : Cause_Class := C_Evidence) is record
      --  Complete encoded cause bytes, in the caller-owned arena. This is
      --  retained even after decoding; neither Class nor Failed_Event is a
      --  producer-supplied authorization verdict. The eventual native decoder
      --  must join them to these bytes and hash them against Unknown_Cause.
      Encoded : Identity;
      case Class is
         when C_Append => Failed_Event : Replay_Identity;
         when others  => null;
      end case;
   end record;

   function Actor_Owner (Item : Actor) return Owner
   with Global => null,
     Post => Actor_Owner'Result =
       (case Item is
          when Front => Front,
          when Worker => Worker,
          when Collector => Collector,
          when Reconciler => Reconciler);

   function Is_Worker_Phase (Phase : Root_Phase) return Boolean
   with Global => null,
     Post => Is_Worker_Phase'Result =
       (Phase in Worker_Owned | Original_Result | Handler_Terminal |
          Worker_Relinquish);

   function Same_Present_Digest
     (Left, Right : Optional_Digest) return Boolean
   with Global => null,
     Post => Same_Present_Digest'Result =
       (Left.Present and then Right.Present and then Left.Value = Right.Value);

   function Failed_Append (Cause : Cause_Record)
      return Optional_Replay_Identity
   with Global => null,
     Post => Failed_Append'Result =
       (if Cause.Class = C_Append then
          (Present => True, Value => Cause.Failed_Event)
        else (Present => False));
end Worldline.Root_Custody_Model;

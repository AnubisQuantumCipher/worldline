with Worldline.Custody_V2_Load_Input;
with Worldline.Custody_V2_Fold_Engine;
package body Worldline.Custody_V2_Typed_Step with SPARK_Mode is
   use type Q.Byte;
   function Kind_Name (Kind : M.Event_Kind) return String is
     (case Kind is
        when M.Prepared_Event => "PREPARED",
        when M.Held_Event => "HELD",
        when M.Running_Event => "RUNNING",
        when M.Execution_Native_Event => "EXECUTION_NATIVE",
        when M.Execution_Ack_Event => "EXECUTION_ACK",
        when M.Handoff_Intent_Event => "HANDOFF_INTENT",
        when M.Front_Close_Intent_Event => "FRONT_CLOSE_INTENT",
        when M.Front_Closed_Event => "FRONT_CLOSED",
        when M.Transfer_Sent_Event => "TRANSFER_SENT",
        when M.Roster_Evidence_Event => "ROSTER_EVIDENCE",
        when M.Custody_Ack_Event => "CUSTODY_ACK",
        when M.Abandon_Event => "ABANDON",
        when M.Front_Retained_Escrow_Event => "FRONT_RETAINED_ESCROW",
        when M.Handoff_Abort_Event => "HANDOFF_ABORT",
        when M.Original_Progress_Event => "ORIGINAL_PROGRESS",
        when M.Original_Result_Event => "ORIGINAL_RESULT",
        when M.Handler_Terminal_Event => "HANDLER_TERMINAL",
        when M.Worker_Relinquish_Event => "WORKER_RELINQUISH",
        when M.Worker_Reattached_Event => "WORKER_REATTACHED",
        when M.Custody_Returned_Event => "CUSTODY_RETURNED",
        when M.Closed_NS_Event => "CLOSED_NS",
        when M.Closed_Outer_Event => "CLOSED_OUTER",
        when M.Closed_Raw_Event => "CLOSED_RAW",
        when M.Closed_Witness_Event => "CLOSED_WITNESS",
        when M.Physical_Settled_Event => "PHYSICAL_SETTLED",
        when M.Historical_Settlement_Event => "HISTORICAL_SETTLEMENT",
        when M.Front_Reconstruction_Event => "FRONT_RECONSTRUCTION",
        when M.Front_Owned_Event => "FRONT_OWNED",
        when M.Unknown_Event => "UNKNOWN",
        when M.Reconciled_Event => "RECONCILED",
        when M.Request_Queued_Event => "REQUEST_QUEUED",
        when M.Request_Transfer_Intent_Event => "REQUEST_TRANSFER_INTENT",
        when M.Request_Intake_Event => "REQUEST_INTAKE",
        when M.Request_Abandon_Event => "REQUEST_ABANDON",
        when M.Request_Responded_Event => "REQUEST_RESPONDED",
        when M.Request_Lost_Event => "REQUEST_LOST",
        when M.Drain_Stop_Intent_Event => "DRAIN_STOP_INTENT",
        when M.Drain_Freeze_Event => "DRAIN_FREEZE",
        when M.Drain_Ofd_Evidence_Event => "DRAIN_OFD_EVIDENCE",
        when M.Drain_Intake_Event => "DRAIN_INTAKE",
        when M.Drain_Abandon_Event => "DRAIN_ABANDON",
        when M.Drain_Released_Event => "DRAIN_RELEASED",
        when M.Drain_Reclaimed_Event => "DRAIN_RECLAIMED");
   function Literal (Data : C.E.Bytes; Item : C.E.Span; Text : String) return Boolean is
     (C.E.C.P.Valid (Data, Item) and then Item.Length = Text'Length and then
      (for all I in Text'Range => Data (Item.First + Q.Byte_Count (I - Text'First)) = Character'Pos (Text (I))));
   function Actor_Name (Actor : M.Actor) return String is
     (case Actor is
       when M.Front => "FRONT", when M.Worker => "WORKER",
       when M.Collector => "COLLECTOR", when M.Reconciler => "RECONCILER");
   function Subject_Name (Kind : M.Subject_Kind) return String is
     (case Kind is when M.Root => "ROOT", when M.Request => "REQUEST", when M.Descriptor => "DESCRIPTOR");
   function Decode (Data : C.E.Bytes; Raw : C.Event_Row) return Decoded_Event is
   begin
      if not C.Base_Matches (Data, Raw) then return (Status => Malformed_Row); end if;
      if not C.G.Origin_Matches (Data, Raw.Event_Id, C.G.Hash (Data, Raw.Base_Archive)) then
         return (Status => Malformed_Row);
      end if;
      for Kind in M.Event_Kind loop
         if Literal (Data, Raw.Kind, Kind_Name (Kind)) then
            for Actor in M.Actor loop
               if Literal (Data, Raw.Actor, Actor_Name (Actor)) then
                  for Subject in M.Subject_Kind loop
                     if Literal (Data, Raw.Subject_Kind, Subject_Name (Subject)) then
                        return (Status => Decoded, Value =>
                          (Kind => Kind,
                           Generation => (False, Raw.Generation.First, Raw.Generation.Length),
                           Operation => (Present => True, Value => (Raw.Operation.First, Raw.Operation.Length)),
                           Kind_Of_Subject => Subject,
                           Subject => (Present => True, Value => (Raw.Subject.First, Raw.Subject.Length)),
                           Subgeneration => (False, Raw.Subgeneration.First, Raw.Subgeneration.Length),
                           Appending_Actor => Actor,
                           Record_Digest => C.G.Hash (Data, Raw.Record_Archive),
                           Event_Id => C.G.Hash (Data, Raw.Base_Archive)));
                     end if;
                  end loop;
               end if;
            end loop;
         end if;
      end loop;
      return (Status => Malformed_Row);
   end Decode;
   procedure Apply_Abandon
     (Data : C.E.Bytes; Raw : C.Event_Row; Roots : in out M.Root_State_Array;
      Events : A.R.Retained_Events; Alternatives : A.Alternative_Rows;
      Expected : A.Expected_Root; Applied : out Boolean) is
      Item : constant Decoded_Event := Decode (Data, Raw);
   begin
      Applied := False;
      if Item.Status /= Decoded or else Item.Value.Kind /= M.Abandon_Event then return; end if;
      if A.Legal_Abandon (Data, Roots, Events, Alternatives, Expected, Item.Value) then
         Roots := A.Next_Abandon (Data, Roots, Events, Alternatives, Expected, Item.Value);
         Applied := True;
      end if;
   end Apply_Abandon;
   procedure Apply_Request_Abandon
     (Data : C.E.Bytes; Raw : C.Event_Row; Roots : in out M.Root_State_Array;
      Subjects : in out M.Subject_State_Array; Events : A.R.Retained_Events;
      Alternatives : A.Alternative_Rows; Root : A.Expected_Root;
      Expected : RA.Expected_Request; Applied : out Boolean) is
      Item : constant Decoded_Event := Decode (Data, Raw);
   begin
      Applied := False;
      if Item.Status /= Decoded or else Item.Value.Kind /= M.Request_Abandon_Event then return; end if;
      if RA.Legal (Data, Roots, Subjects, Events, Alternatives, Root, Expected, Item.Value) then
         RA.Apply_Next (Data, Roots, Subjects, Events, Alternatives, Root, Expected, Item.Value);
         Applied := True;
      end if;
   end Apply_Request_Abandon;
   function Fold_From_S0 (Data : C.E.Bytes) return Fold_Result is
      package I renames Worldline.Custody_V2_Load_Input;
      package Engine renames Worldline.Custody_V2_Fold_Engine;
      use type I.Decode_Status;
      use type Engine.Fold_Status;
      Size : constant I.Sizes := I.Counts (Data);
   begin
      if Size.Status /= I.Parsed then return (Native_Fold_Refused, 3, 0); end if;
      declare
         Value : I.Parsed_Input (Size.Arena, Size.Events, Size.Heads, Size.Roots,
                                Size.Subjects, Size.Alternatives, Size.Blobs);
      begin
         I.Decode (Data, Value);
         if Value.Status /= I.Parsed then return (Native_Fold_Refused, 3, 0); end if;
         declare
            Decision : constant Engine.Observation := Engine.Load_Decide (Value);
         begin
            return (Status => (if Decision.State = Engine.History_Folded
                               then Complete_Fold_And_Rows_Equal else Native_Fold_Refused),
                    Native_Status => Q.Byte_Count (Engine.Status'Pos (Decision.Reason)),
                    Position => Decision.Position);
         end;
      end;
   end Fold_From_S0;
end Worldline.Custody_V2_Typed_Step;

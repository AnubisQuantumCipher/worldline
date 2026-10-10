with Worldline.Custody_V2_Typed_Step;
package Worldline.Custody_V2_Raw_Next with SPARK_Mode is
   package D renames Worldline.Custody_V2_Typed_Step;
   package S renames D.F.S;
   package M renames D.M;
   package Q renames D.Q;
   package P renames D.A.P;
   package C renames D.C;
   use type M.Event_Kind;
   use type M.Root_Phase;
   use type M.Subject_Kind;
   use type M.Request_Phase;
   use type M.Descriptor_Phase;
   use type P.Event_Family;
   use type M.Abort_Class;
   use type S.Root_Columns;
   use type S.Subject_Columns;
   type Root_Names is array (M.Root_Phase) of S.SQL_Cell;
   type Request_Names is array (M.Request_Phase) of S.SQL_Cell;
   type Descriptor_Names is array (M.Descriptor_Phase) of S.SQL_Cell;
   type Abort_Names is array (M.Abort_Class) of S.SQL_Cell;
   type Mode_Names is array (M.Transfer_Mode) of S.SQL_Cell;
   type Symbols is record
      Root : Root_Names;
      Request : Request_Names;
      Descriptor : Descriptor_Names;
      Abort_Name : Abort_Names;
      Mode : Mode_Names;
      Zero, One, Zero_Magnitude, Empty_Text : S.SQL_Cell;
   end record;
   function Valid (Data : C.E.Bytes; Names : Symbols) return Boolean with Global => null;
   function Root_Phase_Image
     (Before : S.Root_Columns; Kind : M.Event_Kind; Names : Symbols)
      return S.SQL_Cell is
     (case Kind is
        when M.Prepared_Event => Names.Root (M.Prepared),
        when M.Held_Event => Names.Root (M.Held),
        when M.Running_Event => Names.Root (M.Running),
        when M.Execution_Native_Event => Names.Root (M.Execution_Native),
        when M.Execution_Ack_Event => Names.Root (M.Execution_Ack),
        when M.Handoff_Intent_Event => Names.Root (M.Handoff_Intent),
        when M.Front_Close_Intent_Event => Names.Root (M.Front_Close_Intent),
        when M.Front_Closed_Event => Names.Root (M.Front_Closed),
        when M.Transfer_Sent_Event => Names.Root (M.Transfer_Sent),
        when M.Roster_Evidence_Event => Names.Root (M.Roster_Evidence),
        when M.Custody_Ack_Event => Names.Root (M.Worker_Owned),
        when M.Abandon_Event => Names.Root (M.Abandoned),
        when M.Front_Retained_Escrow_Event => Names.Root (M.Front_Retained_Escrow),
        when M.Handoff_Abort_Event => Names.Root (M.Handoff_Aborted),
        when M.Original_Result_Event => Names.Root (M.Original_Result),
        when M.Handler_Terminal_Event => Names.Root (M.Handler_Terminal),
        when M.Worker_Relinquish_Event => Names.Root (M.Worker_Relinquish),
        when M.Custody_Returned_Event => Names.Root (M.Custody_Returned),
        when M.Historical_Settlement_Event => Names.Root (M.Historical_Settlement),
        when M.Front_Reconstruction_Event => Names.Root (M.Front_Reconstruction),
        when M.Front_Owned_Event => Names.Root (M.Ended),
        when M.Unknown_Event => Names.Root (M.Unknown),
        when M.Reconciled_Event => Before.Before_Unknown,
        when others => Before.Phase)
      with Global => null;
   -- Internal images only: caller must establish complete Legal from the
   -- authenticated prefix. Nullable SQL fields are not typed default values.
   function Root_Image
     (Data : C.E.Bytes; Before : S.Root_Columns; Kind : M.Event_Kind; Raw : C.Event_Row;
      Names : Symbols; Abort_Kind : M.Abort_Class; Epoch, Cause : S.SQL_Cell)
      return S.Root_Columns with Global => null,
      Pre => P.Family (Kind) not in P.Request_Transition | P.Descriptor_Transition,
      Post => Root_Image'Result =
        (Before with delta
          Phase => Root_Phase_Image (Before, Kind, Names),
          Operation => (if Kind = M.Prepared_Event then
            (Kind => S.SQL_Text, Bytes => (Raw.Operation.First, Raw.Operation.Length))
            else Before.Operation),
          Before_Unknown => (if Kind = M.Unknown_Event then
            (if S.Text_Is (Data, Before.Phase, "UNKNOWN") then Before.Before_Unknown else Before.Phase)
            elsif Kind in M.Reconciled_Event | M.Custody_Returned_Event then (Kind => S.SQL_Null)
            else Before.Before_Unknown),
          Owners_Open => (if Kind = M.Front_Closed_Event then Names.Zero else Before.Owners_Open),
          Abort_Kind => (if Kind = M.Handoff_Abort_Event then Names.Abort_Name (Abort_Kind) else Before.Abort_Kind),
          Launched => (if Kind = M.Held_Event then Names.One else Before.Launched),
          Closure_NS => (if Kind = M.Closed_NS_Event then Names.One else Before.Closure_NS),
          Closure_Outer => (if Kind = M.Closed_Outer_Event then Names.One else Before.Closure_Outer),
          Closure_Raw => (if Kind = M.Closed_Raw_Event then Names.One else Before.Closure_Raw),
          Witness => (if Kind = M.Closed_Witness_Event then Names.One else Before.Witness),
          Settled => (if Kind = M.Physical_Settled_Event then Names.One else Before.Settled),
          Released_Unlaunched => (if Kind = M.Handoff_Abort_Event and then Abort_Kind = M.Never_Dispatched
            then Names.One else Before.Released_Unlaunched),
          Unknown_Cause => (if Kind = M.Unknown_Event then Cause else Before.Unknown_Cause),
          Reattach_Epoch => (if Kind = M.Worker_Reattached_Event then Epoch else Before.Reattach_Epoch),
          Head_Event => (Kind => S.SQL_Text, Bytes => (Raw.Event_Id.First, Raw.Event_Id.Length)));
   function End_Image (Before : S.Root_Columns; Raw : C.Event_Row; Names : Symbols)
      return S.Root_Columns is
     (Before with delta Phase => Names.Root (M.Ended),
        Head_Event => (Kind => S.SQL_Text, Bytes => (Raw.Event_Id.First, Raw.Event_Id.Length)))
      with Global => null;
   function New_Generation (Raw : C.Event_Row; Names : Symbols)
      return S.Root_Columns is
     ((Generation => (Kind => S.SQL_Blob, Bytes => (Raw.Generation.First, Raw.Generation.Length)),
       Operation => Names.Empty_Text, Phase => Names.Root (M.Front_Owned),
       Before_Unknown => (Kind => S.SQL_Null), Owners_Open => Names.One,
       Abort_Kind => (Kind => S.SQL_Null), Launched => Names.Zero,
       Closure_NS => Names.Zero, Closure_Outer => Names.Zero, Closure_Raw => Names.Zero,
       Witness => Names.Zero, Settled => Names.Zero, Released_Unlaunched => Names.Zero,
       Unknown_Cause => (Kind => S.SQL_Null), Reattach_Epoch => Names.Zero_Magnitude,
       Head_Event => (Kind => S.SQL_Text, Bytes => (Raw.Event_Id.First, Raw.Event_Id.Length))))
      with Global => null;
   function New_Subject
     (Raw : C.Event_Row; Kind : M.Subject_Kind; Names : Symbols)
      return S.Subject_Columns is
     ((Generation => (Kind => S.SQL_Blob, Bytes => (Raw.Generation.First, Raw.Generation.Length)),
       Kind_Of_Subject => (Kind => S.SQL_Text, Bytes => (Raw.Subject_Kind.First, Raw.Subject_Kind.Length)),
       Subject => (Kind => S.SQL_Text, Bytes => (Raw.Subject.First, Raw.Subject.Length)),
       Subgeneration => (Kind => S.SQL_Blob, Bytes => (Raw.Subgeneration.First, Raw.Subgeneration.Length)),
       Phase => (if Kind = M.Request then Names.Request (M.Queued)
                 else Names.Descriptor (M.Stop_Intent)),
       Mode => Names.Mode (M.None), Position => (Kind => S.SQL_Null),
       Carried_From => (Kind => S.SQL_Null),
       Head_Event => (Kind => S.SQL_Text, Bytes => (Raw.Event_Id.First, Raw.Event_Id.Length))))
      with Global => null, Pre => Kind in M.Request | M.Descriptor;
   function Subject_Image
     (Before : S.Subject_Columns; Kind : M.Event_Kind; Raw : C.Event_Row;
      Names : Symbols; Mode : M.Transfer_Mode; Position, Next_Subgeneration : S.SQL_Cell)
      return S.Subject_Columns with Global => null,
      Pre => P.Family (Kind) in P.Request_Transition | P.Descriptor_Transition,
      Post => Subject_Image'Result =
        (Before with delta
          Phase => (if P.Family (Kind) = P.Request_Transition then
            Names.Request (P.Original_Request_Target_Equation (Kind)) else
            Names.Descriptor (P.Original_Descriptor_Target_Equation (Kind))),
          Subgeneration => (if Kind = M.Request_Transfer_Intent_Event then
            (Kind => S.SQL_Blob, Bytes => (Raw.Subgeneration.First, Raw.Subgeneration.Length))
            elsif Kind = M.Drain_Abandon_Event then Next_Subgeneration else Before.Subgeneration),
          Mode => (if Kind = M.Request_Transfer_Intent_Event then Names.Mode (Mode) else Before.Mode),
          Position => (if Kind = M.Drain_Freeze_Event then Position else Before.Position),
          Head_Event => (Kind => S.SQL_Text, Bytes => (Raw.Event_Id.First, Raw.Event_Id.Length)));
   function Carried_Image
     (Before : S.Subject_Columns; Raw : C.Event_Row; Names : Symbols)
      return S.Subject_Columns is
     (Before with delta Generation =>
        (Kind => S.SQL_Blob, Bytes => (Raw.Generation.First, Raw.Generation.Length)),
        Phase => Names.Request (M.Queued), Subgeneration => Names.Zero_Magnitude,
        Carried_From => Before.Generation,
        Head_Event => (Kind => S.SQL_Text, Bytes => (Raw.Event_Id.First, Raw.Event_Id.Length)))
      with Global => null;
end Worldline.Custody_V2_Raw_Next;

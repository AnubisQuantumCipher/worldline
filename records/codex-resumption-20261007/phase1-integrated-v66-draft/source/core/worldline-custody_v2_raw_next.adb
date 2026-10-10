package body Worldline.Custody_V2_Raw_Next with SPARK_Mode is
   use type S.SQL_Class;
   use type Q.Byte_Count;
   use type M.Abort_Class;
   function Valid (Data : C.E.Bytes; Names : Symbols) return Boolean is
     ((for all Phase in M.Root_Phase => S.Matches_Root_Phase (Data, Names.Root (Phase), Phase)) and then
      (for all Phase in M.Request_Phase => S.Matches_Request_Phase (Data, Names.Request (Phase), Phase)) and then
      (for all Phase in M.Descriptor_Phase => S.Matches_Descriptor_Phase (Data, Names.Descriptor (Phase), Phase)) and then
      (for all Kind in M.Abort_Class => S.Matches_Abort_Class (Data, Names.Abort_Name (Kind), Kind)) and then
      (for all Mode in M.Transfer_Mode => S.Matches_Transfer_Mode (Data, Names.Mode (Mode), Mode)) and then
      S.Bit_Cell (Data, Names.Zero) and then not S.Bit_Value (Data, Names.Zero) and then
      S.Bit_Cell (Data, Names.One) and then S.Bit_Value (Data, Names.One) and then
      S.Magnitude_Blob (Data, Names.Zero_Magnitude, False) and then
      Names.Zero_Magnitude.Bytes.Length = 0 and then
      S.Text_Cell (Data, Names.Empty_Text) and then Names.Empty_Text.Bytes.Length = 0);

   function Root_Image
     (Data : C.E.Bytes; Before : S.Root_Columns; Kind : M.Event_Kind; Raw : C.Event_Row;
      Names : Symbols; Abort_Kind : M.Abort_Class; Epoch, Cause : S.SQL_Cell)
      return S.Root_Columns
   is
      Phase : constant S.SQL_Cell := Root_Phase_Image (Before, Kind, Names);
   begin
      return (Before with delta
        Phase => Phase,
        Operation => (if Kind = M.Prepared_Event then
          (Kind => S.SQL_Text, Bytes => (Raw.Operation.First, Raw.Operation.Length)) else Before.Operation),
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
   end Root_Image;

   function Subject_Image
     (Before : S.Subject_Columns; Kind : M.Event_Kind; Raw : C.Event_Row;
      Names : Symbols; Mode : M.Transfer_Mode; Position, Next_Subgeneration : S.SQL_Cell)
      return S.Subject_Columns
   is
   begin
      return (Before with delta
        Phase => (if P.Family (Kind) = P.Request_Transition then
          Names.Request (P.Original_Request_Target_Equation (Kind)) else
          Names.Descriptor (P.Original_Descriptor_Target_Equation (Kind))),
        Subgeneration => (if Kind = M.Request_Transfer_Intent_Event then
          (Kind => S.SQL_Blob, Bytes => (Raw.Subgeneration.First, Raw.Subgeneration.Length))
          elsif Kind = M.Drain_Abandon_Event then Next_Subgeneration else Before.Subgeneration),
        Mode => (if Kind = M.Request_Transfer_Intent_Event then Names.Mode (Mode) else Before.Mode),
        Position => (if Kind = M.Drain_Freeze_Event then Position else Before.Position),
        Head_Event => (Kind => S.SQL_Text, Bytes => (Raw.Event_Id.First, Raw.Event_Id.Length)));
   end Subject_Image;
end Worldline.Custody_V2_Raw_Next;

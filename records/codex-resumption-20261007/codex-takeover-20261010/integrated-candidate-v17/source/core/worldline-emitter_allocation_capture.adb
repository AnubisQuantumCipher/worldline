package body Worldline.Emitter_Allocation_Capture with SPARK_Mode is
   procedure Capture
     (Input_View : not null access constant E.Bytes;
      Output : out E.Bytes; Result : out S.Output_Observation)
   is
      Snapshot : constant E.Bytes := Input_View.all;
   begin
      S.Next_Output (Snapshot, Output, Result);
   end Capture;
   procedure Replay_Capture
     (Input_View : not null access constant E.Bytes;
      Output : out E.Bytes; Result : out S.Output_Observation)
   is
      Snapshot : constant E.Bytes := Input_View.all;
   begin
      S.Replay_Output (Snapshot, Output, Result);
   end Replay_Capture;
   procedure Written_Capture
     (Input_View : not null access constant E.Bytes;
      Output : out E.Bytes; Result : out S.Output_Observation)
   is
      Snapshot : constant E.Bytes := Input_View.all;
   begin
      S.Written_Output (Snapshot, Output, Result);
   end Written_Capture;
   procedure Prefix_Capture
     (Input_View : not null access constant E.Bytes;
      Output : out E.Bytes; Result : out S.Output_Observation)
   is
      Snapshot : constant E.Bytes := Input_View.all;
   begin
      S.Prefix_Output (Snapshot, Output, Result);
   end Prefix_Capture;
end Worldline.Emitter_Allocation_Capture;

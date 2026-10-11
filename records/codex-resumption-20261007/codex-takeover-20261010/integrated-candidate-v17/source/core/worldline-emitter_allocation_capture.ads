with Worldline.Root_Output_Sequence;
package Worldline.Emitter_Allocation_Capture with SPARK_Mode is
   package S renames Worldline.Root_Output_Sequence;
   package E renames S.E;
   procedure Capture
     (Input_View : not null access constant E.Bytes;
      Output : out E.Bytes; Result : out S.Output_Observation)
     with Global => null;
   procedure Replay_Capture
     (Input_View : not null access constant E.Bytes;
      Output : out E.Bytes; Result : out S.Output_Observation)
     with Global => null;
   procedure Written_Capture
     (Input_View : not null access constant E.Bytes;
      Output : out E.Bytes; Result : out S.Output_Observation)
     with Global => null;
   procedure Prefix_Capture
     (Input_View : not null access constant E.Bytes;
      Output : out E.Bytes; Result : out S.Output_Observation)
     with Global => null;
end Worldline.Emitter_Allocation_Capture;

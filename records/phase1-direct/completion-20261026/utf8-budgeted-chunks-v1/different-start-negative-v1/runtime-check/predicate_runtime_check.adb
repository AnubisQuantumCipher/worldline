with Ada.Text_IO;
with Chunk_Predicate_Probe;
procedure Predicate_Runtime_Check is
   Output_Length : Natural := 0;
begin
   Chunk_Predicate_Probe.Replay ("A", Output_Length);
   Ada.Text_IO.Put_Line (Natural'Image (Output_Length));
end Predicate_Runtime_Check;

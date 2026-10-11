with Ada.Command_Line;
with Ada.Streams.Stream_IO;
with Ada.Text_IO;
with Worldline.Actor_Archive_Replay;
with Worldline.Custody_V2_Values;
procedure Actor_Archive_Controls is
   package A renames Worldline.Actor_Archive_Replay;
   package E renames A.E;
   package P renames Worldline.Custody_V2_Values;
   package IO renames Ada.Streams.Stream_IO;
   use type Ada.Streams.Stream_Element_Offset;
   use type E.Count;
   function Load (Path : String) return E.Bytes is
      File : IO.File_Type;
   begin
      IO.Open (File, IO.In_File, Path);
      declare
         Raw : Ada.Streams.Stream_Element_Array (1 .. Ada.Streams.Stream_Element_Offset (IO.Size (File)));
         Last : Ada.Streams.Stream_Element_Offset;
         Result : E.Bytes (1 .. E.Count (Raw'Length));
      begin
         IO.Read (File, Raw, Last);
         IO.Close (File);
         if Last /= Raw'Last then raise Ada.Streams.Stream_IO.End_Error; end if;
         for I in Result'Range loop
            Result (I) := E.Q.Byte (Raw (Raw'First + Ada.Streams.Stream_Element_Offset (I - Result'First)));
         end loop;
         return Result;
      end;
   end Load;
begin
   declare
      Mode : constant String := Ada.Command_Line.Argument (1);
      Data : constant E.Bytes := Load (Ada.Command_Line.Argument (2));
      Whole : constant E.Span := (Data'First, Data'Length);
   begin
      if Mode = "actor" then
         declare
            Result : constant A.Actor_Replay_Result := A.Reestablish_Actor_Observation (Data, Whole);
         begin
            Ada.Text_IO.Put_Line (A.R.Replay_State'Image (Result.State) & ":" & A.X.Status'Image (Result.Native_Status));
         end;
      elsif Mode = "actor-material" then
         declare
            Observation : constant E.Span := P.Record_Field (Data, Whole, "observation");
            Material : constant E.Span := P.Record_Field (Data, Whole, "material");
         begin
            Ada.Text_IO.Put_Line (Boolean'Image (A.R.Actor_Material_Matches (Data, Observation, Material)));
         end;
      else
         declare
            Kind : constant A.Boundary_Kind := A.Boundary_Kind'Value (Mode);
         begin
            Ada.Text_IO.Put_Line (Boolean'Image (A.Operation_Boundary_Matches
              (Data, P.Record_Field (Data, Whole, "material"),
               P.Record_Field (Data, Whole, "event"),
               P.Record_Field (Data, Whole, "context"), Kind)));
         end;
      end if;
   end;
end Actor_Archive_Controls;

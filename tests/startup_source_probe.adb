with Ada.Text_IO;
with Worldline.Startup_Source_Custody;

-- Ordinary fixed-fixture consumer of public native relations, not host evidence.
procedure Startup_Source_Probe is
   package C renames Worldline.Startup_Source_Custody;
   package E renames C.L.E;
   package S renames C.L.V.S;
   use type E.Count;
begin
   while not Ada.Text_IO.End_Of_File loop
      declare
         Input : constant String := Ada.Text_IO.Get_Line;
         Data : E.Bytes (1 .. E.Count (Input'Length));
      begin
         for I in Input'Range loop
            Data (E.Count (I - Input'First + 1)) := Character'Pos (Input (I));
         end loop;
         declare
            Whole : constant E.Span := (Data'First, Data'Length);
            Source : constant E.Span := S.Field (Data, Whole, "source");
            Path : constant E.Span := S.Field (Data, Whole, "path");
            Raw : constant E.Span := S.Field (Data, Whole, "raw");
         begin
            Ada.Text_IO.Put_Line
              (Boolean'Image (C.Role_Selected (Data, Source, Path, "DATA")) & " " &
               Boolean'Image (C.File_Corresponds (Data, Source, Path, Raw)) & " " &
               Boolean'Image (C.Image_Corresponds (Data, Source, Path, Raw)) & " " &
               Boolean'Image (C.Unselected_Path (Data, Source, Path)));
         end;
      end;
   end loop;
end Startup_Source_Probe;

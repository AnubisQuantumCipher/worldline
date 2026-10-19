with Ada.Text_IO;
with Worldline.Scoped_Capture_Projection;

--  Ordinary fixture consumer of the public relation, not a custody witness.
procedure Scoped_Capture_Probe is
   package P renames Worldline.Scoped_Capture_Projection;
   package E renames P.E;
   use type E.Count;
begin
   while not Ada.Text_IO.End_Of_File loop
      declare
         Input : constant String := Ada.Text_IO.Get_Line;
         Data : E.Bytes (1 .. E.Count (Input'Length));
      begin
         for I in Data'Range loop
            Data (I) := Character'Pos (Input (Input'First + Natural (I - 1)));
         end loop;
         declare
            Whole : constant E.Span := (Data'First, Data'Length);
            Maps : constant E.Span := P.Raw_Source_Field (Data, Whole, "maps");
            Inventory : constant E.Span := P.Raw_Source_Field (Data, Whole, "inventory");
         begin
            Ada.Text_IO.Put_Line (Boolean'Image (P.Maps_Match (Data, Maps, Inventory)));
         end;
      end;
   end loop;
end Scoped_Capture_Probe;

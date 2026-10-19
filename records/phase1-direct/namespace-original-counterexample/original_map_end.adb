with Ada.Text_IO;
with Worldline.Scoped_Capture_Namespace_Projection;
procedure Original_Map_End is
   package E renames Worldline.Scoped_Capture_Namespace_Projection.E;
   use type E.Count;
   use type E.Q.Byte;
   function Map_Line_End (Raw : E.Bytes; Start : E.Count) return E.Count is
      Finish : E.Count := Start;
   begin
      while Finish <= Raw'Last and then Raw (Finish) /= 10 loop Finish := Finish + 1; end loop;
      return Finish;
   end Map_Line_End;
   Raw : constant E.Bytes (E.Count'Last .. E.Count'Last) := [Character'Pos ('x')];
begin
   declare Answer : constant E.Count := Map_Line_End (Raw, Raw'First); begin
      Ada.Text_IO.Put_Line ("Unexpected return " & E.Count'Image (Answer));
      raise Program_Error with "original boundary defect did not reproduce";
   end;
exception
   when Constraint_Error =>
      Ada.Text_IO.Put_Line ("REPRODUCED original absolute-index scan Constraint_Error");
end Original_Map_End;

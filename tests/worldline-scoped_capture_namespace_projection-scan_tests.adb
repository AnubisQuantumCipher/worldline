with Ada.Text_IO;

-- Exact production private parsers, exercised through an Ada child unit.
-- Ordinary byte fixtures; these are not namespace or credential witnesses.
procedure Worldline.Scoped_Capture_Namespace_Projection.Scan_Tests is
   use SPARK.Big_Integers;
   LF : constant Character := Character'Val (10);
   TAB : constant Character := Character'Val (9);
   Overflow : constant Valid_Big_Integer := To_Big_Integer (65534);

   function Bytes (Text : String) return E.Bytes is
      Result : E.Bytes (1 .. E.Count (Text'Length));
   begin
      for I in Text'Range loop
         Result (E.Count (I - Text'First + 1)) := Character'Pos (Text (I));
      end loop;
      return Result;
   end Bytes;

   procedure Lines is
      Empty : constant E.Bytes (1 .. 0) := [others => 0];
      One : constant E.Bytes (E.Count'Last .. E.Count'Last) := [Character'Pos ('x')];
      Newline : constant E.Bytes (E.Count'Last .. E.Count'Last) := [10];
      Text : constant E.Bytes := Bytes ("a" & LF & "b");
   begin
      pragma Assert (Map_Line_End (Empty, 0) = 0);
      pragma Assert (Map_Line_End (One, 0) = One'Length);
      pragma Assert (Map_Line_End (Newline, 0) = 0);
      pragma Assert (Map_Line_End (Text, 0) = 1);
      pragma Assert (Map_Line_End (Text, 2) = Text'Length);
      pragma Assert (Map_Line_End (Text, Text'Length) = Text'Length);
   end Lines;

   procedure Maps is
      Raw : constant E.Bytes := Bytes ("7 99 1" & LF);
      Rebased : E.Bytes (E.Count'Last - (Raw'Length - 1) .. E.Count'Last);
   begin
      Rebased := Raw;
      pragma Assert (Map_Valid (Raw) and then Map_Valid (Rebased));
      pragma Assert (Map_Value (Raw, To_Big_Integer (7), Overflow) = To_Big_Integer (99));
      pragma Assert (Map_Value (Rebased, To_Big_Integer (7), Overflow) = To_Big_Integer (99));
      pragma Assert (Map_Value (Rebased, To_Big_Integer (6), Overflow) = Overflow);
      pragma Assert (not Map_Valid (Bytes ("7 99 1")));
      pragma Assert (not Map_Valid (Bytes ("7 99 0" & LF)));
      pragma Assert (not Map_Valid (Bytes ("-1 99 1" & LF)));
      pragma Assert (not Map_Valid (Bytes ("7 99 1 extra" & LF)));
      pragma Assert (not Map_Valid (Bytes ("7 99 1" & LF & "7 100 1" & LF)));
      pragma Assert (not Map_Valid (Bytes ("7 99 1" & LF & "8 99 1" & LF)));
      pragma Assert (Map_Valid (Bytes ("7 99 1" & LF & "8 100 1" & LF)));
      pragma Assert (not Map_Valid (Bytes ("4294967295 0 1" & LF)));
      pragma Assert (Map_Valid (Bytes ("")));
      pragma Assert (Map_Value (Bytes (""), To_Big_Integer (7), Overflow) = Overflow);
      pragma Assert (Map_Value (Bytes ("7 99 1"), To_Big_Integer (6), Overflow) = Overflow);
   end Maps;

   procedure PIDs is
   begin
      pragma Assert (Last_PID (Bytes ("NSpid:" & TAB & "17  3" & TAB & "2" & LF)) = To_Big_Integer (2));
      pragma Assert (Last_PID (Bytes ("NSpid: 17 3" & TAB & LF)) = To_Big_Integer (3));
      pragma Assert (Last_PID (Bytes ("NSpid: 17 0" & LF)) = To_Big_Integer (-1));
      pragma Assert (Last_PID (Bytes ("NSpid: 17 bad" & LF)) = To_Big_Integer (-1));
      pragma Assert (Last_PID (Bytes ("NSpid: " & TAB & LF)) = To_Big_Integer (-1));
      pragma Assert (Last_PID (Bytes ("Uid: 17" & LF)) = To_Big_Integer (-1));
   end PIDs;
begin
   Lines;
   Maps;
   PIDs;
   Ada.Text_IO.Put_Line ("PASS namespace scan line/map/PID controls");
end Worldline.Scoped_Capture_Namespace_Projection.Scan_Tests;

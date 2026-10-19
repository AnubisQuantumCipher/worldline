with Ada.Text_IO;
with Worldline.Scoped_Capture_Projection;

--  Actual public byte scanners with owned arrays, including the last legal
--  index. These controls do not establish authentic source or host custody.
procedure Scoped_Capture_Scan_Tests is
   package P renames Worldline.Scoped_Capture_Projection;
   package E renames P.E;
   use type E.Count;
   use type E.Bytes;
   LF : constant Character := Character'Val (10);
   HT : constant Character := Character'Val (9);

   function Bytes (Text : String) return E.Bytes is
      Result : E.Bytes (1 .. E.Count (Text'Length));
   begin
      for I in Result'Range loop
         Result (I) := Character'Pos (Text (Text'First + Natural (I - 1)));
      end loop;
      return Result;
   end Bytes;

   procedure Match (Raw : E.Bytes; Item : E.Span; Expected : String) is
   begin
      pragma Assert (E.C.P.Valid (Raw, Item));
      pragma Assert (Item.Length = E.Count (Expected'Length));
      if Item.Length > 0 then
         pragma Assert
           (Raw (Item.First .. Item.First + (Item.Length - 1)) = Bytes (Expected));
      end if;
   end Match;

   procedure Line_Case (Text, Name, Expected : String) is
      Raw : constant E.Bytes := Bytes (Text);
      Rebased : E.Bytes (E.Count'Last - E.Count (Text'Length) + 1 .. E.Count'Last);
   begin
      Rebased := Raw;
      Match (Raw, P.Line (Raw, Name, Character'Pos (':')), Expected);
      Match (Rebased, P.Line (Rebased, Name, Character'Pos (':')), Expected);
   end Line_Case;

   procedure Lines is
      One : constant E.Bytes (E.Count'Last .. E.Count'Last) :=
        [Character'Pos ('x')];
      Empty : constant E.Bytes (1 .. 0) := [];
   begin
      --  The old absolute-index loop raised before returning this no-match.
      Match (One, P.Line (One, "x", Character'Pos (':')), "");
      Match (Empty, P.Line (Empty, "Uid", Character'Pos (':')), "");
      Line_Case ("Uid: 17", "Uid", " 17");
      Line_Case ("Uid: 17" & LF, "Uid", " 17");
      Line_Case ("Gid: 2" & LF & "Uid:" & HT & "17 3", "Uid", HT & "17 3");
      Line_Case ("Uid:", "Uid", "");
      Line_Case ("Uid:" & LF, "Uid", "");
      Line_Case (LF & "UidX: 7" & LF, "Uid", "");
      Line_Case ("Uid: 1" & LF & "Uid: 2" & LF, "Uid", "");
      --  Preserve the existing empty-value/duplicate behavior exactly.
      Line_Case ("Uid:" & LF & "Uid: 2" & LF, "Uid", " 2");
      Line_Case (":value", "", "value");
   end Lines;

   procedure Words is
      Raw : constant E.Bytes := Bytes (HT & "alpha  beta" & HT);
      Rebased : E.Bytes (E.Count'Last - (Raw'Length - 1) .. E.Count'Last);
      Spaces : constant E.Bytes := Bytes (HT & "  " & LF);
      Empty : constant E.Bytes (1 .. 0) := [];
   begin
      Rebased := Raw;
      Match (Raw, P.Word (Raw, (Raw'First, Raw'Length), 1), "alpha");
      Match (Raw, P.Word (Raw, (Raw'First, Raw'Length), 2), "beta");
      Match (Rebased, P.Word (Rebased, (Rebased'First, Rebased'Length), 1), "alpha");
      Match (Rebased, P.Word (Rebased, (Rebased'First, Rebased'Length), 2), "beta");
      Match (Rebased, P.Word (Rebased, (Rebased'First, Rebased'Length), 3), "");
      Match (Rebased, P.Word (Rebased, (Rebased'First, Rebased'Length), Positive'Last), "");
      Match (Spaces, P.Word (Spaces, (Spaces'First, Spaces'Length), 1), "");
      Match (Empty, P.Word (Empty, (1, 0), 1), "");
      Match (Raw, P.Word (Raw, (Raw'First, Raw'Length + 1), 1), "");
   end Words;
begin
   Lines;
   Words;
   Ada.Text_IO.Put_Line ("PASS scoped capture line/word controls");
end Scoped_Capture_Scan_Tests;

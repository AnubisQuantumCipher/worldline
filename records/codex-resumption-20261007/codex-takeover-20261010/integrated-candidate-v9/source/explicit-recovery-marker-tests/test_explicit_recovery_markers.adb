with Worldline.Recovery;
procedure Test_Explicit_Recovery_Markers is
   package R renames Worldline.Recovery;
   use type R.Recovery_Action;
   Expected : constant R.Identity_Bytes (7 .. 7) := (7 => 0);
   Empty : constant R.Identity_Bytes (2 .. 1) := (others => 0);
   Missing : constant R.Optional_Marker (Present => False, Length => 0) :=
     (Present => False, Length => 0);
   Missing_With_Length : constant R.Optional_Marker
     (Present => False, Length => R.Byte_Count'Last) :=
     (Present => False, Length => R.Byte_Count'Last);
   Present : constant R.Optional_Marker (Present => True, Length => Expected'Length) :=
     (Present => True, Length => Expected'Length, Value => Expected);
   Present_Empty : constant R.Optional_Marker (Present => True, Length => Empty'Length) :=
     (Present => True, Length => Empty'Length, Value => Empty);
begin
   pragma Assert (not R.Matches (Expected, Missing));
   pragma Assert (not R.Matches (Expected, Missing_With_Length));
   pragma Assert (R.Matches (Expected, Present));
   pragma Assert (R.Matches (Empty, Present_Empty));
   pragma Assert (not R.Matches (Empty, Missing));
   pragma Assert (not R.Matches (Expected, Present_Empty));
   pragma Assert (R.Select_Action (Expected, Present, Missing) = R.Finish_Committed);
   pragma Assert (R.Select_Action (Expected, Missing, Present) = R.Abort_Prepared);
   pragma Assert (R.Select_Action (Expected, Present, Present) = R.Ambiguous);
   pragma Assert (R.Select_Action (Expected, Missing, Missing_With_Length) = R.Ambiguous);
   pragma Assert (R.Select_Action (Empty, Present_Empty, Missing) = R.Finish_Committed);
   pragma Assert (R.Select_Action (Empty, Missing_With_Length, Present_Empty) = R.Abort_Prepared);
end Test_Explicit_Recovery_Markers;

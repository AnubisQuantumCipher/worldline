package body Worldline.Startup_Admission_Owned with SPARK_Mode is
   package L renames P.L;
   use type E.Count;
   use type L.Decode_Status;
   use type P.Action;
   use type E.Q.Byte;
   function Text (Name : E.Bytes) return String is
      Result : String (1 .. Integer (Name'Length));
   begin
      for I in Result'Range loop Result (I) := Character'Val (Name (Name'First + E.Count (I - 1))); end loop;
      return Result;
   end Text;
   function Known_Name (Name : E.Bytes) return Boolean is
      Recovery : constant String := "recovery-full-journal";
      Reservations : constant String := "full-use-reservations";
   begin
      return (Name'Length = Recovery'Length and then
        (for all I in Recovery'Range => Name (Name'First + E.Count (I - Recovery'First)) = Character'Pos (Recovery (I)))) or else
        (Name'Length = Reservations'Length and then
        (for all I in Reservations'Range => Name (Name'First + E.Count (I - Reservations'First)) = Character'Pos (Reservations (I))));
   end Known_Name;
   function Runtime_Decide (Data, Name : E.Bytes) return Observation is
      Result : Observation;
   begin
      if not Known_Name (Name) then return Result; end if;
      declare Sizes : constant L.Sizes := L.Counts (Data);
              Word : constant String := Text (Name); begin
         if Sizes.Status /= L.Parsed then return Result; end if;
         declare Value : L.Parsed_Input (Sizes.Arena, Sizes.Events, Sizes.Heads,
             Sizes.Roots, Sizes.Subjects, Sizes.Alternatives, Sizes.Blobs); begin
            L.Decode (Data, Value);
            declare Native : constant P.Decision := P.Observe (Value, Word); begin
               return (Native.Status, Native.Position);
            end;
         end;
      end;
   end Runtime_Decide;
   function Owner_Decide (Data, Name : E.Bytes) return Observation is
      Result : Observation;
      Roster : constant E.Span := (Data'First, Data'Length);
   begin
      if not Known_Name (Name) then return Result; end if;
      declare Native : constant P.Decision := P.Observe_Owner (Data, Roster, Text (Name)); begin
         return (Native.Status, Native.Position);
      end;
   end Owner_Decide;
   function Runtime_Transition
     (Before, After, Name : E.Bytes; Before_Action, After_Action : E.Count) return Boolean is
   begin
      if not Known_Name (Name) or else Before_Action > P.Action'Pos (P.Action'Last) or else
         After_Action > P.Action'Pos (P.Action'Last) then return False; end if;
      declare B : constant L.Sizes := L.Counts (Before);
              A : constant L.Sizes := L.Counts (After); begin
         if B.Status /= L.Parsed or else A.Status /= L.Parsed then return False; end if;
         declare BV : L.Parsed_Input (B.Arena, B.Events, B.Heads, B.Roots, B.Subjects, B.Alternatives, B.Blobs);
                 AV : L.Parsed_Input (A.Arena, A.Events, A.Heads, A.Roots, A.Subjects, A.Alternatives, A.Blobs); begin
            L.Decode (Before, BV); L.Decode (After, AV);
            return P.Transition_Matches (BV, AV, Text (Name), P.Action'Val (Before_Action), P.Action'Val (After_Action));
         end;
      end;
   end Runtime_Transition;
   function Owner_Transition
     (Before, After, Name : E.Bytes; Before_Action, After_Action : E.Count) return Boolean is
   begin
      if not Known_Name (Name) or else
         Before_Action > P.Action'Pos (P.Action'Last) or else After_Action > P.Action'Pos (P.Action'Last) then return False; end if;
      return P.Owner_Transition_Matches (Before, After, (Before'First, Before'Length),
        (After'First, After'Length), Text (Name), P.Action'Val (Before_Action), P.Action'Val (After_Action));
   end Owner_Transition;
end Worldline.Startup_Admission_Owned;

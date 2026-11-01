package body Resource_Reservation_Lifecycle with SPARK_Mode is
   procedure Plan
     (Data : Byte_Array; Rows : Entry_Array;
      Requested : Optional_Identity; Mode : Operation;
      Removed : in out Removal_Array; Status : out Result_Status)
   is
      Found : Boolean := False;
   begin
      Status := Invalid_Input;
      if not Inputs_Valid (Data, Rows, Requested, Mode) then
         return;
      end if;
      Status := Invalid_Output_Layout;
      if Removed'Length /= Rows'Length then
         return;
      end if;
      for I in Rows'Range loop
         pragma Loop_Invariant
           (for all J in Rows'Range =>
              (if J < I then
                 Removed (Removed'First + (J - Rows'First)) =
                   Remove_Row (Data, Rows (J), Requested, Mode)));
         pragma Loop_Invariant
           (Found = (for some J in Rows'Range =>
              J < I and then Remove_Row (Data, Rows (J), Requested, Mode)));
         declare
            Drop : constant Boolean := Remove_Row
              (Data, Rows (I), Requested, Mode);
         begin
            Removed (Removed'First + (I - Rows'First)) := Drop;
            Found := Found or Drop;
         end;
      end loop;
      Status := (if Found then Removal_Planned else No_Change);
   end Plan;
end Resource_Reservation_Lifecycle;

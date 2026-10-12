package body Worldline.Root_Custody_Descriptor with SPARK_Mode is
   function Project_Descriptor
     (Data : Q.Byte_Array; Roots : M.Root_State_Array;
      Subjects : M.Subject_State_Array; Reference : Descriptor_Reference)
      return Descriptor_Projection
   is
      Result : Descriptor_Projection := (Status => Binding_Not_Established);
   begin
      if C.Physical_Actor (Data, Roots, Reference.Original_Root).Status /=
        C.Physical_Projected
      then
         return Result;
      end if;
      for I in Subjects'Range loop
         if Subject_Key_Joined (Data, Subjects (I), Reference) then
            if not Subject_Joined (Data, Subjects (I), Reference) then
               return (Status => Binding_Not_Established);
            end if;
            if Result.Status = Projected then
               return (Status => Binding_Not_Established);
            end if;
            Result :=
              (Status => Projected, Index => I,
               Read_Actor =>
                 (case Subjects (I).Descriptor is
                    when M.Front_Held | M.Stop_Intent => Front_Reader,
                    when M.Intake | M.Released => Worker_Reader,
                    when M.Reclaimed => Collector_Or_Reconciler_Reader,
                    when M.Frozen | M.Ofd_Evidence | M.Abandoned => No_Reader),
               Write_Phase =>
                 (case Subjects (I).Descriptor is
                    when M.Front_Held => Front_Writer,
                    when M.Intake | M.Released => Worker_Writer,
                    when M.Stop_Intent | M.Frozen | M.Ofd_Evidence |
                         M.Abandoned | M.Reclaimed => No_Writer));
         end if;
         --  The complete processed prefix either contains no matching key,
         --  or contains exactly the selected full match. No bounded counter
         --  or shortened identity is used; duplicate keys return above.
         pragma Loop_Invariant
           (if Result.Status = Binding_Not_Established then
               (for all J in Subjects'First .. I =>
                  not Subject_Key_Joined (Data, Subjects (J), Reference))
            else
               Result.Index in Subjects'First .. I and then
               Subject_Joined (Data, Subjects (Result.Index), Reference)
               and then
               (for all J in Subjects'First .. I =>
                  (if J /= Result.Index then
                     not Subject_Key_Joined (Data, Subjects (J), Reference))));
         pragma Loop_Invariant
           (if Result.Status = Projected then
               Result.Read_Actor =
                 (case Subjects (Result.Index).Descriptor is
                    when M.Front_Held | M.Stop_Intent => Front_Reader,
                    when M.Intake | M.Released => Worker_Reader,
                    when M.Reclaimed => Collector_Or_Reconciler_Reader,
                    when M.Frozen | M.Ofd_Evidence | M.Abandoned => No_Reader)
               and then Result.Write_Phase =
                 (case Subjects (Result.Index).Descriptor is
                    when M.Front_Held => Front_Writer,
                    when M.Intake | M.Released => Worker_Writer,
                    when M.Stop_Intent | M.Frozen | M.Ofd_Evidence |
                         M.Abandoned | M.Reclaimed => No_Writer));
      end loop;
      return Result;
   end Project_Descriptor;
end Worldline.Root_Custody_Descriptor;

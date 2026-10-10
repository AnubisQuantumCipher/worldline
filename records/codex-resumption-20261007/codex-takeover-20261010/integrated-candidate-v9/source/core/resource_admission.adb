with SPARK.Big_Integers;

package body Resource_Admission with SPARK_Mode is
   use SPARK.Big_Integers;

   function Numeric_Rejection
     (Left_Value, Right_Value : Valid_Big_Integer;
      Relation : Rejection_Relation) return Boolean is
   begin
      case Relation is
         when At_Least =>
            return Left_Value >= Right_Value;
         when Above =>
            return Left_Value > Right_Value;
         when Below =>
            return Left_Value < Right_Value;
      end case;
   end Numeric_Rejection;

   function Binary_Reference
     (Data : Byte_Array; Left, Right : Quantity;
      Relation : Rejection_Relation; Left_Field, Right_Field : Quantity_Field)
      return Gate_Result is
   begin
      if not Span_Valid (Data, Left) then
         return (Invalid_Representation, Left_Field);
      elsif not Span_Valid (Data, Right) then
         return (Invalid_Representation, Right_Field);
      end if;
      --  Named controlled values retain their complete lexical lifetime during
      --  each comparison under the checked native build. The exact mathematical
      --  comparisons, malformed-span order and returned constructors are unchanged.
      declare
         Left_Value  : constant Valid_Big_Integer := Value (Data, Left);
         Right_Value : constant Valid_Big_Integer := Value (Data, Right);
      begin
         case Relation is
            when At_Least =>
               if Left_Value >= Right_Value then
                  return Refused;
               end if;
            when Above =>
               if Left_Value > Right_Value then
                  return Refused;
               end if;
            when Below =>
               if Left_Value < Right_Value then
                  return Refused;
               end if;
         end case;
      end;
      return Pass;
   end Binary_Reference;

   function Concurrency_Reference
     (Data : Byte_Array; P : Policy_Input) return Gate_Result is
   begin
      if not P.Concurrency_Limit.Present then
         return Pass;
      end if;
      return Binary_Reference
        (Data, P.Outstanding_Count, P.Concurrency_Limit.Value, At_Least,
         Outstanding_Count_Field, Concurrency_Limit_Field);
   end Concurrency_Reference;

   function Pressure_Reference
     (Data : Byte_Array; P : Policy_Input) return Gate_Result is
   begin
      if not P.Memory_Pressure.Present then
         return Pass;
      end if;
      return Binary_Reference
        (Data, P.Memory_Pressure.Value, P.Memory_Pressure_Ceiling, Above,
         Memory_Pressure_Field, Memory_Pressure_Ceiling_Field);
   end Pressure_Reference;

   function Disk_Bytes_Reference
     (Data : Byte_Array; P : Policy_Input; D : Disk_Row) return Gate_Result is
   begin
      return Binary_Reference
        (Data, D.Free_Bytes, P.Disk_Byte_Floor, Below,
         Free_Bytes_Field, Disk_Byte_Floor_Field);
   end Disk_Bytes_Reference;

   function Disk_Inodes_Reference
     (Data : Byte_Array; P : Policy_Input; D : Disk_Row) return Gate_Result is
   begin
      return Binary_Reference
        (Data, D.Free_Inodes, P.Disk_Inode_Floor, Below,
         Free_Inodes_Field, Disk_Inode_Floor_Field);
   end Disk_Inodes_Reference;

   function Capacity_Reference
     (Data : Byte_Array; P : Policy_Input) return Gate_Result is
   begin
      if not Span_Valid (Data, P.Available_Memory) then
         return (Invalid_Representation, Available_Memory_Field);
      elsif not Span_Valid (Data, P.Withheld_Memory) then
         return (Invalid_Representation, Withheld_Memory_Field);
      elsif not Span_Valid (Data, P.Memory_Floor) then
         return (Invalid_Representation, Memory_Floor_Field);
      elsif not Span_Valid (Data, P.Requested_Memory) then
         return (Invalid_Representation, Requested_Memory_Field);
      elsif Value (Data, P.Withheld_Memory) < 0 then
         return (Negative_Debit, Withheld_Memory_Field);
      elsif Value (Data, P.Memory_Floor) < 0 then
         return (Negative_Debit, Memory_Floor_Field);
      elsif Value (Data, P.Requested_Memory) < 0 then
         return (Negative_Debit, Requested_Memory_Field);
      elsif Value (Data, P.Available_Memory) <
        Value (Data, P.Withheld_Memory) + Value (Data, P.Memory_Floor) +
        Value (Data, P.Requested_Memory)
      then
         return Refused;
      end if;
      return Pass;
   end Capacity_Reference;

   function Decision_Conforms
     (Data : Byte_Array; P : Policy_Input; Disks : Disk_Array; D : Decision)
      return Boolean is
   begin
      if Concurrency_Reference (Data, P) /= Pass then
         return D = At_Gate (Concurrency, Concurrency_Reference (Data, P));
      elsif Pressure_Reference (Data, P) /= Pass then
         return D = At_Gate (Pressure, Pressure_Reference (Data, P));
      elsif D.Disk.Present then
         return D.Disk.Value in Disks'Range and then
           (for all I in Disks'Range =>
              (if I < D.Disk.Value then
                 Disk_Bytes_Reference (Data, P, Disks (I)) = Pass and then
                 Disk_Inodes_Reference (Data, P, Disks (I)) = Pass)) and then
           (if Disk_Bytes_Reference (Data, P, Disks (D.Disk.Value)) /= Pass then
              D = At_Disk (Disk_Bytes, D.Disk.Value,
                Disk_Bytes_Reference (Data, P, Disks (D.Disk.Value)))
            else Disk_Inodes_Reference (Data, P, Disks (D.Disk.Value)) /= Pass
              and then D = At_Disk (Disk_Inodes, D.Disk.Value,
                Disk_Inodes_Reference (Data, P, Disks (D.Disk.Value))));
      else
         return
           (for all I in Disks'Range =>
              Disk_Bytes_Reference (Data, P, Disks (I)) = Pass and then
              Disk_Inodes_Reference (Data, P, Disks (I)) = Pass) and then
           (if Capacity_Reference (Data, P) = Pass then D = Admitted
            else D = At_Gate (Capacity, Capacity_Reference (Data, P)));
      end if;
   end Decision_Conforms;

   function Check_Binary
     (Data : Byte_Array; Left, Right : Quantity;
      Relation : Rejection_Relation; Left_Field, Right_Field : Quantity_Field)
      return Gate_Result
   is
      Order : Ordering;
   begin
      if not Span_Valid (Data, Left) then
         return (Invalid_Representation, Left_Field);
      elsif not Span_Valid (Data, Right) then
         return (Invalid_Representation, Right_Field);
      end if;
      Order := Compare (Data, Left, Right);
      --  Additive proof projection of the unchanged Compare contract.
      pragma Assert
        ((case Relation is
            when At_Least => Order = Equal or else Order = Greater,
            when Above => Order = Greater,
            when Below => Order = Less) =
         Numeric_Rejection
           (Value (Data, Left), Value (Data, Right), Relation));
      if (case Relation is
            when At_Least => Order = Equal or else Order = Greater,
            when Above => Order = Greater,
            when Below => Order = Less)
      then
         return Refused;
      end if;
      return Pass;
   end Check_Binary;

   function Check_Capacity
     (Data : Byte_Array; P : Policy_Input) return Gate_Result is
   begin
      if not Span_Valid (Data, P.Available_Memory) then
         return (Invalid_Representation, Available_Memory_Field);
      elsif not Span_Valid (Data, P.Withheld_Memory) then
         return (Invalid_Representation, Withheld_Memory_Field);
      elsif not Span_Valid (Data, P.Memory_Floor) then
         return (Invalid_Representation, Memory_Floor_Field);
      elsif not Span_Valid (Data, P.Requested_Memory) then
         return (Invalid_Representation, Requested_Memory_Field);
      elsif Is_Negative (Data, P.Withheld_Memory) then
         return (Negative_Debit, Withheld_Memory_Field);
      elsif Is_Negative (Data, P.Memory_Floor) then
         return (Negative_Debit, Memory_Floor_Field);
      elsif Is_Negative (Data, P.Requested_Memory) then
         return (Negative_Debit, Requested_Memory_Field);
      elsif Is_Negative (Data, P.Available_Memory) then
         return Refused;
      elsif not Capacity_Fits
        (Data, P.Available_Memory, P.Withheld_Memory,
         P.Memory_Floor, P.Requested_Memory)
      then
         return Refused;
      end if;
      return Pass;
   end Check_Capacity;

   function Admit
     (Data : Byte_Array; P : Policy_Input; Disks : Disk_Array) return Decision
   is
      R : Gate_Result;
   begin
      if P.Concurrency_Limit.Present then
         R := Check_Binary
           (Data, P.Outstanding_Count, P.Concurrency_Limit.Value, At_Least,
            Outstanding_Count_Field, Concurrency_Limit_Field);
         pragma Assert (R = Concurrency_Reference (Data, P));
         if R /= Pass then
            return At_Gate (Concurrency, R);
         end if;
      end if;
      pragma Assert (Concurrency_Reference (Data, P) = Pass);
      if P.Memory_Pressure.Present then
         R := Check_Binary
           (Data, P.Memory_Pressure.Value, P.Memory_Pressure_Ceiling, Above,
            Memory_Pressure_Field, Memory_Pressure_Ceiling_Field);
         pragma Assert (R = Pressure_Reference (Data, P));
         if R /= Pass then
            return At_Gate (Pressure, R);
         end if;
      end if;
      pragma Assert (Pressure_Reference (Data, P) = Pass);
      for I in Disks'Range loop
         pragma Loop_Invariant
           (Concurrency_Reference (Data, P) = Pass and then
            Pressure_Reference (Data, P) = Pass);
         pragma Loop_Invariant
           (for all J in Disks'Range =>
              (if J < I then
                 Disk_Bytes_Reference (Data, P, Disks (J)) = Pass and then
                 Disk_Inodes_Reference (Data, P, Disks (J)) = Pass));
         R := Check_Binary
           (Data, Disks (I).Free_Bytes, P.Disk_Byte_Floor, Below,
            Free_Bytes_Field, Disk_Byte_Floor_Field);
         pragma Assert (R = Disk_Bytes_Reference (Data, P, Disks (I)));
         if R /= Pass then
            return At_Disk (Disk_Bytes, I, R);
         end if;
         R := Check_Binary
           (Data, Disks (I).Free_Inodes, P.Disk_Inode_Floor, Below,
            Free_Inodes_Field, Disk_Inode_Floor_Field);
         pragma Assert (R = Disk_Inodes_Reference (Data, P, Disks (I)));
         if R /= Pass then
            return At_Disk (Disk_Inodes, I, R);
         end if;
         --  The processed current row joins the original strict prior prefix.
         pragma Assert
           (Concurrency_Reference (Data, P) = Pass and then
            Pressure_Reference (Data, P) = Pass);
         pragma Assert
           (for all J in Disks'Range =>
              (if J <= I then
                 Disk_Bytes_Reference (Data, P, Disks (J)) = Pass and then
                 Disk_Inodes_Reference (Data, P, Disks (J)) = Pass));
      end loop;
      pragma Assert
        (for all I in Disks'Range =>
           Disk_Bytes_Reference (Data, P, Disks (I)) = Pass and then
           Disk_Inodes_Reference (Data, P, Disks (I)) = Pass);
      R := Check_Capacity (Data, P);
      pragma Assert (R = Capacity_Reference (Data, P));
      if R /= Pass then
         return At_Gate (Capacity, R);
      end if;
      return Admitted;
   end Admit;
end Resource_Admission;

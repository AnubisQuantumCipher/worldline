with Resource_Quantities;
with SPARK.Big_Integers;

package Resource_Admission with SPARK_Mode is
   use Resource_Quantities;
   use type SPARK.Big_Integers.Big_Integer;

   type Disk_Row is record
      Free_Bytes  : Quantity;
      Free_Inodes : Quantity;
   end record;
   type Disk_Array is array (Byte_Index range <>) of Disk_Row;
   type Optional_Index (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True  => Value : Byte_Index;
      end case;
   end record;

   type Policy_Input is record
      Outstanding_Count       : Quantity;
      Concurrency_Limit       : Optional_Quantity;
      Memory_Pressure          : Optional_Quantity;
      Memory_Pressure_Ceiling  : Quantity;
      Disk_Byte_Floor          : Quantity;
      Disk_Inode_Floor         : Quantity;
      Available_Memory        : Quantity;
      Withheld_Memory          : Quantity;
      Memory_Floor            : Quantity;
      Requested_Memory        : Quantity;
   end record;

   type Quantity_Field is
     (No_Field, Outstanding_Count_Field, Concurrency_Limit_Field,
      Memory_Pressure_Field, Memory_Pressure_Ceiling_Field,
      Free_Bytes_Field, Disk_Byte_Floor_Field,
      Free_Inodes_Field, Disk_Inode_Floor_Field,
      Available_Memory_Field, Withheld_Memory_Field,
      Memory_Floor_Field, Requested_Memory_Field);
   type Check_Status is
     (Passed, Insufficient, Invalid_Representation, Negative_Debit);
   type Gate_Result is record
      Status : Check_Status;
      Field  : Quantity_Field;
   end record;
   Pass : constant Gate_Result := (Passed, No_Field);
   Refused : constant Gate_Result := (Insufficient, No_Field);

   type Gate is (No_Gate, Concurrency, Pressure, Disk_Bytes, Disk_Inodes, Capacity);
   type Decision is record
      Failed_Gate : Gate;
      Disk        : Optional_Index;
      Check       : Gate_Result;
   end record;
   Admitted : constant Decision :=
     (No_Gate, (Present => False), Pass);
   type Outcome_Kind is
     (Admission_Granted, Resources_Unavailable, Resource_State_Unknown);
   function Outcome (D : Decision) return Outcome_Kind is
     (if D = Admitted then Admission_Granted
      elsif D.Check.Status = Insufficient then Resources_Unavailable
      else Resource_State_Unknown);

   function At_Gate (G : Gate; R : Gate_Result) return Decision is
     ((Failed_Gate => G, Disk => (Present => False), Check => R));
   function At_Disk (G : Gate; I : Byte_Index; R : Gate_Result)
      return Decision is
     ((Failed_Gate => G, Disk => (Present => True, Value => I), Check => R));

   type Rejection_Relation is (At_Least, Above, Below);

   --  The arguments own their complete call lifetime, including the checked
   --  Post. Keep controlled mathematical values out of case-arm temporaries.
   --  This total helper states the entire numeric relation; its body and Post
   --  are mandatory proof obligations, not an imported comparison assumption.
   function Numeric_Rejection
     (Left_Value, Right_Value : SPARK.Big_Integers.Valid_Big_Integer;
      Relation : Rejection_Relation) return Boolean
   with Ghost, Global => null,
     Post => Numeric_Rejection'Result =
       (case Relation is
          when At_Least => Left_Value >= Right_Value,
          when Above => Left_Value > Right_Value,
          when Below => Left_Value < Right_Value);

   --  Independent numeric reference: comparisons use the exact signed value,
   --  never a producer assertion that a comparison already succeeded.
   function Binary_Reference
     (Data : Byte_Array; Left, Right : Quantity;
      Relation : Rejection_Relation; Left_Field, Right_Field : Quantity_Field)
      return Gate_Result
   with Ghost, Global => null,
     Post => Binary_Reference'Result =
       (if not Span_Valid (Data, Left) then
          (Invalid_Representation, Left_Field)
        elsif not Span_Valid (Data, Right) then
          (Invalid_Representation, Right_Field)
        elsif Numeric_Rejection
          (Value (Data, Left), Value (Data, Right), Relation)
        then Refused else Pass);

   function Concurrency_Reference
     (Data : Byte_Array; P : Policy_Input) return Gate_Result
   with Ghost, Global => null,
     Post => Concurrency_Reference'Result =
       (if not P.Concurrency_Limit.Present then Pass
        else Binary_Reference
          (Data, P.Outstanding_Count, P.Concurrency_Limit.Value, At_Least,
           Outstanding_Count_Field, Concurrency_Limit_Field));
   function Pressure_Reference
     (Data : Byte_Array; P : Policy_Input) return Gate_Result
   with Ghost, Global => null,
     Post => Pressure_Reference'Result =
       (if not P.Memory_Pressure.Present then Pass
        else Binary_Reference
          (Data, P.Memory_Pressure.Value, P.Memory_Pressure_Ceiling, Above,
           Memory_Pressure_Field, Memory_Pressure_Ceiling_Field));
   function Disk_Bytes_Reference
     (Data : Byte_Array; P : Policy_Input; D : Disk_Row) return Gate_Result
   with Ghost, Global => null,
     Post => Disk_Bytes_Reference'Result = Binary_Reference
       (Data, D.Free_Bytes, P.Disk_Byte_Floor, Below,
        Free_Bytes_Field, Disk_Byte_Floor_Field);
   function Disk_Inodes_Reference
     (Data : Byte_Array; P : Policy_Input; D : Disk_Row) return Gate_Result
   with Ghost, Global => null,
     Post => Disk_Inodes_Reference'Result = Binary_Reference
       (Data, D.Free_Inodes, P.Disk_Inode_Floor, Below,
        Free_Inodes_Field, Disk_Inode_Floor_Field);
   function Capacity_Reference
     (Data : Byte_Array; P : Policy_Input) return Gate_Result
   with Ghost, Global => null,
     Post => Capacity_Reference'Result =
       (if not Span_Valid (Data, P.Available_Memory) then
          (Invalid_Representation, Available_Memory_Field)
        elsif not Span_Valid (Data, P.Withheld_Memory) then
          (Invalid_Representation, Withheld_Memory_Field)
        elsif not Span_Valid (Data, P.Memory_Floor) then
          (Invalid_Representation, Memory_Floor_Field)
        elsif not Span_Valid (Data, P.Requested_Memory) then
          (Invalid_Representation, Requested_Memory_Field)
        elsif Value (Data, P.Withheld_Memory) < 0 then
          (Negative_Debit, Withheld_Memory_Field)
        elsif Value (Data, P.Memory_Floor) < 0 then
          (Negative_Debit, Memory_Floor_Field)
        elsif Value (Data, P.Requested_Memory) < 0 then
          (Negative_Debit, Requested_Memory_Field)
        elsif Value (Data, P.Available_Memory) <
          Value (Data, P.Withheld_Memory) + Value (Data, P.Memory_Floor) +
            Value (Data, P.Requested_Memory)
        then Refused else Pass);

   --  Complete first-failure relation. The disk index is the original ordered
   --  input index, not a sorted name or a newly filtered row number.
   function Decision_Conforms
     (Data : Byte_Array; P : Policy_Input; Disks : Disk_Array; D : Decision)
      return Boolean
   with Ghost, Global => null,
     Post => Decision_Conforms'Result =
       (if Concurrency_Reference (Data, P) /= Pass then
          D = At_Gate (Concurrency, Concurrency_Reference (Data, P))
        elsif Pressure_Reference (Data, P) /= Pass then
          D = At_Gate (Pressure, Pressure_Reference (Data, P))
        elsif D.Disk.Present then
          D.Disk.Value in Disks'Range and then
            (for all I in Disks'Range =>
               (if I < D.Disk.Value then
                  Disk_Bytes_Reference (Data, P, Disks (I)) = Pass and then
                  Disk_Inodes_Reference (Data, P, Disks (I)) = Pass)) and then
            (if Disk_Bytes_Reference (Data, P, Disks (D.Disk.Value)) /= Pass then
               D = At_Disk (Disk_Bytes, D.Disk.Value,
                 Disk_Bytes_Reference (Data, P, Disks (D.Disk.Value)))
             else Disk_Inodes_Reference (Data, P, Disks (D.Disk.Value)) /= Pass
               and then D = At_Disk (Disk_Inodes, D.Disk.Value,
                 Disk_Inodes_Reference (Data, P, Disks (D.Disk.Value))))
        else
          (for all I in Disks'Range =>
             Disk_Bytes_Reference (Data, P, Disks (I)) = Pass and then
             Disk_Inodes_Reference (Data, P, Disks (I)) = Pass) and then
          (if Capacity_Reference (Data, P) = Pass then D = Admitted
           else D = At_Gate (Capacity, Capacity_Reference (Data, P))));

   function Check_Binary
     (Data : Byte_Array; Left, Right : Quantity;
      Relation : Rejection_Relation; Left_Field, Right_Field : Quantity_Field)
      return Gate_Result
   with Global => null,
     Post => Check_Binary'Result = Binary_Reference
       (Data, Left, Right, Relation, Left_Field, Right_Field);

   function Check_Capacity
     (Data : Byte_Array; P : Policy_Input) return Gate_Result
   with Global => null,
     Post => Check_Capacity'Result = Capacity_Reference (Data, P);

   --  This is only the numeric admission stage. No reservation/observer/ledger
   --  effect is claimed. There is no Pre and no fixed whole-quantity cap.
   function Admit
     (Data : Byte_Array; P : Policy_Input; Disks : Disk_Array) return Decision
   with Global => null,
     Post => Decision_Conforms (Data, P, Disks, Admit'Result);
end Resource_Admission;

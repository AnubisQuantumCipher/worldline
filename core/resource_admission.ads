with Resource_Quantities;

package Resource_Admission with SPARK_Mode is
   use Resource_Quantities;

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

   --  Independent numeric reference: comparisons use the exact signed value,
   --  never a producer assertion that a comparison already succeeded.
   function Binary_Reference
     (Data : Byte_Array; Left, Right : Quantity;
      Relation : Rejection_Relation; Left_Field, Right_Field : Quantity_Field)
      return Gate_Result
   with Ghost, Global => null;

   function Concurrency_Reference
     (Data : Byte_Array; P : Policy_Input) return Gate_Result
   with Ghost, Global => null;
   function Pressure_Reference
     (Data : Byte_Array; P : Policy_Input) return Gate_Result
   with Ghost, Global => null;
   function Disk_Bytes_Reference
     (Data : Byte_Array; P : Policy_Input; D : Disk_Row) return Gate_Result
   with Ghost, Global => null;
   function Disk_Inodes_Reference
     (Data : Byte_Array; P : Policy_Input; D : Disk_Row) return Gate_Result
   with Ghost, Global => null;
   function Capacity_Reference
     (Data : Byte_Array; P : Policy_Input) return Gate_Result
   with Ghost, Global => null;

   --  Complete first-failure relation. The disk index is the original ordered
   --  input index, not a sorted name or a newly filtered row number.
   function Decision_Conforms
     (Data : Byte_Array; P : Policy_Input; Disks : Disk_Array; D : Decision)
      return Boolean
   with Ghost, Global => null;

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

with Worldline.Root_Custody_Model;

--  Lossless typed SQL-column operands. This is not raw SQLite/JSON decoding,
--  source authentication, fold equivalence, custody Legal or an ABI layout.
--  Ordinary pure SPARK functions retain intrinsic termination obligations.
package Worldline.Root_Custody_Row_Schema with SPARK_Mode is
   package M renames Worldline.Root_Custody_Model;
   package Q renames M.Q;
   use type Q.Byte_Count;
   use type Q.Byte;
   use type Q.Ordering;
   use type Q.Quantity;
   use type M.Root_Phase;
   use type M.Abort_Class;
   use type M.Request_Phase;
   use type M.Descriptor_Phase;
   use type M.Transfer_Mode;

   --  Unlike authority Identity, SQL TEXT may be present and empty. Never
   --  encode that value as absence merely to fit an Id_Valid helper.
   type Bytes_Span is record
      First : Q.Byte_Index;
      Length : Q.Byte_Count;
   end record;
   type SQL_Class is (SQL_Null, SQL_Integer, SQL_Text, SQL_Blob, SQL_Real);
   type SQL_Cell (Kind : SQL_Class := SQL_Null) is record
      case Kind is
         when SQL_Null => null;
         when SQL_Integer => Integer_Value : Q.Quantity;
         when SQL_Text | SQL_Blob | SQL_Real => Bytes : Bytes_Span;
      end case;
   end record;
   --  Real bytes are opaque source data; no root/subject column accepts Real.
   --  Their encoding is deliberately not invented here.

   type Root_Columns is record
      Generation, Operation, Phase, Before_Unknown, Owners_Open, Abort_Kind,
      Launched, Closure_NS, Closure_Outer, Closure_Raw, Witness, Settled,
      Released_Unlaunched, Unknown_Cause, Reattach_Epoch, Head_Event : SQL_Cell;
   end record;
   type Subject_Columns is record
      Generation, Kind_Of_Subject, Subject, Subgeneration, Phase, Mode,
      Position, Carried_From, Head_Event : SQL_Cell;
   end record;
   type Optional_Root_Row (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Columns : Root_Columns;
      end case;
   end record;
   type Optional_Subject_Row (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Columns : Subject_Columns;
      end case;
   end record;
   type Root_Rows is array (Q.Byte_Index range <>) of Optional_Root_Row;
   type Subject_Rows is array (Q.Byte_Index range <>) of Optional_Subject_Row;

   function Span_Valid (Data : Q.Byte_Array; Span : Bytes_Span) return Boolean is
     (Span.Length = 0 or else
      (Span.First in Data'Range and then Span.Length <= Data'Last - Span.First + 1))
   with Global => null;

   function Text_Is
     (Data : Q.Byte_Array; Cell : SQL_Cell; Value : String) return Boolean
   with Global => null,
     Post => Text_Is'Result =
       (Cell.Kind = SQL_Text and then Span_Valid (Data, Cell.Bytes) and then
        Cell.Bytes.Length = Value'Length and then
        (for all I in Value'Range =>
           Data (Cell.Bytes.First + Q.Byte_Count (I - Value'First)) =
             Q.Byte (Character'Pos (Value (I)))));

   function Same_Span
     (Data : Q.Byte_Array; Left, Right : Bytes_Span) return Boolean
   with Global => null,
     Post => Same_Span'Result =
       (Span_Valid (Data, Left) and then Span_Valid (Data, Right) and then
        Left.Length = Right.Length and then
        (if Left.Length > 0 then
           (for all Offset in Q.Byte_Count range 0 .. Left.Length - 1 =>
              Data (Left.First + Offset) = Data (Right.First + Offset))));

   function Same_Cell
     (Data : Q.Byte_Array; Left, Right : SQL_Cell) return Boolean is
     (Left.Kind = Right.Kind and then
      (case Left.Kind is
         when SQL_Null => True,
         when SQL_Integer =>
           Q.Compare (Data, Left.Integer_Value, Right.Integer_Value) = Q.Equal,
         when SQL_Text | SQL_Blob | SQL_Real =>
           Same_Span (Data, Left.Bytes, Right.Bytes)))
   with Global => null;

   --  Exact DDL magnitude shape, not a public integer-domain restriction.
   --  The existing general Quantity type still permits noncanonical spans.
   function Magnitude_Blob
     (Data : Q.Byte_Array; Cell : SQL_Cell; Positive : Boolean) return Boolean is
     (Cell.Kind = SQL_Blob and then Span_Valid (Data, Cell.Bytes) and then
      (if Cell.Bytes.Length = 0 then not Positive
       else Data (Cell.Bytes.First + (Cell.Bytes.Length - 1)) /= 0))
   with Global => null;

   function Nullable_Magnitude_Blob
     (Data : Q.Byte_Array; Cell : SQL_Cell; Positive : Boolean) return Boolean is
     (Cell.Kind = SQL_Null or else Magnitude_Blob (Data, Cell, Positive))
   with Global => null;

   function Blob_Quantity (Cell : SQL_Cell) return Q.Quantity is
     ((Negative => False, First => Cell.Bytes.First, Length => Cell.Bytes.Length))
   with Pre => Cell.Kind = SQL_Blob, Global => null;

   function Bit_Cell (Data : Q.Byte_Array; Cell : SQL_Cell) return Boolean is
     (Cell.Kind = SQL_Integer and then Q.Span_Valid (Data, Cell.Integer_Value)
      and then not Q.Is_Negative (Data, Cell.Integer_Value) and then
      (Q.Is_Zero (Data, Cell.Integer_Value) or else
         (Q.Digit (Data, Cell.Integer_Value, 0) = 1 and then
          (if Cell.Integer_Value.Length > 1 then
             (for all Offset in Q.Byte_Count range 1 .. Cell.Integer_Value.Length - 1 =>
                Q.Digit (Data, Cell.Integer_Value, Offset) = 0)))))
   with Global => null;

   function Bit_Value (Data : Q.Byte_Array; Cell : SQL_Cell) return Boolean is
     (not Q.Is_Zero (Data, Cell.Integer_Value))
   with Pre => Bit_Cell (Data, Cell), Global => null;

   type Optional_Root_Phase (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : M.Root_Phase;
      end case;
   end record;
   type Optional_Abort_Class (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : M.Abort_Class;
      end case;
   end record;
   type Subject_Row_Kind is (Request_Row, Descriptor_Row);
   type Subject_Phase (Kind : Subject_Row_Kind := Request_Row) is record
      case Kind is
         when Request_Row => Request : M.Request_Phase;
         when Descriptor_Row => Descriptor : M.Descriptor_Phase;
      end case;
   end record;

   --  Fully decoded column VIEW; Raw retains exact original lexical values.
   --  No inactive default root phase or abort class substitutes for SQL NULL.
   type Root_View is record
      Raw : Root_Columns;
      Generation : Q.Quantity;
      Operation : Bytes_Span;
      Phase : M.Root_Phase;
      Before_Unknown : Optional_Root_Phase;
      Owners_Open : Boolean;
      Abort_Kind : Optional_Abort_Class;
      Physical : M.Physical_Flags;
      Unknown_Cause : M.Optional_Digest;
      Reattach_Epoch : Q.Quantity;
      Head : M.Digest;
   end record;
   type Subject_View is record
      Raw : Subject_Columns;
      Generation : Q.Quantity;
      Subject : Bytes_Span;
      Subgeneration : Q.Quantity;
      Phase : Subject_Phase;
      Mode : M.Transfer_Mode;
      Position, Carried_From : Q.Optional_Quantity;
      Head : M.Digest;
   end record;

   --  The text decoders below preserve invalid/null input as the exact raw
   --  operand. A No_Exact_Name result is lexical only, never an authority
   --  refusal. SQL-null handling is separate from enum text recognition.
   type Name_Status is (Exact_Name, No_Exact_Name);
   type Root_Phase_Name (Status : Name_Status := No_Exact_Name) is record
      Raw : SQL_Cell;
      case Status is
         when Exact_Name => Value : M.Root_Phase;
         when No_Exact_Name => null;
      end case;
   end record;
   type Abort_Class_Name (Status : Name_Status := No_Exact_Name) is record
      Raw : SQL_Cell;
      case Status is
         when Exact_Name => Value : M.Abort_Class;
         when No_Exact_Name => null;
      end case;
   end record;
   type Request_Phase_Name (Status : Name_Status := No_Exact_Name) is record
      Raw : SQL_Cell;
      case Status is
         when Exact_Name => Value : M.Request_Phase;
         when No_Exact_Name => null;
      end case;
   end record;
   type Descriptor_Phase_Name (Status : Name_Status := No_Exact_Name) is record
      Raw : SQL_Cell;
      case Status is
         when Exact_Name => Value : M.Descriptor_Phase;
         when No_Exact_Name => null;
      end case;
   end record;
   type Transfer_Mode_Name (Status : Name_Status := No_Exact_Name) is record
      Raw : SQL_Cell;
      case Status is
         when Exact_Name => Value : M.Transfer_Mode;
         when No_Exact_Name => null;
      end case;
   end record;

   function Matches_Root_Phase
     (Data : Q.Byte_Array; Cell : SQL_Cell; Value : M.Root_Phase) return Boolean is
     (case Value is
        when M.Front_Owned => Text_Is (Data, Cell, "FRONT_OWNED"),
        when M.Prepared => Text_Is (Data, Cell, "PREPARED"),
        when M.Held => Text_Is (Data, Cell, "HELD"),
        when M.Running => Text_Is (Data, Cell, "RUNNING"),
        when M.Execution_Native => Text_Is (Data, Cell, "EXECUTION_NATIVE"),
        when M.Execution_Ack => Text_Is (Data, Cell, "EXECUTION_ACK"),
        when M.Handoff_Intent => Text_Is (Data, Cell, "HANDOFF_INTENT"),
        when M.Front_Close_Intent => Text_Is (Data, Cell, "FRONT_CLOSE_INTENT"),
        when M.Front_Closed => Text_Is (Data, Cell, "FRONT_CLOSED"),
        when M.Transfer_Sent => Text_Is (Data, Cell, "TRANSFER_SENT"),
        when M.Roster_Evidence => Text_Is (Data, Cell, "ROSTER_EVIDENCE"),
        when M.Worker_Owned => Text_Is (Data, Cell, "WORKER_OWNED"),
        when M.Original_Result => Text_Is (Data, Cell, "ORIGINAL_RESULT"),
        when M.Handler_Terminal => Text_Is (Data, Cell, "HANDLER_TERMINAL"),
        when M.Worker_Relinquish => Text_Is (Data, Cell, "WORKER_RELINQUISH"),
        when M.Abandoned => Text_Is (Data, Cell, "ABANDONED"),
        when M.Front_Retained_Escrow => Text_Is (Data, Cell, "FRONT_RETAINED_ESCROW"),
        when M.Handoff_Aborted => Text_Is (Data, Cell, "HANDOFF_ABORTED"),
        when M.Custody_Returned => Text_Is (Data, Cell, "CUSTODY_RETURNED"),
        when M.Historical_Settlement => Text_Is (Data, Cell, "HISTORICAL_SETTLEMENT"),
        when M.Front_Reconstruction => Text_Is (Data, Cell, "FRONT_RECONSTRUCTION"),
        when M.Ended => Text_Is (Data, Cell, "ENDED"),
        when M.Unknown => Text_Is (Data, Cell, "UNKNOWN"))
   with Global => null;

   function Read_Root_Phase_Name
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Root_Phase_Name
   with Global => null,
     Post => Read_Root_Phase_Name'Result.Raw = Cell and then
       (if (for some Value in M.Root_Phase => Matches_Root_Phase (Data, Cell, Value))
        then Read_Root_Phase_Name'Result.Status = Exact_Name and then
          Matches_Root_Phase (Data, Cell, Read_Root_Phase_Name'Result.Value)
        else Read_Root_Phase_Name'Result.Status = No_Exact_Name);

   function Matches_Abort_Class
     (Data : Q.Byte_Array; Cell : SQL_Cell; Value : M.Abort_Class) return Boolean is
     (case Value is
        when M.Never_Dispatched => Text_Is (Data, Cell, "NEVER_DISPATCHED"),
        when M.Dispatched => Text_Is (Data, Cell, "DISPATCHED"))
   with Global => null;

   function Read_Abort_Class_Name
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Abort_Class_Name
   with Global => null,
     Post => Read_Abort_Class_Name'Result.Raw = Cell and then
       (if (for some Value in M.Abort_Class => Matches_Abort_Class (Data, Cell, Value))
        then Read_Abort_Class_Name'Result.Status = Exact_Name and then
          Matches_Abort_Class (Data, Cell, Read_Abort_Class_Name'Result.Value)
        else Read_Abort_Class_Name'Result.Status = No_Exact_Name);

   function Matches_Request_Phase
     (Data : Q.Byte_Array; Cell : SQL_Cell; Value : M.Request_Phase) return Boolean is
     (case Value is
        when M.Queued => Text_Is (Data, Cell, "QUEUED"),
        when M.Transfer_Intent => Text_Is (Data, Cell, "TRANSFER_INTENT"),
        when M.Intake => Text_Is (Data, Cell, "INTAKE"),
        when M.Abandoned => Text_Is (Data, Cell, "ABANDONED"),
        when M.Responded => Text_Is (Data, Cell, "RESPONDED"),
        when M.Lost => Text_Is (Data, Cell, "LOST"))
   with Global => null;

   function Read_Request_Phase_Name
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Request_Phase_Name
   with Global => null,
     Post => Read_Request_Phase_Name'Result.Raw = Cell and then
       (if (for some Value in M.Request_Phase => Matches_Request_Phase (Data, Cell, Value))
        then Read_Request_Phase_Name'Result.Status = Exact_Name and then
          Matches_Request_Phase (Data, Cell, Read_Request_Phase_Name'Result.Value)
        else Read_Request_Phase_Name'Result.Status = No_Exact_Name);

   function Matches_Descriptor_Phase
     (Data : Q.Byte_Array; Cell : SQL_Cell; Value : M.Descriptor_Phase) return Boolean is
     (case Value is
        when M.Front_Held => Text_Is (Data, Cell, "FRONT_HELD"),
        when M.Stop_Intent => Text_Is (Data, Cell, "STOP_INTENT"),
        when M.Frozen => Text_Is (Data, Cell, "FROZEN"),
        when M.Ofd_Evidence => Text_Is (Data, Cell, "OFD_EVIDENCE"),
        when M.Intake => Text_Is (Data, Cell, "INTAKE"),
        when M.Abandoned => Text_Is (Data, Cell, "ABANDONED"),
        when M.Released => Text_Is (Data, Cell, "RELEASED"),
        when M.Reclaimed => Text_Is (Data, Cell, "RECLAIMED"))
   with Global => null;

   function Read_Descriptor_Phase_Name
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Descriptor_Phase_Name
   with Global => null,
     Post => Read_Descriptor_Phase_Name'Result.Raw = Cell and then
       (if (for some Value in M.Descriptor_Phase => Matches_Descriptor_Phase (Data, Cell, Value))
        then Read_Descriptor_Phase_Name'Result.Status = Exact_Name and then
          Matches_Descriptor_Phase (Data, Cell, Read_Descriptor_Phase_Name'Result.Value)
        else Read_Descriptor_Phase_Name'Result.Status = No_Exact_Name);

   function Matches_Transfer_Mode
     (Data : Q.Byte_Array; Cell : SQL_Cell; Value : M.Transfer_Mode) return Boolean is
     (case Value is
        when M.None => Text_Is (Data, Cell, "NONE"),
        when M.Fresh => Text_Is (Data, Cell, "FRESH"),
        when M.Relay => Text_Is (Data, Cell, "RELAY"))
   with Global => null;

   function Read_Transfer_Mode_Name
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Transfer_Mode_Name
   with Global => null,
     Post => Read_Transfer_Mode_Name'Result.Raw = Cell and then
       (if (for some Value in M.Transfer_Mode => Matches_Transfer_Mode (Data, Cell, Value))
        then Read_Transfer_Mode_Name'Result.Status = Exact_Name and then
          Matches_Transfer_Mode (Data, Cell, Read_Transfer_Mode_Name'Result.Value)
        else Read_Transfer_Mode_Name'Result.Status = No_Exact_Name);

   function Same_Root_Columns
     (Data : Q.Byte_Array; Left, Right : Root_Columns) return Boolean is
     (Same_Cell (Data, Left.Generation, Right.Generation) and then
      Same_Cell (Data, Left.Operation, Right.Operation) and then
      Same_Cell (Data, Left.Phase, Right.Phase) and then
      Same_Cell (Data, Left.Before_Unknown, Right.Before_Unknown) and then
      Same_Cell (Data, Left.Owners_Open, Right.Owners_Open) and then
      Same_Cell (Data, Left.Abort_Kind, Right.Abort_Kind) and then
      Same_Cell (Data, Left.Launched, Right.Launched) and then
      Same_Cell (Data, Left.Closure_NS, Right.Closure_NS) and then
      Same_Cell (Data, Left.Closure_Outer, Right.Closure_Outer) and then
      Same_Cell (Data, Left.Closure_Raw, Right.Closure_Raw) and then
      Same_Cell (Data, Left.Witness, Right.Witness) and then
      Same_Cell (Data, Left.Settled, Right.Settled) and then
      Same_Cell (Data, Left.Released_Unlaunched, Right.Released_Unlaunched) and then
      Same_Cell (Data, Left.Unknown_Cause, Right.Unknown_Cause) and then
      Same_Cell (Data, Left.Reattach_Epoch, Right.Reattach_Epoch) and then
      Same_Cell (Data, Left.Head_Event, Right.Head_Event))
   with Global => null;

   function Same_Subject_Columns
     (Data : Q.Byte_Array; Left, Right : Subject_Columns) return Boolean is
     (Same_Cell (Data, Left.Generation, Right.Generation) and then
      Same_Cell (Data, Left.Kind_Of_Subject, Right.Kind_Of_Subject) and then
      Same_Cell (Data, Left.Subject, Right.Subject) and then
      Same_Cell (Data, Left.Subgeneration, Right.Subgeneration) and then
      Same_Cell (Data, Left.Phase, Right.Phase) and then
      Same_Cell (Data, Left.Mode, Right.Mode) and then
      Same_Cell (Data, Left.Position, Right.Position) and then
      Same_Cell (Data, Left.Carried_From, Right.Carried_From) and then
      Same_Cell (Data, Left.Head_Event, Right.Head_Event))
   with Global => null;

   type Nullable_Column_State is (Null_Column, Value_Column, Invalid_Column);
   type Root_Phase_Column (State : Nullable_Column_State := Null_Column) is record
      Raw : SQL_Cell;
      case State is
         when Value_Column => Value : M.Root_Phase;
         when Null_Column | Invalid_Column => null;
      end case;
   end record;
   type Abort_Class_Column (State : Nullable_Column_State := Null_Column) is record
      Raw : SQL_Cell;
      case State is
         when Value_Column => Value : M.Abort_Class;
         when Null_Column | Invalid_Column => null;
      end case;
   end record;

   function Read_Nullable_Root_Phase
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Root_Phase_Column
   with Global => null,
     Post => Read_Nullable_Root_Phase'Result.Raw = Cell and then
       (if Cell.Kind = SQL_Null then Read_Nullable_Root_Phase'Result.State = Null_Column
        elsif Read_Root_Phase_Name (Data, Cell).Status = Exact_Name then
          Read_Nullable_Root_Phase'Result.State = Value_Column and then
          Read_Nullable_Root_Phase'Result.Value = Read_Root_Phase_Name (Data, Cell).Value
        else Read_Nullable_Root_Phase'Result.State = Invalid_Column);

   function Read_Nullable_Abort_Class
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Abort_Class_Column
   with Global => null,
     Post => Read_Nullable_Abort_Class'Result.Raw = Cell and then
       (if Cell.Kind = SQL_Null then Read_Nullable_Abort_Class'Result.State = Null_Column
        elsif Read_Abort_Class_Name (Data, Cell).Status = Exact_Name then
          Read_Nullable_Abort_Class'Result.State = Value_Column and then
          Read_Nullable_Abort_Class'Result.Value = Read_Abort_Class_Name (Data, Cell).Value
        else Read_Nullable_Abort_Class'Result.State = Invalid_Column);
   function Text_Cell (Data : Q.Byte_Array; Cell : SQL_Cell) return Boolean is
     (Cell.Kind = SQL_Text and then Span_Valid (Data, Cell.Bytes))
   with Global => null;

   function Is_Hex_Character (Value : Q.Byte) return Boolean is
     (Value in Character'Pos ('0') .. Character'Pos ('9') or else
      Value in Character'Pos ('a') .. Character'Pos ('f') or else
      Value in Character'Pos ('A') .. Character'Pos ('F'))
   with Global => null;

   --  Decoded digest TEXT grammar, not the DDL's length-only check. Exact
   --  bytes/case remain in Raw for subsequent authentic archive comparison.
   function Digest_Text (Data : Q.Byte_Array; Cell : SQL_Cell) return Boolean is
     (Text_Cell (Data, Cell) and then Cell.Bytes.Length = M.Digest'Length * 2
      and then (for all Offset in Q.Byte_Count range 0 .. Cell.Bytes.Length - 1 =>
                  Is_Hex_Character (Data (Cell.Bytes.First + Offset))))
   with Global => null;

   function Before_Unknown_Columns
     (Data : Q.Byte_Array; Phase, Before_Unknown : SQL_Cell) return Boolean is
     (Read_Root_Phase_Name (Data, Phase).Status = Exact_Name and then
      Read_Nullable_Root_Phase (Data, Before_Unknown).State /= Invalid_Column
      and then
      ((Read_Root_Phase_Name (Data, Phase).Value = M.Unknown) =
         (Before_Unknown.Kind /= SQL_Null)) and then
      (if Before_Unknown.Kind /= SQL_Null then
         Read_Nullable_Root_Phase (Data, Before_Unknown).Value not in M.Unknown | M.Ended))
   with Global => null;

   --  Scalar/root field shape only; NOT full DDL uniqueness/FK verification
   --  and NOT fold or event legality. Optional inactive values stay present.
   function Root_Column_Shapes
     (Data : Q.Byte_Array; Row : Root_Columns) return Boolean is
     (Magnitude_Blob (Data, Row.Generation, Positive => True) and then
      Text_Cell (Data, Row.Operation) and then
      Before_Unknown_Columns (Data, Row.Phase, Row.Before_Unknown) and then
      Bit_Cell (Data, Row.Owners_Open) and then
      Read_Nullable_Abort_Class (Data, Row.Abort_Kind).State /= Invalid_Column and then
      Bit_Cell (Data, Row.Launched) and then Bit_Cell (Data, Row.Closure_NS) and then
      Bit_Cell (Data, Row.Closure_Outer) and then Bit_Cell (Data, Row.Closure_Raw) and then
      Bit_Cell (Data, Row.Witness) and then Bit_Cell (Data, Row.Settled) and then
      Bit_Cell (Data, Row.Released_Unlaunched) and then
      (Row.Unknown_Cause.Kind = SQL_Null or else Digest_Text (Data, Row.Unknown_Cause))
      and then Magnitude_Blob (Data, Row.Reattach_Epoch, Positive => False) and then
      Digest_Text (Data, Row.Head_Event))
   with Global => null;

   function Subject_Phase_Columns
     (Data : Q.Byte_Array; Kind, Phase : SQL_Cell) return Boolean is
     ((Text_Is (Data, Kind, "REQUEST") and then
       Read_Request_Phase_Name (Data, Phase).Status = Exact_Name) or else
      (Text_Is (Data, Kind, "DESCRIPTOR") and then
       Read_Descriptor_Phase_Name (Data, Phase).Status = Exact_Name))
   with Global => null;

   function Subject_Column_Shapes
     (Data : Q.Byte_Array; Row : Subject_Columns) return Boolean is
     (Magnitude_Blob (Data, Row.Generation, Positive => True) and then
      Text_Cell (Data, Row.Subject) and then
      Magnitude_Blob (Data, Row.Subgeneration, Positive => False) and then
      Subject_Phase_Columns (Data, Row.Kind_Of_Subject, Row.Phase) and then
      Read_Transfer_Mode_Name (Data, Row.Mode).Status = Exact_Name and then
      Nullable_Magnitude_Blob (Data, Row.Position, Positive => False) and then
      Nullable_Magnitude_Blob (Data, Row.Carried_From, Positive => True) and then
      Digest_Text (Data, Row.Head_Event))
   with Global => null;

   function Same_Optional_Root_Row
     (Data : Q.Byte_Array; Left, Right : Optional_Root_Row) return Boolean is
     (Left.Present = Right.Present and then
      (if Left.Present then Same_Root_Columns (Data, Left.Columns, Right.Columns)))
   with Global => null;

   function Same_Optional_Subject_Row
     (Data : Q.Byte_Array; Left, Right : Optional_Subject_Row) return Boolean is
     (Left.Present = Right.Present and then
      (if Left.Present then Same_Subject_Columns (Data, Left.Columns, Right.Columns)))
   with Global => null;
   type Quantity_Column (State : Nullable_Column_State := Null_Column) is record
      Raw : SQL_Cell;
      case State is
         when Value_Column => Value : Q.Quantity;
         when Null_Column | Invalid_Column => null;
      end case;
   end record;
   function Read_Nullable_Quantity
     (Data : Q.Byte_Array; Cell : SQL_Cell; Positive : Boolean)
      return Quantity_Column
   with Global => null,
     Post => Read_Nullable_Quantity'Result.Raw = Cell and then
       (if Cell.Kind = SQL_Null then Read_Nullable_Quantity'Result.State = Null_Column
        elsif Magnitude_Blob (Data, Cell, Positive) then
          Read_Nullable_Quantity'Result.State = Value_Column and then
          Read_Nullable_Quantity'Result.Value = Blob_Quantity (Cell)
        else Read_Nullable_Quantity'Result.State = Invalid_Column);

   type Subject_Phase_Result (Status : Name_Status := No_Exact_Name) is record
      Raw_Kind, Raw_Phase : SQL_Cell;
      case Status is
         when Exact_Name => Value : Subject_Phase;
         when No_Exact_Name => null;
      end case;
   end record;
   function Read_Subject_Phase
     (Data : Q.Byte_Array; Kind, Phase : SQL_Cell) return Subject_Phase_Result
   with Global => null,
     Post => Read_Subject_Phase'Result.Raw_Kind = Kind and then
       Read_Subject_Phase'Result.Raw_Phase = Phase and then
       (if Text_Is (Data, Kind, "REQUEST") and then
           Read_Request_Phase_Name (Data, Phase).Status = Exact_Name then
          Read_Subject_Phase'Result.Status = Exact_Name and then
          Read_Subject_Phase'Result.Value.Kind = Request_Row and then
          Read_Subject_Phase'Result.Value.Request =
            Read_Request_Phase_Name (Data, Phase).Value
        elsif Text_Is (Data, Kind, "DESCRIPTOR") and then
              Read_Descriptor_Phase_Name (Data, Phase).Status = Exact_Name then
          Read_Subject_Phase'Result.Status = Exact_Name and then
          Read_Subject_Phase'Result.Value.Kind = Descriptor_Row and then
          Read_Subject_Phase'Result.Value.Descriptor =
            Read_Descriptor_Phase_Name (Data, Phase).Value
        else Read_Subject_Phase'Result.Status = No_Exact_Name);
end Worldline.Root_Custody_Row_Schema;

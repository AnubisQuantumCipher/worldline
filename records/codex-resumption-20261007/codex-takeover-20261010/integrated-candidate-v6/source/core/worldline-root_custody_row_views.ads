with Worldline.Root_Custody_Row_Schema;

-- Supplied-column construction, not authenticated source decoding or Legal.
-- Pure SPARK functions retain intrinsic termination obligations (E0016).
package Worldline.Root_Custody_Row_Views with SPARK_Mode is
   package S renames Worldline.Root_Custody_Row_Schema;
   package M renames S.M;
   package Q renames S.Q;
   use type Q.Byte;
   use type Q.Byte_Count;
   use type Q.Quantity;
   use type Q.Optional_Quantity;
   use type S.SQL_Class;
   use type S.Root_Columns;
   use type S.Subject_Columns;
   use type S.Bytes_Span;
   use type S.Optional_Root_Phase;
   use type S.Optional_Abort_Class;
   use type S.Subject_Phase;
   use type S.Optional_Root_Row;
   use type S.Optional_Subject_Row;
   use type M.Root_Phase;
   use type M.Transfer_Mode;
   use type M.Optional_Digest;
   use type M.Digest;

   function Hex_Nibble (Value : Q.Byte) return Q.Byte is
     (if Value in Character'Pos ('0') .. Character'Pos ('9') then
         Value - Character'Pos ('0')
      elsif Value in Character'Pos ('a') .. Character'Pos ('f') then
         Value - Character'Pos ('a') + 10
      else Value - Character'Pos ('A') + 10)
   with Global => null, Pre => S.Is_Hex_Character (Value),
     Post => Hex_Nibble'Result <= 15;

   function Decode_Digest (Data : Q.Byte_Array; Cell : S.SQL_Cell)
      return M.Digest
   with Global => null, Pre => S.Digest_Text (Data, Cell),
     Post => (for all I in M.Digest'Range =>
       Decode_Digest'Result (I) =
         Hex_Nibble (Data (Cell.Bytes.First + Q.Byte_Count (I - M.Digest'First) * 2)) * 16 +
         Hex_Nibble (Data (Cell.Bytes.First + (Q.Byte_Count (I - M.Digest'First) * 2 + 1))));

   function Optional_Digest (Data : Q.Byte_Array; Cell : S.SQL_Cell)
      return M.Optional_Digest is
     (if Cell.Kind = S.SQL_Null then (Present => False)
      else (Present => True, Value => Decode_Digest (Data, Cell)))
   with Global => null,
     Pre => Cell.Kind = S.SQL_Null or else S.Digest_Text (Data, Cell);

   function Optional_Phase (Data : Q.Byte_Array; Cell : S.SQL_Cell)
      return S.Optional_Root_Phase is
     (if Cell.Kind = S.SQL_Null then (Present => False)
      else (Present => True, Value => S.Read_Root_Phase_Name (Data, Cell).Value))
   with Global => null,
     Pre => Cell.Kind = S.SQL_Null or else
       (for some P in M.Root_Phase => S.Matches_Root_Phase (Data, Cell, P));

   function Optional_Abort (Data : Q.Byte_Array; Cell : S.SQL_Cell)
      return S.Optional_Abort_Class is
     (if Cell.Kind = S.SQL_Null then (Present => False)
      else (Present => True, Value => S.Read_Abort_Class_Name (Data, Cell).Value))
   with Global => null,
     Pre => Cell.Kind = S.SQL_Null or else
       (for some A in M.Abort_Class => S.Matches_Abort_Class (Data, Cell, A));

   function Optional_Quantity (Data : Q.Byte_Array; Cell : S.SQL_Cell;
                               Positive : Boolean) return Q.Optional_Quantity is
     (if Cell.Kind = S.SQL_Null then (Present => False)
      else (Present => True, Value => S.Blob_Quantity (Cell)))
   with Global => null,
     Pre => S.Nullable_Magnitude_Blob (Data, Cell, Positive);

   -- Raw equality preserves representation, not merely numeric equivalence.
   function Root_Corresponds
     (Data : Q.Byte_Array; Row : S.Root_Columns; View : S.Root_View)
      return Boolean is
     (S.Root_Column_Shapes (Data, Row) and then View.Raw = Row and then
      View.Generation = S.Blob_Quantity (Row.Generation) and then
      View.Operation = Row.Operation.Bytes and then
      View.Phase = S.Read_Root_Phase_Name (Data, Row.Phase).Value and then
      View.Before_Unknown = Optional_Phase (Data, Row.Before_Unknown) and then
      View.Owners_Open = S.Bit_Value (Data, Row.Owners_Open) and then
      View.Abort_Kind = Optional_Abort (Data, Row.Abort_Kind) and then
      View.Unknown_Cause = Optional_Digest (Data, Row.Unknown_Cause) and then
      View.Reattach_Epoch = S.Blob_Quantity (Row.Reattach_Epoch) and then
      View.Head = Decode_Digest (Data, Row.Head_Event) and then
      View.Physical.Launched = S.Bit_Value (Data, Row.Launched) and then
      View.Physical.NS = S.Bit_Value (Data, Row.Closure_NS) and then
      View.Physical.Outer = S.Bit_Value (Data, Row.Closure_Outer) and then
      View.Physical.Raw = S.Bit_Value (Data, Row.Closure_Raw) and then
      View.Physical.Witness = S.Bit_Value (Data, Row.Witness) and then
      View.Physical.Settled = S.Bit_Value (Data, Row.Settled) and then
      View.Physical.Released_Unlaunched = S.Bit_Value (Data, Row.Released_Unlaunched))
   with Global => null;

   function Make_Root (Data : Q.Byte_Array; Row : S.Root_Columns)
      return S.Root_View
   with Global => null, Pre => S.Root_Column_Shapes (Data, Row),
     Post => Root_Corresponds (Data, Row, Make_Root'Result);

   type Optional_Root_View (Present : Boolean := False) is record
      Raw : S.Optional_Root_Row;
      case Present is
         when False => null;
         when True => Value : S.Root_View;
      end case;
   end record;
   function Make_Optional_Root
     (Data : Q.Byte_Array; Row : S.Optional_Root_Row)
      return Optional_Root_View
   with Global => null,
     Pre => (if Row.Present then S.Root_Column_Shapes (Data, Row.Columns)),
     Post => Make_Optional_Root'Result.Raw = Row and then
       Make_Optional_Root'Result.Present = Row.Present and then
       (if Row.Present then
          Root_Corresponds (Data, Row.Columns, Make_Optional_Root'Result.Value));

   -- Raw equality preserves representation, not merely numeric equivalence.
   function Subject_Corresponds
     (Data : Q.Byte_Array; Row : S.Subject_Columns; View : S.Subject_View)
      return Boolean is
     (S.Subject_Column_Shapes (Data, Row) and then View.Raw = Row and then
      View.Generation = S.Blob_Quantity (Row.Generation) and then
      View.Subject = Row.Subject.Bytes and then
      View.Subgeneration = S.Blob_Quantity (Row.Subgeneration) and then
      View.Phase = S.Read_Subject_Phase (Data, Row.Kind_Of_Subject, Row.Phase).Value and then
      View.Mode = S.Read_Transfer_Mode_Name (Data, Row.Mode).Value and then
      View.Position = Optional_Quantity (Data, Row.Position, Positive => False) and then
      View.Carried_From = Optional_Quantity (Data, Row.Carried_From, Positive => True) and then
      View.Head = Decode_Digest (Data, Row.Head_Event))
   with Global => null;

   function Make_Subject (Data : Q.Byte_Array; Row : S.Subject_Columns)
      return S.Subject_View
   with Global => null, Pre => S.Subject_Column_Shapes (Data, Row),
     Post => Subject_Corresponds (Data, Row, Make_Subject'Result);

   type Optional_Subject_View (Present : Boolean := False) is record
      Raw : S.Optional_Subject_Row;
      case Present is
         when False => null;
         when True => Value : S.Subject_View;
      end case;
   end record;
   function Make_Optional_Subject
     (Data : Q.Byte_Array; Row : S.Optional_Subject_Row)
      return Optional_Subject_View
   with Global => null,
     Pre => (if Row.Present then S.Subject_Column_Shapes (Data, Row.Columns)),
     Post => Make_Optional_Subject'Result.Raw = Row and then
       Make_Optional_Subject'Result.Present = Row.Present and then
       (if Row.Present then
          Subject_Corresponds (Data, Row.Columns, Make_Optional_Subject'Result.Value));

end Worldline.Root_Custody_Row_Views;

with Interfaces;

--  Isolated source proposal: no build/proof/execution or product integration.
--  Scalar exact columns and compact repeated runs, not a Big_Integer backend.
package Full_Domain_Columns with SPARK_Mode is
   subtype Byte is Interfaces.Unsigned_8;
   subtype Run_Length is Interfaces.Unsigned_64;
   use type Run_Length;
   type Source_Count is range 0 .. Long_Long_Integer'Last;

   type Column is record
      Digit : Byte;
      Carry : Boolean;
   end record;
   type Run is record
      Digit  : Byte;
      Length : Run_Length;
   end record;
   --  Little-endian concatenation: First, then Rest; Carry is above both.
   --  A zero-length run contributes no digit. No canonicality is assumed.
   type Two_Runs is record
      First : Run;
      Rest  : Run;
      Carry : Boolean;
   end record;

   function Add_Column (Left, Right : Byte; Carry_In : Boolean) return Column
   with Global => null,
     Post => Natural (Add_Column'Result.Digit) +
       256 * Boolean'Pos (Add_Column'Result.Carry) =
       Natural (Left) + Natural (Right) + Boolean'Pos (Carry_In);

   function Subtract_Column
     (Left, Right : Byte; Borrow_In : Boolean) return Column
   with Global => null,
     Post => Integer (Left) - Integer (Right) - Boolean'Pos (Borrow_In) =
       Integer (Subtract_Column'Result.Digit) -
       256 * Boolean'Pos (Subtract_Column'Result.Carry);

   function Add_Uniform
     (Left, Right : Byte; Carry_In : Boolean; Length : Run_Length)
      return Two_Runs
   with Global => null,
     Post =>
       (if Length = 0 then
          Add_Uniform'Result.First.Length = 0 and then
          Add_Uniform'Result.Rest.Length = 0 and then
          Add_Uniform'Result.Carry = Carry_In
        else
          Add_Uniform'Result.First.Length = 1 and then
          Add_Uniform'Result.Rest.Length = Length - 1 and then
          Add_Uniform'Result.First.Digit =
            Add_Column (Left, Right, Carry_In).Digit and then
          Add_Uniform'Result.Rest.Digit =
            Add_Column (Left, Right,
              Add_Column (Left, Right, Carry_In).Carry).Digit and then
          Add_Uniform'Result.Carry =
            Add_Column (Left, Right, Carry_In).Carry);

   function Subtract_Uniform
     (Left, Right : Byte; Borrow_In : Boolean; Length : Run_Length)
      return Two_Runs
   with Global => null,
     Post =>
       (if Length = 0 then
          Subtract_Uniform'Result.First.Length = 0 and then
          Subtract_Uniform'Result.Rest.Length = 0 and then
          Subtract_Uniform'Result.Carry = Borrow_In
        else
          Subtract_Uniform'Result.First.Length = 1 and then
          Subtract_Uniform'Result.Rest.Length = Length - 1 and then
          Subtract_Uniform'Result.First.Digit =
            Subtract_Column (Left, Right, Borrow_In).Digit and then
          Subtract_Uniform'Result.Rest.Digit =
            Subtract_Column (Left, Right,
              Subtract_Column (Left, Right, Borrow_In).Carry).Digit and then
          Subtract_Uniform'Result.Carry =
            Subtract_Column (Left, Right, Borrow_In).Carry);

   function Power_256_Runs (Exponent : Source_Count) return Two_Runs
   with Global => null,
     Post => Power_256_Runs'Result.First = (0, Run_Length (Exponent)) and then
       Power_256_Runs'Result.Rest = (1, 1) and then
       not Power_256_Runs'Result.Carry;

   function Power_Minus_One_Runs (Exponent : Source_Count) return Two_Runs
   with Global => null,
     Post => Power_Minus_One_Runs'Result.First =
       (255, Run_Length (Exponent)) and then
       Power_Minus_One_Runs'Result.Rest = (0, 0) and then
       not Power_Minus_One_Runs'Result.Carry;

   subtype Triple_Borrow is Natural range 0 .. 3;
   type Debit_Column is record
      Digit  : Byte;
      Borrow : Triple_Borrow;
   end record;
   function Subtract_Three
     (Available, Withheld, Floor, Requested : Byte;
      Borrow_In : Triple_Borrow) return Debit_Column
   with Global => null,
     Post => Integer (Available) - Integer (Withheld) - Integer (Floor) -
       Integer (Requested) - Borrow_In =
       Integer (Subtract_Three'Result.Digit) -
       256 * Subtract_Three'Result.Borrow;
end Full_Domain_Columns;

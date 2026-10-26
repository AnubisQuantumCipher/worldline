package body Full_Domain_Columns with SPARK_Mode is
   function Add_Column (Left, Right : Byte; Carry_In : Boolean) return Column is
      Total : constant Natural :=
        Natural (Left) + Natural (Right) + Boolean'Pos (Carry_In);
   begin
      return (Byte (Total mod 256), Total >= 256);
   end Add_Column;

   function Subtract_Column
     (Left, Right : Byte; Borrow_In : Boolean) return Column
   is
      Total : constant Integer :=
        Integer (Left) - Integer (Right) - Boolean'Pos (Borrow_In);
   begin
      return (Byte (Total mod 256), Total < 0);
   end Subtract_Column;

   function Add_Uniform
     (Left, Right : Byte; Carry_In : Boolean; Length : Run_Length)
      return Two_Runs
   is
      First  : constant Column := Add_Column (Left, Right, Carry_In);
      Steady : constant Column := Add_Column (Left, Right, First.Carry);
   begin
      if Length = 0 then
         return ((0, 0), (0, 0), Carry_In);
      end if;
      --  After the first column, the carry is a fixed point for this pair.
      pragma Assert (Steady.Carry = First.Carry);
      return ((First.Digit, 1), (Steady.Digit, Length - 1), First.Carry);
   end Add_Uniform;

   function Subtract_Uniform
     (Left, Right : Byte; Borrow_In : Boolean; Length : Run_Length)
      return Two_Runs
   is
      First  : constant Column := Subtract_Column (Left, Right, Borrow_In);
      Steady : constant Column := Subtract_Column (Left, Right, First.Carry);
   begin
      if Length = 0 then
         return ((0, 0), (0, 0), Borrow_In);
      end if;
      pragma Assert (Steady.Carry = First.Carry);
      return ((First.Digit, 1), (Steady.Digit, Length - 1), First.Carry);
   end Subtract_Uniform;

   function Power_256_Runs (Exponent : Source_Count) return Two_Runs is
   begin
      return ((0, Run_Length (Exponent)), (1, 1), False);
   end Power_256_Runs;

   function Power_Minus_One_Runs (Exponent : Source_Count) return Two_Runs is
   begin
      return ((255, Run_Length (Exponent)), (0, 0), False);
   end Power_Minus_One_Runs;

   function Subtract_Three
     (Available, Withheld, Floor, Requested : Byte;
      Borrow_In : Triple_Borrow) return Debit_Column
   is
      Total : constant Integer := Integer (Available) - Integer (Withheld) -
        Integer (Floor) - Integer (Requested) - Borrow_In;
      Borrow : constant Triple_Borrow :=
        (if Total >= 0 then 0 else (-Total + 255) / 256);
   begin
      return (Byte (Total mod 256), Borrow);
   end Subtract_Three;
end Full_Domain_Columns;

with Interfaces;
with Ada.Numerics.Big_Numbers.Big_Integers;

package Worldline.Resources with SPARK_Mode is
   package Mathematics renames Ada.Numerics.Big_Numbers.Big_Integers;
   use Mathematics;
   --  Nonnegative integers in little-endian base 256. Any lower bound,
   --  length and leading zeroes are accepted; a null array denotes zero.
   --  No machine-word bound is imposed on a whole resource quantity.
   subtype Byte is Interfaces.Unsigned_8;
   --  Match the host's signed byte-length representation rather than imposing
   --  Standard.Natural's smaller index domain on arbitrary integer operands.
   subtype Byte_Count is Long_Long_Integer range 0 .. Long_Long_Integer'Last;
   subtype Byte_Index is Byte_Count range 1 .. Byte_Count'Last;
   type Byte_Array is array (Byte_Index range <>) of Byte;

   function Digit_At (Value : Byte_Array; Offset : Byte_Count) return Natural
     with Global => null,
          Post => Digit_At'Result <= 255
            and then Digit_At'Result =
              (if Offset < Value'Length
               then Natural (Value (Value'First + Offset)) else 0);

   --  Closed mathematical interpretation, independent of either decision
   --  algorithm. The exponent and prefix count retain the complete Byte_Count
   --  domain: neither is converted to the narrower Natural exponent of **.
   --  These are executable Ghost definitions, with their own required proof
   --  and termination obligations; no imported theorem is introduced.
   function Radix_Power (Count : Byte_Count) return Big_Positive is
     (if Count = 0 then 1 else 256 * Radix_Power (Count - 1))
     with Ghost, Global => null,
          Subprogram_Variant => (Decreases => Count);

   function Prefix_Value
     (Value : Byte_Array; Count : Byte_Count) return Big_Natural is
     (if Count = 0 then 0
      else Prefix_Value (Value, Count - 1)
        + To_Big_Integer (Digit_At (Value, Count - 1))
          * Radix_Power (Count - 1))
     with Ghost, Global => null,
          Subprogram_Variant => (Decreases => Count),
          Post => Prefix_Value'Result < Radix_Power (Count);

   function Magnitude (Value : Byte_Array) return Big_Natural is
     (Prefix_Value (Value, Value'Length))
     with Ghost, Global => null;

   function Fits_Mathematically
     (Available, Withheld, Floor, Requested : Byte_Array) return Boolean is
     (Magnitude (Available) >= Magnitude (Withheld) + Magnitude (Floor)
                                + Magnitude (Requested))
     with Ghost, Global => null;

   subtype Borrow is Natural range 0 .. 3;
   type Column_Result is record
      Remainder : Byte;
      Next     : Borrow;
   end record;

   --  Exact column conservation. All intermediate operations fit Natural;
   --  there is no modular arithmetic on the semantic operands.
   function Subtract_Column
     (Available, Withheld, Floor, Requested : Byte;
      Previous : Borrow) return Column_Result
     with Global => null,
          Post =>
            Natural (Available) + 256 * Subtract_Column'Result.Next =
              Natural (Withheld) + Natural (Floor) + Natural (Requested)
              + Previous + Natural (Subtract_Column'Result.Remainder);

   --  Independent reference: add the three requested quantities by columns,
   --  then compare the entire sum with Available, most significant differing
   --  column winning. This is the exact nonnegative-integer relation
   --     Available >= Withheld + Floor + Requested.
   --  Its addition algorithm is separate from the subtraction implementation.
   --  Reference/body equivalence and its mathematical interpretation remain
   --  required proof obligations, not trusted imported declarations.
   function Fits_By_Addition
     (Available, Withheld, Floor, Requested : Byte_Array) return Boolean
     with Global => null,
          Post => Fits_By_Addition'Result =
            Fits_Mathematically (Available, Withheld, Floor, Requested);

   function Can_Reserve
     (Available, Withheld, Floor, Requested : Byte_Array) return Boolean
     with Global => null,
          Post => Can_Reserve'Result =
            Fits_By_Addition (Available, Withheld, Floor, Requested)
            and then Can_Reserve'Result =
              Fits_Mathematically (Available, Withheld, Floor, Requested);

   --  Exact whole-value relation Result = Left + Right, including carry out.
   function Sum_Equals
     (Left, Right, Result : Byte_Array) return Boolean
     with Global => null,
          Post => Sum_Equals'Result =
            (Magnitude (Result) = Magnitude (Left) + Magnitude (Right));

   --  Caller-owned bounded storage; Capacity is arbitrary, not a test profile.
   --  Available and Floor are observations, never silently changed by reserve.
   --  Outstanding is the arithmetic projection of the caller's ledger. Binding
   --  that projection to authenticated live reservations is an integration
   --  obligation; this record does not assert producer truth or custody.
   type Reservation_State (Capacity : Byte_Index) is record
      Available   : Byte_Array (1 .. Capacity);
      Floor       : Byte_Array (1 .. Capacity);
      Outstanding : Byte_Array (1 .. Capacity);
   end record;

   function Reserve_Mathematically_Conforms
     (Before, After : Reservation_State;
      Requested : Byte_Array;
      Accepted : Boolean) return Boolean is
     (Accepted = Fits_Mathematically
        (Before.Available, Before.Outstanding, Before.Floor, Requested)
      and then After.Capacity = Before.Capacity
      and then After.Available = Before.Available
      and then After.Floor = Before.Floor
      and then
        (if Accepted then
           Magnitude (After.Outstanding) =
             Magnitude (Before.Outstanding) + Magnitude (Requested)
         else After.Outstanding = Before.Outstanding))
     with Ghost, Global => null;

   --  The complete relation is an expression, not an imported premise. Naming
   --  the old/new records avoids an installed compiler failure on selectors
   --  of a discriminated record's Old value inside a conditional Post.
   function Reserve_Conforms
     (Before, After : Reservation_State;
      Requested : Byte_Array;
      Accepted : Boolean) return Boolean is
     (Accepted = Fits_By_Addition
        (Before.Available, Before.Outstanding, Before.Floor, Requested)
      and then After.Capacity = Before.Capacity
      and then After.Available = Before.Available
      and then After.Floor = Before.Floor
      and then
        (if Accepted then
           Sum_Equals (Before.Outstanding, Requested, After.Outstanding)
         else After.Outstanding = Before.Outstanding))
     with Global => null,
          Post => Reserve_Conforms'Result =
            Reserve_Mathematically_Conforms
              (Before, After, Requested, Accepted);

   procedure Try_Reserve
     (State : in out Reservation_State;
      Requested : Byte_Array;
      Accepted : out Boolean)
     with Global => null,
          Always_Terminates,
          Post => Reserve_Conforms (State'Old, State, Requested, Accepted)
            and then Reserve_Mathematically_Conforms
              (State'Old, State, Requested, Accepted);
end Worldline.Resources;

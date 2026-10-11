with Interfaces;
with Worldline.Resources;
package Worldline.Ordinary_Reservation_Lifecycle with SPARK_Mode is
   use type Interfaces.Unsigned_32;
   use type Worldline.Resources.Byte;
   type Mask_Array is array (Positive range <>) of Worldline.Resources.Byte;
   -- Codes: 0 malformed capture, 1 false/skip/refused, 2 true/proceed.
   -- Mask: 0 untouched, 1 selected, 2 selected retaining current identity.
   -- Position is the unique matching row, or zero. No resource arithmetic.
   procedure Plan (Data : String; Mask : out Mask_Array;
                   Code : out Interfaces.Unsigned_32; Position : out Natural)
     with Global => null, Always_Terminates,
       Post => Code <= 2 and then Position <= Mask'Length and then
         (for all I in Mask'Range => Mask (I) <= 2);
end Worldline.Ordinary_Reservation_Lifecycle;

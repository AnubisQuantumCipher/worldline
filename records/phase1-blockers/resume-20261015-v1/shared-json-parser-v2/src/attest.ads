--  Attest — a proof-carrying evidence core.
--
--  The point of this library is that the bytes it produces are computed by
--  code whose absence of runtime error is machine-checked, not merely tested.
--  Every unit below is SPARK_Mode => On.  The only exceptions are the I/O shim
--  and the command line, which are explicitly SPARK_Mode => Off and kept as
--  thin as possible so the trusted-but-unproved surface stays small.

with Interfaces;

package Attest with Pure, SPARK_Mode is

   subtype Byte is Interfaces.Unsigned_8;

   --  The index subtype stops one short of Natural'Last on purpose: an array
   --  indexed by full Natural can have 'Length = Natural'Last + 1, which does
   --  not fit in Natural, and any contract mentioning 'Length would then be
   --  able to overflow before it was even evaluated.  gnatprove found this.
   subtype Byte_Index is Natural range 0 .. Natural'Last - 1;

   type Byte_Array is array (Byte_Index range <>) of Byte;

end Attest;

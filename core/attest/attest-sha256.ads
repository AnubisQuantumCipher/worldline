--  SHA-256 (FIPS 180-4) in SPARK.
--
--  Proof obligations of interest here are not the round function -- modular
--  arithmetic cannot overflow -- but the buffer arithmetic in Update/Final,
--  where a hand-written implementation actually goes wrong: the partial-block
--  index, the 0x80 pad byte landing one past the end, and the 64-bit length
--  field.  Those are the checks gnatprove discharges.

with Interfaces; use Interfaces;

package Attest.SHA256 with SPARK_Mode is

   Digest_Bytes : constant := 32;
   Block_Bytes  : constant := 64;

   subtype Digest is Byte_Array (0 .. Digest_Bytes - 1);

   --  The length field of the padded message is 64 bits wide and counts bits,
   --  so a message must be shorter than 2**61 bytes for the encoding to be
   --  injective.  Callers are held to that by precondition rather than by a
   --  silent truncation.
   Max_Message_Bytes : constant Unsigned_64 := 2 ** 61 - 1;

   type Context is private;

   function Absorbed (C : Context) return Unsigned_64;
   --  Number of message bytes fed to C so far.

   function Initial return Context
     with Post => Absorbed (Initial'Result) = 0;

   procedure Update (C : in out Context; Input : Byte_Array)
     with Pre  => Absorbed (C) <= Max_Message_Bytes - Unsigned_64 (Input'Length),
          Post => Absorbed (C) = Absorbed (C'Old) + Unsigned_64 (Input'Length);

   function Final (C : Context) return Digest;
   --  Pure: pads a copy, so a context may be finalized more than once and
   --  cannot be corrupted by finalization.

   function Hash (Input : Byte_Array) return Digest
     with Pre => Unsigned_64 (Input'Length) <= Max_Message_Bytes;

private

   subtype State_Index  is Natural range 0 .. 7;
   subtype Block_Offset is Natural range 0 .. Block_Bytes - 1;

   type State is array (State_Index) of Unsigned_32;
   type Block is array (Block_Offset) of Byte;

   type Context is record
      H     : State;
      Buf   : Block;
      Fill  : Block_Offset;  --  bytes of Buf that are live; always < Block_Bytes
      Count : Unsigned_64;   --  total message bytes absorbed
   end record;

   function Absorbed (C : Context) return Unsigned_64 is (C.Count);

end Attest.SHA256;

-- NEW unproved provider-compatible retention package; no original proof transfer.
--  SHA-256 (FIPS 180-4) in SPARK.
--
--  Proof obligations of interest here are not the round function -- modular
--  arithmetic cannot overflow -- but the buffer arithmetic in Update/Final,
--  where a hand-written implementation actually goes wrong: the partial-block
--  index, the 0x80 pad byte landing one past the end, and the 64-bit length
--  field.  Those are the checks gnatprove discharges.

with Interfaces; use Interfaces;

package Attest.Custody_SHA256 with SPARK_Mode is

   Digest_Bytes : constant := 32;
   Block_Bytes  : constant := 64;

   subtype Digest is Byte_Array (0 .. Digest_Bytes - 1);

   -- Retention-provider compatibility digest. This is a NEW package; the
   -- original bounded Attest.SHA256 specification/body remain unchanged.
   -- Byte accounting and final bit-length encoding are modulo Unsigned_64,
   -- matching OpenSSL md32_common's low/high bit counters. This is NOT an
   -- injective encoding promise for messages beyond the FIPS SHA domain.
   function Bit_Length (Byte_Length : Unsigned_64) return Unsigned_64 is
     (Shift_Left (Byte_Length, 3));

   type Context is private;

   function Absorbed (C : Context) return Unsigned_64;
   -- Number of message bytes modulo Unsigned_64 modulus.

   function Initial return Context
     with Post => Absorbed (Initial'Result) = 0;

   procedure Update (C : in out Context; Input : Byte_Array)
     with Post => Absorbed (C) = Absorbed (C'Old) + Unsigned_64 (Input'Length);

   function Final (C : Context) return Digest;
   --  Pure: pads a copy, so a context may be finalized more than once and
   --  cannot be corrupted by finalization.

   function Hash (Input : Byte_Array) return Digest;

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

end Attest.Custody_SHA256;

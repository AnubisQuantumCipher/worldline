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


   type Digest_Record is record
      B00, B01, B02, B03, B04, B05, B06, B07,
      B08, B09, B10, B11, B12, B13, B14, B15,
      B16, B17, B18, B19, B20, B21, B22, B23,
      B24, B25, B26, B27, B28, B29, B30, B31 : Byte;
   end record;
   function To_Digest_Bytes (Value : Digest) return Digest_Record is
     (B00 => Value (0), B01 => Value (1), B02 => Value (2), B03 => Value (3),
      B04 => Value (4), B05 => Value (5), B06 => Value (6), B07 => Value (7),
      B08 => Value (8), B09 => Value (9), B10 => Value (10), B11 => Value (11),
      B12 => Value (12), B13 => Value (13), B14 => Value (14), B15 => Value (15),
      B16 => Value (16), B17 => Value (17), B18 => Value (18), B19 => Value (19),
      B20 => Value (20), B21 => Value (21), B22 => Value (22), B23 => Value (23),
      B24 => Value (24), B25 => Value (25), B26 => Value (26), B27 => Value (27),
      B28 => Value (28), B29 => Value (29), B30 => Value (30), B31 => Value (31));
   function From_Digest_Bytes (Value : Digest_Record) return Digest is
     (0 => Value.B00, 1 => Value.B01, 2 => Value.B02, 3 => Value.B03,
      4 => Value.B04, 5 => Value.B05, 6 => Value.B06, 7 => Value.B07,
      8 => Value.B08, 9 => Value.B09, 10 => Value.B10, 11 => Value.B11,
      12 => Value.B12, 13 => Value.B13, 14 => Value.B14, 15 => Value.B15,
      16 => Value.B16, 17 => Value.B17, 18 => Value.B18, 19 => Value.B19,
      20 => Value.B20, 21 => Value.B21, 22 => Value.B22, 23 => Value.B23,
      24 => Value.B24, 25 => Value.B25, 26 => Value.B26, 27 => Value.B27,
      28 => Value.B28, 29 => Value.B29, 30 => Value.B30, 31 => Value.B31);
   function Receipt_Link_Digest (Previous, Root : Digest_Record) return Digest
     with Global => null;
   function Causal_Link_Digest (Previous, Root : Digest_Record) return Digest
     with Global => null;

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

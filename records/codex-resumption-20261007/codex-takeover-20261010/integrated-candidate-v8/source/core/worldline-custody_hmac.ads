with Attest.SHA256;

--  RFC 2104 keyed hash primitive, not the custody-chain decision/export.
--  All lengths/bounds of the existing Attest.Byte_Array are accepted, including
--  empty keys/messages and keys longer than the SHA block. No key truncation.
--  X4's Resource_Quantities arena streaming bridge remains a separate obligation;
--  this helper MUST NOT narrow that original arena domain to Attest indexes.
package Worldline.Custody_Hmac with SPARK_Mode is
   package SHA renames Attest.SHA256;
   subtype Key_Block is Attest.Byte_Array (0 .. SHA.Block_Bytes - 1);
   use type Attest.Byte;
   use type Attest.Byte_Array;

   function Normalize (Key : Attest.Byte_Array) return Key_Block
   with Global => null,
     Post =>
       (if Key'Length > SHA.Block_Bytes then
          Normalize'Result (SHA.Digest'Range) = SHA.Hash (Key) and then
          (for all I in SHA.Digest_Bytes .. SHA.Block_Bytes - 1 =>
             Normalize'Result (I) = 0)
        else
          (for all I in Key_Block'Range =>
             Normalize'Result (I) =
               (if I < Key'Length then Key (Key'First + I) else 0)));

   --  RFC 2104 section 2: H((K0 xor opad) || H((K0 xor ipad) || Message)).
   --  Sequential Update calls avoid imposing a concatenated-array size bound.
   --  SHA's existing contracts cover absorbed lengths/AoRTE, not a proved
   --  mathematical SHA/HMAC functional equivalence; that obligation stays open.
   function Mac (Key, Message : Attest.Byte_Array) return SHA.Digest
     with Global => null;
end Worldline.Custody_Hmac;

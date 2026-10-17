with Attest.SHA256;

package Worldline with SPARK_Mode is
   use type Attest.Byte;
   use type Attest.Byte_Array;

   subtype Hash is Attest.SHA256.Digest;

   Zero_Hash : constant Hash := [others => 0];

   --  Componentwise equality of a fixed-bound digest. Proved equal to
   --  predefined "=" so callers do not need a GNATprove annotation.
   function Hash_Eq (Left, Right : Hash) return Boolean is
     (for all I in Hash'Range => Left (I) = Right (I))
     with Ghost, Global => null,
          Post => Hash_Eq'Result = (Left = Right);

end Worldline;

with Attest.SHA256;

package Worldline with SPARK_Mode is
   use type Attest.Byte;

   subtype Hash is Attest.SHA256.Digest;

   Zero_Hash : constant Hash := [others => 0];

   --  Predefined array "=" is componentwise. In the prover that is not identity
   --  of the array value, so pure functions of Hash do not transfer across "="
   --  until this predicate has introduced logical equality.
   function Hash_Eq (Left, Right : Hash) return Boolean is
     (for all I in Hash'Range => Left (I) = Right (I))
     with Ghost, Global => null,
          Annotate => (GNATprove, Logical_Equal);

end Worldline;

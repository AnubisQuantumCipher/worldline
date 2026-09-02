with Attest.SHA256;

package Worldline with SPARK_Mode is

   subtype Hash is Attest.SHA256.Digest;

   Zero_Hash : constant Hash := [others => 0];

end Worldline;

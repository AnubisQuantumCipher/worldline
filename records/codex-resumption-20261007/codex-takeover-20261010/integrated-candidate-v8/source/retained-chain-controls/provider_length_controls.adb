with Interfaces;
with Attest.SHA256;
with Attest.Custody_SHA256;
procedure Provider_Length_Controls is
   package N renames Attest.Custody_SHA256;
   use type Interfaces.Unsigned_64;
   use type Attest.Byte_Array;
   Data : constant Attest.Byte_Array := (16#61#, 16#62#, 16#63#);
   C : N.Context := N.Initial;
begin
   -- Arithmetic fixtures: JACKAL exact, not functional/provider proof.
   pragma Assert (N.Bit_Length (2 ** 61) = 0);
   pragma Assert (N.Bit_Length (2 ** 61 + 1) = 8);
   -- Same inherited compression/padding on supported small input and chunks.
   pragma Assert (N.Hash (Data) = Attest.SHA256.Hash (Data));
   for I in Data'Range loop N.Update (C, Attest.Byte_Array'(0 => Data (I))); end loop;
   pragma Assert (N.Final (C) = Attest.SHA256.Hash (Data));
end Provider_Length_Controls;

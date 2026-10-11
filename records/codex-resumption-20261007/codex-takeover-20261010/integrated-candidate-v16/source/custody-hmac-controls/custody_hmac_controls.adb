with Attest;
with Attest.SHA256;
with Worldline.Custody_Hmac;
procedure Custody_Hmac_Controls is
   package H renames Worldline.Custody_Hmac;
   use type Attest.Byte_Array;
   function Bytes (S : String) return Attest.Byte_Array is
      Result : Attest.Byte_Array (1 .. S'Length);
   begin
      for I in Result'Range loop
         Result (I) := Character'Pos (S (S'First + I - 1));
      end loop;
      return Result;
   end Bytes;
   function Hex (D : Attest.SHA256.Digest) return String is
      Alphabet : constant String := "0123456789abcdef";
      Result : String (1 .. D'Length * 2);
      Cursor : Positive := Result'First;
   begin
      for B of D loop
         Result (Cursor) := Alphabet (Natural (B) / 16 + 1);
         Result (Cursor + 1) := Alphabet (Natural (B) mod 16 + 1);
         Cursor := Cursor + 2;
      end loop;
      return Result;
   end Hex;
   Short_Key : constant Attest.Byte_Array (1 .. 20) := (others => 16#0B#);
   Long_Key : constant Attest.Byte_Array (1 .. 131) := (others => 16#AA#);
   Shifted_Key : constant Attest.Byte_Array (7 .. 7 + Short_Key'Length - 1) := (others => 16#0B#);
begin
   --  Expected data/digests are literal RFC 4231 sections 4.2, 4.3, 4.7.
   pragma Assert (Hex (H.Mac (Short_Key, Bytes ("Hi There"))) =
     "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7");
   pragma Assert (Hex (H.Mac (Bytes ("Jefe"), Bytes ("what do ya want for nothing?"))) =
     "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843");
   pragma Assert (Hex (H.Mac (Long_Key, Bytes ("Test Using Larger Than Block-Size Key - Hash Key First"))) =
     "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54");
   pragma Assert (H.Mac (Shifted_Key, Bytes ("Hi There")) = H.Mac (Short_Key, Bytes ("Hi There")));
   pragma Assert (H.Mac (Short_Key, Bytes ("Hi There!")) /= H.Mac (Short_Key, Bytes ("Hi There")));
end Custody_Hmac_Controls;

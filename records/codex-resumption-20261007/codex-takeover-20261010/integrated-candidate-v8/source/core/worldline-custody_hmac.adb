package body Worldline.Custody_Hmac with SPARK_Mode is
   function Normalize (Key : Attest.Byte_Array) return Key_Block is
      Result : Key_Block := (others => 0);
   begin
      if Key'Length > SHA.Block_Bytes then
         Result (SHA.Digest'Range) := SHA.Hash (Key);
      else
         for I in Key_Block'Range loop
            if I < Key'Length then
               Result (I) := Key (Key'First + I);
            end if;
            pragma Loop_Invariant
              (for all J in Key_Block'First .. I =>
                 Result (J) =
                   (if J < Key'Length then Key (Key'First + J) else 0));
         end loop;
      end if;
      return Result;
   end Normalize;

   function Mac (Key, Message : Attest.Byte_Array) return SHA.Digest is
      K0 : constant Key_Block := Normalize (Key);
      Inner_Pad, Outer_Pad : Key_Block := (others => 0);
      Inner_Context : SHA.Context := SHA.Initial;
      Outer_Context : SHA.Context := SHA.Initial;
   begin
      for I in Key_Block'Range loop
         Inner_Pad (I) := K0 (I) xor 16#36#;
         Outer_Pad (I) := K0 (I) xor 16#5C#;
         pragma Loop_Invariant
           (for all J in Key_Block'First .. I =>
              Inner_Pad (J) = (K0 (J) xor 16#36#) and then
              Outer_Pad (J) = (K0 (J) xor 16#5C#));
      end loop;
      SHA.Update (Inner_Context, Inner_Pad);
      SHA.Update (Inner_Context, Message);
      SHA.Update (Outer_Context, Outer_Pad);
      SHA.Update (Outer_Context, SHA.Final (Inner_Context));
      return SHA.Final (Outer_Context);
   end Mac;
end Worldline.Custody_Hmac;

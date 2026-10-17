with Interfaces;
with Worldline.Producer_Bytes;
package body Worldline.Confinement_Filter with SPARK_Mode is
   package B renames Worldline.Producer_Bytes;
   subtype U32 is Interfaces.Unsigned_32;
   use type U32;
   type Instruction is record
      Code : Natural;
      True_Jump, False_Jump : Natural;
      Operand : U32;
   end record;
   type Program is array (Natural range <>) of Instruction;
   Thread_Flags : constant U32 := 16#10000# or 16#100# or 16#800#;
   Allow : constant U32 := 16#7FFF0000#;
   Deny : constant U32 := 16#00050001#;
   Reference : constant Program :=
     ((16#20#, 0, 0, 4),
      (16#15#, 1, 0, 16#C00000B7#),
      (16#06#, 0, 0, 16#80000000#),
      (16#20#, 0, 0, 0),
      (16#15#, 0, 1, 221), (16#06#, 0, 0, Deny),
      (16#15#, 0, 1, 281), (16#06#, 0, 0, Deny),
      (16#15#, 0, 1, 435), (16#06#, 0, 0, 16#00050026#),
      (16#15#, 0, 1, 117), (16#06#, 0, 0, Deny),
      (16#15#, 0, 1, 268), (16#06#, 0, 0, Deny),
      --  The constructor denies every unshare call but preserves ENOSPC for
      --  CLONE_NEWUSER. Recognize its actual flags load and branch, not an
      --  older expected-program projection that no longer matches the input.
      (16#15#, 0, 4, 97),
      (16#20#, 0, 0, 16),
      (16#45#, 1, 0, 16#10000000#),
      (16#06#, 0, 0, Deny), (16#06#, 0, 0, 16#0005001C#),
      (16#15#, 1, 0, 220), (16#06#, 0, 0, Allow),
      (16#20#, 0, 0, 16),
      (16#54#, 0, 0, Thread_Flags or 16#FF#),
      (16#15#, 1, 0, Thread_Flags),
      (16#06#, 0, 0, Deny), (16#06#, 0, 0, Allow));
   function Establishes (Encoded_Program : String) return Boolean is
      Actual : constant B.Decoded := B.Base64 (Encoded_Program);
      function Octet (Index : Natural) return Natural is
      begin
         if Index >= Actual.Length or else Index = Natural'Last then
            return 0;
         end if;
         return Character'Pos (Actual.Data (Index + 1));
      end Octet;
   begin
      if not Actual.Valid or else Actual.Length /= Reference'Length * 8 then return False; end if;
      for I in Reference'Range loop
         if Octet (I * 8) + Octet (I * 8 + 1) * 256 /= Reference (I).Code or else
           Octet (I * 8 + 2) /= Reference (I).True_Jump or else
           Octet (I * 8 + 3) /= Reference (I).False_Jump then return False; end if;
         for J in 0 .. 3 loop
            if U32 (Octet (I * 8 + 4 + J)) /=
              (Reference (I).Operand / 2 ** (J * 8)) mod 256 then return False; end if;
         end loop;
      end loop;
      return True;
   end Establishes;
end Worldline.Confinement_Filter;

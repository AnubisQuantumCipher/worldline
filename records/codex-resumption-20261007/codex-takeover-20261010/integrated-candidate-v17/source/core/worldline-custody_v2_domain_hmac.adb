with Interfaces;
package body Worldline.Custody_V2_Domain_Hmac with SPARK_Mode is
   use type E.Q.Byte;
   use type E.Count;
   use type Interfaces.Unsigned_64;
   subtype Block is Attest.Byte_Array (0 .. SHA.Block_Bytes - 1);
   procedure Feed (Context : in out SHA.Context; Data : E.Bytes; Item : E.Span)
      with Pre => E.C.P.Valid (Data, Item), Always_Terminates,
      Post => SHA.Absorbed (Context) = SHA.Absorbed (Context'Old) + Interfaces.Unsigned_64 (Item.Length)
   is
      Before : constant Interfaces.Unsigned_64 := SHA.Absorbed (Context);
   begin
      if Item.Length > 0 then
         for I in E.Count range 0 .. Item.Length - 1 loop
            pragma Loop_Variant (Increases => I);
            pragma Loop_Invariant (SHA.Absorbed (Context) = Before + Interfaces.Unsigned_64 (I));
            SHA.Update (Context, Attest.Byte_Array'(0 => Data (Item.First + I)));
         end loop;
      end if;
   end Feed;
   function Mac (Data : E.Bytes; Key, Message : E.Span; Domain : String)
      return SHA.Digest
   is
   begin
      return Mac (Data, Data, Key, Message, Domain);
   end Mac;
   function Mac (Key_Data, Message_Data : E.Bytes;
                 Key, Message : E.Span; Domain : String)
      return SHA.Digest
   is
      K0, Inner_Pad, Outer_Pad : Block := (others => 0);
      Inner_Context, Outer_Context : SHA.Context := SHA.Initial;
   begin
      if Key.Length > SHA.Block_Bytes then
         K0 (SHA.Digest'Range) := C.G.Hash (Key_Data, Key);
      elsif Key.Length > 0 then
         for I in E.Count range 0 .. Key.Length - 1 loop
            pragma Loop_Variant (Increases => I);
            K0 (Natural (I)) := Key_Data (Key.First + I);
         end loop;
      end if;
      for I in Block'Range loop
         pragma Loop_Variant (Increases => I);
         Inner_Pad (I) := K0 (I) xor 16#36#;
         Outer_Pad (I) := K0 (I) xor 16#5C#;
      end loop;
      SHA.Update (Inner_Context, Inner_Pad);
      for Character_Byte of Domain loop
         SHA.Update (Inner_Context, Attest.Byte_Array'(0 => Character'Pos (Character_Byte)));
      end loop;
      Feed (Inner_Context, Message_Data, Message);
      SHA.Update (Outer_Context, Outer_Pad);
      SHA.Update (Outer_Context, SHA.Final (Inner_Context));
      return SHA.Final (Outer_Context);
   end Mac;
end Worldline.Custody_V2_Domain_Hmac;

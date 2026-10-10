package body Worldline.Archive_Base64 with SPARK_Mode is
   procedure Decode
     (Data : Q.Byte_Array; Item : Span; Result : out Q.Byte_Array) is
   begin
      --  Establish complete initialization before the prefix invariant reads.
      Result := (others => 0);
      for I in Result'Range loop
         Result (I) := Decoded_Byte (Data, Item, I - Result'First);
         pragma Loop_Invariant
           (for all J in Result'First .. I =>
              Result (J) = Decoded_Byte (Data, Item, J - Result'First));
      end loop;
   end Decode;
end Worldline.Archive_Base64;

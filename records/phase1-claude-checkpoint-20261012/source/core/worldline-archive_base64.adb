package body Worldline.Archive_Base64 with SPARK_Mode is
   procedure Decode
     (Data : Q.Byte_Array; Item : Span; Result : out Q.Byte_Array) is
   begin
      --  Construct the complete value without an incremental partial prefix.
      --  Each component retains the checked public byte projection, and the
      --  unchanged complete Post checks the final every-byte correspondence.
      Result :=
        [for I in Result'Range =>
           Decoded_Byte (Data, Item, I - Result'First)];
   end Decode;
end Worldline.Archive_Base64;

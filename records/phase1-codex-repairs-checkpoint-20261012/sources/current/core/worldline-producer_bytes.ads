package Worldline.Producer_Bytes with SPARK_Mode is
   type Decoded (Length : Natural) is record
      Valid : Boolean;
      Data : String (1 .. Length);
   end record;
   type Extent is record
      Length : Natural;
      Valid : Boolean;
   end record;
   function Base64_Extent (Encoded : String) return Extent with Global => null;
   procedure Decode_Base64 (Encoded : String; Output : out String; Valid : out Boolean) with Global => null;
   function Base64 (Encoded : String) return Decoded with Global => null;
   function Digest (Data : String) return String with Global => null,
      Post => Digest'Result'Length = 64;
end Worldline.Producer_Bytes;

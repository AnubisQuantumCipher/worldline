with Ada.Text_IO;
with Worldline.Producer_Bytes;

procedure Decoder_Controls is
   package B renames Worldline.Producer_Bytes;

   procedure Require (Condition : Boolean; Label : String) is
   begin
      if not Condition then
         raise Program_Error with Label;
      end if;
   end Require;

   procedure Verify
     (Encoded, Expected : String; Accepted : Boolean := True)
   is
      Extent : constant B.Extent := B.Base64_Extent (Encoded);
      Value : constant B.Decoded := B.Base64 (Encoded);
      Output : String (7 .. 6 + Expected'Length) := (others => '#');
      Poison : String (7 .. 11) := (others => '#');
      Valid : Boolean;
   begin
      Require (Extent.Valid = Accepted, "extent validity: " & Encoded);
      Require (Value.Valid = Accepted, "value validity: " & Encoded);
      if Accepted then
         Require (Extent.Length = Expected'Length, "extent length");
         Require (Value.Data = Expected, "value bytes");
      else
         Require (Extent.Length = 0 and Value.Length = 0, "failure extent");
      end if;
      B.Decode_Base64 (Encoded, Output, Valid);
      Require (Valid = Accepted, "decode validity");
      if Accepted then
         Require (Output = Expected, "shifted output bytes");
      else
         B.Decode_Base64 (Encoded, Poison, Valid);
         Require (not Valid, "invalid input with nonempty output");
         Require
           ((for all C of Poison => C = Character'Val (0)),
            "failure must clear every output byte");
      end if;
      if Accepted then
         declare
            Too_Long : String (7 .. 7 + Expected'Length) := (others => '#');
         begin
            B.Decode_Base64 (Encoded, Too_Long, Valid);
            Require (not Valid, "oversized output rejected");
            Require ((for all C of Too_Long => C = Character'Val (0)),
                     "oversized output cleared");
         end;
         if Expected'Length > 0 then
            declare
               Too_Short : String (7 .. 5 + Expected'Length) := (others => '#');
               High : String
                 (Positive'Last - (Expected'Length - 1) .. Positive'Last)
                 := (others => '#');
            begin
               B.Decode_Base64 (Encoded, Too_Short, Valid);
               Require (not Valid, "undersized output rejected");
               Require ((for all C of Too_Short => C = Character'Val (0)),
                        "partial output cleared");
               B.Decode_Base64 (Encoded, High, Valid);
               Require (Valid and then High = Expected, "high output bound");
            end;
         end if;
      end if;
      if Encoded'Length > 0 then
         declare
            High_Input : constant String
              (Positive'Last - (Encoded'Length - 1) .. Positive'Last) := Encoded;
            High_Extent : constant B.Extent := B.Base64_Extent (High_Input);
         begin
            Require (High_Extent.Valid = Extent.Valid and then
                     High_Extent.Length = Extent.Length, "high input extent");
            B.Decode_Base64 (High_Input, Output, Valid);
            Require (Valid = Accepted, "high input validity");
            if Accepted then Require (Output = Expected, "high input bytes"); end if;
         end;
      end if;
   end Verify;
begin
   Verify ("", "");
   Verify ("Zg==", "f");
   Verify ("Zm8=", "fo");
   Verify ("Zm9v", "foo");
   Verify ("Zm9vYg==", "foob");
   Verify ("Zm9vYmE=", "fooba");
   Verify ("Zm9vYmFy", "foobar");
   Verify ("AA==", String'(1 => Character'Val (0)));
   Verify ("/w==", String'(1 => Character'Last));
   -- Existing permissive accepted inputs must remain accepted.
   Verify ("Zm9v====", "foo");
   Verify ("Zh==", "f");
   Verify ("Zm9=", "fo");
   Verify ("Z", "", False);
   Verify ("Zg", "", False);
   Verify ("Zg=", "", False);
   Verify ("Zm8", "", False);
   Verify ("=", "", False);
   Verify ("====", "", False);
   Verify ("Z=g=", "", False);
   Verify ("Zg==Zg==", "", False);
   Verify ("Zm9v!", "", False);
   Verify ("Zm9v=Z", "", False);
   Verify ("Zg==" & Character'Val (10), "", False);
   Verify (" Zg==", "", False);
   Verify ("Zg__", "", False);
   declare
      Empty : String (Positive'Last .. Positive'Last - 1);
      Valid : Boolean;
   begin
      B.Decode_Base64 ("", Empty, Valid);
      Require (Valid and then Empty = "", "high null output");
   end;
   Ada.Text_IO.Put_Line ("decoder controls passed");
end Decoder_Controls;

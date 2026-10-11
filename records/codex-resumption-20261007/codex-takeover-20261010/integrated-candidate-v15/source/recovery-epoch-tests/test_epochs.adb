--  Additive actual-library controls; source only, not yet built or executed.
--  The original resource fixtures and proof requirements remain mandatory.
with Ada.Assertions;
with Interfaces;
with Resource_Quantities;
with Resource_Reservation_Transition;
with Worldline.Recovery_Authorization_V3;
with Worldline.Recovery_Authorization_V3_Wire;

procedure Test_Epochs is
   package Q renames Resource_Quantities;
   package T renames Resource_Reservation_Transition;
   package R renames Worldline.Recovery_Authorization_V3;
   package W renames Worldline.Recovery_Authorization_V3_Wire;
   use type Interfaces.Unsigned_8;
   use type Interfaces.Integer_64;
   Data : constant Q.Byte_Array := [1 .. 8 => 0, 9 => 1, 10 => 0];
   Empty : constant R.Optional_Epoch :=
     (Present => True, Value => (Negative => False, First => 1, Length => 0));
   Signed_Zero : constant R.Optional_Epoch :=
     (Present => True, Value => (Negative => True, First => 1, Length => 8));
   Wide : constant R.Optional_Epoch :=
     (Present => True, Value => (Negative => False, First => 1, Length => 9));
   Padded_Wide : constant R.Optional_Epoch :=
     (Present => True, Value => (Negative => False, First => 1, Length => 10));
   Negative_Wide : constant R.Optional_Epoch :=
     (Present => True, Value => (Negative => True, First => 1, Length => 9));
   Invalid_Span : constant R.Optional_Epoch :=
     (Present => True, Value => (Negative => False, First => 10, Length => 9));
   Absent : constant R.Optional_Epoch := (Present => False);
   Raw : W.Raw_Epoch;
begin
   --  Byte specimen is JACKAL status=exact parsed=2^64. It exceeds the
   --  bounded recovery API; arithmetic evidence is informational, not proof.
   Ada.Assertions.Assert (T.Epoch_Valid (Data, Wide));
   Ada.Assertions.Assert (T.Epoch_Valid (Data, Padded_Wide));
   Ada.Assertions.Assert (R.Same (Data, Wide, Padded_Wide));
   Raw := W.Encode_Original (Data, Padded_Wide);
   Ada.Assertions.Assert (W.Well_Formed (Data, Raw));
   Ada.Assertions.Assert (Raw.Length = 9);
   Ada.Assertions.Assert (R.Same (Data, Wide, W.Decode (Raw)));

   Ada.Assertions.Assert (T.Epoch_Valid (Data, Signed_Zero));
   Ada.Assertions.Assert (R.Same (Data, Empty, Signed_Zero));
   Raw := W.Encode_Original (Data, Signed_Zero);
   Ada.Assertions.Assert (W.Well_Formed (Data, Raw));
   Ada.Assertions.Assert (Raw.Present = 1 and then Raw.Length = 0);
   Ada.Assertions.Assert (R.Same (Data, Empty, W.Decode (Raw)));

   Raw := W.Encode_Original (Data, Absent);
   Ada.Assertions.Assert (W.Well_Formed (Data, Raw));
   Ada.Assertions.Assert (not W.Decode (Raw).Present);
   Ada.Assertions.Assert (not R.Same (Data, Absent, Absent));
   Ada.Assertions.Assert (not R.Same (Data, Empty, Absent));
   Ada.Assertions.Assert (not R.Same (Data, Wide, Empty));

   Raw := W.Encode_Original (Data, Negative_Wide);
   Ada.Assertions.Assert (not W.Well_Formed (Data, Raw));
   Raw := W.Encode_Original (Data, Invalid_Span);
   Ada.Assertions.Assert (not W.Well_Formed (Data, Raw));
   Ada.Assertions.Assert (not R.Same (Data, Invalid_Span, Invalid_Span));
   Ada.Assertions.Assert (not R.Same (Data, Negative_Wide, Negative_Wide));
end Test_Epochs;

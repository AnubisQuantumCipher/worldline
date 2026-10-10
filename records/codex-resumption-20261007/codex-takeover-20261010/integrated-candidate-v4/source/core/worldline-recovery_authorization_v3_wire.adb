package body Worldline.Recovery_Authorization_V3_Wire with SPARK_Mode is
   --  Independent induction over the original exact prefix equations.
   procedure Equal_Prefix
     (Data : Q.Byte_Array; Left, Right : Q.Quantity; Count : Q.Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Q.Span_Valid (Data, Left) and then Q.Span_Valid (Data, Right)
       and then Left.First = Right.First and then Count <= Left.Length
       and then Count <= Right.Length,
     Post => Q.Prefix_Reference (Data, Left, Count) =
       Q.Prefix_Reference (Data, Right, Count),
     Subprogram_Variant => (Decreases => Count);
   procedure Equal_Prefix
     (Data : Q.Byte_Array; Left, Right : Q.Quantity; Count : Q.Byte_Count) is
   begin
      if Count > 0 then
         Equal_Prefix (Data, Left, Right, Count - 1);
         pragma Assert
           (Q.Digit (Data, Left, Count - 1) =
            Q.Digit (Data, Right, Count - 1));
      end if;
   end Equal_Prefix;

   procedure Zero_Padding
     (Data : Q.Byte_Array; Item : Q.Quantity; Count : Q.Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Q.Span_Valid (Data, Item) and then Count <= Item.Length
       and then (for all Offset in Q.Byte_Count range Count .. Item.Length =>
         (if Offset < Item.Length then Q.Digit (Data, Item, Offset) = 0)),
     Post => Q.Prefix_Reference (Data, Item, Count) = Q.Magnitude (Data, Item),
     Subprogram_Variant => (Decreases => Item.Length - Count);
   procedure Zero_Padding
     (Data : Q.Byte_Array; Item : Q.Quantity; Count : Q.Byte_Count) is
   begin
      if Count < Item.Length then
         Zero_Padding (Data, Item, Count + 1);
         pragma Assert (Q.Digit (Data, Item, Count) = 0);
         pragma Assert
           (Q.Prefix_Reference (Data, Item, Count + 1) =
            Q.Prefix_Reference (Data, Item, Count));
      else
         pragma Assert
           (Q.Prefix_Reference (Data, Item, Count) =
            Q.Prefix_Value (Data, Item, Item.Length));
      end if;
   end Zero_Padding;

   procedure Positive_Prefix
     (Data : Q.Byte_Array; Item : Q.Quantity; Count : Q.Byte_Count)
   with Ghost, Global => null, Always_Terminates,
     Pre => Count > 0 and then Q.Digit (Data, Item, Count - 1) > 0,
     Post => Q.Prefix_Reference (Data, Item, Count) > 0;
   procedure Positive_Prefix
     (Data : Q.Byte_Array; Item : Q.Quantity; Count : Q.Byte_Count) is
   begin
      pragma Assert (Q.Prefix_Reference (Data, Item, Count - 1) >= 0);
      pragma Assert (Q.Power_Reference (Count - 1) >= 1);
      pragma Assert
        (Q.Prefix_Reference (Data, Item, Count) =
           Q.Prefix_Reference (Data, Item, Count - 1) +
           SPARK.Big_Integers.To_Big_Integer
             (Q.Digit (Data, Item, Count - 1)) * Q.Power_Reference (Count - 1));
   end Positive_Prefix;

   function Encode_Original (Data : Q.Byte_Array; Epoch : R.Optional_Epoch)
      return Raw_Epoch
   is
      Count : Q.Byte_Count;
   begin
      if not Epoch.Present then
         return (Present => 0, Negative => 0, First => 1, Length => 0);
      elsif not T.Epoch_Valid (Data, Epoch) then
         return (Present => 255, Negative => 0, First => 1, Length => 0);
      end if;
      Count := Epoch.Value.Length;
      while Count > 0 loop
         pragma Loop_Invariant (Count <= Epoch.Value.Length);
         pragma Loop_Invariant
           (for all Offset in Q.Byte_Count range Count .. Epoch.Value.Length =>
             (if Offset < Epoch.Value.Length then
                Q.Digit (Data, Epoch.Value, Offset) = 0));
         pragma Loop_Variant (Decreases => Count);
         exit when Q.Digit (Data, Epoch.Value, Count - 1) /= 0;
         Count := Count - 1;
      end loop;
      Zero_Padding (Data, Epoch.Value, Count);
      if Count = 0 then
         pragma Assert (Q.Value (Data, Epoch.Value) = 0);
         return (Present => 1, Negative => 0, First => 1, Length => 0);
      end if;
      Positive_Prefix (Data, Epoch.Value, Count);
      pragma Assert (Q.Magnitude (Data, Epoch.Value) > 0);
      declare
         Canonical : constant Q.Quantity :=
           (Negative => False, First => Epoch.Value.First, Length => Count);
      begin
         Equal_Prefix (Data, Epoch.Value, Canonical, Count);
         pragma Assert (Q.Magnitude (Data, Canonical) =
                          Q.Magnitude (Data, Epoch.Value));
         pragma Assert (not Epoch.Value.Negative);
         pragma Assert (Q.Value (Data, Canonical) = Q.Value (Data, Epoch.Value));
         return (Present => 1, Negative => 0,
                 First => Interfaces.Integer_64 (Canonical.First),
                 Length => Interfaces.Integer_64 (Canonical.Length));
      end;
   end Encode_Original;

   function Decide (Data : Q.Byte_Array; Raw : Raw_Request) return Raw_Result is
      Action : constant R.Recovery_Action := Selected_Action (Data, Raw);
   begin
      return
        (Action => R.Recovery_Action'Pos (Action),
         State => R.Use_State'Pos
           (R.Next_State (R.Use_State'Val (Raw.State), Action)));
   end Decide;
end Worldline.Recovery_Authorization_V3_Wire;

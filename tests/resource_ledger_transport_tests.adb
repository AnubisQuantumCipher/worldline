with Ada.Text_IO;
with Resource_Quantities;
with Resource_Ledger;
with Resource_Scoped_Run_Ledger_Wire;
with Worldline.Resource_Ledger_C_API;

-- Ordinary owned storage: these cases exercise actual typed refusal handlers.
procedure Resource_Ledger_Transport_Tests is
   package Q renames Resource_Quantities;
   package L renames Resource_Ledger;
   package T renames Worldline.Resource_Ledger_C_API;
   use type T.U8;
   use type Q.Quantity;
   use type Q.Byte_Count;
   use type L.Result_Status;

   procedure Check_Empty_Decoders is
      package W renames Resource_Scoped_Run_Ledger_Wire;
      Data : constant Q.Byte_Array (1 .. 0) := [others => 0];
      H : W.Raw_History_Array (7 .. 6);
      B : W.Raw_Bucket_Array (7 .. 6);
      P : W.Raw_Projection_Array (7 .. 6);
      F : W.Raw_Facts_Array (7 .. 6);
      DH : constant W.S.History_Array := W.Decode_History (Data, H);
      DB : constant W.S.Bucket_Array := W.Decode_Bucket (Data, B);
      DP : constant W.S.Projection_Array := W.Decode_Projection (Data, P);
      DF : constant W.S.Facts_Array := W.Decode_Facts (Data, F);
   begin
      pragma Assert (DH'First = 7 and then DH'Length = 0);
      pragma Assert (DB'First = 7 and then DB'Length = 0);
      pragma Assert (DP'First = 7 and then DP'Length = 0);
      pragma Assert (DF'First = 7 and then DF'Length = 0);
   end Check_Empty_Decoders;

   procedure Check_Compute (Bad_First : Boolean) is
      First : constant Q.Byte_Index := (if Bad_First then 2 else 1);
      Data : aliased Q.Byte_Array := [First => 7];
      Rows : aliased T.Row_Array :=
        [(Reserved => (1, 1, (if Bad_First then 0 else 2)),
          Used => (0, (1, 0, 0)), Output_First => 1, Output_Length => 2)];
      Detail, Total_Data : Q.Byte_Array (1 .. 2) := [others => 165];
      Details : L.Quantity_Array (1 .. 1) := [(False, 1, 1)];
      Total : Q.Quantity := (False, 1, 1);
      Status : L.Result_Status := L.Computed;
      Transport : T.U8;
   begin
      Transport := T.Compute
        (Data'Access, Rows'Access, Detail, Total_Data, Details, Total, Status);
      pragma Assert (Transport = 255 and then Status = L.Invalid_Input);
      pragma Assert (Total = L.Empty and then Details (1) = L.Empty);
      pragma Assert ((for all X of Detail => X = 0));
      pragma Assert ((for all X of Total_Data => X = 0));
      pragma Assert (Data (First) = 7);
   end Check_Compute;

   procedure Check_Headroom (Bad_First : Boolean) is
      First : constant Q.Byte_Index := (if Bad_First then 2 else 1);
      Data : aliased Q.Byte_Array := [First => 7];
      Available : aliased T.Quantity_C :=
        (1, 1, (if Bad_First then 0 else 2));
      Zero : aliased T.Quantity_C := (1, 0, 0);
      Output : Q.Byte_Array (1 .. 2) := [others => 165];
      Result : Q.Quantity := (False, 1, 1);
      Status : L.Result_Status := L.Computed;
      Transport : T.U8;
   begin
      Transport := T.Headroom
        (Data'Access, Available'Access, Zero'Access, Zero'Access,
         Output, Result, Status);
      pragma Assert (Transport = 255 and then Status = L.Invalid_Input);
      pragma Assert (Result = L.Empty);
      pragma Assert ((for all X of Output => X = 0));
      pragma Assert (Data (First) = 7);
   end Check_Headroom;
begin
   Check_Empty_Decoders;
   Check_Compute (True);
   Check_Compute (False);
   Check_Headroom (True);
   Check_Headroom (False);
   Ada.Text_IO.Put_Line ("PASS typed ledger/headroom malformed-input cleanup");
end Resource_Ledger_Transport_Tests;

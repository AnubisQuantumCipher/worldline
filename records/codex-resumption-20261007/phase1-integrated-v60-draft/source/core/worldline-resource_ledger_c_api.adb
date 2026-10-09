with System;
with Resource_Quantities;
with Resource_Ledger;

package body Worldline.Resource_Ledger_C_API with SPARK_Mode => On is
   use type U8;
   use type Size;
   package Q renames Resource_Quantities;
   package L renames Resource_Ledger;
   use type Q.Byte_Count;


   function ABI_Version return Interfaces.Unsigned_32 is (1);
   function Layout_Size (Selector : U8) return Size is
     (case Selector is
         when 1 => Quantity_C'Object_Size / System.Storage_Unit,
         when 2 => Optional_C'Object_Size / System.Storage_Unit,
         when 3 => Row_C'Object_Size / System.Storage_Unit,
         when 4 => Result_C'Object_Size / System.Storage_Unit,
         when others => Size'Last);

   function Layout_Offset (Selector, Field : U8) return Size is
      VQ : constant Quantity_C := (First => 1, Length => 0, Negative => 0);
      VO : constant Optional_C := (Present => 0, Value => VQ);
      VR : constant Row_C := (Reserved => VQ, Used => VO,
                             Output_First => 1, Output_Length => 0);
      VT : constant Result_C := (Status => 0, Total => VQ);
   begin
      pragma Compile_Time_Error (VQ.First'Position /= 0, "Quantity.First");
      pragma Compile_Time_Error (VQ.Length'Position /= 8, "Quantity.Length");
      pragma Compile_Time_Error (VQ.Negative'Position /= 16, "Quantity.Negative");
      pragma Compile_Time_Error (VO.Present'Position /= 0, "Optional.Present");
      pragma Compile_Time_Error (VO.Value'Position /= 8, "Optional.Value");
      pragma Compile_Time_Error (VR.Reserved'Position /= 0, "Row.Reserved");
      pragma Compile_Time_Error (VR.Used'Position /= 24, "Row.Used");
      pragma Compile_Time_Error (VR.Output_First'Position /= 56, "Row.Output_First");
      pragma Compile_Time_Error (VR.Output_Length'Position /= 64, "Row.Output_Length");
      pragma Compile_Time_Error (VT.Status'Position /= 0, "Result.Status");
      pragma Compile_Time_Error (VT.Total'Position /= 8, "Result.Total");
      case Selector is
         when 1 =>
            return (case Field is
              when 1 => 0, when 2 => 8, when 3 => 16, when others => Size'Last);
         when 2 =>
            return (case Field is
              when 1 => 0, when 2 => 8, when others => Size'Last);
         when 3 =>
            return (case Field is
              when 1 => 0, when 2 => 24, when 3 => 56, when 4 => 64,
              when others => Size'Last);
         when 4 =>
            return (case Field is
              when 1 => 0, when 2 => 8, when others => Size'Last);
         when others => return Size'Last;
      end case;
   end Layout_Offset;


   function Shape (V : Quantity_C) return Boolean is
     (V.Negative <= 1 and then V.First >= 1 and then
      V.First <= Size (Q.Byte_Count'Last) and then
      V.Length <= Size (Q.Byte_Count'Last));
   function Shape (V : Optional_C) return Boolean is
     (V.Present <= 1 and then (V.Present = 0 or else Shape (V.Value)));
   function Decode (V : Quantity_C) return Q.Quantity is
     ((Negative => V.Negative = 1, First => Q.Byte_Index (V.First),
       Length => Q.Byte_Count (V.Length)))
   with Pre => Shape (V);
   function Decode (V : Optional_C) return Q.Optional_Quantity is
     (if V.Present = 0 then (Present => False)
      else (Present => True, Value => Decode (V.Value)))
   with Pre => Shape (V);
   function Encode (V : Q.Quantity) return Quantity_C is
     ((First => Size (V.First), Length => Size (V.Length),
       Negative => Boolean'Pos (V.Negative)));

   procedure Read_Byte (Source : Q.Byte; Item : out Q.Byte) is
   begin
      Item := Source;
   end Read_Byte;


   procedure Read_Row (Source : not null access constant Row_Array; Index : Q.Byte_Index; Item : out Row_C)
     with Pre => Index in Source'Range
   is
   begin
      Item := Source (Index);
   end Read_Row;

   procedure Read_Quantity (Source : not null access constant Quantity_C; Item : out Quantity_C)
   is
   begin
      Item := Source.all;
   end Read_Quantity;



   procedure Copy_Data
     (Source : not null access constant Q.Byte_Array; Value : out Q.Byte_Array)
     with Pre => Source'First = 1 and then Value'First = 1
       and then Value'Length = Source'Length
   is
   begin
      for I in Value'Range loop
         Read_Byte (Source (I), Value (I));
      end loop;
   end Copy_Data;


   function Compute
     (Data : not null access constant Resource_Quantities.Byte_Array;
      Rows : not null access constant Row_Array;
      Detail_Arena, Total_Arena : out Resource_Quantities.Byte_Array;
      Typed_Details : out Resource_Ledger.Quantity_Array;
      Total : out Resource_Quantities.Quantity;
      Status : out Resource_Ledger.Result_Status) return U8
   is
   begin
      if Data'First /= 1 or else Rows'First /= 1 or else Detail_Arena'First /= 1 or else Total_Arena'First /= 1 or else Typed_Details'First /= 1 or else Typed_Details'Length /= Rows'Length then Detail_Arena := (others => 0); Total_Arena := (others => 0);
         Typed_Details := (others => L.Empty); Total := L.Empty; Status := L.Invalid_Input; return 255; end if;
      declare
         Arena : Q.Byte_Array (1 .. Q.Byte_Count (Data'Length));
         Blank_Row : constant L.Reservation_Row :=
           (Reserved => L.Empty, Used => (Present => False));
         Blank_Slot : constant L.Output_Span := (First => 1, Length => 0);
         Typed_Rows : L.Reservation_Array (1 .. Q.Byte_Count (Rows'Length)) :=
           (others => Blank_Row);
         Slots : L.Span_Array (Typed_Rows'Range) := (others => Blank_Slot);
      begin
         Copy_Data (Data, Arena);
         for I in Typed_Rows'Range loop
            declare
               V : Row_C;
            begin
               Read_Row (Rows, I, V);
               if not Shape (V.Reserved) or else not Shape (V.Used) or else
                 V.Output_First < 1 or else
                 V.Output_First > Size (Q.Byte_Count'Last) or else
                 V.Output_Length > Size (Q.Byte_Count'Last)
               then
                  Detail_Arena := (others => 0); Total_Arena := (others => 0);
         Typed_Details := (others => L.Empty); Total := L.Empty; Status := L.Invalid_Input; return 255;
               end if;
               Typed_Rows (I) := (Decode (V.Reserved), Decode (V.Used));
               Slots (I) := (Q.Byte_Index (V.Output_First),
                             Q.Byte_Count (V.Output_Length));
            end;
         end loop;
         L.Compute (Arena, Typed_Rows, Slots, Detail_Arena, Total_Arena,
                    Typed_Details, Total, Status);
         return 0;
      end;
   exception
      when others => Detail_Arena := (others => 0); Total_Arena := (others => 0);
         Typed_Details := (others => L.Empty); Total := L.Empty; Status := L.Invalid_Input; return 255;
   end Compute;
   function Headroom
     (Data : not null access constant Resource_Quantities.Byte_Array;
      Available, Withheld, Floor : not null access constant Quantity_C;
      Output_Arena : out Resource_Quantities.Byte_Array;
      Typed_Result : out Resource_Quantities.Quantity;
      Status : out Resource_Ledger.Result_Status) return U8
   is
   begin
      if Data'First /= 1 or else Output_Arena'First /= 1 then Output_Arena := (others => 0); Typed_Result := L.Empty; Status := L.Invalid_Input; return 255; end if;
      declare
         A, W, F : Quantity_C;
      begin
         Read_Quantity (Available, A);
         Read_Quantity (Withheld, W);
         Read_Quantity (Floor, F);
         if not Shape (A) or else not Shape (W) or else not Shape (F) then
            Output_Arena := (others => 0); Typed_Result := L.Empty; Status := L.Invalid_Input; return 255;
         end if;
         declare
            Arena : Q.Byte_Array (1 .. Q.Byte_Count (Data'Length));
            begin
            Copy_Data (Data, Arena);
            L.Compute_Headroom
              (Arena, Decode (A), Decode (W), Decode (F),
               Output_Arena, Typed_Result, Status);
            return 0;
         end;
      end;
   exception
      when others => Output_Arena := (others => 0); Typed_Result := L.Empty; Status := L.Invalid_Input; return 255;
   end Headroom;
end Worldline.Resource_Ledger_C_API;

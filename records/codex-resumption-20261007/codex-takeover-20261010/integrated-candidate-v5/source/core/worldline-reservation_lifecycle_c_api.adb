with System;
with Resource_Reservation_Lifecycle;
with Worldline.Resources;

package body Worldline.Reservation_Lifecycle_C_API with SPARK_Mode => On is
   use type U8;
   use type Size;
   package L renames Resource_Reservation_Lifecycle;
   package R renames Worldline.Resources;
   use type L.Result_Status;


   function ABI_Version return Interfaces.Unsigned_32 is (1);
   function Layout_Size return Size is
     (Row_C'Object_Size / System.Storage_Unit);
   function Layout_Offset (Field : U8) return Size is
      Row : constant Row_C := (1, 0, 0);
   begin
      pragma Compile_Time_Error (Row.First'Position /= 0, "Row.First");
      pragma Compile_Time_Error (Row.Length'Position /= 8, "Row.Length");
      pragma Compile_Time_Error (Row.Observed'Position /= 16, "Row.Observed");
      return (case Field is
         when 1 => 0,
         when 2 => 8,
         when 3 => 16,
         when others => Size'Last);
   end Layout_Offset;


   procedure Read_Byte (Source : U8; Item : out U8) is
   begin
      Item := Source;
   end Read_Byte;


   procedure Read_Row (Source : not null access constant Row_Array; Index : R.Byte_Index; Item : out Row_C)
     with Pre => Index in Source'Range
   is
   begin
      Item := Source (Index);
   end Read_Row;

   procedure Copy_Data
     (Source : not null access constant R.Byte_Array; Value : out R.Byte_Array)
     with Pre => Source'First = 1 and then Value'First = 1
       and then Value'Length = Source'Length
   is
   begin
      for I in Value'Range loop
         Read_Byte (Source (I), Value (I));
      end loop;
   end Copy_Data;

   function Plan
     (Data : not null access constant Worldline.Resources.Byte_Array;
      Rows : not null access constant Row_Array;
      Mode, Present : U8; Requested_First, Requested_Length : Size;
      Mask : out Resource_Reservation_Lifecycle.Removal_Array) return U8
   is
   begin
      Mask := (others => False);
      if Present > 1 or else
        (Present = 1 and then (Requested_First < 1 or else
          Requested_First > Size (R.Byte_Count'Last) or else
          Requested_Length > Size (R.Byte_Count'Last)))
      then return 255; end if;
      if Data'First /= 1 or else Rows'First /= 1 or else Mask'First /= 1 then return 255; end if;
      declare
         Arena : R.Byte_Array (1 .. R.Byte_Count (Data'Length));
         Blank : constant L.Reservation_Entry :=
           (Identity => (First => 1, Length => 0), Observed => L.Unknown);
         Typed_Rows : L.Entry_Array (1 .. R.Byte_Count (Rows'Length)) :=
           (others => Blank);
         Requested : constant L.Optional_Identity :=
           (if Present = 0 then (Present => False)
            else (Present => True,
                  Value => (R.Byte_Index (Requested_First),
                            R.Byte_Count (Requested_Length))));
         Selected_Mode : constant L.Operation :=
           (case Mode is
              when 1 => L.Release_Exact,
              when 2 => L.Reconcile_Observed,
              when others => L.Unknown_Operation);
         Status : L.Result_Status;
      begin
         Copy_Data (Data, Arena);
         for I in Typed_Rows'Range loop
            declare
               Row : Row_C;
            begin
               Read_Row (Rows, I, Row);
               if Row.First < 1 or else Row.First > Size (R.Byte_Count'Last) or else
                 Row.Length > Size (R.Byte_Count'Last) or else Row.Observed > 2
               then
                  return 255;
               end if;
               Typed_Rows (I) :=
                 (Identity => (R.Byte_Index (Row.First), R.Byte_Count (Row.Length)),
                  Observed => L.Liveness'Val (Row.Observed));
            end;
         end loop;
         L.Plan (Arena, Typed_Rows, Requested, Selected_Mode, Mask, Status);
         return L.Result_Status'Pos (Status);
      end;
   exception
      when others => return 255;
   end Plan;
end Worldline.Reservation_Lifecycle_C_API;

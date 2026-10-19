with Ada.Command_Line;
with Ada.Text_IO;
with Ada.Unchecked_Conversion;
with System;

--  Test oracle only: reinterpret owned initialized storage using the compiler's
--  actual native layout. Raw wire components are full-range integer types.
--  Equality compares fields, not unspecified record padding.
procedure Raw_Decode_Case is
   package Q renames Resource_Quantities;
   use type Q.Byte_Count;
   Width : constant Q.Byte_Count := Item_Type'Object_Size / System.Storage_Unit;
   subtype Image is Q.Byte_Array (1 .. Width);
   subtype Value_Image is Q.Byte_Array (1 .. Value_Width);
   function Native_View is new Ada.Unchecked_Conversion (Value_Image, Item_Type);

   procedure Check (Source : Image; First : Q.Byte_Index;
                    Count : Q.Byte_Count) is
      Data : constant Q.Byte_Array (First .. First + (Count - 1)) :=
        Source (1 .. Count);
      Expected : constant Item_Type := Native_View (Source (1 .. Value_Width));
      Actual : constant Item_Type := Load (Data);
   begin
      pragma Assert (Actual = Expected);
   end Check;

   procedure Probe_Length (Count : Q.Byte_Count) is
   begin
      if Count > Width + 1 then
         raise Constraint_Error with "probe length exceeds native test bound";
      end if;
      declare
         Data : constant Q.Byte_Array (1 .. Count) := [others => 0];
         Result : constant Item_Type := Load (Data);
         pragma Unreferenced (Result);
      begin
         Ada.Text_IO.Put_Line ("ACCEPTED");
      end;
   end Probe_Length;

   procedure Check_Padding is
      Source : Image := [others => 0];
      Zero : constant Item_Type := Native_View (Source (1 .. Value_Width));
   begin
      pragma Assert (Padding_Valid (Source, Zero));
      pragma Assert (Padding_Valid (Source (1 .. Value_Width), Zero));
      --  A single changed byte is padding iff it changes no native field.
      --  Walk every byte, including nested and trailing alignment padding.
      for I in Source'Range loop
         Source (I) := 255;
         declare
            Native : constant Item_Type := Native_View (Source (1 .. Value_Width));
            Full : constant Boolean := Padding_Valid (Source, Native);
         begin
            pragma Assert (Full = (Native /= Zero));
            if I <= Value_Width then
               pragma Assert
                 (Padding_Valid (Source (1 .. Value_Width), Native) = Full);
            end if;
         end;
         Source (I) := 0;
      end loop;
   end Check_Padding;

   Source : Image;
begin
   if Ada.Command_Line.Argument_Count = 2 then
      Probe_Length (Q.Byte_Count'Value (Ada.Command_Line.Argument (2)));
      return;
   end if;
   pragma Assert (Value_Width > 0 and then Value_Width <= Width);
   for Pattern in 0 .. 3 loop
      for I in Source'Range loop
         Source (I) := (case Pattern is
            when 0 => 0,
            when 1 => 255,
            when 2 => Q.Byte (I mod 256),
            when others => Q.Byte ((I / 256) mod 256));
      end loop;
      Check (Source, 7, Width);
      Check (Source, Q.Byte_Index'Last - (Width - 1), Width);
      Check (Source, 7, Value_Width);
      Check (Source, Q.Byte_Index'Last - (Value_Width - 1), Value_Width);
   end loop;
   Check_Padding;
end Raw_Decode_Case;

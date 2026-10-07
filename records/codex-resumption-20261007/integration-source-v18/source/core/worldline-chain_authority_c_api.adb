with System.Address_To_Access_Conversions;
with System.Storage_Elements;
with Worldline.Chain_Authority_Wire;
package body Worldline.Chain_Authority_C_API with SPARK_Mode => On is
   package W renames Worldline.Chain_Authority_Wire;
   package A renames W.A;
   use System.Storage_Elements;
   use type System.Address;
   use type Interfaces.C.size_t;
   use type Interfaces.C.long;
   use type Interfaces.C.int;
   use type A.Q.Byte_Count;
   package Anchors_Pointers is new System.Address_To_Access_Conversions (W.Raw_Anchors);
   package Row_Pointers is new System.Address_To_Access_Conversions (W.Raw_Row);
   package Result_Pointers is new System.Address_To_Access_Conversions (W.Raw_Result);
   use type Anchors_Pointers.Object_Pointer;
   use type Row_Pointers.Object_Pointer;
   use type Result_Pointers.Object_Pointer;

   procedure Read_Anchors (Address : System.Address; Item : out W.Raw_Anchors)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Anchors_Pointers.Object_Pointer := Anchors_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Anchors;

   procedure Read_Row (Address : System.Address; Item : out W.Raw_Row)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Row_Pointers.Object_Pointer := Row_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Row;

   procedure Write_Result (Address : System.Address; Item : W.Raw_Result)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Result_Pointers.Object_Pointer := Result_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Result;

   function Version return Interfaces.Unsigned_32 is (1);
   function Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long is
      Blank : constant W.Raw_Hash := (others => 0);
      D : constant W.Raw_Digest := (Present => 0, Value => Blank);
      R : constant W.Raw_Row := (others => D);
      H : constant W.Raw_Anchors := (Kind => 0, others => D);
      O : constant W.Raw_Result :=
        (Disposition => 0, Head => Blank, Accepted_Count => 0);
   begin
      pragma Compile_Time_Error (D.Present'Position /= 0, "Digest.Present");
      pragma Compile_Time_Error (D.Value'Position /= 1, "Digest.Value");
      pragma Compile_Time_Error (R.Previous'Position /= 0, "Row.Previous");
      pragma Compile_Time_Error (R.Actual_Payload_Root'Position /= 33, "Row.Actual");
      pragma Compile_Time_Error (R.Stored_Payload_Root'Position /= 66, "Row.Stored_Payload");
      pragma Compile_Time_Error (R.Stored_Head'Position /= 99, "Row.Stored_Head");
      pragma Compile_Time_Error (H.Kind'Position /= 0, "Anchors.Kind");
      pragma Compile_Time_Error (H.Observed_Genesis'Position /= 1, "Anchors.Observed");
      pragma Compile_Time_Error (H.Witnessed_Genesis'Position /= 34, "Anchors.Witnessed_Genesis");
      pragma Compile_Time_Error (H.Witnessed_Head'Position /= 67, "Anchors.Witnessed_Head");
      pragma Compile_Time_Error (O.Disposition'Position /= 0, "Result.Disposition");
      pragma Compile_Time_Error (O.Head'Position /= 1, "Result.Head");
      pragma Compile_Time_Error (O.Accepted_Count'Position /= 40, "Result.Accepted");
      case Kind is
         when 1 => case Field is
            when 0 => return W.Raw_Digest'Size / System.Storage_Unit;
            when 1 => return W.Raw_Digest'Alignment;
            when 2 => return 0;
            when 3 => return 1;
            when others => return -1;
         end case;
         when 2 => case Field is
            when 0 => return W.Raw_Row'Size / System.Storage_Unit;
            when 1 => return W.Raw_Row'Alignment;
            when 2 => return 0;
            when 3 => return 33;
            when 4 => return 66;
            when 5 => return 99;
            when others => return -1;
         end case;
         when 3 => case Field is
            when 0 => return W.Raw_Anchors'Size / System.Storage_Unit;
            when 1 => return W.Raw_Anchors'Alignment;
            when 2 => return 0;
            when 3 => return 1;
            when 4 => return 34;
            when 5 => return 67;
            when others => return -1;
         end case;
         when 4 => case Field is
            when 0 => return W.Raw_Result'Size / System.Storage_Unit;
            when 1 => return W.Raw_Result'Alignment;
            when 2 => return 0;
            when 3 => return 1;
            when 4 => return 40;
            when others => return -1;
         end case;
         when others => return -1;
      end case;
   end Layout;
   function Shape (Address : System.Address; Length : Interfaces.C.size_t) return Boolean is
     (Address /= System.Null_Address and then Length > 0
      and then Length <= Interfaces.C.size_t (Storage_Offset'Last)
      and then Integer_Address (Length - 1) <= Integer_Address'Last - To_Integer (Address));
   function Replay
     (Anchors : System.Address; Anchors_Length : Interfaces.C.size_t;
      Rows : System.Address; Rows_Count, Rows_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Interfaces.C.int
   is
      Stride : constant Interfaces.C.size_t := W.Raw_Row'Size / System.Storage_Unit;
   begin
      if Anchors_Length /= W.Raw_Anchors'Size / System.Storage_Unit
        or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit
        or else not Shape (Anchors, Anchors_Length) or else not Shape (Output, Output_Length)
        or else To_Integer (Anchors) mod W.Raw_Anchors'Alignment /= 0
        or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0
        or else Rows_Count > Interfaces.C.size_t (A.Q.Byte_Count'Last)
        or else Rows_Count > Interfaces.C.size_t'Last / Stride
        or else Rows_Length /= Rows_Count * Stride
        or else (Rows_Length > 0 and then
          (not Shape (Rows, Rows_Length) or else To_Integer (Rows) mod W.Raw_Row'Alignment /= 0))
      then return -1;
      end if;
      declare
         H : W.Raw_Anchors;
         Owned : A.Retained_Rows (1 .. A.Q.Byte_Count (Rows_Count));
      begin
         Read_Anchors (Anchors, H);
         if not W.Well_Formed (H) then return -1; end if;
         for I in Owned'Range loop
            declare
               Raw : W.Raw_Row;
            begin
               Read_Row
                 (Rows + Storage_Offset (Interfaces.C.size_t (I - 1) * Stride), Raw);
               if not W.Well_Formed (Raw) then return -1; end if;
               Owned (I) := W.Decode (Raw);
            end;
         end loop;
         -- All anchors and rows are copied before the output is touched.
         Write_Result (Output, W.Decide (Owned, H));
      end;
      return 0;
   exception when others => return -1;
   end Replay;
end Worldline.Chain_Authority_C_API;

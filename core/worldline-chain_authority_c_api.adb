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

   procedure Read_Anchors (View : access constant Worldline.Chain_Authority_Wire.Raw_Anchors; Item : out Worldline.Chain_Authority_Wire.Raw_Anchors)
     with Exceptional_Cases => (others => True)
   is
   begin
      if View = null then raise Constraint_Error; end if;
      Item := View.all;
   end Read_Anchors;

   procedure Read_Row (View : access constant Raw_Rows; Position : A.Q.Byte_Index; Item : out Worldline.Chain_Authority_Wire.Raw_Row)
     with Exceptional_Cases => (others => True)
   is
   begin
      if View = null or else Position not in View.all'Range then raise Constraint_Error; end if;
      Item := View.all (Position);
   end Read_Row;

   procedure Write_Result (View : access Worldline.Chain_Authority_Wire.Raw_Result; Item : Worldline.Chain_Authority_Wire.Raw_Result)
     with Exceptional_Cases => (others => True)
   is
   begin
      if View = null then raise Constraint_Error; end if;
      View.all := Item;
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
            when 0 => return W.Raw_Digest'Object_Size / System.Storage_Unit;
            when 1 => return W.Raw_Digest'Alignment;
            when 2 => return 0;
            when 3 => return 1;
            when others => return -1;
         end case;
         when 2 => case Field is
            when 0 => return W.Raw_Row'Object_Size / System.Storage_Unit;
            when 1 => return W.Raw_Row'Alignment;
            when 2 => return 0;
            when 3 => return 33;
            when 4 => return 66;
            when 5 => return 99;
            when others => return -1;
         end case;
         when 3 => case Field is
            when 0 => return W.Raw_Anchors'Object_Size / System.Storage_Unit;
            when 1 => return W.Raw_Anchors'Alignment;
            when 2 => return 0;
            when 3 => return 1;
            when 4 => return 34;
            when 5 => return 67;
            when others => return -1;
         end case;
         when 4 => case Field is
            when 0 => return W.Raw_Result'Object_Size / System.Storage_Unit;
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
   function Transport_Valid
     (Anchors : System.Address; Anchors_Length : Interfaces.C.size_t;
      Rows : System.Address; Rows_Count, Rows_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Boolean is
      Stride : constant Interfaces.C.size_t := W.Raw_Row'Object_Size / System.Storage_Unit;
   begin
      return not (Anchors_Length /= W.Raw_Anchors'Object_Size / System.Storage_Unit
        or else Output_Length /= W.Raw_Result'Object_Size / System.Storage_Unit
        or else not Shape (Anchors, Anchors_Length) or else not Shape (Output, Output_Length)
        or else To_Integer (Anchors) mod W.Raw_Anchors'Alignment /= 0
        or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0
        or else Rows_Count > Interfaces.C.size_t (A.Q.Byte_Count'Last)
        or else Rows_Count > Interfaces.C.size_t'Last / Stride
        or else Rows_Length /= Rows_Count * Stride
        or else (Rows_Length > 0 and then
          (not Shape (Rows, Rows_Length) or else To_Integer (Rows) mod W.Raw_Row'Alignment /= 0)));
   end Transport_Valid;

   function Replay
     (Anchors : System.Address; Anchors_Length : Interfaces.C.size_t;
      Rows : System.Address; Rows_Count, Rows_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t;
      Anchors_View : access constant Worldline.Chain_Authority_Wire.Raw_Anchors;
      Rows_View : access constant Raw_Rows;
      Output_View : access Worldline.Chain_Authority_Wire.Raw_Result)
      return Interfaces.C.int
   is
   begin
      if not Transport_Valid (Anchors, Anchors_Length, Rows, Rows_Count, Rows_Length, Output, Output_Length) then return -1;
      end if;
      if Rows_Count > 0 and then
        (Rows_View = null or else Rows_View.all'First /= 1 or else
         Rows_View.all'Length /= Rows_Count) then return -1;
      end if;
      declare
         H : W.Raw_Anchors;
         Owned : A.Retained_Rows (1 .. A.Q.Byte_Count (Rows_Count));
      begin
         Read_Anchors (Anchors_View, H);
         if not W.Well_Formed (H) then return -1; end if;
         for I in Owned'Range loop
            declare
               Raw : W.Raw_Row;
            begin
               Read_Row
                 (Rows_View, I, Raw);
               if not W.Well_Formed (Raw) then return -1; end if;
               Owned (I) := W.Decode (Raw);
            end;
         end loop;
         -- All anchors and rows are copied before the output is touched.
         Write_Result (Output_View, W.Decide (Owned, H));
      end;
      return 0;
   exception when others => return -1;
   end Replay;
end Worldline.Chain_Authority_C_API;

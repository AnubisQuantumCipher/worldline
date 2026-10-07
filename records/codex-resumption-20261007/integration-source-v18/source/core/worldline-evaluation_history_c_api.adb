with System.Address_To_Access_Conversions;
with Evaluation_History;
with Resource_Quantities;
with System.Storage_Elements;

package body Worldline.Evaluation_History_C_API with SPARK_Mode => On is
   package H renames Evaluation_History;
   package R renames Resource_Quantities;
   use type U8;
   use type R.Byte_Count;
   use type Size;
   use type System.Address;
   use System.Storage_Elements;
   package Byte_Pointers is new System.Address_To_Access_Conversions (U8);
   package Row_Pointers is new System.Address_To_Access_Conversions (Row_C);
   package Query_Pointers is new System.Address_To_Access_Conversions (Query_C);
   package Selection_Pointers is new System.Address_To_Access_Conversions (Selection_C);
   use type Byte_Pointers.Object_Pointer;
   use type Row_Pointers.Object_Pointer;
   use type Query_Pointers.Object_Pointer;
   use type Selection_Pointers.Object_Pointer;

   function ABI_Version return Interfaces.Unsigned_32 is (1);
   function Layout_Size (Kind : U8) return Size is
     (case Kind is
        when 1 => Identity_C'Object_Size / System.Storage_Unit,
        when 2 => Epoch_C'Object_Size / System.Storage_Unit,
        when 3 => Cursor_C'Object_Size / System.Storage_Unit,
        when 4 => Row_C'Object_Size / System.Storage_Unit,
        when 5 => Query_C'Object_Size / System.Storage_Unit,
        when 6 => Selection_C'Object_Size / System.Storage_Unit,
        when others => Size'Last);
   function Layout_Offset (Kind, Field : U8) return Size is
      I : constant Identity_C := (0, 0, 0);
      E : constant Epoch_C := (0, 0, 0);
      C : constant Cursor_C := (Present => 0, Sequence => E, Run => I);
      Rw : constant Row_C :=
        (Subject => I, Content => I, Requirement => I, Run => I, Sequence => E,
         State => 0, Outcome => 0);
      Q : constant Query_C :=
        (Subject => I, Content => I, Requirement => I,
         Current_Head => C, Prepared_Evidence => C);
      S : constant Selection_C := (0, 0, 0, 0, 0);
   begin
      pragma Compile_Time_Error (I.Present'Position /= 0, "Identity.Present");
      pragma Compile_Time_Error (I.First'Position /= 8, "Identity.First");
      pragma Compile_Time_Error (I.Length'Position /= 16, "Identity.Length");
      pragma Compile_Time_Error (E.Present'Position /= 0, "Epoch.Present");
      pragma Compile_Time_Error (E.First'Position /= 8, "Epoch.First");
      pragma Compile_Time_Error (E.Length'Position /= 16, "Epoch.Length");
      pragma Compile_Time_Error (C.Present'Position /= 0, "Cursor.Present");
      pragma Compile_Time_Error (C.Sequence'Position /= 8, "Cursor.Sequence");
      pragma Compile_Time_Error (C.Run'Position /= 32, "Cursor.Run");
      pragma Compile_Time_Error (Rw.Subject'Position /= 0, "Row.Subject");
      pragma Compile_Time_Error (Rw.Content'Position /= 24, "Row.Content");
      pragma Compile_Time_Error (Rw.Requirement'Position /= 48, "Row.Requirement");
      pragma Compile_Time_Error (Rw.Run'Position /= 72, "Row.Run");
      pragma Compile_Time_Error (Rw.Sequence'Position /= 96, "Row.Sequence");
      pragma Compile_Time_Error (Rw.State'Position /= 120, "Row.State");
      pragma Compile_Time_Error (Rw.Outcome'Position /= 121, "Row.Outcome");
      pragma Compile_Time_Error (Q.Subject'Position /= 0, "Query.Subject");
      pragma Compile_Time_Error (Q.Content'Position /= 24, "Query.Content");
      pragma Compile_Time_Error (Q.Requirement'Position /= 48, "Query.Requirement");
      pragma Compile_Time_Error (Q.Current_Head'Position /= 72, "Query.Current");
      pragma Compile_Time_Error (Q.Prepared_Evidence'Position /= 128, "Query.Prepared");
      pragma Compile_Time_Error (S.Reason'Position /= 0, "Selection.Reason");
      pragma Compile_Time_Error (S.Head_Kind'Position /= 1, "Selection.Head_Kind");
      pragma Compile_Time_Error (S.Head_Index'Position /= 8, "Selection.Head_Index");
      pragma Compile_Time_Error (S.Failure_Kind'Position /= 16, "Selection.Failure_Kind");
      pragma Compile_Time_Error (S.Failure_Index'Position /= 24, "Selection.Failure_Index");
      case Kind is
         when 1 => return (case Field is when 1 => 0, when 2 => 8, when 3 => 16,
            when others => Size'Last);
         when 2 => return (case Field is when 1 => 0, when 2 => 8, when 3 => 16,
            when others => Size'Last);
         when 3 => return (case Field is when 1 => 0, when 2 => 8, when 3 => 32,
            when others => Size'Last);
         when 4 => return (case Field is when 1 => 0, when 2 => 24, when 3 => 48,
            when 4 => 72, when 5 => 96, when 6 => 120, when 7 => 121,
            when others => Size'Last);
         when 5 => return (case Field is when 1 => 0, when 2 => 24, when 3 => 48,
            when 4 => 72, when 5 => 128, when others => Size'Last);
         when 6 => return (case Field is when 1 => 0, when 2 => 1, when 3 => 8,
            when 4 => 16, when 5 => 24, when others => Size'Last);
         when others => return Size'Last;
      end case;
   end Layout_Offset;
   function Extent_Valid
     (A : System.Address; Length : Size; Alignment : Size := 1)
      return Boolean is
     (Alignment /= 0 and then
      Length <= Size (Storage_Offset'Last) and then
      (Length = 0 or else (A /= System.Null_Address and then
       To_Integer (A) mod Integer_Address (Alignment) = 0 and then
       Integer_Address (Length - 1) <= Integer_Address'Last - To_Integer (A))));
   function Id_Valid (I : Identity_C) return Boolean is
     (I.Present <= 1 and then (I.Present = 0 or else
       (I.First >= 1 and then I.First <= Size (R.Byte_Count'Last)
        and then I.Length <= Size (R.Byte_Count'Last))));
   function Epoch_Valid (E : Epoch_C) return Boolean is
     (E.Present <= 1 and then (E.Present = 0 or else
       (E.First >= 1 and then E.First <= Size (R.Byte_Count'Last)
        and then E.Length <= Size (R.Byte_Count'Last))));
   function Cursor_Valid (C : Cursor_C) return Boolean is
     (C.Present <= 1 and then (C.Present = 0 or else
       (Epoch_Valid (C.Sequence) and then C.Run.Present = 1
        and then Id_Valid (C.Run))));
   function Row_Valid (V : Row_C) return Boolean is
     (Id_Valid (V.Subject) and then Id_Valid (V.Content)
      and then Id_Valid (V.Requirement) and then Id_Valid (V.Run)
      and then Epoch_Valid (V.Sequence) and then V.State <= 3
      and then V.Outcome <= 2);
   function Span (I : Identity_C) return H.Identity_Span is
     (R.Byte_Index (I.First), R.Byte_Count (I.Length))
   with Pre => I.First >= 1 and then I.First <= Size (R.Byte_Count'Last)
     and then I.Length <= Size (R.Byte_Count'Last);
   function Epoch (E : Epoch_C) return H.Optional_Epoch is
     (if E.Present = 0 then (Present => False)
      else (Present => True, Value =>
        (R.Byte_Index (E.First), R.Byte_Count (E.Length))))
   with Pre => Epoch_Valid (E);
   function Subject (I : Identity_C) return H.Optional_Subject is
     (if I.Present = 0 then (Present => False)
      else (Present => True, Value => H.Subject_Id (Span (I))))
   with Pre => Id_Valid (I);
   function Content (I : Identity_C) return H.Optional_Content is
     (if I.Present = 0 then (Present => False)
      else (Present => True, Value => H.Content_Id (Span (I))))
   with Pre => Id_Valid (I);
   function Requirement (I : Identity_C) return H.Optional_Requirement is
     (if I.Present = 0 then (Present => False)
      else (Present => True, Value => H.Requirement_Id (Span (I))))
   with Pre => Id_Valid (I);
   function Run (I : Identity_C) return H.Optional_Evaluation is
     (if I.Present = 0 then (Present => False)
      else (Present => True, Value => H.Evaluation_Id (Span (I))))
   with Pre => Id_Valid (I);
   function Cursor (C : Cursor_C) return H.Optional_Cursor is
     (if C.Present = 0 then (Present => False)
      else (Present => True, Value =>
        (Sequence => Epoch (C.Sequence), Run => H.Evaluation_Id (Span (C.Run)))))
   with Pre => Cursor_Valid (C);
   function Row (V : Row_C) return H.Evaluation_Record is
     (Subject (V.Subject), Content (V.Content), Requirement (V.Requirement),
      Run (V.Run), Epoch (V.Sequence), H.Lifecycle'Val (V.State), H.Verdict'Val (V.Outcome))
   with Pre => Row_Valid (V);
   procedure Read_Byte (Address : System.Address; Item : out U8)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Byte_Pointers.Object_Pointer :=
        Byte_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Byte;

   procedure Read_Query (Address : System.Address; Item : out Query_C)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Query_Pointers.Object_Pointer :=
        Query_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Query;

   procedure Read_Row (Address : System.Address; Item : out Row_C)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Row_Pointers.Object_Pointer :=
        Row_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Row;

   procedure Write_Selection (Address : System.Address; Item : Selection_C)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Selection_Pointers.Object_Pointer :=
        Selection_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Selection;

   procedure Copy_Data
     (Address : System.Address; Length : Size; Value : out R.Byte_Array)
     with Pre => Length <= Size (R.Byte_Count'Last)
            and then Value'First = 1
            and then Value'Length = R.Byte_Count (Length)
            and then (Length = 0 or else Address /= System.Null_Address),
          Exceptional_Cases => (others => True)
   is
   begin
      for I in Value'Range loop
         Read_Byte (Address + Storage_Offset (I - 1), Value (I));
      end loop;
   end Copy_Data;
   function Ref_Index (Ref : H.Record_Reference) return Size is
     (case Ref.Kind is when H.History_Entry => Size (Ref.Index),
      when others => 0);

   function Select_Evidence
     (Data : System.Address; Data_Length : Size;
      Rows : System.Address; Row_Count : Size;
      Final_Present : U8; Final_Row, Query, Output : System.Address) return U8 is
      Stride : constant Size := Layout_Size (4);
   begin
      if Data_Length > Size (R.Byte_Count'Last) or else
        Row_Count > Size (R.Byte_Count'Last) or else
        Row_Count > Size (Storage_Offset'Last) / Stride or else
        Final_Present > 1 or else
        not Extent_Valid (Data, Data_Length) or else
        not Extent_Valid (Rows, Row_Count * Stride, Row_C'Alignment) or else
        (Final_Present = 1 and then
          not Extent_Valid (Final_Row, Stride, Row_C'Alignment)) or else
        not Extent_Valid (Query, Layout_Size (5), Query_C'Alignment) or else
        not Extent_Valid (Output, Layout_Size (6), Selection_C'Alignment)
      then return 255;
      end if;
      declare
         Raw_Q : Query_C;
         A : R.Byte_Array (1 .. R.Byte_Count (Data_Length));
         Blank : constant H.Evaluation_Record :=
           (Subject => (Present => False), Content => (Present => False),
            Requirement => (Present => False), Run => (Present => False),
            Sequence => (Present => False), State => H.Pending,
            Outcome => H.No_Verdict);
         History : H.History (1 .. R.Byte_Count (Row_Count)) := (others => Blank);
         F : H.Optional_Record (Present => Final_Present = 1) :=
           (if Final_Present = 1 then (Present => True, Value => Blank)
            else (Present => False));
      begin
         Read_Query (Query, Raw_Q);
         Copy_Data (Data, Data_Length, A);
         if not Id_Valid (Raw_Q.Subject) or else not Id_Valid (Raw_Q.Content)
           or else not Id_Valid (Raw_Q.Requirement)
           or else not Cursor_Valid (Raw_Q.Current_Head)
           or else not Cursor_Valid (Raw_Q.Prepared_Evidence)
         then return 255;
         end if;
         if Final_Present = 1 then
            declare
               V : Row_C;
            begin
               Read_Row (Final_Row, V);
               declare
                  Fixed : constant Row_C := V;
                  Item : H.Evaluation_Record :=
                    (Subject => (Present => False),
                     Content => (Present => False),
                     Requirement => (Present => False),
                     Run => (Present => False),
                     Sequence => (Present => False),
                     State => H.Pending, Outcome => H.No_Verdict);
               begin
                  if not Row_Valid (Fixed) then return 255; end if;
                  Item.Subject := Subject (Fixed.Subject);
                  Item.Content := Content (Fixed.Content);
                  Item.Requirement := Requirement (Fixed.Requirement);
                  Item.Run := Run (Fixed.Run);
                  Item.Sequence := Epoch (Fixed.Sequence);
                  Item.State := H.Lifecycle'Val (Fixed.State);
                  Item.Outcome := H.Verdict'Val (Fixed.Outcome);
                  F.Value := Item;
               end;
            end;
         end if;
         for I in History'Range loop
            declare
               V : Row_C;
            begin
               Read_Row (Rows + Storage_Offset (Size (I - 1) * Stride), V);
               if not Row_Valid (V) then return 255; end if;
               History (I) := Row (V);
            end;
         end loop;
         declare
            Q : constant H.Query :=
              (Subject (Raw_Q.Subject), Content (Raw_Q.Content),
               Requirement (Raw_Q.Requirement), Cursor (Raw_Q.Current_Head),
               Cursor (Raw_Q.Prepared_Evidence));
            Selected : constant H.Selection := H.Select_Evidence (A, History, F, Q);
            Result : constant Selection_C :=
              (H.Decision'Pos (Selected.Reason), H.Source_Kind'Pos (Selected.Head.Kind),
               Ref_Index (Selected.Head), H.Source_Kind'Pos (Selected.Completed_Failure.Kind),
               Ref_Index (Selected.Completed_Failure));
         begin
            Write_Selection (Output, Result);
            return 0;
         end;
      end;
   exception
      when others => return 255;
   end Select_Evidence;
end Worldline.Evaluation_History_C_API;

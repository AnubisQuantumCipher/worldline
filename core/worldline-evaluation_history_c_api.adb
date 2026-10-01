with Ada.Unchecked_Conversion;
with Evaluation_History;
with Resource_Quantities;
with System.Storage_Elements;

package body Worldline.Evaluation_History_C_API with SPARK_Mode => Off is
   package H renames Evaluation_History;
   package R renames Resource_Quantities;
   use type U8;
   use type R.Byte_Count;
   use type Size;
   use type System.Address;
   use System.Storage_Elements;
   type Byte_Access is access all U8;
   type Row_Access is access all Row_C;
   type Query_Access is access all Query_C;
   type Selection_Access is access all Selection_C;
   function As_Byte is new Ada.Unchecked_Conversion (System.Address, Byte_Access);
   function As_Row is new Ada.Unchecked_Conversion (System.Address, Row_Access);
   function As_Query is new Ada.Unchecked_Conversion (System.Address, Query_Access);
   function As_Selection is new Ada.Unchecked_Conversion (System.Address, Selection_Access);

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
      I : Identity_C;
      E : Epoch_C;
      C : Cursor_C;
      Rw : Row_C;
      Q : Query_C;
      S : Selection_C;
   begin
      case Kind is
         when 1 => return (case Field is when 1 => I.Present'Position,
            when 2 => I.First'Position, when 3 => I.Length'Position,
            when others => Size'Last);
         when 2 => return (case Field is when 1 => E.Present'Position,
            when 2 => E.First'Position, when 3 => E.Length'Position, when others => Size'Last);
         when 3 => return (case Field is when 1 => C.Present'Position,
            when 2 => C.Sequence'Position, when 3 => C.Run'Position,
            when others => Size'Last);
         when 4 => return (case Field is when 1 => Rw.Subject'Position,
            when 2 => Rw.Content'Position, when 3 => Rw.Requirement'Position,
            when 4 => Rw.Run'Position, when 5 => Rw.Sequence'Position,
            when 6 => Rw.State'Position, when 7 => Rw.Outcome'Position,
            when others => Size'Last);
         when 5 => return (case Field is when 1 => Q.Subject'Position,
            when 2 => Q.Content'Position, when 3 => Q.Requirement'Position,
            when 4 => Q.Current_Head'Position, when 5 => Q.Prepared_Evidence'Position,
            when others => Size'Last);
         when 6 => return (case Field is when 1 => S.Reason'Position,
            when 2 => S.Head_Kind'Position, when 3 => S.Head_Index'Position,
            when 4 => S.Failure_Kind'Position, when 5 => S.Failure_Index'Position,
            when others => Size'Last);
         when others => return Size'Last;
      end case;
   end Layout_Offset;
   function Extent_Valid
     (A : System.Address; Length : Size; Alignment : Size := 1)
      return Boolean is
     (Length <= Size (Storage_Offset'Last) and then
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
     (R.Byte_Index (I.First), R.Byte_Count (I.Length));
   function Epoch (E : Epoch_C) return H.Optional_Epoch is
     (if E.Present = 0 then (Present => False)
      else (Present => True, Value =>
        (R.Byte_Index (E.First), R.Byte_Count (E.Length))));
   function Subject (I : Identity_C) return H.Optional_Subject is
     (if I.Present = 0 then (Present => False)
      else (Present => True, Value => H.Subject_Id (Span (I))));
   function Content (I : Identity_C) return H.Optional_Content is
     (if I.Present = 0 then (Present => False)
      else (Present => True, Value => H.Content_Id (Span (I))));
   function Requirement (I : Identity_C) return H.Optional_Requirement is
     (if I.Present = 0 then (Present => False)
      else (Present => True, Value => H.Requirement_Id (Span (I))));
   function Run (I : Identity_C) return H.Optional_Evaluation is
     (if I.Present = 0 then (Present => False)
      else (Present => True, Value => H.Evaluation_Id (Span (I))));
   function Cursor (C : Cursor_C) return H.Optional_Cursor is
     (if C.Present = 0 then (Present => False)
      else (Present => True, Value =>
        (Sequence => Epoch (C.Sequence), Run => H.Evaluation_Id (Span (C.Run)))));
   function Row (V : Row_C) return H.Evaluation_Record is
     (Subject (V.Subject), Content (V.Content), Requirement (V.Requirement),
      Run (V.Run), Epoch (V.Sequence), H.Lifecycle'Val (V.State), H.Verdict'Val (V.Outcome));
   function Copy_Data (A : System.Address; Length : Size) return R.Byte_Array is
      V : R.Byte_Array (1 .. R.Byte_Count (Length));
   begin
      for I in V'Range loop
         V (I) := As_Byte (A + Storage_Offset (I - 1)).all;
      end loop;
      return V;
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
         Raw_Q : constant Query_C := As_Query (Query).all;
         A : constant R.Byte_Array := Copy_Data (Data, Data_Length);
         History : H.History (1 .. R.Byte_Count (Row_Count));
         F : H.Optional_Record;
      begin
         if not Id_Valid (Raw_Q.Subject) or else not Id_Valid (Raw_Q.Content)
           or else not Id_Valid (Raw_Q.Requirement)
           or else not Cursor_Valid (Raw_Q.Current_Head)
           or else not Cursor_Valid (Raw_Q.Prepared_Evidence)
         then return 255;
         end if;
         if Final_Present = 1 then
            declare
               V : constant Row_C := As_Row (Final_Row).all;
            begin
               if not Row_Valid (V) then return 255; end if;
               F := (Present => True, Value => Row (V));
            end;
         end if;
         for I in History'Range loop
            declare
               V : constant Row_C := As_Row
                 (Rows + Storage_Offset (Size (I - 1) * Stride)).all;
            begin
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
            As_Selection (Output).all := Result;
            return 0;
         end;
      end;
   exception
      when others => return 255;
   end Select_Evidence;
end Worldline.Evaluation_History_C_API;

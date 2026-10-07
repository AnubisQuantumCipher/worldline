with Evaluation_Pending;
with System.Address_To_Access_Conversions;
with System.Storage_Elements;

package body Evaluation_Pending_C with SPARK_Mode => On is
   package E renames Evaluation_Pending;
   use type System.Address;
   use type I64;
   use type U32;
   use type E.Count;
   use System.Storage_Elements;
   package Request_Pointers is new System.Address_To_Access_Conversions (Request);
   package Result_Pointers is new System.Address_To_Access_Conversions (Result);
   package Row_Pointers is new System.Address_To_Access_Conversions (Row);
   package Byte_Pointers is new System.Address_To_Access_Conversions (E.Byte);
   use type Byte_Pointers.Object_Pointer;
   use type Request_Pointers.Object_Pointer;
   use type Result_Pointers.Object_Pointer;
   use type Row_Pointers.Object_Pointer;

   function ABI_Version return U32 is (1);
   function Layout_Size (Kind : U32) return I64 is
     (case Kind is
        when 1 => Span'Object_Size / System.Storage_Unit,
        when 2 => Cursor'Object_Size / System.Storage_Unit,
        when 3 => Row'Object_Size / System.Storage_Unit,
        when 4 => Request'Object_Size / System.Storage_Unit,
        when 5 => Result'Object_Size / System.Storage_Unit,
        when others => I64'Last);
   function Layout_Alignment (Kind : U32) return I64 is
     (case Kind is
        when 1 => Span'Alignment, when 2 => Cursor'Alignment,
        when 3 => Row'Alignment, when 4 => Request'Alignment,
        when 5 => Result'Alignment, when others => I64'Last);
   function Layout_Offset (Kind, Field : U32) return I64 is
      S : constant Span := (0, 0);
      C : constant Cursor := (Present => 0, Sequence => S, Run => S);
      V : constant Row :=
        (Store_Id | Subject | Content | Run | Sequence => S,
         Previous => C, Linked => 0);
      R : constant Request :=
        (Version => 0, Operation => 0,
         Data => System.Null_Address, Data_Length => 0,
         Rows => System.Null_Address, Row_Count => 0,
         Store_Id | Subject | Content | Run | Proposed_Epoch => S,
         Authority_Head => C, Target_Head => C);
      O : constant Result := (Reason => 0, Sequence => S, Selected => 0);
   begin
      pragma Compile_Time_Error (S.First'Position /= 0, "Span.First");
      pragma Compile_Time_Error (S.Length'Position /= 8, "Span.Length");
      pragma Compile_Time_Error (C.Present'Position /= 0, "Cursor.Present");
      pragma Compile_Time_Error (C.Sequence'Position /= 8, "Cursor.Sequence");
      pragma Compile_Time_Error (C.Run'Position /= 24, "Cursor.Run");
      pragma Compile_Time_Error (V.Store_Id'Position /= 0, "Row.Store");
      pragma Compile_Time_Error (V.Subject'Position /= 16, "Row.Subject");
      pragma Compile_Time_Error (V.Content'Position /= 32, "Row.Content");
      pragma Compile_Time_Error (V.Run'Position /= 48, "Row.Run");
      pragma Compile_Time_Error (V.Sequence'Position /= 64, "Row.Sequence");
      pragma Compile_Time_Error (V.Previous'Position /= 80, "Row.Previous");
      pragma Compile_Time_Error (V.Linked'Position /= 120, "Row.Linked");
      pragma Compile_Time_Error (R.Version'Position /= 0, "Request.Version");
      pragma Compile_Time_Error (R.Operation'Position /= 4, "Request.Operation");
      pragma Compile_Time_Error (R.Data'Position /= 8, "Request.Data");
      pragma Compile_Time_Error (R.Data_Length'Position /= 16, "Request.Data_Length");
      pragma Compile_Time_Error (R.Rows'Position /= 24, "Request.Rows");
      pragma Compile_Time_Error (R.Row_Count'Position /= 32, "Request.Row_Count");
      pragma Compile_Time_Error (R.Store_Id'Position /= 40, "Request.Store");
      pragma Compile_Time_Error (R.Subject'Position /= 56, "Request.Subject");
      pragma Compile_Time_Error (R.Content'Position /= 72, "Request.Content");
      pragma Compile_Time_Error (R.Run'Position /= 88, "Request.Run");
      pragma Compile_Time_Error (R.Proposed_Epoch'Position /= 104, "Request.Epoch");
      pragma Compile_Time_Error (R.Authority_Head'Position /= 120, "Request.Authority");
      pragma Compile_Time_Error (R.Target_Head'Position /= 160, "Request.Target");
      pragma Compile_Time_Error (O.Reason'Position /= 0, "Result.Reason");
      pragma Compile_Time_Error (O.Sequence'Position /= 8, "Result.Sequence");
      pragma Compile_Time_Error (O.Selected'Position /= 24, "Result.Selected");
      case Kind is
         when 1 => return (case Field is when 1 => 0, when 2 => 8, when others => I64'Last);
         when 2 => return (case Field is when 1 => 0, when 2 => 8, when 3 => 24,
            when others => I64'Last);
         when 3 => return (case Field is when 1 => 0, when 2 => 16, when 3 => 32,
            when 4 => 48, when 5 => 64, when 6 => 80, when 7 => 120,
            when others => I64'Last);
         when 4 => return (case Field is when 1 => 0, when 2 => 4, when 3 => 8,
            when 4 => 16, when 5 => 24, when 6 => 32, when 7 => 40, when 8 => 56,
            when 9 => 72, when 10 => 88, when 11 => 104, when 12 => 120,
            when 13 => 160, when others => I64'Last);
         when 5 => return (case Field is when 1 => 0, when 2 => 8, when 3 => 24,
            when others => I64'Last);
         when others => return I64'Last;
      end case;
   end Layout_Offset;

   --  Numeric checks do not establish mapped, live, readable or owned memory.
   function Extent_Valid
     (A : System.Address; Length, Alignment : I64) return Boolean is
     (Length >= 0 and then Alignment > 0
      and then Length <= I64 (Storage_Offset'Last)
      and then (Length = 0 or else
        (A /= System.Null_Address
         and then To_Integer (A) mod Integer_Address (Alignment) = 0
         and then Integer_Address (Length - 1) <=
           Integer_Address'Last - To_Integer (A))));
   --  Validated lengths and ordered subtraction avoid modular wrap acceptance.
   function Disjoint
     (Left : System.Address; Left_Length : I64;
      Right : System.Address; Right_Length : I64) return Boolean is
     (Left_Length = 0 or else Right_Length = 0 or else
        (if To_Integer (Left) <= To_Integer (Right) then
            Integer_Address (Left_Length) <= To_Integer (Right) - To_Integer (Left)
         else Integer_Address (Right_Length) <= To_Integer (Left) - To_Integer (Right)))
   with Pre => Left_Length >= 0 and then Right_Length >= 0;

   function Valid (S : Span) return Boolean is
     (S.First >= 1 and then S.Length >= 0);
   function Convert (S : Span) return E.Span is
     ((First => E.Index (S.First), Length => E.Count (S.Length)))
   with Pre => Valid (S);
   function Valid (C : Cursor) return Boolean is
     (C.Present <= 1 and then (C.Present = 0 or else (Valid (C.Run) and then Valid (C.Sequence))));
   function Convert (C : Cursor) return E.Cursor is
     (if C.Present = 0 then (Present => False)
      else (Present => True, Sequence => Convert (C.Sequence), Run => Convert (C.Run)))
   with Pre => Valid (C);

   procedure Read_Byte (Address : System.Address; Item : out E.Byte)
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

   procedure Read_Request (Address : System.Address; Item : out Request)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Request_Pointers.Object_Pointer :=
        Request_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Request;

   procedure Read_Row (Address : System.Address; Item : out Row)
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

   procedure Write_Result (Address : System.Address; Item : Result)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Result_Pointers.Object_Pointer :=
        Result_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Result;

   procedure Copy_Data (Address : System.Address; Length : I64; Owned : out E.Bytes)
     with Pre => Length >= 0
            and then Length <= I64 (Storage_Offset'Last)
            and then Owned'First = 1
            and then Owned'Length = E.Count (Length)
            and then (Length = 0 or else Address /= System.Null_Address),
          Exceptional_Cases => (others => True)
   is
   begin
      for I in Owned'Range loop
         Read_Byte (Address + Storage_Offset (I - 1), Owned (I));
      end loop;
   end Copy_Data;

   function Decide (Input, Output : System.Address) return Interfaces.C.int is
      Request_Size : constant I64 := Layout_Size (4);
      Result_Size : constant I64 := Layout_Size (5);
      Stride : constant I64 := Layout_Size (3);
   begin
      --  Validate fixed extents before the first foreign dereference.
      if not Extent_Valid (Input, Request_Size, Request'Alignment)
        or else not Extent_Valid (Output, Result_Size, Result'Alignment)
        or else not Disjoint (Input, Request_Size, Output, Result_Size)
      then
         return 255;
      end if;
      declare
         R : Request;
      begin
         Read_Request (Input, R);
         if R.Version /= 1 or else R.Operation > 1
           or else R.Data_Length < 0 or else R.Row_Count < 0
           or else Stride <= 0
           or else R.Row_Count > I64 (Storage_Offset'Last) / Stride
           or else not Extent_Valid (R.Data, R.Data_Length, E.Byte'Alignment)
           or else not Extent_Valid (R.Rows, R.Row_Count * Stride, Row'Alignment)
           or else not Disjoint (Output, Result_Size, R.Data, R.Data_Length)
           or else not Disjoint (Output, Result_Size, R.Rows, R.Row_Count * Stride)
           or else not Valid (R.Store_Id) or else not Valid (R.Subject)
           or else not Valid (R.Content) or else not Valid (R.Run)
           or else not Valid (R.Proposed_Epoch)
           or else not Valid (R.Authority_Head) or else not Valid (R.Target_Head)
         then
            return 255;
         end if;
         declare
            Data_Length : constant I64 := R.Data_Length;
            Row_Count : constant I64 := R.Row_Count;
            Blank : constant E.Intent :=
              (Store_Id | Subject | Content | Run | Sequence =>
                 (First => 1, Length => 0),
               Previous => (Present => False),
               State => E.Reserved);
            A : E.Bytes (1 .. E.Count (Data_Length));
            J : E.Journal (1 .. E.Count (Row_Count)) := (others => Blank);
            P : E.Plan;
         begin
            Copy_Data (R.Data, Data_Length, A);
            for I in J'Range loop
               declare
                  --  Physical stride is Object_Size, not logical payload Size.
                  V : Row;
               begin
                  Read_Row
                    (R.Rows + Storage_Offset (I64 (I - 1) * Stride), V);
                  if not Valid (V.Store_Id) or else not Valid (V.Subject)
                    or else not Valid (V.Content) or else not Valid (V.Run)
                    or else not Valid (V.Sequence)
                    or else not Valid (V.Previous) or else V.Linked > 1
                  then
                     return 255;
                  end if;
                  J (I) :=
                    (Store_Id => Convert (V.Store_Id),
                     Subject => Convert (V.Subject), Content => Convert (V.Content),
                     Run => Convert (V.Run), Sequence => Convert (V.Sequence),
                     Previous => Convert (V.Previous),
                     State => (if V.Linked = 0 then E.Reserved else E.Linked));
               end;
            end loop;
            P := E.Decide
              (A, J, Convert (R.Store_Id), Convert (R.Subject), Convert (R.Content),
               Convert (R.Run), Convert (R.Proposed_Epoch), Convert (R.Authority_Head), Convert (R.Target_Head),
               (if R.Operation = 0 then E.Begin_New else E.Replay));
            Write_Result
              (Output,
               (Reason => U32 (E.Decision'Pos (P.Reason)),
                Sequence => (First => I64 (P.Sequence.First),
                             Length => I64 (P.Sequence.Length)),
                Selected => I64 (P.Selected)));
            return 0;
         end;
      end;
   exception
      when others => return 255;
   end Decide;
end Evaluation_Pending_C;

with Evaluation_Pending;
with Evaluation_Pending_V2;
with System.Address_To_Access_Conversions;
with System.Storage_Elements;

package body Evaluation_Pending_V2_C with SPARK_Mode => Off is
   package E renames Evaluation_Pending;
   package V2 renames Evaluation_Pending_V2;
   use type System.Address;
   use type I64;
   use type U32;
   use type E.Count;
   use System.Storage_Elements;
   package Request_Pointers is new System.Address_To_Access_Conversions (Request);
   package Result_Pointers is new System.Address_To_Access_Conversions (Result);
   package Row_Pointers is new System.Address_To_Access_Conversions (Row);
   package Byte_Pointers is new System.Address_To_Access_Conversions (E.Byte);

   function ABI_Version return U32 is (2);
   function Layout_Size (Kind : U32) return I64 is
     (case Kind is
        when 1 => Span'Object_Size / System.Storage_Unit,
        when 2 => Cursor'Object_Size / System.Storage_Unit,
        when 3 => Row'Object_Size / System.Storage_Unit,
        when 4 => Request'Object_Size / System.Storage_Unit,
        when 5 => Result'Object_Size / System.Storage_Unit,
        when 6 => Optional_Requirement'Object_Size / System.Storage_Unit,
        when others => I64'Last);
   function Layout_Alignment (Kind : U32) return I64 is
     (case Kind is
        when 1 => Span'Alignment, when 2 => Cursor'Alignment,
        when 3 => Row'Alignment, when 4 => Request'Alignment,
        when 5 => Result'Alignment,
        when 6 => Optional_Requirement'Alignment, when others => I64'Last);
   function Layout_Offset (Kind, Field : U32) return I64 is
      S : Span;
      C : Cursor;
      V : Row;
      R : Request;
      O : Result;
      Q : Optional_Requirement;
   begin
      case Kind is
         when 1 => return (case Field is
            when 1 => S.First'Position, when 2 => S.Length'Position,
            when others => I64'Last);
         when 2 => return (case Field is
            when 1 => C.Present'Position, when 2 => C.Sequence'Position,
            when 3 => C.Run'Position, when others => I64'Last);
         when 3 => return (case Field is
            when 1 => V.Store_Id'Position, when 2 => V.Subject'Position,
            when 3 => V.Content'Position, when 4 => V.Run'Position,
            when 5 => V.Sequence'Position, when 6 => V.Previous'Position,
            when 7 => V.Linked'Position, when 8 => V.Requirement'Position,
            when others => I64'Last);
         when 4 => return (case Field is
            when 1 => R.Version'Position, when 2 => R.Operation'Position,
            when 3 => R.Data'Position, when 4 => R.Data_Length'Position,
            when 5 => R.Rows'Position, when 6 => R.Row_Count'Position,
            when 7 => R.Store_Id'Position, when 8 => R.Subject'Position,
            when 9 => R.Content'Position, when 10 => R.Run'Position,
            when 11 => R.Proposed_Epoch'Position,
            when 12 => R.Authority_Head'Position,
            when 13 => R.Target_Head'Position, when 14 => R.Required'Position,
            when others => I64'Last);
         when 5 => return (case Field is
            when 1 => O.Reason'Position, when 2 => O.Sequence'Position,
            when 3 => O.Selected'Position, when 4 => O.Requirement'Position,
            when others => I64'Last);
         when 6 => return (case Field is
            when 1 => Q.Present'Position, when 2 => Q.Value'Position,
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
         else Integer_Address (Right_Length) <= To_Integer (Left) - To_Integer (Right)));

   function Valid (S : Span) return Boolean is
     (S.First >= 1 and then S.Length >= 0);
   function Convert (S : Span) return E.Span is
     ((First => E.Index (S.First), Length => E.Count (S.Length)));
   function Valid (C : Cursor) return Boolean is
     (C.Present <= 1 and then (C.Present = 0 or else (Valid (C.Run) and then Valid (C.Sequence))));
   function Convert (C : Cursor) return E.Cursor is
     (if C.Present = 0 then (Present => False)
      else (Present => True, Sequence => Convert (C.Sequence), Run => Convert (C.Run)));

   function Valid (Q : Optional_Requirement) return Boolean is
     (Q.Present <= 1 and then (Q.Present = 0 or else Valid (Q.Value)));
   function Convert (Q : Optional_Requirement) return V2.Optional_Requirement is
     (if Q.Present = 0 then (Present => False)
      else (True, V2.Requirement_Id (Convert (Q.Value))));
   function Export_Requirement (Q : V2.Optional_Requirement)
      return Optional_Requirement is
     (if not Q.Present then (0, (1, 0))
      else (1, (I64 (Q.Value.First), I64 (Q.Value.Length))));

   function Copy_Data (Address : System.Address; Length : I64) return E.Bytes is
      Owned : E.Bytes (1 .. E.Count (Length));
   begin
      for I in Owned'Range loop
         Owned (I) := Byte_Pointers.To_Pointer
           (Address + Storage_Offset (I - 1)).all;
      end loop;
      return Owned;
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
         R : constant Request := Request_Pointers.To_Pointer (Input).all;
      begin
         if R.Version /= 2 or else R.Operation > 1
           or else R.Data_Length < 0 or else R.Row_Count < 0
           or else Stride <= 0
           or else R.Row_Count > I64 (Storage_Offset'Last) / Stride
           or else not Extent_Valid (R.Data, R.Data_Length, E.Byte'Alignment)
           or else not Extent_Valid (R.Rows, R.Row_Count * Stride, Row'Alignment)
           or else not Disjoint (Output, Result_Size, R.Data, R.Data_Length)
           or else not Disjoint (Output, Result_Size, R.Rows, R.Row_Count * Stride)
           or else not Valid (R.Store_Id) or else not Valid (R.Subject)
           or else not Valid (R.Content) or else not Valid (R.Run)
           or else not Valid (R.Proposed_Epoch) or else not Valid (R.Required)
           or else not Valid (R.Authority_Head) or else not Valid (R.Target_Head)
         then
            return 255;
         end if;
         declare
            A : constant E.Bytes := Copy_Data (R.Data, R.Data_Length);
            J : V2.Journal (1 .. E.Count (R.Row_Count));
            P : V2.Plan;
         begin
            for I in J'Range loop
               declare
                  --  Physical stride is Object_Size, not logical payload Size.
                  V : constant Row := Row_Pointers.To_Pointer
                    (R.Rows + Storage_Offset (I64 (I - 1) * Stride)).all;
               begin
                  if not Valid (V.Store_Id) or else not Valid (V.Subject)
                    or else not Valid (V.Content) or else not Valid (V.Run)
                    or else not Valid (V.Sequence)
                    or else not Valid (V.Previous) or else V.Linked > 1
                    or else not Valid (V.Requirement)
                  then
                     return 255;
                  end if;
                  J (I) :=
                    (Base => (Store_Id => Convert (V.Store_Id),
                     Subject => Convert (V.Subject), Content => Convert (V.Content),
                     Run => Convert (V.Run), Sequence => Convert (V.Sequence),
                     Previous => Convert (V.Previous),
                     State => (if V.Linked = 0 then E.Reserved else E.Linked)),
                     Requirement => Convert (V.Requirement));
               end;
            end loop;
            P := V2.Decide
              (A, J, Convert (R.Store_Id), Convert (R.Subject), Convert (R.Content),
               Convert (R.Run), Convert (R.Proposed_Epoch), Convert (R.Required), Convert (R.Authority_Head), Convert (R.Target_Head),
               (if R.Operation = 0 then E.Begin_New else E.Replay));
            Result_Pointers.To_Pointer (Output).all :=
              (Reason => U32 (V2.Decision'Pos (P.Reason)),
               Sequence => (First => I64 (P.Sequence.First),
                           Length => I64 (P.Sequence.Length)), Selected => I64 (P.Selected),
               Requirement => Export_Requirement (P.Requirement));
            return 0;
         end;
      end;
   exception
      when others => return 255;
   end Decide;
end Evaluation_Pending_V2_C;

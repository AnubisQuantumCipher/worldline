package body Worldline.Root_Custody_Row_Schema with SPARK_Mode is
   function Text_Is
     (Data : Q.Byte_Array; Cell : SQL_Cell; Value : String) return Boolean
   is
   begin
      if Cell.Kind /= SQL_Text or else not Span_Valid (Data, Cell.Bytes)
        or else Cell.Bytes.Length /= Value'Length
      then
         return False;
      end if;
      for I in Value'Range loop
         if Data (Cell.Bytes.First + Q.Byte_Count (I - Value'First)) /=
           Q.Byte (Character'Pos (Value (I)))
         then
            return False;
         end if;
         pragma Loop_Invariant
           (for all J in Value'First .. I =>
              Data (Cell.Bytes.First + Q.Byte_Count (J - Value'First)) =
                Q.Byte (Character'Pos (Value (J))));
      end loop;
      return True;
   end Text_Is;

   function Same_Span
     (Data : Q.Byte_Array; Left, Right : Bytes_Span) return Boolean
   is
   begin
      if not Span_Valid (Data, Left) or else not Span_Valid (Data, Right)
        or else Left.Length /= Right.Length
      then
         return False;
      end if;
      if Left.Length > 0 then
         for Offset in Q.Byte_Count range 0 .. Left.Length - 1 loop
            if Data (Left.First + Offset) /= Data (Right.First + Offset) then
               return False;
            end if;
            pragma Loop_Invariant
              (for all J in Q.Byte_Count range 0 .. Offset =>
                 Data (Left.First + J) = Data (Right.First + J));
         end loop;
      end if;
      return True;
   end Same_Span;

   function Read_Root_Phase_Name
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Root_Phase_Name
   is
   begin
      for Value in M.Root_Phase loop
         if Matches_Root_Phase (Data, Cell, Value) then
            return (Status => Exact_Name, Raw => Cell, Value => Value);
         end if;
         pragma Loop_Invariant
           (for all Examined in M.Root_Phase'First .. Value =>
              not Matches_Root_Phase (Data, Cell, Examined));
      end loop;
      return (Status => No_Exact_Name, Raw => Cell);
   end Read_Root_Phase_Name;

   function Read_Abort_Class_Name
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Abort_Class_Name
   is
   begin
      for Value in M.Abort_Class loop
         if Matches_Abort_Class (Data, Cell, Value) then
            return (Status => Exact_Name, Raw => Cell, Value => Value);
         end if;
      end loop;
      return (Status => No_Exact_Name, Raw => Cell);
   end Read_Abort_Class_Name;

   function Read_Request_Phase_Name
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Request_Phase_Name
   is
   begin
      for Value in M.Request_Phase loop
         if Matches_Request_Phase (Data, Cell, Value) then
            return (Status => Exact_Name, Raw => Cell, Value => Value);
         end if;
      end loop;
      return (Status => No_Exact_Name, Raw => Cell);
   end Read_Request_Phase_Name;

   function Read_Descriptor_Phase_Name
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Descriptor_Phase_Name
   is
   begin
      for Value in M.Descriptor_Phase loop
         if Matches_Descriptor_Phase (Data, Cell, Value) then
            return (Status => Exact_Name, Raw => Cell, Value => Value);
         end if;
      end loop;
      return (Status => No_Exact_Name, Raw => Cell);
   end Read_Descriptor_Phase_Name;

   function Read_Transfer_Mode_Name
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Transfer_Mode_Name
   is
   begin
      for Value in M.Transfer_Mode loop
         if Matches_Transfer_Mode (Data, Cell, Value) then
            return (Status => Exact_Name, Raw => Cell, Value => Value);
         end if;
      end loop;
      return (Status => No_Exact_Name, Raw => Cell);
   end Read_Transfer_Mode_Name;

   function Read_Nullable_Root_Phase
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Root_Phase_Column
   is
      Decoded : constant Root_Phase_Name := Read_Root_Phase_Name (Data, Cell);
   begin
      if Cell.Kind = SQL_Null then
         return (State => Null_Column, Raw => Cell);
      elsif Decoded.Status = Exact_Name then
         return (State => Value_Column, Raw => Cell, Value => Decoded.Value);
      else
         return (State => Invalid_Column, Raw => Cell);
      end if;
   end Read_Nullable_Root_Phase;

   function Read_Nullable_Abort_Class
     (Data : Q.Byte_Array; Cell : SQL_Cell) return Abort_Class_Column
   is
      Decoded : constant Abort_Class_Name := Read_Abort_Class_Name (Data, Cell);
   begin
      if Cell.Kind = SQL_Null then
         return (State => Null_Column, Raw => Cell);
      elsif Decoded.Status = Exact_Name then
         return (State => Value_Column, Raw => Cell, Value => Decoded.Value);
      else
         return (State => Invalid_Column, Raw => Cell);
      end if;
   end Read_Nullable_Abort_Class;

   function Read_Nullable_Quantity
     (Data : Q.Byte_Array; Cell : SQL_Cell; Positive : Boolean)
      return Quantity_Column
   is
   begin
      if Cell.Kind = SQL_Null then
         return (State => Null_Column, Raw => Cell);
      elsif Magnitude_Blob (Data, Cell, Positive) then
         return (State => Value_Column, Raw => Cell, Value => Blob_Quantity (Cell));
      else
         return (State => Invalid_Column, Raw => Cell);
      end if;
   end Read_Nullable_Quantity;

   function Read_Subject_Phase
     (Data : Q.Byte_Array; Kind, Phase : SQL_Cell) return Subject_Phase_Result
   is
      Request : constant Request_Phase_Name := Read_Request_Phase_Name (Data, Phase);
      Descriptor : constant Descriptor_Phase_Name := Read_Descriptor_Phase_Name (Data, Phase);
   begin
      if Text_Is (Data, Kind, "REQUEST") and then Request.Status = Exact_Name then
         return (Status => Exact_Name, Raw_Kind => Kind, Raw_Phase => Phase,
                 Value => (Kind => Request_Row, Request => Request.Value));
      elsif Text_Is (Data, Kind, "DESCRIPTOR") and then Descriptor.Status = Exact_Name then
         return (Status => Exact_Name, Raw_Kind => Kind, Raw_Phase => Phase,
                 Value => (Kind => Descriptor_Row, Descriptor => Descriptor.Value));
      else
         return (Status => No_Exact_Name, Raw_Kind => Kind, Raw_Phase => Phase);
      end if;
   end Read_Subject_Phase;
end Worldline.Root_Custody_Row_Schema;

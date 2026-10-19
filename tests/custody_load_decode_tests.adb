with Ada.Command_Line;
with Ada.Streams.Stream_IO;
with Ada.Text_IO;
with Worldline.Custody_V2_Load_Input;

-- Synthetic complete producer envelopes exercise decoding, never authority.
-- A single Ada runtime also makes assertion failures an explicit test result.
procedure Custody_Load_Decode_Tests is
   package L renames Worldline.Custody_V2_Load_Input;
   package E renames L.E;
   package Q renames L.Q;
   package IO renames Ada.Streams.Stream_IO;
   use type Ada.Streams.Stream_Element_Offset;
   use type E.Count;
   use type Q.Byte;
   use type L.Decode_Status;
   use type L.S.SQL_Class;

   procedure Check_Constrained_Cells (Value : L.Parsed_Input) is
      Encoded : constant E.Span :=
        L.V.Element (Value.Arena, Value.Event_Encoded (1), 0);
      Expected : constant Q.Quantity := Value.Event_SQL (1, 1).Integer_Value;
   begin
      for Kind in L.S.SQL_Class loop
         declare
            Cell : L.S.SQL_Cell (Kind);
            Work : E.Bytes (1 .. Value.Arena'Length + 8) := [others => 173];
            Used : E.Count := Value.Arena_Used;
            Status : L.Decode_Status;
         begin
            Work (Value.Arena'Range) := Value.Arena;
            L.Append_SQL_Cell (Work, Encoded, Used, Cell, Status);
            pragma Assert (Cell.Kind = Kind);
            if Kind = L.S.SQL_Integer then
               pragma Assert (Status = L.Parsed);
               pragma Assert (Cell.Integer_Value.Negative = Expected.Negative);
               pragma Assert (Cell.Integer_Value.Length = Expected.Length);
               for I in E.Count range 1 .. Expected.Length loop
                  pragma Assert
                    (Work (Cell.Integer_Value.First + (I - 1)) =
                     Value.Arena (Expected.First + (I - 1)));
               end loop;
            else
               pragma Assert (Status = L.Malformed);
               pragma Assert (Used = Value.Arena_Used);
               for I in Value.Arena'Range loop
                  pragma Assert (Work (I) = Value.Arena (I));
               end loop;
               for I in E.Count range Value.Arena'Length + 1 .. Work'Last loop
                  pragma Assert (Work (I) = 173);
               end loop;
            end if;
         end;
      end loop;
   end Check_Constrained_Cells;

   procedure Check (Data : E.Bytes; Expected : E.Count) is
      Size : constant L.Sizes := L.Counts (Data);
      Value : L.Parsed_Input
        (Size.Arena, Size.Events, Size.Heads, Size.Roots,
         Size.Subjects, Size.Alternatives, Size.Blobs);
      Grown : L.Parsed_Input
        (Size.Arena + 16, Size.Events + 1, Size.Heads, Size.Roots,
         Size.Subjects, Size.Alternatives, Size.Blobs);
      Short : L.Parsed_Input
        (0, Size.Events, Size.Heads, Size.Roots,
         Size.Subjects, Size.Alternatives, Size.Blobs);
      Used : E.Count;
   begin
      pragma Assert (Size.Status = L.Parsed);
      pragma Assert (Size.Events = Expected and Size.Heads = Expected
        and Size.Roots = Expected and Size.Subjects = Expected
        and Size.Alternatives = Expected and Size.Blobs = Expected);
      L.Decode (Data, Value);
      pragma Assert (Value.Status = L.Parsed);
      pragma Assert (L.Parsed_Spans_Valid (Value));
      pragma Assert (Value.Arena_Used = Size.Arena);
      for I in E.Count range 1 .. Data'Length loop
         pragma Assert (Value.Arena (I) = Data (Data'First + (I - 1)));
      end loop;
      if Expected = 1 then
         pragma Assert (Value.Event_SQL (1, 1).Kind = L.S.SQL_Integer);
         pragma Assert (Value.Event_SQL (1, 1).Integer_Value.Negative);
         pragma Assert (Value.Event_SQL (1, 2).Kind = L.S.SQL_Text);
         pragma Assert (Value.Event_SQL (1, 3).Kind = L.S.SQL_Null);
         pragma Assert (Value.Blob_SQL (1, 1).Kind = L.S.SQL_Blob);
         pragma Assert (Value.Blob_SQL (1, 3).Kind = L.S.SQL_Real);
         Check_Constrained_Cells (Value);
      end if;
      L.Decode_Grown (Data, (Data'First, Data'Length), Grown, Used);
      pragma Assert (Grown.Status = L.Parsed and Used = Size.Arena);
      pragma Assert (Grown.Decoded_Event_Count = Expected);
      for I in E.Count range Size.Arena + 1 .. Grown.Arena'Last loop
         pragma Assert (Grown.Arena (I) = 0);
      end loop;
      L.Decode (Data, Short);
      pragma Assert (Short.Status = L.Storage_Extent);
      Ada.Text_IO.Put_Line ("PASS custody table decode, grown buffer, capacity refusal");
   end Check;

   procedure Run (Path : String; Expected : E.Count; Maximum : Boolean) is
      File : IO.File_Type;
   begin
      IO.Open (File, IO.In_File, Path);
      -- Harness storage budget for these fixed committed fixtures only.
      pragma Assert (IO.Size (File) in 1 .. 131_072);
      declare
         Raw : Ada.Streams.Stream_Element_Array
           (1 .. Ada.Streams.Stream_Element_Offset (IO.Size (File)));
         Last : Ada.Streams.Stream_Element_Offset;
         Data : E.Bytes (1 .. E.Count (Raw'Length));
      begin
         IO.Read (File, Raw, Last);
         IO.Close (File);
         pragma Assert (Last = Raw'Last);
         for I in Data'Range loop
            Data (I) := Q.Byte (Raw (Ada.Streams.Stream_Element_Offset (I)));
         end loop;
         if Maximum then
            declare
               Rebased : constant E.Bytes
                 (Q.Byte_Index'Last - (Data'Length - 1) .. Q.Byte_Index'Last) := Data;
            begin
               Check (Rebased, Expected);
            end;
         else
            Check (Data, Expected);
            declare
               Rebased : constant E.Bytes (7 .. 7 + (Data'Length - 1)) := Data;
            begin
               Check (Rebased, Expected);
            end;
         end if;
      end;
   end Run;
begin
   pragma Assert (Ada.Command_Line.Argument_Count in 2 .. 3);
   pragma Assert (Ada.Command_Line.Argument_Count = 2 or else
                  Ada.Command_Line.Argument (3) = "maximum");
   Run (Ada.Command_Line.Argument (1),
        E.Count'Value (Ada.Command_Line.Argument (2)),
        Ada.Command_Line.Argument_Count = 3);
end Custody_Load_Decode_Tests;

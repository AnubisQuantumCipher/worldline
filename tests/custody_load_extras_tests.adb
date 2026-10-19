with Ada.Command_Line;
with Ada.Streams.Stream_IO;
with Ada.Text_IO;
with Worldline.Custody_V2_Load_Input;

procedure Custody_Load_Extras_Tests is
   package L renames Worldline.Custody_V2_Load_Input;
   package E renames L.E;
   package Q renames L.Q;
   package IO renames Ada.Streams.Stream_IO;
   use type Ada.Streams.Stream_Element_Offset;
   use type E.Count;
   use type Q.Byte;
   use type L.Decode_Status;
   use type L.S.SQL_Class;
   use type L.Original_Format;

   function Read_Fixture (Path : String) return E.Bytes is
      File : IO.File_Type;
   begin
      IO.Open (File, IO.In_File, Path);
      pragma Assert (IO.Size (File) in 1 .. 32_768);
      declare
         Raw : Ada.Streams.Stream_Element_Array
           (1 .. Ada.Streams.Stream_Element_Offset (IO.Size (File)));
         Last : Ada.Streams.Stream_Element_Offset;
      begin
         IO.Read (File, Raw, Last);
         IO.Close (File);
         pragma Assert (Last = Raw'Last);
         return Result : E.Bytes (1 .. E.Count (Raw'Length)) do
            for I in Result'Range loop
               Result (I) := Q.Byte (Raw (Ada.Streams.Stream_Element_Offset (I)));
            end loop;
         end return;
      end;
   end Read_Fixture;

   procedure Check (Raw, Digest : E.Bytes; First : Q.Byte_Index) is
      Amount : constant E.Count := L.Event_Extra_Byte_Count (Raw, (Raw'First, Raw'Length));
      Length : constant E.Count := Raw'Length + Amount;
      type Case_Kind is (Exact_Capacity, Too_Short, Invalid_Used);
   begin
      pragma Assert (Amount >= Digest'Length and Digest'Length = 64);
      for Mode in Case_Kind loop
         declare
            Capacity : constant E.Count := Length - (if Mode = Too_Short then 1 else 0);
            Data : E.Bytes (First .. First + (Capacity - 1)) := [others => 173];
            Used : E.Count := (if Mode = Invalid_Used then Capacity + 1 else Raw'Length);
            Extras : L.Event_Extra;
            Status : L.Decode_Status;
         begin
            Data (First .. First + (Raw'Length - 1)) := Raw;
            L.Append_Event_Extras (Data, (First, Raw'Length), Used, Extras, Status);
            if Mode = Exact_Capacity then
               pragma Assert (Status = L.Parsed and Used = Capacity);
               pragma Assert (Extras.Unknown_Cause.Kind = L.S.SQL_Text);
               pragma Assert (Extras.Unknown_Cause.Bytes.Length = Digest'Length);
               for I in Digest'Range loop
                  pragma Assert (Data (Extras.Unknown_Cause.Bytes.First + (I - 1)) = Digest (I));
               end loop;
               pragma Assert (Extras.Reattach_Epoch.Kind = L.S.SQL_Blob);
               pragma Assert (Extras.Position.Kind = L.S.SQL_Integer);
               pragma Assert (Extras.Position.Integer_Value.Negative);
               pragma Assert (L.S.Text_Is (Data, Extras.Transfer_Mode, "abc"));
               pragma Assert (Extras.Abort_Class.Kind = L.S.SQL_Null);
               pragma Assert (Extras.Original_Encoding = L.Scoped_Original);
            else
               pragma Assert (Status = (if Mode = Too_Short then L.Storage_Extent else L.Malformed));
               pragma Assert (Used = (if Mode = Too_Short then Raw'Length else Capacity + 1));
               for I in E.Count range Raw'Length .. Capacity - 1 loop
                  pragma Assert (Data (First + I) = 173);
               end loop;
            end if;
            for I in Raw'Range loop
               pragma Assert (Data (First + (I - 1)) = Raw (I));
            end loop;
         end;
      end loop;
   end Check;
begin
   pragma Assert (Ada.Command_Line.Argument_Count = 2);
   declare
      Raw : constant E.Bytes := Read_Fixture (Ada.Command_Line.Argument (1));
      Digest : constant E.Bytes := Read_Fixture (Ada.Command_Line.Argument (2));
      Length : constant E.Count := Raw'Length + L.Event_Extra_Byte_Count (Raw, (1, Raw'Length));
   begin
      Check (Raw, Digest, 1);
      Check (Raw, Digest, 7);
      Check (Raw, Digest, Q.Byte_Index'Last - (Length - 1));
   end;
   Ada.Text_IO.Put_Line ("PASS event extras: digest, exact capacity, short refusal, invalid used, prefix, endpoint");
end Custody_Load_Extras_Tests;

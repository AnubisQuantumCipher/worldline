with Ada.Streams.Stream_IO;
with Worldline.Operation_Archive;
with Worldline.Archive_Envelope;
with Worldline.Operation_Authority_Wire;
with Worldline.Retained_Raw_Decode;
with System;
package body Operation_Effect_Fixtures is
   package IO renames Ada.Streams.Stream_IO;
   package E renames Worldline.Archive_Envelope;
   package O renames Worldline.Operation_Archive;
   package T renames Worldline.Operation_Authority_Wire;
   package D renames Worldline.Retained_Raw_Decode;
   use type Q.Byte_Count;
   use type Q.Byte;
   use type E.Value_Kind;
   use type Ada.Streams.Stream_Element_Offset;
   function Read_All (Path : String) return Q.Byte_Array is
      File : IO.File_Type;
   begin
      IO.Open (File, IO.In_File, Path);
      declare
         Size : constant IO.Count := IO.Size (File);
         Buffer : Ada.Streams.Stream_Element_Array (1 .. Ada.Streams.Stream_Element_Offset (Size));
         Last : Ada.Streams.Stream_Element_Offset;
         Result : Q.Byte_Array (1 .. Q.Byte_Count (Size));
      begin
         IO.Read (File, Buffer, Last);
         IO.Close (File);
         if Last /= Buffer'Last then raise Program_Error with "complete operation fixture was not read"; end if;
         for I in Result'Range loop Result (I) := Q.Byte (Buffer (Ada.Streams.Stream_Element_Offset (I))); end loop;
         return Result;
      end;
   exception
      when others =>
         if IO.Is_Open (File) then IO.Close (File); end if;
         raise;
   end Read_All;
   function Load (Path : String) return Fixture is
      File : constant Q.Byte_Array := Read_All (Path);
      Whole : constant E.Span := (File'First, File'Length);
      function Bytes (Key : String) return Q.Byte_Array is
         Value : constant E.View := E.Decode (File, O.Field (File, Whole, Key), E.Operation);
      begin
         if Value.Form /= E.Bytes_Value or else not E.Bytes_Valid (File, Value.Payload)
         then raise Program_Error with "full raw operation fixture field absent"; end if;
         return E.Materialize (File, Value.Payload);
      end Bytes;
      Input : constant Q.Byte_Array := Bytes ("input");
      Arena : constant Q.Byte_Array := Bytes ("arena");
      Grants : constant Q.Byte_Array := Bytes ("grants");
      Uses : constant Q.Byte_Array := Bytes ("uses");
      Receipts : constant Q.Byte_Array := Bytes ("receipts");
      Events : constant Q.Byte_Array := Bytes ("events");
      Output : constant Q.Byte_Array := Bytes ("output");
      Grant_Size : constant Q.Byte_Count := T.Raw_Grant'Size / System.Storage_Unit;
      Use_Size : constant Q.Byte_Count := T.Raw_Use'Size / System.Storage_Unit;
      Row_Size : constant Q.Byte_Count := T.C.Raw_Row'Size / System.Storage_Unit;
   begin
      if not O.Valid (File, Whole)
        or else Input'Length /= T.Raw_Input'Size / System.Storage_Unit
        or else Output'Length /= T.Raw_Result'Size / System.Storage_Unit
        or else Grants'Length mod Grant_Size /= 0 or else Uses'Length mod Use_Size /= 0
        or else Receipts'Length mod Row_Size /= 0 or else Events'Length mod Row_Size /= 0
      then raise Program_Error with "complete expanded native operation fixture layout differs"; end if;
      declare
         Raw : constant T.Raw_Input := D.Load (Input);
         Value : Fixture (Arena'Length, Grants'Length / Grant_Size,
           Uses'Length / Use_Size, Receipts'Length / Row_Size, Events'Length / Row_Size);
      begin
         if not T.Well_Formed (Raw) or else not T.Recovery_Well_Formed (Arena, Raw.Facts)
           or else Raw.Mode /= A.Command'Pos (A.Observe_Effect)
           or else Output (Output'First) /= A.Decision'Pos (A.Effect_Accepted)
         then raise Program_Error with "fixture is not the original accepted effect observation"; end if;
         Value.Arena := Arena;
         Value.Bound := T.Decode (Raw.Bound);
         Value.Facts := T.Decode (Arena, Raw.Facts);
         Value.Now := T.Decode (Raw.Now).Value;
         for I in Value.Grants'Range loop
            declare
               First : constant Q.Byte_Index := Grants'First + (I - 1) * Grant_Size;
               Item : constant T.Raw_Grant := D.Load (Grants (First .. First + Grant_Size - 1));
            begin
               if not T.Well_Formed (Item) then raise Program_Error with "original grant raw field invalid"; end if;
               Value.Grants (I) := T.Decode (Item);
            end;
         end loop;
         for I in Value.Uses'Range loop
            declare
               First : constant Q.Byte_Index := Uses'First + (I - 1) * Use_Size;
               Item : constant T.Raw_Use := D.Load (Uses (First .. First + Use_Size - 1));
            begin
               if not T.Well_Formed (Item) then raise Program_Error with "original use raw field invalid"; end if;
               Value.Uses (I) := (Bound => T.Decode (Item.Bound), State => A.Use_State'Val (Item.State));
            end;
         end loop;
         for I in Value.Receipts'Range loop
            declare
               First : constant Q.Byte_Index := Receipts'First + (I - 1) * Row_Size;
               Item : constant T.C.Raw_Row := D.Load (Receipts (First .. First + Row_Size - 1));
            begin
               if not T.C.Well_Formed (Item) then raise Program_Error with "original receipt raw field invalid"; end if;
               Value.Receipts (I) := T.C.Decode (Item);
            end;
         end loop;
         for I in Value.Events'Range loop
            declare
               First : constant Q.Byte_Index := Events'First + (I - 1) * Row_Size;
               Item : constant T.C.Raw_Row := D.Load (Events (First .. First + Row_Size - 1));
            begin
               if not T.C.Well_Formed (Item) then raise Program_Error with "original causal raw field invalid"; end if;
               Value.Events (I) := T.C.Decode (Item);
            end;
         end loop;
         return Value;
      end;
   end Load;
end Operation_Effect_Fixtures;

package body Resource_Run_Ledger_Wire with SPARK_Mode is
   function Decode_Rows (Data : Q.Byte_Array; Raw : Raw_Row_Array) return L.Row_Array is
      Result : L.Row_Array (Raw'Range) with Relaxed_Initialization;
   begin
      for I in Raw'Range loop
         pragma Loop_Invariant (for all J in Raw'Range => (if J < I then Result (J)'Initialized));
         pragma Loop_Invariant (for all J in Raw'Range => (if J < I then Result (J) = Decode (Data, Raw (J))));
         Result (I) := Decode (Data, Raw (I));
      end loop;
      pragma Assert (Result'Initialized);
      return Result;
   end Decode_Rows;
   function Decode_Native (Data : Q.Byte_Array; Raw : Raw_Native_Array) return L.Native_Array is
      Result : L.Native_Array (Raw'Range) with Relaxed_Initialization;
   begin
      for I in Raw'Range loop
         pragma Loop_Invariant (for all J in Raw'Range => (if J < I then Result (J)'Initialized));
         pragma Loop_Invariant (for all J in Raw'Range => (if J < I then Result (J) = Decode (Data, Raw (J))));
         Result (I) := Decode (Data, Raw (I));
         pragma Assert (Result (I)'Initialized);
         pragma Assert (Result (I) = Decode (Data, Raw (I)));
      end loop;
      pragma Assert (Result'Initialized);
      return Result;
   end Decode_Native;
   function Decide (Data : Q.Byte_Array; Raw : Raw_Packet;
                    Before_Rows, Proposed_Rows : Raw_Row_Array;
                    Native : Raw_Native_Array) return Raw_Result is
     (Status => L.Status'Pos (L.Check
       (Data, Decode (Data, Raw.Before_State), Decode_Rows (Data, Before_Rows),
        Decode (Data, Raw.Proposed_State), Decode_Rows (Data, Proposed_Rows),
        Decode_Native (Data, Native), Decode (Data, Raw.Intent))));
end Resource_Run_Ledger_Wire;

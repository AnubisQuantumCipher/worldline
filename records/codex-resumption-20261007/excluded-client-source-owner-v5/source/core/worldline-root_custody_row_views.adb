package body Worldline.Root_Custody_Row_Views with SPARK_Mode is
   function Decode_Digest (Data : Q.Byte_Array; Cell : S.SQL_Cell)
      return M.Digest is
      Result : M.Digest := (others => 0);
   begin
      for I in Result'Range loop
         Result (I) :=
           Hex_Nibble (Data (Cell.Bytes.First + Q.Byte_Count (I - Result'First) * 2)) * 16 +
           Hex_Nibble (Data (Cell.Bytes.First + (Q.Byte_Count (I - Result'First) * 2 + 1)));
         pragma Loop_Invariant
           (for all J in Result'First .. I =>
              Result (J) =
                Hex_Nibble (Data (Cell.Bytes.First + Q.Byte_Count (J - Result'First) * 2)) * 16 +
                Hex_Nibble (Data (Cell.Bytes.First + (Q.Byte_Count (J - Result'First) * 2 + 1))));
      end loop;
      return Result;
   end Decode_Digest;

   function Make_Root (Data : Q.Byte_Array; Row : S.Root_Columns)
      return S.Root_View is
   begin
      return (Raw => Row,
              Generation => S.Blob_Quantity (Row.Generation),
              Operation => Row.Operation.Bytes,
              Phase => S.Read_Root_Phase_Name (Data, Row.Phase).Value,
              Before_Unknown => Optional_Phase (Data, Row.Before_Unknown),
              Owners_Open => S.Bit_Value (Data, Row.Owners_Open),
              Abort_Kind => Optional_Abort (Data, Row.Abort_Kind),
              Unknown_Cause => Optional_Digest (Data, Row.Unknown_Cause),
              Reattach_Epoch => S.Blob_Quantity (Row.Reattach_Epoch),
              Head => Decode_Digest (Data, Row.Head_Event),
              Physical => (Launched => S.Bit_Value (Data, Row.Launched),
                      NS => S.Bit_Value (Data, Row.Closure_NS),
                      Outer => S.Bit_Value (Data, Row.Closure_Outer),
                      Raw => S.Bit_Value (Data, Row.Closure_Raw),
                      Witness => S.Bit_Value (Data, Row.Witness),
                      Settled => S.Bit_Value (Data, Row.Settled),
                      Released_Unlaunched => S.Bit_Value (Data, Row.Released_Unlaunched)));
   end Make_Root;

   function Make_Optional_Root
     (Data : Q.Byte_Array; Row : S.Optional_Root_Row)
      return Optional_Root_View is
   begin
      if Row.Present then
         return (Present => True, Raw => Row, Value => Make_Root (Data, Row.Columns));
      else
         return (Present => False, Raw => Row);
      end if;
   end Make_Optional_Root;

   function Make_Subject (Data : Q.Byte_Array; Row : S.Subject_Columns)
      return S.Subject_View is
   begin
      return (Raw => Row,
              Generation => S.Blob_Quantity (Row.Generation),
              Subject => Row.Subject.Bytes,
              Subgeneration => S.Blob_Quantity (Row.Subgeneration),
              Phase => S.Read_Subject_Phase (Data, Row.Kind_Of_Subject, Row.Phase).Value,
              Mode => S.Read_Transfer_Mode_Name (Data, Row.Mode).Value,
              Position => Optional_Quantity (Data, Row.Position, Positive => False),
              Carried_From => Optional_Quantity (Data, Row.Carried_From, Positive => True),
              Head => Decode_Digest (Data, Row.Head_Event));
   end Make_Subject;

   function Make_Optional_Subject
     (Data : Q.Byte_Array; Row : S.Optional_Subject_Row)
      return Optional_Subject_View is
   begin
      if Row.Present then
         return (Present => True, Raw => Row, Value => Make_Subject (Data, Row.Columns));
      else
         return (Present => False, Raw => Row);
      end if;
   end Make_Optional_Subject;

end Worldline.Root_Custody_Row_Views;

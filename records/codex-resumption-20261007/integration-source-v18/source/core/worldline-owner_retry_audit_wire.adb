package body Worldline.Owner_Retry_Audit_Wire with SPARK_Mode is
   function Decode (Q : Raw_Audit) return K.Audit is
     (Before_Request => W.Decode (Q.Before_Request),
      Receipt => (Consumed => W.Grant (Q.Consumed),
        Issued_Event => W.Identity (Q.Issued_Event),
        Reserved_Event => W.Identity (Q.Reserved_Event),
        Consumed_Event => W.Identity (Q.Consumed_Event),
        Consumed_Issue => W.Identity (Q.Consumed_Issue),
        Consumed_Reservation => W.Identity (Q.Consumed_Reservation)),
      Current_Head => W.Cursor (Q.Current_Head),
      Prepared_Evidence => W.Cursor (Q.Prepared_Evidence),
      Current_Epoch => W.Epoch (Q.Current_Epoch));
   function Final (R : W.Raw_Row; Present : W.U8) return E.Optional_Record is
     (if Present = 0 then (Present => False)
      else (Present => True, Value => W.Row (R)));
   function Decide (A : E.Byte_Array; Before, After : W.Raw_Rows;
      Before_Final, After_Final : W.Raw_Row;
      Before_Present, After_Present : W.U8; Q : Raw_Audit) return K.Decision is
   begin
      if not Well_Formed (Before, After, Before_Final, After_Final,
        Before_Present, After_Present, Q) then return K.Input_Invalid; end if;
      return K.Decide (A, W.Rows (Before), W.Rows (After),
        Final (Before_Final, Before_Present), Final (After_Final, After_Present),
        Decode (Q));
   end Decide;
end Worldline.Owner_Retry_Audit_Wire;

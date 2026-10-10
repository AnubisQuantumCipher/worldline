with Worldline.Owner_Retry_Audit;
with Worldline.Owner_Transitions_Wire;
package Worldline.Owner_Retry_Audit_Wire with SPARK_Mode is
   package K renames Worldline.Owner_Retry_Audit;
   package W renames Worldline.Owner_Transitions_Wire;
   package E renames W.E;
   use type W.U8;
   use type K.Decision;
   use type K.Audit;
   use type E.Optional_Record;
   type Raw_Audit is record
      Before_Request : W.Raw_Request;
      Consumed : W.Raw_Grant;
      Issued_Event, Reserved_Event, Consumed_Event : W.Raw_Identity;
      Consumed_Issue, Consumed_Reservation : W.Raw_Identity;
      Current_Head, Prepared_Evidence : W.Raw_Cursor;
      Current_Epoch : W.Raw_Epoch;
   end record with Convention => C;
   function Valid (Q : Raw_Audit) return Boolean is
     (W.Request_Valid (Q.Before_Request) and then W.Grant_Valid (Q.Consumed)
      and then W.Identity_Valid (Q.Issued_Event)
      and then W.Identity_Valid (Q.Reserved_Event)
      and then W.Identity_Valid (Q.Consumed_Event)
      and then W.Identity_Valid (Q.Consumed_Issue)
      and then W.Identity_Valid (Q.Consumed_Reservation)
      and then W.Cursor_Valid (Q.Current_Head)
      and then W.Cursor_Valid (Q.Prepared_Evidence)
      and then W.Identity_Valid (Q.Current_Epoch)) with Global => null;
   function Decode (Q : Raw_Audit) return K.Audit
     with Global => null, Pre => Valid (Q),
       Post => Decode'Result =
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
   function Well_Formed (Before, After : W.Raw_Rows;
      Before_Final, After_Final : W.Raw_Row;
      Before_Present, After_Present : W.U8; Q : Raw_Audit) return Boolean is
     (Valid (Q) and then Before_Present <= 1 and then After_Present <= 1
      and then (Before_Present = 0 or else W.Row_Valid (Before_Final))
      and then (After_Present = 0 or else W.Row_Valid (After_Final))
      and then (for all I in Before'Range => W.Row_Valid (Before (I)))
      and then (for all I in After'Range => W.Row_Valid (After (I))))
     with Global => null;
   function Final (R : W.Raw_Row; Present : W.U8) return E.Optional_Record
     with Global => null, Pre => Present <= 1 and then
       (Present = 0 or else W.Row_Valid (R)),
       Post => Final'Result = (if Present = 0 then (Present => False)
         else (Present => True, Value => W.Row (R)));
   function Decide (A : E.Byte_Array; Before, After : W.Raw_Rows;
      Before_Final, After_Final : W.Raw_Row;
      Before_Present, After_Present : W.U8; Q : Raw_Audit) return K.Decision
     with Global => null,
     Post => (if not Well_Formed (Before, After, Before_Final, After_Final,
       Before_Present, After_Present, Q) then Decide'Result = K.Input_Invalid
       else Decide'Result = K.Reference (A, W.Rows (Before), W.Rows (After),
         Final (Before_Final, Before_Present), Final (After_Final, After_Present),
         Decode (Q)));
end Worldline.Owner_Retry_Audit_Wire;

with Worldline.Root_Custody_Model;

--  Exact X4 EventRow/ChainInput fields from the controlling design. Semantic
--  enums are already decoded views; archive/base bytes remain retained.
--  This unit certifies neither decoding nor authentication.
package Worldline.Root_Custody_Raw_Operands with SPARK_Mode is
   package M renames Worldline.Root_Custody_Model;
   package Q renames M.Q;
   type Head_Kind is (Origin, Event);
   type Chain_Input is record
      Key, Genesis_File, Genesis_Row : M.Identity;
      Genesis_Mac : M.Digest;
      Kind : Head_Kind;
      Head_Event, Head_Origin, Head_Mac : M.Digest;
   end record;
   type Event_Row is record
      Event_Id, Previous : M.Digest;
      Generation : Q.Quantity;
      Operation : M.Identity;
      Kind_Of_Subject : M.Subject_Kind;
      Subject : M.Identity;
      Subgeneration : Q.Quantity;
      Kind : M.Event_Kind;
      Appending_Actor : M.Actor;
      Record_Bytes, Base_Archive : M.Identity;
      Mac : M.Digest;
   end record;
   type Event_Rows is array (Q.Byte_Index range <>) of Event_Row;

   --  The original X5 EvidenceRec has an encoded value and kind. There is
   --  no result/Ready field here. Concrete raw grammar for each evidence
   --  kind must be supplied and checked by the consuming native decision.
   --  This declaration intentionally does not invent ABI enum assignments.
   type Evidence_Operand is record
      Kind_Code : Q.Byte;
      Encoded_Value : M.Identity;
   end record;
   type Evidence_Rows is array (Q.Byte_Index range <>) of Evidence_Operand;
end Worldline.Root_Custody_Raw_Operands;

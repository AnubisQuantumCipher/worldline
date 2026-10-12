package body Worldline.Custody_V2_Prepared with SPARK_Mode is
   procedure Try_Next
     (Data : C.E.Bytes; Raw : C.Event_Row; Before : M.Root_State;
      Grants : O.Grants; Before_Uses, Intent_Uses : O.Uses; Bound : O.Binding;
      Reserve_Now, Intent_Now : Q.Quantity; Reserve_Evidence, Intent_Evidence : O.Evidence;
      Reserve_Receipts, Reserve_Events, Intent_Receipts, Intent_Events : O.C.Retained_Rows;
      After : out M.Root_State; Value_Join : out Boolean) is
      Item : constant D.Decoded_Event := D.Decode (Data, Raw);
      use type D.Decode_Status;
   begin
      After := Before; Value_Join := False;
      if Item.Status /= D.Decoded or else not Root_Event_Join (Data, Before, Raw, Item.Value, Bound) then return; end if;
      if not Operation_Heads_Reestablished (Data, Grants, Before_Uses, Intent_Uses, Bound,
        Reserve_Now, Intent_Now, Reserve_Evidence, Intent_Evidence,
        Reserve_Receipts, Reserve_Events, Intent_Receipts, Intent_Events) then return; end if;
      After := P.Single_Root_Image (Before, Item.Value);
      Value_Join := True;
   end Try_Next;
end Worldline.Custody_V2_Prepared;

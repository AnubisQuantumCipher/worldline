package body Worldline.Owner_Conjunction_Wire with SPARK_Mode is
   function Checkpoint_Reference (A : W.E.Byte_Array; H : W.Raw_Rows;
      F : W.Raw_Row; Final_Present : W.U8; Original : C.Raw_Request;
      Resulting : C.Raw_Optional_Hash; S : Raw_Scope;
      Adopt_Present : W.U8; Adopt : W.Raw_Request) return K.Decision is
   begin
      if Final_Present > 1 or else Adopt_Present > 1
        or else (Final_Present = 1 and then not W.Row_Valid (F))
        or else (for some I in H'Range => not W.Row_Valid (H (I)))
        or else not C.Well_Formed (Original) or else not C.Hash_Well_Formed (Resulting)
        or else not Scope_Valid (S)
        or else (Adopt_Present = 1 and then not W.Request_Valid (Adopt))
      then return K.Input_Invalid; end if;
      return K.Authorize_Checkpoint (A, W.Rows (H), R.Final (F, Final_Present),
        C.Decode (Original), C.Requirement (Resulting), Scope (S),
        (if Adopt_Present = 0 then (Present => False)
         else (Present => True, Value => W.Decode (Adopt))));
   end Checkpoint_Reference;
   function Authorize_Checkpoint (A : W.E.Byte_Array; H : W.Raw_Rows;
      F : W.Raw_Row; Final_Present : W.U8; Original : C.Raw_Request;
      Resulting : C.Raw_Optional_Hash; S : Raw_Scope;
      Adopt_Present : W.U8; Adopt : W.Raw_Request) return K.Decision is
   begin return Checkpoint_Reference (A, H, F, Final_Present, Original,
     Resulting, S, Adopt_Present, Adopt); end;
   function Retry_Reference (A : W.E.Byte_Array; Before, After : W.Raw_Rows;
      Before_Final, After_Final : W.Raw_Row; Before_Present, After_Present : W.U8;
      Original : C.Raw_Request; S : Raw_Scope; Audit : R.Raw_Audit) return K.Decision is
   begin
      if not R.Well_Formed (Before, After, Before_Final, After_Final,
        Before_Present, After_Present, Audit)
        or else not C.Well_Formed (Original) or else not Scope_Valid (S)
      then return K.Input_Invalid; end if;
      return K.Authorize_Retry (A, W.Rows (Before), W.Rows (After),
        R.Final (Before_Final, Before_Present), R.Final (After_Final, After_Present),
        C.Decode (Original), Scope (S), R.Decode (Audit));
   end Retry_Reference;
   function Authorize_Retry (A : W.E.Byte_Array; Before, After : W.Raw_Rows;
      Before_Final, After_Final : W.Raw_Row; Before_Present, After_Present : W.U8;
      Original : C.Raw_Request; S : Raw_Scope; Audit : R.Raw_Audit) return K.Decision is
   begin return Retry_Reference (A, Before, After, Before_Final, After_Final,
     Before_Present, After_Present, Original, S, Audit); end;
   function Adopt_Receipt_Reference (A : W.E.Byte_Array; H : W.Raw_Rows;
      F : W.Raw_Row; Final_Present : W.U8; Original : C.Raw_Request;
      Resulting : C.Raw_Optional_Hash; S : Raw_Scope; Audit : R.Raw_Audit) return K.Decision is
   begin
      if Final_Present > 1 or else not R.Valid (Audit)
        or else (Final_Present = 1 and then not W.Row_Valid (F))
        or else (for some J in H'Range => not W.Row_Valid (H (J)))
        or else not C.Well_Formed (Original) or else not C.Hash_Well_Formed (Resulting)
        or else not Scope_Valid (S) then return K.Input_Invalid; end if;
      return K.Authorize_Adopt_Receipt (A, W.Rows (H), R.Final (F, Final_Present),
        C.Decode (Original), C.Requirement (Resulting), Scope (S), R.Decode (Audit));
   end Adopt_Receipt_Reference;
   function Authorize_Adopt_Receipt (A : W.E.Byte_Array; H : W.Raw_Rows;
      F : W.Raw_Row; Final_Present : W.U8; Original : C.Raw_Request;
      Resulting : C.Raw_Optional_Hash; S : Raw_Scope; Audit : R.Raw_Audit) return K.Decision is
   begin return Adopt_Receipt_Reference (A, H, F, Final_Present, Original, Resulting, S, Audit); end;
end Worldline.Owner_Conjunction_Wire;

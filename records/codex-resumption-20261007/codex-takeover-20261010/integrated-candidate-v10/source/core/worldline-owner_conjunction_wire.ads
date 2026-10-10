with Worldline.Owner_Transitions_Wire;
with Worldline.Owner_Conjunction;
with Worldline.Owner_Retry_Audit_Wire;
with Worldline.Collapse_Wire;
package Worldline.Owner_Conjunction_Wire with SPARK_Mode is
   package K renames Worldline.Owner_Conjunction;
   package W renames Worldline.Owner_Transitions_Wire;
   package R renames Worldline.Owner_Retry_Audit_Wire;
   package C renames Worldline.Collapse_Wire;
   use type W.U8;
   use type K.Decision;
   type Raw_Scope is record
      Subject, Content, Transaction : W.Raw_Identity;
   end record with Convention => C;
   function Scope_Valid (S : Raw_Scope) return Boolean is
     (W.Identity_Valid (S.Subject) and then W.Identity_Valid (S.Content)
      and then W.Identity_Valid (S.Transaction)) with Global => null;
   function Scope (S : Raw_Scope) return K.Full_Scope is
     (W.Identity (S.Subject), W.Identity (S.Content), W.Identity (S.Transaction))
     with Global => null, Pre => Scope_Valid (S);
   function Checkpoint_Reference (A : W.E.Byte_Array; H : W.Raw_Rows;
      F : W.Raw_Row; Final_Present : W.U8; Original : C.Raw_Request;
      Resulting : C.Raw_Optional_Hash; S : Raw_Scope;
      Adopt_Present : W.U8; Adopt : W.Raw_Request) return K.Decision
     with Global => null, Post => Checkpoint_Reference'Result =
       (if not (Final_Present <= 1 and then Adopt_Present <= 1
      and then (Final_Present = 0 or else W.Row_Valid (F))
      and then (for all J in H'Range => W.Row_Valid (H (J)))
      and then C.Well_Formed (Original) and then C.Hash_Well_Formed (Resulting)
      and then Scope_Valid (S)
      and then (Adopt_Present = 0 or else W.Request_Valid (Adopt))) then K.Input_Invalid
        else K.Checkpoint_Reference (A, W.Rows (H), R.Final (F, Final_Present),
          C.Decode (Original), C.Requirement (Resulting), Scope (S),
          (if Adopt_Present = 0 then (Present => False)
           else (Present => True, Value => W.Decode (Adopt)))));
   function Authorize_Checkpoint (A : W.E.Byte_Array; H : W.Raw_Rows;
      F : W.Raw_Row; Final_Present : W.U8; Original : C.Raw_Request;
      Resulting : C.Raw_Optional_Hash; S : Raw_Scope;
      Adopt_Present : W.U8; Adopt : W.Raw_Request) return K.Decision
     with Global => null, Post => Authorize_Checkpoint'Result =
       Checkpoint_Reference (A, H, F, Final_Present, Original, Resulting,
         S, Adopt_Present, Adopt);
   function Retry_Reference (A : W.E.Byte_Array; Before, After : W.Raw_Rows;
      Before_Final, After_Final : W.Raw_Row; Before_Present, After_Present : W.U8;
      Original : C.Raw_Request; S : Raw_Scope; Audit : R.Raw_Audit) return K.Decision
     with Global => null, Post => Retry_Reference'Result =
       (if not R.Well_Formed (Before, After, Before_Final, After_Final,
         Before_Present, After_Present, Audit) or else not C.Well_Formed (Original)
         or else not Scope_Valid (S) then K.Input_Invalid
        else K.Retry_Reference (A, W.Rows (Before), W.Rows (After),
          R.Final (Before_Final, Before_Present), R.Final (After_Final, After_Present),
          C.Decode (Original), Scope (S), R.Decode (Audit)));
   function Authorize_Retry (A : W.E.Byte_Array; Before, After : W.Raw_Rows;
      Before_Final, After_Final : W.Raw_Row; Before_Present, After_Present : W.U8;
      Original : C.Raw_Request; S : Raw_Scope; Audit : R.Raw_Audit) return K.Decision
     with Global => null, Post => Authorize_Retry'Result = Retry_Reference
       (A, Before, After, Before_Final, After_Final, Before_Present, After_Present,
         Original, S, Audit);
   function Adopt_Receipt_Reference (A : W.E.Byte_Array; H : W.Raw_Rows;
      F : W.Raw_Row; Final_Present : W.U8; Original : C.Raw_Request;
      Resulting : C.Raw_Optional_Hash; S : Raw_Scope; Audit : R.Raw_Audit) return K.Decision
     with Global => null, Post => Adopt_Receipt_Reference'Result =
       (if Final_Present > 1 or else not R.Valid (Audit)
          or else (Final_Present = 1 and then not W.Row_Valid (F))
          or else (for some J in H'Range => not W.Row_Valid (H (J)))
          or else not C.Well_Formed (Original) or else not C.Hash_Well_Formed (Resulting)
          or else not Scope_Valid (S) then K.Input_Invalid
        else K.Adopt_Receipt_Reference (A, W.Rows (H), R.Final (F, Final_Present),
          C.Decode (Original), C.Requirement (Resulting), Scope (S), R.Decode (Audit)));
   function Authorize_Adopt_Receipt (A : W.E.Byte_Array; H : W.Raw_Rows;
      F : W.Raw_Row; Final_Present : W.U8; Original : C.Raw_Request;
      Resulting : C.Raw_Optional_Hash; S : Raw_Scope; Audit : R.Raw_Audit) return K.Decision
     with Global => null, Post => Authorize_Adopt_Receipt'Result =
       Adopt_Receipt_Reference (A, H, F, Final_Present, Original, Resulting, S, Audit);
end Worldline.Owner_Conjunction_Wire;

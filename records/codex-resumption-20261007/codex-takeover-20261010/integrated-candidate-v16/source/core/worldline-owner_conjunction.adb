package body Worldline.Owner_Conjunction with SPARK_Mode is
   function Checkpoint_Reference (A : E.Byte_Array; H : E.History; F : E.Optional_Record;
      Original : C.Collapse_Request; Resulting : I.Optional_Requirement_Id;
      Scope : Full_Scope; Adopt : Optional_Adopt) return Decision is
   begin
      if Original.Mode /= C.Checkpoint_Return or else C.Decide (Original) /= C.Authorized
      then return Original_Collapse_Denied;
      elsif not Original.Current_Requirement.Present or else not Resulting.Present
      then return Resulting_Requirement_Absent;
      elsif Adopt.Present then
         if not Scope_Holds (A, Scope, Adopt.Value)
           or else not Original_Scope_Holds (A, Scope, Original)
           or else not Hash_Holds (A, Adopt.Value.Current_Requirement,
             Original.Current_Requirement.Present, Hash (Original.Current_Requirement.Value))
           or else not Hash_Holds (A, Adopt.Value.Resulting_Requirement,
             Resulting.Present, Hash (Resulting.Value))
         then return Owner_Scope_Mismatch;
         elsif Adopt.Value.Action /= K.Adopt_Requirement
           or else K.Authorize (A, H, F, Adopt.Value) /= K.Ready
         then return Owner_Not_Authorized;
         else return Ready; end if;
      elsif not I.Same (Original.Current_Requirement, Resulting)
      then return Requirement_Changed;
      else return Ready; end if;
   end Checkpoint_Reference;
   function Authorize_Checkpoint (A : E.Byte_Array; H : E.History; F : E.Optional_Record;
      Original : C.Collapse_Request; Resulting : I.Optional_Requirement_Id;
      Scope : Full_Scope; Adopt : Optional_Adopt) return Decision is
   begin return Checkpoint_Reference (A, H, F, Original, Resulting, Scope, Adopt); end;
   function Retry_Reference (A : E.Byte_Array; Before, After : E.History;
      Before_Final, After_Final : E.Optional_Record; Original : C.Collapse_Request;
      Scope : Full_Scope; Audit : R.Audit) return Decision is
   begin
      if Original.Mode /= C.Candidate_Evaluation or else C.Decide (Original) /= C.Authorized
      then return Original_Collapse_Denied;
      elsif not Scope_Holds (A, Scope, Audit.Before_Request)
        or else not Original_Scope_Holds (A, Scope, Original)
        or else not Hash_Holds (A, Audit.Before_Request.Current_Requirement,
          Original.Current_Requirement.Present, Hash (Original.Current_Requirement.Value))
        or else not Hash_Holds (A, Audit.Before_Request.Resulting_Requirement,
          Original.Resulting_Requirement.Present, Hash (Original.Resulting_Requirement.Value))
      then return Owner_Scope_Mismatch;
      elsif R.Decide (A, Before, After, Before_Final, After_Final, Audit) /= R.Ready
      then return Retry_Not_Admitted;
      else return Ready; end if;
   end Retry_Reference;
   function Authorize_Retry (A : E.Byte_Array; Before, After : E.History;
      Before_Final, After_Final : E.Optional_Record; Original : C.Collapse_Request;
      Scope : Full_Scope; Audit : R.Audit) return Decision is
   begin return Retry_Reference (A, Before, After, Before_Final, After_Final, Original, Scope, Audit); end;
   function Adopt_Receipt_Reference (A : E.Byte_Array; H : E.History; F : E.Optional_Record;
      Original : C.Collapse_Request; Resulting : I.Optional_Requirement_Id;
      Scope : Full_Scope; Audit : R.Audit) return Decision is
      D : constant Decision := Authorize_Checkpoint (A, H, F, Original,
        Resulting, Scope, (Present => True, Value => Audit.Before_Request));
   begin
      if D /= Ready then return D;
      elsif not R.Receipt_Holds (A, Audit.Before_Request.Grant, Audit.Receipt)
      then return Owner_Not_Authorized;
      else return Ready; end if;
   end Adopt_Receipt_Reference;
   function Authorize_Adopt_Receipt (A : E.Byte_Array; H : E.History; F : E.Optional_Record;
      Original : C.Collapse_Request; Resulting : I.Optional_Requirement_Id;
      Scope : Full_Scope; Audit : R.Audit) return Decision is
   begin return Adopt_Receipt_Reference (A, H, F, Original, Resulting, Scope, Audit); end;
end Worldline.Owner_Conjunction;

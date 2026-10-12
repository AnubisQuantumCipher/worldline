with Worldline.Owner_Subject_Projection;
with Interfaces;
with Evaluation_History;
with Worldline.Collapse;
with Worldline.Identities;
with Worldline.Owner_Retry_Audit;
with Worldline.Owner_Transitions;
package Worldline.Owner_Conjunction with SPARK_Mode is
   package C renames Worldline.Collapse;
   package I renames Worldline.Identities;
   package E renames Evaluation_History;
   package K renames Worldline.Owner_Transitions;
   package R renames Worldline.Owner_Retry_Audit;
   use type Interfaces.Unsigned_8;
   use type E.Byte_Count;
   use type C.Evaluation_Mode;
   use type C.Decision;
   use type K.Operation;
   use type K.Decision;
   use type R.Decision;
   type Full_Scope is record
      Subject, Content, Transaction : K.Optional_Identity;
   end record;
   type Optional_Adopt (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : K.Request;
      end case;
   end record;
   type Decision is (Input_Invalid, Original_Collapse_Denied,
      Resulting_Requirement_Absent, Requirement_Changed, Owner_Scope_Mismatch,
      Owner_Not_Authorized, Retry_Not_Admitted, Ready);
   Digest_Prefix : constant String := "sha256:";
   function Nibble (V : Interfaces.Unsigned_8) return Interfaces.Unsigned_8 is
     (if V < 10 then Character'Pos ('0') + V
      else Character'Pos ('a') + V - 10)
     with Global => null, Pre => V <= 15;
   -- Full lowercase digest identity, never a prefix or truncated comparison.
   function Hash_Holds (A : E.Byte_Array; Span : K.Optional_Identity;
      Present : Boolean; Value : Worldline.Hash) return Boolean is
     (Present and then K.Present (A, Span)
      and then Span.Value.Length = Digest_Prefix'Length + Worldline.Hash'Length * 2
      and then (for all P in Digest_Prefix'Range =>
        A (Span.Value.First + E.Byte_Count (P - Digest_Prefix'First)) =
          Character'Pos (Digest_Prefix (P)))
      and then (for all J in Worldline.Hash'Range =>
        A (Span.Value.First + Digest_Prefix'Length + E.Byte_Count (J) * 2) = Nibble (Value (J) / 16)
        and then A (Span.Value.First + Digest_Prefix'Length + E.Byte_Count (J) * 2 + 1) =
          Nibble (Value (J) mod 16))) with Global => null;
   function Scope_Holds (A : E.Byte_Array; S : Full_Scope; Q : K.Request)
      return Boolean is
     (K.Same (A, S.Subject, Q.Subject) and then K.Same (A, S.Content, Q.Content)
      and then K.Same (A, S.Transaction, Q.Transaction)) with Global => null;
   function Original_Scope_Holds (A : E.Byte_Array; S : Full_Scope;
      Original : C.Collapse_Request) return Boolean is
     (Worldline.Owner_Subject_Projection.Matches (A, S.Subject,
        Original.Mode = C.Checkpoint_Return, Original.Expected_Subject)
      and then (Original.Mode /= C.Checkpoint_Return or else
        Hash_Holds (A, S.Content, Original.Expected_Checkpoint.Present,
          Hash (Original.Expected_Checkpoint.Value)))) with Global => null;
   function Adopt_Holds (A : E.Byte_Array; H : E.History; F : E.Optional_Record;
      Original : C.Collapse_Request; Resulting : I.Optional_Requirement_Id;
      Scope : Full_Scope; Adopt : Optional_Adopt) return Boolean is
     (Adopt.Present and then Adopt.Value.Action = K.Adopt_Requirement
      and then Scope_Holds (A, Scope, Adopt.Value)
      and then Original_Scope_Holds (A, Scope, Original)
      and then Hash_Holds (A, Adopt.Value.Current_Requirement,
        Original.Current_Requirement.Present, Hash (Original.Current_Requirement.Value))
      and then Hash_Holds (A, Adopt.Value.Resulting_Requirement,
        Resulting.Present, Hash (Resulting.Value))
      and then K.Reference (A, H, F, Adopt.Value) = K.Ready) with Global => null;
   function Checkpoint_Holds (A : E.Byte_Array; H : E.History; F : E.Optional_Record;
      Original : C.Collapse_Request; Resulting : I.Optional_Requirement_Id;
      Scope : Full_Scope; Adopt : Optional_Adopt) return Boolean is
     (Original.Mode = C.Checkpoint_Return and then C.All_Hold (Original)
      and then Original.Current_Requirement.Present and then Resulting.Present
      and then (if Adopt.Present then
        Adopt_Holds (A, H, F, Original, Resulting, Scope, Adopt)
        else I.Same (Original.Current_Requirement, Resulting))) with Global => null;
   function Checkpoint_Reference (A : E.Byte_Array; H : E.History; F : E.Optional_Record;
      Original : C.Collapse_Request; Resulting : I.Optional_Requirement_Id;
      Scope : Full_Scope; Adopt : Optional_Adopt) return Decision
     with Global => null, Post => (Checkpoint_Reference'Result = Ready) =
       Checkpoint_Holds (A, H, F, Original, Resulting, Scope, Adopt);
   function Authorize_Checkpoint (A : E.Byte_Array; H : E.History; F : E.Optional_Record;
      Original : C.Collapse_Request; Resulting : I.Optional_Requirement_Id;
      Scope : Full_Scope; Adopt : Optional_Adopt) return Decision
     with Global => null, Post => Authorize_Checkpoint'Result =
       Checkpoint_Reference (A, H, F, Original, Resulting, Scope, Adopt);
   function Retry_Holds (A : E.Byte_Array; Before, After : E.History;
      Before_Final, After_Final : E.Optional_Record; Original : C.Collapse_Request;
      Scope : Full_Scope; Audit : R.Audit) return Boolean is
     (Original.Mode = C.Candidate_Evaluation and then C.All_Hold (Original)
      and then Scope_Holds (A, Scope, Audit.Before_Request)
      and then Original_Scope_Holds (A, Scope, Original)
      and then Hash_Holds (A, Audit.Before_Request.Current_Requirement,
        Original.Current_Requirement.Present, Hash (Original.Current_Requirement.Value))
      and then Hash_Holds (A, Audit.Before_Request.Resulting_Requirement,
        Original.Resulting_Requirement.Present, Hash (Original.Resulting_Requirement.Value))
      and then R.Holds (A, Before, After, Before_Final, After_Final, Audit))
     with Global => null;
   function Retry_Reference (A : E.Byte_Array; Before, After : E.History;
      Before_Final, After_Final : E.Optional_Record; Original : C.Collapse_Request;
      Scope : Full_Scope; Audit : R.Audit) return Decision
     with Global => null, Post => (Retry_Reference'Result = Ready) =
       Retry_Holds (A, Before, After, Before_Final, After_Final, Original, Scope, Audit);
   function Authorize_Retry (A : E.Byte_Array; Before, After : E.History;
      Before_Final, After_Final : E.Optional_Record; Original : C.Collapse_Request;
      Scope : Full_Scope; Audit : R.Audit) return Decision
     with Global => null, Post => Authorize_Retry'Result = Retry_Reference
       (A, Before, After, Before_Final, After_Final, Original, Scope, Audit);
   function Adopt_Receipt_Holds (A : E.Byte_Array; H : E.History; F : E.Optional_Record;
      Original : C.Collapse_Request; Resulting : I.Optional_Requirement_Id;
      Scope : Full_Scope; Audit : R.Audit) return Boolean is
     (Checkpoint_Holds (A, H, F, Original, Resulting, Scope,
        (Present => True, Value => Audit.Before_Request))
      and then R.Receipt_Holds (A, Audit.Before_Request.Grant, Audit.Receipt))
     with Global => null;
   function Adopt_Receipt_Reference (A : E.Byte_Array; H : E.History; F : E.Optional_Record;
      Original : C.Collapse_Request; Resulting : I.Optional_Requirement_Id;
      Scope : Full_Scope; Audit : R.Audit) return Decision
     with Global => null, Post => (Adopt_Receipt_Reference'Result = Ready) =
       Adopt_Receipt_Holds (A, H, F, Original, Resulting, Scope, Audit);
   function Authorize_Adopt_Receipt (A : E.Byte_Array; H : E.History; F : E.Optional_Record;
      Original : C.Collapse_Request; Resulting : I.Optional_Requirement_Id;
      Scope : Full_Scope; Audit : R.Audit) return Decision
     with Global => null, Post => Authorize_Adopt_Receipt'Result =
       Adopt_Receipt_Reference (A, H, F, Original, Resulting, Scope, Audit);
end Worldline.Owner_Conjunction;

with Interfaces;
with Attest.SHA256;
with Evaluation_History;
with Worldline.Identities;
with Worldline.Owner_Transitions;
-- Exact original _subject_digest / _return_binding + canonical JSON grammar.
-- This relation computes the projection; a matching hash does not authenticate
-- peer, producer, journal, source custody or executed native mapping.
package Worldline.Owner_Subject_Projection with SPARK_Mode is
   package E renames Evaluation_History;
   package K renames Worldline.Owner_Transitions;
   package I renames Worldline.Identities;
   use type I.Optional_Subject_Id;
   use type E.Byte_Count;
   use type Interfaces.Unsigned_8;
   use type Interfaces.Unsigned_64;
   procedure Feed (C : in out Attest.SHA256.Context; B : Interfaces.Unsigned_8;
      Valid : in out Boolean) with Global => null,
      Post => (if not Valid'Old then not Valid)
        and then (if Valid then Attest.SHA256.Absorbed (C) =
          Attest.SHA256.Absorbed (C'Old) + 1);
   procedure Feed_String (C : in out Attest.SHA256.Context; S : String;
      Valid : in out Boolean) with Global => null;
   function UTF8_Valid (A : E.Byte_Array; S : E.Identity_Span) return Boolean
     with Global => null, Pre => E.Span_Valid (A, S);
   procedure Quoted (C : in out Attest.SHA256.Context; A : E.Byte_Array;
      S : E.Identity_Span; Valid : in out Boolean)
     with Global => null, Pre => E.Span_Valid (A, S);
   function Reference (A : E.Byte_Array; Subject : K.Optional_Identity;
      Checkpoint : Boolean) return I.Optional_Subject_Id with Global => null;
   function Project (A : E.Byte_Array; Subject : K.Optional_Identity;
      Checkpoint : Boolean) return I.Optional_Subject_Id with Global => null,
      Post => Project'Result = Reference (A, Subject, Checkpoint);
   function Matches (A : E.Byte_Array; Subject : K.Optional_Identity;
      Checkpoint : Boolean; Expected : I.Optional_Subject_Id) return Boolean is
     (I.Same (Project (A, Subject, Checkpoint), Expected)) with Global => null;
end Worldline.Owner_Subject_Projection;

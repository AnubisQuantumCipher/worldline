with Interfaces.C;
with System;
with Worldline;
with Worldline.Evaluation_Wire;
with Evaluation_Completion_C;

--  Owned foreign-call boundary. Address arithmetic checks do not prove that
--  memory is live/readable/unchanged. The caller must keep all input extents
--  alive and stable for the call; output is disjoint. All native obligations
--  remain explicit. This is a new entry, not an exemption of an old body.
package Evaluation_Finalization_C with SPARK_Mode => Off is
   subtype I64 is Interfaces.Integer_64;
   subtype U32 is Interfaces.Unsigned_32;
   subtype U8 is Interfaces.Unsigned_8;
   subtype Span is Evaluation_Completion_C.Span;
   subtype Optional_Span is Evaluation_Completion_C.Optional_Span;
   subtype Required_Row is Evaluation_Completion_C.Required_Row;
   type Digest is array (Worldline.Hash'Range) of U8 with Convention => C;
   type Start_Record is record
      Store_Id, Subject, Run, Sequence : Span;
      Requirement : Optional_Span;
      Policy, Verifier_Plan, Base_Context : Span;
      Parent, Config, Repository : Digest;
      Required : Span;
      Declaration : U32;
   end record with Convention => C;
   type Input_Record is record
      Start : Start_Record;
      Root, Manifests : Span;
      Filesystem, Config, Repository : Digest;
   end record with Convention => C;
   type Row is record
      Start : Start_Record;
      Check_Id, Source_Id : Span;
      Execution, Verifier : Optional_Span;
      State, Outcome : U32;
      Payload, Declared : Span;
      Raw : Worldline.Evaluation_Wire.Raw_Record;
      Confinement : U8;
   end record with Convention => C;
   type Request is record
      Version, Operation : U32;
      Data : System.Address;
      Data_Length : I64;
      Start : Start_Record;
      Inputs : Input_Record;
      Post_Root, Post_Manifests : Span;
      Rows : System.Address;
      Row_Count : I64;
      Required : System.Address;
      Required_Count : I64;
      Completion : Required_Row;
      Content : Span;
      Environment_Root, Evidence_Root : Digest;
      Context, Source_Id, Evidence, Environment : Span;
   end record with Convention => C;
   type Result is record
      Reason, State, Outcome, Promotion : U32;
      Finalization_State, Finalization_Outcome : U32;
      Identity : Digest;
   end record with Convention => C;
   --  Operations: start validation, input validation, raw capture, final seal.
   --  Result Reason 0 means observed by the typed relation, not authenticated.
   --  Malformed transport returns 255 without publishing a partial result.
   function Version return U32 with Export, Convention => C,
     External_Name => "wl_finalization_version_v1";
   function Layout (Kind, Field : U32) return I64 with Export, Convention => C,
     External_Name => "wl_finalization_layout_v1";
   function Decide (Input, Output : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_finalization_decide_v1";
   --  Kind 0 absent, 1 original ordinary request, 2 additive finalization.
   --  Unneeded checkpoint inputs remain unobserved. Original ordinary entries
   --  are called with their unchanged guards; finalization is revalidated and
   --  joined to complete context/metadata inside this actual collapse call.
   function Decide_Mixed
     (Collapse : System.Address; Primary_Kind : U32;
      Primary, Primary_Raw, Primary_Confinement, Primary_Context : System.Address;
      Staged_Kind : U32;
      Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address;
      Agent_Confinement : U8) return U8
     with Export, Convention => C, External_Name => "wl_collapse_decide_finalization_v1";
end Evaluation_Finalization_C;

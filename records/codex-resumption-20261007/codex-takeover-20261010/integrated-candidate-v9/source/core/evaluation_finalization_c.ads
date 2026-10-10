with Interfaces.C;
with System;
with Worldline;
with Worldline.Evaluation_Wire;
with Evaluation_Completion_C;
with Worldline.Collapse_Wire;
with Worldline.Evaluation_Authority;

--  Typed native observer boundary. C_API alone maps foreign storage after
--  numerical shape checks. ctypes retains live stable read-only input owners
--  and exclusive disjoint output for the whole call. Original semantic copies
--  and authority decisions remain in this analyzed unit.
package Evaluation_Finalization_C with SPARK_Mode => On is
   subtype I64 is Interfaces.Integer_64;
   subtype U32 is Interfaces.Unsigned_32;
   subtype U8 is Interfaces.Unsigned_8;
   use type I64;
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
   --  Only C_API constructs these observers. Numerical transport metadata is
   --  retained; semantic snapshot loops below remain analyzed SPARK code.
   --  Reuse the original shared span layout and the exact raw-record fields.
   --  Preserve padding before Start.Required and at both enclosing row tails.
   Wide_Alignment_Bits : constant := Evaluation_Completion_C.Wide_Alignment_Bits;
   Span_Bits : constant := Evaluation_Completion_C.Span_Bits;
   Optional_Span_Bits : constant := Evaluation_Completion_C.Optional_Span_Bits;
   Digest_Bits : constant := Digest'Length * U8'Object_Size;
   Start_Required_Offset_Bits : constant :=
     ((7 * Span_Bits + Optional_Span_Bits + 3 * Digest_Bits
       + Wide_Alignment_Bits - 1) / Wide_Alignment_Bits) * Wide_Alignment_Bits;
   Start_Bits : constant :=
     ((Start_Required_Offset_Bits + Span_Bits + U32'Object_Size
       + Wide_Alignment_Bits - 1) / Wide_Alignment_Bits) * Wide_Alignment_Bits;
   Row_Bits : constant :=
     ((Start_Bits + 4 * Span_Bits + 2 * Optional_Span_Bits
       + 2 * U32'Object_Size + Evaluation_Completion_C.Raw_Record_Bits
       + U8'Object_Size + Wide_Alignment_Bits - 1)
       / Wide_Alignment_Bits) * Wide_Alignment_Bits;
   type Row_Array is array (I64 range <>) of Row
     with Component_Size => Row_Bits;
   pragma Compile_Time_Error
     (Row_Array'Component_Size /= Row'Object_Size,
      "finalization row stride differs from its C element layout");
   type Row_Observer is access constant Row_Array;
   type Request_View is record
      Descriptor : Request;
      Address : System.Address;
      Data : Evaluation_Completion_C.Bytes_Observer;
      Rows : Row_Observer;
      Required : Evaluation_Completion_C.Required_Row_Observer;
   end record;
   type Ordinary_Observer is access constant Evaluation_Completion_C.Request_View;
   type Finalization_Observer is access constant Request_View;
   type Metadata_Observer is access constant Evaluation_Completion_C.Metadata_View;
   type Context_Observer is access constant Evaluation_Completion_C.Context_View;
   type Checkpoint_View is record
      Ordinary : Ordinary_Observer := null;
      Raw : Evaluation_Completion_C.Raw_View;
      Finalized : Finalization_Observer := null;
      Metadata : Metadata_Observer := null;
      Context : Context_Observer := null;
   end record;
   type Mixed_State is record
      Bound : Worldline.Collapse_Wire.Raw_Request;
      Needed : Worldline.Evaluation_Authority.Raw_Dependency;
      Primary_Ready, Staged_Ready, Agent_Ready : U8;
      Valid : Boolean;
   end record;
   function Extent_Valid (A : System.Address; Length, Alignment : I64)
      return Boolean;
   function Array_Extent (A : System.Address; N, Stride, Alignment : I64)
      return Boolean;
   function Disjoint (L : System.Address; LL : I64; R : System.Address; RL : I64)
      return Boolean with Pre => LL >= 0 and then RL >= 0;
   function Transport_Valid
     (X : Request; Input, Output : System.Address; Have_Output : Boolean)
      return Boolean;
   function Version return U32;
   function Layout (Kind, Field : U32) return I64;
   function Decide
     (Input : Request_View; Output_Address : System.Address;
      Output : in out Result) return Interfaces.C.int with Side_Effects;
   --  Original ordered readiness phases let C_API observe only needed storage.
   function Prepare_Mixed
     (Evidence : Evaluation_Completion_C.Evidence_View;
      Primary_Kind : U32; Primary : Checkpoint_View) return Mixed_State with Side_Effects;
   function Prepare_Staged
     (Prepared : Mixed_State; Staged_Kind : U32; Staged : Checkpoint_View)
      return Mixed_State with Side_Effects;
   function Finish_Prepare_Agent
     (Prepared : Mixed_State;
      Evidence : Evaluation_Completion_C.Evidence_View;
      Agent_Confinement : U8) return Mixed_State with Side_Effects;
   function Preview_Mixed (Prepared : Mixed_State) return U8;
   function Decide_Mixed
     (Prepared : Mixed_State;
      Evidence : Evaluation_Completion_C.Evidence_View;
      Primary_Kind : U32; Primary : Checkpoint_View;
      Staged_Kind : U32; Staged : Checkpoint_View;
      Agent_Confinement : U8) return U8 with Side_Effects;
end Evaluation_Finalization_C;

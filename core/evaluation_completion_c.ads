with Interfaces.C;
with System;
-- Explicit owned-call bridge. Numeric checks do not establish foreign memory
-- mapping, caller custody, snapshot truth, or SPARK proof of this boundary.
package Evaluation_Completion_C with SPARK_Mode => Off is
   subtype I64 is Interfaces.Integer_64;
   subtype U32 is Interfaces.Unsigned_32;
   type Span is record
      First : I64;
      Length : I64;
   end record with Convention => C;
   type Optional_Span is record
      Present : U32;
      Value : Span;
   end record with Convention => C;
   type Cursor is record
      Present : U32;
      Sequence : Span;
      Run : Span;
   end record with Convention => C;
   type Binding is record
      Store_Id : Span;
      Subject : Span;
      Content : Span;
      Run : Span;
      Sequence : Span;
      Requirement : Optional_Span;
   end record with Convention => C;
   type Journal_Row is record
      Bound : Binding;
      Previous : Cursor;
      Linked : U32;
   end record with Convention => C;
   type Capture is record
      Bound : Binding;
      Source_Id : Span;
      Context : Span;
      State : U32;
      Outcome : U32;
   end record with Convention => C;
   type Facts is record
      Source : U32;
      Status : U32;
      Channel : U32;
      Stage : U32;
      Exit_Present : U32;
      Exit_Integer : U32;
      Supervisor : U32;
      Supervisor_Stopped : U32;
      Bundle_Present : U32;
      Bundle_Is_Mapping : U32;
      Bundle_Stable : U32;
      Bundle_Changed : U32;
      Unsatisfied_Imports : U32;
   end record with Convention => C;
   type Presence is record
      Record_Identified : U32;
      Verdict_Recorded : U32;
      Binding_Established : U32;
      Declaration_Matches : U32;
      Bundle_Identified : U32;
   end record with Convention => C;
   type Required_Row is record
      Check_Id : Span;
      Declared : Span;
   end record with Convention => C;
   type Check_Row is record
      Bound : Binding;
      Check_Id : Span;
      Source_Id : Span;
      Execution : Optional_Span;
      Verifier : Optional_Span;
      State : U32;
      Outcome : U32;
      Payload : Span;
      Observed : Facts;
      Report : U32;
      Evidence : Presence;
      Declared : Span;
   end record with Convention => C;
   type History_Row is record
      Subject : Optional_Span;
      Content : Optional_Span;
      Requirement : Optional_Span;
      Run : Optional_Span;
      Sequence : Optional_Span;
      State : U32;
      Outcome : U32;
   end record with Convention => C;
   type Request is record
      Version : U32;
      Operation : U32;
      Data : System.Address;
      Data_Length : I64;
      Journal : System.Address;
      Journal_Count : I64;
      Current : Cursor;
      Captured : Capture;
      Captured_Results : System.Address;
      Captured_Count : I64;
      Retained_Present : U32;
      Retained : Capture;
      Retained_Results : System.Address;
      Retained_Count : I64;
      History : System.Address;
      History_Count : I64;
      Required : System.Address;
      Required_Count : I64;
      Policy : U32;
      Before_Root : Span;
      After_Root : Span;
      Completion : Required_Row;
      Observed_Binding : Binding;
   end record with Convention => C;
   type Result is record
      Reason : U32;
      Selected : I64;
      Summary_Present : U32;
      Summary : History_Row;
      Execution_State : U32;
      Outcome : U32;
      Promotion : U32;
   end record with Convention => C;
   -- Operation: Decide=0 (before reconciliation), Apply=1, Classify=2.
   -- Classify still validates the complete pending/capture binding via Decide.
   function ABI_Version return U32 with Export, Convention => C,
     External_Name => "wl_completion_abi_version_v1";
   function Layout_Size (Kind : U32) return I64 with Export, Convention => C,
     External_Name => "wl_completion_layout_size_v1";
   function Layout_Alignment (Kind : U32) return I64 with Export, Convention => C,
     External_Name => "wl_completion_layout_alignment_v1";
   function Layout_Offset (Kind, Field : U32) return I64 with Export, Convention => C,
     External_Name => "wl_completion_layout_offset_v1";
   function Decide (Input, Output : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_completion_decide_v1";
end Evaluation_Completion_C;

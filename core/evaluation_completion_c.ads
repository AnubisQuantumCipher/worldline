with Ada.Exceptions;
with Interfaces.C;
with Worldline.Collapse_Wire;
with Worldline.Evaluation_Wire;
with Worldline.Evaluation_Authority;
with System;
-- Explicit owned-call bridge. Numeric checks do not establish foreign memory
-- mapping, caller custody, snapshot truth, or SPARK proof of this boundary.
package Evaluation_Completion_C with SPARK_Mode => Off is
   subtype I64 is Interfaces.Integer_64;
   subtype U32 is Interfaces.Unsigned_32;
   -- Diagnostic-only control for a serial, owned diagnostic call. Disabled at
   -- library initialization. It cannot supply or alter an authority input.
   -- Enable=1 starts observation; Enable=0 stops and reports any write failure.
   -- Result 0 is clean, 1 is already-active/write-failed, 2 is invalid control.
   function Diagnostic_Control (Enable : U32) return U32
     with Export, Convention => C,
       External_Name => "wl_native_diagnostic_control_v1";
   procedure Diagnostic_Mark (Site : String);
   procedure Diagnostic_Value (Site : String; Value : I64);
   procedure Diagnostic_Exception
     (Site : String; Error : Ada.Exceptions.Exception_Occurrence);
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

   -- Additive raw operation: the complete same request/owned identities are
   -- checked by the original relation; every classification is recomputed from
   -- the raw wire. No 4096 policy/history cap is used by this semantic bridge.
   function Raw_Decide (Input, Raw_Rows, Confinements, Output : System.Address)
      return Interfaces.C.int with Export, Convention => C,
      External_Name => "wl_completion_raw_decide_v1";

   package A renames Worldline.Evaluation_Authority;
   type Context_Fields is array (A.Context_Field) of Optional_Span
     with Convention => C;
   type Row_Fields is array (A.Row_Field) of Optional_Span with Convention => C;
   type Context_Row is record
      Item : Check_Row;
      Expected, Observed : Row_Fields;
   end record with Convention => C;
   type Context_Input is record
      Version : U32;
      Data : System.Address;
      Data_Length : I64;
      Expected_Binding : Binding;
      Expected_Current : Cursor;
      Prepared_Current : Cursor;
      Expected, Observed : Context_Fields;
      Rows : System.Address;
      Row_Count : I64;
      Required : System.Address;
      Required_Count : I64;
      Policy : U32;
      Projection : Worldline.Collapse_Wire.Raw_Request;
      Agent : Worldline.Evaluation_Wire.Raw_Record;
      Agent_Confinement : Interfaces.Unsigned_8;
   end record with Convention => C;
   -- Numeric extent/alignment checks cannot prove foreign allocation custody.
   -- All pointees must be live, readable and immutable for the complete call.
   function Context_Layout (Kind, Field : U32) return I64
     with Export, Convention => C, External_Name => "wl_completion_context_layout_v1";
   function Context_Matches
     (Input, Context, Collapse, Agent : System.Address;
      Agent_Confinement : Interfaces.Unsigned_8) return Interfaces.C.int;

   -- Additive descriptor; the original Context_Input and layout v1 are exact.
   -- Base points to that original descriptor. Data is an independent immutable
   -- byte arena for projections; no combined-arena semantic capacity is added.
   type Row_Metadata is record
      Check_Id, Source_Id, Payload : Span;
      Execution, Verifier : Optional_Span;
   end record with Convention => C;
   type Metadata_Context is record
      Version : U32;
      Base, Data : System.Address;
      Data_Length : I64;
      Rows : System.Address;
      Row_Count : I64;
   end record with Convention => C;
   function Metadata_Layout (Kind, Field : U32) return I64
     with Export, Convention => C, External_Name => "wl_completion_metadata_layout_v1";
   function Metadata_Matches (Input, Context : System.Address)
      return Interfaces.C.int with Export, Convention => C,
        External_Name => "wl_completion_metadata_matches_v1";
   function Metadata_Base (Context : System.Address) return System.Address;
end Evaluation_Completion_C;

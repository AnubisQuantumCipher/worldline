with Interfaces.C;
with Evaluation_Pending;
with Worldline.Collapse_Wire;
with Worldline.Evaluation_Wire;
with Worldline.Evaluation_Authority;
with System;
-- Explicit owned-call bridge. Numeric checks do not establish foreign memory
-- mapping, caller custody, snapshot truth, or SPARK proof of this boundary.
package Evaluation_Completion_C with SPARK_Mode => On is
   subtype I64 is Interfaces.Integer_64;
   subtype U32 is Interfaces.Unsigned_32;
   -- Diagnostic-only control for a serial, owned diagnostic call. Disabled at
   -- library initialization. It cannot supply or alter an authority input.
   -- Enable=1 starts observation; Enable=0 stops and reports any write failure.
   -- Result 0 is clean, 1 is already-active/write-failed, 2 is invalid control.
   function Diagnostic_Control (Enable : U32) return U32
     with Side_Effects, Always_Terminates;
   procedure Diagnostic_Mark (Site : String) with Always_Terminates;
   procedure Diagnostic_Value (Site : String; Value : I64) with Always_Terminates;
   --  Capture Exception_Information statically inside the original handler.
   --  GNAT.Current_Exception must never be hidden in a library-level helper:
   --  its intrinsic is bound to the lexically enclosing handler.
   function Diagnostic_Enabled return Boolean with Volatile_Function, Side_Effects;
   function Diagnostic_Retention_Failed return Boolean
     with Volatile_Function, Side_Effects;
   procedure Diagnostic_Capture_Failed with Always_Terminates;
   procedure Diagnostic_Exception (Site, Information : String)
     with Always_Terminates;
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
   --  Value rows for the finalization projection. Not a C ABI type. The
   --  exported address entries keep their disjoint-output checks.
   type Check_Row_Array is array (I64 range <>) of Check_Row;
   type Required_Row_Array is array (I64 range <>) of Required_Row;
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
   function ABI_Version return U32;
   function Layout_Size (Kind : U32) return I64;
   function Layout_Alignment (Kind : U32) return I64;
   function Layout_Offset (Kind, Field : U32) return I64;
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
   function Context_Layout (Kind, Field : U32) return I64;
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
   function Metadata_Layout (Kind, Field : U32) return I64;
   --  These views exist only for the extent of a native call. The sole C_API
   --  boundary maps live immutable ctypes objects; all semantic snapshots,
   --  encoding guards and authority decisions remain in this analyzed unit.
   --  Static C strides follow the actual nested element fields, not composite
   --  Size attributes. Every wide-field boundary and tail keeps I64 padding.
   Wide_Alignment_Bits : constant := I64'Alignment * System.Storage_Unit;
   Span_Bits : constant := 2 * I64'Object_Size;
   Flag_Bits : constant :=
     ((U32'Object_Size + Wide_Alignment_Bits - 1) / Wide_Alignment_Bits)
       * Wide_Alignment_Bits;
   Optional_Span_Bits : constant := Flag_Bits + Span_Bits;
   Cursor_Bits : constant := Flag_Bits + 2 * Span_Bits;
   Binding_Bits : constant := 5 * Span_Bits + Optional_Span_Bits;
   Journal_Row_Bits : constant := Binding_Bits + Cursor_Bits + Flag_Bits;
   Required_Row_Bits : constant := 2 * Span_Bits;
   Check_Declared_Offset_Bits : constant :=
     ((Binding_Bits + 3 * Span_Bits + 2 * Optional_Span_Bits
       + (2 + 13 + 1 + 5) * U32'Object_Size + Wide_Alignment_Bits - 1)
       / Wide_Alignment_Bits) * Wide_Alignment_Bits;
   Check_Row_Bits : constant := Check_Declared_Offset_Bits + Span_Bits;
   History_Row_Bits : constant :=
     ((5 * Optional_Span_Bits + 2 * U32'Object_Size + Wide_Alignment_Bits - 1)
       / Wide_Alignment_Bits) * Wide_Alignment_Bits;
   Raw_Record_Bits : constant :=
     (Worldline.Evaluation_Wire.Raw_Observations'Length + 1
      + Worldline.Evaluation_Wire.R.Raw_Facts'Length
      + Worldline.Evaluation_Wire.Raw_Presence'Length)
       * Worldline.Evaluation_Wire.Byte'Object_Size;
   Context_Row_Bits : constant :=
     Check_Row_Bits + 2 * Row_Fields'Length * Optional_Span_Bits;
   Row_Metadata_Bits : constant := 3 * Span_Bits + 2 * Optional_Span_Bits;
   type Check_Buffer_Array is array (I64 range <>) of Check_Row
     with Component_Size => Check_Row_Bits;
   type Required_Buffer_Array is array (I64 range <>) of Required_Row
     with Component_Size => Required_Row_Bits;
   type Journal_Row_Array is array (I64 range <>) of Journal_Row
     with Component_Size => Journal_Row_Bits;
   type History_Row_Array is array (I64 range <>) of History_Row
     with Component_Size => History_Row_Bits;
   type Raw_Row_Array is array (I64 range <>) of Worldline.Evaluation_Wire.Raw_Record
     with Component_Size => Raw_Record_Bits;
   type Context_Row_Array is array (I64 range <>) of Context_Row
     with Component_Size => Context_Row_Bits;
   type Row_Metadata_Array is array (I64 range <>) of Row_Metadata
     with Component_Size => Row_Metadata_Bits;
   pragma Compile_Time_Error
     (Check_Buffer_Array'Component_Size /= Check_Row'Object_Size
      or else Required_Buffer_Array'Component_Size /= Required_Row'Object_Size
      or else Journal_Row_Array'Component_Size /= Journal_Row'Object_Size
      or else History_Row_Array'Component_Size /= History_Row'Object_Size
      or else Raw_Row_Array'Component_Size /= Worldline.Evaluation_Wire.Raw_Record'Object_Size
      or else Context_Row_Array'Component_Size /= Context_Row'Object_Size
      or else Row_Metadata_Array'Component_Size /= Row_Metadata'Object_Size,
      "completion row strides differ from their C element layouts");
   type Bytes_Observer is access constant Evaluation_Pending.Bytes;
   type Journal_Row_Observer is access constant Journal_Row_Array;
   type Check_Row_Observer is access constant Check_Buffer_Array;
   type History_Row_Observer is access constant History_Row_Array;
   type Required_Row_Observer is access constant Required_Buffer_Array;
   type Raw_Row_Observer is access constant Raw_Row_Array;
   type Context_Row_Observer is access constant Context_Row_Array;
   type Row_Metadata_Observer is access constant Row_Metadata_Array;
   type Request_View is record
      Descriptor : Request;
      Address : System.Address := System.Null_Address;
      Data : Bytes_Observer := null;
      Journal : Journal_Row_Observer := null;
      Captured, Retained : Check_Row_Observer := null;
      History : History_Row_Observer := null;
      Required : Required_Row_Observer := null;
   end record;
   type Raw_View is record
      Rows : Raw_Row_Observer := null;
      Confinements : Bytes_Observer := null;
      Rows_Address, Confinements_Address : System.Address := System.Null_Address;
   end record;
   type Context_View is record
      Descriptor : Context_Input;
      Address : System.Address := System.Null_Address;
      Data : Bytes_Observer := null;
      Rows : Context_Row_Observer := null;
      Required : Required_Row_Observer := null;
   end record;
   type Metadata_View is record
      Descriptor : Metadata_Context;
      Address : System.Address := System.Null_Address;
      Data : Bytes_Observer := null;
      Rows : Row_Metadata_Observer := null;
   end record;
   type Evidence_View is record
      Collapse : Worldline.Collapse_Wire.Raw_Request;
      Agent : Worldline.Evaluation_Wire.Raw_Record;
      Collapse_Address, Agent_Address : System.Address;
   end record;
   --  Numeric transport predicates establish shape only, never allocation.
   function Extent_Valid (A : System.Address; Length, Alignment : I64) return Boolean;
   function Array_Extent (A : System.Address; N, Stride, Alignment : I64) return Boolean;
   function Decide
     (Input : Request_View; Output : System.Address; Observed : in out Result)
      return Interfaces.C.int with Side_Effects;
   function Raw_Decide
     (Input : Request_View; Raw : Raw_View; Output : System.Address;
      Observed : in out Result) return Interfaces.C.int with Side_Effects;
   function Raw_Decide_Observed
     (Input : Request_View; Raw : Raw_View; Observed : in out Result)
      return Interfaces.C.int with Side_Effects;
   function Context_Matches
     (Input : Request_View; Context : Context_View; Evidence : Evidence_View;
      Agent_Confinement : Interfaces.Unsigned_8) return Interfaces.C.int with Side_Effects;
   function Context_Matches_Projected
     (Input : Request_View; Projected_Rows : Check_Row_Array;
      Projected_Plans : Required_Row_Array; Context : Context_View;
      Evidence : Evidence_View; Agent_Confinement : Interfaces.Unsigned_8)
      return Interfaces.C.int with Side_Effects;
   function Metadata_Matches
     (Input : Request_View; Context : Metadata_View)
      return Interfaces.C.int with Side_Effects;
   function Metadata_Matches_Projected
     (Input : Request_View; Projected_Rows : Check_Row_Array;
      Context : Metadata_View) return Interfaces.C.int with Side_Effects;
   function Metadata_Base (Context : Metadata_View) return System.Address;
end Evaluation_Completion_C;

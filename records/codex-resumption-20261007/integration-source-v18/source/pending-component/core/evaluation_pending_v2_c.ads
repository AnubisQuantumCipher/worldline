with Interfaces.C;
with System;

--  Pointer extents and custody are C-caller premises, not proved by this ABI.
package Evaluation_Pending_V2_C with SPARK_Mode => Off is
   subtype I64 is Interfaces.Integer_64;
   subtype U32 is Interfaces.Unsigned_32;
   type Span is record First, Length : I64; end record
     with Convention => C;
   type Cursor is record
      Present : U32;
      Sequence : Span;
      Run : Span;
   end record with Convention => C;
   type Optional_Requirement is record
      Present : U32;
      Value : Span;
   end record with Convention => C;
   type Row is record
      Store_Id, Subject, Content, Run : Span;
      Sequence : Span;
      Previous : Cursor;
      Linked : U32;
      Requirement : Optional_Requirement;
   end record with Convention => C;
   type Request is record
      Version, Operation : U32;
      Data : System.Address;
      Data_Length : I64;
      Rows : System.Address;
      Row_Count : I64;
      Store_Id, Subject, Content, Run, Proposed_Epoch : Span;
      Authority_Head, Target_Head : Cursor;
      Required : Optional_Requirement;
   end record with Convention => C;
   type Result is record
      Reason : U32;
      Sequence : Span;
      Selected : I64;
      Requirement : Optional_Requirement;
   end record with Convention => C;
   --  Layout kinds: Span, Cursor, Row, Request, Result, Optional_Requirement.
   --  Unknown kind/field returns I64'Last, never a plausible layout value.
   function ABI_Version return U32
     with Export, Convention => C, External_Name => "wl_pending_abi_version_v2";
   function Layout_Size (Kind : U32) return I64
     with Export, Convention => C, External_Name => "wl_pending_layout_size_v2";
   function Layout_Alignment (Kind : U32) return I64
     with Export, Convention => C, External_Name => "wl_pending_layout_alignment_v2";
   function Layout_Offset (Kind, Field : U32) return I64
     with Export, Convention => C, External_Name => "wl_pending_layout_offset_v2";
   function Decide (Input, Output : System.Address) return Interfaces.C.int
     with Export, Convention => C, External_Name => "wl_pending_decide_v2";
end Evaluation_Pending_V2_C;

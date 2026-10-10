with Evaluation_Pending;
with Interfaces.C;
with System;

--  C_API maps caller-owned live read-only views; this analyzed unit performs
--  the original single byte/journal snapshot and all semantic decisions.
package Evaluation_Pending_V2_C with SPARK_Mode => On is
   subtype I64 is Interfaces.Integer_64;
   subtype U32 is Interfaces.Unsigned_32;
   use type I64;
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
   type Row_Array is array (Evaluation_Pending.Index range <>) of aliased Row
     with Convention => C, Component_Size => Row'Object_Size;

   function Extent_Valid
     (A : System.Address; Length, Alignment : I64) return Boolean;
   function Disjoint
     (Left : System.Address; Left_Length : I64;
      Right : System.Address; Right_Length : I64) return Boolean
     with Pre => Left_Length >= 0 and then Right_Length >= 0;
   function Fixed_Valid (Input, Output : System.Address) return Boolean;
   function Valid (S : Span) return Boolean;
   function Valid (C : Cursor) return Boolean;
   function Valid (Q : Optional_Requirement) return Boolean;
   function Transport_Valid (R : Request; Output : System.Address) return Boolean
     with Post =>
       (if Transport_Valid'Result then
           R.Data_Length >= 0 and then R.Row_Count >= 0
           and then Valid (R.Store_Id) and then Valid (R.Subject)
           and then Valid (R.Content) and then Valid (R.Run)
           and then Valid (R.Proposed_Epoch)
           and then Valid (R.Authority_Head) and then Valid (R.Target_Head)
           and then Valid (R.Required));
   procedure Read_Request
     (Source : not null access constant Request; Item : out Request);

   --  These observers can alias one another, but not the foreign mutable result.
   --  C_API holds the actual output until the original successful write point.
   function Decide
     (R : Request; Output_Address : System.Address;
      Data : not null access constant Evaluation_Pending.Bytes;
      Rows : not null access constant Row_Array; Item : out Result)
      return Interfaces.C.int with Side_Effects;
end Evaluation_Pending_V2_C;

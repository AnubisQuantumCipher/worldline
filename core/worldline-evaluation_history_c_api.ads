with Interfaces;
with Interfaces.C;
with System;

--  Owned snapshot transport only. All declared input extents must remain live,
--  aligned, readable and unchanged during the call. Result storage is live,
--  writable and disjoint. These pointer/custody premises are not SPARK proofs.
package Worldline.Evaluation_History_C_API with SPARK_Mode => Off is
   subtype U8 is Interfaces.Unsigned_8;
   subtype Size is Interfaces.C.size_t;
   type Identity_C is record
      Present : U8;
      First, Length : Size;
   end record with Convention => C;
   type Epoch_C is record
      Present : U8;
      First, Length : Size;
   end record with Convention => C;
   type Cursor_C is record
      Present : U8;
      Sequence : Epoch_C;
      Run : Identity_C;
   end record with Convention => C;
   type Row_C is record
      Subject, Content, Requirement, Run : Identity_C;
      Sequence : Epoch_C;
      State, Outcome : U8;
   end record with Convention => C;
   type Query_C is record
      Subject, Content, Requirement : Identity_C;
      Current_Head, Prepared_Evidence : Cursor_C;
   end record with Convention => C;
   type Selection_C is record
      Reason, Head_Kind : U8;
      Head_Index : Size;
      Failure_Kind : U8;
      Failure_Index : Size;
   end record with Convention => C;
   function ABI_Version return Interfaces.Unsigned_32
     with Export, Convention => C,
       External_Name => "wl_evaluation_history_abi_version";
   --  Kinds 1 identity, 2 epoch, 3 cursor, 4 row, 5 query, 6 selection.
   function Layout_Size (Kind : U8) return Size
     with Export, Convention => C,
       External_Name => "wl_evaluation_history_layout_size";
   function Layout_Offset (Kind, Field : U8) return Size
     with Export, Convention => C,
       External_Name => "wl_evaluation_history_layout_offset";
   --  0 means a complete typed result was written; 255 is a transport failure
   --  and leaves the output untouched. Absent payload fields are ignored.
   --  History order is retained exactly. No payload/context filtering occurs.
   function Select_Evidence
     (Data : System.Address; Data_Length : Size;
      Rows : System.Address; Row_Count : Size;
      Final_Present : U8; Final_Row, Query, Output : System.Address) return U8
     with Export, Convention => C,
       External_Name => "wl_evaluation_history_select";
end Worldline.Evaluation_History_C_API;

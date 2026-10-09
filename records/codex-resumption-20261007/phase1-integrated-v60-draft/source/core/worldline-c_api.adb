with Worldline.Evaluation_Policy;
with Worldline.Report_Parser;
with Worldline.Protected_Paths;
with Worldline.Runner_Acquisition_Bytes;
with Worldline.Evaluation_Producer;
with Worldline.Evaluation_Wire;
with Worldline.Archive_Envelope;
with Worldline.Manager_Resource_Lifecycle;
with Worldline.Ordinary_Reservation_Lifecycle;
with Worldline.Runner_Lifecycle;
with Worldline.Runner_Outcome;
with Worldline.Recovery_Packet;
with Worldline.Recovery_Material_Replay;
with Canonical_Artifacts;
with Exact_Decimal;
with Decimal_Binary64;
with Worldline.Journal_Witness;
with Worldline.Operation_Result_View;
with Worldline.Ordinary_Receipt_Policy;
with Worldline.Transaction_Relations;
with Worldline.Operation_Archive;
with Worldline.Native_Execution_Views;
with Worldline.Native_Execution_Capture;
with Resource_Observation_Classification_Wire;
with Ada.Exceptions;
with Worldline.Startup_Admission_Owned;
with Worldline.Canonical_Operation_Wire;
with Ada.Unchecked_Conversion;
with Worldline.Operation_Authority_Wire;
with Worldline.Chain_Authority_Wire;
with Worldline.Custody_V2_Prepared_Wire;
with Worldline.Retained_Custody_Chain;
with Ada.Finalization;
with Worldline.Custody_V2_Provision;
with Worldline.Emitter_Allocation_Capture;
with Worldline.Root_Output_Sequence;
with Worldline.Custody_V2_Mutation_Decision;
with Worldline.Custody_V2_Fold_Engine;
with Worldline.Custody_V2_Load_Input;
with Worldline.Custody_V2_Operation_Journal;
with Ada.IO_Exceptions;
with Native_Diagnostic_Trace;
with Worldline.Owner_Retry_Audit;
with Worldline.Owner_Retry_Audit_Wire;
with Worldline.Owner_Conjunction;
with Worldline.Owner_Conjunction_Wire;
with Worldline.Collapse_Wire;
with Evaluation_History;
with Worldline.Owner_Transitions;
with Worldline.Owner_Transitions_Wire;
with Evaluation_Completion_C;
with Evaluation_Pending;
with Evaluation_Finalization_C;
with Worldline.Recovery_Authorization_C_API;
with Worldline.Recovery_Authorization_Wire;
with Worldline.Recovery_Authorization_V3_C_API;
with Worldline.Recovery_Authorization_V3_Wire;
with Resource_Quantities;
with Worldline.Recovery_Protocol_C_API;
with Worldline.Recovery_Protocol_Wire;
with Worldline.Chain_Authority_C_API;
with Worldline.Recovery_C_API;
with Worldline.Recovery;
with Worldline.Evaluation_History_C_API;
with Resource_Ledger;
with Resource_Run_Ledger_Wire;
with Resource_Reservation_Lifecycle;
with Worldline.Resources;
with Worldline.Resources_C_API;
with Worldline.Resource_Policy_C_API;
with Worldline.Resource_Ledger_C_API;
with Resource_Run_Ledger_C_API;
with Worldline.Reservation_Lifecycle_C_API;
with Evaluation_Pending_C;
with Evaluation_Pending_V2_C;
with Evaluation_Completion;
with Worldline.Evaluation_Authority;
with Worldline.Collapse;
with System.Address_To_Access_Conversions;
with Ada.Streams;
with Ada.Streams.Stream_IO;
with Attest;
with Attest.SHA256;
with System.Storage_Elements;
with Worldline.Causal_Graph;
with Worldline.Evaluation;
with Worldline.Receipts;
with Worldline.Transitions;
with Worldline.World;

package body Worldline.C_API with SPARK_Mode => Off is
   --  Physical serialization and descriptor output remain in this sole
   --  original Off C_API. The C helper is enrolled real environmental source;
   --  mutex acquisition can block and has NO proved termination/purity claim.
   --  Every export encloses guard/view elaboration in an outer handled block.
   --  Its outer handler returns only the existing failure representation; it
   --  cannot touch shared Ada state after an acquired guard has finalized.
   function Native_Enter return Interfaces.C.int
     with Import, Convention => C, External_Name => "wl_native_call_enter_v1";
   function Native_Leave return Interfaces.C.int
     with Import, Convention => C, External_Name => "wl_native_call_leave_v1";
   function Native_Depth return Interfaces.C.unsigned
     with Import, Convention => C, External_Name => "wl_native_call_depth_v1";
   function Native_Errors return Interfaces.Unsigned_32
     with Import, Convention => C, External_Name => "wl_native_diag_errors_v1";
   procedure Native_Reset_Errors
     with Import, Convention => C, External_Name => "wl_native_diag_reset_errors_v1";
   function Native_Emit (Data : System.Address; Length : Interfaces.C.size_t)
     return Interfaces.Unsigned_32
     with Import, Convention => C, External_Name => "wl_native_diag_emit_v1";

   procedure Flush_Native_Diagnostic_Trace;
   type Native_Call_Guard is new Ada.Finalization.Limited_Controlled with record
      Owned : Boolean := False;
   end record;
   overriding procedure Initialize (Guard : in out Native_Call_Guard);
   overriding procedure Finalize (Guard : in out Native_Call_Guard);

   overriding procedure Initialize (Guard : in out Native_Call_Guard) is
      use type Interfaces.C.int;
      use type Interfaces.Unsigned_32;
      Result : Interfaces.C.int;
   begin
      Result := Native_Enter;
      if Result /= 0 then raise Ada.IO_Exceptions.Device_Error; end if;
      Guard.Owned := True;
      if Native_Errors /= 0 then
         Evaluation_Completion_C.Diagnostic_Capture_Failed;
      end if;
   exception
      when others =>
         if Guard.Owned then
            Guard.Owned := False;
            if Native_Leave /= 0 then null; end if;
         end if;
         raise;
   end Initialize;

   overriding procedure Finalize (Guard : in out Native_Call_Guard) is
      use type Interfaces.C.unsigned;
      use type Interfaces.C.int;
   begin
      if Guard.Owned then
         --  The outermost guard spans input validation, snapshots, typed
         --  decisions, nested exported calls, all primary handlers and drain.
         --  No nested call drains its parent's queue or restores cancellation.
         begin
            if Native_Depth = 1 then Flush_Native_Diagnostic_Trace; end if;
         exception
            when others => Evaluation_Completion_C.Diagnostic_Capture_Failed;
         end;
         Guard.Owned := False;
         --  C leaves the recursive lock BEFORE restoring cancellation. A
         --  pending asynchronous cancellation may take effect after release;
         --  this finalizer never reports a secondary successful observation.
         if Native_Leave /= 0 then null; end if;
         --  Native_Leave itself latches any real restore/unlock failure. Do not
         --  mutate shared Ada flags after releasing their lock.
      end if;
   end Finalize;

   procedure Capture_Native_Exception
     (Label : String; Error : Ada.Exceptions.Exception_Occurrence) is
   begin
      -- Build and retain the complete original exception text inside the
      -- secondary handler; failures never replace the primary ABI result.
      Native_Diagnostic_Trace.Push
        (Label & Ada.Exceptions.Exception_Information (Error));
   exception
      when others => Evaluation_Completion_C.Diagnostic_Capture_Failed;
   end Capture_Native_Exception;

   procedure Emit_Native_Diagnostic (Text : String) is
      use type Interfaces.Unsigned_32;
      Data : System.Address := System.Null_Address;
   begin
      if Text'Length /= 0 then Data := Text (Text'First)'Address; end if;
      if Native_Emit (Data, Interfaces.C.size_t (Text'Length)) /= 0 then
         raise Ada.IO_Exceptions.Device_Error;
      end if;
   end Emit_Native_Diagnostic;

   procedure Flush_Native_Diagnostic_Trace is
      use type Native_Diagnostic_Trace.Line_Access;
      use type Interfaces.C.unsigned;
      --  The model donor's explicitly aliased out handoff is by-reference:
      --  if its allocating checked Post raises, detached ownership is already
      --  visible here for cleanup, rather than lost before scalar copyback.
      Items : aliased Native_Diagnostic_Trace.Line_Access := null;
   begin
      --  All callers, including OwnedAbi's explicit flush sites, are inside
      --  the same guard. Do not detach/drain a parent's unfinished trace.
      if Native_Depth /= 1 then return; end if;
      Native_Diagnostic_Trace.Take_All (Items);
      while Items /= null loop
         declare
            Item : Native_Diagnostic_Trace.Line_Access := Items;
         begin
            Items := Item.Next;
            Item.Next := null;
            begin
               Emit_Native_Diagnostic (Item.Text);
            exception
               when others => Evaluation_Completion_C.Diagnostic_Capture_Failed;
            end;
            Native_Diagnostic_Trace.Release (Item);
         end;
      end loop;
   exception
      when others =>
         Evaluation_Completion_C.Diagnostic_Capture_Failed;
         --  Take_All transferred ownership even when output failed. Release
         --  the entire still-owned remainder; never abandon the detached tail.
         while Items /= null loop
            declare
               Item : Native_Diagnostic_Trace.Line_Access := Items;
            begin
               Items := Item.Next;
               Item.Next := null;
               Native_Diagnostic_Trace.Release (Item);
            end;
         end loop;
   end Flush_Native_Diagnostic_Trace;

   function Diagnostic_Control (Enable : Interfaces.Unsigned_32)
     return Interfaces.Unsigned_32
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      use type Interfaces.Unsigned_32;
      use type Interfaces.C.unsigned;
      Status : Interfaces.Unsigned_32;
   begin
      Status := Evaluation_Completion_C.Diagnostic_Control (Enable);
      if Enable = 1 and then Status = 0 then Native_Reset_Errors; end if;
      Flush_Native_Diagnostic_Trace;
      if Enable = 0 and then Status = 0 and then
        (Evaluation_Completion_C.Diagnostic_Retention_Failed or else Native_Errors /= 0)
      then
         return 1;
      end if;
      return Status;
   exception
      when others =>
         --  An acquisition failure is already latched by real native source;
         --  shared Ada state may only be touched while actually guarded.
         if Native_Depth /= 0 then
            Evaluation_Completion_C.Diagnostic_Capture_Failed;
         end if;
         return 1;
      end;
   exception
      when others => return 1;
   end Diagnostic_Control;


   use type Interfaces.C.size_t;
   use type Interfaces.C.long;
   use type Resource_Quantities.Byte_Count;
   use type Interfaces.Integer_64;
   use type Interfaces.Unsigned_8;
   use type Ada.Streams.Stream_Element_Offset;
   use type Interfaces.Unsigned_64;
   use type System.Address;
   use type System.Storage_Elements.Integer_Address;

   --  GNAT's one-dimensional unconstrained-array observer is a data address
   --  followed by a bounds address, not a pointer to a constrained subtype.
   --  Bounds belong to the enclosing native call, never to a mapper's frame.
   --  These limited records contain only geometry; no caller array is copied.
   Foreign_Word_Bits : constant := Interfaces.Integer_64'Object_Size;
   Foreign_Word_Bytes : constant := Foreign_Word_Bits / System.Storage_Unit;
   type Foreign_Array_Bounds is limited record
      First : Interfaces.Integer_64 := 1;
      Last : Interfaces.Integer_64 := 0;
   end record
     with Size => 2 * Foreign_Word_Bits,
          Alignment => Interfaces.Integer_64'Alignment;
   for Foreign_Array_Bounds use record
      First at 0 range 0 .. Foreign_Word_Bits - 1;
      Last at Foreign_Word_Bytes range 0 .. Foreign_Word_Bits - 1;
   end record;
   --  GNAT reads these words through its internal array-bounds record type.
   --  State that real representation alias explicitly, without disabling
   --  checks, warnings or alias analysis for the caller's arrays.
   pragma Universal_Aliasing (Foreign_Array_Bounds);
   type Foreign_Array_Descriptor is record
      Data : System.Address;
      Bounds : System.Address;
   end record with Size => 2 * Foreign_Word_Bits;
   for Foreign_Array_Descriptor use record
      Data at 0 range 0 .. Foreign_Word_Bits - 1;
      Bounds at Foreign_Word_Bytes range 0 .. Foreign_Word_Bits - 1;
   end record;
   pragma Compile_Time_Error
     (System.Address'Size /= Foreign_Word_Bits
      or else Foreign_Array_Bounds'Object_Size /= 2 * Foreign_Word_Bits
      or else Foreign_Array_Descriptor'Object_Size /= 2 * Foreign_Word_Bits,
      "foreign array descriptor must retain both complete address/bounds words");
   Foreign_Empty : aliased Interfaces.Integer_64 := 0;

   generic
      type Index_Type is range <>;
      type Element_Type is private;
      type Array_Type is array (Index_Type range <>) of Element_Type;
      type Observer is access constant Array_Type;
   function Observe_Foreign_Array
     (Address : System.Address; Bounds : aliased in Foreign_Array_Bounds)
      return Observer;

   function Observe_Foreign_Array
     (Address : System.Address; Bounds : aliased in Foreign_Array_Bounds)
      return Observer
   is
      function Map is new Ada.Unchecked_Conversion
        (Foreign_Array_Descriptor, Observer);
   begin
      --  Record-array geometry need not be static in a generic instance.
      --  Check every nominal invariant before publishing the descriptor,
      --  independently of assertion policy; no caller element is inspected.
      if Index_Type'Object_Size /= Foreign_Word_Bits
        or else Index_Type'Alignment /= Foreign_Array_Bounds'Alignment
        or else Observer'Size /= Foreign_Array_Descriptor'Size
        or else Array_Type'Component_Size /= Element_Type'Object_Size
        or else Foreign_Empty'Alignment mod Array_Type'Alignment /= 0
      then
         raise Program_Error with
           "foreign array nominal index, descriptor, stride or empty alignment differs";
      end if;
      --  The calling transport has already checked its complete extent,
      --  alignment, host-index limits and required output separation. This
      --  descriptor does not establish memory validity or transfer ownership.
      --  Caller storage is stable through the guard; Bounds lives until every
      --  observer made from it has ceased to be used. An empty view reads no
      --  element and has a nonnull aligned anchor for not-null access formals.
      return Map
        ((Data => (if Bounds.Last = 0 then Foreign_Empty'Address else Address),
          Bounds => Bounds'Address));
   end Observe_Foreign_Array;
   --  The original bit-sized separation relation is shared by authority and
   --  recovery transports; exporting its scope changes neither lengths nor
   --  the established ordering/refusal behavior.
   function Disjoint (L : System.Address; L_Bits : Natural;
                      R : System.Address; R_Bits : Natural) return Boolean is
      use System.Storage_Elements;
   begin
      return
        (if To_Integer (L) <= To_Integer (R) then
           Integer_Address (L_Bits / System.Storage_Unit) <= To_Integer (R) - To_Integer (L)
         else Integer_Address (R_Bits / System.Storage_Unit) <= To_Integer (L) - To_Integer (R));
   end Disjoint;

   type Resource_Bytes_Observer is access constant Resource_Quantities.Byte_Array;
   function Observe_Resource_Bytes is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Resource_Quantities.Byte,
      Resource_Quantities.Byte_Array, Resource_Bytes_Observer);
   type Resources_Bytes_Observer is access constant Worldline.Resources.Byte_Array;
   function Observe_Resources_Bytes is new Observe_Foreign_Array
     (Worldline.Resources.Byte_Index, Worldline.Resources.Byte,
      Worldline.Resources.Byte_Array, Resources_Bytes_Observer);
   type Recovery_Bytes_Observer is access constant Worldline.Recovery.Identity_Bytes;
   function Observe_Recovery_Bytes is new Observe_Foreign_Array
     (Worldline.Recovery.Byte_Index, Interfaces.Unsigned_8,
      Worldline.Recovery.Identity_Bytes, Recovery_Bytes_Observer);
   package Native_Borrow_Types renames Worldline.Native_Execution_Views;
   type Native_History_Observer is access constant Native_Borrow_Types.N.Raw_History_Array;
   function Observe_Native_History is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.N.Raw_Scope_Frame, Native_Borrow_Types.N.Raw_History_Array, Native_History_Observer);
   type Native_Projection_Observer is access constant Native_Borrow_Types.N.Raw_Projection_Array;
   function Observe_Native_Projection is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.N.Raw_Projection, Native_Borrow_Types.N.Raw_Projection_Array, Native_Projection_Observer);
   type Native_Buckets_Observer is access constant Native_Borrow_Types.N.Raw_Bucket_Array;
   function Observe_Native_Buckets is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.N.Raw_Bucket, Native_Borrow_Types.N.Raw_Bucket_Array, Native_Buckets_Observer);
   type Native_Facts_Observer is access constant Native_Borrow_Types.N.Raw_Facts_Array;
   function Observe_Native_Facts is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.O.Raw_Facts, Native_Borrow_Types.N.Raw_Facts_Array, Native_Facts_Observer);
   type Native_Rows_Observer is access constant Native_Borrow_Types.W.Raw_Row_Array;
   function Observe_Native_Rows is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.W.Raw_Row, Native_Borrow_Types.W.Raw_Row_Array, Native_Rows_Observer);
   type Native_Observed_Observer is access constant Native_Borrow_Types.W.Raw_Native_Array;
   function Observe_Native_Observed is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.W.Raw_Native, Native_Borrow_Types.W.Raw_Native_Array, Native_Observed_Observer);
   type Native_Capabilities_Observer is access constant Native_Borrow_Types.D.Raw_Capability_Array;
   function Observe_Native_Capabilities is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.D.Raw_Capability, Native_Borrow_Types.D.Raw_Capability_Array, Native_Capabilities_Observer);
   type Native_Groups_Observer is access constant Native_Borrow_Types.D.Raw_Group_Array;
   function Observe_Native_Groups is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.W.Raw_Quantity, Native_Borrow_Types.D.Raw_Group_Array, Native_Groups_Observer);
   type Native_Grants_Observer is access constant Native_Borrow_Types.Raw_Grant_Array;
   function Observe_Native_Grants is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.T.Raw_Grant, Native_Borrow_Types.Raw_Grant_Array, Native_Grants_Observer);
   type Native_Uses_Observer is access constant Native_Borrow_Types.Raw_Use_Array;
   function Observe_Native_Uses is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.T.Raw_Use, Native_Borrow_Types.Raw_Use_Array, Native_Uses_Observer);
   type Native_Chain_Observer is access constant Native_Borrow_Types.Raw_Chain_Array;
   function Observe_Native_Chain is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.T.C.Raw_Row, Native_Borrow_Types.Raw_Chain_Array, Native_Chain_Observer);
   type Native_Tasks_Observer is access constant Native_Borrow_Types.Y.Raw_Task_Array;
   function Observe_Native_Tasks is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.Y.Raw_Task, Native_Borrow_Types.Y.Raw_Task_Array, Native_Tasks_Observer);
   type Native_Processes_Observer is access constant Native_Borrow_Types.Y.Raw_Process_Array;
   function Observe_Native_Processes is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.Y.Raw_Process, Native_Borrow_Types.Y.Raw_Process_Array, Native_Processes_Observer);
   type Native_Namespaces_Observer is access constant Native_Borrow_Types.Y.Raw_Namespace_Array;
   function Observe_Native_Namespaces is new Observe_Foreign_Array
     (Resource_Quantities.Byte_Index, Native_Borrow_Types.Y.Raw_Namespace, Native_Borrow_Types.Y.Raw_Namespace_Array, Native_Namespaces_Observer);

   package Byte_Pointers is new System.Address_To_Access_Conversions
     (Interfaces.Unsigned_8);

   Error_OK               : constant Interfaces.C.int := 0;
   Error_Invalid_Argument : constant Interfaces.C.int := 1;
   Error_IO               : constant Interfaces.C.int := 2;
   Error_Too_Large        : constant Interfaces.C.int := 3;
   Error_Internal         : constant Interfaces.C.int := 4;

   Chunk_Length : constant Positive :=
     Attest.SHA256.Block_Bytes * Attest.SHA256.Block_Bytes;

   function Get_Byte
     (Base   : System.Address;
      Offset : System.Storage_Elements.Storage_Offset)
      return Interfaces.Unsigned_8
   is
      use System.Storage_Elements;
   begin
      return Byte_Pointers.To_Pointer (Base + Offset).all;
   end Get_Byte;

   procedure Put_Byte
     (Base   : System.Address;
      Offset : System.Storage_Elements.Storage_Offset;
      Value  : Interfaces.Unsigned_8)
   is
      use System.Storage_Elements;
   begin
      Byte_Pointers.To_Pointer (Base + Offset).all := Value;
   end Put_Byte;

   function Read_Hash (Base : System.Address) return Hash is
      Result : Hash;
   begin
      for I in Result'Range loop
         Result (I) :=
           Get_Byte
             (Base,
              System.Storage_Elements.Storage_Offset (I - Result'First));
      end loop;
      return Result;
   end Read_Hash;

   procedure Write_Hash (Base : System.Address; Value : Hash) is
   begin
      for I in Value'Range loop
         Put_Byte
           (Base,
            System.Storage_Elements.Storage_Offset (I - Value'First),
            Value (I));
      end loop;
   end Write_Hash;

   function Hash_File
     (Path       : System.Address;
      Path_Len   : Interfaces.C.size_t;
      Out_Digest : System.Address) return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package SIO renames Ada.Streams.Stream_IO;
      File       : SIO.File_Type;
      Raw        : Ada.Streams.Stream_Element_Array
        (1 .. Ada.Streams.Stream_Element_Offset (Chunk_Length));
      Last       : Ada.Streams.Stream_Element_Offset;
      Buffer     : Attest.Byte_Array (0 .. Chunk_Length - 1);
      C          : Attest.SHA256.Context := Attest.SHA256.Initial;
   begin
      if Path = System.Null_Address
        or else Out_Digest = System.Null_Address
        or else Path_Len = 0
        or else Path_Len > Interfaces.C.size_t (Natural'Last)
      then
         return Error_Invalid_Argument;
      end if;

      declare
         Native_Path : String (1 .. Natural (Path_Len));
      begin
         for I in Native_Path'Range loop
            declare
               B : constant Interfaces.Unsigned_8 :=
                 Get_Byte
                   (Path,
                    System.Storage_Elements.Storage_Offset
                      (I - Native_Path'First));
            begin
               if B = 0 then
                  return Error_Invalid_Argument;
               end if;
               Native_Path (I) := Character'Val (Integer (B));
            end;
         end loop;

         SIO.Open (File, SIO.In_File, Native_Path);
      end;

      while not SIO.End_Of_File (File) loop
         SIO.Read (File, Raw, Last);
         declare
            Count : constant Natural :=
              Natural (Last - Raw'First + 1);
         begin
            if Attest.SHA256.Absorbed (C) >
              Attest.SHA256.Max_Message_Bytes -
                Interfaces.Unsigned_64 (Count)
            then
               SIO.Close (File);
               return Error_Too_Large;
            end if;

            for I in 0 .. Count - 1 loop
               Buffer (I) :=
                 Attest.Byte
                   (Raw (Raw'First + Ada.Streams.Stream_Element_Offset (I)));
            end loop;
            Attest.SHA256.Update (C, Buffer (0 .. Count - 1));
         end;
      end loop;

      SIO.Close (File);
      Write_Hash (Out_Digest, Attest.SHA256.Final (C));
      return Error_OK;
   exception
      when others =>
         if SIO.Is_Open (File) then
            SIO.Close (File);
         end if;
         return Error_IO;
      end;
   exception
      when others => return Error_IO;
   end Hash_File;

   function Hash_Bytes
     (Data       : System.Address;
      Data_Len   : Interfaces.C.size_t;
      Out_Digest : System.Address) return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      Buffer : Attest.Byte_Array (0 .. Chunk_Length - 1);
      C      : Attest.SHA256.Context := Attest.SHA256.Initial;
      Offset : Interfaces.C.size_t := 0;
   begin
      if Out_Digest = System.Null_Address
        or else (Data_Len > 0 and then Data = System.Null_Address)
      then
         return Error_Invalid_Argument;
      elsif Data_Len >
        Interfaces.C.size_t (Attest.SHA256.Max_Message_Bytes)
      then
         return Error_Too_Large;
      end if;

      while Offset < Data_Len loop
         declare
            Remaining : constant Interfaces.C.size_t := Data_Len - Offset;
            Count     : constant Natural :=
              (if Remaining > Interfaces.C.size_t (Buffer'Length)
               then Buffer'Length
               else Natural (Remaining));
         begin
            for I in 0 .. Count - 1 loop
               Buffer (I) :=
                 Get_Byte
                   (Data,
                    System.Storage_Elements.Storage_Offset
                      (Offset + Interfaces.C.size_t (I)));
            end loop;
            Attest.SHA256.Update (C, Buffer (0 .. Count - 1));
            Offset := Offset + Interfaces.C.size_t (Count);
         end;
      end loop;

      Write_Hash (Out_Digest, Attest.SHA256.Final (C));
      return Error_OK;
   exception
      when others =>
         return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end Hash_Bytes;

   function World_ID
     (Parent_ID        : System.Address;
      Filesystem_Root  : System.Address;
      Config_Root      : System.Address;
      Repository_Root  : System.Address;
      Environment_Root : System.Address;
      Evidence_Root    : System.Address;
      Out_Digest       : System.Address) return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if Parent_ID = System.Null_Address
        or else Filesystem_Root = System.Null_Address
        or else Config_Root = System.Null_Address
        or else Repository_Root = System.Null_Address
        or else Environment_Root = System.Null_Address
        or else Evidence_Root = System.Null_Address
        or else Out_Digest = System.Null_Address
      then
         return Error_Invalid_Argument;
      end if;

      Write_Hash
        (Out_Digest,
         Worldline.World.Identity
           (Read_Hash (Parent_ID),
            Read_Hash (Filesystem_Root),
            Read_Hash (Config_Root),
            Read_Hash (Repository_Root),
            Read_Hash (Environment_Root),
            Read_Hash (Evidence_Root)));
      return Error_OK;
   exception
      when others =>
         return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end World_ID;

   function Causal_Link
     (Previous   : System.Address;
      Event_Root : System.Address;
      Out_Digest : System.Address) return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if Previous = System.Null_Address
        or else Event_Root = System.Null_Address
        or else Out_Digest = System.Null_Address
      then
         return Error_Invalid_Argument;
      end if;
      Write_Hash
        (Out_Digest,
         Worldline.Causal_Graph.Link
           (Read_Hash (Previous), Read_Hash (Event_Root)));
      return Error_OK;
   exception
      when others =>
         return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end Causal_Link;

   function Receipt_Link
     (Previous     : System.Address;
      Receipt_Root : System.Address;
      Out_Digest   : System.Address) return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if Previous = System.Null_Address
        or else Receipt_Root = System.Null_Address
        or else Out_Digest = System.Null_Address
      then
         return Error_Invalid_Argument;
      end if;
      Write_Hash
        (Out_Digest,
         Worldline.Receipts.Link
           (Read_Hash (Previous), Read_Hash (Receipt_Root)));
      return Error_OK;
   exception
      when others =>
         return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end Receipt_Link;

   function Transition_Allowed
     (From_State : Interfaces.Unsigned_8;
      To_State   : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      Last : constant Interfaces.Unsigned_8 :=
        Interfaces.Unsigned_8
          (Transitions.World_State'Pos (Transitions.World_State'Last));
   begin
      if From_State > Last or else To_State > Last then
         return 0;
      elsif Transitions.Allowed
        (Transitions.World_State'Val (Integer (From_State)),
         Transitions.World_State'Val (Integer (To_State)))
      then
         return 1;
      else
         return 0;
      end if;
      end;
   exception
      when others => return 0;
   end Transition_Allowed;

   function Transaction_Transition_Allowed
     (From_State : Interfaces.Unsigned_8;
      To_State   : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      Last : constant Interfaces.Unsigned_8 :=
        Interfaces.Unsigned_8
          (Transitions.Transaction_State'Pos
             (Transitions.Transaction_State'Last));
   begin
      if From_State > Last or else To_State > Last then
         return 0;
      elsif Transitions.Transaction_Allowed
        (Transitions.Transaction_State'Val (Integer (From_State)),
         Transitions.Transaction_State'Val (Integer (To_State)))
      then
         return 1;
      else
         return 0;
      end if;
      end;
   exception
      when others => return 0;
   end Transaction_Transition_Allowed;

   function Collapse_Decide
     (Request : C_Collapse_Request_Access) return Interfaces.Unsigned_8
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if Request = null then
         return Collapse_Wire.Invalid_Request;
      end if;
      return Collapse_Wire.Decide_Wire (Request.all);
   exception
      when others =>
         return Collapse_Wire.Invalid_Request;
      end;
   exception
      when others => return 255;
   end Collapse_Decide;

   function Evaluation_Classify
     (Facts : C_Evaluation_Observations_Access;
      Result : C_Evaluation_Classification_Access)
      return Interfaces.Unsigned_8
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if Facts = null or else Result = null
        or else Facts.Source > Evaluation.Origin'Pos (Evaluation.Origin'Last)
        or else Facts.Status > Evaluation.Raw_Status'Pos (Evaluation.Raw_Status'Last)
        or else Facts.Channel > Evaluation.Channel_State'Pos (Evaluation.Channel_State'Last)
        or else Facts.Stage > Evaluation.Rejection_Stage'Pos (Evaluation.Rejection_Stage'Last)
        or else Facts.Supervisor > Evaluation.Supervision_State'Pos (Evaluation.Supervision_State'Last)
        or else Facts.Exit_Present > 1
        or else Facts.Exit_Integer > 1
        or else Facts.Supervisor_Stopped > 1
        or else Facts.Bundle_Present > 1
        or else Facts.Bundle_Is_Mapping > 1
        or else Facts.Bundle_Stable > 1
        or else Facts.Bundle_Changed > 1
        or else Facts.Unsatisfied_Imports > 1
        or else Facts.Exit_Integer > Facts.Exit_Present
        or else Facts.Bundle_Stable > Facts.Bundle_Present
        or else Facts.Bundle_Changed > Facts.Bundle_Present
        or else Facts.Bundle_Stable > Facts.Bundle_Is_Mapping
        or else Facts.Bundle_Changed > Facts.Bundle_Is_Mapping
      then
         return 255;
      end if;

      declare
         Value : constant Evaluation.Classification := Evaluation.Classify
           ((Source => Evaluation.Origin'Val (Integer (Facts.Source)),
             Status => Evaluation.Raw_Status'Val (Integer (Facts.Status)),
             Channel => Evaluation.Channel_State'Val (Integer (Facts.Channel)),
             Stage => Evaluation.Rejection_Stage'Val (Integer (Facts.Stage)),
             Exit_Present => Facts.Exit_Present = 1,
             Exit_Integer => Facts.Exit_Integer = 1,
             Supervisor => Evaluation.Supervision_State'Val
               (Integer (Facts.Supervisor)),
             Supervisor_Stopped => Facts.Supervisor_Stopped = 1,
             Bundle_Present => Facts.Bundle_Present = 1,
             Bundle_Is_Mapping => Facts.Bundle_Is_Mapping = 1,
             Bundle_Stable => Facts.Bundle_Stable = 1,
             Bundle_Changed => Facts.Bundle_Changed = 1,
             Unsatisfied_Imports => Facts.Unsatisfied_Imports = 1));
      begin
         Result.Execution := Interfaces.Unsigned_8
           (Evaluation.Execution_State'Pos (Value.Execution));
         Result.Outcome := Interfaces.Unsigned_8
           (Evaluation.Outcome'Pos (Value.Result));
         Result.Bundle := Interfaces.Unsigned_8
           (Evaluation.Bundle_Integrity'Pos (Value.Bundle));
         return 0;
      end;
   exception
      when others =>
         return 255;
      end;
   exception
      when others => return 255;
   end Evaluation_Classify;

   function Evaluation_Admissible
     (Value    : C_Evaluation_Classification_Read_Access;
      Report   : Interfaces.Unsigned_8;
      Presence : C_Evidence_Presence_Access)
      return Interfaces.Unsigned_8
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      Completed_Code : constant Interfaces.Unsigned_8 :=
        Evaluation.Execution_State'Pos (Evaluation.Completed);
      No_Outcome_Code : constant Interfaces.Unsigned_8 :=
        Evaluation.Outcome'Pos (Evaluation.No_Outcome);
   begin
      if Value = null or else Presence = null
        or else Value.Execution >
          Evaluation.Execution_State'Pos (Evaluation.Execution_State'Last)
        or else Value.Outcome > Evaluation.Outcome'Pos (Evaluation.Outcome'Last)
        or else Value.Bundle >
          Evaluation.Bundle_Integrity'Pos (Evaluation.Bundle_Integrity'Last)
        or else Report >
          Evaluation.Report_Integrity'Pos (Evaluation.Report_Integrity'Last)
        or else (Value.Execution = Completed_Code) =
                (Value.Outcome = No_Outcome_Code)
        --  Classify never produces an in-flight state.
        or else Value.Execution in
          Evaluation.Execution_State'Pos (Evaluation.Prepared) ..
          Evaluation.Execution_State'Pos (Evaluation.Started)
        or else Presence.Record_Identified > 1
        or else Presence.Verdict_Recorded > 1
        or else Presence.Binding_Established > 1
        or else Presence.Declaration_Matches > 1
        or else Presence.Bundle_Identified > 1
      then
         return 255;
      end if;

      return
        (if Evaluation.Admissible
          ((Execution => Evaluation.Execution_State'Val
              (Integer (Value.Execution)),
            Result => Evaluation.Outcome'Val (Integer (Value.Outcome)),
            Bundle => Evaluation.Bundle_Integrity'Val
              (Integer (Value.Bundle))),
           Evaluation.Report_Integrity'Val (Integer (Report)),
           (Record_Identified   => Presence.Record_Identified = 1,
            Verdict_Recorded    => Presence.Verdict_Recorded = 1,
            Binding_Established => Presence.Binding_Established = 1,
            Declaration_Matches => Presence.Declaration_Matches = 1,
            Bundle_Identified   => Presence.Bundle_Identified = 1))
         then 1 else 0);
   exception
      when others =>
         return 255;
      end;
   exception
      when others => return 255;
   end Evaluation_Admissible;

   Last_Execution_Code : constant Interfaces.Unsigned_8 :=
     Evaluation.Execution_State'Pos (Evaluation.Execution_State'Last);

   function Evaluation_Transition_Allowed
     (From_State : Interfaces.Unsigned_8;
      To_State   : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if From_State > Last_Execution_Code or else To_State > Last_Execution_Code then
         return 255;
      end if;
      return
        (if Evaluation.Transition_Allowed
           (Evaluation.Execution_State'Val (Integer (From_State)),
            Evaluation.Execution_State'Val (Integer (To_State)))
         then 1 else 0);
   exception
      when others =>
         return 255;
      end;
   exception
      when others => return 255;
   end Evaluation_Transition_Allowed;

   function Evaluation_Advance
     (State     : C_State_Access;
      Requested : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if State = null
        or else State.all > Last_Execution_Code
        or else Requested > Last_Execution_Code
      then
         return 255;
      end if;
      declare
         Current : Evaluation.Execution_State :=
           Evaluation.Execution_State'Val (Integer (State.all));
      begin
         Evaluation.Advance
           (Current, Evaluation.Execution_State'Val (Integer (Requested)));
         State.all := Interfaces.Unsigned_8
           (Evaluation.Execution_State'Pos (Current));
      end;
      return 0;
   exception
      when others =>
         return 255;
      end;
   exception
      when others => return 255;
   end Evaluation_Advance;

   function Evaluation_Roster_Complete
     (Admitted       : System.Address;
      Count          : Interfaces.C.size_t;
      Empty_Declared : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      use System.Storage_Elements;
   begin
      if Empty_Declared > 1
        or else Count > Interfaces.C.size_t (Evaluation.Roster_Index'Last)
        or else (Count > 0 and then Admitted = System.Null_Address)
      then
         return 255;
      end if;
      declare
         Length : constant Natural := Natural (Count);
         Values : Evaluation.Admissions (1 .. Length);
      begin
         for I in Values'Range loop
            declare
               Byte : constant Interfaces.Unsigned_8 :=
                 Get_Byte (Admitted, Storage_Offset (I - 1));
            begin
               if Byte > 1 then
                  return 255;
               end if;
               Values (I) := Byte = 1;
            end;
         end loop;
         return
           (if Evaluation.Roster_Complete (Values, Empty_Declared = 1)
            then 1 else 0);
      end;
   exception
      when others =>
         return 255;
      end;
   exception
      when others => return 255;
   end Evaluation_Roster_Complete;

   function ABI_Generation return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return ABI_Version;
      end;
   exception
      when others => return 0;
   end ABI_Generation;

   function Layout_Size
     (Selector : Interfaces.Unsigned_8) return Interfaces.C.size_t
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      case Selector is
         when 0 => return C_Collapse_Request'Size / 8;
         when 1 => return C_Evaluation_Observations'Size / 8;
         when 2 => return C_Evaluation_Classification'Size / 8;
         when 3 => return C_Evidence_Presence'Size / 8;
         when 4 => return Collapse_Wire.Raw_Optional_Hash'Size / 8;
         when 5 => return Collapse_Wire.Raw_Optional_Counter'Size / 8;
         when others => return 0;
      end case;
      end;
   exception
      when others => return Interfaces.C.size_t'Last;
   end Layout_Size;

   function Layout_Offset
     (Selector : Interfaces.Unsigned_8;
      Name     : System.Address;
      Name_Len : Interfaces.C.size_t) return Interfaces.C.size_t
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      use System.Storage_Elements;
      Unknown : constant Interfaces.C.size_t := Interfaces.C.size_t'Last;
      Collapse_Probe    : Collapse_Wire.Raw_Request;
      Observation_Probe : C_Evaluation_Observations;
      Class_Probe       : C_Evaluation_Classification;
      Presence_Probe    : C_Evidence_Presence;
      Hash_Probe        : Collapse_Wire.Raw_Optional_Hash;
      Counter_Probe     : Collapse_Wire.Raw_Optional_Counter;
      --  Only the components' 'Position is read; no value is.
      pragma Warnings (Off, Collapse_Probe);
      pragma Warnings (Off, Observation_Probe);
      pragma Warnings (Off, Class_Probe);
      pragma Warnings (Off, Presence_Probe);
      pragma Warnings (Off, Hash_Probe);
      pragma Warnings (Off, Counter_Probe);
   begin
      if Name = System.Null_Address or else Name_Len = 0 or else Name_Len > 64 then
         return Unknown;
      end if;
      declare
         Text : String (1 .. Natural (Name_Len));
      begin
         for I in Text'Range loop
            Text (I) := Character'Val (Integer (Get_Byte (Name, Storage_Offset (I - 1))));
         end loop;
         case Selector is
            when 0 =>
               if Text = "candidate_state" then return Interfaces.C.size_t (Collapse_Probe.Candidate_State'Position);
               elsif Text = "phase" then return Interfaces.C.size_t (Collapse_Probe.Phase'Position);
               elsif Text = "evaluation_mode" then return Interfaces.C.size_t (Collapse_Probe.Evaluation_Mode'Position);
               elsif Text = "conflicts" then return Interfaces.C.size_t (Collapse_Probe.Conflicts'Position);
               elsif Text = "foreign_writes" then return Interfaces.C.size_t (Collapse_Probe.Foreign_Writes'Position);
               elsif Text = "roster_complete" then return Interfaces.C.size_t (Collapse_Probe.Roster_Complete'Position);
               elsif Text = "staged_roster_complete" then return Interfaces.C.size_t (Collapse_Probe.Staged_Roster_Complete'Position);
               elsif Text = "expected_parent" then return Interfaces.C.size_t (Collapse_Probe.Expected_Parent'Position);
               elsif Text = "candidate_parent" then return Interfaces.C.size_t (Collapse_Probe.Candidate_Parent'Position);
               elsif Text = "expected_subject" then return Interfaces.C.size_t (Collapse_Probe.Expected_Subject'Position);
               elsif Text = "evidence_subject" then return Interfaces.C.size_t (Collapse_Probe.Evidence_Subject'Position);
               elsif Text = "expected_base" then return Interfaces.C.size_t (Collapse_Probe.Expected_Base'Position);
               elsif Text = "candidate_base" then return Interfaces.C.size_t (Collapse_Probe.Candidate_Base'Position);
               elsif Text = "expected_delta" then return Interfaces.C.size_t (Collapse_Probe.Expected_Delta'Position);
               elsif Text = "candidate_delta" then return Interfaces.C.size_t (Collapse_Probe.Candidate_Delta'Position);
               elsif Text = "expected_root_set" then return Interfaces.C.size_t (Collapse_Probe.Expected_Root_Set'Position);
               elsif Text = "candidate_root_set" then return Interfaces.C.size_t (Collapse_Probe.Candidate_Root_Set'Position);
               elsif Text = "expected_staged_root" then return Interfaces.C.size_t (Collapse_Probe.Expected_Staged_Root'Position);
               elsif Text = "actual_staged_root" then return Interfaces.C.size_t (Collapse_Probe.Actual_Staged_Root'Position);
               elsif Text = "staged_content_root" then return Interfaces.C.size_t (Collapse_Probe.Staged_Content_Root'Position);
               elsif Text = "tested_root" then return Interfaces.C.size_t (Collapse_Probe.Tested_Root'Position);
               elsif Text = "current_requirement" then return Interfaces.C.size_t (Collapse_Probe.Current_Requirement'Position);
               elsif Text = "resulting_requirement" then return Interfaces.C.size_t (Collapse_Probe.Resulting_Requirement'Position);
               elsif Text = "evaluated_requirement" then return Interfaces.C.size_t (Collapse_Probe.Evaluated_Requirement'Position);
               elsif Text = "declared_verifiers" then return Interfaces.C.size_t (Collapse_Probe.Declared_Verifiers'Position);
               elsif Text = "executed_verifiers" then return Interfaces.C.size_t (Collapse_Probe.Executed_Verifiers'Position);
               elsif Text = "staged_evaluated_requirement" then return Interfaces.C.size_t (Collapse_Probe.Staged_Evaluated_Requirement'Position);
               elsif Text = "staged_executed_verifiers" then return Interfaces.C.size_t (Collapse_Probe.Staged_Executed_Verifiers'Position);
               elsif Text = "staged_examined_root" then return Interfaces.C.size_t (Collapse_Probe.Staged_Examined_Root'Position);
               elsif Text = "expected_checkpoint" then return Interfaces.C.size_t (Collapse_Probe.Expected_Checkpoint'Position);
               elsif Text = "witnessed_checkpoint" then return Interfaces.C.size_t (Collapse_Probe.Witnessed_Checkpoint'Position);
               elsif Text = "registered_watch_set" then return Interfaces.C.size_t (Collapse_Probe.Registered_Watch_Set'Position);
               elsif Text = "watched_set" then return Interfaces.C.size_t (Collapse_Probe.Watched_Set'Position);
               elsif Text = "generation_before" then return Interfaces.C.size_t (Collapse_Probe.Generation_Before'Position);
               elsif Text = "generation_after" then return Interfaces.C.size_t (Collapse_Probe.Generation_After'Position);
               end if;
            when 1 =>
               if Text = "source" then return Interfaces.C.size_t (Observation_Probe.Source'Position);
               elsif Text = "status" then return Interfaces.C.size_t (Observation_Probe.Status'Position);
               elsif Text = "channel" then return Interfaces.C.size_t (Observation_Probe.Channel'Position);
               elsif Text = "stage" then return Interfaces.C.size_t (Observation_Probe.Stage'Position);
               elsif Text = "exit_present" then return Interfaces.C.size_t (Observation_Probe.Exit_Present'Position);
               elsif Text = "exit_integer" then return Interfaces.C.size_t (Observation_Probe.Exit_Integer'Position);
               elsif Text = "supervisor" then return Interfaces.C.size_t (Observation_Probe.Supervisor'Position);
               elsif Text = "supervisor_stopped" then return Interfaces.C.size_t (Observation_Probe.Supervisor_Stopped'Position);
               elsif Text = "bundle_present" then return Interfaces.C.size_t (Observation_Probe.Bundle_Present'Position);
               elsif Text = "bundle_is_mapping" then return Interfaces.C.size_t (Observation_Probe.Bundle_Is_Mapping'Position);
               elsif Text = "bundle_stable" then return Interfaces.C.size_t (Observation_Probe.Bundle_Stable'Position);
               elsif Text = "bundle_changed" then return Interfaces.C.size_t (Observation_Probe.Bundle_Changed'Position);
               elsif Text = "unsatisfied_imports" then return Interfaces.C.size_t (Observation_Probe.Unsatisfied_Imports'Position);
               end if;
            when 2 =>
               if Text = "execution" then return Interfaces.C.size_t (Class_Probe.Execution'Position);
               elsif Text = "outcome" then return Interfaces.C.size_t (Class_Probe.Outcome'Position);
               elsif Text = "bundle" then return Interfaces.C.size_t (Class_Probe.Bundle'Position);
               end if;
            when 3 =>
               if Text = "record_identified" then return Interfaces.C.size_t (Presence_Probe.Record_Identified'Position);
               elsif Text = "verdict_recorded" then return Interfaces.C.size_t (Presence_Probe.Verdict_Recorded'Position);
               elsif Text = "binding_established" then return Interfaces.C.size_t (Presence_Probe.Binding_Established'Position);
               elsif Text = "declaration_matches" then return Interfaces.C.size_t (Presence_Probe.Declaration_Matches'Position);
               elsif Text = "bundle_identified" then return Interfaces.C.size_t (Presence_Probe.Bundle_Identified'Position);
               end if;
            when 4 =>
               if Text = "present" then return Interfaces.C.size_t (Hash_Probe.Present'Position);
               elsif Text = "value" then return Interfaces.C.size_t (Hash_Probe.Value'Position);
               end if;
            when 5 =>
               if Text = "present" then return Interfaces.C.size_t (Counter_Probe.Present'Position);
               elsif Text = "value_le" then return Interfaces.C.size_t (Counter_Probe.Value_LE'Position);
               end if;
            when others => null;
         end case;
      end;
      return Unknown;
      end;
   exception
      when others => return Interfaces.C.size_t'Last;
   end Layout_Offset;



   package Completion_K renames Evaluation_Completion_C;
   package Completion_P renames Evaluation_Pending;
   use type Completion_K.I64;
   use type Interfaces.C.int;
   use type System.Storage_Elements.Integer_Address;
   type Completion_Request_Bounds is limited record
      Data, Journal, Captured, Retained, History, Required : aliased Foreign_Array_Bounds;
   end record;
   type Completion_Raw_Bounds is limited record
      Rows, Confinements : aliased Foreign_Array_Bounds;
   end record;
   type Completion_Context_Bounds is limited record
      Data, Rows, Required : aliased Foreign_Array_Bounds;
   end record;
   type Completion_Metadata_Bounds is limited record
      Data, Rows : aliased Foreign_Array_Bounds;
   end record;
   procedure Completion_Flush_Diagnostics is
   begin
      Flush_Native_Diagnostic_Trace;
   exception
      when others => Completion_K.Diagnostic_Capture_Failed;
   end Completion_Flush_Diagnostics;
   function Completion_Bytes_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Bytes_Observer;
   function Completion_Journal_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Journal_Row_Observer;
   function Completion_Check_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Check_Row_Observer;
   function Completion_History_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.History_Row_Observer;
   function Completion_Required_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Required_Row_Observer;
   function Completion_Raw_Rows_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Raw_Row_Observer;
   function Completion_Context_Rows_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Context_Row_Observer;
   function Completion_Metadata_Rows_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Row_Metadata_Observer;
   function Completion_Request_View
     (Address : System.Address; Bounds : aliased in out Completion_Request_Bounds;
      Full : Boolean := True; Plans : Boolean := True)
      return Completion_K.Request_View;
   function Completion_Raw_View
     (Rows, Confinements : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Completion_Raw_Bounds)
      return Completion_K.Raw_View;
   function Completion_Context_View
     (Address : System.Address; Bounds : aliased in out Completion_Context_Bounds)
      return Completion_K.Context_View;
   function Completion_Metadata_View
     (Address : System.Address; Bounds : aliased in out Completion_Metadata_Bounds;
      Contents : Boolean := True)
      return Completion_K.Metadata_View;
   function Completion_Metadata_Base (Address : System.Address) return System.Address;
   function Completion_Evidence_View (Collapse, Agent : System.Address)
      return Completion_K.Evidence_View;

   function Completion_Bytes_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Bytes_Observer is
      function Observe is new Observe_Foreign_Array
        (Completion_P.Index, Completion_P.Byte, Completion_P.Bytes, Completion_K.Bytes_Observer);
   begin
      if not Completion_K.Array_Extent
        (Address, Count, Completion_P.Byte'Object_Size / System.Storage_Unit, Completion_P.Byte'Alignment)
      then raise Constraint_Error; end if;
      if Count = 0 then return null; end if;
      Bounds.Last := Count;
      return Observe (Address, Bounds);
   end Completion_Bytes_View;
   function Completion_Journal_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Journal_Row_Observer is
      function Observe is new Observe_Foreign_Array
        (Completion_K.I64, Completion_K.Journal_Row, Completion_K.Journal_Row_Array, Completion_K.Journal_Row_Observer);
   begin
      if not Completion_K.Array_Extent
        (Address, Count, Completion_K.Journal_Row'Object_Size / System.Storage_Unit, Completion_K.Journal_Row'Alignment)
      then raise Constraint_Error; end if;
      if Count = 0 then return null; end if;
      Bounds.Last := Count;
      return Observe (Address, Bounds);
   end Completion_Journal_View;
   function Completion_Check_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Check_Row_Observer is
      function Observe is new Observe_Foreign_Array
        (Completion_K.I64, Completion_K.Check_Row, Completion_K.Check_Buffer_Array, Completion_K.Check_Row_Observer);
   begin
      if not Completion_K.Array_Extent
        (Address, Count, Completion_K.Check_Row'Object_Size / System.Storage_Unit, Completion_K.Check_Row'Alignment)
      then raise Constraint_Error; end if;
      if Count = 0 then return null; end if;
      Bounds.Last := Count;
      return Observe (Address, Bounds);
   end Completion_Check_View;
   function Completion_History_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.History_Row_Observer is
      function Observe is new Observe_Foreign_Array
        (Completion_K.I64, Completion_K.History_Row, Completion_K.History_Row_Array, Completion_K.History_Row_Observer);
   begin
      if not Completion_K.Array_Extent
        (Address, Count, Completion_K.History_Row'Object_Size / System.Storage_Unit, Completion_K.History_Row'Alignment)
      then raise Constraint_Error; end if;
      if Count = 0 then return null; end if;
      Bounds.Last := Count;
      return Observe (Address, Bounds);
   end Completion_History_View;
   function Completion_Required_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Required_Row_Observer is
      function Observe is new Observe_Foreign_Array
        (Completion_K.I64, Completion_K.Required_Row, Completion_K.Required_Buffer_Array, Completion_K.Required_Row_Observer);
   begin
      if not Completion_K.Array_Extent
        (Address, Count, Completion_K.Required_Row'Object_Size / System.Storage_Unit, Completion_K.Required_Row'Alignment)
      then raise Constraint_Error; end if;
      if Count = 0 then return null; end if;
      Bounds.Last := Count;
      return Observe (Address, Bounds);
   end Completion_Required_View;
   function Completion_Raw_Rows_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Raw_Row_Observer is
      function Observe is new Observe_Foreign_Array
        (Completion_K.I64, Worldline.Evaluation_Wire.Raw_Record, Completion_K.Raw_Row_Array, Completion_K.Raw_Row_Observer);
   begin
      if not Completion_K.Array_Extent
        (Address, Count, Worldline.Evaluation_Wire.Raw_Record'Object_Size / System.Storage_Unit, Worldline.Evaluation_Wire.Raw_Record'Alignment)
      then raise Constraint_Error; end if;
      if Count = 0 then return null; end if;
      Bounds.Last := Count;
      return Observe (Address, Bounds);
   end Completion_Raw_Rows_View;
   function Completion_Context_Rows_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Context_Row_Observer is
      function Observe is new Observe_Foreign_Array
        (Completion_K.I64, Completion_K.Context_Row, Completion_K.Context_Row_Array, Completion_K.Context_Row_Observer);
   begin
      if not Completion_K.Array_Extent
        (Address, Count, Completion_K.Context_Row'Object_Size / System.Storage_Unit, Completion_K.Context_Row'Alignment)
      then raise Constraint_Error; end if;
      if Count = 0 then return null; end if;
      Bounds.Last := Count;
      return Observe (Address, Bounds);
   end Completion_Context_Rows_View;
   function Completion_Metadata_Rows_View
     (Address : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Completion_K.Row_Metadata_Observer is
      function Observe is new Observe_Foreign_Array
        (Completion_K.I64, Completion_K.Row_Metadata, Completion_K.Row_Metadata_Array, Completion_K.Row_Metadata_Observer);
   begin
      if not Completion_K.Array_Extent
        (Address, Count, Completion_K.Row_Metadata'Object_Size / System.Storage_Unit, Completion_K.Row_Metadata'Alignment)
      then raise Constraint_Error; end if;
      if Count = 0 then return null; end if;
      Bounds.Last := Count;
      return Observe (Address, Bounds);
   end Completion_Metadata_Rows_View;
   function Completion_Request_View
     (Address : System.Address; Bounds : aliased in out Completion_Request_Bounds;
      Full : Boolean := True; Plans : Boolean := True)
      return Completion_K.Request_View is
      package Pointers is new System.Address_To_Access_Conversions (Completion_K.Request);
   begin
      if not Completion_K.Extent_Valid
        (Address, Completion_K.Request'Object_Size / System.Storage_Unit, Completion_K.Request'Alignment)
      then raise Constraint_Error; end if;
      declare
         R : constant Completion_K.Request := Pointers.To_Pointer (Address).all;
         V : Completion_K.Request_View := (Descriptor => R, Address => Address, others => <>);
      begin
         V.Data := Completion_Bytes_View (R.Data, R.Data_Length, Bounds.Data);
         V.Captured := Completion_Check_View (R.Captured_Results, R.Captured_Count, Bounds.Captured);
         if Full or else Plans then
            V.Required := Completion_Required_View (R.Required, R.Required_Count, Bounds.Required);
         end if;
         if Full then
            V.Journal := Completion_Journal_View (R.Journal, R.Journal_Count, Bounds.Journal);
            V.Retained := Completion_Check_View (R.Retained_Results, R.Retained_Count, Bounds.Retained);
            V.History := Completion_History_View (R.History, R.History_Count, Bounds.History);
         end if;
         return V;
      end;
   end Completion_Request_View;
   function Completion_Raw_View
     (Rows, Confinements : System.Address; Count : Completion_K.I64;
      Bounds : aliased in out Completion_Raw_Bounds)
      return Completion_K.Raw_View is
   begin
      return (Rows => Completion_Raw_Rows_View (Rows, Count, Bounds.Rows),
              Confinements => Completion_Bytes_View (Confinements, Count, Bounds.Confinements),
              Rows_Address => Rows, Confinements_Address => Confinements);
   end Completion_Raw_View;
   function Completion_Context_View
     (Address : System.Address; Bounds : aliased in out Completion_Context_Bounds)
      return Completion_K.Context_View is
      package Pointers is new System.Address_To_Access_Conversions (Completion_K.Context_Input);
   begin
      if not Completion_K.Extent_Valid
        (Address, Completion_K.Context_Input'Object_Size / System.Storage_Unit, Completion_K.Context_Input'Alignment)
      then raise Constraint_Error; end if;
      declare
         X : constant Completion_K.Context_Input := Pointers.To_Pointer (Address).all;
      begin
         return (Descriptor => X, Address => Address,
                 Data => Completion_Bytes_View (X.Data, X.Data_Length, Bounds.Data),
                 Rows => Completion_Context_Rows_View (X.Rows, X.Row_Count, Bounds.Rows),
                 Required => Completion_Required_View (X.Required, X.Required_Count, Bounds.Required));
      end;
   end Completion_Context_View;
   function Completion_Metadata_View
     (Address : System.Address; Bounds : aliased in out Completion_Metadata_Bounds;
      Contents : Boolean := True)
      return Completion_K.Metadata_View is
      package Pointers is new System.Address_To_Access_Conversions (Completion_K.Metadata_Context);
   begin
      if not Completion_K.Extent_Valid
        (Address, Completion_K.Metadata_Context'Object_Size / System.Storage_Unit, Completion_K.Metadata_Context'Alignment)
      then raise Constraint_Error; end if;
      declare
         X : constant Completion_K.Metadata_Context := Pointers.To_Pointer (Address).all;
         V : Completion_K.Metadata_View := (Descriptor => X, Address => Address, others => <>);
      begin
         if Contents then
            V.Data := Completion_Bytes_View (X.Data, X.Data_Length, Bounds.Data);
            V.Rows := Completion_Metadata_Rows_View (X.Rows, X.Row_Count, Bounds.Rows);
         end if;
         return V;
      end;
   end Completion_Metadata_View;
   function Completion_Metadata_Base (Address : System.Address) return System.Address is
      Bounds : aliased Completion_Metadata_Bounds;
   begin
      if not Completion_K.Extent_Valid
        (Address, Completion_K.Metadata_Context'Object_Size / System.Storage_Unit,
         Completion_K.Metadata_Context'Alignment)
      then return System.Null_Address; end if;
      return Completion_K.Metadata_Base
        (Completion_Metadata_View (Address, Bounds, Contents => False));
   exception
      when others => return System.Null_Address;
   end Completion_Metadata_Base;
   function Completion_Evidence_View (Collapse, Agent : System.Address)
      return Completion_K.Evidence_View is
      package Collapse_Pointers is new System.Address_To_Access_Conversions (Worldline.Collapse_Wire.Raw_Request);
      package Agent_Pointers is new System.Address_To_Access_Conversions (Worldline.Evaluation_Wire.Raw_Record);
   begin
      if not Completion_K.Extent_Valid
        (Collapse, Worldline.Collapse_Wire.Raw_Request'Object_Size / System.Storage_Unit,
         Worldline.Collapse_Wire.Raw_Request'Alignment)
        or else not Completion_K.Extent_Valid
        (Agent, Worldline.Evaluation_Wire.Raw_Record'Object_Size / System.Storage_Unit,
         Worldline.Evaluation_Wire.Raw_Record'Alignment)
      then raise Constraint_Error; end if;
      return (Collapse => Collapse_Pointers.To_Pointer (Collapse).all,
              Agent => Agent_Pointers.To_Pointer (Agent).all,
              Collapse_Address => Collapse, Agent_Address => Agent);
   end Completion_Evidence_View;
   function Completion_ABI_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Completion_K.ABI_Version;
      end;
   exception
      when others => return 0;
   end Completion_ABI_Version;
   function Completion_Layout_Size (Kind : Interfaces.Unsigned_32) return Interfaces.Integer_64 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Completion_K.Layout_Size (Kind);
      end;
   exception
      when others => return -1;
   end Completion_Layout_Size;
   function Completion_Layout_Alignment (Kind : Interfaces.Unsigned_32) return Interfaces.Integer_64 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Completion_K.Layout_Alignment (Kind);
      end;
   exception
      when others => return -1;
   end Completion_Layout_Alignment;
   function Completion_Layout_Offset (Kind, Field : Interfaces.Unsigned_32) return Interfaces.Integer_64 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Completion_K.Layout_Offset (Kind, Field);
      end;
   exception
      when others => return -1;
   end Completion_Layout_Offset;
   function Completion_Context_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.Integer_64 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Completion_K.Context_Layout (Kind, Field);
      end;
   exception
      when others => return -1;
   end Completion_Context_Layout;
   function Completion_Metadata_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.Integer_64 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Completion_K.Metadata_Layout (Kind, Field);
      end;
   exception
      when others => return -1;
   end Completion_Metadata_Layout;
   function Completion_Decide (Input, Output : System.Address) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package Outputs is new System.Address_To_Access_Conversions (Completion_K.Result);
      ISz : constant Completion_K.I64 := Completion_K.Request'Object_Size / System.Storage_Unit;
      OSz : constant Completion_K.I64 := Completion_K.Result'Object_Size / System.Storage_Unit;
      function Separated return Boolean is
        (if System.Storage_Elements.To_Integer (Input) <= System.Storage_Elements.To_Integer (Output)
         then System.Storage_Elements.Integer_Address (ISz) <=
           System.Storage_Elements.To_Integer (Output) - System.Storage_Elements.To_Integer (Input)
         else System.Storage_Elements.Integer_Address (OSz) <=
           System.Storage_Elements.To_Integer (Input) - System.Storage_Elements.To_Integer (Output));
   begin
      if not Completion_K.Extent_Valid (Input, ISz, Completion_K.Request'Alignment)
        or else not Completion_K.Extent_Valid (Output, OSz, Completion_K.Result'Alignment)
        or else not Separated
      then
         Completion_Flush_Diagnostics;
         return 255;
      end if;
      declare
         Bounds : aliased Completion_Request_Bounds;
         View : constant Completion_K.Request_View := Completion_Request_View (Input, Bounds);
         Observed : Completion_K.Result :=
           (Reason => 0, Selected => 0, Summary_Present => 0,
            Summary =>
              (Subject | Content | Requirement | Run | Sequence =>
                 (Present => 0, Value => (First => 1, Length => 0)),
               State | Outcome => 0),
            Execution_State => 0, Outcome => 0, Promotion => 0);
         Status : constant Interfaces.C.int := Completion_K.Decide (View, Output, Observed);
      begin
         if Status = 0 then Outputs.To_Pointer (Output).all := Observed; end if;
         Completion_Flush_Diagnostics;
         return Status;
      end;
   exception
      when others =>
         Completion_Flush_Diagnostics;
         return 255;
      end;
   exception
      when others => return 255;
   end Completion_Decide;
   function Completion_Raw_Decide (Input, Raw_Rows, Confinements, Output : System.Address) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package Outputs is new System.Address_To_Access_Conversions (Completion_K.Result);
      ISz : constant Completion_K.I64 := Completion_K.Request'Object_Size / System.Storage_Unit;
      OSz : constant Completion_K.I64 := Completion_K.Result'Object_Size / System.Storage_Unit;
      function Separated return Boolean is
        (if System.Storage_Elements.To_Integer (Input) <= System.Storage_Elements.To_Integer (Output)
         then System.Storage_Elements.Integer_Address (ISz) <=
           System.Storage_Elements.To_Integer (Output) - System.Storage_Elements.To_Integer (Input)
         else System.Storage_Elements.Integer_Address (OSz) <=
           System.Storage_Elements.To_Integer (Input) - System.Storage_Elements.To_Integer (Output));
   begin
      if not Completion_K.Extent_Valid (Input, ISz, Completion_K.Request'Alignment)
        or else not Completion_K.Extent_Valid (Output, OSz, Completion_K.Result'Alignment)
        or else not Separated
      then
         Completion_Flush_Diagnostics;
         return 255;
      end if;
      declare
         Bounds : aliased Completion_Request_Bounds;
         Raw_Bounds : aliased Completion_Raw_Bounds;
         View : constant Completion_K.Request_View := Completion_Request_View (Input, Bounds);
         Observed : Completion_K.Result :=
           (Reason => 0, Selected => 0, Summary_Present => 0,
            Summary =>
              (Subject | Content | Requirement | Run | Sequence =>
                 (Present => 0, Value => (First => 1, Length => 0)),
               State | Outcome => 0),
            Execution_State => 0, Outcome => 0, Promotion => 0);
         Status : constant Interfaces.C.int := Completion_K.Raw_Decide (View, Completion_Raw_View
           (Raw_Rows, Confinements, View.Descriptor.Captured_Count, Raw_Bounds), Output, Observed);
      begin
         if Status = 0 then Outputs.To_Pointer (Output).all := Observed; end if;
         Completion_Flush_Diagnostics;
         return Status;
      end;
   exception
      when others =>
         Completion_Flush_Diagnostics;
         return 255;
      end;
   exception
      when others => return 255;
   end Completion_Raw_Decide;
   function Completion_Metadata_Matches (Input, Context : System.Address) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      declare
         Request_Bounds : aliased Completion_Request_Bounds;
         Metadata_Bounds : aliased Completion_Metadata_Bounds;
         Status : constant Interfaces.C.int := Completion_K.Metadata_Matches
           (Completion_Request_View (Input, Request_Bounds, Full => False, Plans => False),
            Completion_Metadata_View (Context, Metadata_Bounds));
      begin
         Completion_Flush_Diagnostics;
         return Status;
      end;
   exception
      when others =>
         Completion_Flush_Diagnostics;
         return 255;
      end;
   exception
      when others => return 255;
   end Completion_Metadata_Matches;

   package Finalization_Native renames Evaluation_Finalization_C;
   procedure Finalization_Flush is
   begin
      Flush_Native_Diagnostic_Trace;
   exception
      when others => Evaluation_Completion_C.Diagnostic_Capture_Failed;
   end Finalization_Flush;
   function Finalization_Mixed_Return (Value : Interfaces.Unsigned_8)
      return Interfaces.Unsigned_8 is
   begin
      Finalization_Flush;
      return Value;
   end Finalization_Mixed_Return;
   package Finalization_Request_Pointers is new System.Address_To_Access_Conversions
     (Finalization_Native.Request);
   package Finalization_Result_Pointers is new System.Address_To_Access_Conversions
     (Finalization_Native.Result);
   type Finalization_Request_Bounds is limited record
      Data, Required, Rows : aliased Foreign_Array_Bounds;
   end record;
   function Finalization_Rows_View
     (Address : System.Address; Count : Interfaces.Integer_64;
      Bounds : aliased in out Foreign_Array_Bounds)
      return Finalization_Native.Row_Observer is
      package F renames Finalization_Native;
      use type F.I64;
      function Observe is new Observe_Foreign_Array
        (F.I64, F.Row, F.Row_Array, F.Row_Observer);
   begin
      if not F.Array_Extent (Address, Count, F.Row'Object_Size / System.Storage_Unit,
                             F.Row'Alignment) then raise Constraint_Error; end if;
      if Count = 0 then return null; end if;
      Bounds.Last := Count;
      return Observe (Address, Bounds);
   end Finalization_Rows_View;
   function Finalization_Request_View
     (Address : System.Address; Bounds : aliased in out Finalization_Request_Bounds;
      Output : System.Address := System.Null_Address;
      Have_Output : Boolean := False) return Finalization_Native.Request_View is
      package F renames Finalization_Native;
      use type F.U32;
      X : F.Request;
   begin
      if not F.Extent_Valid (Address, F.Request'Object_Size / System.Storage_Unit,
                            F.Request'Alignment)
        or else (Have_Output and then
          (not F.Extent_Valid (Output, F.Result'Object_Size / System.Storage_Unit,
                               F.Result'Alignment)
           or else not F.Disjoint (Address, F.Request'Object_Size / System.Storage_Unit,
                                   Output, F.Result'Object_Size / System.Storage_Unit)))
      then raise Constraint_Error; end if;
      X := Finalization_Request_Pointers.To_Pointer (Address).all;
      if not F.Transport_Valid (X, Address, Output, Have_Output)
      then raise Constraint_Error; end if;
      return (Descriptor => X, Address => Address,
        Data => Completion_Bytes_View (X.Data, X.Data_Length, Bounds.Data),
        Required => Completion_Required_View (X.Required, X.Required_Count, Bounds.Required),
        Rows => (if X.Operation >= 2 then Finalization_Rows_View (X.Rows, X.Row_Count, Bounds.Rows)
                 else null));
   end Finalization_Request_View;
   function Finalization_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Finalization_Native.Version;
      end;
   exception
      when others => return 0;
   end Finalization_Version;
   function Finalization_Layout (Kind, Field : Interfaces.Unsigned_32)
      return Interfaces.Integer_64 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Finalization_Native.Layout (Kind, Field);
      end;
   exception
      when others => return -1;
   end Finalization_Layout;
   function Finalization_Decide (Input, Output : System.Address) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      use type Interfaces.C.int;
      Bounds : aliased Finalization_Request_Bounds;
      View : constant Finalization_Native.Request_View :=
        Finalization_Request_View (Input, Bounds, Output, True);
      Observed : Finalization_Native.Result :=
        (Reason => 1, State => 0, Outcome => 0, Promotion => 0,
         Finalization_State => 0, Finalization_Outcome => 0, Identity => (others => 0));
      Status : Interfaces.C.int;
   begin
      Status := Finalization_Native.Decide (View, Output, Observed);
      if Status = 0 then Finalization_Result_Pointers.To_Pointer (Output).all := Observed; end if;
      Finalization_Flush;
      return Status;
   exception when others =>
      Finalization_Flush;
      return 255;
      end;
   exception
      when others => return 255;
   end Finalization_Decide;
   function Finalization_Decide_Mixed
     (Collapse : System.Address; Primary_Kind : Interfaces.Unsigned_32;
      Primary, Primary_Raw, Primary_Confinement, Primary_Context : System.Address;
      Staged_Kind : Interfaces.Unsigned_32;
      Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address;
      Agent_Confinement : Interfaces.Unsigned_8) return Interfaces.Unsigned_8 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package F renames Finalization_Native;
      package K renames Evaluation_Completion_C;
      package A renames Worldline.Evaluation_Authority;
      package CW renames Worldline.Collapse_Wire;
      package W renames Worldline.Evaluation_Wire;
      package CP is new System.Address_To_Access_Conversions (CW.Raw_Request);
      package AP is new System.Address_To_Access_Conversions (W.Raw_Record);
      use type F.U32;
      use type A.Raw_Dependency;
      P, S : F.Checkpoint_View;
      P_Ordinary, S_Ordinary : aliased K.Request_View;
      P_Final, S_Final : aliased F.Request_View;
      P_Meta, S_Meta : aliased K.Metadata_View;
      P_Context, S_Context : aliased K.Context_View;
      P_Request_Bounds, S_Request_Bounds : aliased Completion_Request_Bounds;
      P_Final_Bounds, S_Final_Bounds : aliased Finalization_Request_Bounds;
      P_Raw_Bounds, S_Raw_Bounds : aliased Completion_Raw_Bounds;
      P_Meta_Bounds, S_Meta_Bounds : aliased Completion_Metadata_Bounds;
      P_Context_Bounds, S_Context_Bounds : aliased Completion_Context_Bounds;
      Evidence : K.Evidence_View;
      Prepared : F.Mixed_State;
      Needed : A.Raw_Dependency;
      Preview : Interfaces.Unsigned_8;
      procedure Map_Checkpoint
        (Kind : F.U32; Address, Raw, Confined : System.Address;
         Ordinary : aliased in out K.Request_View;
         Finalized : aliased in out F.Request_View;
         Request_Bounds : aliased in out Completion_Request_Bounds;
         Final_Bounds : aliased in out Finalization_Request_Bounds;
         Raw_Bounds : aliased in out Completion_Raw_Bounds;
         Target : in out F.Checkpoint_View) is
      begin
         if Kind = 1 then
            Ordinary := Completion_Request_View (Address, Request_Bounds);
            Target.Ordinary := Ordinary'Unchecked_Access;
            Target.Raw := Completion_Raw_View (Raw, Confined, Ordinary.Descriptor.Captured_Count, Raw_Bounds);
         elsif Kind = 2 then
            Finalized := Finalization_Request_View (Address, Final_Bounds);
            Target.Finalized := Finalized'Unchecked_Access;
         end if;
      end Map_Checkpoint;
      procedure Map_Metadata
        (Address : System.Address; Need_Context, Contents : Boolean;
         Metadata : aliased in out K.Metadata_View;
         Context : aliased in out K.Context_View;
         Meta_Bounds : aliased in out Completion_Metadata_Bounds;
         Context_Bounds : aliased in out Completion_Context_Bounds;
         Target : in out F.Checkpoint_View) is
      begin
         Metadata := Completion_Metadata_View (Address, Meta_Bounds, Contents => Contents);
         Target.Metadata := Metadata'Unchecked_Access;
         if Need_Context then
            Context := Completion_Context_View (K.Metadata_Base (Metadata), Context_Bounds);
            Target.Context := Context'Unchecked_Access;
         end if;
      end Map_Metadata;
   begin
      if not F.Extent_Valid (Collapse, CW.Raw_Request'Object_Size / System.Storage_Unit,
                            CW.Raw_Request'Alignment) then
         return Finalization_Mixed_Return (CW.Invalid_Request);
      end if;
      Evidence := (Collapse => CP.To_Pointer (Collapse).all, Agent => W.Zero_Record,
                   Collapse_Address => Collapse, Agent_Address => System.Null_Address);
      Needed := A.Dependencies (Evidence.Collapse);
      if Needed = A.Invalid_Collapse then return Finalization_Mixed_Return (CW.Invalid_Request); end if;
      if A.Needs_Primary (Needed) then
         Map_Checkpoint (Primary_Kind, Primary, Primary_Raw, Primary_Confinement,
                         P_Ordinary, P_Final, P_Request_Bounds, P_Final_Bounds, P_Raw_Bounds, P);
      end if;
      Prepared := F.Prepare_Mixed (Evidence, Primary_Kind, P);
      if not Prepared.Valid then return Finalization_Mixed_Return (CW.Invalid_Request); end if;
      if A.Needs_Staged (Needed) then
         Map_Checkpoint (Staged_Kind, Staged, Staged_Raw, Staged_Confinement,
                         S_Ordinary, S_Final, S_Request_Bounds, S_Final_Bounds, S_Raw_Bounds, S);
      end if;
      Prepared := F.Prepare_Staged (Prepared, Staged_Kind, S);
      if not Prepared.Valid then return Finalization_Mixed_Return (CW.Invalid_Request); end if;
      if A.Needs_Agent (Needed) and then Agent /= System.Null_Address then
         if not F.Extent_Valid (Agent, W.Raw_Record'Object_Size / System.Storage_Unit,
                               W.Raw_Record'Alignment) then
            return Finalization_Mixed_Return (CW.Invalid_Request);
         end if;
         Evidence.Agent := AP.To_Pointer (Agent).all;
         Evidence.Agent_Address := Agent;
      end if;
      Prepared := F.Finish_Prepare_Agent (Prepared, Evidence, Agent_Confinement);
      if not Prepared.Valid then return Finalization_Mixed_Return (CW.Invalid_Request); end if;
      Preview := F.Preview_Mixed (Prepared);
      if A.Needs_Primary (Needed) and then
        ((Prepared.Agent_Ready = 1 and then Prepared.Primary_Ready = 1)
         or else (Primary_Kind = 1 and then Preview =
           Interfaces.Unsigned_8 (Worldline.Collapse.Decision'Pos (Worldline.Collapse.Authorized))))
      then
         Map_Metadata (Primary_Context,
           Prepared.Agent_Ready = 1 and then Prepared.Primary_Ready = 1,
           Primary_Kind = 2 or else Preview =
             Interfaces.Unsigned_8 (Worldline.Collapse.Decision'Pos (Worldline.Collapse.Authorized)),
           P_Meta, P_Context, P_Meta_Bounds, P_Context_Bounds, P);
      end if;
      if A.Needs_Staged (Needed) and then
        ((Prepared.Agent_Ready = 1 and then Prepared.Staged_Ready = 1)
         or else (Staged_Kind = 1 and then Preview =
           Interfaces.Unsigned_8 (Worldline.Collapse.Decision'Pos (Worldline.Collapse.Authorized))))
      then
         Map_Metadata (Staged_Context,
           Prepared.Agent_Ready = 1 and then Prepared.Staged_Ready = 1,
           Staged_Kind = 2 or else Preview =
             Interfaces.Unsigned_8 (Worldline.Collapse.Decision'Pos (Worldline.Collapse.Authorized)),
           S_Meta, S_Context, S_Meta_Bounds, S_Context_Bounds, S);
      end if;
      return Finalization_Mixed_Return
        (F.Decide_Mixed (Prepared, Evidence, Primary_Kind, P,
                         Staged_Kind, S, Agent_Confinement));
   exception when others =>
      return Finalization_Mixed_Return (Worldline.Collapse_Wire.Invalid_Request);
      end;
   exception
      when others => return 255;
   end Finalization_Decide_Mixed;

   use type Interfaces.C.int;

   function Owned_recovery_authorization
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package Native renames Worldline.Recovery_Authorization_C_API;
      package Wire renames Worldline.Recovery_Authorization_Wire;
      package Inputs is new System.Address_To_Access_Conversions (Wire.Raw_Request);
      package Outputs is new System.Address_To_Access_Conversions (Wire.Raw_Result);
   begin
      if not Native.Transport_Valid (Input, Input_Length, Output, Output_Length) then
         return -1;
      end if;
      declare
         Result : aliased Wire.Raw_Result;
         Status : Interfaces.C.int;
      begin
         Status := Native.Decide (Input, Input_Length, Output, Output_Length,
           Inputs.To_Pointer (Input), Result'Access);
         if Status = 0 then
            Outputs.To_Pointer (Output).all := Result;
         end if;
         Flush_Native_Diagnostic_Trace;
         return Status;
      end;
   exception when others =>
      Flush_Native_Diagnostic_Trace;
      return -1;
      end;
   exception
      when others => return -1;
   end Owned_recovery_authorization;

   function Owned_recovery_authorization_v3
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Arena : System.Address; Arena_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package Native renames Worldline.Recovery_Authorization_V3_C_API;
      package Wire renames Worldline.Recovery_Authorization_V3_Wire;
      package Inputs is new System.Address_To_Access_Conversions (Wire.Raw_Request);
      package Outputs is new System.Address_To_Access_Conversions (Wire.Raw_Result);
   begin
      if not Native.Transport_Valid (Input, Input_Length, Arena, Arena_Length, Output, Output_Length) then
         return -1;
      end if;
      declare
         Result : aliased Wire.Raw_Result;
         Status : Interfaces.C.int;
         Bytes_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Arena_Length));
         Bytes : constant Resource_Bytes_Observer := Observe_Resource_Bytes (Arena, Bytes_Bounds);
      begin
         Status := Native.Decide (Input, Input_Length, Arena, Arena_Length, Output, Output_Length,
           Inputs.To_Pointer (Input), Result'Access, Bytes);
         if Status = 0 then
            Outputs.To_Pointer (Output).all := Result;
         end if;
         Flush_Native_Diagnostic_Trace;
         return Status;
      end;
   exception when others =>
      Flush_Native_Diagnostic_Trace;
      return -1;
      end;
   exception
      when others => return -1;
   end Owned_recovery_authorization_v3;

   function Owned_recovery_protocol
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package Native renames Worldline.Recovery_Protocol_C_API;
      package Wire renames Worldline.Recovery_Protocol_Wire;
      package Inputs is new System.Address_To_Access_Conversions (Wire.Raw_Request);
      package Outputs is new System.Address_To_Access_Conversions (Wire.Raw_Result);
   begin
      if not Native.Transport_Valid (Input, Input_Length, Output, Output_Length) then
         return -1;
      end if;
      declare
         Result : aliased Wire.Raw_Result;
         Status : Interfaces.C.int;
      begin
         Status := Native.Decide (Input, Input_Length, Output, Output_Length,
           Inputs.To_Pointer (Input), Result'Access);
         if Status = 0 then
            Outputs.To_Pointer (Output).all := Result;
         end if;
         Flush_Native_Diagnostic_Trace;
         return Status;
      end;
   exception when others =>
      Flush_Native_Diagnostic_Trace;
      return -1;
      end;
   exception
      when others => return -1;
   end Owned_recovery_protocol;

   function Owned_Chain_Replay
     (Anchors : System.Address; Anchors_Length : Interfaces.C.size_t;
      Rows : System.Address; Rows_Count, Rows_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package Native renames Worldline.Chain_Authority_C_API;
      package Wire renames Worldline.Chain_Authority_Wire;
      package Inputs is new System.Address_To_Access_Conversions (Wire.Raw_Anchors);
      package Outputs is new System.Address_To_Access_Conversions (Wire.Raw_Result);
   begin
      if not Native.Transport_Valid (Anchors, Anchors_Length, Rows, Rows_Count, Rows_Length, Output, Output_Length) then
         return -1;
      end if;
      declare
         Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Rows_Count));
         type Rows_Observer is access constant Native.Raw_Rows;
         function Observe_Rows is new Observe_Foreign_Array
           (Resource_Quantities.Byte_Index, Wire.Raw_Row, Native.Raw_Rows, Rows_Observer);
         Items : constant Rows_Observer := Observe_Rows (Rows, Rows_Bounds);
         Result : aliased Wire.Raw_Result;
         Status : Interfaces.C.int;
      begin
         Status := Native.Replay (Anchors, Anchors_Length, Rows, Rows_Count, Rows_Length, Output, Output_Length,
           Inputs.To_Pointer (Anchors), Items, Result'Access);
         if Status = 0 then Outputs.To_Pointer (Output).all := Result; end if;
         Flush_Native_Diagnostic_Trace;
         return Status;
      end;
   exception when others =>
      Flush_Native_Diagnostic_Trace;
      return -1;
      end;
   exception
      when others => return -1;
   end Owned_Chain_Replay;

   function Owned_Recovery_Select
     (Expected : System.Address; Expected_Length : Interfaces.C.size_t;
      Live_Present : Interfaces.Unsigned_8;
      Live : System.Address; Live_Length : Interfaces.C.size_t;
      Prepared_Present : Interfaces.Unsigned_8;
      Prepared : System.Address; Prepared_Length : Interfaces.C.size_t)
      return Interfaces.Unsigned_8
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package Native renames Worldline.Recovery_C_API;
   begin
      if not Native.Transport_Valid (Expected, Expected_Length, Live_Present, Live, Live_Length, Prepared_Present, Prepared, Prepared_Length) then return 255; end if;
      declare
         Expected_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Expected_Length));
         Expected_Bytes : constant Recovery_Bytes_Observer :=
           Observe_Recovery_Bytes (Expected, Expected_Bounds);
         Live_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 ((if Live_Present = 1 then Live_Length else 0)));
         Live_Bytes : constant Recovery_Bytes_Observer :=
           Observe_Recovery_Bytes (Live, Live_Bounds);
         Prepared_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 ((if Prepared_Present = 1 then Prepared_Length else 0)));
         Prepared_Bytes : constant Recovery_Bytes_Observer :=
           Observe_Recovery_Bytes (Prepared, Prepared_Bounds);
         Status : Interfaces.Unsigned_8;
      begin
         Status := Native.Select_Action (Expected, Expected_Length, Live_Present, Live, Live_Length,
           Prepared_Present, Prepared, Prepared_Length, Expected_Bytes, Live_Bytes, Prepared_Bytes);
         Flush_Native_Diagnostic_Trace;
         return Status;
      end;
   exception when others =>
      Flush_Native_Diagnostic_Trace;
      return 255;
      end;
   exception
      when others => return 255;
   end Owned_Recovery_Select;

   function Owned_History_Select
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Rows : System.Address; Row_Count : Interfaces.C.size_t;
      Final_Present : Interfaces.Unsigned_8; Final_Row, Query, Output : System.Address) return Interfaces.Unsigned_8
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package Native renames Worldline.Evaluation_History_C_API;
      package Q renames Resource_Quantities;
      package Queries is new System.Address_To_Access_Conversions (Native.Query_C);
      package Final_Rows is new System.Address_To_Access_Conversions (Native.Row_C);
      package Outputs is new System.Address_To_Access_Conversions (Native.Selection_C);
   begin
      if not Native.Transport_Valid (Data, Data_Length, Rows, Row_Count, Final_Present, Final_Row, Query, Output) then return 255; end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Data_Length));
         Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Row_Count));
         type Rows_Observer is access constant Native.Row_Array;
         function Observe_Rows is new Observe_Foreign_Array
           (Q.Byte_Index, Native.Row_C, Native.Row_Array, Rows_Observer);
         Bytes : constant Resource_Bytes_Observer := Observe_Resource_Bytes (Data, Data_Bounds);
         Items : constant Rows_Observer := Observe_Rows (Rows, Rows_Bounds);
         Final_View : constant access constant Native.Row_C :=
           (if Final_Present = 1 then Final_Rows.To_Pointer (Final_Row) else null);
         Result : aliased Native.Selection_C;
         Status : Interfaces.Unsigned_8;
      begin
         Status := Native.Select_Evidence (Data, Data_Length, Rows, Row_Count, Final_Present, Final_Row, Query, Output,
           Bytes, Items, Final_View, Queries.To_Pointer (Query), Result'Access);
         if Status = 0 then Outputs.To_Pointer (Output).all := Result; end if;
         Flush_Native_Diagnostic_Trace;
         return Status;
      end;
   exception when others =>
      Flush_Native_Diagnostic_Trace;
      return 255;
      end;
   exception
      when others => return 255;
   end Owned_History_Select;

   package Startup_U64 is new System.Address_To_Access_Conversions (Interfaces.Unsigned_64);
   package Startup_O renames Worldline.Startup_Admission_Owned;
   function Startup_Fits (Pointer : System.Address; Length : Interfaces.C.size_t) return Boolean is
      use System.Storage_Elements;
   begin
      return Length = 0 or else (Pointer /= System.Null_Address and then
        Length <= Interfaces.C.size_t (Startup_O.E.Count'Last) and then
        Length <= Interfaces.C.size_t (Storage_Offset'Last) and then
        To_Integer (Pointer) <= Integer_Address'Last - Integer_Address (Length - 1));
   end Startup_Fits;
   function Startup_U64_Fits (Pointer : System.Address) return Boolean is
     (Startup_Fits (Pointer, 8) and then System.Storage_Elements.To_Integer (Pointer) mod
        Interfaces.Unsigned_64'Alignment = 0);
   function Startup_Disjoint (A : System.Address; AL : Interfaces.C.size_t;
                             B : System.Address; BL : Interfaces.C.size_t) return Boolean is
      use System.Storage_Elements;
   begin
      return AL = 0 or else BL = 0 or else
        (To_Integer (A) <= To_Integer (B) and then Integer_Address (AL) <= To_Integer (B) - To_Integer (A)) or else
        (To_Integer (B) < To_Integer (A) and then Integer_Address (BL) <= To_Integer (A) - To_Integer (B));
   end Startup_Disjoint;
   function Startup_Admission_Decide_V1
     (Input : System.Address; Length : Interfaces.C.size_t;
      Name : System.Address; Name_Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if not Startup_U64_Fits (Status) or else
         not Startup_U64_Fits (Position) or else
         not Startup_Disjoint (Status, 8, Position, 8) or else
         not Startup_Fits (Name, Name_Length) or else
         not Startup_Disjoint (Name, Name_Length, Status, 8) or else
         not Startup_Disjoint (Name, Name_Length, Position, 8) or else
         not Startup_Fits (Input, Length) or else
         not Startup_Disjoint (Input, Length, Status, 8) or else
         not Startup_Disjoint (Input, Length, Position, 8) then return Error_Invalid_Argument; end if;
      Startup_U64.To_Pointer (Status).all := 0;
      Startup_U64.To_Pointer (Position).all := 0;
      declare
         Name_Bytes : Startup_O.E.Bytes (1 .. Startup_O.E.Count (Name_Length)) with Import, Address => Name;
         Input_Bytes : Startup_O.E.Bytes (1 .. Startup_O.E.Count (Length)) with Import, Address => Input;
         Result : Startup_O.Observation;
      begin
         Result := Startup_O.Runtime_Decide (Input_Bytes, Name_Bytes);
         Startup_U64.To_Pointer (Status).all := Interfaces.Unsigned_64 (Startup_O.P.Action'Pos (Result.Status));
         Startup_U64.To_Pointer (Position).all := Interfaces.Unsigned_64 (Result.Position);
      end;
      return Error_OK;
   exception
      when Error : others =>
         Capture_Native_Exception ("wl_startup_admission_decide_v1: ", Error);
         return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end Startup_Admission_Decide_V1;

   function Startup_Owner_Admission_Decide_V1
     (Input : System.Address; Length : Interfaces.C.size_t;
      Name : System.Address; Name_Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if not Startup_U64_Fits (Status) or else
         not Startup_U64_Fits (Position) or else
         not Startup_Disjoint (Status, 8, Position, 8) or else
         not Startup_Fits (Name, Name_Length) or else
         not Startup_Disjoint (Name, Name_Length, Status, 8) or else
         not Startup_Disjoint (Name, Name_Length, Position, 8) or else
         not Startup_Fits (Input, Length) or else
         not Startup_Disjoint (Input, Length, Status, 8) or else
         not Startup_Disjoint (Input, Length, Position, 8) then return Error_Invalid_Argument; end if;
      Startup_U64.To_Pointer (Status).all := 0;
      Startup_U64.To_Pointer (Position).all := 0;
      declare
         Name_Bytes : Startup_O.E.Bytes (1 .. Startup_O.E.Count (Name_Length)) with Import, Address => Name;
         Input_Bytes : Startup_O.E.Bytes (1 .. Startup_O.E.Count (Length)) with Import, Address => Input;
         Result : Startup_O.Observation;
      begin
         Result := Startup_O.Owner_Decide (Input_Bytes, Name_Bytes);
         Startup_U64.To_Pointer (Status).all := Interfaces.Unsigned_64 (Startup_O.P.Action'Pos (Result.Status));
         Startup_U64.To_Pointer (Position).all := Interfaces.Unsigned_64 (Result.Position);
      end;
      return Error_OK;
   exception
      when Error : others =>
         Capture_Native_Exception ("wl_startup_owner_admission_decide_v1: ", Error);
         return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end Startup_Owner_Admission_Decide_V1;

   function Startup_Admission_Transition_V1
     (Before : System.Address; Before_Length : Interfaces.C.size_t;
      After : System.Address; After_Length : Interfaces.C.size_t;
      Name : System.Address; Name_Length : Interfaces.C.size_t;
      Before_Action, After_Action : Interfaces.Unsigned_64;
      Status, Position : System.Address) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if not Startup_U64_Fits (Status) or else
         not Startup_U64_Fits (Position) or else
         not Startup_Disjoint (Status, 8, Position, 8) or else
         not Startup_Fits (Name, Name_Length) or else
         not Startup_Disjoint (Name, Name_Length, Status, 8) or else
         not Startup_Disjoint (Name, Name_Length, Position, 8) or else
         not Startup_Fits (Before, Before_Length) or else
         not Startup_Disjoint (Before, Before_Length, Status, 8) or else
         not Startup_Disjoint (Before, Before_Length, Position, 8) or else
         not Startup_Fits (After, After_Length) or else
         not Startup_Disjoint (After, After_Length, Status, 8) or else
         not Startup_Disjoint (After, After_Length, Position, 8) or else
         Before_Action > Interfaces.Unsigned_64 (Startup_O.E.Count'Last) or else
         After_Action > Interfaces.Unsigned_64 (Startup_O.E.Count'Last) then return Error_Invalid_Argument; end if;
      Startup_U64.To_Pointer (Status).all := 0;
      Startup_U64.To_Pointer (Position).all := 0;
      declare
         Name_Bytes : Startup_O.E.Bytes (1 .. Startup_O.E.Count (Name_Length)) with Import, Address => Name;
         Before_Bytes : Startup_O.E.Bytes (1 .. Startup_O.E.Count (Before_Length)) with Import, Address => Before;
         After_Bytes : Startup_O.E.Bytes (1 .. Startup_O.E.Count (After_Length)) with Import, Address => After;
      begin
         Startup_U64.To_Pointer (Status).all := Boolean'Pos (Startup_O.Runtime_Transition (Before_Bytes, After_Bytes, Name_Bytes, Startup_O.E.Count (Before_Action), Startup_O.E.Count (After_Action)));
         Startup_U64.To_Pointer (Position).all := 0;
      end;
      return Error_OK;
   exception
      when Error : others =>
         Capture_Native_Exception ("wl_startup_admission_transition_v1: ", Error);
         return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end Startup_Admission_Transition_V1;

   function Startup_Owner_Admission_Transition_V1
     (Before : System.Address; Before_Length : Interfaces.C.size_t;
      After : System.Address; After_Length : Interfaces.C.size_t;
      Name : System.Address; Name_Length : Interfaces.C.size_t;
      Before_Action, After_Action : Interfaces.Unsigned_64;
      Status, Position : System.Address) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if not Startup_U64_Fits (Status) or else
         not Startup_U64_Fits (Position) or else
         not Startup_Disjoint (Status, 8, Position, 8) or else
         not Startup_Fits (Name, Name_Length) or else
         not Startup_Disjoint (Name, Name_Length, Status, 8) or else
         not Startup_Disjoint (Name, Name_Length, Position, 8) or else
         not Startup_Fits (Before, Before_Length) or else
         not Startup_Disjoint (Before, Before_Length, Status, 8) or else
         not Startup_Disjoint (Before, Before_Length, Position, 8) or else
         not Startup_Fits (After, After_Length) or else
         not Startup_Disjoint (After, After_Length, Status, 8) or else
         not Startup_Disjoint (After, After_Length, Position, 8) or else
         Before_Action > Interfaces.Unsigned_64 (Startup_O.E.Count'Last) or else
         After_Action > Interfaces.Unsigned_64 (Startup_O.E.Count'Last) then return Error_Invalid_Argument; end if;
      Startup_U64.To_Pointer (Status).all := 0;
      Startup_U64.To_Pointer (Position).all := 0;
      declare
         Name_Bytes : Startup_O.E.Bytes (1 .. Startup_O.E.Count (Name_Length)) with Import, Address => Name;
         Before_Bytes : Startup_O.E.Bytes (1 .. Startup_O.E.Count (Before_Length)) with Import, Address => Before;
         After_Bytes : Startup_O.E.Bytes (1 .. Startup_O.E.Count (After_Length)) with Import, Address => After;
      begin
         Startup_U64.To_Pointer (Status).all := Boolean'Pos (Startup_O.Owner_Transition (Before_Bytes, After_Bytes, Name_Bytes, Startup_O.E.Count (Before_Action), Startup_O.E.Count (After_Action)));
         Startup_U64.To_Pointer (Position).all := 0;
      end;
      return Error_OK;
   exception
      when Error : others =>
         Capture_Native_Exception ("wl_startup_owner_admission_transition_v1: ", Error);
         return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end Startup_Owner_Admission_Transition_V1;


   package body Resources_Transport is
      package Sem renames Worldline.Resources_C_API;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.Unsigned_8;
      use type Interfaces.C.size_t;
      package Resources renames Worldline.Resources;
   function Valid (Address : System.Address; Length : Interfaces.C.size_t)
     return Boolean is
     (Length <= Interfaces.C.size_t (Resources.Byte_Count'Last)
      and then Length <= Interfaces.C.size_t (Storage_Offset'Last)
      and then (Length = 0 or else (Address /= System.Null_Address
        and then Integer_Address (Length - 1) <= Integer_Address'Last - To_Integer (Address))));
      function ABI_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Sem.ABI_Version;
      end;
   exception
      when others => return 0;
   end ABI_Version;
   function Can_Reserve
     (Available_Negative : Interfaces.Unsigned_8;
      Available : System.Address; Available_Length : Interfaces.C.size_t;
      Withheld : System.Address; Withheld_Length : Interfaces.C.size_t;
      Floor : System.Address; Floor_Length : Interfaces.C.size_t;
      Requested : System.Address; Requested_Length : Interfaces.C.size_t)
      return Interfaces.Unsigned_8 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if Available_Negative > 1
        or else not Valid (Available, Available_Length)
        or else not Valid (Withheld, Withheld_Length)
        or else not Valid (Floor, Floor_Length)
        or else not Valid (Requested, Requested_Length)
      then
         return 255;
      end if;
      declare
         Available_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Available_Length));
         Withheld_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Withheld_Length));
         Floor_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Floor_Length));
         Requested_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Requested_Length));
         Decision : U8;
      begin
         Decision := Sem.Can_Reserve
           (Available_Negative, Observe_Resources_Bytes (Available, Available_Bounds),
            Observe_Resources_Bytes (Withheld, Withheld_Bounds),
            Observe_Resources_Bytes (Floor, Floor_Bounds),
            Observe_Resources_Bytes (Requested, Requested_Bounds));
         Flush_Native_Diagnostic_Trace;
         return Decision;
      end;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return 255;
      end;
   exception
      when others => return 255;
   end Can_Reserve;
   end Resources_Transport;

   package body Resource_Policy_Transport is
      package Sem renames Worldline.Resource_Policy_C_API;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.Unsigned_8;
      use type Interfaces.C.size_t;
      package Q renames Resource_Quantities;
      use type Q.Byte_Count;
      subtype Quantity_C is Sem.Quantity_C;
      subtype Optional_C is Sem.Optional_C;
      subtype Input_C is Sem.Input_C;
      subtype Disk_C is Sem.Disk_C;
      subtype Result_C is Sem.Result_C;
   package Input_Pointers is new System.Address_To_Access_Conversions (Input_C);
   package Result_Pointers is new System.Address_To_Access_Conversions (Result_C);
   use type Input_Pointers.Object_Pointer;
   use type Result_Pointers.Object_Pointer;
   function Extent_Valid
     (Address : System.Address; Length : Size; Alignment : Size := 1)
      return Boolean is
     (Alignment /= 0 and then
      Length <= Size (Storage_Offset'Last) and then
      (Length = 0 or else
        (Address /= System.Null_Address and then
         To_Integer (Address) mod Integer_Address (Alignment) = 0 and then
         Integer_Address (Length - 1) <=
           Integer_Address'Last - To_Integer (Address))));
   procedure Write_Result (Address : System.Address; Item : Result_C)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Result_Pointers.Object_Pointer := Result_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Result;
      function ABI_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Sem.ABI_Version;
      end;
   exception
      when others => return 0;
   end ABI_Version;
      function Layout_Size (Selector : U8) return Size is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Sem.Layout_Size (Selector);
      end;
   exception
      when others => return Size'Last;
   end Layout_Size;
      function Layout_Offset (Selector, Field : U8) return Size is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Sem.Layout_Offset (Selector, Field);
      end;
   exception
      when others => return Size'Last;
   end Layout_Offset;
   function Admit
     (Data : System.Address; Data_Length : Size;
      Input : System.Address; Disks : System.Address; Disk_Count : Size;
      Result : System.Address) return U8 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      Disk_Size : constant Size := Disk_C'Object_Size / System.Storage_Unit;
   begin
      if Data_Length > Size (Q.Byte_Count'Last) or else
        Disk_Count > Size (Q.Byte_Count'Last) or else
        Disk_Count > Size (Storage_Offset'Last) / Disk_Size or else
        not Extent_Valid (Data, Data_Length) or else
        not Extent_Valid (Input, Input_C'Object_Size / System.Storage_Unit,
                         Input_C'Alignment) or else
        not Extent_Valid (Result, Result_C'Object_Size / System.Storage_Unit,
                         Result_C'Alignment) or else
        not Extent_Valid (Disks, Disk_Count * Disk_Size, Disk_C'Alignment)
      then
         return 255;
      end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Data_Length));
         Disks_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Disk_Count));
         type Disks_Observer is access constant Sem.Disk_Array;
         function Observe_Disks is new Observe_Foreign_Array
           (Q.Byte_Index, Disk_C, Sem.Disk_Array, Disks_Observer);
         Value : Result_C;
         Transport : U8;
      begin
         Transport := Sem.Admit
           (Observe_Resource_Bytes (Data, Data_Bounds), Input_Pointers.To_Pointer (Input),
            Observe_Disks (Disks, Disks_Bounds), Value);
         Flush_Native_Diagnostic_Trace;
         if Transport = 0 then Write_Result (Result, Value); end if;
         return Transport;
      end;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return 255;
      end;
   exception
      when others => return 255;
   end Admit;
   end Resource_Policy_Transport;

   package body Resource_Ledger_Transport is
      package Sem renames Worldline.Resource_Ledger_C_API;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.Unsigned_8;
      use type Interfaces.C.size_t;
      package Q renames Resource_Quantities;
      use type Q.Byte_Count;
      package L renames Resource_Ledger;
      subtype Quantity_C is Sem.Quantity_C;
      subtype Optional_C is Sem.Optional_C;
      subtype Row_C is Sem.Row_C;
      subtype Result_C is Sem.Result_C;
   package Byte_Pointers is new System.Address_To_Access_Conversions (Q.Byte);
   package Quantity_Pointers is new System.Address_To_Access_Conversions (Quantity_C);
   package Result_Pointers is new System.Address_To_Access_Conversions (Result_C);
   use type Byte_Pointers.Object_Pointer;
   use type Quantity_Pointers.Object_Pointer;
   use type Result_Pointers.Object_Pointer;
   function Extent_Valid
     (Address : System.Address; Length : Size; Alignment : Size := 1)
      return Boolean is
     (Alignment /= 0 and then
      Length <= Size (Storage_Offset'Last) and then
      (Length = 0 or else
        (Address /= System.Null_Address and then
         To_Integer (Address) mod Integer_Address (Alignment) = 0 and then
         Integer_Address (Length - 1) <=
           Integer_Address'Last - To_Integer (Address))));
   procedure Write_Byte (Address : System.Address; Item : Q.Byte)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Byte_Pointers.Object_Pointer := Byte_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Byte;
   procedure Write_Quantity (Address : System.Address; Item : Quantity_C)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Quantity_Pointers.Object_Pointer := Quantity_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Quantity;
   procedure Write_Result (Address : System.Address; Item : Result_C)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Result_Pointers.Object_Pointer := Result_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Result;
   procedure Write_Data (Address : System.Address; Value : Q.Byte_Array)
     with Pre => (Value'Length = 0 or else Address /= System.Null_Address),
          Exceptional_Cases => (others => True)
   is
   begin
      for I in Value'Range loop
         Write_Byte (Address + Storage_Offset (I - Value'First), Value (I));
      end loop;
   end Write_Data;
      function Encode (V : Q.Quantity) return Quantity_C renames Sem.Encode;
         function Overlaps (Left : System.Address; Left_Length : Size;
                         Right : System.Address; Right_Length : Size) return Boolean is
        (Left_Length /= 0 and then Right_Length /= 0 and then
          (if To_Integer (Left) <= To_Integer (Right) then
             To_Integer (Right) - To_Integer (Left) < Integer_Address (Left_Length)
           else To_Integer (Left) - To_Integer (Right) < Integer_Address (Right_Length)));
   function ABI_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Sem.ABI_Version;
      end;
   exception
      when others => return 0;
   end ABI_Version;
      function Layout_Size (Selector : U8) return Size is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Sem.Layout_Size (Selector);
      end;
   exception
      when others => return Size'Last;
   end Layout_Size;
      function Layout_Offset (Selector, Field : U8) return Size is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Sem.Layout_Offset (Selector, Field);
      end;
   exception
      when others => return Size'Last;
   end Layout_Offset;
   function Compute
     (Data : System.Address; Data_Length : Size;
      Rows : System.Address; Row_Count : Size;
      Detail_Data : System.Address; Detail_Length : Size;
      Total_Data : System.Address; Total_Length : Size;
      Details : System.Address; Result : System.Address) return U8 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      Row_Size : constant Size := Row_C'Object_Size / System.Storage_Unit;
      Quantity_Size : constant Size := Quantity_C'Object_Size / System.Storage_Unit;
   begin
      if Data_Length > Size (Q.Byte_Count'Last) or else
        Detail_Length > Size (Q.Byte_Count'Last) or else
        Total_Length > Size (Q.Byte_Count'Last) or else

        Row_Count > Size (Q.Byte_Count'Last) or else
        Row_Count > Size (Storage_Offset'Last) / Row_Size or else
        Row_Count > Size (Storage_Offset'Last) / Quantity_Size or else
        not Extent_Valid (Data, Data_Length) or else
        not Extent_Valid (Detail_Data, Detail_Length) or else
        not Extent_Valid (Total_Data, Total_Length) or else
        not Extent_Valid (Rows, Row_Count * Row_Size, Row_C'Alignment) or else
        not Extent_Valid (Details, Row_Count * Quantity_Size,
                         Quantity_C'Alignment) or else
        not Extent_Valid (Result, Result_C'Object_Size / System.Storage_Unit,
                         Result_C'Alignment)
      then
         return 255;
      end if;
      if Overlaps (Detail_Data, Detail_Length, Data, Data_Length) or else
        Overlaps (Detail_Data, Detail_Length, Rows, Row_Count * Row_Size) or else
        Overlaps (Total_Data, Total_Length, Data, Data_Length) or else
        Overlaps (Total_Data, Total_Length, Rows, Row_Count * Row_Size) or else
        Overlaps (Total_Data, Total_Length, Detail_Data, Detail_Length) or else
        Overlaps (Details, Row_Count * Quantity_Size, Data, Data_Length) or else
        Overlaps (Details, Row_Count * Quantity_Size, Rows, Row_Count * Row_Size) or else
        Overlaps (Details, Row_Count * Quantity_Size, Detail_Data, Detail_Length) or else
        Overlaps (Details, Row_Count * Quantity_Size, Total_Data, Total_Length) or else
        Overlaps (Result, Result_C'Object_Size / System.Storage_Unit, Data, Data_Length) or else
        Overlaps (Result, Result_C'Object_Size / System.Storage_Unit, Rows, Row_Count * Row_Size) or else
        Overlaps (Result, Result_C'Object_Size / System.Storage_Unit, Detail_Data, Detail_Length) or else
        Overlaps (Result, Result_C'Object_Size / System.Storage_Unit, Total_Data, Total_Length) or else
        Overlaps (Result, Result_C'Object_Size / System.Storage_Unit, Details, Row_Count * Quantity_Size)
      then return 255; end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Data_Length));
         Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Row_Count));
         type Rows_Observer is access constant Sem.Row_Array;
         function Observe_Rows is new Observe_Foreign_Array
           (Q.Byte_Index, Row_C, Sem.Row_Array, Rows_Observer);
         Detail_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Detail_Length));
         Total_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Total_Length));
         Typed_Details : L.Quantity_Array (1 .. Q.Byte_Count (Row_Count));
         Total : Q.Quantity;
         Status : L.Result_Status;
         Transport : U8;
      begin
         Transport := Sem.Compute
           (Observe_Resource_Bytes (Data, Data_Bounds), Observe_Rows (Rows, Rows_Bounds),
            Detail_Arena, Total_Arena, Typed_Details, Total, Status);
         Flush_Native_Diagnostic_Trace;
         if Transport = 0 then
            Write_Data (Detail_Data, Detail_Arena);
            Write_Data (Total_Data, Total_Arena);
            for I in Typed_Details'Range loop
               Write_Quantity (Details + Storage_Offset (Size (I - 1) * Quantity_Size),
                               Encode (Typed_Details (I)));
            end loop;
            Write_Result (Result, (Status => L.Result_Status'Pos (Status), Total => Encode (Total)));
         end if;
         return Transport;
      end;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return 255;
      end;
   exception
      when others => return 255;
   end Compute;
   function Headroom
     (Data : System.Address; Data_Length : Size;
      Available, Withheld, Floor : System.Address;
      Output : System.Address; Output_Length : Size;
      Result : System.Address) return U8 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      Quantity_Size : constant Size := Quantity_C'Object_Size / System.Storage_Unit;
   begin
      if Data_Length > Size (Q.Byte_Count'Last) or else
        Output_Length > Size (Q.Byte_Count'Last) or else
        not Extent_Valid (Data, Data_Length) or else
        not Extent_Valid (Output, Output_Length) or else
        not Extent_Valid (Available, Quantity_Size, Quantity_C'Alignment) or else
        not Extent_Valid (Withheld, Quantity_Size, Quantity_C'Alignment) or else
        not Extent_Valid (Floor, Quantity_Size, Quantity_C'Alignment) or else
        not Extent_Valid (Result, Result_C'Object_Size / System.Storage_Unit,
                         Result_C'Alignment)
      then
         return 255;
      end if;
      if Overlaps (Output, Output_Length, Data, Data_Length) or else
        Overlaps (Output, Output_Length, Available, Quantity_Size) or else
        Overlaps (Output, Output_Length, Withheld, Quantity_Size) or else
        Overlaps (Output, Output_Length, Floor, Quantity_Size) or else
        Overlaps (Result, Result_C'Object_Size / System.Storage_Unit, Data, Data_Length) or else
        Overlaps (Result, Result_C'Object_Size / System.Storage_Unit, Available, Quantity_Size) or else
        Overlaps (Result, Result_C'Object_Size / System.Storage_Unit, Withheld, Quantity_Size) or else
        Overlaps (Result, Result_C'Object_Size / System.Storage_Unit, Floor, Quantity_Size) or else
        Overlaps (Result, Result_C'Object_Size / System.Storage_Unit, Output, Output_Length)
      then return 255; end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Data_Length));
         Output_Arena : Q.Byte_Array (1 .. Q.Byte_Count (Output_Length));
         Typed_Result : Q.Quantity;
         Status : L.Result_Status;
         Transport : U8;
      begin
         Transport := Sem.Headroom (Observe_Resource_Bytes (Data, Data_Bounds), Quantity_Pointers.To_Pointer (Available), Quantity_Pointers.To_Pointer (Withheld), Quantity_Pointers.To_Pointer (Floor), Output_Arena, Typed_Result, Status);
         Flush_Native_Diagnostic_Trace;
         if Transport = 0 then
            Write_Data (Output, Output_Arena);
            Write_Result (Result, (Status => L.Result_Status'Pos (Status), Total => Encode (Typed_Result)));
         end if;
         return Transport;
      end;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return 255;
      end;
   exception
      when others => return 255;
   end Headroom;
   end Resource_Ledger_Transport;

   package body Resource_Run_Ledger_Transport is
      package Sem renames Resource_Run_Ledger_C_API;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.Unsigned_8;
      use type Interfaces.C.size_t;
      package Q renames Resource_Quantities;
      use type Q.Byte_Count;
      package W renames Resource_Run_Ledger_Wire;
      use type Interfaces.C.int;
   package Packet_Pointers is new System.Address_To_Access_Conversions (W.Raw_Packet);
   package Result_Pointers is new System.Address_To_Access_Conversions (W.Raw_Result);
   use type Packet_Pointers.Object_Pointer;
   use type Result_Pointers.Object_Pointer;
   function Shape (Address : System.Address; Length : Interfaces.C.size_t) return Boolean is
     (Address /= System.Null_Address and then Length > 0
      and then Length <= Interfaces.C.size_t (Storage_Offset'Last)
      and then Integer_Address (Length - 1) <= Integer_Address'Last - To_Integer (Address));
   function Array_Shape (Address : System.Address; Count, Element_Size : Interfaces.C.size_t;
                        Alignment : Integer_Address) return Boolean is
     (Element_Size /= 0 and then Alignment /= 0
      and then Count <= Interfaces.C.size_t (Q.Byte_Count'Last)
      and then (Count = 0 or else (Count <= Interfaces.C.size_t (Storage_Offset'Last) / Element_Size
       and then Shape (Address, Count * Element_Size) and then To_Integer (Address) mod Alignment = 0)));
   procedure Write_Result (Address : System.Address; Item : W.Raw_Result)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Result_Pointers.Object_Pointer := Result_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Result;
      function Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Sem.Version;
      end;
   exception
      when others => return 0;
   end Version;
      function Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Sem.Layout (Kind, Field);
      end;
   exception
      when others => return -1;
   end Layout;
   function Check
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Arena : System.Address; Arena_Length : Interfaces.C.size_t;
      Before_Rows : System.Address; Before_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address; Proposed_Count : Interfaces.C.size_t;
      Native : System.Address; Native_Count : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      Row_Size : constant Size := W.Raw_Row'Size / System.Storage_Unit;
      Native_Size : constant Size := W.Raw_Native'Size / System.Storage_Unit;
   begin
      if Input_Length /= W.Raw_Packet'Size / System.Storage_Unit
        or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit
        or else not Shape (Input, Input_Length) or else not Shape (Output, Output_Length)
        or else To_Integer (Input) mod W.Raw_Packet'Alignment /= 0
        or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0
        or else Arena_Length > Interfaces.C.size_t (Q.Byte_Count'Last)
        or else (Arena_Length > 0 and then not Shape (Arena, Arena_Length))
        or else not Array_Shape (Before_Rows, Before_Count, Row_Size, W.Raw_Row'Alignment)
        or else not Array_Shape (Proposed_Rows, Proposed_Count, Row_Size, W.Raw_Row'Alignment)
        or else not Array_Shape (Native, Native_Count, Native_Size, W.Raw_Native'Alignment)
      then return -1; end if;
      declare
         Arena_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Arena_Length));
         Before_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Before_Count));
         Proposed_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Count));
         Native_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Native_Count));
         type Rows_Observer is access constant W.Raw_Row_Array;
         function Observe_Rows is new Observe_Foreign_Array
           (Q.Byte_Index, W.Raw_Row, W.Raw_Row_Array, Rows_Observer);
         type Native_Observer is access constant W.Raw_Native_Array;
         function Observe_Native is new Observe_Foreign_Array
           (Q.Byte_Index, W.Raw_Native, W.Raw_Native_Array, Native_Observer);
         Value : W.Raw_Result;
         Transport : Interfaces.C.int;
      begin
         Transport := Sem.Check
           (Packet_Pointers.To_Pointer (Input), Observe_Resource_Bytes (Arena, Arena_Bounds),
            Observe_Rows (Before_Rows, Before_Bounds), Observe_Rows (Proposed_Rows, Proposed_Bounds),
            Observe_Native (Native, Native_Bounds), Value);
         Flush_Native_Diagnostic_Trace;
         if Transport = 0 then Write_Result (Output, Value); end if;
         return Transport;
      end;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return -1;
      end;
   exception
      when others => return -1;
   end Check;
   end Resource_Run_Ledger_Transport;

   package body Reservation_Lifecycle_Transport is
      package Sem renames Worldline.Reservation_Lifecycle_C_API;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.Unsigned_8;
      use type Interfaces.C.size_t;
      package R renames Worldline.Resources;
      package L renames Resource_Reservation_Lifecycle;
      subtype Row_C is Sem.Row_C;
   package Byte_Pointers is new System.Address_To_Access_Conversions (U8);
   use type Byte_Pointers.Object_Pointer;
   function Extent_Valid
     (Address : System.Address; Length : Size; Alignment : Size := 1)
      return Boolean is
     (Alignment /= 0 and then
      Length <= Size (Storage_Offset'Last) and then
      (Length = 0 or else
        (Address /= System.Null_Address and then
         To_Integer (Address) mod Integer_Address (Alignment) = 0 and then
         Integer_Address (Length - 1) <=
           Integer_Address'Last - To_Integer (Address))));
   procedure Write_Byte (Address : System.Address; Item : U8)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Byte_Pointers.Object_Pointer :=
        Byte_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Byte;
         function Overlaps (Left : System.Address; Left_Length : Size;
                         Right : System.Address; Right_Length : Size) return Boolean is
        (Left_Length /= 0 and then Right_Length /= 0 and then
          (if To_Integer (Left) <= To_Integer (Right) then
             To_Integer (Right) - To_Integer (Left) < Integer_Address (Left_Length)
           else To_Integer (Left) - To_Integer (Right) < Integer_Address (Right_Length)));
   function ABI_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Sem.ABI_Version;
      end;
   exception
      when others => return 0;
   end ABI_Version;
      function Layout_Size return Size is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Sem.Layout_Size;
      end;
   exception
      when others => return Size'Last;
   end Layout_Size;
      function Layout_Offset (Field : U8) return Size is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Sem.Layout_Offset (Field);
      end;
   exception
      when others => return Size'Last;
   end Layout_Offset;
   function Plan
     (Data : System.Address; Data_Length : Size;
      Rows : System.Address; Row_Count : Size;
      Mode, Present : U8; Requested_First, Requested_Length : Size;
      Removed : System.Address; Removed_Length : Size) return U8 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      Row_Size : constant Size := Layout_Size;
   begin
      if Data_Length > Size (R.Byte_Count'Last) or else
        Row_Count > Size (R.Byte_Count'Last) or else
        Removed_Length > Size (R.Byte_Count'Last) or else
        Row_Count > Size (Storage_Offset'Last) / Row_Size or else
        Present > 1 or else
        (Present = 1 and then
          (Requested_First < 1 or else
           Requested_First > Size (R.Byte_Count'Last) or else
           Requested_Length > Size (R.Byte_Count'Last))) or else
        not Extent_Valid (Data, Data_Length) or else
        not Extent_Valid (Rows, Row_Count * Row_Size, Row_C'Alignment) or else
        not Extent_Valid (Removed, Removed_Length)
      then
         return 255;
      end if;
      if Overlaps (Removed, Removed_Length, Data, Data_Length) or else
        Overlaps (Removed, Removed_Length, Rows, Row_Count * Row_Size)
      then return 255; end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Data_Length));
         Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Row_Count));
         type Rows_Observer is access constant Sem.Row_Array;
         function Observe_Rows is new Observe_Foreign_Array
           (R.Byte_Index, Row_C, Sem.Row_Array, Rows_Observer);
         Mask : L.Removal_Array (1 .. R.Byte_Count (Removed_Length));
         Status : U8;
      begin
         Status := Sem.Plan
           (Observe_Resources_Bytes (Data, Data_Bounds), Observe_Rows (Rows, Rows_Bounds),
            Mode, Present, Requested_First, Requested_Length, Mask);
         Flush_Native_Diagnostic_Trace;
         if Status in 2 | 3 then
            for I in Mask'Range loop
               Write_Byte (Removed + Storage_Offset (I - 1), Boolean'Pos (Mask (I)));
            end loop;
         end if;
         return Status;
      end;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return 255;
      end;
   exception
      when others => return 255;
   end Plan;
   end Reservation_Lifecycle_Transport;

   function Pending_Decide_V1 (Input, Output : System.Address) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package P renames Evaluation_Pending_C;
      package E renames Evaluation_Pending;
      package Requests is new System.Address_To_Access_Conversions (P.Request);
      package Results is new System.Address_To_Access_Conversions (P.Result);
      use type Interfaces.C.int;
      use type P.I64;
      R : P.Request;
      Value : P.Result;
      Status : Interfaces.C.int;
      Data_Bounds, Rows_Bounds : aliased Foreign_Array_Bounds;
      type Rows_Observer is access constant P.Row_Array;
      function Observe_Rows is new Observe_Foreign_Array
        (E.Index, P.Row, P.Row_Array, Rows_Observer);
   begin
      --  Arithmetic guards are analyzed On; they establish only numeric shape.
      --  The caller supplies live stable readable allocations and exclusive output.
      if not P.Fixed_Valid (Input, Output) then
         return 255;
      end if;
      --  The original fixed-record snapshot, performed exactly once.
      P.Read_Request (Requests.To_Pointer (Input), R);
      if not P.Transport_Valid (R, Output) then
         return 255;
      end if;
      --  Views do not copy or authorize. Original On loops own the sole snapshots.
      Data_Bounds.Last := R.Data_Length;
      Rows_Bounds.Last := R.Row_Count;
      Status := P.Decide
        (R, Output, Observe_Resource_Bytes (R.Data, Data_Bounds),
         Observe_Rows (R.Rows, Rows_Bounds), Value);
      if Status = 0 then
         --  Only the original successful write point mutates foreign storage.
         Results.To_Pointer (Output).all := Value;
      end if;
      Flush_Native_Diagnostic_Trace;
      return Status;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return 255;
      end;
   exception
      when others => return 255;
   end Pending_Decide_V1;

   function Pending_Decide_V2 (Input, Output : System.Address) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package P renames Evaluation_Pending_V2_C;
      package E renames Evaluation_Pending;
      package Requests is new System.Address_To_Access_Conversions (P.Request);
      package Results is new System.Address_To_Access_Conversions (P.Result);
      use type Interfaces.C.int;
      use type P.I64;
      R : P.Request;
      Value : P.Result;
      Status : Interfaces.C.int;
      Data_Bounds, Rows_Bounds : aliased Foreign_Array_Bounds;
      type Rows_Observer is access constant P.Row_Array;
      function Observe_Rows is new Observe_Foreign_Array
        (E.Index, P.Row, P.Row_Array, Rows_Observer);
   begin
      --  Arithmetic guards are analyzed On; they establish only numeric shape.
      --  The caller supplies live stable readable allocations and exclusive output.
      if not P.Fixed_Valid (Input, Output) then
         return 255;
      end if;
      --  The original fixed-record snapshot, performed exactly once.
      P.Read_Request (Requests.To_Pointer (Input), R);
      if not P.Transport_Valid (R, Output) then
         return 255;
      end if;
      --  Views do not copy or authorize. Original On loops own the sole snapshots.
      Data_Bounds.Last := R.Data_Length;
      Rows_Bounds.Last := R.Row_Count;
      Status := P.Decide
        (R, Output, Observe_Resource_Bytes (R.Data, Data_Bounds),
         Observe_Rows (R.Rows, Rows_Bounds), Value);
      if Status = 0 then
         --  Only the original successful write point mutates foreign storage.
         Results.To_Pointer (Output).all := Value;
      end if;
      Flush_Native_Diagnostic_Trace;
      return Status;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return 255;
      end;
   exception
      when others => return 255;
   end Pending_Decide_V2;

   package body Authority_Glue is
   package A renames Worldline.Evaluation_Authority;
   package W renames A.W;
   package C renames Worldline.Collapse_Wire;
   use type System.Address;
   use System.Storage_Elements;
   package RP is new System.Address_To_Access_Conversions (W.Raw_Record);
   package OP is new System.Address_To_Access_Conversions (W.Wire_Classification);
   package CP is new System.Address_To_Access_Conversions (C.Raw_Request);
   -- Numeric extents do not establish C allocation ownership. Callers must
   -- supply stable owned objects of the queried exact extent for the call.
   function Fits (P : System.Address; Bits, Alignment : Natural) return Boolean is
     (P /= System.Null_Address and then Alignment > 0
      and then To_Integer (P) mod Integer_Address (Alignment) = 0
      and then Bits mod System.Storage_Unit = 0
      and then Bits / System.Storage_Unit > 0
      and then Integer_Address (Bits / System.Storage_Unit - 1) <=
        Integer_Address'Last - To_Integer (P));
function Version return Byte is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return (1);
      end;
   exception
      when others => return 255;
   end Version;
   function Layout (Kind, Field : Byte) return Interfaces.C.size_t is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      R : W.Raw_Record; O : W.Wire_Classification;
   begin
      case Kind is
         when 0 => case Field is
            when 0 => return W.Raw_Record'Object_Size / System.Storage_Unit;
            when 1 => return W.Raw_Record'Alignment;
            when 2 => return R.Observations'Position;
            when 3 => return R.Report_Based'Position;
            when 4 => return R.Report_Facts'Position;
            when 5 => return R.Presence'Position;
            when others => return Interfaces.C.size_t'Last; end case;
         when 1 => case Field is
            when 0 => return W.Wire_Classification'Object_Size / System.Storage_Unit;
            when 1 => return W.Wire_Classification'Alignment;
            when 2 => return O.Status'Position;
            when 3 => return O.Execution'Position;
            when 4 => return O.Result'Position;
            when 5 => return O.Bundle'Position;
            when others => return Interfaces.C.size_t'Last; end case;
         when others => return Interfaces.C.size_t'Last;
      end case;
      end;
   exception
      when others => return Interfaces.C.size_t'Last;
   end Layout;
   function Classify (Raw, Output : System.Address) return Byte is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if not Fits (Raw, W.Raw_Record'Object_Size, W.Raw_Record'Alignment)
        or else not Fits (Output, W.Wire_Classification'Object_Size, W.Wire_Classification'Alignment)
        or else not Disjoint (Raw, W.Raw_Record'Object_Size, Output, W.Wire_Classification'Object_Size)
      then return W.Invalid_Record; end if;
      declare
         Owned : constant W.Raw_Record := RP.To_Pointer (Raw).all;
         Value : constant W.Wire_Classification := W.Classify_Wire (Owned);
      begin OP.To_Pointer (Output).all := Value; return Value.Status; end;
   exception when others => return W.Invalid_Record;
      end;
   exception
      when others => return 255;
   end Classify;
   function Admit (Raw : System.Address; Confinement : Byte) return Byte is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if not Fits (Raw, W.Raw_Record'Object_Size, W.Raw_Record'Alignment) then return W.Invalid_Record; end if;
      declare Owned : constant W.Raw_Record := RP.To_Pointer (Raw).all;
      begin return W.Confined_Admit_Wire (Owned, Confinement); end;
   exception when others => return W.Invalid_Record;
      end;
   exception
      when others => return 255;
   end Admit;
   function Report (Raw : System.Address) return Byte is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      if not Fits (Raw, W.Raw_Record'Object_Size, W.Raw_Record'Alignment) then return W.Invalid_Record; end if;
      declare Owned : constant W.Raw_Record := RP.To_Pointer (Raw).all;
      begin return A.Report_Of (Owned); end;
   exception when others => return W.Invalid_Record;
      end;
   exception
      when others => return 255;
   end Report;
   function Dependencies (Request : System.Address) return Byte is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      use type A.Raw_Dependency;
   begin
      if not Fits (Request, C.Raw_Request'Object_Size, C.Raw_Request'Alignment)
      then return C.Invalid_Request; end if;
      declare
         Owned : constant C.Raw_Request := CP.To_Pointer (Request).all;
         Needed : constant A.Raw_Dependency := A.Dependencies (Owned);
      begin
         if Needed = A.Invalid_Collapse then return C.Invalid_Request; end if;
         return A.Raw_Dependency'Pos (Needed);
      end;
   exception when others => return C.Invalid_Request;
      end;
   exception
      when others => return 255;
   end Dependencies;
   function Decide_Raw_Context (Request, Primary, Primary_Raw, Primary_Confinement, Primary_Context,
       Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address;
       Agent_Confinement : Byte) return Byte is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package K renames Evaluation_Completion_C;
      package T renames Evaluation_Completion;
      use type Interfaces.C.int;
      use type K.U32;
      P_Result, S_Result : aliased K.Result;
      P_Request_Bounds, S_Request_Bounds : aliased Completion_Request_Bounds;
      P_Context_Bounds, S_Context_Bounds : aliased Completion_Context_Bounds;
      P_Ready, S_Ready : Byte := 0;
      Agent_Ready : Byte := 0;
      function Retained (R : K.Result) return Boolean is
        (R.Reason = T.Decision'Pos (T.Retain_Terminal)
         or else R.Reason = T.Decision'Pos (T.Already_Retained));
   begin
      if not Fits (Request, C.Raw_Request'Object_Size, C.Raw_Request'Alignment)
      then return C.Invalid_Request; end if;
      declare
         Bound : C.Raw_Request := CP.To_Pointer (Request).all;
         Needed : constant A.Raw_Dependency := A.Dependencies (Bound);
         use type A.Raw_Dependency;
      begin
      if Needed = A.Invalid_Collapse then return C.Invalid_Request; end if;
      -- Classify every required owned request again. An unused checkpoint or
      -- already-covered staged input is not read, decoded or made a premise.
      -- Neither carried Collapse_Request roster byte authorizes anything.
      if A.Needs_Primary (Needed) and then Primary /= System.Null_Address then
         if Completion_Raw_Decide (Primary, Primary_Raw, Primary_Confinement,
                          P_Result'Address) /= 0
           or else not Retained (P_Result) or else P_Result.Promotion > 1
         then return C.Invalid_Request; end if;
         P_Ready := Byte (P_Result.Promotion);
      end if;
      if A.Needs_Staged (Needed) and then Staged /= System.Null_Address then
         if Completion_Raw_Decide (Staged, Staged_Raw, Staged_Confinement,
                          S_Result'Address) /= 0
           or else not Retained (S_Result) or else S_Result.Promotion > 1
         then return C.Invalid_Request; end if;
         S_Ready := Byte (S_Result.Promotion);
      end if;
      if A.Needs_Agent (Needed) and then Agent /= System.Null_Address then
         if not Fits (Agent, W.Raw_Record'Object_Size, W.Raw_Record'Alignment)
         then return C.Invalid_Request; end if;
         declare
            Owned_Agent : constant W.Raw_Record := RP.To_Pointer (Agent).all;
         begin
            Agent_Ready := W.Confined_Admit_Wire (Owned_Agent, Agent_Confinement);
            if Agent_Ready = W.Invalid_Record then return C.Invalid_Request; end if;
            if Owned_Agent.Observations (W.Source_Field) /= W.E.Origin'Pos (W.E.Agent)
            then Agent_Ready := 0; end if;
         end;
      end if;
         if Agent_Ready = 1 then
            if P_Ready = 1 and then K.Context_Matches
              (Completion_Request_View (Primary, P_Request_Bounds, Full => False),
               Completion_Context_View (Primary_Context, P_Context_Bounds),
               Completion_Evidence_View (Request, Agent), Agent_Confinement) /= 1
            then return C.Invalid_Request; end if;
            if S_Ready = 1 and then K.Context_Matches
              (Completion_Request_View (Staged, S_Request_Bounds, Full => False),
               Completion_Context_View (Staged_Context, S_Context_Bounds),
               Completion_Evidence_View (Request, Agent), Agent_Confinement) /= 1
            then return C.Invalid_Request; end if;
         end if;
         Bound.Roster_Complete := (if Agent_Ready = 1 then P_Ready else 0);
         Bound.Staged_Roster_Complete := (if Agent_Ready = 1 then S_Ready else 0);
         return C.Decide_Wire (Bound);
      end;
   exception when others => return C.Invalid_Request;
      end;
   exception
      when others => return 255;
   end Decide_Raw_Context;
   function Decide_Raw (Request, Primary, Primary_Raw, Primary_Confinement,
       Staged, Staged_Raw, Staged_Confinement, Agent : System.Address;
       Agent_Confinement : Byte) return Byte is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return Decide_Raw_Context
        (Request, Primary, Primary_Raw, Primary_Confinement, System.Null_Address,
         Staged, Staged_Raw, Staged_Confinement, System.Null_Address, Agent,
         Agent_Confinement);
      end;
   exception
      when others => return 255;
   end Decide_Raw;
   function Decide_Raw_Metadata
     (Request, Primary, Primary_Raw, Primary_Confinement, Primary_Context,
      Staged, Staged_Raw, Staged_Confinement, Staged_Context, Agent : System.Address;
      Agent_Confinement : Byte) return Byte is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package K renames Evaluation_Completion_C;
      use type Interfaces.C.int;
      P_Context, S_Context : System.Address := System.Null_Address;
      P_Request_Bounds, S_Request_Bounds : aliased Completion_Request_Bounds;
      P_Meta_Bounds, S_Meta_Bounds : aliased Completion_Metadata_Bounds;
   begin
      if not Fits (Request, C.Raw_Request'Object_Size, C.Raw_Request'Alignment)
      then return C.Invalid_Request; end if;
      declare
         Bound : constant C.Raw_Request := CP.To_Pointer (Request).all;
         Needed : constant A.Raw_Dependency := A.Dependencies (Bound);
         use type A.Raw_Dependency;
      begin
         if Needed = A.Invalid_Collapse then return C.Invalid_Request; end if;
         -- Unneeded checkpoint evidence stays unobserved. The compatibility
         -- path computes a provisional decision only; neither function effects
         -- a promotion. Preserve its complete original ordered refusal result.
         if A.Needs_Primary (Needed) then
            P_Context := Completion_Metadata_Base (Primary_Context);
         end if;
         if A.Needs_Staged (Needed) then
            S_Context := Completion_Metadata_Base (Staged_Context);
         end if;
         declare
            Decision : constant Byte := Decide_Raw_Context
              (Request, Primary, Primary_Raw, Primary_Confinement, P_Context,
               Staged, Staged_Raw, Staged_Confinement, S_Context, Agent, Agent_Confinement);
         begin
            if Decision /= Byte (Worldline.Collapse.Decision'Pos (Worldline.Collapse.Authorized))
            then return Decision; end if;
            -- Every row joins before returning authorization, regardless of
            -- requirement membership, duplicate position, state or verdict.
            if A.Needs_Primary (Needed) and then
              K.Metadata_Matches (Completion_Request_View (Primary, P_Request_Bounds, Full => False, Plans => False),
                Completion_Metadata_View (Primary_Context, P_Meta_Bounds)) /= 1
            then return C.Invalid_Request; end if;
            if A.Needs_Staged (Needed) and then
              K.Metadata_Matches (Completion_Request_View (Staged, S_Request_Bounds, Full => False, Plans => False),
                Completion_Metadata_View (Staged_Context, S_Meta_Bounds)) /= 1
            then return C.Invalid_Request; end if;
            return Decision;
         end;
      end;
   exception when others => return C.Invalid_Request;
      end;
   exception
      when others => return 255;
   end Decide_Raw_Metadata;
   end Authority_Glue;

   package Owner_Wire renames Worldline.Owner_Transitions_Wire;
   package Owner_Kernel renames Worldline.Owner_Transitions;
   package Owner_History renames Evaluation_History;
   package Owner_Request_Pointers is new System.Address_To_Access_Conversions (Owner_Wire.Raw_Request);
   package Owner_Row_Pointers is new System.Address_To_Access_Conversions (Owner_Wire.Raw_Row);
function Owner_ABI_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return (1);
      end;
   exception
      when others => return 0;
   end Owner_ABI_Version;
   function Owner_Layout (Kind, Field : Interfaces.Unsigned_8)
     return Interfaces.C.size_t is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      V1 : Owner_Wire.Raw_Identity;
      V2 : Owner_Wire.Raw_Cursor;
      V3 : Owner_Wire.Raw_Row;
      V4 : Owner_Wire.Raw_Grant;
      V5 : Owner_Wire.Raw_Request;
   begin
      case Kind is
         when 1 => case Field is
            when 0 => return Owner_Wire.Raw_Identity'Object_Size / System.Storage_Unit;
            when 1 => return Owner_Wire.Raw_Identity'Alignment;
            when 2 => return V1.Present'Position;
            when 3 => return V1.First'Position;
            when 4 => return V1.Length'Position;
            when others => return Interfaces.C.size_t'Last;
         end case;
         when 2 => case Field is
            when 0 => return Owner_Wire.Raw_Cursor'Object_Size / System.Storage_Unit;
            when 1 => return Owner_Wire.Raw_Cursor'Alignment;
            when 2 => return V2.Present'Position;
            when 3 => return V2.Sequence'Position;
            when 4 => return V2.Run'Position;
            when others => return Interfaces.C.size_t'Last;
         end case;
         when 3 => case Field is
            when 0 => return Owner_Wire.Raw_Row'Object_Size / System.Storage_Unit;
            when 1 => return Owner_Wire.Raw_Row'Alignment;
            when 2 => return V3.Subject'Position;
            when 3 => return V3.Content'Position;
            when 4 => return V3.Requirement'Position;
            when 5 => return V3.Run'Position;
            when 6 => return V3.Sequence'Position;
            when 7 => return V3.State'Position;
            when 8 => return V3.Outcome'Position;
            when others => return Interfaces.C.size_t'Last;
         end case;
         when 4 => case Field is
            when 0 => return Owner_Wire.Raw_Grant'Object_Size / System.Storage_Unit;
            when 1 => return Owner_Wire.Raw_Grant'Alignment;
            when 2 => return V4.Action'Position;
            when 3 => return V4.State'Position;
            when 4 => return V4.Grant'Position;
            when 5 => return V4.Use_Id'Position;
            when 6 => return V4.Issuer'Position;
            when 7 => return V4.Principal'Position;
            when 8 => return V4.Subject'Position;
            when 9 => return V4.Content'Position;
            when 10 => return V4.Transaction'Position;
            when 11 => return V4.Current_Requirement'Position;
            when 12 => return V4.Expected_Requirement'Position;
            when 13 => return V4.Reason'Position;
            when 14 => return V4.Issued_Grant'Position;
            when 15 => return V4.Reserved_Grant'Position;
            when 16 => return V4.Reserved_Use'Position;
            when 17 => return V4.Failed_Run'Position;
            when 18 => return V4.Prior_Head'Position;
            when 19 => return V4.Next_Run'Position;
            when 20 => return V4.Epoch'Position;
            when others => return Interfaces.C.size_t'Last;
         end case;
         when 5 => case Field is
            when 0 => return Owner_Wire.Raw_Request'Object_Size / System.Storage_Unit;
            when 1 => return Owner_Wire.Raw_Request'Alignment;
            when 2 => return V5.Action'Position;
            when 3 => return V5.Peer'Position;
            when 4 => return V5.Owner'Position;
            when 5 => return V5.Trusted_Issuer'Position;
            when 6 => return V5.Subject'Position;
            when 7 => return V5.Content'Position;
            when 8 => return V5.Transaction'Position;
            when 9 => return V5.Current_Requirement'Position;
            when 10 => return V5.Resulting_Requirement'Position;
            when 11 => return V5.Current_Head'Position;
            when 12 => return V5.Attempt'Position;
            when 13 => return V5.Current_Epoch'Position;
            when 14 => return V5.Grant'Position;
            when others => return Interfaces.C.size_t'Last;
         end case;
         when others => return Interfaces.C.size_t'Last;
      end case;
      end;
   exception
      when others => return Interfaces.C.size_t'Last;
   end Owner_Layout;
   function Owner_Extent
     (Address : System.Address; Length, Alignment : Interfaces.C.size_t)
     return Boolean is
     (Alignment > 0 and then Length <= Interfaces.C.size_t (System.Storage_Elements.Storage_Offset'Last)
      and then (Length = 0 or else
        (Address /= System.Null_Address and then
         System.Storage_Elements.To_Integer (Address) mod
           System.Storage_Elements.Integer_Address (Alignment) = 0 and then
         System.Storage_Elements.Integer_Address (Length - 1) <=
           System.Storage_Elements.Integer_Address'Last - System.Storage_Elements.To_Integer (Address))));
   function Owner_Authorize
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      History : System.Address; Row_Count : Interfaces.C.size_t;
      Final_Present : Interfaces.Unsigned_8; Final_Row, Request, Output : System.Address)
     return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      use System.Storage_Elements;
      use type Owner_History.Byte_Count;
      Stride : constant Interfaces.C.size_t := Owner_Wire.Raw_Row'Object_Size / System.Storage_Unit;
   begin
      if Data_Length > Interfaces.C.size_t (Owner_History.Byte_Count'Last)
        or else Row_Count > Interfaces.C.size_t (Owner_History.Byte_Count'Last)
        or else Row_Count > Interfaces.C.size_t (Storage_Offset'Last) / Stride
        or else Final_Present > 1
        or else not Owner_Extent (Data, Data_Length, 1)
        or else not Owner_Extent (History, Row_Count * Stride, Owner_Wire.Raw_Row'Alignment)
        or else (Final_Present = 1 and then
          not Owner_Extent (Final_Row, Stride, Owner_Wire.Raw_Row'Alignment))
        or else not Owner_Extent (Request, Owner_Wire.Raw_Request'Object_Size / System.Storage_Unit, Owner_Wire.Raw_Request'Alignment)
        or else not Owner_Extent (Output, Interfaces.Unsigned_8'Object_Size / System.Storage_Unit, Interfaces.Unsigned_8'Alignment)
      then return Error_Invalid_Argument;
      end if;
      declare
         Raw : constant Owner_Wire.Raw_Request := Owner_Request_Pointers.To_Pointer (Request).all;
         A : Owner_History.Byte_Array (1 .. Owner_History.Byte_Count (Data_Length));
         H : Owner_Wire.Raw_Rows (1 .. Owner_History.Byte_Count (Row_Count));
         Absent : constant Owner_Wire.Raw_Identity := (Present => 0, First => 0, Length => 0);
         F : Owner_Wire.Raw_Row := (Subject => Absent, Content => Absent,
           Requirement => Absent, Run => Absent, Sequence => Absent,
           State => Owner_History.Lifecycle'Pos (Owner_History.Pending),
           Outcome => Owner_History.Verdict'Pos (Owner_History.No_Verdict));
      begin
         for I in A'Range loop A (I) := Get_Byte (Data, Storage_Offset (I - 1)); end loop;
         for I in H'Range loop
            H (I) := Owner_Row_Pointers.To_Pointer
              (History + Storage_Offset (Interfaces.C.size_t (I - 1) * Stride)).all;
         end loop;
         if Final_Present = 1 then F := Owner_Row_Pointers.To_Pointer (Final_Row).all; end if;
         declare
            Result : constant Owner_Kernel.Decision := Owner_Wire.Decide (A, H, F, Final_Present, Raw);
         begin
            --  Complete input has been owned before output, even with aliases.
            Put_Byte (Output, 0, Interfaces.Unsigned_8 (Owner_Kernel.Decision'Pos (Result)));
         end;
      end;
      return Error_OK;
   exception when others => return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end Owner_Authorize;
   package Retry_Wire renames Worldline.Owner_Retry_Audit_Wire;
   package Retry_Kernel renames Worldline.Owner_Retry_Audit;
   package Join_Wire renames Worldline.Owner_Conjunction_Wire;
   package Join_Kernel renames Worldline.Owner_Conjunction;
   package Audit_Pointers is new System.Address_To_Access_Conversions (Retry_Wire.Raw_Audit);
   package Scope_Pointers is new System.Address_To_Access_Conversions (Join_Wire.Raw_Scope);
   package Collapse_Pointers is new System.Address_To_Access_Conversions (Worldline.Collapse_Wire.Raw_Request);
   package Requirement_Pointers is new System.Address_To_Access_Conversions (Worldline.Collapse_Wire.Raw_Optional_Hash);
function Owner_Audit_ABI return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return (1);
      end;
   exception
      when others => return 0;
   end Owner_Audit_ABI;
   function Owner_Audit_Layout (Kind, Field : Interfaces.Unsigned_8) return Interfaces.C.size_t is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      R : Retry_Wire.Raw_Audit;
      S : Join_Wire.Raw_Scope;
   begin
      case Kind is
         when 6 => case Field is
            when 0 => return Retry_Wire.Raw_Audit'Object_Size / System.Storage_Unit;
            when 1 => return Retry_Wire.Raw_Audit'Alignment;
            when 2 => return R.Before_Request'Position;
            when 3 => return R.Consumed'Position;
            when 4 => return R.Issued_Event'Position;
            when 5 => return R.Reserved_Event'Position;
            when 6 => return R.Consumed_Event'Position;
            when 7 => return R.Consumed_Issue'Position;
            when 8 => return R.Consumed_Reservation'Position;
            when 9 => return R.Current_Head'Position;
            when 10 => return R.Prepared_Evidence'Position;
            when 11 => return R.Current_Epoch'Position;
            when others => return Interfaces.C.size_t'Last; end case;
         when 7 => case Field is
            when 0 => return Join_Wire.Raw_Scope'Object_Size / System.Storage_Unit;
            when 1 => return Join_Wire.Raw_Scope'Alignment;
            when 2 => return S.Subject'Position;
            when 3 => return S.Content'Position;
            when 4 => return S.Transaction'Position;
            when others => return Interfaces.C.size_t'Last; end case;
         when others => return Owner_Layout (Kind, Field);
      end case;
      end;
   exception
      when others => return Interfaces.C.size_t'Last;
   end Owner_Audit_Layout;
   function Owner_Audit_Decide
     (Mode : Interfaces.Unsigned_8; Data : System.Address; Data_Length : Interfaces.C.size_t;
      Before : System.Address; Before_Count : Interfaces.C.size_t;
      After : System.Address; After_Count : Interfaces.C.size_t;
      Before_Present : Interfaces.Unsigned_8; Before_Final : System.Address;
      After_Present : Interfaces.Unsigned_8; After_Final : System.Address;
      Audit, Original, Scope, Resulting : System.Address;
      Adopt_Present : Interfaces.Unsigned_8; Adopt, Output : System.Address) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      use System.Storage_Elements;
      use type Owner_History.Byte_Count;
      Stride : constant Interfaces.C.size_t := Owner_Wire.Raw_Row'Object_Size / System.Storage_Unit;
   begin
      if Mode > 3 or else Data_Length > Interfaces.C.size_t (Owner_History.Byte_Count'Last)
        or else Before_Count > Interfaces.C.size_t (Owner_History.Byte_Count'Last)
        or else After_Count > Interfaces.C.size_t (Owner_History.Byte_Count'Last)
        or else Before_Count > Interfaces.C.size_t (Storage_Offset'Last) / Stride
        or else After_Count > Interfaces.C.size_t (Storage_Offset'Last) / Stride
        or else Before_Present > 1 or else After_Present > 1 or else Adopt_Present > 1
        or else not Owner_Extent (Data, Data_Length, 1)
        or else not Owner_Extent (Before, Before_Count * Stride, Owner_Wire.Raw_Row'Alignment)
        or else not Owner_Extent (After, After_Count * Stride, Owner_Wire.Raw_Row'Alignment)
        or else (Before_Present = 1 and then not Owner_Extent (Before_Final, Stride, Owner_Wire.Raw_Row'Alignment))
        or else (After_Present = 1 and then not Owner_Extent (After_Final, Stride, Owner_Wire.Raw_Row'Alignment))
        or else (Mode /= 2 and then not Owner_Extent (Audit, Retry_Wire.Raw_Audit'Object_Size / System.Storage_Unit, Retry_Wire.Raw_Audit'Alignment))
        or else (Mode /= 0 and then
          (not Owner_Extent (Original, Worldline.Collapse_Wire.Raw_Request'Object_Size / System.Storage_Unit, Worldline.Collapse_Wire.Raw_Request'Alignment)
           or else not Owner_Extent (Scope, Join_Wire.Raw_Scope'Object_Size / System.Storage_Unit, Join_Wire.Raw_Scope'Alignment)))
        or else (Mode >= 2 and then not Owner_Extent (Resulting, Worldline.Collapse_Wire.Raw_Optional_Hash'Object_Size / System.Storage_Unit, Worldline.Collapse_Wire.Raw_Optional_Hash'Alignment))
        or else (Mode = 2 and then Adopt_Present = 1 and then not Owner_Extent (Adopt, Owner_Wire.Raw_Request'Object_Size / System.Storage_Unit, Owner_Wire.Raw_Request'Alignment))
        or else (Mode >= 2 and then (After_Count /= 0 or else After_Present /= 0))
        or else (Mode /= 2 and then Adopt_Present /= 0)
        or else not Owner_Extent (Output, Interfaces.Unsigned_8'Object_Size / System.Storage_Unit, Interfaces.Unsigned_8'Alignment)
      then return Error_Invalid_Argument; end if;
      declare
         A : Owner_History.Byte_Array (1 .. Owner_History.Byte_Count (Data_Length));
         B : Owner_Wire.Raw_Rows (1 .. Owner_History.Byte_Count (Before_Count));
         H : Owner_Wire.Raw_Rows (1 .. Owner_History.Byte_Count (After_Count));
         Zero : constant Owner_Wire.Raw_Identity := (0, 0, 0);
         BF : Owner_Wire.Raw_Row := (Zero, Zero, Zero, Zero, Zero, 0, 0);
         AF : Owner_Wire.Raw_Row := BF;
         Code : Interfaces.Unsigned_8;
      begin
         for J in A'Range loop A (J) := Get_Byte (Data, Storage_Offset (J - 1)); end loop;
         for J in B'Range loop B (J) := Owner_Row_Pointers.To_Pointer (Before + Storage_Offset (Interfaces.C.size_t (J - 1) * Stride)).all; end loop;
         for J in H'Range loop H (J) := Owner_Row_Pointers.To_Pointer (After + Storage_Offset (Interfaces.C.size_t (J - 1) * Stride)).all; end loop;
         if Before_Present = 1 then BF := Owner_Row_Pointers.To_Pointer (Before_Final).all; end if;
         if After_Present = 1 then AF := Owner_Row_Pointers.To_Pointer (After_Final).all; end if;
         if Mode = 0 then
            declare Q : constant Retry_Wire.Raw_Audit := Audit_Pointers.To_Pointer (Audit).all;
            begin Code := Interfaces.Unsigned_8 (Retry_Kernel.Decision'Pos
              (Retry_Wire.Decide (A, B, H, BF, AF, Before_Present, After_Present, Q))); end;
         elsif Mode = 1 then
            declare
               Q : constant Retry_Wire.Raw_Audit := Audit_Pointers.To_Pointer (Audit).all;
               C : constant Worldline.Collapse_Wire.Raw_Request := Collapse_Pointers.To_Pointer (Original).all;
               S : constant Join_Wire.Raw_Scope := Scope_Pointers.To_Pointer (Scope).all;
            begin Code := Interfaces.Unsigned_8 (Join_Kernel.Decision'Pos
              (Join_Wire.Authorize_Retry (A, B, H, BF, AF, Before_Present, After_Present, C, S, Q))); end;
         elsif Mode = 3 then
            declare
               Q : constant Retry_Wire.Raw_Audit := Audit_Pointers.To_Pointer (Audit).all;
               C : constant Worldline.Collapse_Wire.Raw_Request := Collapse_Pointers.To_Pointer (Original).all;
               S : constant Join_Wire.Raw_Scope := Scope_Pointers.To_Pointer (Scope).all;
               R : constant Worldline.Collapse_Wire.Raw_Optional_Hash := Requirement_Pointers.To_Pointer (Resulting).all;
            begin Code := Interfaces.Unsigned_8 (Join_Kernel.Decision'Pos
              (Join_Wire.Authorize_Adopt_Receipt (A, B, BF, Before_Present, C, R, S, Q))); end;
         else
            declare
               C : constant Worldline.Collapse_Wire.Raw_Request := Collapse_Pointers.To_Pointer (Original).all;
               S : constant Join_Wire.Raw_Scope := Scope_Pointers.To_Pointer (Scope).all;
               R : constant Worldline.Collapse_Wire.Raw_Optional_Hash := Requirement_Pointers.To_Pointer (Resulting).all;
               G : Owner_Wire.Raw_Request;
            begin
               if Adopt_Present = 1 then G := Owner_Request_Pointers.To_Pointer (Adopt).all;
               else G.Action := 0; end if;
               -- In the absent branch no uninitialized field is consulted:
               -- initialize the complete wire through a zeroed owned record below.
               if Adopt_Present = 0 then
                  declare
                     Empty_Cursor : constant Owner_Wire.Raw_Cursor := (0, Zero, Zero);
                     Empty_Grant : constant Owner_Wire.Raw_Grant :=
                       (Action => 0, State => 0, Grant => Zero, Use_Id => Zero,
                        Issuer => Zero, Principal => Zero, Subject => Zero, Content => Zero,
                        Transaction => Zero, Current_Requirement => Zero, Expected_Requirement => Zero,
                        Reason => Zero, Issued_Grant => Zero, Reserved_Grant => Zero, Reserved_Use => Zero,
                        Failed_Run => Empty_Cursor, Prior_Head => Empty_Cursor, Next_Run => Empty_Cursor, Epoch => Zero);
                  begin G := (0, Zero, Zero, Zero, Zero, Zero, Zero, Zero, Zero,
                    Empty_Cursor, Empty_Cursor, Zero, Empty_Grant); end;
               end if;
               Code := Interfaces.Unsigned_8 (Join_Kernel.Decision'Pos
                 (Join_Wire.Authorize_Checkpoint (A, B, BF, Before_Present, C, R, S, Adopt_Present, G)));
            end;
         end if;
         -- All consulted original bytes/rows/records owned before output aliases.
         Put_Byte (Output, 0, Code);
      end;
      return Error_OK;
   exception when others => return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end Owner_Audit_Decide;
   package RC renames Worldline.Retained_Custody_Chain;
   type Retained_Span is record
      First, Length : Interfaces.Integer_64;
   end record with Convention => C;
   type Retained_Output is record
      Status : Interfaces.C.int;
      Failing_Row : Interfaces.Integer_64;
      Origin, Head : RC.SHA.Digest;
   end record with Convention => C;
   package Retained_Span_Pointers is new System.Address_To_Access_Conversions (Retained_Span);
   package Retained_Output_Pointers is new System.Address_To_Access_Conversions (Retained_Output);
function Retained_Chain_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return (1);
      end;
   exception
      when others => return 0;
   end Retained_Chain_Version;
   function Retained_Chain_Layout (Kind, Field : Interfaces.Unsigned_8)
      return Interfaces.C.size_t is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      S : Retained_Span;
      R : Retained_Output;
   begin
      case Kind is
         when 1 =>
            case Field is
               when 0 => return Retained_Span'Object_Size / System.Storage_Unit;
               when 1 => return Retained_Span'Alignment;
               when 2 => return S.First'Position;
               when 3 => return S.Length'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 2 =>
            case Field is
               when 0 => return Retained_Output'Object_Size / System.Storage_Unit;
               when 1 => return Retained_Output'Alignment;
               when 2 => return R.Status'Position;
               when 3 => return R.Failing_Row'Position;
               when 4 => return R.Origin'Position;
               when 5 => return R.Head'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when others => return Interfaces.C.size_t'Last;
      end case;
      end;
   exception
      when others => return Interfaces.C.size_t'Last;
   end Retained_Chain_Layout;
   function Retained_Chain_Verify
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Spans : System.Address; Span_Count, Genesis_Count, Event_Count, Head_Count : Interfaces.C.size_t;
      Output : System.Address; Output_Size : Interfaces.C.size_t) return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      use System.Storage_Elements;
      use type RC.E.Count;
      use type Interfaces.Integer_64;
      Stride : constant Interfaces.C.size_t := Retained_Span'Object_Size / System.Storage_Unit;
      Expected : Interfaces.C.size_t := 3;
   begin
      -- Counts bound owned host storage only, never numeric quantities or key values.
      if Genesis_Count > (Interfaces.C.size_t'Last - Expected) / 2 then return Error_Invalid_Argument; end if;
      Expected := Expected + Genesis_Count * 2;
      if Event_Count > (Interfaces.C.size_t'Last - Expected) / 7 then return Error_Invalid_Argument; end if;
      Expected := Expected + Event_Count * 7;
      if Head_Count > (Interfaces.C.size_t'Last - Expected) / 3 then return Error_Invalid_Argument; end if;
      Expected := Expected + Head_Count * 3;
      if Span_Count /= Expected or else
        Data_Length > Interfaces.C.size_t (RC.E.Count'Last) or else
        Span_Count > Interfaces.C.size_t (RC.E.Count'Last) or else
        Span_Count > Interfaces.C.size_t (Storage_Offset'Last) / Stride or else
        not Owner_Extent (Data, Data_Length, 1) or else
        not Owner_Extent (Spans, Span_Count * Stride, Retained_Span'Alignment) or else
        Output_Size /= Retained_Output'Object_Size / System.Storage_Unit or else
        not Owner_Extent (Output, Output_Size, Retained_Output'Alignment)
      then return Error_Invalid_Argument; end if;
      declare
         A : RC.E.Bytes (1 .. RC.E.Count (Data_Length));
         type Span_Array is array (RC.E.Q.Byte_Index range <>) of RC.E.Span;
         Owned : Span_Array (1 .. RC.E.Count (Span_Count));
         G : RC.Genesis_Rows (1 .. RC.E.Count (Genesis_Count));
         E : RC.Event_Rows (1 .. RC.E.Count (Event_Count));
         H : RC.Head_Rows (1 .. RC.E.Count (Head_Count));
         Cursor : RC.E.Count := 3;
         function Take return RC.E.Span is
         begin
            Cursor := Cursor + 1;
            return Owned (Cursor);
         end Take;
      begin
         for I in A'Range loop A (I) := Get_Byte (Data, Storage_Offset (I - 1)); end loop;
         for I in Owned'Range loop
            declare
               Raw : constant Retained_Span := Retained_Span_Pointers.To_Pointer
                 (Spans + Storage_Offset (Interfaces.C.size_t (I - 1) * Stride)).all;
            begin
               if Raw.First < 1 or else Raw.Length < 0 then return Error_Invalid_Argument; end if;
               Owned (I) := (RC.E.Q.Byte_Index (Raw.First), RC.E.Count (Raw.Length));
               if not RC.E.C.P.Valid (A, Owned (I)) then return Error_Invalid_Argument; end if;
            end;
         end loop;
         -- Sequential assignments preserve declared field order; no evaluation-
         -- order dependence from side-effecting function calls in aggregates.
         for I in G'Range loop G (I).Name := Take; G (I).Value := Take; end loop;
         for I in E'Range loop
            E (I).Event_Id := Take; E (I).Previous := Take;
            E (I).Operation := Take; E (I).Kind := Take;
            E (I).Record_Archive := Take; E (I).Mac := Take; E (I).Base_Archive := Take;
         end loop;
         for I in H'Range loop
            H (I).Name := Take; H (I).Event_Id := Take; H (I).Mac := Take;
         end loop;
         declare
            Value : constant RC.Result := RC.Verify (A, Owned (1), Owned (2), Owned (3), G, E, H);
            Result : constant Retained_Output :=
              (Status => RC.Status'Pos (Value.State),
               Failing_Row => Interfaces.Integer_64 (Value.Failing_Row),
               Origin => Value.Origin, Head => Value.Head);
         begin
            -- All input bytes/spans/rows owned before writing potentially aliased output.
            Retained_Output_Pointers.To_Pointer (Output).all := Result;
         end;
      end;
      return Error_OK;
   exception when others => return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end Retained_Chain_Verify;

   -- Finite PREPARED value transport only. Not authenticated X4/X5/startup.
   package PW renames Worldline.Custody_V2_Prepared_Wire;
   package PM renames PW.M;
   package PQ renames PW.Q;
   type Prepared_Root is record
      Generation : PW.W.Raw_Quantity;
      Operation : PW.W.Raw_Quantity;
      Phase : Interfaces.Unsigned_8;
      Before_Unknown : Interfaces.Unsigned_8;
      Owners_Open : Interfaces.Unsigned_8;
      Abort_Kind : Interfaces.Unsigned_8;
      Launched : Interfaces.Unsigned_8;
      NS : Interfaces.Unsigned_8;
      Outer : Interfaces.Unsigned_8;
      Raw : Interfaces.Unsigned_8;
      Witness : Interfaces.Unsigned_8;
      Settled : Interfaces.Unsigned_8;
      Released_Unlaunched : Interfaces.Unsigned_8;
      Unknown_Cause : PW.CW.Raw_Digest;
      Reattach_Epoch : PW.W.Raw_Quantity;
      Head : PW.CW.Raw_Hash;
   end record with Convention => C;
   type Prepared_Event is record
      Event_Id : Retained_Span;
      Previous : Retained_Span;
      Generation : Retained_Span;
      Operation : Retained_Span;
      Subject_Kind : Retained_Span;
      Subject : Retained_Span;
      Subgeneration : Retained_Span;
      Kind : Retained_Span;
      Actor : Retained_Span;
      Record_Archive : Retained_Span;
      Base_Archive : Retained_Span;
      Mac : Retained_Span;
   end record with Convention => C;
   type Prepared_Output is record
      Status : Interfaces.C.int;
      After_State : Prepared_Root;
   end record with Convention => C;
function Prepared_Step_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return (1);
      end;
   exception
      when others => return 0;
   end Prepared_Step_Version;
   function Prepared_Step_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.size_t is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      V1 : Retained_Span;
      V2 : Prepared_Root;
      V3 : Prepared_Event;
      V4 : Prepared_Output;
      V5 : PW.W.Raw_Quantity;
      V6 : PW.W.Raw_UID;
      V7 : PW.W.Raw_Binding;
      V8 : PW.W.Raw_Grant;
      V9 : PW.W.Raw_Use;
      V10 : PW.W.Raw_Evidence;
      V11 : PW.W.Raw_Input;
      V12 : PW.CW.Raw_Digest;
      V13 : PW.CW.Raw_Row;
      V14 : PW.W.RW.Raw_Epoch;
      V15 : PW.W.RW.Raw_Digest;
      V16 : PW.W.RW.Raw_Binding;
      V17 : PW.W.RW.Raw_Native;
      V18 : PW.W.RW.Raw_Request;
   begin
      case Kind is
         when 1 =>
            case Field is
               when 0 => return Retained_Span'Object_Size / System.Storage_Unit;
               when 1 => return Retained_Span'Alignment;
               when 2 => return V1.First'Position;
               when 3 => return V1.Length'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 2 =>
            case Field is
               when 0 => return Prepared_Root'Object_Size / System.Storage_Unit;
               when 1 => return Prepared_Root'Alignment;
               when 2 => return V2.Generation'Position;
               when 3 => return V2.Operation'Position;
               when 4 => return V2.Phase'Position;
               when 5 => return V2.Before_Unknown'Position;
               when 6 => return V2.Owners_Open'Position;
               when 7 => return V2.Abort_Kind'Position;
               when 8 => return V2.Launched'Position;
               when 9 => return V2.NS'Position;
               when 10 => return V2.Outer'Position;
               when 11 => return V2.Raw'Position;
               when 12 => return V2.Witness'Position;
               when 13 => return V2.Settled'Position;
               when 14 => return V2.Released_Unlaunched'Position;
               when 15 => return V2.Unknown_Cause'Position;
               when 16 => return V2.Reattach_Epoch'Position;
               when 17 => return V2.Head'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 3 =>
            case Field is
               when 0 => return Prepared_Event'Object_Size / System.Storage_Unit;
               when 1 => return Prepared_Event'Alignment;
               when 2 => return V3.Event_Id'Position;
               when 3 => return V3.Previous'Position;
               when 4 => return V3.Generation'Position;
               when 5 => return V3.Operation'Position;
               when 6 => return V3.Subject_Kind'Position;
               when 7 => return V3.Subject'Position;
               when 8 => return V3.Subgeneration'Position;
               when 9 => return V3.Kind'Position;
               when 10 => return V3.Actor'Position;
               when 11 => return V3.Record_Archive'Position;
               when 12 => return V3.Base_Archive'Position;
               when 13 => return V3.Mac'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 4 =>
            case Field is
               when 0 => return Prepared_Output'Object_Size / System.Storage_Unit;
               when 1 => return Prepared_Output'Alignment;
               when 2 => return V4.Status'Position;
               when 3 => return V4.After_State'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 5 =>
            case Field is
               when 0 => return PW.W.Raw_Quantity'Object_Size / System.Storage_Unit;
               when 1 => return PW.W.Raw_Quantity'Alignment;
               when 2 => return V5.Present'Position;
               when 3 => return V5.Negative'Position;
               when 4 => return V5.First'Position;
               when 5 => return V5.Length'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 6 =>
            case Field is
               when 0 => return PW.W.Raw_UID'Object_Size / System.Storage_Unit;
               when 1 => return PW.W.Raw_UID'Alignment;
               when 2 => return V6.Present'Position;
               when 3 => return V6.Value'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 7 =>
            case Field is
               when 0 => return PW.W.Raw_Binding'Object_Size / System.Storage_Unit;
               when 1 => return PW.W.Raw_Binding'Alignment;
               when 2 => return V7.Action'Position;
               when 3 => return V7.Id'Position;
               when 4 => return V7.Peer'Position;
               when 5 => return V7.Preparer'Position;
               when 6 => return V7.Owner'Position;
               when 7 => return V7.Target_Owner'Position;
               when 8 => return V7.Policy_Epoch'Position;
               when 9 => return V7.Resource_Epoch'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 8 =>
            case Field is
               when 0 => return PW.W.Raw_Grant'Object_Size / System.Storage_Unit;
               when 1 => return PW.W.Raw_Grant'Alignment;
               when 2 => return V8.Id'Position;
               when 3 => return V8.Parent'Position;
               when 4 => return V8.Issuer'Position;
               when 5 => return V8.Instance'Position;
               when 6 => return V8.Root_Set'Position;
               when 7 => return V8.Policy'Position;
               when 8 => return V8.Subject'Position;
               when 9 => return V8.Owner'Position;
               when 10 => return V8.Allowed'Position;
               when 11 => return V8.State'Position;
               when 12 => return V8.Epoch'Position;
               when 13 => return V8.Ceiling'Position;
               when 14 => return V8.Issued_At'Position;
               when 15 => return V8.Expires_At'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 9 =>
            case Field is
               when 0 => return PW.W.Raw_Use'Object_Size / System.Storage_Unit;
               when 1 => return PW.W.Raw_Use'Alignment;
               when 2 => return V9.Bound'Position;
               when 3 => return V9.State'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 10 =>
            case Field is
               when 0 => return PW.W.Raw_Evidence'Object_Size / System.Storage_Unit;
               when 1 => return PW.W.Raw_Evidence'Alignment;
               when 2 => return V10.Effect_Binding'Position;
               when 3 => return V10.Actual_Receipt_Root'Position;
               when 4 => return V10.Actual_Causal_Root'Position;
               when 5 => return V10.No_Effect_Binding'Position;
               when 6 => return V10.Owner_Resolution'Position;
               when 7 => return V10.Quarantine_Head'Position;
               when 8 => return V10.Witnessed_Receipt_Head'Position;
               when 9 => return V10.Witnessed_Causal_Head'Position;
               when 10 => return V10.Recovery'Position;
               when 11 => return V10.Original_Use'Position;
               when 12 => return V10.Effect_Material_First'Position;
               when 13 => return V10.Effect_Material_Length'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 11 =>
            case Field is
               when 0 => return PW.W.Raw_Input'Object_Size / System.Storage_Unit;
               when 1 => return PW.W.Raw_Input'Alignment;
               when 2 => return V11.Schema'Position;
               when 3 => return V11.Mode'Position;
               when 4 => return V11.Bound'Position;
               when 5 => return V11.Now'Position;
               when 6 => return V11.Facts'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 12 =>
            case Field is
               when 0 => return PW.CW.Raw_Digest'Object_Size / System.Storage_Unit;
               when 1 => return PW.CW.Raw_Digest'Alignment;
               when 2 => return V12.Present'Position;
               when 3 => return V12.Value'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 13 =>
            case Field is
               when 0 => return PW.CW.Raw_Row'Object_Size / System.Storage_Unit;
               when 1 => return PW.CW.Raw_Row'Alignment;
               when 2 => return V13.Previous'Position;
               when 3 => return V13.Actual_Payload_Root'Position;
               when 4 => return V13.Stored_Payload_Root'Position;
               when 5 => return V13.Stored_Head'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 14 =>
            case Field is
               when 0 => return PW.W.RW.Raw_Epoch'Object_Size / System.Storage_Unit;
               when 1 => return PW.W.RW.Raw_Epoch'Alignment;
               when 2 => return V14.Present'Position;
               when 3 => return V14.Negative'Position;
               when 4 => return V14.First'Position;
               when 5 => return V14.Length'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 15 =>
            case Field is
               when 0 => return PW.W.RW.Raw_Digest'Object_Size / System.Storage_Unit;
               when 1 => return PW.W.RW.Raw_Digest'Alignment;
               when 2 => return V15.Present'Position;
               when 3 => return V15.Value'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 16 =>
            case Field is
               when 0 => return PW.W.RW.Raw_Binding'Object_Size / System.Storage_Unit;
               when 1 => return PW.W.RW.Raw_Binding'Alignment;
               when 2 => return V16.Mode'Position;
               when 3 => return V16.Operation'Position;
               when 4 => return V16.Transaction'Position;
               when 5 => return V16.Capability'Position;
               when 6 => return V16.Universe_Head'Position;
               when 7 => return V16.Instance'Position;
               when 8 => return V16.Subject'Position;
               when 9 => return V16.Staged_Root'Position;
               when 10 => return V16.Current_Requirement'Position;
               when 11 => return V16.Resulting_Requirement'Position;
               when 12 => return V16.Requester'Position;
               when 13 => return V16.Grant_Use'Position;
               when 14 => return V16.Policy_Identity'Position;
               when 15 => return V16.Selected_Evaluation'Position;
               when 16 => return V16.History_Head'Position;
               when 17 => return V16.Reservation'Position;
               when 18 => return V16.Host'Position;
               when 19 => return V16.Before_Prime'Position;
               when 20 => return V16.Before_Root'Position;
               when 21 => return V16.Before_Mapping'Position;
               when 22 => return V16.Staged_Mapping'Position;
               when 23 => return V16.Input_Snapshot'Position;
               when 24 => return V16.Kernel_Build'Position;
               when 25 => return V16.Kernel_Library'Position;
               when 26 => return V16.Kernel_Mapping'Position;
               when 27 => return V16.Issuer_Head'Position;
               when 28 => return V16.Receipt_Head'Position;
               when 29 => return V16.Causal_Head'Position;
               when 30 => return V16.Policy_Epoch'Position;
               when 31 => return V16.Resource_Epoch'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 17 =>
            case Field is
               when 0 => return PW.W.RW.Raw_Native'Object_Size / System.Storage_Unit;
               when 1 => return PW.W.RW.Raw_Native'Alignment;
               when 2 => return V17.Live_Mapping'Position;
               when 3 => return V17.Live_Root'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 18 =>
            case Field is
               when 0 => return PW.W.RW.Raw_Request'Object_Size / System.Storage_Unit;
               when 1 => return PW.W.RW.Raw_Request'Alignment;
               when 2 => return V18.Schema_Version'Position;
               when 3 => return V18.State'Position;
               when 4 => return V18.Fresh'Position;
               when 5 => return V18.Historical'Position;
               when 6 => return V18.Grant_Eligible'Position;
               when 7 => return V18.Issued_Binding'Position;
               when 8 => return V18.Recovered_Binding'Position;
               when 9 => return V18.Native'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when others => return Interfaces.C.size_t'Last;
      end case;
      end;
   exception
      when others => return Interfaces.C.size_t'Last;
   end Prepared_Step_Layout;
   package P_Root is new System.Address_To_Access_Conversions (Prepared_Root);
   package P_Event is new System.Address_To_Access_Conversions (Prepared_Event);
   package P_Input is new System.Address_To_Access_Conversions (PW.W.Raw_Input);
   package P_Grant is new System.Address_To_Access_Conversions (PW.W.Raw_Grant);
   package P_Use is new System.Address_To_Access_Conversions (PW.W.Raw_Use);
   package P_Row is new System.Address_To_Access_Conversions (PW.CW.Raw_Row);
   package P_Output is new System.Address_To_Access_Conversions (Prepared_Output);
   function Prepared_Quantity_Valid (Data : PQ.Byte_Array; V : PW.W.Raw_Quantity)
      return Boolean is
     (PW.W.Well_Formed (V) and then V.Present = 1
       and then PQ.Span_Valid (Data, PW.W.Decode (V).Value));
   function Prepared_Root_Valid (Data : PQ.Byte_Array; V : Prepared_Root) return Boolean is
     (Prepared_Quantity_Valid (Data, V.Generation)
      and then Prepared_Quantity_Valid (Data, V.Reattach_Epoch)
      and then PW.W.Well_Formed (V.Operation) and then V.Operation.Negative = 0
      and then (V.Operation.Present = 0 or else
        PQ.Span_Valid (Data, PW.W.Decode (V.Operation).Value))
      and then V.Phase <= PM.Root_Phase'Pos (PM.Root_Phase'Last)
      and then V.Before_Unknown <= PM.Root_Phase'Pos (PM.Root_Phase'Last)
      and then V.Abort_Kind <= PM.Abort_Class'Pos (PM.Abort_Class'Last)
      and then V.Owners_Open <= 1 and then V.Launched <= 1 and then V.NS <= 1
      and then V.Outer <= 1 and then V.Raw <= 1 and then V.Witness <= 1
      and then V.Settled <= 1 and then V.Released_Unlaunched <= 1
      and then PW.CW.Well_Formed (V.Unknown_Cause));
   function Prepared_Decode_Root (V : Prepared_Root) return PM.Root_State is
     (Generation => PW.W.Decode (V.Generation).Value,
      Operation => (if V.Operation.Present = 0 then (Present => False) else
        (Present => True, Value => (First => PQ.Byte_Index (V.Operation.First),
                                   Length => PQ.Byte_Count (V.Operation.Length)))),
      Phase => PM.Root_Phase'Val (V.Phase),
      Before_Unknown => PM.Root_Phase'Val (V.Before_Unknown),
      Owners_Open => V.Owners_Open = 1,
      Abort_Kind => PM.Abort_Class'Val (V.Abort_Kind),
      Physical => (Launched => V.Launched = 1, NS => V.NS = 1, Outer => V.Outer = 1,
        Raw => V.Raw = 1, Witness => V.Witness = 1, Settled => V.Settled = 1,
        Released_Unlaunched => V.Released_Unlaunched = 1),
      Unknown_Cause => (if V.Unknown_Cause.Present = 0 then (Present => False)
        else (Present => True, Value => Hash (V.Unknown_Cause.Value))),
      Reattach_Epoch => PW.W.Decode (V.Reattach_Epoch).Value, Head => Hash (V.Head));
   function Prepared_Encode_Quantity (V : PQ.Quantity) return PW.W.Raw_Quantity is
     (Present => 1, Negative => Boolean'Pos (V.Negative),
      First => Interfaces.Integer_64 (V.First), Length => Interfaces.Integer_64 (V.Length));
   function Prepared_Encode_Root (V : PM.Root_State) return Prepared_Root is
     (Generation => Prepared_Encode_Quantity (V.Generation),
      Operation => (if not V.Operation.Present then (0, 0, 1, 0) else
        (1, 0, Interfaces.Integer_64 (V.Operation.Value.First),
         Interfaces.Integer_64 (V.Operation.Value.Length))),
      Phase => PM.Root_Phase'Pos (V.Phase),
      Before_Unknown => PM.Root_Phase'Pos (V.Before_Unknown),
      Owners_Open => Boolean'Pos (V.Owners_Open), Abort_Kind => PM.Abort_Class'Pos (V.Abort_Kind),
      Launched => Boolean'Pos (V.Physical.Launched), NS => Boolean'Pos (V.Physical.NS),
      Outer => Boolean'Pos (V.Physical.Outer), Raw => Boolean'Pos (V.Physical.Raw),
      Witness => Boolean'Pos (V.Physical.Witness), Settled => Boolean'Pos (V.Physical.Settled),
      Released_Unlaunched => Boolean'Pos (V.Physical.Released_Unlaunched),
      Unknown_Cause => (if V.Unknown_Cause.Present then
        (1, PW.CW.Raw_Hash (V.Unknown_Cause.Value)) else (0, (others => 0))),
      Reattach_Epoch => Prepared_Encode_Quantity (V.Reattach_Epoch),
      Head => PW.CW.Raw_Hash (V.Head));
   function Prepared_Step_Decide
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Event, Root, Reserve, Intent : System.Address;
      Event_Size, Root_Size, Reserve_Size, Intent_Size : Interfaces.C.size_t;
      Reserve_Grants : System.Address; Reserve_Grants_Count, Reserve_Grants_Bytes : Interfaces.C.size_t;
      Intent_Grants : System.Address; Intent_Grants_Count, Intent_Grants_Bytes : Interfaces.C.size_t;
      Reserve_Uses : System.Address; Reserve_Uses_Count, Reserve_Uses_Bytes : Interfaces.C.size_t;
      Intent_Uses : System.Address; Intent_Uses_Count, Intent_Uses_Bytes : Interfaces.C.size_t;
      Reserve_Receipts : System.Address; Reserve_Receipts_Count, Reserve_Receipts_Bytes : Interfaces.C.size_t;
      Reserve_Events : System.Address; Reserve_Events_Count, Reserve_Events_Bytes : Interfaces.C.size_t;
      Intent_Receipts : System.Address; Intent_Receipts_Count, Intent_Receipts_Bytes : Interfaces.C.size_t;
      Intent_Events : System.Address; Intent_Events_Count, Intent_Events_Bytes : Interfaces.C.size_t;
      Output : System.Address; Output_Size : Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      use System.Storage_Elements;
      use type PQ.Byte_Count;
      use type Interfaces.Integer_64;
      Reserve_Grants_Stride : constant Interfaces.C.size_t := PW.W.Raw_Grant'Object_Size / System.Storage_Unit;
      Intent_Grants_Stride : constant Interfaces.C.size_t := PW.W.Raw_Grant'Object_Size / System.Storage_Unit;
      Reserve_Uses_Stride : constant Interfaces.C.size_t := PW.W.Raw_Use'Object_Size / System.Storage_Unit;
      Intent_Uses_Stride : constant Interfaces.C.size_t := PW.W.Raw_Use'Object_Size / System.Storage_Unit;
      Reserve_Receipts_Stride : constant Interfaces.C.size_t := PW.CW.Raw_Row'Object_Size / System.Storage_Unit;
      Reserve_Events_Stride : constant Interfaces.C.size_t := PW.CW.Raw_Row'Object_Size / System.Storage_Unit;
      Intent_Receipts_Stride : constant Interfaces.C.size_t := PW.CW.Raw_Row'Object_Size / System.Storage_Unit;
      Intent_Events_Stride : constant Interfaces.C.size_t := PW.CW.Raw_Row'Object_Size / System.Storage_Unit;
   begin
      if Data_Length > Interfaces.C.size_t (PQ.Byte_Count'Last) or else
        not Owner_Extent (Data, Data_Length, 1) then return Error_Invalid_Argument; end if;
      if Event_Size /= Prepared_Event'Object_Size / System.Storage_Unit or else
        not Owner_Extent (Event, Event_Size, Prepared_Event'Alignment) then return Error_Invalid_Argument; end if;
      if Root_Size /= Prepared_Root'Object_Size / System.Storage_Unit or else
        not Owner_Extent (Root, Root_Size, Prepared_Root'Alignment) then return Error_Invalid_Argument; end if;
      if Reserve_Size /= PW.W.Raw_Input'Object_Size / System.Storage_Unit or else
        not Owner_Extent (Reserve, Reserve_Size, PW.W.Raw_Input'Alignment) then return Error_Invalid_Argument; end if;
      if Intent_Size /= PW.W.Raw_Input'Object_Size / System.Storage_Unit or else
        not Owner_Extent (Intent, Intent_Size, PW.W.Raw_Input'Alignment) then return Error_Invalid_Argument; end if;
      if Output_Size /= Prepared_Output'Object_Size / System.Storage_Unit or else
        not Owner_Extent (Output, Output_Size, Prepared_Output'Alignment) then return Error_Invalid_Argument; end if;
      if Reserve_Grants_Count > Interfaces.C.size_t (PQ.Byte_Count'Last) or else
        Reserve_Grants_Count > Interfaces.C.size_t (Storage_Offset'Last) / Reserve_Grants_Stride or else
        Reserve_Grants_Bytes /= Reserve_Grants_Count * Reserve_Grants_Stride or else
        not Owner_Extent (Reserve_Grants, Reserve_Grants_Bytes, PW.W.Raw_Grant'Alignment) then return Error_Invalid_Argument; end if;
      if Intent_Grants_Count > Interfaces.C.size_t (PQ.Byte_Count'Last) or else
        Intent_Grants_Count > Interfaces.C.size_t (Storage_Offset'Last) / Intent_Grants_Stride or else
        Intent_Grants_Bytes /= Intent_Grants_Count * Intent_Grants_Stride or else
        not Owner_Extent (Intent_Grants, Intent_Grants_Bytes, PW.W.Raw_Grant'Alignment) then return Error_Invalid_Argument; end if;
      if Reserve_Uses_Count > Interfaces.C.size_t (PQ.Byte_Count'Last) or else
        Reserve_Uses_Count > Interfaces.C.size_t (Storage_Offset'Last) / Reserve_Uses_Stride or else
        Reserve_Uses_Bytes /= Reserve_Uses_Count * Reserve_Uses_Stride or else
        not Owner_Extent (Reserve_Uses, Reserve_Uses_Bytes, PW.W.Raw_Use'Alignment) then return Error_Invalid_Argument; end if;
      if Intent_Uses_Count > Interfaces.C.size_t (PQ.Byte_Count'Last) or else
        Intent_Uses_Count > Interfaces.C.size_t (Storage_Offset'Last) / Intent_Uses_Stride or else
        Intent_Uses_Bytes /= Intent_Uses_Count * Intent_Uses_Stride or else
        not Owner_Extent (Intent_Uses, Intent_Uses_Bytes, PW.W.Raw_Use'Alignment) then return Error_Invalid_Argument; end if;
      if Reserve_Receipts_Count > Interfaces.C.size_t (PQ.Byte_Count'Last) or else
        Reserve_Receipts_Count > Interfaces.C.size_t (Storage_Offset'Last) / Reserve_Receipts_Stride or else
        Reserve_Receipts_Bytes /= Reserve_Receipts_Count * Reserve_Receipts_Stride or else
        not Owner_Extent (Reserve_Receipts, Reserve_Receipts_Bytes, PW.CW.Raw_Row'Alignment) then return Error_Invalid_Argument; end if;
      if Reserve_Events_Count > Interfaces.C.size_t (PQ.Byte_Count'Last) or else
        Reserve_Events_Count > Interfaces.C.size_t (Storage_Offset'Last) / Reserve_Events_Stride or else
        Reserve_Events_Bytes /= Reserve_Events_Count * Reserve_Events_Stride or else
        not Owner_Extent (Reserve_Events, Reserve_Events_Bytes, PW.CW.Raw_Row'Alignment) then return Error_Invalid_Argument; end if;
      if Intent_Receipts_Count > Interfaces.C.size_t (PQ.Byte_Count'Last) or else
        Intent_Receipts_Count > Interfaces.C.size_t (Storage_Offset'Last) / Intent_Receipts_Stride or else
        Intent_Receipts_Bytes /= Intent_Receipts_Count * Intent_Receipts_Stride or else
        not Owner_Extent (Intent_Receipts, Intent_Receipts_Bytes, PW.CW.Raw_Row'Alignment) then return Error_Invalid_Argument; end if;
      if Intent_Events_Count > Interfaces.C.size_t (PQ.Byte_Count'Last) or else
        Intent_Events_Count > Interfaces.C.size_t (Storage_Offset'Last) / Intent_Events_Stride or else
        Intent_Events_Bytes /= Intent_Events_Count * Intent_Events_Stride or else
        not Owner_Extent (Intent_Events, Intent_Events_Bytes, PW.CW.Raw_Row'Alignment) then return Error_Invalid_Argument; end if;
      declare
         A : PQ.Byte_Array (1 .. PQ.Byte_Count (Data_Length));
         Raw_Event : constant Prepared_Event := P_Event.To_Pointer (Event).all;
         Raw_Root : constant Prepared_Root := P_Root.To_Pointer (Root).all;
         R : constant PW.W.Raw_Input := P_Input.To_Pointer (Reserve).all;
         I : constant PW.W.Raw_Input := P_Input.To_Pointer (Intent).all;
         Ev : PW.P.C.Event_Row;
         After : PM.Root_State;
         Status : PW.Status;
         Owned_Reserve_Grants : PW.Raw_Grants (1 .. PQ.Byte_Count (Reserve_Grants_Count));
         Owned_Intent_Grants : PW.Raw_Grants (1 .. PQ.Byte_Count (Intent_Grants_Count));
         Owned_Reserve_Uses : PW.Raw_Uses (1 .. PQ.Byte_Count (Reserve_Uses_Count));
         Owned_Intent_Uses : PW.Raw_Uses (1 .. PQ.Byte_Count (Intent_Uses_Count));
         Owned_Reserve_Receipts : PW.Raw_Rows (1 .. PQ.Byte_Count (Reserve_Receipts_Count));
         Owned_Reserve_Events : PW.Raw_Rows (1 .. PQ.Byte_Count (Reserve_Events_Count));
         Owned_Intent_Receipts : PW.Raw_Rows (1 .. PQ.Byte_Count (Intent_Receipts_Count));
         Owned_Intent_Events : PW.Raw_Rows (1 .. PQ.Byte_Count (Intent_Events_Count));
         function Valid_Span (S : Retained_Span) return Boolean is
           (S.First >= 1 and then S.Length >= 0 and then
             PW.P.C.E.C.P.Valid (A, (PQ.Byte_Index (S.First), PQ.Byte_Count (S.Length))));
      begin
         for J in A'Range loop A (J) := Get_Byte (Data, Storage_Offset (J - 1)); end loop;
         if not Valid_Span (Raw_Event.Event_Id) then return Error_Invalid_Argument; end if;
         Ev.Event_Id := (PQ.Byte_Index (Raw_Event.Event_Id.First), PQ.Byte_Count (Raw_Event.Event_Id.Length));
         if not Valid_Span (Raw_Event.Previous) then return Error_Invalid_Argument; end if;
         Ev.Previous := (PQ.Byte_Index (Raw_Event.Previous.First), PQ.Byte_Count (Raw_Event.Previous.Length));
         if not Valid_Span (Raw_Event.Generation) then return Error_Invalid_Argument; end if;
         Ev.Generation := (PQ.Byte_Index (Raw_Event.Generation.First), PQ.Byte_Count (Raw_Event.Generation.Length));
         if not Valid_Span (Raw_Event.Operation) then return Error_Invalid_Argument; end if;
         Ev.Operation := (PQ.Byte_Index (Raw_Event.Operation.First), PQ.Byte_Count (Raw_Event.Operation.Length));
         if not Valid_Span (Raw_Event.Subject_Kind) then return Error_Invalid_Argument; end if;
         Ev.Subject_Kind := (PQ.Byte_Index (Raw_Event.Subject_Kind.First), PQ.Byte_Count (Raw_Event.Subject_Kind.Length));
         if not Valid_Span (Raw_Event.Subject) then return Error_Invalid_Argument; end if;
         Ev.Subject := (PQ.Byte_Index (Raw_Event.Subject.First), PQ.Byte_Count (Raw_Event.Subject.Length));
         if not Valid_Span (Raw_Event.Subgeneration) then return Error_Invalid_Argument; end if;
         Ev.Subgeneration := (PQ.Byte_Index (Raw_Event.Subgeneration.First), PQ.Byte_Count (Raw_Event.Subgeneration.Length));
         if not Valid_Span (Raw_Event.Kind) then return Error_Invalid_Argument; end if;
         Ev.Kind := (PQ.Byte_Index (Raw_Event.Kind.First), PQ.Byte_Count (Raw_Event.Kind.Length));
         if not Valid_Span (Raw_Event.Actor) then return Error_Invalid_Argument; end if;
         Ev.Actor := (PQ.Byte_Index (Raw_Event.Actor.First), PQ.Byte_Count (Raw_Event.Actor.Length));
         if not Valid_Span (Raw_Event.Record_Archive) then return Error_Invalid_Argument; end if;
         Ev.Record_Archive := (PQ.Byte_Index (Raw_Event.Record_Archive.First), PQ.Byte_Count (Raw_Event.Record_Archive.Length));
         if not Valid_Span (Raw_Event.Base_Archive) then return Error_Invalid_Argument; end if;
         Ev.Base_Archive := (PQ.Byte_Index (Raw_Event.Base_Archive.First), PQ.Byte_Count (Raw_Event.Base_Archive.Length));
         if not Valid_Span (Raw_Event.Mac) then return Error_Invalid_Argument; end if;
         Ev.Mac := (PQ.Byte_Index (Raw_Event.Mac.First), PQ.Byte_Count (Raw_Event.Mac.Length));
         for J in Owned_Reserve_Grants'Range loop
            Owned_Reserve_Grants (J) := P_Grant.To_Pointer
              (Reserve_Grants + Storage_Offset (Interfaces.C.size_t (J - 1) * Reserve_Grants_Stride)).all;
         end loop;
         for J in Owned_Intent_Grants'Range loop
            Owned_Intent_Grants (J) := P_Grant.To_Pointer
              (Intent_Grants + Storage_Offset (Interfaces.C.size_t (J - 1) * Intent_Grants_Stride)).all;
         end loop;
         for J in Owned_Reserve_Uses'Range loop
            Owned_Reserve_Uses (J) := P_Use.To_Pointer
              (Reserve_Uses + Storage_Offset (Interfaces.C.size_t (J - 1) * Reserve_Uses_Stride)).all;
         end loop;
         for J in Owned_Intent_Uses'Range loop
            Owned_Intent_Uses (J) := P_Use.To_Pointer
              (Intent_Uses + Storage_Offset (Interfaces.C.size_t (J - 1) * Intent_Uses_Stride)).all;
         end loop;
         for J in Owned_Reserve_Receipts'Range loop
            Owned_Reserve_Receipts (J) := P_Row.To_Pointer
              (Reserve_Receipts + Storage_Offset (Interfaces.C.size_t (J - 1) * Reserve_Receipts_Stride)).all;
         end loop;
         for J in Owned_Reserve_Events'Range loop
            Owned_Reserve_Events (J) := P_Row.To_Pointer
              (Reserve_Events + Storage_Offset (Interfaces.C.size_t (J - 1) * Reserve_Events_Stride)).all;
         end loop;
         for J in Owned_Intent_Receipts'Range loop
            Owned_Intent_Receipts (J) := P_Row.To_Pointer
              (Intent_Receipts + Storage_Offset (Interfaces.C.size_t (J - 1) * Intent_Receipts_Stride)).all;
         end loop;
         for J in Owned_Intent_Events'Range loop
            Owned_Intent_Events (J) := P_Row.To_Pointer
              (Intent_Events + Storage_Offset (Interfaces.C.size_t (J - 1) * Intent_Events_Stride)).all;
         end loop;
         if not Prepared_Root_Valid (A, Raw_Root) then return Error_Invalid_Argument; end if;
         PW.Try_Next (A, Ev, Prepared_Decode_Root (Raw_Root), R, I,
           Owned_Reserve_Grants,
           Owned_Intent_Grants,
           Owned_Reserve_Uses,
           Owned_Intent_Uses,
           Owned_Reserve_Receipts,
           Owned_Reserve_Events,
           Owned_Intent_Receipts,
           Owned_Intent_Events,
           After, Status);
         -- All foreign buffers are copied/checked before the output can alias.
         P_Output.To_Pointer (Output).all :=
           (Status => PW.Status'Pos (Status), After_State => Prepared_Encode_Root (After));
      end;
      return Error_OK;
   exception when others => return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end Prepared_Step_Decide;
function Operation_Authority_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return (2);
      end;
   exception
      when others => return 0;
   end Operation_Authority_Version;
   function Operation_Authority_Layout(Kind,Field:Interfaces.Unsigned_32) return Interfaces.C.long is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   package W renames Worldline.Operation_Authority_Wire; package A renames W.A;
   use System.Storage_Elements; use type System.Address;
   use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int;
   use type Interfaces.Unsigned_8; use type A.Q.Byte_Count;
   begin case Kind is
when 1 => declare V : W.Raw_Quantity; begin case Field is
when 0 => return W.Raw_Quantity'Size / System.Storage_Unit;
when 1 => return W.Raw_Quantity'Alignment;
when 2 => return V.Present'Position;
when 3 => return V.Negative'Position;
when 4 => return V.First'Position;
when 5 => return V.Length'Position;
when others => return -1; end case; end;
when 2 => declare V : W.Raw_UID; begin case Field is
when 0 => return W.Raw_UID'Size / System.Storage_Unit;
when 1 => return W.Raw_UID'Alignment;
when 2 => return V.Present'Position;
when 3 => return V.Value'Position;
when others => return -1; end case; end;
when 3 => declare V : W.Raw_Binding; begin case Field is
when 0 => return W.Raw_Binding'Size / System.Storage_Unit;
when 1 => return W.Raw_Binding'Alignment;
when 2 => return V.Action'Position;
when 3 => return V.Id'Position;
when 4 => return V.Peer'Position;
when 5 => return V.Preparer'Position;
when 6 => return V.Owner'Position;
when 7 => return V.Target_Owner'Position;
when 8 => return V.Policy_Epoch'Position;
when 9 => return V.Resource_Epoch'Position;
when others => return -1; end case; end;
when 4 => declare V : W.Raw_Grant; begin case Field is
when 0 => return W.Raw_Grant'Size / System.Storage_Unit;
when 1 => return W.Raw_Grant'Alignment;
when 2 => return V.Id'Position;
when 3 => return V.Parent'Position;
when 4 => return V.Issuer'Position;
when 5 => return V.Instance'Position;
when 6 => return V.Root_Set'Position;
when 7 => return V.Policy'Position;
when 8 => return V.Subject'Position;
when 9 => return V.Owner'Position;
when 10 => return V.Allowed'Position;
when 11 => return V.State'Position;
when 12 => return V.Epoch'Position;
when 13 => return V.Ceiling'Position;
when 14 => return V.Issued_At'Position;
when 15 => return V.Expires_At'Position;
when others => return -1; end case; end;
when 5 => declare V : W.Raw_Use; begin case Field is
when 0 => return W.Raw_Use'Size / System.Storage_Unit;
when 1 => return W.Raw_Use'Alignment;
when 2 => return V.Bound'Position;
when 3 => return V.State'Position;
when others => return -1; end case; end;
when 6 => declare V : W.Raw_Evidence; begin case Field is
when 0 => return W.Raw_Evidence'Size / System.Storage_Unit;
when 1 => return W.Raw_Evidence'Alignment;
when 2 => return V.Effect_Binding'Position;
when 3 => return V.Actual_Receipt_Root'Position;
when 4 => return V.Actual_Causal_Root'Position;
when 5 => return V.No_Effect_Binding'Position;
when 6 => return V.Owner_Resolution'Position;
when 7 => return V.Quarantine_Head'Position;
when 8 => return V.Witnessed_Receipt_Head'Position;
when 9 => return V.Witnessed_Causal_Head'Position;
when 10 => return V.Recovery'Position;
when 11 => return V.Original_Use'Position;
when 12 => return V.Effect_Material_First'Position;
when 13 => return V.Effect_Material_Length'Position;
when others => return -1; end case; end;
when 7 => declare V : W.Raw_Input; begin case Field is
when 0 => return W.Raw_Input'Size / System.Storage_Unit;
when 1 => return W.Raw_Input'Alignment;
when 2 => return V.Schema'Position;
when 3 => return V.Mode'Position;
when 4 => return V.Bound'Position;
when 5 => return V.Now'Position;
when 6 => return V.Facts'Position;
when others => return -1; end case; end;
when 8 => declare V : W.Raw_Result; begin case Field is
when 0 => return W.Raw_Result'Size / System.Storage_Unit;
when 1 => return W.Raw_Result'Alignment;
when 2 => return V.Disposition'Position;
when others => return -1; end case; end;
      when others => return -1; end case;
      end;
   exception
      when others => return -1;
   end Operation_Authority_Layout;
   -- Numeric representation guards are not valid-memory theorems. Authentic
   -- ctypes owns every referenced input until return, with no concurrent write.
   -- Original foreign output alias controls remain admitted: the On snapshot
   -- and returned local Result are disjoint before the one final foreign write.
   function Native_Execution_Shape (Address : System.Address; Length : Interfaces.C.size_t) return Boolean is
     (Address /= System.Null_Address and then Length > 0
      and then Length <= Interfaces.C.size_t (System.Storage_Elements.Storage_Offset'Last)
      and then System.Storage_Elements.Integer_Address (Length - 1) <=
        System.Storage_Elements.Integer_Address'Last - System.Storage_Elements.To_Integer (Address));
   function Native_Execution_Array_Shape
     (Address : System.Address; Count, Element_Size : Interfaces.C.size_t;
      Alignment : System.Storage_Elements.Integer_Address) return Boolean is
     (Count <= Interfaces.C.size_t (Resource_Quantities.Byte_Count'Last)
      and then (Count = 0 or else (Element_Size > 0
        and then Count <= Interfaces.C.size_t (System.Storage_Elements.Storage_Offset'Last) / Element_Size
        and then Native_Execution_Shape (Address, Count * Element_Size)
        and then System.Storage_Elements.To_Integer (Address) mod Alignment = 0)));
   function Resource_Scoped_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return 1;
      end;
   exception
      when others => return 0;
   end Resource_Scoped_Version;
   function Resource_Scoped_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Native renames Worldline.Native_Execution_Capture;
      package N renames V.N;
      package W renames V.W;
      package O renames V.O;
      package Q renames V.Q;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.long;
      use type Interfaces.C.int;
      V_State : N.Raw_State;
      V_Scope_Frame : N.Raw_Scope_Frame;
      V_Physical_Key : N.Raw_Physical_Key;
      V_Bucket : N.Raw_Bucket;
      V_Projection : N.Raw_Projection;
      V_Current_Observation : N.Raw_Current_Observation;
      V_Intent : N.Raw_Intent;
      V_Packet : N.Raw_Packet;
      V_Result : W.Raw_Result;
   begin
      case Kind is
         when 0 =>
            case Field is
               when 0 => return N.Raw_State'Size / System.Storage_Unit;
               when 1 => return N.Raw_State'Alignment;
               when 2 => return V_State.Current'Position;
               when 3 => return V_State.Resource_Epoch'Position;
               when 4 => return V_State.Universe_Head'Position;
               when 5 => return V_State.Ledger_Head'Position;
               when 6 => return V_State.History_Head'Position;
               when 7 => return V_State.Physical_Head'Position;
               when others => return -1;
            end case;
         when 1 =>
            case Field is
               when 0 => return N.Raw_Scope_Frame'Size / System.Storage_Unit;
               when 1 => return N.Raw_Scope_Frame'Alignment;
               when 2 => return V_Scope_Frame.Scope'Position;
               when 3 => return V_Scope_Frame.First_Epoch'Position;
               when 4 => return V_Scope_Frame.Universe_Head'Position;
               when 5 => return V_Scope_Frame.Frame_Head'Position;
               when 6 => return V_Scope_Frame.Prior_Frame'Position;
               when 7 => return V_Scope_Frame.Store_Genesis'Position;
               when 8 => return V_Scope_Frame.Store_Id'Position;
               when 9 => return V_Scope_Frame.Root_Head'Position;
               when 10 => return V_Scope_Frame.Prime'Position;
               when 11 => return V_Scope_Frame.Root_Count'Position;
               when 12 => return V_Scope_Frame.Cause'Position;
               when 13 => return V_Scope_Frame.Requester'Position;
               when 14 => return V_Scope_Frame.Receipt'Position;
               when 15 => return V_Scope_Frame.Catalogue_Head'Position;
               when 16 => return V_Scope_Frame.Observation_Head'Position;
               when others => return -1;
            end case;
         when 2 =>
            case Field is
               when 0 => return N.Raw_Physical_Key'Size / System.Storage_Unit;
               when 1 => return N.Raw_Physical_Key'Alignment;
               when 2 => return V_Physical_Key.Machine'Position;
               when 3 => return V_Physical_Key.Resource'Position;
               when 4 => return V_Physical_Key.Unit'Position;
               when others => return -1;
            end case;
         when 3 =>
            case Field is
               when 0 => return N.Raw_Bucket'Size / System.Storage_Unit;
               when 1 => return N.Raw_Bucket'Alignment;
               when 2 => return V_Bucket.Key'Position;
               when 3 => return V_Bucket.Capacity'Position;
               when 4 => return V_Bucket.Held_Total'Position;
               when 5 => return V_Bucket.Charged_Total'Position;
               when 6 => return V_Bucket.Capacity_Source'Position;
               when 7 => return V_Bucket.Catalogue_Head'Position;
               when 8 => return V_Bucket.Observation_Head'Position;
               when others => return -1;
            end case;
         when 4 =>
            case Field is
               when 0 => return N.Raw_Projection'Size / System.Storage_Unit;
               when 1 => return N.Raw_Projection'Alignment;
               when 2 => return V_Projection.Key'Position;
               when 3 => return V_Projection.Bound'Position;
               when 4 => return V_Projection.Origin'Position;
               when 5 => return V_Projection.Catalogue_Head'Position;
               when 6 => return V_Projection.Numerator'Position;
               when 7 => return V_Projection.Denominator'Position;
               when 8 => return V_Projection.Amount'Position;
               when others => return -1;
            end case;
         when 5 =>
            case Field is
               when 0 => return N.Raw_Current_Observation'Size / System.Storage_Unit;
               when 1 => return N.Raw_Current_Observation'Alignment;
               when 2 => return V_Current_Observation.Scope'Position;
               when 3 => return V_Current_Observation.Resource_Epoch'Position;
               when 4 => return V_Current_Observation.Universe_Head'Position;
               when 5 => return V_Current_Observation.Ledger_Head'Position;
               when 6 => return V_Current_Observation.History_Head'Position;
               when 7 => return V_Current_Observation.Physical_Head'Position;
               when 8 => return V_Current_Observation.Store_Genesis'Position;
               when 9 => return V_Current_Observation.Store_Id'Position;
               when 10 => return V_Current_Observation.Root_Head'Position;
               when 11 => return V_Current_Observation.Prime'Position;
               when 12 => return V_Current_Observation.Root_Count'Position;
               when 13 => return V_Current_Observation.Cause'Position;
               when 14 => return V_Current_Observation.Requester'Position;
               when 15 => return V_Current_Observation.Receipt'Position;
               when 16 => return V_Current_Observation.Catalogue_Head'Position;
               when 17 => return V_Current_Observation.Observation_Head'Position;
               when others => return -1;
            end case;
         when 6 =>
            case Field is
               when 0 => return N.Raw_Intent'Size / System.Storage_Unit;
               when 1 => return N.Raw_Intent'Alignment;
               when 2 => return V_Intent.Kind'Position;
               when 3 => return V_Intent.Original'Position;
               when 4 => return V_Intent.Expected_Epoch'Position;
               when 5 => return V_Intent.Expected_Ledger_Head'Position;
               when 6 => return V_Intent.Request_Id'Position;
               when 7 => return V_Intent.Cause'Position;
               when 8 => return V_Intent.Requester'Position;
               when 9 => return V_Intent.Receipt'Position;
               when others => return -1;
            end case;
         when 7 =>
            case Field is
               when 0 => return N.Raw_Packet'Size / System.Storage_Unit;
               when 1 => return N.Raw_Packet'Alignment;
               when 2 => return V_Packet.Schema_Version'Position;
               when 3 => return V_Packet.Before_State'Position;
               when 4 => return V_Packet.Proposed_State'Position;
               when 5 => return V_Packet.Current'Position;
               when 6 => return V_Packet.Request'Position;
               when others => return -1;
            end case;
         when 8 =>
            case Field is
               when 0 => return W.Raw_Result'Size / System.Storage_Unit;
               when 1 => return W.Raw_Result'Alignment;
               when 2 => return V_Result.Status'Position;
               when others => return -1;
            end case;
         when others => return -1;
      end case;
      end;
   exception
      when others => return -1;
   end Resource_Scoped_Layout;
   function Resource_Scoped_Check
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      History : System.Address;
      History_Count : Interfaces.C.size_t;
      Proposed_History : System.Address;
      Proposed_History_Count : Interfaces.C.size_t;
      Rows : System.Address;
      Rows_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address;
      Proposed_Rows_Count : Interfaces.C.size_t;
      Projection : System.Address;
      Projection_Count : Interfaces.C.size_t;
      Proposed_Projection : System.Address;
      Proposed_Projection_Count : Interfaces.C.size_t;
      Buckets : System.Address;
      Buckets_Count : Interfaces.C.size_t;
      Proposed_Buckets : System.Address;
      Proposed_Buckets_Count : Interfaces.C.size_t;
      Actual_Buckets : System.Address;
      Actual_Buckets_Count : Interfaces.C.size_t;
      Observed : System.Address;
      Observed_Count : Interfaces.C.size_t;
      Facts : System.Address;
      Facts_Count : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Native renames Worldline.Native_Execution_Capture;
      package N renames V.N;
      package W renames V.W;
      package O renames V.O;
      package Q renames V.Q;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.long;
      use type Interfaces.C.int;
      package Raw_Pointers is new System.Address_To_Access_Conversions (N.Raw_Packet);
      package Output_Pointers is new System.Address_To_Access_Conversions (W.Raw_Result);
   begin
      if Input_Length /= N.Raw_Packet'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Input, Input_Length)
        or else To_Integer (Input) mod N.Raw_Packet'Alignment /= 0
        or else not Native_Execution_Array_Shape (Arena, Arena_Length, Q.Byte'Size / System.Storage_Unit, Q.Byte'Alignment)
        or else not Native_Execution_Array_Shape (History, History_Count, N.Raw_Scope_Frame'Size / System.Storage_Unit, N.Raw_Scope_Frame'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_History, Proposed_History_Count, N.Raw_Scope_Frame'Size / System.Storage_Unit, N.Raw_Scope_Frame'Alignment)
        or else not Native_Execution_Array_Shape (Rows, Rows_Count, W.Raw_Row'Size / System.Storage_Unit, W.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Rows, Proposed_Rows_Count, W.Raw_Row'Size / System.Storage_Unit, W.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Projection, Projection_Count, N.Raw_Projection'Size / System.Storage_Unit, N.Raw_Projection'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Projection, Proposed_Projection_Count, N.Raw_Projection'Size / System.Storage_Unit, N.Raw_Projection'Alignment)
        or else not Native_Execution_Array_Shape (Buckets, Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Buckets, Proposed_Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Actual_Buckets, Actual_Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Observed, Observed_Count, W.Raw_Native'Size / System.Storage_Unit, W.Raw_Native'Alignment)
        or else not Native_Execution_Array_Shape (Facts, Facts_Count, O.Raw_Facts'Size / System.Storage_Unit, O.Raw_Facts'Alignment)
        or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Output, Output_Length)
        or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Arena_Length));
         Data_View : constant Resource_Bytes_Observer :=
           Observe_Resource_Bytes (Arena, Data_Bounds);
         History_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (History_Count));
         History_View : constant Native_History_Observer :=
           Observe_Native_History (History, History_Bounds);
         Proposed_History_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_History_Count));
         Proposed_History_View : constant Native_History_Observer :=
           Observe_Native_History (Proposed_History, Proposed_History_Bounds);
         Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Rows_Count));
         Rows_View : constant Native_Rows_Observer :=
           Observe_Native_Rows (Rows, Rows_Bounds);
         Proposed_Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Rows_Count));
         Proposed_Rows_View : constant Native_Rows_Observer :=
           Observe_Native_Rows (Proposed_Rows, Proposed_Rows_Bounds);
         Projection_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Projection_Count));
         Projection_View : constant Native_Projection_Observer :=
           Observe_Native_Projection (Projection, Projection_Bounds);
         Proposed_Projection_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Projection_Count));
         Proposed_Projection_View : constant Native_Projection_Observer :=
           Observe_Native_Projection (Proposed_Projection, Proposed_Projection_Bounds);
         Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Buckets_Count));
         Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Buckets, Buckets_Bounds);
         Proposed_Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Buckets_Count));
         Proposed_Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Proposed_Buckets, Proposed_Buckets_Bounds);
         Actual_Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Actual_Buckets_Count));
         Actual_Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Actual_Buckets, Actual_Buckets_Bounds);
         Observed_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Observed_Count));
         Observed_View : constant Native_Observed_Observer :=
           Observe_Native_Observed (Observed, Observed_Bounds);
         Facts_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Facts_Count));
         Facts_View : constant Native_Facts_Observer :=
           Observe_Native_Facts (Facts, Facts_Bounds);
         Result : constant V.Result := Native.Scoped_Check (Raw_Pointers.To_Pointer (Input), Data_View, History_View, Proposed_History_View, Rows_View, Proposed_Rows_View, Projection_View, Proposed_Projection_View, Buckets_View, Proposed_Buckets_View, Actual_Buckets_View, Observed_View, Facts_View);
      begin
         Flush_Native_Diagnostic_Trace;
         if not Result.Well_Formed then return -1; end if;
         Output_Pointers.To_Pointer (Output).all := (Status => Result.Status);
      end;
      return 0;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return -1;
      end;
   exception
      when others => return -1;
   end Resource_Scoped_Check;
   function Resource_Scoped_Validate
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      History : System.Address;
      History_Count : Interfaces.C.size_t;
      Proposed_History : System.Address;
      Proposed_History_Count : Interfaces.C.size_t;
      Rows : System.Address;
      Rows_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address;
      Proposed_Rows_Count : Interfaces.C.size_t;
      Projection : System.Address;
      Projection_Count : Interfaces.C.size_t;
      Proposed_Projection : System.Address;
      Proposed_Projection_Count : Interfaces.C.size_t;
      Buckets : System.Address;
      Buckets_Count : Interfaces.C.size_t;
      Proposed_Buckets : System.Address;
      Proposed_Buckets_Count : Interfaces.C.size_t;
      Actual_Buckets : System.Address;
      Actual_Buckets_Count : Interfaces.C.size_t;
      Observed : System.Address;
      Observed_Count : Interfaces.C.size_t;
      Facts : System.Address;
      Facts_Count : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Native renames Worldline.Native_Execution_Capture;
      package N renames V.N;
      package W renames V.W;
      package O renames V.O;
      package Q renames V.Q;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.long;
      use type Interfaces.C.int;
      package Raw_Pointers is new System.Address_To_Access_Conversions (N.Raw_Packet);
      package Output_Pointers is new System.Address_To_Access_Conversions (W.Raw_Result);
   begin
      if Input_Length /= N.Raw_Packet'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Input, Input_Length)
        or else To_Integer (Input) mod N.Raw_Packet'Alignment /= 0
        or else not Native_Execution_Array_Shape (Arena, Arena_Length, Q.Byte'Size / System.Storage_Unit, Q.Byte'Alignment)
        or else not Native_Execution_Array_Shape (History, History_Count, N.Raw_Scope_Frame'Size / System.Storage_Unit, N.Raw_Scope_Frame'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_History, Proposed_History_Count, N.Raw_Scope_Frame'Size / System.Storage_Unit, N.Raw_Scope_Frame'Alignment)
        or else not Native_Execution_Array_Shape (Rows, Rows_Count, W.Raw_Row'Size / System.Storage_Unit, W.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Rows, Proposed_Rows_Count, W.Raw_Row'Size / System.Storage_Unit, W.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Projection, Projection_Count, N.Raw_Projection'Size / System.Storage_Unit, N.Raw_Projection'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Projection, Proposed_Projection_Count, N.Raw_Projection'Size / System.Storage_Unit, N.Raw_Projection'Alignment)
        or else not Native_Execution_Array_Shape (Buckets, Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Buckets, Proposed_Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Actual_Buckets, Actual_Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Observed, Observed_Count, W.Raw_Native'Size / System.Storage_Unit, W.Raw_Native'Alignment)
        or else not Native_Execution_Array_Shape (Facts, Facts_Count, O.Raw_Facts'Size / System.Storage_Unit, O.Raw_Facts'Alignment)
        or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Output, Output_Length)
        or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Arena_Length));
         Data_View : constant Resource_Bytes_Observer :=
           Observe_Resource_Bytes (Arena, Data_Bounds);
         History_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (History_Count));
         History_View : constant Native_History_Observer :=
           Observe_Native_History (History, History_Bounds);
         Proposed_History_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_History_Count));
         Proposed_History_View : constant Native_History_Observer :=
           Observe_Native_History (Proposed_History, Proposed_History_Bounds);
         Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Rows_Count));
         Rows_View : constant Native_Rows_Observer :=
           Observe_Native_Rows (Rows, Rows_Bounds);
         Proposed_Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Rows_Count));
         Proposed_Rows_View : constant Native_Rows_Observer :=
           Observe_Native_Rows (Proposed_Rows, Proposed_Rows_Bounds);
         Projection_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Projection_Count));
         Projection_View : constant Native_Projection_Observer :=
           Observe_Native_Projection (Projection, Projection_Bounds);
         Proposed_Projection_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Projection_Count));
         Proposed_Projection_View : constant Native_Projection_Observer :=
           Observe_Native_Projection (Proposed_Projection, Proposed_Projection_Bounds);
         Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Buckets_Count));
         Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Buckets, Buckets_Bounds);
         Proposed_Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Buckets_Count));
         Proposed_Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Proposed_Buckets, Proposed_Buckets_Bounds);
         Actual_Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Actual_Buckets_Count));
         Actual_Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Actual_Buckets, Actual_Buckets_Bounds);
         Observed_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Observed_Count));
         Observed_View : constant Native_Observed_Observer :=
           Observe_Native_Observed (Observed, Observed_Bounds);
         Facts_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Facts_Count));
         Facts_View : constant Native_Facts_Observer :=
           Observe_Native_Facts (Facts, Facts_Bounds);
         Result : constant V.Result := Native.Scoped_Validate (Raw_Pointers.To_Pointer (Input), Data_View, History_View, Proposed_History_View, Rows_View, Proposed_Rows_View, Projection_View, Proposed_Projection_View, Buckets_View, Proposed_Buckets_View, Actual_Buckets_View, Observed_View, Facts_View);
      begin
         Flush_Native_Diagnostic_Trace;
         if not Result.Well_Formed then return -1; end if;
         Output_Pointers.To_Pointer (Output).all := (Status => Result.Status);
      end;
      return 0;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return -1;
      end;
   exception
      when others => return -1;
   end Resource_Scoped_Validate;
   function Resource_Scoped_Classify
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      History : System.Address;
      History_Count : Interfaces.C.size_t;
      Proposed_History : System.Address;
      Proposed_History_Count : Interfaces.C.size_t;
      Rows : System.Address;
      Rows_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address;
      Proposed_Rows_Count : Interfaces.C.size_t;
      Projection : System.Address;
      Projection_Count : Interfaces.C.size_t;
      Proposed_Projection : System.Address;
      Proposed_Projection_Count : Interfaces.C.size_t;
      Buckets : System.Address;
      Buckets_Count : Interfaces.C.size_t;
      Proposed_Buckets : System.Address;
      Proposed_Buckets_Count : Interfaces.C.size_t;
      Actual_Buckets : System.Address;
      Actual_Buckets_Count : Interfaces.C.size_t;
      Observed : System.Address;
      Observed_Count : Interfaces.C.size_t;
      Facts : System.Address;
      Facts_Count : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Native renames Worldline.Native_Execution_Capture;
      package N renames V.N;
      package W renames V.W;
      package O renames V.O;
      package Q renames V.Q;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.long;
      use type Interfaces.C.int;
      package Raw_Pointers is new System.Address_To_Access_Conversions (N.Raw_Packet);
      package Output_Pointers is new System.Address_To_Access_Conversions (W.Raw_Result);
   begin
      if Input_Length /= N.Raw_Packet'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Input, Input_Length)
        or else To_Integer (Input) mod N.Raw_Packet'Alignment /= 0
        or else not Native_Execution_Array_Shape (Arena, Arena_Length, Q.Byte'Size / System.Storage_Unit, Q.Byte'Alignment)
        or else not Native_Execution_Array_Shape (History, History_Count, N.Raw_Scope_Frame'Size / System.Storage_Unit, N.Raw_Scope_Frame'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_History, Proposed_History_Count, N.Raw_Scope_Frame'Size / System.Storage_Unit, N.Raw_Scope_Frame'Alignment)
        or else not Native_Execution_Array_Shape (Rows, Rows_Count, W.Raw_Row'Size / System.Storage_Unit, W.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Rows, Proposed_Rows_Count, W.Raw_Row'Size / System.Storage_Unit, W.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Projection, Projection_Count, N.Raw_Projection'Size / System.Storage_Unit, N.Raw_Projection'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Projection, Proposed_Projection_Count, N.Raw_Projection'Size / System.Storage_Unit, N.Raw_Projection'Alignment)
        or else not Native_Execution_Array_Shape (Buckets, Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Buckets, Proposed_Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Actual_Buckets, Actual_Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Observed, Observed_Count, W.Raw_Native'Size / System.Storage_Unit, W.Raw_Native'Alignment)
        or else not Native_Execution_Array_Shape (Facts, Facts_Count, O.Raw_Facts'Size / System.Storage_Unit, O.Raw_Facts'Alignment)
        or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Output, Output_Length)
        or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Arena_Length));
         Data_View : constant Resource_Bytes_Observer :=
           Observe_Resource_Bytes (Arena, Data_Bounds);
         History_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (History_Count));
         History_View : constant Native_History_Observer :=
           Observe_Native_History (History, History_Bounds);
         Proposed_History_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_History_Count));
         Proposed_History_View : constant Native_History_Observer :=
           Observe_Native_History (Proposed_History, Proposed_History_Bounds);
         Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Rows_Count));
         Rows_View : constant Native_Rows_Observer :=
           Observe_Native_Rows (Rows, Rows_Bounds);
         Proposed_Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Rows_Count));
         Proposed_Rows_View : constant Native_Rows_Observer :=
           Observe_Native_Rows (Proposed_Rows, Proposed_Rows_Bounds);
         Projection_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Projection_Count));
         Projection_View : constant Native_Projection_Observer :=
           Observe_Native_Projection (Projection, Projection_Bounds);
         Proposed_Projection_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Projection_Count));
         Proposed_Projection_View : constant Native_Projection_Observer :=
           Observe_Native_Projection (Proposed_Projection, Proposed_Projection_Bounds);
         Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Buckets_Count));
         Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Buckets, Buckets_Bounds);
         Proposed_Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Buckets_Count));
         Proposed_Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Proposed_Buckets, Proposed_Buckets_Bounds);
         Actual_Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Actual_Buckets_Count));
         Actual_Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Actual_Buckets, Actual_Buckets_Bounds);
         Observed_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Observed_Count));
         Observed_View : constant Native_Observed_Observer :=
           Observe_Native_Observed (Observed, Observed_Bounds);
         Facts_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Facts_Count));
         Facts_View : constant Native_Facts_Observer :=
           Observe_Native_Facts (Facts, Facts_Bounds);
         Result : constant V.Result := Native.Scoped_Classify (Raw_Pointers.To_Pointer (Input), Data_View, History_View, Proposed_History_View, Rows_View, Proposed_Rows_View, Projection_View, Proposed_Projection_View, Buckets_View, Proposed_Buckets_View, Actual_Buckets_View, Observed_View, Facts_View);
      begin
         Flush_Native_Diagnostic_Trace;
         if not Result.Well_Formed then return -1; end if;
         Output_Pointers.To_Pointer (Output).all := (Status => Result.Status);
      end;
      return 0;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return -1;
      end;
   exception
      when others => return -1;
   end Resource_Scoped_Classify;
   function Resource_Observation_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return 1;
      end;
   exception
      when others => return 0;
   end Resource_Observation_Version;
   function Resource_Observation_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package OW renames Resource_Observation_Classification_Wire;
      use type Interfaces.C.long;
      F : OW.Raw_Facts;
      P : OW.Raw_Input;
   begin
      case Kind is
         when 1 =>
            case Field is
               when 0 => return OW.Raw_Facts'Size / System.Storage_Unit;
               when 1 => return OW.Raw_Facts'Alignment;
               when 2 => return F.Current'Position;
               when 3 => return F.Current_Epoch'Position;
               when 4 => return F.Retained'Position;
               when 5 => return F.Current_Universe_Head'Position;
               when 6 => return F.Current_Ledger_Head'Position;
               when 7 => return F.Intent'Position;
               when 8 => return F.Dispatch'Position;
               when 9 => return F.Observation_Head'Position;
               when 10 => return F.Actual_Unit'Position;
               when 11 => return F.Cgroup'Position;
               when 12 => return F.Invocation'Position;
               when 13 => return F.Namespace'Position;
               when 14 => return F.Held_Namespace'Position;
               when 15 => return F.Peer'Position;
               when 16 => return F.Held_Peer'Position;
               when 17 => return F.Helper_Image'Position;
               when 18 => return F.Expected_Helper_Image'Position;
               when 19 => return F.Challenge'Position;
               when 20 => return F.Held_Challenge'Position;
               when 21 => return F.Protocol'Position;
               when 22 => return F.Closed_Event'Position;
               when 23 => return F.Namespace_Wait'Position;
               when 24 => return F.Helper_Wait'Position;
               when 25 => return F.Cgroup_Events'Position;
               when 26 => return F.Cgroup_Type'Position;
               when 27 => return F.Manager_Delegate'Position;
               when 28 => return F.Cgroup_Owner'Position;
               when 29 => return F.Cgroup_Group_Write'Position;
               when 30 => return F.Cgroup_Other_Write'Position;
               when 31 => return F.Actual_Store_Genesis'Position;
               when 32 => return F.Actual_Store_Id'Position;
               when 33 => return F.Owner_Store_Genesis'Position;
               when 34 => return F.Owner_Store_Id'Position;
               when 35 => return F.Genesis_Universe'Position;
               when 36 => return F.Genesis_Instance'Position;
               when 37 => return F.Genesis_Context_Head'Position;
               when 38 => return F.Genesis_Prime'Position;
               when 39 => return F.Genesis_Root_Count'Position;
               when 40 => return F.Phase'Position;
               when others => return -1;
            end case;
         when 2 =>
            case Field is
               when 0 => return OW.Raw_Input'Size / System.Storage_Unit;
               when 1 => return OW.Raw_Input'Alignment;
               when 2 => return P.State'Position;
               when 3 => return P.Item'Position;
               when 4 => return P.Captured'Position;
               when others => return -1;
            end case;
         when others => return -1;
      end case;
      end;
   exception
      when others => return -1;
   end Resource_Observation_Layout;
   function Resource_Observation_Classify
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Native renames Worldline.Native_Execution_Capture;
      package N renames V.N;
      package W renames V.W;
      package O renames V.O;
      package Q renames V.Q;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.long;
      use type Interfaces.C.int;
      package Raw_Pointers is new System.Address_To_Access_Conversions (O.Raw_Input);
      package Output_Pointers is new System.Address_To_Access_Conversions (W.Raw_Result);
   begin
      if Input_Length /= O.Raw_Input'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Input, Input_Length)
        or else To_Integer (Input) mod O.Raw_Input'Alignment /= 0
        or else not Native_Execution_Array_Shape (Arena, Arena_Length, Q.Byte'Size / System.Storage_Unit, Q.Byte'Alignment)
        or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Output, Output_Length)
        or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Arena_Length));
         Data_View : constant Resource_Bytes_Observer :=
           Observe_Resource_Bytes (Arena, Data_Bounds);
         Result : constant V.Result := Native.Observation_Classify (Raw_Pointers.To_Pointer (Input), Data_View);
      begin
         Flush_Native_Diagnostic_Trace;
         if not Result.Well_Formed then return -1; end if;
         Output_Pointers.To_Pointer (Output).all := (Status => Result.Status);
      end;
      return 0;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return -2;
      end;
   exception
      when others => return -2;
   end Resource_Observation_Classify;
   function Resource_Observation_Current
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Native renames Worldline.Native_Execution_Capture;
      package N renames V.N;
      package W renames V.W;
      package O renames V.O;
      package Q renames V.Q;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.long;
      use type Interfaces.C.int;
      package Raw_Pointers is new System.Address_To_Access_Conversions (O.Raw_Input);
      package Output_Pointers is new System.Address_To_Access_Conversions (W.Raw_Result);
   begin
      if Input_Length /= O.Raw_Input'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Input, Input_Length)
        or else To_Integer (Input) mod O.Raw_Input'Alignment /= 0
        or else not Native_Execution_Array_Shape (Arena, Arena_Length, Q.Byte'Size / System.Storage_Unit, Q.Byte'Alignment)
        or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Output, Output_Length)
        or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Arena_Length));
         Data_View : constant Resource_Bytes_Observer :=
           Observe_Resource_Bytes (Arena, Data_Bounds);
         Result : constant V.Result := Native.Observation_Current (Raw_Pointers.To_Pointer (Input), Data_View);
      begin
         Flush_Native_Diagnostic_Trace;
         if not Result.Well_Formed then return -1; end if;
         Output_Pointers.To_Pointer (Output).all := (Status => Result.Status);
      end;
      return 0;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return -2;
      end;
   exception
      when others => return -2;
   end Resource_Observation_Current;
   function Resource_Observation_Genesis_Current
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Native renames Worldline.Native_Execution_Capture;
      package N renames V.N;
      package W renames V.W;
      package O renames V.O;
      package Q renames V.Q;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.long;
      use type Interfaces.C.int;
      package Raw_Pointers is new System.Address_To_Access_Conversions (O.Raw_Input);
      package Output_Pointers is new System.Address_To_Access_Conversions (W.Raw_Result);
   begin
      if Input_Length /= O.Raw_Input'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Input, Input_Length)
        or else To_Integer (Input) mod O.Raw_Input'Alignment /= 0
        or else not Native_Execution_Array_Shape (Arena, Arena_Length, Q.Byte'Size / System.Storage_Unit, Q.Byte'Alignment)
        or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Output, Output_Length)
        or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Arena_Length));
         Data_View : constant Resource_Bytes_Observer :=
           Observe_Resource_Bytes (Arena, Data_Bounds);
         Result : constant V.Result := Native.Observation_Genesis_Current (Raw_Pointers.To_Pointer (Input), Data_View);
      begin
         Flush_Native_Diagnostic_Trace;
         if not Result.Well_Formed then return -1; end if;
         Output_Pointers.To_Pointer (Output).all := (Status => Result.Status);
      end;
      return 0;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return -2;
      end;
   exception
      when others => return -2;
   end Resource_Observation_Genesis_Current;
   function Resource_Actor_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return 1;
      end;
   exception
      when others => return 0;
   end Resource_Actor_Version;
   function Resource_Actor_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Native renames Worldline.Native_Execution_Capture;
      package N renames V.N;
      package W renames V.W;
      package Q renames V.Q;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.long;
      use type Interfaces.C.int;
      O : D.Raw_Observation;
      C : D.Raw_Capability;
      R : D.Raw_Packet;
   begin
      case Kind is
         when 0 =>
            case Field is
               when 0 => return D.Raw_Observation'Size / System.Storage_Unit;
               when 1 => return D.Raw_Observation'Alignment;
               when 2 => return O.Bound'Position;
               when 3 => return O.Raw_Frame'Position;
               when 4 => return O.Raw_Sender'Position;
               when 5 => return O.Ticket'Position;
               when 6 => return O.Raw_Proc_Status'Position;
               when 7 => return O.Raw_Proc_Cgroup'Position;
               when 8 => return O.Raw_Proc_Maps'Position;
               when 9 => return O.Raw_Proc_Cmdline'Position;
               when 10 => return O.Raw_Pidfd_Info'Position;
               when 11 => return O.Namespace'Position;
               when 12 => return O.Held_Namespace'Position;
               when 13 => return O.Helper_Image'Position;
               when 14 => return O.Expected_Helper_Image'Position;
               when 15 => return O.Executable_Plan'Position;
               when 16 => return O.Expected_Executable_Plan'Position;
               when 17 => return O.Original_Requester'Position;
               when 18 => return O.Requester_Credentials'Position;
               when 19 => return O.Expected_Requester_Credentials'Position;
               when 20 => return O.Dispatch'Position;
               when 21 => return O.Running_Event'Position;
               when 22 => return O.Expected_Running_Event'Position;
               when 23 => return O.Canonical_Use_Event'Position;
               when 24 => return O.Expected_Canonical_Use_Event'Position;
               when 25 => return O.Store_Genesis'Position;
               when 26 => return O.Expected_Store_Genesis'Position;
               when 27 => return O.Source_Lease'Position;
               when 28 => return O.Expected_Source_Lease'Position;
               when 29 => return O.Actor_Wait'Position;
               when 30 => return O.Helper_Wait'Position;
               when 31 => return O.Namespace_Wait'Position;
               when 32 => return O.Host_Pid'Position;
               when 33 => return O.Namespace_Pid'Position;
               when 34 => return O.Sender_Uid'Position;
               when 35 => return O.Sender_Gid'Position;
               when 36 => return O.Real_Uid'Position;
               when 37 => return O.Effective_Uid'Position;
               when 38 => return O.Saved_Uid'Position;
               when 39 => return O.Real_Gid'Position;
               when 40 => return O.Effective_Gid'Position;
               when 41 => return O.Saved_Gid'Position;
               when 42 => return O.Capability_Version'Position;
               when 43 => return O.Effective_Low'Position;
               when 44 => return O.Permitted_Low'Position;
               when 45 => return O.Inheritable_Low'Position;
               when 46 => return O.Effective_High'Position;
               when 47 => return O.Permitted_High'Position;
               when 48 => return O.Inheritable_High'Position;
               when 49 => return O.Securebits'Position;
               when 50 => return O.No_New_Privs'Position;
               when 51 => return O.Requester_Uid'Position;
               when 52 => return O.Requester_Gid'Position;
               when 53 => return O.Configured_Requester_Uid'Position;
               when 54 => return O.Workload_Uid'Position;
               when 55 => return O.Workload_Gid'Position;
               when 56 => return O.Proc_Host_Pid'Position;
               when 57 => return O.Proc_Namespace_Pid'Position;
               when 58 => return O.Proc_Real_Uid'Position;
               when 59 => return O.Proc_Effective_Uid'Position;
               when 60 => return O.Proc_Saved_Uid'Position;
               when 61 => return O.Proc_Real_Gid'Position;
               when 62 => return O.Proc_Effective_Gid'Position;
               when 63 => return O.Proc_Saved_Gid'Position;
               when 64 => return O.Proc_Effective'Position;
               when 65 => return O.Proc_Permitted'Position;
               when 66 => return O.Proc_Inheritable'Position;
               when 67 => return O.Proc_Bounding'Position;
               when 68 => return O.Proc_Ambient'Position;
               when 69 => return O.Proc_No_New_Privs'Position;
               when 70 => return O.Proc_Fs_Uid'Position;
               when 71 => return O.Proc_Fs_Gid'Position;
               when others => return -1;
            end case;
         when 1 =>
            case Field is
               when 0 => return D.Raw_Capability'Size / System.Storage_Unit;
               when 1 => return D.Raw_Capability'Alignment;
               when 2 => return C.Index'Position;
               when 3 => return C.Bounding'Position;
               when 4 => return C.Ambient'Position;
               when others => return -1;
            end case;
         when 2 =>
            case Field is
               when 0 => return D.Raw_Packet'Size / System.Storage_Unit;
               when 1 => return D.Raw_Packet'Alignment;
               when 2 => return R.Ledger'Position;
               when 3 => return R.Captured'Position;
               when others => return -1;
            end case;
         when others => return -1;
      end case;
      end;
   exception
      when others => return -1;
   end Resource_Actor_Layout;
   function Resource_Actor_Check
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      History : System.Address;
      History_Count : Interfaces.C.size_t;
      Proposed_History : System.Address;
      Proposed_History_Count : Interfaces.C.size_t;
      Rows : System.Address;
      Rows_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address;
      Proposed_Rows_Count : Interfaces.C.size_t;
      Projection : System.Address;
      Projection_Count : Interfaces.C.size_t;
      Proposed_Projection : System.Address;
      Proposed_Projection_Count : Interfaces.C.size_t;
      Buckets : System.Address;
      Buckets_Count : Interfaces.C.size_t;
      Proposed_Buckets : System.Address;
      Proposed_Buckets_Count : Interfaces.C.size_t;
      Actual_Buckets : System.Address;
      Actual_Buckets_Count : Interfaces.C.size_t;
      Observed : System.Address;
      Observed_Count : Interfaces.C.size_t;
      Facts : System.Address;
      Facts_Count : Interfaces.C.size_t;
      Capabilities : System.Address;
      Capabilities_Count : Interfaces.C.size_t;
      Groups : System.Address;
      Groups_Count : Interfaces.C.size_t;
      Proc_Groups : System.Address;
      Proc_Groups_Count : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Native renames Worldline.Native_Execution_Capture;
      package N renames V.N;
      package W renames V.W;
      package O renames V.O;
      package Q renames V.Q;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.long;
      use type Interfaces.C.int;
      package Raw_Pointers is new System.Address_To_Access_Conversions (D.Raw_Packet);
      package Output_Pointers is new System.Address_To_Access_Conversions (W.Raw_Result);
   begin
      if Input_Length /= D.Raw_Packet'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Input, Input_Length)
        or else To_Integer (Input) mod D.Raw_Packet'Alignment /= 0
        or else not Native_Execution_Array_Shape (Arena, Arena_Length, Q.Byte'Size / System.Storage_Unit, Q.Byte'Alignment)
        or else not Native_Execution_Array_Shape (History, History_Count, N.Raw_Scope_Frame'Size / System.Storage_Unit, N.Raw_Scope_Frame'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_History, Proposed_History_Count, N.Raw_Scope_Frame'Size / System.Storage_Unit, N.Raw_Scope_Frame'Alignment)
        or else not Native_Execution_Array_Shape (Rows, Rows_Count, W.Raw_Row'Size / System.Storage_Unit, W.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Rows, Proposed_Rows_Count, W.Raw_Row'Size / System.Storage_Unit, W.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Projection, Projection_Count, N.Raw_Projection'Size / System.Storage_Unit, N.Raw_Projection'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Projection, Proposed_Projection_Count, N.Raw_Projection'Size / System.Storage_Unit, N.Raw_Projection'Alignment)
        or else not Native_Execution_Array_Shape (Buckets, Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Buckets, Proposed_Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Actual_Buckets, Actual_Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Observed, Observed_Count, W.Raw_Native'Size / System.Storage_Unit, W.Raw_Native'Alignment)
        or else not Native_Execution_Array_Shape (Facts, Facts_Count, O.Raw_Facts'Size / System.Storage_Unit, O.Raw_Facts'Alignment)
        or else not Native_Execution_Array_Shape (Capabilities, Capabilities_Count, D.Raw_Capability'Size / System.Storage_Unit, D.Raw_Capability'Alignment)
        or else not Native_Execution_Array_Shape (Groups, Groups_Count, W.Raw_Quantity'Size / System.Storage_Unit, W.Raw_Quantity'Alignment)
        or else not Native_Execution_Array_Shape (Proc_Groups, Proc_Groups_Count, W.Raw_Quantity'Size / System.Storage_Unit, W.Raw_Quantity'Alignment)
        or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Output, Output_Length)
        or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Arena_Length));
         Data_View : constant Resource_Bytes_Observer :=
           Observe_Resource_Bytes (Arena, Data_Bounds);
         History_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (History_Count));
         History_View : constant Native_History_Observer :=
           Observe_Native_History (History, History_Bounds);
         Proposed_History_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_History_Count));
         Proposed_History_View : constant Native_History_Observer :=
           Observe_Native_History (Proposed_History, Proposed_History_Bounds);
         Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Rows_Count));
         Rows_View : constant Native_Rows_Observer :=
           Observe_Native_Rows (Rows, Rows_Bounds);
         Proposed_Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Rows_Count));
         Proposed_Rows_View : constant Native_Rows_Observer :=
           Observe_Native_Rows (Proposed_Rows, Proposed_Rows_Bounds);
         Projection_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Projection_Count));
         Projection_View : constant Native_Projection_Observer :=
           Observe_Native_Projection (Projection, Projection_Bounds);
         Proposed_Projection_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Projection_Count));
         Proposed_Projection_View : constant Native_Projection_Observer :=
           Observe_Native_Projection (Proposed_Projection, Proposed_Projection_Bounds);
         Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Buckets_Count));
         Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Buckets, Buckets_Bounds);
         Proposed_Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Buckets_Count));
         Proposed_Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Proposed_Buckets, Proposed_Buckets_Bounds);
         Actual_Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Actual_Buckets_Count));
         Actual_Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Actual_Buckets, Actual_Buckets_Bounds);
         Observed_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Observed_Count));
         Observed_View : constant Native_Observed_Observer :=
           Observe_Native_Observed (Observed, Observed_Bounds);
         Facts_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Facts_Count));
         Facts_View : constant Native_Facts_Observer :=
           Observe_Native_Facts (Facts, Facts_Bounds);
         Capabilities_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Capabilities_Count));
         Capabilities_View : constant Native_Capabilities_Observer :=
           Observe_Native_Capabilities (Capabilities, Capabilities_Bounds);
         Groups_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Groups_Count));
         Groups_View : constant Native_Groups_Observer :=
           Observe_Native_Groups (Groups, Groups_Bounds);
         Proc_Groups_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proc_Groups_Count));
         Proc_Groups_View : constant Native_Groups_Observer :=
           Observe_Native_Groups (Proc_Groups, Proc_Groups_Bounds);
         Result : constant V.Result := Native.Actor_Check (Raw_Pointers.To_Pointer (Input), Data_View, History_View, Proposed_History_View, Rows_View, Proposed_Rows_View, Projection_View, Proposed_Projection_View, Buckets_View, Proposed_Buckets_View, Actual_Buckets_View, Observed_View, Facts_View, Capabilities_View, Groups_View, Proc_Groups_View);
      begin
         Flush_Native_Diagnostic_Trace;
         if not Result.Well_Formed then return -1; end if;
         Output_Pointers.To_Pointer (Output).all := (Status => Result.Status);
      end;
      return 0;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return -1;
      end;
   exception
      when others => return -1;
   end Resource_Actor_Check;
   function Resource_Actor_Execution_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return 1;
      end;
   exception
      when others => return 0;
   end Resource_Actor_Execution_Version;
   function Resource_Actor_Execution_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Native renames Worldline.Native_Execution_Capture;
      package N renames V.N;
      package W renames V.W;
      package Q renames V.Q;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.long;
      use type Interfaces.C.int;
      O : D.Raw_Observation;
      C : D.Raw_Capability;
      R : D.Raw_Packet;
      Cw : X.Raw_Crosswalk;
   begin
      case Kind is
         when 0 =>
            case Field is
               when 0 => return D.Raw_Observation'Size / System.Storage_Unit;
               when 1 => return D.Raw_Observation'Alignment;
               when 2 => return O.Bound'Position;
               when 3 => return O.Raw_Frame'Position;
               when 4 => return O.Raw_Sender'Position;
               when 5 => return O.Ticket'Position;
               when 6 => return O.Raw_Proc_Status'Position;
               when 7 => return O.Raw_Proc_Cgroup'Position;
               when 8 => return O.Raw_Proc_Maps'Position;
               when 9 => return O.Raw_Proc_Cmdline'Position;
               when 10 => return O.Raw_Pidfd_Info'Position;
               when 11 => return O.Namespace'Position;
               when 12 => return O.Held_Namespace'Position;
               when 13 => return O.Helper_Image'Position;
               when 14 => return O.Expected_Helper_Image'Position;
               when 15 => return O.Executable_Plan'Position;
               when 16 => return O.Expected_Executable_Plan'Position;
               when 17 => return O.Original_Requester'Position;
               when 18 => return O.Requester_Credentials'Position;
               when 19 => return O.Expected_Requester_Credentials'Position;
               when 20 => return O.Dispatch'Position;
               when 21 => return O.Running_Event'Position;
               when 22 => return O.Expected_Running_Event'Position;
               when 23 => return O.Canonical_Use_Event'Position;
               when 24 => return O.Expected_Canonical_Use_Event'Position;
               when 25 => return O.Store_Genesis'Position;
               when 26 => return O.Expected_Store_Genesis'Position;
               when 27 => return O.Source_Lease'Position;
               when 28 => return O.Expected_Source_Lease'Position;
               when 29 => return O.Actor_Wait'Position;
               when 30 => return O.Helper_Wait'Position;
               when 31 => return O.Namespace_Wait'Position;
               when 32 => return O.Host_Pid'Position;
               when 33 => return O.Namespace_Pid'Position;
               when 34 => return O.Sender_Uid'Position;
               when 35 => return O.Sender_Gid'Position;
               when 36 => return O.Real_Uid'Position;
               when 37 => return O.Effective_Uid'Position;
               when 38 => return O.Saved_Uid'Position;
               when 39 => return O.Real_Gid'Position;
               when 40 => return O.Effective_Gid'Position;
               when 41 => return O.Saved_Gid'Position;
               when 42 => return O.Capability_Version'Position;
               when 43 => return O.Effective_Low'Position;
               when 44 => return O.Permitted_Low'Position;
               when 45 => return O.Inheritable_Low'Position;
               when 46 => return O.Effective_High'Position;
               when 47 => return O.Permitted_High'Position;
               when 48 => return O.Inheritable_High'Position;
               when 49 => return O.Securebits'Position;
               when 50 => return O.No_New_Privs'Position;
               when 51 => return O.Requester_Uid'Position;
               when 52 => return O.Requester_Gid'Position;
               when 53 => return O.Configured_Requester_Uid'Position;
               when 54 => return O.Workload_Uid'Position;
               when 55 => return O.Workload_Gid'Position;
               when 56 => return O.Proc_Host_Pid'Position;
               when 57 => return O.Proc_Namespace_Pid'Position;
               when 58 => return O.Proc_Real_Uid'Position;
               when 59 => return O.Proc_Effective_Uid'Position;
               when 60 => return O.Proc_Saved_Uid'Position;
               when 61 => return O.Proc_Real_Gid'Position;
               when 62 => return O.Proc_Effective_Gid'Position;
               when 63 => return O.Proc_Saved_Gid'Position;
               when 64 => return O.Proc_Effective'Position;
               when 65 => return O.Proc_Permitted'Position;
               when 66 => return O.Proc_Inheritable'Position;
               when 67 => return O.Proc_Bounding'Position;
               when 68 => return O.Proc_Ambient'Position;
               when 69 => return O.Proc_No_New_Privs'Position;
               when 70 => return O.Proc_Fs_Uid'Position;
               when 71 => return O.Proc_Fs_Gid'Position;
               when others => return -1;
            end case;
         when 1 =>
            case Field is
               when 0 => return D.Raw_Capability'Size / System.Storage_Unit;
               when 1 => return D.Raw_Capability'Alignment;
               when 2 => return C.Index'Position;
               when 3 => return C.Bounding'Position;
               when 4 => return C.Ambient'Position;
               when others => return -1;
            end case;
         when 2 =>
            case Field is
               when 0 => return D.Raw_Packet'Size / System.Storage_Unit;
               when 1 => return D.Raw_Packet'Alignment;
               when 2 => return R.Ledger'Position;
               when 3 => return R.Captured'Position;
               when others => return -1;
            end case;
         when 3 =>
            case Field is
               when 0 => return X.Raw_Crosswalk'Size / System.Storage_Unit;
               when 1 => return X.Raw_Crosswalk'Alignment;
               when 2 => return Cw.Resource_Current'Position;
               when 3 => return Cw.Operation_Policy'Position;
               when 4 => return Cw.Operation_Root_Set'Position;
               when 5 => return Cw.Owner_Genesis'Position;
               when 6 => return Cw.Installation'Position;
               when 7 => return Cw.Gate_Config'Position;
               when 8 => return Cw.Managed_Observation'Position;
               when 9 => return Cw.Original_Grant'Position;
               when 10 => return Cw.Complete_Crosswalk'Position;
               when 11 => return Cw.Current_Source'Position;
               when 12 => return Cw.Original_Request'Position;
               when 13 => return Cw.Original_Requester'Position;
               when 14 => return Cw.Original_Transaction'Position;
               when 15 => return Cw.Preparer'Position;
               when 16 => return Cw.Selected_Plan'Position;
               when others => return -1;
            end case;
         when others => return -1;
      end case;
      end;
   exception
      when others => return -1;
   end Resource_Actor_Execution_Layout;
   function Resource_Actor_Execution_Decide
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      History : System.Address;
      History_Count : Interfaces.C.size_t;
      Proposed_History : System.Address;
      Proposed_History_Count : Interfaces.C.size_t;
      Rows : System.Address;
      Rows_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address;
      Proposed_Rows_Count : Interfaces.C.size_t;
      Projection : System.Address;
      Projection_Count : Interfaces.C.size_t;
      Proposed_Projection : System.Address;
      Proposed_Projection_Count : Interfaces.C.size_t;
      Buckets : System.Address;
      Buckets_Count : Interfaces.C.size_t;
      Proposed_Buckets : System.Address;
      Proposed_Buckets_Count : Interfaces.C.size_t;
      Actual_Buckets : System.Address;
      Actual_Buckets_Count : Interfaces.C.size_t;
      Observed : System.Address;
      Observed_Count : Interfaces.C.size_t;
      Facts : System.Address;
      Facts_Count : Interfaces.C.size_t;
      Capabilities : System.Address;
      Capabilities_Count : Interfaces.C.size_t;
      Groups : System.Address;
      Groups_Count : Interfaces.C.size_t;
      Proc_Groups : System.Address;
      Proc_Groups_Count : Interfaces.C.size_t;
      Authority_Input : System.Address;
      Authority_Input_Length : Interfaces.C.size_t;
      Authority_Arena : System.Address;
      Authority_Arena_Length : Interfaces.C.size_t;
      Authority_Grants : System.Address;
      Authority_Grants_Count : Interfaces.C.size_t;
      Authority_Uses : System.Address;
      Authority_Uses_Count : Interfaces.C.size_t;
      Authority_Receipts : System.Address;
      Authority_Receipts_Count : Interfaces.C.size_t;
      Authority_Events : System.Address;
      Authority_Events_Count : Interfaces.C.size_t;
      Crosswalk : System.Address;
      Crosswalk_Length : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Native renames Worldline.Native_Execution_Capture;
      package N renames V.N;
      package W renames V.W;
      package O renames V.O;
      package Q renames V.Q;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.long;
      use type Interfaces.C.int;
      package Raw_Pointers is new System.Address_To_Access_Conversions (D.Raw_Packet);
      package Authority_Pointers is new System.Address_To_Access_Conversions (T.Raw_Input);
      package Crosswalk_Pointers is new System.Address_To_Access_Conversions (X.Raw_Crosswalk);
      package Output_Pointers is new System.Address_To_Access_Conversions (W.Raw_Result);
   begin
      if Input_Length /= D.Raw_Packet'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Input, Input_Length)
        or else To_Integer (Input) mod D.Raw_Packet'Alignment /= 0
        or else not Native_Execution_Array_Shape (Arena, Arena_Length, Q.Byte'Size / System.Storage_Unit, Q.Byte'Alignment)
        or else not Native_Execution_Array_Shape (History, History_Count, N.Raw_Scope_Frame'Size / System.Storage_Unit, N.Raw_Scope_Frame'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_History, Proposed_History_Count, N.Raw_Scope_Frame'Size / System.Storage_Unit, N.Raw_Scope_Frame'Alignment)
        or else not Native_Execution_Array_Shape (Rows, Rows_Count, W.Raw_Row'Size / System.Storage_Unit, W.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Rows, Proposed_Rows_Count, W.Raw_Row'Size / System.Storage_Unit, W.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Projection, Projection_Count, N.Raw_Projection'Size / System.Storage_Unit, N.Raw_Projection'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Projection, Proposed_Projection_Count, N.Raw_Projection'Size / System.Storage_Unit, N.Raw_Projection'Alignment)
        or else not Native_Execution_Array_Shape (Buckets, Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Buckets, Proposed_Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Actual_Buckets, Actual_Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Observed, Observed_Count, W.Raw_Native'Size / System.Storage_Unit, W.Raw_Native'Alignment)
        or else not Native_Execution_Array_Shape (Facts, Facts_Count, O.Raw_Facts'Size / System.Storage_Unit, O.Raw_Facts'Alignment)
        or else not Native_Execution_Array_Shape (Capabilities, Capabilities_Count, D.Raw_Capability'Size / System.Storage_Unit, D.Raw_Capability'Alignment)
        or else not Native_Execution_Array_Shape (Groups, Groups_Count, W.Raw_Quantity'Size / System.Storage_Unit, W.Raw_Quantity'Alignment)
        or else not Native_Execution_Array_Shape (Proc_Groups, Proc_Groups_Count, W.Raw_Quantity'Size / System.Storage_Unit, W.Raw_Quantity'Alignment)
        or else Authority_Input_Length /= T.Raw_Input'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Authority_Input, Authority_Input_Length)
        or else To_Integer (Authority_Input) mod T.Raw_Input'Alignment /= 0
        or else not Native_Execution_Array_Shape (Authority_Arena, Authority_Arena_Length, Q.Byte'Size / System.Storage_Unit, Q.Byte'Alignment)
        or else not Native_Execution_Array_Shape (Authority_Grants, Authority_Grants_Count, T.Raw_Grant'Size / System.Storage_Unit, T.Raw_Grant'Alignment)
        or else not Native_Execution_Array_Shape (Authority_Uses, Authority_Uses_Count, T.Raw_Use'Size / System.Storage_Unit, T.Raw_Use'Alignment)
        or else not Native_Execution_Array_Shape (Authority_Receipts, Authority_Receipts_Count, T.C.Raw_Row'Size / System.Storage_Unit, T.C.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Authority_Events, Authority_Events_Count, T.C.Raw_Row'Size / System.Storage_Unit, T.C.Raw_Row'Alignment)
        or else Crosswalk_Length /= X.Raw_Crosswalk'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Crosswalk, Crosswalk_Length)
        or else To_Integer (Crosswalk) mod X.Raw_Crosswalk'Alignment /= 0
        or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Output, Output_Length)
        or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Arena_Length));
         Data_View : constant Resource_Bytes_Observer :=
           Observe_Resource_Bytes (Arena, Data_Bounds);
         History_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (History_Count));
         History_View : constant Native_History_Observer :=
           Observe_Native_History (History, History_Bounds);
         Proposed_History_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_History_Count));
         Proposed_History_View : constant Native_History_Observer :=
           Observe_Native_History (Proposed_History, Proposed_History_Bounds);
         Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Rows_Count));
         Rows_View : constant Native_Rows_Observer :=
           Observe_Native_Rows (Rows, Rows_Bounds);
         Proposed_Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Rows_Count));
         Proposed_Rows_View : constant Native_Rows_Observer :=
           Observe_Native_Rows (Proposed_Rows, Proposed_Rows_Bounds);
         Projection_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Projection_Count));
         Projection_View : constant Native_Projection_Observer :=
           Observe_Native_Projection (Projection, Projection_Bounds);
         Proposed_Projection_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Projection_Count));
         Proposed_Projection_View : constant Native_Projection_Observer :=
           Observe_Native_Projection (Proposed_Projection, Proposed_Projection_Bounds);
         Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Buckets_Count));
         Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Buckets, Buckets_Bounds);
         Proposed_Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Buckets_Count));
         Proposed_Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Proposed_Buckets, Proposed_Buckets_Bounds);
         Actual_Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Actual_Buckets_Count));
         Actual_Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Actual_Buckets, Actual_Buckets_Bounds);
         Observed_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Observed_Count));
         Observed_View : constant Native_Observed_Observer :=
           Observe_Native_Observed (Observed, Observed_Bounds);
         Facts_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Facts_Count));
         Facts_View : constant Native_Facts_Observer :=
           Observe_Native_Facts (Facts, Facts_Bounds);
         Capabilities_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Capabilities_Count));
         Capabilities_View : constant Native_Capabilities_Observer :=
           Observe_Native_Capabilities (Capabilities, Capabilities_Bounds);
         Groups_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Groups_Count));
         Groups_View : constant Native_Groups_Observer :=
           Observe_Native_Groups (Groups, Groups_Bounds);
         Proc_Groups_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proc_Groups_Count));
         Proc_Groups_View : constant Native_Groups_Observer :=
           Observe_Native_Groups (Proc_Groups, Proc_Groups_Bounds);
         Authority_Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Authority_Arena_Length));
         Authority_Data_View : constant Resource_Bytes_Observer :=
           Observe_Resource_Bytes (Authority_Arena, Authority_Data_Bounds);
         Authority_Grants_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Authority_Grants_Count));
         Authority_Grants_View : constant Native_Grants_Observer :=
           Observe_Native_Grants (Authority_Grants, Authority_Grants_Bounds);
         Authority_Uses_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Authority_Uses_Count));
         Authority_Uses_View : constant Native_Uses_Observer :=
           Observe_Native_Uses (Authority_Uses, Authority_Uses_Bounds);
         Authority_Receipts_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Authority_Receipts_Count));
         Authority_Receipts_View : constant Native_Chain_Observer :=
           Observe_Native_Chain (Authority_Receipts, Authority_Receipts_Bounds);
         Authority_Events_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Authority_Events_Count));
         Authority_Events_View : constant Native_Chain_Observer :=
           Observe_Native_Chain (Authority_Events, Authority_Events_Bounds);
         Result : constant V.Result := Native.Execution_Decide (Raw_Pointers.To_Pointer (Input), Data_View, History_View, Proposed_History_View, Rows_View, Proposed_Rows_View, Projection_View, Proposed_Projection_View, Buckets_View, Proposed_Buckets_View, Actual_Buckets_View, Observed_View, Facts_View, Capabilities_View, Groups_View, Proc_Groups_View, Authority_Pointers.To_Pointer (Authority_Input), Authority_Data_View, Authority_Grants_View, Authority_Uses_View, Authority_Receipts_View, Authority_Events_View, Crosswalk_Pointers.To_Pointer (Crosswalk));
      begin
         Flush_Native_Diagnostic_Trace;
         if not Result.Well_Formed then return -1; end if;
         Output_Pointers.To_Pointer (Output).all := (Status => Result.Status);
      end;
      return 0;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return -1;
      end;
   exception
      when others => return -1;
   end Resource_Actor_Execution_Decide;
   function Child_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return 1;
      end;
   exception
      when others => return 0;
   end Child_Version;
   function Child_Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package N renames V.N;
      package W renames V.W;
      package O renames V.O;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use type Interfaces.Unsigned_32;
      use type Interfaces.C.long;
   type Record_Kind is (D_Raw_Observation, D_Raw_Capability, D_Raw_Packet, X_Raw_Crosswalk, W_Raw_Id, W_Raw_Quantity, W_Raw_Epoch, W_Raw_Context, W_Raw_Binding, W_Raw_Row, W_Raw_State, W_Raw_Native, W_Raw_Request, W_Raw_Packet, W_Raw_Result, N_Raw_State, N_Raw_Scope_Frame, N_Raw_Physical_Key, N_Raw_Bucket, N_Raw_Projection, N_Raw_Current_Observation, N_Raw_Intent, N_Raw_Packet, O_Raw_Facts, O_Raw_Input, T_Raw_Quantity, T_Raw_UID, T_Raw_Binding, T_Raw_Grant, T_Raw_Use, T_Raw_Evidence, T_Raw_Input, T_Raw_Result, TC_Raw_Digest, TC_Raw_Row, TC_Raw_Anchors, TC_Raw_Result, Y_Raw_Process, Y_Raw_Controller, Y_Raw_Task, Y_Raw_Namespace, Y_Raw_Input);
   type D_Raw_Observation_Field is (Size, Alignment, F_Bound, F_Raw_Frame, F_Raw_Sender, F_Ticket, F_Raw_Proc_Status, F_Raw_Proc_Cgroup, F_Raw_Proc_Maps, F_Raw_Proc_Cmdline, F_Raw_Pidfd_Info, F_Namespace, F_Held_Namespace, F_Helper_Image, F_Expected_Helper_Image, F_Executable_Plan, F_Expected_Executable_Plan, F_Original_Requester, F_Requester_Credentials, F_Expected_Requester_Credentials, F_Dispatch, F_Running_Event, F_Expected_Running_Event, F_Canonical_Use_Event, F_Expected_Canonical_Use_Event, F_Store_Genesis, F_Expected_Store_Genesis, F_Source_Lease, F_Expected_Source_Lease, F_Actor_Wait, F_Helper_Wait, F_Namespace_Wait, F_Host_Pid, F_Namespace_Pid, F_Sender_Uid, F_Sender_Gid, F_Real_Uid, F_Effective_Uid, F_Saved_Uid, F_Real_Gid, F_Effective_Gid, F_Saved_Gid, F_Capability_Version, F_Effective_Low, F_Permitted_Low, F_Inheritable_Low, F_Effective_High, F_Permitted_High, F_Inheritable_High, F_Securebits, F_No_New_Privs, F_Requester_Uid, F_Requester_Gid, F_Configured_Requester_Uid, F_Workload_Uid, F_Workload_Gid, F_Proc_Host_Pid, F_Proc_Namespace_Pid, F_Proc_Real_Uid, F_Proc_Effective_Uid, F_Proc_Saved_Uid, F_Proc_Real_Gid, F_Proc_Effective_Gid, F_Proc_Saved_Gid, F_Proc_Effective, F_Proc_Permitted, F_Proc_Inheritable, F_Proc_Bounding, F_Proc_Ambient, F_Proc_No_New_Privs, F_Proc_Fs_Uid, F_Proc_Fs_Gid);
   type D_Raw_Capability_Field is (Size, Alignment, F_Index, F_Bounding, F_Ambient);
   type D_Raw_Packet_Field is (Size, Alignment, F_Ledger, F_Captured);
   type X_Raw_Crosswalk_Field is (Size, Alignment, F_Resource_Current, F_Operation_Policy, F_Operation_Root_Set, F_Owner_Genesis, F_Installation, F_Gate_Config, F_Managed_Observation, F_Original_Grant, F_Complete_Crosswalk, F_Current_Source, F_Original_Request, F_Original_Requester, F_Original_Transaction, F_Preparer, F_Selected_Plan);
   type W_Raw_Id_Field is (Size, Alignment, F_Present, F_First, F_Length);
   type W_Raw_Quantity_Field is (Size, Alignment, F_Negative, F_First, F_Length);
   type W_Raw_Epoch_Field is (Size, Alignment, F_Present, F_Value);
   type W_Raw_Context_Field is (Size, Alignment, F_Universe, F_Policy, F_Resource, F_Unit, F_Instance, F_Host, F_Boot, F_Authority, F_Policy_Epoch);
   type W_Raw_Binding_Field is (Size, Alignment, F_Reservation, F_Operation, F_Owner, F_Workload, F_Universe_Head, F_Capability, F_Grant_Use, F_Payload, F_Provenance, F_Resource_Epoch);
   type W_Raw_Row_Field is (Size, Alignment, F_Scope, F_Bound, F_Parent, F_Kind, F_State, F_Amount, F_Observed_Usage, F_Planned_Unit, F_Actual_Unit, F_Cgroup, F_Invocation);
   type W_Raw_State_Field is (Size, Alignment, F_Scope, F_Resource_Epoch, F_Universe_Head, F_Ledger_Head, F_Capacity, F_Held_Total, F_Charged_Total);
   type W_Raw_Native_Field is (Size, Alignment, F_Scope, F_Resource_Epoch, F_Bound, F_Actual_Unit, F_Cgroup, F_Invocation, F_Observation_Head, F_Observed);
   type W_Raw_Request_Field is (Size, Alignment, F_Kind, F_Scope, F_Expected_Epoch, F_Expected_Ledger_Head, F_Request_Id, F_Reservation, F_Operation_Id, F_Requester, F_Bound, F_New_Row);
   type W_Raw_Packet_Field is (Size, Alignment, F_Schema_Version, F_Before_State, F_Proposed_State, F_Intent);
   type W_Raw_Result_Field is (Size, Alignment, F_Status);
   type N_Raw_State_Field is (Size, Alignment, F_Current, F_Resource_Epoch, F_Universe_Head, F_Ledger_Head, F_History_Head, F_Physical_Head);
   type N_Raw_Scope_Frame_Field is (Size, Alignment, F_Scope, F_First_Epoch, F_Universe_Head, F_Frame_Head, F_Prior_Frame, F_Store_Genesis, F_Store_Id, F_Root_Head, F_Prime, F_Root_Count, F_Cause, F_Requester, F_Receipt, F_Catalogue_Head, F_Observation_Head);
   type N_Raw_Physical_Key_Field is (Size, Alignment, F_Machine, F_Resource, F_Unit);
   type N_Raw_Bucket_Field is (Size, Alignment, F_Key, F_Capacity, F_Held_Total, F_Charged_Total, F_Capacity_Source, F_Catalogue_Head, F_Observation_Head);
   type N_Raw_Projection_Field is (Size, Alignment, F_Key, F_Bound, F_Origin, F_Catalogue_Head, F_Numerator, F_Denominator, F_Amount);
   type N_Raw_Current_Observation_Field is (Size, Alignment, F_Scope, F_Resource_Epoch, F_Universe_Head, F_Ledger_Head, F_History_Head, F_Physical_Head, F_Store_Genesis, F_Store_Id, F_Root_Head, F_Prime, F_Root_Count, F_Cause, F_Requester, F_Receipt, F_Catalogue_Head, F_Observation_Head);
   type N_Raw_Intent_Field is (Size, Alignment, F_Kind, F_Original, F_Expected_Epoch, F_Expected_Ledger_Head, F_Request_Id, F_Cause, F_Requester, F_Receipt);
   type N_Raw_Packet_Field is (Size, Alignment, F_Schema_Version, F_Before_State, F_Proposed_State, F_Current, F_Request);
   type O_Raw_Facts_Field is (Size, Alignment, F_Current, F_Current_Epoch, F_Retained, F_Current_Universe_Head, F_Current_Ledger_Head, F_Intent, F_Dispatch, F_Observation_Head, F_Actual_Unit, F_Cgroup, F_Invocation, F_Namespace, F_Held_Namespace, F_Peer, F_Held_Peer, F_Helper_Image, F_Expected_Helper_Image, F_Challenge, F_Held_Challenge, F_Protocol, F_Closed_Event, F_Namespace_Wait, F_Helper_Wait, F_Cgroup_Events, F_Cgroup_Type, F_Manager_Delegate, F_Cgroup_Owner, F_Cgroup_Group_Write, F_Cgroup_Other_Write, F_Actual_Store_Genesis, F_Actual_Store_Id, F_Owner_Store_Genesis, F_Owner_Store_Id, F_Genesis_Universe, F_Genesis_Instance, F_Genesis_Context_Head, F_Genesis_Prime, F_Genesis_Root_Count, F_Phase);
   type O_Raw_Input_Field is (Size, Alignment, F_State, F_Item, F_Captured);
   type T_Raw_Quantity_Field is (Size, Alignment, F_Present, F_Negative, F_First, F_Length);
   type T_Raw_UID_Field is (Size, Alignment, F_Present, F_Value);
   type T_Raw_Binding_Field is (Size, Alignment, F_Action, F_Id, F_Peer, F_Preparer, F_Owner, F_Target_Owner, F_Policy_Epoch, F_Resource_Epoch);
   type T_Raw_Grant_Field is (Size, Alignment, F_Id, F_Parent, F_Issuer, F_Instance, F_Root_Set, F_Policy, F_Subject, F_Owner, F_Allowed, F_State, F_Epoch, F_Ceiling, F_Issued_At, F_Expires_At);
   type T_Raw_Use_Field is (Size, Alignment, F_Bound, F_State);
   type T_Raw_Evidence_Field is (Size, Alignment, F_Effect_Binding, F_Actual_Receipt_Root, F_Actual_Causal_Root, F_No_Effect_Binding, F_Owner_Resolution, F_Quarantine_Head, F_Witnessed_Receipt_Head, F_Witnessed_Causal_Head, F_Recovery, F_Original_Use, F_Effect_Material_First, F_Effect_Material_Length);
   type T_Raw_Input_Field is (Size, Alignment, F_Schema, F_Mode, F_Bound, F_Now, F_Facts);
   type T_Raw_Result_Field is (Size, Alignment, F_Disposition);
   type TC_Raw_Digest_Field is (Size, Alignment, F_Present, F_Value);
   type TC_Raw_Row_Field is (Size, Alignment, F_Previous, F_Actual_Payload_Root, F_Stored_Payload_Root, F_Stored_Head);
   type TC_Raw_Anchors_Field is (Size, Alignment, F_Kind, F_Observed_Genesis, F_Witnessed_Genesis, F_Witnessed_Head);
   type TC_Raw_Result_Field is (Size, Alignment, F_Disposition, F_Head, F_Accepted_Count);
   type Y_Raw_Process_Field is (Size, Alignment, F_raw_status, F_raw_stat, F_raw_cgroup, F_raw_maps, F_raw_cmdline, F_raw_pidfd_info, F_namespace, F_cgroup, F_actual_unit, F_invocation, F_source_lease, F_pidfd_wait, F_host_pid, F_start_tick, F_parent_pid, F_parent_start_tick, F_real_uid, F_effective_uid, F_saved_uid, F_real_gid, F_effective_gid, F_saved_gid);
   type Y_Raw_Controller_Field is (Size, Alignment, F_Bound, F_Process, F_Requester_Uid, F_Requester_Gid, F_raw_manager, F_raw_channel, F_owner_endpoint, F_expected_owner_endpoint, F_source_lease, F_expected_source_lease, F_worker_image, F_expected_worker_image, F_handler_plan, F_expected_handler_plan, F_raw_request, F_requester, F_dispatch, F_running_event, F_expected_running_event, F_store_genesis, F_expected_store_genesis, F_current_source);
   type Y_Raw_Task_Field is (Size, Alignment, F_Action, F_Root, F_Child, F_task_id, F_root_world, F_child_world, F_root_instance, F_child_instance, F_world_store, F_full_world_ancestry, F_original_workload, F_sandbox, F_adapter, F_context, F_mission, F_stdin, F_credential_source, F_executable_source, F_configuration, F_owner_plan, F_native_cost_input, F_raw_request, F_requester, F_cause, F_root_dispatch, F_root_running_event, F_task_journal, F_task_intent, F_task_reservation_event, F_task_launch_event, F_parent_namespace_source, F_fd_lineage, F_source_lease);
   type Y_Raw_Namespace_Field is (Size, Alignment, F_identity, F_parent, F_raw_nsfs, F_raw_get_parent, F_source_lease);
   type Y_Raw_Input_Field is (Size, Alignment, F_Mode, F_Controller, F_Task);
      V_D_Raw_Observation : D.Raw_Observation;
      V_D_Raw_Capability : D.Raw_Capability;
      V_D_Raw_Packet : D.Raw_Packet;
      V_X_Raw_Crosswalk : X.Raw_Crosswalk;
      V_W_Raw_Id : W.Raw_Id;
      V_W_Raw_Quantity : W.Raw_Quantity;
      V_W_Raw_Epoch : W.Raw_Epoch;
      V_W_Raw_Context : W.Raw_Context;
      V_W_Raw_Binding : W.Raw_Binding;
      V_W_Raw_Row : W.Raw_Row;
      V_W_Raw_State : W.Raw_State;
      V_W_Raw_Native : W.Raw_Native;
      V_W_Raw_Request : W.Raw_Request;
      V_W_Raw_Packet : W.Raw_Packet;
      V_W_Raw_Result : W.Raw_Result;
      V_N_Raw_State : N.Raw_State;
      V_N_Raw_Scope_Frame : N.Raw_Scope_Frame;
      V_N_Raw_Physical_Key : N.Raw_Physical_Key;
      V_N_Raw_Bucket : N.Raw_Bucket;
      V_N_Raw_Projection : N.Raw_Projection;
      V_N_Raw_Current_Observation : N.Raw_Current_Observation;
      V_N_Raw_Intent : N.Raw_Intent;
      V_N_Raw_Packet : N.Raw_Packet;
      V_O_Raw_Facts : O.Raw_Facts;
      V_O_Raw_Input : O.Raw_Input;
      V_T_Raw_Quantity : T.Raw_Quantity;
      V_T_Raw_UID : T.Raw_UID;
      V_T_Raw_Binding : T.Raw_Binding;
      V_T_Raw_Grant : T.Raw_Grant;
      V_T_Raw_Use : T.Raw_Use;
      V_T_Raw_Evidence : T.Raw_Evidence;
      V_T_Raw_Input : T.Raw_Input;
      V_T_Raw_Result : T.Raw_Result;
      V_TC_Raw_Digest : T.C.Raw_Digest;
      V_TC_Raw_Row : T.C.Raw_Row;
      V_TC_Raw_Anchors : T.C.Raw_Anchors;
      V_TC_Raw_Result : T.C.Raw_Result;
      V_Y_Raw_Process : Y.Raw_Process;
      V_Y_Raw_Controller : Y.Raw_Controller;
      V_Y_Raw_Task : Y.Raw_Task;
      V_Y_Raw_Namespace : Y.Raw_Namespace;
      V_Y_Raw_Input : Y.Raw_Input;
   begin
      if Kind > Record_Kind'Pos (Record_Kind'Last) then return -1; end if;
      case Record_Kind'Val (Kind) is
         when D_Raw_Observation =>
            if Field > D_Raw_Observation_Field'Pos (D_Raw_Observation_Field'Last) then return -1; end if;
            case D_Raw_Observation_Field'Val (Field) is
               when Size => return D.Raw_Observation'Size / System.Storage_Unit;
               when Alignment => return D.Raw_Observation'Alignment;
               when F_Bound => return V_D_Raw_Observation.Bound'Position;
               when F_Raw_Frame => return V_D_Raw_Observation.Raw_Frame'Position;
               when F_Raw_Sender => return V_D_Raw_Observation.Raw_Sender'Position;
               when F_Ticket => return V_D_Raw_Observation.Ticket'Position;
               when F_Raw_Proc_Status => return V_D_Raw_Observation.Raw_Proc_Status'Position;
               when F_Raw_Proc_Cgroup => return V_D_Raw_Observation.Raw_Proc_Cgroup'Position;
               when F_Raw_Proc_Maps => return V_D_Raw_Observation.Raw_Proc_Maps'Position;
               when F_Raw_Proc_Cmdline => return V_D_Raw_Observation.Raw_Proc_Cmdline'Position;
               when F_Raw_Pidfd_Info => return V_D_Raw_Observation.Raw_Pidfd_Info'Position;
               when F_Namespace => return V_D_Raw_Observation.Namespace'Position;
               when F_Held_Namespace => return V_D_Raw_Observation.Held_Namespace'Position;
               when F_Helper_Image => return V_D_Raw_Observation.Helper_Image'Position;
               when F_Expected_Helper_Image => return V_D_Raw_Observation.Expected_Helper_Image'Position;
               when F_Executable_Plan => return V_D_Raw_Observation.Executable_Plan'Position;
               when F_Expected_Executable_Plan => return V_D_Raw_Observation.Expected_Executable_Plan'Position;
               when F_Original_Requester => return V_D_Raw_Observation.Original_Requester'Position;
               when F_Requester_Credentials => return V_D_Raw_Observation.Requester_Credentials'Position;
               when F_Expected_Requester_Credentials => return V_D_Raw_Observation.Expected_Requester_Credentials'Position;
               when F_Dispatch => return V_D_Raw_Observation.Dispatch'Position;
               when F_Running_Event => return V_D_Raw_Observation.Running_Event'Position;
               when F_Expected_Running_Event => return V_D_Raw_Observation.Expected_Running_Event'Position;
               when F_Canonical_Use_Event => return V_D_Raw_Observation.Canonical_Use_Event'Position;
               when F_Expected_Canonical_Use_Event => return V_D_Raw_Observation.Expected_Canonical_Use_Event'Position;
               when F_Store_Genesis => return V_D_Raw_Observation.Store_Genesis'Position;
               when F_Expected_Store_Genesis => return V_D_Raw_Observation.Expected_Store_Genesis'Position;
               when F_Source_Lease => return V_D_Raw_Observation.Source_Lease'Position;
               when F_Expected_Source_Lease => return V_D_Raw_Observation.Expected_Source_Lease'Position;
               when F_Actor_Wait => return V_D_Raw_Observation.Actor_Wait'Position;
               when F_Helper_Wait => return V_D_Raw_Observation.Helper_Wait'Position;
               when F_Namespace_Wait => return V_D_Raw_Observation.Namespace_Wait'Position;
               when F_Host_Pid => return V_D_Raw_Observation.Host_Pid'Position;
               when F_Namespace_Pid => return V_D_Raw_Observation.Namespace_Pid'Position;
               when F_Sender_Uid => return V_D_Raw_Observation.Sender_Uid'Position;
               when F_Sender_Gid => return V_D_Raw_Observation.Sender_Gid'Position;
               when F_Real_Uid => return V_D_Raw_Observation.Real_Uid'Position;
               when F_Effective_Uid => return V_D_Raw_Observation.Effective_Uid'Position;
               when F_Saved_Uid => return V_D_Raw_Observation.Saved_Uid'Position;
               when F_Real_Gid => return V_D_Raw_Observation.Real_Gid'Position;
               when F_Effective_Gid => return V_D_Raw_Observation.Effective_Gid'Position;
               when F_Saved_Gid => return V_D_Raw_Observation.Saved_Gid'Position;
               when F_Capability_Version => return V_D_Raw_Observation.Capability_Version'Position;
               when F_Effective_Low => return V_D_Raw_Observation.Effective_Low'Position;
               when F_Permitted_Low => return V_D_Raw_Observation.Permitted_Low'Position;
               when F_Inheritable_Low => return V_D_Raw_Observation.Inheritable_Low'Position;
               when F_Effective_High => return V_D_Raw_Observation.Effective_High'Position;
               when F_Permitted_High => return V_D_Raw_Observation.Permitted_High'Position;
               when F_Inheritable_High => return V_D_Raw_Observation.Inheritable_High'Position;
               when F_Securebits => return V_D_Raw_Observation.Securebits'Position;
               when F_No_New_Privs => return V_D_Raw_Observation.No_New_Privs'Position;
               when F_Requester_Uid => return V_D_Raw_Observation.Requester_Uid'Position;
               when F_Requester_Gid => return V_D_Raw_Observation.Requester_Gid'Position;
               when F_Configured_Requester_Uid => return V_D_Raw_Observation.Configured_Requester_Uid'Position;
               when F_Workload_Uid => return V_D_Raw_Observation.Workload_Uid'Position;
               when F_Workload_Gid => return V_D_Raw_Observation.Workload_Gid'Position;
               when F_Proc_Host_Pid => return V_D_Raw_Observation.Proc_Host_Pid'Position;
               when F_Proc_Namespace_Pid => return V_D_Raw_Observation.Proc_Namespace_Pid'Position;
               when F_Proc_Real_Uid => return V_D_Raw_Observation.Proc_Real_Uid'Position;
               when F_Proc_Effective_Uid => return V_D_Raw_Observation.Proc_Effective_Uid'Position;
               when F_Proc_Saved_Uid => return V_D_Raw_Observation.Proc_Saved_Uid'Position;
               when F_Proc_Real_Gid => return V_D_Raw_Observation.Proc_Real_Gid'Position;
               when F_Proc_Effective_Gid => return V_D_Raw_Observation.Proc_Effective_Gid'Position;
               when F_Proc_Saved_Gid => return V_D_Raw_Observation.Proc_Saved_Gid'Position;
               when F_Proc_Effective => return V_D_Raw_Observation.Proc_Effective'Position;
               when F_Proc_Permitted => return V_D_Raw_Observation.Proc_Permitted'Position;
               when F_Proc_Inheritable => return V_D_Raw_Observation.Proc_Inheritable'Position;
               when F_Proc_Bounding => return V_D_Raw_Observation.Proc_Bounding'Position;
               when F_Proc_Ambient => return V_D_Raw_Observation.Proc_Ambient'Position;
               when F_Proc_No_New_Privs => return V_D_Raw_Observation.Proc_No_New_Privs'Position;
               when F_Proc_Fs_Uid => return V_D_Raw_Observation.Proc_Fs_Uid'Position;
               when F_Proc_Fs_Gid => return V_D_Raw_Observation.Proc_Fs_Gid'Position;
            end case;
         when D_Raw_Capability =>
            if Field > D_Raw_Capability_Field'Pos (D_Raw_Capability_Field'Last) then return -1; end if;
            case D_Raw_Capability_Field'Val (Field) is
               when Size => return D.Raw_Capability'Size / System.Storage_Unit;
               when Alignment => return D.Raw_Capability'Alignment;
               when F_Index => return V_D_Raw_Capability.Index'Position;
               when F_Bounding => return V_D_Raw_Capability.Bounding'Position;
               when F_Ambient => return V_D_Raw_Capability.Ambient'Position;
            end case;
         when D_Raw_Packet =>
            if Field > D_Raw_Packet_Field'Pos (D_Raw_Packet_Field'Last) then return -1; end if;
            case D_Raw_Packet_Field'Val (Field) is
               when Size => return D.Raw_Packet'Size / System.Storage_Unit;
               when Alignment => return D.Raw_Packet'Alignment;
               when F_Ledger => return V_D_Raw_Packet.Ledger'Position;
               when F_Captured => return V_D_Raw_Packet.Captured'Position;
            end case;
         when X_Raw_Crosswalk =>
            if Field > X_Raw_Crosswalk_Field'Pos (X_Raw_Crosswalk_Field'Last) then return -1; end if;
            case X_Raw_Crosswalk_Field'Val (Field) is
               when Size => return X.Raw_Crosswalk'Size / System.Storage_Unit;
               when Alignment => return X.Raw_Crosswalk'Alignment;
               when F_Resource_Current => return V_X_Raw_Crosswalk.Resource_Current'Position;
               when F_Operation_Policy => return V_X_Raw_Crosswalk.Operation_Policy'Position;
               when F_Operation_Root_Set => return V_X_Raw_Crosswalk.Operation_Root_Set'Position;
               when F_Owner_Genesis => return V_X_Raw_Crosswalk.Owner_Genesis'Position;
               when F_Installation => return V_X_Raw_Crosswalk.Installation'Position;
               when F_Gate_Config => return V_X_Raw_Crosswalk.Gate_Config'Position;
               when F_Managed_Observation => return V_X_Raw_Crosswalk.Managed_Observation'Position;
               when F_Original_Grant => return V_X_Raw_Crosswalk.Original_Grant'Position;
               when F_Complete_Crosswalk => return V_X_Raw_Crosswalk.Complete_Crosswalk'Position;
               when F_Current_Source => return V_X_Raw_Crosswalk.Current_Source'Position;
               when F_Original_Request => return V_X_Raw_Crosswalk.Original_Request'Position;
               when F_Original_Requester => return V_X_Raw_Crosswalk.Original_Requester'Position;
               when F_Original_Transaction => return V_X_Raw_Crosswalk.Original_Transaction'Position;
               when F_Preparer => return V_X_Raw_Crosswalk.Preparer'Position;
               when F_Selected_Plan => return V_X_Raw_Crosswalk.Selected_Plan'Position;
            end case;
         when W_Raw_Id =>
            if Field > W_Raw_Id_Field'Pos (W_Raw_Id_Field'Last) then return -1; end if;
            case W_Raw_Id_Field'Val (Field) is
               when Size => return W.Raw_Id'Size / System.Storage_Unit;
               when Alignment => return W.Raw_Id'Alignment;
               when F_Present => return V_W_Raw_Id.Present'Position;
               when F_First => return V_W_Raw_Id.First'Position;
               when F_Length => return V_W_Raw_Id.Length'Position;
            end case;
         when W_Raw_Quantity =>
            if Field > W_Raw_Quantity_Field'Pos (W_Raw_Quantity_Field'Last) then return -1; end if;
            case W_Raw_Quantity_Field'Val (Field) is
               when Size => return W.Raw_Quantity'Size / System.Storage_Unit;
               when Alignment => return W.Raw_Quantity'Alignment;
               when F_Negative => return V_W_Raw_Quantity.Negative'Position;
               when F_First => return V_W_Raw_Quantity.First'Position;
               when F_Length => return V_W_Raw_Quantity.Length'Position;
            end case;
         when W_Raw_Epoch =>
            if Field > W_Raw_Epoch_Field'Pos (W_Raw_Epoch_Field'Last) then return -1; end if;
            case W_Raw_Epoch_Field'Val (Field) is
               when Size => return W.Raw_Epoch'Size / System.Storage_Unit;
               when Alignment => return W.Raw_Epoch'Alignment;
               when F_Present => return V_W_Raw_Epoch.Present'Position;
               when F_Value => return V_W_Raw_Epoch.Value'Position;
            end case;
         when W_Raw_Context =>
            if Field > W_Raw_Context_Field'Pos (W_Raw_Context_Field'Last) then return -1; end if;
            case W_Raw_Context_Field'Val (Field) is
               when Size => return W.Raw_Context'Size / System.Storage_Unit;
               when Alignment => return W.Raw_Context'Alignment;
               when F_Universe => return V_W_Raw_Context.Universe'Position;
               when F_Policy => return V_W_Raw_Context.Policy'Position;
               when F_Resource => return V_W_Raw_Context.Resource'Position;
               when F_Unit => return V_W_Raw_Context.Unit'Position;
               when F_Instance => return V_W_Raw_Context.Instance'Position;
               when F_Host => return V_W_Raw_Context.Host'Position;
               when F_Boot => return V_W_Raw_Context.Boot'Position;
               when F_Authority => return V_W_Raw_Context.Authority'Position;
               when F_Policy_Epoch => return V_W_Raw_Context.Policy_Epoch'Position;
            end case;
         when W_Raw_Binding =>
            if Field > W_Raw_Binding_Field'Pos (W_Raw_Binding_Field'Last) then return -1; end if;
            case W_Raw_Binding_Field'Val (Field) is
               when Size => return W.Raw_Binding'Size / System.Storage_Unit;
               when Alignment => return W.Raw_Binding'Alignment;
               when F_Reservation => return V_W_Raw_Binding.Reservation'Position;
               when F_Operation => return V_W_Raw_Binding.Operation'Position;
               when F_Owner => return V_W_Raw_Binding.Owner'Position;
               when F_Workload => return V_W_Raw_Binding.Workload'Position;
               when F_Universe_Head => return V_W_Raw_Binding.Universe_Head'Position;
               when F_Capability => return V_W_Raw_Binding.Capability'Position;
               when F_Grant_Use => return V_W_Raw_Binding.Grant_Use'Position;
               when F_Payload => return V_W_Raw_Binding.Payload'Position;
               when F_Provenance => return V_W_Raw_Binding.Provenance'Position;
               when F_Resource_Epoch => return V_W_Raw_Binding.Resource_Epoch'Position;
            end case;
         when W_Raw_Row =>
            if Field > W_Raw_Row_Field'Pos (W_Raw_Row_Field'Last) then return -1; end if;
            case W_Raw_Row_Field'Val (Field) is
               when Size => return W.Raw_Row'Size / System.Storage_Unit;
               when Alignment => return W.Raw_Row'Alignment;
               when F_Scope => return V_W_Raw_Row.Scope'Position;
               when F_Bound => return V_W_Raw_Row.Bound'Position;
               when F_Parent => return V_W_Raw_Row.Parent'Position;
               when F_Kind => return V_W_Raw_Row.Kind'Position;
               when F_State => return V_W_Raw_Row.State'Position;
               when F_Amount => return V_W_Raw_Row.Amount'Position;
               when F_Observed_Usage => return V_W_Raw_Row.Observed_Usage'Position;
               when F_Planned_Unit => return V_W_Raw_Row.Planned_Unit'Position;
               when F_Actual_Unit => return V_W_Raw_Row.Actual_Unit'Position;
               when F_Cgroup => return V_W_Raw_Row.Cgroup'Position;
               when F_Invocation => return V_W_Raw_Row.Invocation'Position;
            end case;
         when W_Raw_State =>
            if Field > W_Raw_State_Field'Pos (W_Raw_State_Field'Last) then return -1; end if;
            case W_Raw_State_Field'Val (Field) is
               when Size => return W.Raw_State'Size / System.Storage_Unit;
               when Alignment => return W.Raw_State'Alignment;
               when F_Scope => return V_W_Raw_State.Scope'Position;
               when F_Resource_Epoch => return V_W_Raw_State.Resource_Epoch'Position;
               when F_Universe_Head => return V_W_Raw_State.Universe_Head'Position;
               when F_Ledger_Head => return V_W_Raw_State.Ledger_Head'Position;
               when F_Capacity => return V_W_Raw_State.Capacity'Position;
               when F_Held_Total => return V_W_Raw_State.Held_Total'Position;
               when F_Charged_Total => return V_W_Raw_State.Charged_Total'Position;
            end case;
         when W_Raw_Native =>
            if Field > W_Raw_Native_Field'Pos (W_Raw_Native_Field'Last) then return -1; end if;
            case W_Raw_Native_Field'Val (Field) is
               when Size => return W.Raw_Native'Size / System.Storage_Unit;
               when Alignment => return W.Raw_Native'Alignment;
               when F_Scope => return V_W_Raw_Native.Scope'Position;
               when F_Resource_Epoch => return V_W_Raw_Native.Resource_Epoch'Position;
               when F_Bound => return V_W_Raw_Native.Bound'Position;
               when F_Actual_Unit => return V_W_Raw_Native.Actual_Unit'Position;
               when F_Cgroup => return V_W_Raw_Native.Cgroup'Position;
               when F_Invocation => return V_W_Raw_Native.Invocation'Position;
               when F_Observation_Head => return V_W_Raw_Native.Observation_Head'Position;
               when F_Observed => return V_W_Raw_Native.Observed'Position;
            end case;
         when W_Raw_Request =>
            if Field > W_Raw_Request_Field'Pos (W_Raw_Request_Field'Last) then return -1; end if;
            case W_Raw_Request_Field'Val (Field) is
               when Size => return W.Raw_Request'Size / System.Storage_Unit;
               when Alignment => return W.Raw_Request'Alignment;
               when F_Kind => return V_W_Raw_Request.Kind'Position;
               when F_Scope => return V_W_Raw_Request.Scope'Position;
               when F_Expected_Epoch => return V_W_Raw_Request.Expected_Epoch'Position;
               when F_Expected_Ledger_Head => return V_W_Raw_Request.Expected_Ledger_Head'Position;
               when F_Request_Id => return V_W_Raw_Request.Request_Id'Position;
               when F_Reservation => return V_W_Raw_Request.Reservation'Position;
               when F_Operation_Id => return V_W_Raw_Request.Operation_Id'Position;
               when F_Requester => return V_W_Raw_Request.Requester'Position;
               when F_Bound => return V_W_Raw_Request.Bound'Position;
               when F_New_Row => return V_W_Raw_Request.New_Row'Position;
            end case;
         when W_Raw_Packet =>
            if Field > W_Raw_Packet_Field'Pos (W_Raw_Packet_Field'Last) then return -1; end if;
            case W_Raw_Packet_Field'Val (Field) is
               when Size => return W.Raw_Packet'Size / System.Storage_Unit;
               when Alignment => return W.Raw_Packet'Alignment;
               when F_Schema_Version => return V_W_Raw_Packet.Schema_Version'Position;
               when F_Before_State => return V_W_Raw_Packet.Before_State'Position;
               when F_Proposed_State => return V_W_Raw_Packet.Proposed_State'Position;
               when F_Intent => return V_W_Raw_Packet.Intent'Position;
            end case;
         when W_Raw_Result =>
            if Field > W_Raw_Result_Field'Pos (W_Raw_Result_Field'Last) then return -1; end if;
            case W_Raw_Result_Field'Val (Field) is
               when Size => return W.Raw_Result'Size / System.Storage_Unit;
               when Alignment => return W.Raw_Result'Alignment;
               when F_Status => return V_W_Raw_Result.Status'Position;
            end case;
         when N_Raw_State =>
            if Field > N_Raw_State_Field'Pos (N_Raw_State_Field'Last) then return -1; end if;
            case N_Raw_State_Field'Val (Field) is
               when Size => return N.Raw_State'Size / System.Storage_Unit;
               when Alignment => return N.Raw_State'Alignment;
               when F_Current => return V_N_Raw_State.Current'Position;
               when F_Resource_Epoch => return V_N_Raw_State.Resource_Epoch'Position;
               when F_Universe_Head => return V_N_Raw_State.Universe_Head'Position;
               when F_Ledger_Head => return V_N_Raw_State.Ledger_Head'Position;
               when F_History_Head => return V_N_Raw_State.History_Head'Position;
               when F_Physical_Head => return V_N_Raw_State.Physical_Head'Position;
            end case;
         when N_Raw_Scope_Frame =>
            if Field > N_Raw_Scope_Frame_Field'Pos (N_Raw_Scope_Frame_Field'Last) then return -1; end if;
            case N_Raw_Scope_Frame_Field'Val (Field) is
               when Size => return N.Raw_Scope_Frame'Size / System.Storage_Unit;
               when Alignment => return N.Raw_Scope_Frame'Alignment;
               when F_Scope => return V_N_Raw_Scope_Frame.Scope'Position;
               when F_First_Epoch => return V_N_Raw_Scope_Frame.First_Epoch'Position;
               when F_Universe_Head => return V_N_Raw_Scope_Frame.Universe_Head'Position;
               when F_Frame_Head => return V_N_Raw_Scope_Frame.Frame_Head'Position;
               when F_Prior_Frame => return V_N_Raw_Scope_Frame.Prior_Frame'Position;
               when F_Store_Genesis => return V_N_Raw_Scope_Frame.Store_Genesis'Position;
               when F_Store_Id => return V_N_Raw_Scope_Frame.Store_Id'Position;
               when F_Root_Head => return V_N_Raw_Scope_Frame.Root_Head'Position;
               when F_Prime => return V_N_Raw_Scope_Frame.Prime'Position;
               when F_Root_Count => return V_N_Raw_Scope_Frame.Root_Count'Position;
               when F_Cause => return V_N_Raw_Scope_Frame.Cause'Position;
               when F_Requester => return V_N_Raw_Scope_Frame.Requester'Position;
               when F_Receipt => return V_N_Raw_Scope_Frame.Receipt'Position;
               when F_Catalogue_Head => return V_N_Raw_Scope_Frame.Catalogue_Head'Position;
               when F_Observation_Head => return V_N_Raw_Scope_Frame.Observation_Head'Position;
            end case;
         when N_Raw_Physical_Key =>
            if Field > N_Raw_Physical_Key_Field'Pos (N_Raw_Physical_Key_Field'Last) then return -1; end if;
            case N_Raw_Physical_Key_Field'Val (Field) is
               when Size => return N.Raw_Physical_Key'Size / System.Storage_Unit;
               when Alignment => return N.Raw_Physical_Key'Alignment;
               when F_Machine => return V_N_Raw_Physical_Key.Machine'Position;
               when F_Resource => return V_N_Raw_Physical_Key.Resource'Position;
               when F_Unit => return V_N_Raw_Physical_Key.Unit'Position;
            end case;
         when N_Raw_Bucket =>
            if Field > N_Raw_Bucket_Field'Pos (N_Raw_Bucket_Field'Last) then return -1; end if;
            case N_Raw_Bucket_Field'Val (Field) is
               when Size => return N.Raw_Bucket'Size / System.Storage_Unit;
               when Alignment => return N.Raw_Bucket'Alignment;
               when F_Key => return V_N_Raw_Bucket.Key'Position;
               when F_Capacity => return V_N_Raw_Bucket.Capacity'Position;
               when F_Held_Total => return V_N_Raw_Bucket.Held_Total'Position;
               when F_Charged_Total => return V_N_Raw_Bucket.Charged_Total'Position;
               when F_Capacity_Source => return V_N_Raw_Bucket.Capacity_Source'Position;
               when F_Catalogue_Head => return V_N_Raw_Bucket.Catalogue_Head'Position;
               when F_Observation_Head => return V_N_Raw_Bucket.Observation_Head'Position;
            end case;
         when N_Raw_Projection =>
            if Field > N_Raw_Projection_Field'Pos (N_Raw_Projection_Field'Last) then return -1; end if;
            case N_Raw_Projection_Field'Val (Field) is
               when Size => return N.Raw_Projection'Size / System.Storage_Unit;
               when Alignment => return N.Raw_Projection'Alignment;
               when F_Key => return V_N_Raw_Projection.Key'Position;
               when F_Bound => return V_N_Raw_Projection.Bound'Position;
               when F_Origin => return V_N_Raw_Projection.Origin'Position;
               when F_Catalogue_Head => return V_N_Raw_Projection.Catalogue_Head'Position;
               when F_Numerator => return V_N_Raw_Projection.Numerator'Position;
               when F_Denominator => return V_N_Raw_Projection.Denominator'Position;
               when F_Amount => return V_N_Raw_Projection.Amount'Position;
            end case;
         when N_Raw_Current_Observation =>
            if Field > N_Raw_Current_Observation_Field'Pos (N_Raw_Current_Observation_Field'Last) then return -1; end if;
            case N_Raw_Current_Observation_Field'Val (Field) is
               when Size => return N.Raw_Current_Observation'Size / System.Storage_Unit;
               when Alignment => return N.Raw_Current_Observation'Alignment;
               when F_Scope => return V_N_Raw_Current_Observation.Scope'Position;
               when F_Resource_Epoch => return V_N_Raw_Current_Observation.Resource_Epoch'Position;
               when F_Universe_Head => return V_N_Raw_Current_Observation.Universe_Head'Position;
               when F_Ledger_Head => return V_N_Raw_Current_Observation.Ledger_Head'Position;
               when F_History_Head => return V_N_Raw_Current_Observation.History_Head'Position;
               when F_Physical_Head => return V_N_Raw_Current_Observation.Physical_Head'Position;
               when F_Store_Genesis => return V_N_Raw_Current_Observation.Store_Genesis'Position;
               when F_Store_Id => return V_N_Raw_Current_Observation.Store_Id'Position;
               when F_Root_Head => return V_N_Raw_Current_Observation.Root_Head'Position;
               when F_Prime => return V_N_Raw_Current_Observation.Prime'Position;
               when F_Root_Count => return V_N_Raw_Current_Observation.Root_Count'Position;
               when F_Cause => return V_N_Raw_Current_Observation.Cause'Position;
               when F_Requester => return V_N_Raw_Current_Observation.Requester'Position;
               when F_Receipt => return V_N_Raw_Current_Observation.Receipt'Position;
               when F_Catalogue_Head => return V_N_Raw_Current_Observation.Catalogue_Head'Position;
               when F_Observation_Head => return V_N_Raw_Current_Observation.Observation_Head'Position;
            end case;
         when N_Raw_Intent =>
            if Field > N_Raw_Intent_Field'Pos (N_Raw_Intent_Field'Last) then return -1; end if;
            case N_Raw_Intent_Field'Val (Field) is
               when Size => return N.Raw_Intent'Size / System.Storage_Unit;
               when Alignment => return N.Raw_Intent'Alignment;
               when F_Kind => return V_N_Raw_Intent.Kind'Position;
               when F_Original => return V_N_Raw_Intent.Original'Position;
               when F_Expected_Epoch => return V_N_Raw_Intent.Expected_Epoch'Position;
               when F_Expected_Ledger_Head => return V_N_Raw_Intent.Expected_Ledger_Head'Position;
               when F_Request_Id => return V_N_Raw_Intent.Request_Id'Position;
               when F_Cause => return V_N_Raw_Intent.Cause'Position;
               when F_Requester => return V_N_Raw_Intent.Requester'Position;
               when F_Receipt => return V_N_Raw_Intent.Receipt'Position;
            end case;
         when N_Raw_Packet =>
            if Field > N_Raw_Packet_Field'Pos (N_Raw_Packet_Field'Last) then return -1; end if;
            case N_Raw_Packet_Field'Val (Field) is
               when Size => return N.Raw_Packet'Size / System.Storage_Unit;
               when Alignment => return N.Raw_Packet'Alignment;
               when F_Schema_Version => return V_N_Raw_Packet.Schema_Version'Position;
               when F_Before_State => return V_N_Raw_Packet.Before_State'Position;
               when F_Proposed_State => return V_N_Raw_Packet.Proposed_State'Position;
               when F_Current => return V_N_Raw_Packet.Current'Position;
               when F_Request => return V_N_Raw_Packet.Request'Position;
            end case;
         when O_Raw_Facts =>
            if Field > O_Raw_Facts_Field'Pos (O_Raw_Facts_Field'Last) then return -1; end if;
            case O_Raw_Facts_Field'Val (Field) is
               when Size => return O.Raw_Facts'Size / System.Storage_Unit;
               when Alignment => return O.Raw_Facts'Alignment;
               when F_Current => return V_O_Raw_Facts.Current'Position;
               when F_Current_Epoch => return V_O_Raw_Facts.Current_Epoch'Position;
               when F_Retained => return V_O_Raw_Facts.Retained'Position;
               when F_Current_Universe_Head => return V_O_Raw_Facts.Current_Universe_Head'Position;
               when F_Current_Ledger_Head => return V_O_Raw_Facts.Current_Ledger_Head'Position;
               when F_Intent => return V_O_Raw_Facts.Intent'Position;
               when F_Dispatch => return V_O_Raw_Facts.Dispatch'Position;
               when F_Observation_Head => return V_O_Raw_Facts.Observation_Head'Position;
               when F_Actual_Unit => return V_O_Raw_Facts.Actual_Unit'Position;
               when F_Cgroup => return V_O_Raw_Facts.Cgroup'Position;
               when F_Invocation => return V_O_Raw_Facts.Invocation'Position;
               when F_Namespace => return V_O_Raw_Facts.Namespace'Position;
               when F_Held_Namespace => return V_O_Raw_Facts.Held_Namespace'Position;
               when F_Peer => return V_O_Raw_Facts.Peer'Position;
               when F_Held_Peer => return V_O_Raw_Facts.Held_Peer'Position;
               when F_Helper_Image => return V_O_Raw_Facts.Helper_Image'Position;
               when F_Expected_Helper_Image => return V_O_Raw_Facts.Expected_Helper_Image'Position;
               when F_Challenge => return V_O_Raw_Facts.Challenge'Position;
               when F_Held_Challenge => return V_O_Raw_Facts.Held_Challenge'Position;
               when F_Protocol => return V_O_Raw_Facts.Protocol'Position;
               when F_Closed_Event => return V_O_Raw_Facts.Closed_Event'Position;
               when F_Namespace_Wait => return V_O_Raw_Facts.Namespace_Wait'Position;
               when F_Helper_Wait => return V_O_Raw_Facts.Helper_Wait'Position;
               when F_Cgroup_Events => return V_O_Raw_Facts.Cgroup_Events'Position;
               when F_Cgroup_Type => return V_O_Raw_Facts.Cgroup_Type'Position;
               when F_Manager_Delegate => return V_O_Raw_Facts.Manager_Delegate'Position;
               when F_Cgroup_Owner => return V_O_Raw_Facts.Cgroup_Owner'Position;
               when F_Cgroup_Group_Write => return V_O_Raw_Facts.Cgroup_Group_Write'Position;
               when F_Cgroup_Other_Write => return V_O_Raw_Facts.Cgroup_Other_Write'Position;
               when F_Actual_Store_Genesis => return V_O_Raw_Facts.Actual_Store_Genesis'Position;
               when F_Actual_Store_Id => return V_O_Raw_Facts.Actual_Store_Id'Position;
               when F_Owner_Store_Genesis => return V_O_Raw_Facts.Owner_Store_Genesis'Position;
               when F_Owner_Store_Id => return V_O_Raw_Facts.Owner_Store_Id'Position;
               when F_Genesis_Universe => return V_O_Raw_Facts.Genesis_Universe'Position;
               when F_Genesis_Instance => return V_O_Raw_Facts.Genesis_Instance'Position;
               when F_Genesis_Context_Head => return V_O_Raw_Facts.Genesis_Context_Head'Position;
               when F_Genesis_Prime => return V_O_Raw_Facts.Genesis_Prime'Position;
               when F_Genesis_Root_Count => return V_O_Raw_Facts.Genesis_Root_Count'Position;
               when F_Phase => return V_O_Raw_Facts.Phase'Position;
            end case;
         when O_Raw_Input =>
            if Field > O_Raw_Input_Field'Pos (O_Raw_Input_Field'Last) then return -1; end if;
            case O_Raw_Input_Field'Val (Field) is
               when Size => return O.Raw_Input'Size / System.Storage_Unit;
               when Alignment => return O.Raw_Input'Alignment;
               when F_State => return V_O_Raw_Input.State'Position;
               when F_Item => return V_O_Raw_Input.Item'Position;
               when F_Captured => return V_O_Raw_Input.Captured'Position;
            end case;
         when T_Raw_Quantity =>
            if Field > T_Raw_Quantity_Field'Pos (T_Raw_Quantity_Field'Last) then return -1; end if;
            case T_Raw_Quantity_Field'Val (Field) is
               when Size => return T.Raw_Quantity'Size / System.Storage_Unit;
               when Alignment => return T.Raw_Quantity'Alignment;
               when F_Present => return V_T_Raw_Quantity.Present'Position;
               when F_Negative => return V_T_Raw_Quantity.Negative'Position;
               when F_First => return V_T_Raw_Quantity.First'Position;
               when F_Length => return V_T_Raw_Quantity.Length'Position;
            end case;
         when T_Raw_UID =>
            if Field > T_Raw_UID_Field'Pos (T_Raw_UID_Field'Last) then return -1; end if;
            case T_Raw_UID_Field'Val (Field) is
               when Size => return T.Raw_UID'Size / System.Storage_Unit;
               when Alignment => return T.Raw_UID'Alignment;
               when F_Present => return V_T_Raw_UID.Present'Position;
               when F_Value => return V_T_Raw_UID.Value'Position;
            end case;
         when T_Raw_Binding =>
            if Field > T_Raw_Binding_Field'Pos (T_Raw_Binding_Field'Last) then return -1; end if;
            case T_Raw_Binding_Field'Val (Field) is
               when Size => return T.Raw_Binding'Size / System.Storage_Unit;
               when Alignment => return T.Raw_Binding'Alignment;
               when F_Action => return V_T_Raw_Binding.Action'Position;
               when F_Id => return V_T_Raw_Binding.Id'Position;
               when F_Peer => return V_T_Raw_Binding.Peer'Position;
               when F_Preparer => return V_T_Raw_Binding.Preparer'Position;
               when F_Owner => return V_T_Raw_Binding.Owner'Position;
               when F_Target_Owner => return V_T_Raw_Binding.Target_Owner'Position;
               when F_Policy_Epoch => return V_T_Raw_Binding.Policy_Epoch'Position;
               when F_Resource_Epoch => return V_T_Raw_Binding.Resource_Epoch'Position;
            end case;
         when T_Raw_Grant =>
            if Field > T_Raw_Grant_Field'Pos (T_Raw_Grant_Field'Last) then return -1; end if;
            case T_Raw_Grant_Field'Val (Field) is
               when Size => return T.Raw_Grant'Size / System.Storage_Unit;
               when Alignment => return T.Raw_Grant'Alignment;
               when F_Id => return V_T_Raw_Grant.Id'Position;
               when F_Parent => return V_T_Raw_Grant.Parent'Position;
               when F_Issuer => return V_T_Raw_Grant.Issuer'Position;
               when F_Instance => return V_T_Raw_Grant.Instance'Position;
               when F_Root_Set => return V_T_Raw_Grant.Root_Set'Position;
               when F_Policy => return V_T_Raw_Grant.Policy'Position;
               when F_Subject => return V_T_Raw_Grant.Subject'Position;
               when F_Owner => return V_T_Raw_Grant.Owner'Position;
               when F_Allowed => return V_T_Raw_Grant.Allowed'Position;
               when F_State => return V_T_Raw_Grant.State'Position;
               when F_Epoch => return V_T_Raw_Grant.Epoch'Position;
               when F_Ceiling => return V_T_Raw_Grant.Ceiling'Position;
               when F_Issued_At => return V_T_Raw_Grant.Issued_At'Position;
               when F_Expires_At => return V_T_Raw_Grant.Expires_At'Position;
            end case;
         when T_Raw_Use =>
            if Field > T_Raw_Use_Field'Pos (T_Raw_Use_Field'Last) then return -1; end if;
            case T_Raw_Use_Field'Val (Field) is
               when Size => return T.Raw_Use'Size / System.Storage_Unit;
               when Alignment => return T.Raw_Use'Alignment;
               when F_Bound => return V_T_Raw_Use.Bound'Position;
               when F_State => return V_T_Raw_Use.State'Position;
            end case;
         when T_Raw_Evidence =>
            if Field > T_Raw_Evidence_Field'Pos (T_Raw_Evidence_Field'Last) then return -1; end if;
            case T_Raw_Evidence_Field'Val (Field) is
               when Size => return T.Raw_Evidence'Size / System.Storage_Unit;
               when Alignment => return T.Raw_Evidence'Alignment;
               when F_Effect_Binding => return V_T_Raw_Evidence.Effect_Binding'Position;
               when F_Actual_Receipt_Root => return V_T_Raw_Evidence.Actual_Receipt_Root'Position;
               when F_Actual_Causal_Root => return V_T_Raw_Evidence.Actual_Causal_Root'Position;
               when F_No_Effect_Binding => return V_T_Raw_Evidence.No_Effect_Binding'Position;
               when F_Owner_Resolution => return V_T_Raw_Evidence.Owner_Resolution'Position;
               when F_Quarantine_Head => return V_T_Raw_Evidence.Quarantine_Head'Position;
               when F_Witnessed_Receipt_Head => return V_T_Raw_Evidence.Witnessed_Receipt_Head'Position;
               when F_Witnessed_Causal_Head => return V_T_Raw_Evidence.Witnessed_Causal_Head'Position;
               when F_Recovery => return V_T_Raw_Evidence.Recovery'Position;
               when F_Original_Use => return V_T_Raw_Evidence.Original_Use'Position;
               when F_Effect_Material_First => return V_T_Raw_Evidence.Effect_Material_First'Position;
               when F_Effect_Material_Length => return V_T_Raw_Evidence.Effect_Material_Length'Position;
            end case;
         when T_Raw_Input =>
            if Field > T_Raw_Input_Field'Pos (T_Raw_Input_Field'Last) then return -1; end if;
            case T_Raw_Input_Field'Val (Field) is
               when Size => return T.Raw_Input'Size / System.Storage_Unit;
               when Alignment => return T.Raw_Input'Alignment;
               when F_Schema => return V_T_Raw_Input.Schema'Position;
               when F_Mode => return V_T_Raw_Input.Mode'Position;
               when F_Bound => return V_T_Raw_Input.Bound'Position;
               when F_Now => return V_T_Raw_Input.Now'Position;
               when F_Facts => return V_T_Raw_Input.Facts'Position;
            end case;
         when T_Raw_Result =>
            if Field > T_Raw_Result_Field'Pos (T_Raw_Result_Field'Last) then return -1; end if;
            case T_Raw_Result_Field'Val (Field) is
               when Size => return T.Raw_Result'Size / System.Storage_Unit;
               when Alignment => return T.Raw_Result'Alignment;
               when F_Disposition => return V_T_Raw_Result.Disposition'Position;
            end case;
         when TC_Raw_Digest =>
            if Field > TC_Raw_Digest_Field'Pos (TC_Raw_Digest_Field'Last) then return -1; end if;
            case TC_Raw_Digest_Field'Val (Field) is
               when Size => return T.C.Raw_Digest'Size / System.Storage_Unit;
               when Alignment => return T.C.Raw_Digest'Alignment;
               when F_Present => return V_TC_Raw_Digest.Present'Position;
               when F_Value => return V_TC_Raw_Digest.Value'Position;
            end case;
         when TC_Raw_Row =>
            if Field > TC_Raw_Row_Field'Pos (TC_Raw_Row_Field'Last) then return -1; end if;
            case TC_Raw_Row_Field'Val (Field) is
               when Size => return T.C.Raw_Row'Size / System.Storage_Unit;
               when Alignment => return T.C.Raw_Row'Alignment;
               when F_Previous => return V_TC_Raw_Row.Previous'Position;
               when F_Actual_Payload_Root => return V_TC_Raw_Row.Actual_Payload_Root'Position;
               when F_Stored_Payload_Root => return V_TC_Raw_Row.Stored_Payload_Root'Position;
               when F_Stored_Head => return V_TC_Raw_Row.Stored_Head'Position;
            end case;
         when TC_Raw_Anchors =>
            if Field > TC_Raw_Anchors_Field'Pos (TC_Raw_Anchors_Field'Last) then return -1; end if;
            case TC_Raw_Anchors_Field'Val (Field) is
               when Size => return T.C.Raw_Anchors'Size / System.Storage_Unit;
               when Alignment => return T.C.Raw_Anchors'Alignment;
               when F_Kind => return V_TC_Raw_Anchors.Kind'Position;
               when F_Observed_Genesis => return V_TC_Raw_Anchors.Observed_Genesis'Position;
               when F_Witnessed_Genesis => return V_TC_Raw_Anchors.Witnessed_Genesis'Position;
               when F_Witnessed_Head => return V_TC_Raw_Anchors.Witnessed_Head'Position;
            end case;
         when TC_Raw_Result =>
            if Field > TC_Raw_Result_Field'Pos (TC_Raw_Result_Field'Last) then return -1; end if;
            case TC_Raw_Result_Field'Val (Field) is
               when Size => return T.C.Raw_Result'Size / System.Storage_Unit;
               when Alignment => return T.C.Raw_Result'Alignment;
               when F_Disposition => return V_TC_Raw_Result.Disposition'Position;
               when F_Head => return V_TC_Raw_Result.Head'Position;
               when F_Accepted_Count => return V_TC_Raw_Result.Accepted_Count'Position;
            end case;
         when Y_Raw_Process =>
            if Field > Y_Raw_Process_Field'Pos (Y_Raw_Process_Field'Last) then return -1; end if;
            case Y_Raw_Process_Field'Val (Field) is
               when Size => return Y.Raw_Process'Size / System.Storage_Unit;
               when Alignment => return Y.Raw_Process'Alignment;
               when F_raw_status => return V_Y_Raw_Process.raw_status'Position;
               when F_raw_stat => return V_Y_Raw_Process.raw_stat'Position;
               when F_raw_cgroup => return V_Y_Raw_Process.raw_cgroup'Position;
               when F_raw_maps => return V_Y_Raw_Process.raw_maps'Position;
               when F_raw_cmdline => return V_Y_Raw_Process.raw_cmdline'Position;
               when F_raw_pidfd_info => return V_Y_Raw_Process.raw_pidfd_info'Position;
               when F_namespace => return V_Y_Raw_Process.namespace'Position;
               when F_cgroup => return V_Y_Raw_Process.cgroup'Position;
               when F_actual_unit => return V_Y_Raw_Process.actual_unit'Position;
               when F_invocation => return V_Y_Raw_Process.invocation'Position;
               when F_source_lease => return V_Y_Raw_Process.source_lease'Position;
               when F_pidfd_wait => return V_Y_Raw_Process.pidfd_wait'Position;
               when F_host_pid => return V_Y_Raw_Process.host_pid'Position;
               when F_start_tick => return V_Y_Raw_Process.start_tick'Position;
               when F_parent_pid => return V_Y_Raw_Process.parent_pid'Position;
               when F_parent_start_tick => return V_Y_Raw_Process.parent_start_tick'Position;
               when F_real_uid => return V_Y_Raw_Process.real_uid'Position;
               when F_effective_uid => return V_Y_Raw_Process.effective_uid'Position;
               when F_saved_uid => return V_Y_Raw_Process.saved_uid'Position;
               when F_real_gid => return V_Y_Raw_Process.real_gid'Position;
               when F_effective_gid => return V_Y_Raw_Process.effective_gid'Position;
               when F_saved_gid => return V_Y_Raw_Process.saved_gid'Position;
            end case;
         when Y_Raw_Controller =>
            if Field > Y_Raw_Controller_Field'Pos (Y_Raw_Controller_Field'Last) then return -1; end if;
            case Y_Raw_Controller_Field'Val (Field) is
               when Size => return Y.Raw_Controller'Size / System.Storage_Unit;
               when Alignment => return Y.Raw_Controller'Alignment;
               when F_Bound => return V_Y_Raw_Controller.Bound'Position;
               when F_Process => return V_Y_Raw_Controller.Process'Position;
               when F_Requester_Uid => return V_Y_Raw_Controller.Requester_Uid'Position;
               when F_Requester_Gid => return V_Y_Raw_Controller.Requester_Gid'Position;
               when F_raw_manager => return V_Y_Raw_Controller.raw_manager'Position;
               when F_raw_channel => return V_Y_Raw_Controller.raw_channel'Position;
               when F_owner_endpoint => return V_Y_Raw_Controller.owner_endpoint'Position;
               when F_expected_owner_endpoint => return V_Y_Raw_Controller.expected_owner_endpoint'Position;
               when F_source_lease => return V_Y_Raw_Controller.source_lease'Position;
               when F_expected_source_lease => return V_Y_Raw_Controller.expected_source_lease'Position;
               when F_worker_image => return V_Y_Raw_Controller.worker_image'Position;
               when F_expected_worker_image => return V_Y_Raw_Controller.expected_worker_image'Position;
               when F_handler_plan => return V_Y_Raw_Controller.handler_plan'Position;
               when F_expected_handler_plan => return V_Y_Raw_Controller.expected_handler_plan'Position;
               when F_raw_request => return V_Y_Raw_Controller.raw_request'Position;
               when F_requester => return V_Y_Raw_Controller.requester'Position;
               when F_dispatch => return V_Y_Raw_Controller.dispatch'Position;
               when F_running_event => return V_Y_Raw_Controller.running_event'Position;
               when F_expected_running_event => return V_Y_Raw_Controller.expected_running_event'Position;
               when F_store_genesis => return V_Y_Raw_Controller.store_genesis'Position;
               when F_expected_store_genesis => return V_Y_Raw_Controller.expected_store_genesis'Position;
               when F_current_source => return V_Y_Raw_Controller.current_source'Position;
            end case;
         when Y_Raw_Task =>
            if Field > Y_Raw_Task_Field'Pos (Y_Raw_Task_Field'Last) then return -1; end if;
            case Y_Raw_Task_Field'Val (Field) is
               when Size => return Y.Raw_Task'Size / System.Storage_Unit;
               when Alignment => return Y.Raw_Task'Alignment;
               when F_Action => return V_Y_Raw_Task.Action'Position;
               when F_Root => return V_Y_Raw_Task.Root'Position;
               when F_Child => return V_Y_Raw_Task.Child'Position;
               when F_task_id => return V_Y_Raw_Task.task_id'Position;
               when F_root_world => return V_Y_Raw_Task.root_world'Position;
               when F_child_world => return V_Y_Raw_Task.child_world'Position;
               when F_root_instance => return V_Y_Raw_Task.root_instance'Position;
               when F_child_instance => return V_Y_Raw_Task.child_instance'Position;
               when F_world_store => return V_Y_Raw_Task.world_store'Position;
               when F_full_world_ancestry => return V_Y_Raw_Task.full_world_ancestry'Position;
               when F_original_workload => return V_Y_Raw_Task.original_workload'Position;
               when F_sandbox => return V_Y_Raw_Task.sandbox'Position;
               when F_adapter => return V_Y_Raw_Task.adapter'Position;
               when F_context => return V_Y_Raw_Task.context'Position;
               when F_mission => return V_Y_Raw_Task.mission'Position;
               when F_stdin => return V_Y_Raw_Task.stdin'Position;
               when F_credential_source => return V_Y_Raw_Task.credential_source'Position;
               when F_executable_source => return V_Y_Raw_Task.executable_source'Position;
               when F_configuration => return V_Y_Raw_Task.configuration'Position;
               when F_owner_plan => return V_Y_Raw_Task.owner_plan'Position;
               when F_native_cost_input => return V_Y_Raw_Task.native_cost_input'Position;
               when F_raw_request => return V_Y_Raw_Task.raw_request'Position;
               when F_requester => return V_Y_Raw_Task.requester'Position;
               when F_cause => return V_Y_Raw_Task.cause'Position;
               when F_root_dispatch => return V_Y_Raw_Task.root_dispatch'Position;
               when F_root_running_event => return V_Y_Raw_Task.root_running_event'Position;
               when F_task_journal => return V_Y_Raw_Task.task_journal'Position;
               when F_task_intent => return V_Y_Raw_Task.task_intent'Position;
               when F_task_reservation_event => return V_Y_Raw_Task.task_reservation_event'Position;
               when F_task_launch_event => return V_Y_Raw_Task.task_launch_event'Position;
               when F_parent_namespace_source => return V_Y_Raw_Task.parent_namespace_source'Position;
               when F_fd_lineage => return V_Y_Raw_Task.fd_lineage'Position;
               when F_source_lease => return V_Y_Raw_Task.source_lease'Position;
            end case;
         when Y_Raw_Namespace =>
            if Field > Y_Raw_Namespace_Field'Pos (Y_Raw_Namespace_Field'Last) then return -1; end if;
            case Y_Raw_Namespace_Field'Val (Field) is
               when Size => return Y.Raw_Namespace'Size / System.Storage_Unit;
               when Alignment => return Y.Raw_Namespace'Alignment;
               when F_identity => return V_Y_Raw_Namespace.identity'Position;
               when F_parent => return V_Y_Raw_Namespace.parent'Position;
               when F_raw_nsfs => return V_Y_Raw_Namespace.raw_nsfs'Position;
               when F_raw_get_parent => return V_Y_Raw_Namespace.raw_get_parent'Position;
               when F_source_lease => return V_Y_Raw_Namespace.source_lease'Position;
            end case;
         when Y_Raw_Input =>
            if Field > Y_Raw_Input_Field'Pos (Y_Raw_Input_Field'Last) then return -1; end if;
            case Y_Raw_Input_Field'Val (Field) is
               when Size => return Y.Raw_Input'Size / System.Storage_Unit;
               when Alignment => return Y.Raw_Input'Alignment;
               when F_Mode => return V_Y_Raw_Input.Mode'Position;
               when F_Controller => return V_Y_Raw_Input.Controller'Position;
               when F_Task => return V_Y_Raw_Input.Child_Task'Position;
            end case;
      end case;
      end;
   exception
      when others => return -1;
   end Child_Layout;
   function Child_Decide
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      History : System.Address;
      History_Count : Interfaces.C.size_t;
      Proposed_History : System.Address;
      Proposed_History_Count : Interfaces.C.size_t;
      Rows : System.Address;
      Rows_Count : Interfaces.C.size_t;
      Proposed_Rows : System.Address;
      Proposed_Rows_Count : Interfaces.C.size_t;
      Projection : System.Address;
      Projection_Count : Interfaces.C.size_t;
      Proposed_Projection : System.Address;
      Proposed_Projection_Count : Interfaces.C.size_t;
      Buckets : System.Address;
      Buckets_Count : Interfaces.C.size_t;
      Proposed_Buckets : System.Address;
      Proposed_Buckets_Count : Interfaces.C.size_t;
      Actual_Buckets : System.Address;
      Actual_Buckets_Count : Interfaces.C.size_t;
      Observed : System.Address;
      Observed_Count : Interfaces.C.size_t;
      Facts : System.Address;
      Facts_Count : Interfaces.C.size_t;
      Capabilities : System.Address;
      Capabilities_Count : Interfaces.C.size_t;
      Groups : System.Address;
      Groups_Count : Interfaces.C.size_t;
      Proc_Groups : System.Address;
      Proc_Groups_Count : Interfaces.C.size_t;
      Authority_Input : System.Address;
      Authority_Input_Length : Interfaces.C.size_t;
      Authority_Arena : System.Address;
      Authority_Arena_Length : Interfaces.C.size_t;
      Authority_Grants : System.Address;
      Authority_Grants_Count : Interfaces.C.size_t;
      Authority_Uses : System.Address;
      Authority_Uses_Count : Interfaces.C.size_t;
      Authority_Receipts : System.Address;
      Authority_Receipts_Count : Interfaces.C.size_t;
      Authority_Events : System.Address;
      Authority_Events_Count : Interfaces.C.size_t;
      Crosswalk : System.Address;
      Crosswalk_Length : Interfaces.C.size_t;
      Child_Input : System.Address;
      Child_Input_Length : Interfaces.C.size_t;
      Tasks : System.Address;
      Tasks_Count : Interfaces.C.size_t;
      Processes : System.Address;
      Processes_Count : Interfaces.C.size_t;
      Namespaces : System.Address;
      Namespaces_Count : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Native renames Worldline.Native_Execution_Capture;
      package N renames V.N;
      package W renames V.W;
      package O renames V.O;
      package Q renames V.Q;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.long;
      use type Interfaces.C.int;
      package Raw_Pointers is new System.Address_To_Access_Conversions (D.Raw_Packet);
      package Authority_Pointers is new System.Address_To_Access_Conversions (T.Raw_Input);
      package Crosswalk_Pointers is new System.Address_To_Access_Conversions (X.Raw_Crosswalk);
      package Child_Pointers is new System.Address_To_Access_Conversions (Y.Raw_Input);
      package Output_Pointers is new System.Address_To_Access_Conversions (W.Raw_Result);
   begin
      if Input_Length /= D.Raw_Packet'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Input, Input_Length)
        or else To_Integer (Input) mod D.Raw_Packet'Alignment /= 0
        or else not Native_Execution_Array_Shape (Arena, Arena_Length, Q.Byte'Size / System.Storage_Unit, Q.Byte'Alignment)
        or else not Native_Execution_Array_Shape (History, History_Count, N.Raw_Scope_Frame'Size / System.Storage_Unit, N.Raw_Scope_Frame'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_History, Proposed_History_Count, N.Raw_Scope_Frame'Size / System.Storage_Unit, N.Raw_Scope_Frame'Alignment)
        or else not Native_Execution_Array_Shape (Rows, Rows_Count, W.Raw_Row'Size / System.Storage_Unit, W.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Rows, Proposed_Rows_Count, W.Raw_Row'Size / System.Storage_Unit, W.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Projection, Projection_Count, N.Raw_Projection'Size / System.Storage_Unit, N.Raw_Projection'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Projection, Proposed_Projection_Count, N.Raw_Projection'Size / System.Storage_Unit, N.Raw_Projection'Alignment)
        or else not Native_Execution_Array_Shape (Buckets, Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Proposed_Buckets, Proposed_Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Actual_Buckets, Actual_Buckets_Count, N.Raw_Bucket'Size / System.Storage_Unit, N.Raw_Bucket'Alignment)
        or else not Native_Execution_Array_Shape (Observed, Observed_Count, W.Raw_Native'Size / System.Storage_Unit, W.Raw_Native'Alignment)
        or else not Native_Execution_Array_Shape (Facts, Facts_Count, O.Raw_Facts'Size / System.Storage_Unit, O.Raw_Facts'Alignment)
        or else not Native_Execution_Array_Shape (Capabilities, Capabilities_Count, D.Raw_Capability'Size / System.Storage_Unit, D.Raw_Capability'Alignment)
        or else not Native_Execution_Array_Shape (Groups, Groups_Count, W.Raw_Quantity'Size / System.Storage_Unit, W.Raw_Quantity'Alignment)
        or else not Native_Execution_Array_Shape (Proc_Groups, Proc_Groups_Count, W.Raw_Quantity'Size / System.Storage_Unit, W.Raw_Quantity'Alignment)
        or else Authority_Input_Length /= T.Raw_Input'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Authority_Input, Authority_Input_Length)
        or else To_Integer (Authority_Input) mod T.Raw_Input'Alignment /= 0
        or else not Native_Execution_Array_Shape (Authority_Arena, Authority_Arena_Length, Q.Byte'Size / System.Storage_Unit, Q.Byte'Alignment)
        or else not Native_Execution_Array_Shape (Authority_Grants, Authority_Grants_Count, T.Raw_Grant'Size / System.Storage_Unit, T.Raw_Grant'Alignment)
        or else not Native_Execution_Array_Shape (Authority_Uses, Authority_Uses_Count, T.Raw_Use'Size / System.Storage_Unit, T.Raw_Use'Alignment)
        or else not Native_Execution_Array_Shape (Authority_Receipts, Authority_Receipts_Count, T.C.Raw_Row'Size / System.Storage_Unit, T.C.Raw_Row'Alignment)
        or else not Native_Execution_Array_Shape (Authority_Events, Authority_Events_Count, T.C.Raw_Row'Size / System.Storage_Unit, T.C.Raw_Row'Alignment)
        or else Crosswalk_Length /= X.Raw_Crosswalk'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Crosswalk, Crosswalk_Length)
        or else To_Integer (Crosswalk) mod X.Raw_Crosswalk'Alignment /= 0
        or else Child_Input_Length /= Y.Raw_Input'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Child_Input, Child_Input_Length)
        or else To_Integer (Child_Input) mod Y.Raw_Input'Alignment /= 0
        or else not Native_Execution_Array_Shape (Tasks, Tasks_Count, Y.Raw_Task'Size / System.Storage_Unit, Y.Raw_Task'Alignment)
        or else not Native_Execution_Array_Shape (Processes, Processes_Count, Y.Raw_Process'Size / System.Storage_Unit, Y.Raw_Process'Alignment)
        or else not Native_Execution_Array_Shape (Namespaces, Namespaces_Count, Y.Raw_Namespace'Size / System.Storage_Unit, Y.Raw_Namespace'Alignment)
        or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Output, Output_Length)
        or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0 then return -1; end if;
      declare
         Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Arena_Length));
         Data_View : constant Resource_Bytes_Observer :=
           Observe_Resource_Bytes (Arena, Data_Bounds);
         History_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (History_Count));
         History_View : constant Native_History_Observer :=
           Observe_Native_History (History, History_Bounds);
         Proposed_History_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_History_Count));
         Proposed_History_View : constant Native_History_Observer :=
           Observe_Native_History (Proposed_History, Proposed_History_Bounds);
         Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Rows_Count));
         Rows_View : constant Native_Rows_Observer :=
           Observe_Native_Rows (Rows, Rows_Bounds);
         Proposed_Rows_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Rows_Count));
         Proposed_Rows_View : constant Native_Rows_Observer :=
           Observe_Native_Rows (Proposed_Rows, Proposed_Rows_Bounds);
         Projection_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Projection_Count));
         Projection_View : constant Native_Projection_Observer :=
           Observe_Native_Projection (Projection, Projection_Bounds);
         Proposed_Projection_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Projection_Count));
         Proposed_Projection_View : constant Native_Projection_Observer :=
           Observe_Native_Projection (Proposed_Projection, Proposed_Projection_Bounds);
         Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Buckets_Count));
         Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Buckets, Buckets_Bounds);
         Proposed_Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proposed_Buckets_Count));
         Proposed_Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Proposed_Buckets, Proposed_Buckets_Bounds);
         Actual_Buckets_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Actual_Buckets_Count));
         Actual_Buckets_View : constant Native_Buckets_Observer :=
           Observe_Native_Buckets (Actual_Buckets, Actual_Buckets_Bounds);
         Observed_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Observed_Count));
         Observed_View : constant Native_Observed_Observer :=
           Observe_Native_Observed (Observed, Observed_Bounds);
         Facts_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Facts_Count));
         Facts_View : constant Native_Facts_Observer :=
           Observe_Native_Facts (Facts, Facts_Bounds);
         Capabilities_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Capabilities_Count));
         Capabilities_View : constant Native_Capabilities_Observer :=
           Observe_Native_Capabilities (Capabilities, Capabilities_Bounds);
         Groups_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Groups_Count));
         Groups_View : constant Native_Groups_Observer :=
           Observe_Native_Groups (Groups, Groups_Bounds);
         Proc_Groups_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Proc_Groups_Count));
         Proc_Groups_View : constant Native_Groups_Observer :=
           Observe_Native_Groups (Proc_Groups, Proc_Groups_Bounds);
         Authority_Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Authority_Arena_Length));
         Authority_Data_View : constant Resource_Bytes_Observer :=
           Observe_Resource_Bytes (Authority_Arena, Authority_Data_Bounds);
         Authority_Grants_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Authority_Grants_Count));
         Authority_Grants_View : constant Native_Grants_Observer :=
           Observe_Native_Grants (Authority_Grants, Authority_Grants_Bounds);
         Authority_Uses_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Authority_Uses_Count));
         Authority_Uses_View : constant Native_Uses_Observer :=
           Observe_Native_Uses (Authority_Uses, Authority_Uses_Bounds);
         Authority_Receipts_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Authority_Receipts_Count));
         Authority_Receipts_View : constant Native_Chain_Observer :=
           Observe_Native_Chain (Authority_Receipts, Authority_Receipts_Bounds);
         Authority_Events_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Authority_Events_Count));
         Authority_Events_View : constant Native_Chain_Observer :=
           Observe_Native_Chain (Authority_Events, Authority_Events_Bounds);
         Tasks_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Tasks_Count));
         Tasks_View : constant Native_Tasks_Observer :=
           Observe_Native_Tasks (Tasks, Tasks_Bounds);
         Processes_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Processes_Count));
         Processes_View : constant Native_Processes_Observer :=
           Observe_Native_Processes (Processes, Processes_Bounds);
         Namespaces_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Namespaces_Count));
         Namespaces_View : constant Native_Namespaces_Observer :=
           Observe_Native_Namespaces (Namespaces, Namespaces_Bounds);
         Result : constant V.Result := Native.Child_Decide (Raw_Pointers.To_Pointer (Input), Data_View, History_View, Proposed_History_View, Rows_View, Proposed_Rows_View, Projection_View, Proposed_Projection_View, Buckets_View, Proposed_Buckets_View, Actual_Buckets_View, Observed_View, Facts_View, Capabilities_View, Groups_View, Proc_Groups_View, Authority_Pointers.To_Pointer (Authority_Input), Authority_Data_View, Authority_Grants_View, Authority_Uses_View, Authority_Receipts_View, Authority_Events_View, Crosswalk_Pointers.To_Pointer (Crosswalk), Child_Pointers.To_Pointer (Child_Input), Tasks_View, Processes_View, Namespaces_View);
      begin
         Flush_Native_Diagnostic_Trace;
         if not Result.Well_Formed then return -1; end if;
         Output_Pointers.To_Pointer (Output).all := (Status => Result.Status);
      end;
      return 0;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return -1;
      end;
   exception
      when others => return -1;
   end Child_Decide;

   function Operation_Authority_Decide
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      Grants : System.Address;
      Grant_Count : Interfaces.C.size_t;
      Grant_Length : Interfaces.C.size_t;
      Uses : System.Address;
      Use_Count : Interfaces.C.size_t;
      Use_Length : Interfaces.C.size_t;
      Receipts : System.Address;
      Receipt_Count : Interfaces.C.size_t;
      Receipt_Length : Interfaces.C.size_t;
      Events : System.Address;
      Event_Count : Interfaces.C.size_t;
      Event_Length : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Native renames Worldline.Native_Execution_Capture;
      package N renames V.N;
      package W renames V.W;
      package O renames V.O;
      package Q renames V.Q;
      package D renames V.D;
      package X renames V.X;
      package Y renames V.Y;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.long;
      use type Interfaces.C.int;
      package Input_Pointers is new System.Address_To_Access_Conversions (T.Raw_Input);
      package Output_Pointers is new System.Address_To_Access_Conversions (T.Raw_Result);
   begin
      if Input_Length /= T.Raw_Input'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Input, Input_Length)
        or else To_Integer (Input) mod T.Raw_Input'Alignment /= 0
        or else not Native_Execution_Array_Shape (Arena, Arena_Length, Q.Byte'Size / System.Storage_Unit, Q.Byte'Alignment)
        or else not Native_Execution_Array_Shape (Grants, Grant_Count, T.Raw_Grant'Size / System.Storage_Unit, T.Raw_Grant'Alignment)
        or else Grant_Length /= Grant_Count * (T.Raw_Grant'Size / System.Storage_Unit)
        or else not Native_Execution_Array_Shape (Uses, Use_Count, T.Raw_Use'Size / System.Storage_Unit, T.Raw_Use'Alignment)
        or else Use_Length /= Use_Count * (T.Raw_Use'Size / System.Storage_Unit)
        or else not Native_Execution_Array_Shape (Receipts, Receipt_Count, T.C.Raw_Row'Size / System.Storage_Unit, T.C.Raw_Row'Alignment)
        or else Receipt_Length /= Receipt_Count * (T.C.Raw_Row'Size / System.Storage_Unit)
        or else not Native_Execution_Array_Shape (Events, Event_Count, T.C.Raw_Row'Size / System.Storage_Unit, T.C.Raw_Row'Alignment)
        or else Event_Length /= Event_Count * (T.C.Raw_Row'Size / System.Storage_Unit)
        or else Output_Length /= T.Raw_Result'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Output, Output_Length)
        or else To_Integer (Output) mod T.Raw_Result'Alignment /= 0 then return -1; end if;
      declare
         Authority_Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Arena_Length));
         Authority_Data_View : constant Resource_Bytes_Observer :=
           Observe_Resource_Bytes (Arena, Authority_Data_Bounds);
         Authority_Grants_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Grant_Count));
         Authority_Grants_View : constant Native_Grants_Observer :=
           Observe_Native_Grants (Grants, Authority_Grants_Bounds);
         Authority_Uses_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Use_Count));
         Authority_Uses_View : constant Native_Uses_Observer :=
           Observe_Native_Uses (Uses, Authority_Uses_Bounds);
         Authority_Receipts_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Receipt_Count));
         Authority_Receipts_View : constant Native_Chain_Observer :=
           Observe_Native_Chain (Receipts, Authority_Receipts_Bounds);
         Authority_Events_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Event_Count));
         Authority_Events_View : constant Native_Chain_Observer :=
           Observe_Native_Chain (Events, Authority_Events_Bounds);
         Result : constant V.Result := Native.Operation_Decide (Input_Pointers.To_Pointer (Input), Authority_Data_View, Authority_Grants_View, Authority_Uses_View, Authority_Receipts_View, Authority_Events_View);
      begin
         Flush_Native_Diagnostic_Trace;
         if not Result.Well_Formed then return -1; end if;
         Output_Pointers.To_Pointer (Output).all := (Disposition => Interfaces.Unsigned_8 (Result.Status));
      end;
      return 0;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return -1;
      end;
   exception
      when others => return -1;
   end Operation_Authority_Decide;
function Canonical_Operation_Version return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return (1);
      end;
   exception
      when others => return 0;
   end Canonical_Operation_Version;
   function Canonical_Operation_Layout(Kind,Field:Interfaces.Unsigned_32) return Interfaces.C.long is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   package W renames Worldline.Canonical_Operation_Wire; package K renames W.K;
   package A renames K.A; package L renames W.L;
   use System.Storage_Elements; use type System.Address;
   use type A.Q.Byte_Count;
   use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int;
   begin case Kind is
when 1 => declare V:W.Raw_Input; begin case Field is
when 0 => return W.Raw_Input'Size/System.Storage_Unit;
when 1 => return W.Raw_Input'Alignment;
when 2 => return V.Authority'Position;
when 3 => return V.State'Position;
when 4 => return V.Bound'Position;
when 5 => return V.Requester'Position;
when 6 => return V.Peer'Position;
when 7 => return V.Collapse'Position;
when others=>return -1; end case; end;
when 2 => declare V:W.Raw_Result; begin case Field is
when 0 => return W.Raw_Result'Size/System.Storage_Unit;
when 1 => return W.Raw_Result'Alignment;
when 2 => return V.Disposition'Position;
when others=>return -1; end case; end;
   when others=>return -1; end case;
      end;
   exception
      when others => return -1;
   end Canonical_Operation_Layout;
   function Canonical_Operation_Decide(Input:System.Address; Input_Length:Interfaces.C.size_t;
      Arena:System.Address; Arena_Length:Interfaces.C.size_t;
      Grants:System.Address; Grant_Count,Grant_Length:Interfaces.C.size_t;
      Uses:System.Address; Use_Count,Use_Length:Interfaces.C.size_t;
      Rows:System.Address; Row_Count,Row_Length:Interfaces.C.size_t;
      Observed:System.Address; Observed_Count,Observed_Length:Interfaces.C.size_t;
      Output:System.Address; Output_Length:Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   package W renames Worldline.Canonical_Operation_Wire; package K renames W.K;
   package A renames K.A; package L renames W.L;
   use System.Storage_Elements; use type System.Address;
   use type A.Q.Byte_Count;
   use type Interfaces.C.size_t; use type Interfaces.C.long; use type Interfaces.C.int;
   function Shape(P:System.Address; Count,Length,Stride:Interfaces.C.size_t; Alignment:Integer_Address) return Boolean is
     (Stride>0 and then Count<=Interfaces.C.size_t(A.Q.Byte_Count'Last)
      and then Count<=Interfaces.C.size_t'Last/Stride and then Length=Count*Stride
      and then (Length=0 or else (P/=System.Null_Address
        and then Length<=Interfaces.C.size_t(Storage_Offset'Last)
        and then Integer_Address(Length-1)<=Integer_Address'Last-To_Integer(P)
        and then To_Integer(P) mod Alignment=0)));
   type Input_Access is access all W.Raw_Input; type Output_Access is access all W.Raw_Result;
   type Byte_Access is access all A.Q.Byte; type Grant_Access is access all W.W.Raw_Grant;
   type Use_Access is access all W.W.Raw_Use; type Row_Access is access all L.Raw_Row;
   type Native_Access is access all L.Raw_Native;
   function In_At is new Ada.Unchecked_Conversion(System.Address,Input_Access);
   function Out_At is new Ada.Unchecked_Conversion(System.Address,Output_Access);
   function B_At is new Ada.Unchecked_Conversion(System.Address,Byte_Access);
   function G_At is new Ada.Unchecked_Conversion(System.Address,Grant_Access);
   function H_At is new Ada.Unchecked_Conversion(System.Address,Use_Access);
   function R_At is new Ada.Unchecked_Conversion(System.Address,Row_Access);
   function N_At is new Ada.Unchecked_Conversion(System.Address,Native_Access);
      GS:constant Interfaces.C.size_t:=W.W.Raw_Grant'Size/System.Storage_Unit;
      HS:constant Interfaces.C.size_t:=W.W.Raw_Use'Size/System.Storage_Unit;
      RS:constant Interfaces.C.size_t:=L.Raw_Row'Size/System.Storage_Unit;
      NS:constant Interfaces.C.size_t:=L.Raw_Native'Size/System.Storage_Unit;
   begin
      if not Shape(Input,1,Input_Length,W.Raw_Input'Size/System.Storage_Unit,W.Raw_Input'Alignment)
       or else not Shape(Output,1,Output_Length,W.Raw_Result'Size/System.Storage_Unit,W.Raw_Result'Alignment)
       or else not Shape(Arena,Arena_Length,Arena_Length,1,1)
       or else not Shape(Grants,Grant_Count,Grant_Length,GS,W.W.Raw_Grant'Alignment)
       or else not Shape(Uses,Use_Count,Use_Length,HS,W.W.Raw_Use'Alignment)
       or else not Shape(Rows,Row_Count,Row_Length,RS,L.Raw_Row'Alignment)
       or else not Shape(Observed,Observed_Count,Observed_Length,NS,L.Raw_Native'Alignment)
      then return -1; end if;
      declare
         V:constant W.Raw_Input:=In_At(Input).all;
         Data:A.Q.Byte_Array(1..A.Q.Byte_Count(Arena_Length));
         G:A.Grants(1..A.Q.Byte_Count(Grant_Count)); H:A.Uses(1..A.Q.Byte_Count(Use_Count));
         R:K.L.Row_Array(1..A.Q.Byte_Count(Row_Count)); N:K.L.Native_Array(1..A.Q.Byte_Count(Observed_Count));
      begin
         for I in Data'Range loop Data(I):=B_At(Arena+Storage_Offset(I-1)).all; end loop;
         if not W.Well_Formed(Data,V) then return -1; end if;
         for I in G'Range loop declare X:constant W.W.Raw_Grant:=G_At(Grants+Storage_Offset(Interfaces.C.size_t(I-1)*GS)).all;
            begin if not W.W.Well_Formed(X) then return -1; end if; G(I):=W.W.Decode(X); end; end loop;
         for I in H'Range loop declare X:constant W.W.Raw_Use:=H_At(Uses+Storage_Offset(Interfaces.C.size_t(I-1)*HS)).all;
            begin if not W.W.Well_Formed(X) then return -1; end if; H(I):=W.W.Decode(X); end; end loop;
         for I in R'Range loop declare X:constant L.Raw_Row:=R_At(Rows+Storage_Offset(Interfaces.C.size_t(I-1)*RS)).all;
            begin if not L.Well_Formed(Data,X) then return -1; end if; R(I):=L.Decode(Data,X); end; end loop;
         for I in N'Range loop declare X:constant L.Raw_Native:=N_At(Observed+Storage_Offset(Interfaces.C.size_t(I-1)*NS)).all;
            begin if not L.Well_Formed(Data,X) then return -1; end if; N(I):=L.Decode(Data,X); end; end loop;
         -- All input records/bytes copied before touching possibly aliased output.
         Out_At(Output).Disposition:=K.Decision'Pos(K.Decide(Data,G,H,W.W.Decode(V.Authority.Bound),
           W.W.Decode(V.Authority.Now).Value,W.W.Decode(Data,V.Authority.Facts),L.Decode(Data,V.State),R,N,
           L.Decode(Data,V.Bound),L.Decode(Data,V.Requester),W.W.Decode(V.Peer),V.Collapse));
      end;
      return 0;
   exception when others=>return -1;
      end;
   exception
      when others => return -1;
   end Canonical_Operation_Decide;
   function Operation_Result_Relation
     (Input : System.Address;
      Input_Length : Interfaces.C.size_t;
      Arena : System.Address;
      Arena_Length : Interfaces.C.size_t;
      Grants : System.Address;
      Grant_Count : Interfaces.C.size_t;
      Grant_Length : Interfaces.C.size_t;
      Uses : System.Address;
      Use_Count : Interfaces.C.size_t;
      Use_Length : Interfaces.C.size_t;
      Receipts : System.Address;
      Receipt_Count : Interfaces.C.size_t;
      Receipt_Length : Interfaces.C.size_t;
      Events : System.Address;
      Event_Count : Interfaces.C.size_t;
      Event_Length : Interfaces.C.size_t;
      Output : System.Address;
      Output_Length : Interfaces.C.size_t) return Interfaces.C.int is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package V renames Worldline.Native_Execution_Views;
      package Q renames V.Q;
      package T renames V.T;
      use System.Storage_Elements;
      use type System.Address;
      use type Interfaces.C.size_t;
      use type Interfaces.C.int;
      package Input_Pointers is new System.Address_To_Access_Conversions (T.Raw_Input);
      package Output_Pointers is new System.Address_To_Access_Conversions (T.Raw_Result);
   begin
      if Input_Length /= T.Raw_Input'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Input, Input_Length)
        or else To_Integer (Input) mod T.Raw_Input'Alignment /= 0
        or else not Native_Execution_Array_Shape (Arena, Arena_Length, Q.Byte'Size / System.Storage_Unit, Q.Byte'Alignment)
        or else not Native_Execution_Array_Shape (Grants, Grant_Count, T.Raw_Grant'Size / System.Storage_Unit, T.Raw_Grant'Alignment)
        or else Grant_Length /= Grant_Count * (T.Raw_Grant'Size / System.Storage_Unit)
        or else not Native_Execution_Array_Shape (Uses, Use_Count, T.Raw_Use'Size / System.Storage_Unit, T.Raw_Use'Alignment)
        or else Use_Length /= Use_Count * (T.Raw_Use'Size / System.Storage_Unit)
        or else not Native_Execution_Array_Shape (Receipts, Receipt_Count, T.C.Raw_Row'Size / System.Storage_Unit, T.C.Raw_Row'Alignment)
        or else Receipt_Length /= Receipt_Count * (T.C.Raw_Row'Size / System.Storage_Unit)
        or else not Native_Execution_Array_Shape (Events, Event_Count, T.C.Raw_Row'Size / System.Storage_Unit, T.C.Raw_Row'Alignment)
        or else Event_Length /= Event_Count * (T.C.Raw_Row'Size / System.Storage_Unit)
        or else Output_Length /= T.Raw_Result'Size / System.Storage_Unit
        or else not Native_Execution_Shape (Output, Output_Length)
        or else To_Integer (Output) mod T.Raw_Result'Alignment /= 0 then return -1; end if;
      declare
         Authority_Data_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Arena_Length));
         Authority_Data_View : constant Resource_Bytes_Observer :=
           Observe_Resource_Bytes (Arena, Authority_Data_Bounds);
         Authority_Grants_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Grant_Count));
         Authority_Grants_View : constant Native_Grants_Observer :=
           Observe_Native_Grants (Grants, Authority_Grants_Bounds);
         Authority_Uses_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Use_Count));
         Authority_Uses_View : constant Native_Uses_Observer :=
           Observe_Native_Uses (Uses, Authority_Uses_Bounds);
         Authority_Receipts_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Receipt_Count));
         Authority_Receipts_View : constant Native_Chain_Observer :=
           Observe_Native_Chain (Receipts, Authority_Receipts_Bounds);
         Authority_Events_Bounds : aliased Foreign_Array_Bounds :=
           (First => 1, Last => Interfaces.Integer_64 (Event_Count));
         Authority_Events_View : constant Native_Chain_Observer :=
           Observe_Native_Chain (Events, Authority_Events_Bounds);
         Result : constant V.Result := Worldline.Operation_Result_View.Check (Input_Pointers.To_Pointer (Input).all, Authority_Data_View.all, Authority_Grants_View.all, Authority_Uses_View.all, Authority_Receipts_View.all, Authority_Events_View.all);
      begin
         Flush_Native_Diagnostic_Trace;
         if not Result.Well_Formed then return -1; end if;
         Output_Pointers.To_Pointer (Output).all := (Disposition => Interfaces.Unsigned_8 (Result.Status));
      end;
      return 0;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return -1;
      end;
   exception
      when others => return -1;
   end Operation_Result_Relation;

   function Ordinary_Receipt_Policy_Version_V35 return Interfaces.Unsigned_32 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   begin
      return 35;
      end;
   exception
      when others => return 0;
   end Ordinary_Receipt_Policy_Version_V35;
   function Ordinary_Receipt_Policy_Decide_V35
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Mode : Interfaces.Unsigned_8) return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package O renames Worldline.Ordinary_Receipt_Policy;
      use type Interfaces.C.size_t;
      use type Interfaces.Unsigned_8;
   begin
      if Mode > O.Action'Pos (O.Action'Last)
        or else Data_Length = 0
        or else Data_Length > Interfaces.C.size_t (O.E.Count'Last)
        or else not Owner_Extent (Data, Data_Length, O.E.Bytes'Alignment)
      then return -1; end if;
      declare
         Arena : O.E.Bytes (1 .. O.E.Count (Data_Length));
         for Arena'Address use Data;
         pragma Import (Ada, Arena);
      begin
         return Interfaces.C.int (O.Reason'Pos (O.Decide
           (Arena, (1, O.E.Count (Data_Length)), O.Action'Val (Mode))));
      end;
   exception
      when others => return -1;
      end;
   exception
      when others => return -1;
   end Ordinary_Receipt_Policy_Decide_V35;

   function Ordinary_Receipt_Verify_History_V35
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Differences : System.Address) return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package O renames Worldline.Ordinary_Receipt_Policy;
      use type Interfaces.C.size_t;
      package Mask_Pointers is new System.Address_To_Access_Conversions
        (Interfaces.Unsigned_32);
   begin
      if Data_Length = 0
        or else Data_Length > Interfaces.C.size_t (O.E.Count'Last)
        or else not Owner_Extent (Data, Data_Length, O.E.Bytes'Alignment)
        or else not Owner_Extent (Differences,
          Interfaces.Unsigned_32'Size / System.Storage_Unit,
          Interfaces.Unsigned_32'Alignment)
      then return -1; end if;
      declare
         Arena : O.E.Bytes (1 .. O.E.Count (Data_Length));
         for Arena'Address use Data;
         pragma Import (Ada, Arena);
         Result : constant O.Column_Result := O.Verify_History
           (Arena, (1, O.E.Count (Data_Length)));
      begin
         Mask_Pointers.To_Pointer (Differences).all := Result.Differences;
         return Interfaces.C.int (O.Reason'Pos (Result.Status));
      end;
   exception
      when others => return -1;
      end;
   exception
      when others => return -1;
   end Ordinary_Receipt_Verify_History_V35;

function Transaction_Relation_V1 (Input : System.Address; Length : Interfaces.C.size_t) return Interfaces.Unsigned_8 is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
   package K renames Worldline.Transaction_Relations;
   package E renames K.E;
   use type System.Address;
   use type Interfaces.C.size_t;
begin
   if Input = System.Null_Address or else Length = 0 or else Length > Interfaces.C.size_t (E.Count'Last) or else not Owner_Extent (Input, Length, E.Bytes'Alignment) then return 255; end if;
   declare
      subtype Image is E.Bytes (1 .. E.Count (Length));
      Owned : Image with Import, Address => Input;
   begin
      if not Worldline.Operation_Archive.Valid (Owned, (Owned'First, Owned'Length)) then return 255; end if;
      return Interfaces.Unsigned_8 (K.Decide (Owned, (Owned'First, Owned'Length)));
   end;
exception
   when others => return 255;
      end;
   exception
      when others => return 255;
end Transaction_Relation_V1;
   function Genesis_Archive_Matches_V1
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      File_First, File_Length, Row_First, Row_Length : Interfaces.Integer_64)
      return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package P renames Evaluation_Pending;
      use type Interfaces.Integer_64;
   begin
      if Data_Length > Interfaces.C.size_t (P.Count'Last) or else
        not Owner_Extent (Data, Data_Length, 1) or else
        File_First < 1 or else Row_First < 1 or else
        File_Length < 0 or else Row_Length < 0
      then return 255; end if;
      declare
         --  Foreign mapping is confined to this existing Off boundary.
         --  This constrained thin view is read-only and borrows the original
         --  live DATA lease; no .all assignment or second full-data copy.
         subtype Input_Array is P.Bytes (1 .. P.Count (Data_Length));
         type Input_Access is access constant Input_Array;
         function Input_View is new Ada.Unchecked_Conversion (System.Address, Input_Access);
         File_Span : constant P.Span := (P.Index (File_First), P.Count (File_Length));
         Row_Span : constant P.Span := (P.Index (Row_First), P.Count (Row_Length));
      begin
         if Data_Length = 0 then
            declare Empty : constant P.Bytes (1 .. 0) := (others => 0);
            begin
               return Interfaces.C.int (Canonical_Artifacts.Genesis_Correspondence'Pos
                 (Canonical_Artifacts.Genesis_Archive_Matches (Empty, File_Span, Row_Span)));
            end;
         end if;
         return Interfaces.C.int (Canonical_Artifacts.Genesis_Correspondence'Pos
           (Canonical_Artifacts.Genesis_Archive_Matches
             (Input_View (Data).all, File_Span, Row_Span)));
      end;
   exception
      when others => return 255;
      end;
   exception
      when others => return 255;
   end Genesis_Archive_Matches_V1;

   function Decimal_Binary64_V1
     (Mode : Interfaces.Unsigned_8;
      Data : System.Address; Data_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t)
      return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package P renames Evaluation_Pending;
      use type P.Count;
      use System.Storage_Elements;
      D : constant Integer_Address := To_Integer (Data);
      O : constant Integer_Address := To_Integer (Output);
   begin
      if Mode > 1 or else Data_Length > Interfaces.C.size_t (P.Count'Last) or else
        not Owner_Extent (Data, Data_Length, 1) or else Output_Length /= 8 or else
        not Owner_Extent (Output, Output_Length, 1) or else
        (Data_Length > 0 and then
          (if D <= O then Integer_Address (Data_Length) > O - D else O + 7 >= D))
      then return 255; end if;
      if Data_Length = 0 then return 1; end if;
      declare
         subtype Input_Array is P.Bytes (1 .. P.Count (Data_Length));
         type Input_Access is access constant Input_Array;
         function Input_View is new Ada.Unchecked_Conversion (System.Address, Input_Access);
         Span : constant P.Span := (1, P.Count (Data_Length));
         C : Decimal_Binary64.Conversion;
         B : Interfaces.Unsigned_64;
      begin
         if Mode = 1 then C := Decimal_Binary64.Canonical (Input_View (Data).all, Span);
         else
            declare
               N : constant Exact_Decimal.Number := Exact_Decimal.Parse (Input_View (Data).all, Span, 0);
            begin
               if not N.Valid or else N.After /= Span.Length then return 1; end if;
               C := Decimal_Binary64.Convert (N);
            end;
         end if;
         if not C.Valid then return 1; end if;
         B := C.Encoding;
         for I in reverse 0 .. 7 loop
            Put_Byte (Output, Storage_Offset (I), Interfaces.Unsigned_8 (B mod 256));
            B := B / 256;
         end loop;
         return 0;
      end;
   exception
      when others => return 255;
      end;
   exception
      when others => return 255;
   end Decimal_Binary64_V1;

   function Operation_Archive_JSON_Matches_V1
     (JSON_Data : System.Address; JSON_Length : Interfaces.C.size_t;
      Archive_Data : System.Address; Archive_Length : Interfaces.C.size_t)
      return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package P renames Evaluation_Pending;
   begin
      if JSON_Length > Interfaces.C.size_t (P.Count'Last) or else
        Archive_Length > Interfaces.C.size_t (P.Count'Last) or else
        not Owner_Extent (JSON_Data, JSON_Length, 1) or else
        not Owner_Extent (Archive_Data, Archive_Length, 1) then return 255; end if;
      --  Empty JSON/archive cannot match. Admit original NULL/zero extents
      --  without constructing or dereferencing a null borrowed array view.
      if JSON_Length = 0 or else Archive_Length = 0 then return 0; end if;
      declare
         subtype JSON_Array is P.Bytes (1 .. P.Count (JSON_Length));
         subtype Archive_Array is P.Bytes (1 .. P.Count (Archive_Length));
         type JSON_Access is access constant JSON_Array;
         type Archive_Access is access constant Archive_Array;
         function JSON_View is new Ada.Unchecked_Conversion (System.Address, JSON_Access);
         function Archive_View is new Ada.Unchecked_Conversion (System.Address, Archive_Access);
      begin
         return Boolean'Pos (Canonical_Artifacts.Operation_Archive_JSON_Matches
           (JSON_View (JSON_Data).all, Archive_View (Archive_Data).all,
            (1, P.Count (JSON_Length)), (1, P.Count (Archive_Length))));
      end;
   exception
      when others => return 255;
      end;
   exception
      when others => return 255;
   end Operation_Archive_JSON_Matches_V1;

   function Scoped_Archive_JSON_Matches_V1
     (JSON_Data : System.Address; JSON_Length : Interfaces.C.size_t;
      Archive_Data : System.Address; Archive_Length : Interfaces.C.size_t)
      return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package P renames Evaluation_Pending;
   begin
      if JSON_Length > Interfaces.C.size_t (P.Count'Last) or else
        Archive_Length > Interfaces.C.size_t (P.Count'Last) or else
        not Owner_Extent (JSON_Data, JSON_Length, 1) or else
        not Owner_Extent (Archive_Data, Archive_Length, 1) then return 255; end if;
      if JSON_Length = 0 then return 0; end if;
      declare
         subtype JSON_Array is P.Bytes (1 .. P.Count (JSON_Length));
         type JSON_Access is access constant JSON_Array;
         function JSON_View is new Ada.Unchecked_Conversion (System.Address, JSON_Access);
         JSON_Span : constant P.Span := (1, P.Count (JSON_Length));
      begin
         if Archive_Length = 0 then
            declare
               Empty : constant P.Bytes (1 .. 0) := (others => 0);
            begin
               return Canonical_Artifacts.Genesis_Correspondence'Pos
                 (Canonical_Artifacts.Scoped_Archive_JSON_Matches
                   (JSON_View (JSON_Data).all, Empty, JSON_Span, (1, 0)));
            end;
         end if;
         declare
            subtype Archive_Array is P.Bytes (1 .. P.Count (Archive_Length));
            type Archive_Access is access constant Archive_Array;
            function Archive_View is new Ada.Unchecked_Conversion (System.Address, Archive_Access);
         begin
            return Canonical_Artifacts.Genesis_Correspondence'Pos
              (Canonical_Artifacts.Scoped_Archive_JSON_Matches
                (JSON_View (JSON_Data).all, Archive_View (Archive_Data).all,
                 JSON_Span, (1, P.Count (Archive_Length))));
         end;
      end;
   exception
      when others => return 255;
      end;
   exception
      when others => return 255;
   end Scoped_Archive_JSON_Matches_V1;

   function Journal_Witness_Decide_V1
     (Kind : Interfaces.Unsigned_8;
      Current : System.Address; Current_Length : Interfaces.C.size_t;
      Input : System.Address; Input_Length : Interfaces.C.size_t;
      Decision : access Interfaces.Unsigned_64) return Interfaces.C.int
   is
   begin
      declare
      Native_Call : Native_Call_Guard;
      pragma Unreferenced (Native_Call);
      package W renames Worldline.Journal_Witness;
      package E renames W.E;
   begin
      if Decision = null or else not Owner_Extent
        (Decision.all'Address, Interfaces.Unsigned_64'Size / System.Storage_Unit,
         Interfaces.Unsigned_64'Alignment)
      then return Error_Invalid_Argument; end if;
      if Kind > Interfaces.Unsigned_8 (W.Witness_Kind'Pos (W.Witness_Kind'Last))
         or else Current = System.Null_Address or else Input = System.Null_Address
         or else Current_Length = 0 or else Input_Length = 0
      then
         Decision.all := Interfaces.Unsigned_64 (W.Decision'Pos (W.Input_Invalid));
         return Error_Invalid_Argument;
      end if;
      if Current_Length > Interfaces.C.size_t (E.Count'Last)
         or else Input_Length > Interfaces.C.size_t (E.Count'Last)
         or else Current_Length > Interfaces.C.size_t (System.Storage_Elements.Storage_Offset'Last)
         or else Input_Length > Interfaces.C.size_t (System.Storage_Elements.Storage_Offset'Last)
      then
         Decision.all := Interfaces.Unsigned_64 (W.Decision'Pos (W.Input_Invalid));
         return Error_Too_Large;
      end if;
      if not Owner_Extent (Current, Current_Length, E.Bytes'Alignment)
         or else not Owner_Extent (Input, Input_Length, E.Bytes'Alignment)
      then
         Decision.all := Interfaces.Unsigned_64 (W.Decision'Pos (W.Input_Invalid));
         return Error_Invalid_Argument;
      end if;
      declare
         Current_Bytes : aliased E.Bytes (1 .. E.Count (Current_Length))
           with Import, Address => Current;
         Input_Bytes : aliased E.Bytes (1 .. E.Count (Input_Length))
           with Import, Address => Input;
         Result : constant Interfaces.Unsigned_64 := Interfaces.Unsigned_64
           (W.Decision'Pos (W.Decide
             (W.Witness_Kind'Val (Kind), Current_Bytes, Input_Bytes)));
      begin
         -- All semantic reads precede the sole possibly aliased output write.
         Decision.all := Result;
      end;
      return Error_OK;
   exception
      when Storage_Error => return Error_Too_Large;
      when others => return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end Journal_Witness_Decide_V1;
   -- A null-length imported object still needs an actual aligned base address.
   -- No semantic bytes or authority are manufactured: the empty view has zero
   -- elements. All positive extents remain the original immutable caller lease.
   Empty_Input_Byte : aliased Interfaces.Unsigned_8 := 0;
   function Borrowed_Input_Address
     (Address : System.Address; Length : Interfaces.C.size_t) return System.Address is
     (if Length = 0 then Empty_Input_Byte'Address else Address);


   function Evaluation_Policy_Project_V1
        (      Requirement_Address : System.Address;
         Requirement_Length : Interfaces.C.size_t;
         Additional_Address : System.Address;
         Additional_Length : Interfaces.C.size_t;
         Finalization : Interfaces.Unsigned_8;
         Output : System.Address;
         Capacity : Interfaces.C.size_t)
         return Interfaces.C.size_t is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);

      begin
         if         Requirement_Length > Interfaces.C.size_t (Natural'Last) or else
           not Owner_Extent (Requirement_Address, Requirement_Length, 1) or else
           Additional_Length > Interfaces.C.size_t (Natural'Last) or else
           not Owner_Extent (Additional_Address, Additional_Length, 1) or else
           Finalization > 1 then return 0; end if;
         declare
            Requirement_Owned : constant String (1 .. Natural (Requirement_Length))
              with Import, Address => Borrowed_Input_Address (Requirement_Address, Requirement_Length);
            Additional_Owned : constant String (1 .. Natural (Additional_Length))
              with Import, Address => Borrowed_Input_Address (Additional_Address, Additional_Length);
            Text : constant String := Worldline.Evaluation_Policy.Project (Requirement_Owned, Additional_Owned, Finalization = 1);
         begin
            if Capacity >= Interfaces.C.size_t (Text'Length) and then
              Owner_Extent (Output, Interfaces.C.size_t (Text'Length), 1)
            then
               for I in Text'Range loop
                  Put_Byte (Output, System.Storage_Elements.Storage_Offset (I - Text'First),
                            Interfaces.Unsigned_8 (Character'Pos (Text (I))));
               end loop;
            end if;
            return Interfaces.C.size_t (Text'Length);
         end;
      
      end;
   exception
      when others => return 0;
   end Evaluation_Policy_Project_V1;

   function Evaluation_Capture_Plan_V1
        (      Rows_Address : System.Address;
         Rows_Length : Interfaces.C.size_t;
         Invocations_Address : System.Address;
         Invocations_Length : Interfaces.C.size_t;
         Returns_Address : System.Address;
         Returns_Length : Interfaces.C.size_t;
         Expected_Requirement_Address : System.Address;
         Expected_Requirement_Length : Interfaces.C.size_t;
         Returned_Context_Address : System.Address;
         Returned_Context_Length : Interfaces.C.size_t;
         Output : System.Address;
         Capacity : Interfaces.C.size_t)
         return Interfaces.C.size_t is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);

      begin
         if         Rows_Length > Interfaces.C.size_t (Natural'Last) or else
           not Owner_Extent (Rows_Address, Rows_Length, 1) or else
           Invocations_Length > Interfaces.C.size_t (Natural'Last) or else
           not Owner_Extent (Invocations_Address, Invocations_Length, 1) or else
           Returns_Length > Interfaces.C.size_t (Natural'Last) or else
           not Owner_Extent (Returns_Address, Returns_Length, 1) or else
           Expected_Requirement_Length > Interfaces.C.size_t (Natural'Last) or else
           not Owner_Extent (Expected_Requirement_Address, Expected_Requirement_Length, 1) or else
           Returned_Context_Length > Interfaces.C.size_t (Natural'Last) or else
           not Owner_Extent (Returned_Context_Address, Returned_Context_Length, 1) then return 0; end if;
         declare
            Rows_Owned : constant String (1 .. Natural (Rows_Length))
              with Import, Address => Borrowed_Input_Address (Rows_Address, Rows_Length);
            Invocations_Owned : constant String (1 .. Natural (Invocations_Length))
              with Import, Address => Borrowed_Input_Address (Invocations_Address, Invocations_Length);
            Returns_Owned : constant String (1 .. Natural (Returns_Length))
              with Import, Address => Borrowed_Input_Address (Returns_Address, Returns_Length);
            Expected_Requirement_Owned : constant String (1 .. Natural (Expected_Requirement_Length))
              with Import, Address => Borrowed_Input_Address (Expected_Requirement_Address, Expected_Requirement_Length);
            Returned_Context_Owned : constant String (1 .. Natural (Returned_Context_Length))
              with Import, Address => Borrowed_Input_Address (Returned_Context_Address, Returned_Context_Length);
            Text : constant String := Worldline.Evaluation_Policy.Capture_Plan (Rows_Owned, Invocations_Owned, Returns_Owned, Expected_Requirement_Owned, Returned_Context_Owned);
         begin
            if Capacity >= Interfaces.C.size_t (Text'Length) and then
              Owner_Extent (Output, Interfaces.C.size_t (Text'Length), 1)
            then
               for I in Text'Range loop
                  Put_Byte (Output, System.Storage_Elements.Storage_Offset (I - Text'First),
                            Interfaces.Unsigned_8 (Character'Pos (Text (I))));
               end loop;
            end if;
            return Interfaces.C.size_t (Text'Length);
         end;
      
      end;
   exception
      when others => return 0;
   end Evaluation_Capture_Plan_V1;

-- This snippet belongs inside that existing Off boundary, not a new Off unit.
   package Report_Int_Pointers is new System.Address_To_Access_Conversions (Interfaces.C.int);
   package Report_Size_Pointers is new System.Address_To_Access_Conversions (Interfaces.C.size_t);

   function Report_Parser_ABI return Interfaces.Unsigned_32 is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);

      begin
      return 1;
      end;
   exception
      when others => return 0;
   end Report_Parser_ABI;

   function Parse_Report
        (Format_Address : System.Address; Format_Length : Interfaces.C.size_t;
         Profile_Address : System.Address; Profile_Length : Interfaces.C.size_t;
         Exit_Address : System.Address; Exit_Length : Interfaces.C.size_t;
         Stdout_Address : System.Address; Stdout_Length : Interfaces.C.size_t;
         Stderr_Address : System.Address; Stderr_Length : Interfaces.C.size_t;
         Result_Address : System.Address; Result_Length : Interfaces.C.size_t;
         Result_Present : Interfaces.C.int;
         Output_Address : System.Address; Output_Capacity : Interfaces.C.size_t;
         Output_Required, Status_Output, Class_Output : System.Address)
         return Interfaces.C.int
      is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
         use System.Storage_Elements;
         use type System.Address;
         use type Interfaces.C.size_t;
         use type Interfaces.C.int;
         function Shape (Address : System.Address; Length : Interfaces.C.size_t) return Boolean is
           (Length <= Interfaces.C.size_t (Natural'Last) and then
            (Length = 0 or else (Address /= System.Null_Address and then
             Length <= Interfaces.C.size_t (Storage_Offset'Last) and then
             Integer_Address (Length - 1) <= Integer_Address'Last - To_Integer (Address))));
         function Scalar (Address : System.Address; Size, Alignment : Natural) return Boolean is
           (Address /= System.Null_Address and then To_Integer (Address) mod Integer_Address (Alignment) = 0
            and then Shape (Address, Interfaces.C.size_t (Size / System.Storage_Unit)));
         function Disjoint (A : System.Address; N : Interfaces.C.size_t;
                            B : System.Address; M : Interfaces.C.size_t) return Boolean is
           (N = 0 or else M = 0 or else
             (if To_Integer (A) <= To_Integer (B) then Integer_Address (N) <= To_Integer (B) - To_Integer (A)
              else Integer_Address (M) <= To_Integer (A) - To_Integer (B)));
         Size_Length : constant Interfaces.C.size_t := Interfaces.C.size_t'Size / System.Storage_Unit;
         Int_Length : constant Interfaces.C.size_t := Interfaces.C.int'Size / System.Storage_Unit;
      begin
         if not Shape (Format_Address, Format_Length) or else not Shape (Profile_Address, Profile_Length)
           or else not Shape (Exit_Address, Exit_Length) or else not Shape (Stdout_Address, Stdout_Length)
           or else not Shape (Stderr_Address, Stderr_Length) or else not Shape (Result_Address, Result_Length)
           or else not Shape (Output_Address, Output_Capacity) or else Result_Present not in 0 .. 1
           or else not Scalar (Output_Required, Interfaces.C.size_t'Size, Interfaces.C.size_t'Alignment)
           or else not Scalar (Status_Output, Interfaces.C.int'Size, Interfaces.C.int'Alignment)
           or else not Scalar (Class_Output, Interfaces.C.int'Size, Interfaces.C.int'Alignment)
           or else not Disjoint (Output_Required, Size_Length, Status_Output, Int_Length)
           or else not Disjoint (Output_Required, Size_Length, Class_Output, Int_Length)
           or else not Disjoint (Status_Output, Int_Length, Class_Output, Int_Length)
           or else not Disjoint (Output_Address, Output_Capacity, Output_Required, Size_Length)
           or else not Disjoint (Output_Address, Output_Capacity, Status_Output, Int_Length)
           or else not Disjoint (Output_Address, Output_Capacity, Class_Output, Int_Length)
         then return -1; end if;
         -- The complete parsed result consumes all six immutable inputs before any output write.
         declare
            Format : constant String (1 .. Natural (Format_Length))
              with Import, Address => Borrowed_Input_Address (Format_Address, Format_Length);
            Profile : constant String (1 .. Natural (Profile_Length))
              with Import, Address => Borrowed_Input_Address (Profile_Address, Profile_Length);
            Exit_Code : constant String (1 .. Natural (Exit_Length))
              with Import, Address => Borrowed_Input_Address (Exit_Address, Exit_Length);
            Stdout : constant String (1 .. Natural (Stdout_Length))
              with Import, Address => Borrowed_Input_Address (Stdout_Address, Stdout_Length);
            Stderr : constant String (1 .. Natural (Stderr_Length))
              with Import, Address => Borrowed_Input_Address (Stderr_Address, Stderr_Length);
            Result : constant String (1 .. Natural (Result_Length))
              with Import, Address => Borrowed_Input_Address (Result_Address, Result_Length);
            Parsed : constant Worldline.Report_Parser.Parsed_Report := Worldline.Report_Parser.Parse
              (Format, Profile, Exit_Code, Stdout, Stderr, Result, Result_Present = 1);
         begin
            Report_Size_Pointers.To_Pointer (Output_Required).all := Interfaces.C.size_t (Parsed.Diagnostic_Length);
            Report_Int_Pointers.To_Pointer (Status_Output).all :=
              Interfaces.C.int (Worldline.Report_Parser.Report_Status'Pos (Parsed.Status));
            Report_Int_Pointers.To_Pointer (Class_Output).all :=
              Interfaces.C.int (Worldline.Report_Parser.Classification'Pos (Parsed.Class));
            if Output_Capacity < Interfaces.C.size_t (Parsed.Diagnostic_Length) then return 0; end if;
            for K in Parsed.Diagnostic'Range loop
               Byte_Pointers.To_Pointer (Output_Address + Storage_Offset (K - 1)).all :=
                 Interfaces.Unsigned_8 (Character'Pos (Parsed.Diagnostic (K)));
            end loop;
            return 1;
         end;
      exception
         when others => return -1;
      
      end;
   exception
      when others => return -1;
   end Parse_Report;


   function Protected_Paths_Touched_V1
        (Requirement_Address : System.Address; Requirement_Length : Interfaces.C.size_t;
         Delta_Address : System.Address; Delta_Length : Interfaces.C.size_t)
         return Interfaces.Unsigned_8 is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);

      begin
         if Requirement_Length > Interfaces.C.size_t (Natural'Last) or else
           Delta_Length > Interfaces.C.size_t (Natural'Last) or else
           not Owner_Extent (Requirement_Address, Requirement_Length, 1) or else
           not Owner_Extent (Delta_Address, Delta_Length, 1)
         then return 255; end if;
         declare
            Requirement_Owned : constant String (1 .. Natural (Requirement_Length))
              with Import, Address => Borrowed_Input_Address (Requirement_Address, Requirement_Length);
            Delta_Owned : constant String (1 .. Natural (Delta_Length))
              with Import, Address => Borrowed_Input_Address (Delta_Address, Delta_Length);
         begin
            return Boolean'Pos (Worldline.Protected_Paths.Touched (Requirement_Owned, Delta_Owned));
         end;
      
      end;
   exception
      when others => return 255;
   end Protected_Paths_Touched_V1;


   function Evaluation_Acquisitions_Closed_V1
        (Subject_Address : System.Address; Subject_Length : Interfaces.C.size_t;
         Owners_Address : System.Address; Owners_Length : Interfaces.C.size_t;
         Acquisitions_Address : System.Address; Acquisitions_Length : Interfaces.C.size_t)
         return Interfaces.Unsigned_8 is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
         package E renames Worldline.Archive_Envelope;
         use System.Storage_Elements;
         use type Interfaces.C.size_t;
      begin
         if Subject_Length > Interfaces.C.size_t (E.Count'Last) or else
           Owners_Length > Interfaces.C.size_t (E.Count'Last) or else
           Acquisitions_Length > Interfaces.C.size_t (E.Count'Last) or else
           not Owner_Extent (Subject_Address, Subject_Length, 1) or else
           not Owner_Extent (Owners_Address, Owners_Length, 1) or else
           not Owner_Extent (Acquisitions_Address, Acquisitions_Length, 1)
         then return 255; end if;
         declare
            S : constant E.Bytes (1 .. E.Count (Subject_Length))
              with Import, Address => Borrowed_Input_Address (Subject_Address, Subject_Length);
            O : constant E.Bytes (1 .. E.Count (Owners_Length))
              with Import, Address => Borrowed_Input_Address (Owners_Address, Owners_Length);
            A : constant E.Bytes (1 .. E.Count (Acquisitions_Length))
              with Import, Address => Borrowed_Input_Address (Acquisitions_Address, Acquisitions_Length);
         begin
            return Boolean'Pos (Worldline.Runner_Acquisition_Bytes.Closed
              (S, O, A, (S'First, E.Count (S'Length)), (O'First, E.Count (O'Length)),
               (A'First, E.Count (A'Length))));
         end;
      
      end;
   exception
      when others => return 255;
   end Evaluation_Acquisitions_Closed_V1;


   function Evaluation_Producer_Derive_V1
     (Expected : System.Address; Expected_Length : Interfaces.C.size_t;
      Observed : System.Address; Observed_Length : Interfaces.C.size_t;
      Result_Record : System.Address; Result_Length : Interfaces.C.size_t;
      Declared : System.Address; Declared_Length : Interfaces.C.size_t;
      Agent_Terminal : System.Address; Agent_Terminal_Length : Interfaces.C.size_t;
      Out_Raw, Out_Confinement : System.Address) return Interfaces.Unsigned_8
   is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
      package W renames Worldline.Evaluation_Wire;
      package P renames Worldline.Evaluation_Producer;
      package E renames Worldline.Archive_Envelope;
      use type E.Count;
      use System.Storage_Elements;
      use type Interfaces.C.size_t;
      use type System.Address;
      package Raw_Pointers is new System.Address_To_Access_Conversions (W.Raw_Record);
      package Octet_Pointers is new System.Address_To_Access_Conversions (Interfaces.Unsigned_8);
      Raw_Length : constant Interfaces.C.size_t := W.Raw_Record'Object_Size / System.Storage_Unit;
      function Extent (Base : System.Address; Length : Interfaces.C.size_t) return Boolean is
        (Length <= Interfaces.C.size_t (Natural'Last) and then Owner_Extent (Base, Length, 1));
      function Disjoint (L : System.Address; LL : Interfaces.C.size_t;
         R : System.Address; RL : Interfaces.C.size_t) return Boolean is
        (LL = 0 or else RL = 0 or else
         (if To_Integer (L) <= To_Integer (R) then
            Integer_Address (LL) <= To_Integer (R) - To_Integer (L)
          else Integer_Address (RL) <= To_Integer (L) - To_Integer (R)));
      function Safe_Input (Base : System.Address; Length : Interfaces.C.size_t) return Boolean is
        (Extent (Base, Length) and then
         Disjoint (Base, Length, Out_Raw, Raw_Length) and then
         Disjoint (Base, Length, Out_Confinement, 1));
      function Safe_Arena (Base : System.Address; Length : Interfaces.C.size_t) return Boolean is
        (Length <= Interfaces.C.size_t (E.Count'Last) and then
         Owner_Extent (Base, Length, 1) and then
         Disjoint (Base, Length, Out_Raw, Raw_Length) and then
         Disjoint (Base, Length, Out_Confinement, 1));
      begin
      if not Owner_Extent (Out_Raw, Raw_Length, W.Raw_Record'Alignment) or else
        not Extent (Out_Confinement, 1) or else
        not Disjoint (Out_Raw, Raw_Length, Out_Confinement, 1) or else
        not Safe_Input (Expected, Expected_Length) or else
        not Safe_Input (Observed, Observed_Length) or else
        not Safe_Input (Result_Record, Result_Length) or else
        not Safe_Input (Declared, Declared_Length) or else
        not Safe_Arena (Agent_Terminal, Agent_Terminal_Length) then return 1; end if;
      declare
         Owned_Expected : constant String (1 .. Natural (Expected_Length))
           with Import, Address => Borrowed_Input_Address (Expected, Expected_Length);
         Owned_Observed : constant String (1 .. Natural (Observed_Length))
           with Import, Address => Borrowed_Input_Address (Observed, Observed_Length);
         Owned_Result : constant String (1 .. Natural (Result_Length))
           with Import, Address => Borrowed_Input_Address (Result_Record, Result_Length);
         Owned_Declared : constant String (1 .. Natural (Declared_Length))
           with Import, Address => Borrowed_Input_Address (Declared, Declared_Length);
         Arena : constant E.Bytes (1 .. E.Count (Agent_Terminal_Length))
           with Import, Address => Borrowed_Input_Address (Agent_Terminal, Agent_Terminal_Length);
         Derived : constant P.Produced_Record := P.Derive
           (Owned_Expected, Owned_Observed, Owned_Result, Owned_Declared, "", "",
            Arena, (1, E.Count (Agent_Terminal_Length)));
      begin
         -- All four immutable text views and the independent Count64 arena are fully
         -- consumed before either disjoint, aligned output is published.
         Raw_Pointers.To_Pointer (Out_Raw).all := Derived.Raw;
         Octet_Pointers.To_Pointer (Out_Confinement).all :=
           Interfaces.Unsigned_8 (P.R.Confinement_Observation'Pos (Derived.Confinement));
      end;
      return 0;
   exception
      when others => return 255;
      end;
   exception
      when others => return 255;
   end Evaluation_Producer_Derive_V1;

   package Manager_Size_Pointers is new System.Address_To_Access_Conversions (Interfaces.C.size_t);

   function Manager_Resource_Lifecycle_V1
        (Capture_Address : System.Address; Capture_Length : Interfaces.C.size_t;
         Output_Address : System.Address; Output_Capacity : Interfaces.C.size_t;
         Output_Required : System.Address) return Interfaces.C.int
      is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
         use System.Storage_Elements;
         use type System.Address;
         use type Interfaces.C.size_t;
         function Shape (A : System.Address; N : Interfaces.C.size_t) return Boolean is
           (N <= Interfaces.C.size_t (Natural'Last) and then
            (N = 0 or else (A /= System.Null_Address and then
             N <= Interfaces.C.size_t (Storage_Offset'Last) and then
             Integer_Address (N - 1) <= Integer_Address'Last - To_Integer (A))));
         function Disjoint (A : System.Address; N : Interfaces.C.size_t;
                            B : System.Address; M : Interfaces.C.size_t) return Boolean is
           (N = 0 or else M = 0 or else
            (if To_Integer (A) <= To_Integer (B) then Integer_Address (N) <= To_Integer (B) - To_Integer (A)
             else Integer_Address (M) <= To_Integer (A) - To_Integer (B)));
         Size_Length : constant Interfaces.C.size_t := Interfaces.C.size_t'Size / System.Storage_Unit;
      begin
         if not Shape (Capture_Address, Capture_Length) or else not Shape (Output_Address, Output_Capacity)
           or else Output_Required = System.Null_Address
           or else To_Integer (Output_Required) mod Integer_Address (Interfaces.C.size_t'Alignment) /= 0
           or else not Shape (Output_Required, Size_Length)
           or else not Disjoint (Output_Address, Output_Capacity, Output_Required, Size_Length)
         then return -1; end if;
         declare
            Owned : constant String (1 .. Natural (Capture_Length))
              with Import, Address => Borrowed_Input_Address (Capture_Address, Capture_Length);
         begin
            -- The pure result fully consumes the immutable input before any output write.
            declare
               Result : constant String := Worldline.Manager_Resource_Lifecycle.Decide (Owned);
            begin
               Manager_Size_Pointers.To_Pointer (Output_Required).all := Interfaces.C.size_t (Result'Length);
               if Output_Capacity < Interfaces.C.size_t (Result'Length) then return 0; end if;
               for K in Result'Range loop
                  Byte_Pointers.To_Pointer (Output_Address + Storage_Offset (K - Result'First)).all :=
                    Interfaces.Unsigned_8 (Character'Pos (Result (K)));
               end loop;
               return 1;
            end;
         end;
      exception
         when others => return -1;
      
      end;
   exception
      when others => return -1;
   end Manager_Resource_Lifecycle_V1;

   package Ordinary_U32_Pointers is new System.Address_To_Access_Conversions (Interfaces.Unsigned_32);
   package Ordinary_Size_Pointers is new System.Address_To_Access_Conversions (Interfaces.C.size_t);

   function Ordinary_Reservation_ABI return Interfaces.Unsigned_32 is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);

      begin
      return 1;
      end;
   exception
      when others => return 0;
   end Ordinary_Reservation_ABI;

   function Ordinary_Reservation_Plan
        (Input_Address : System.Address; Input_Length : Interfaces.C.size_t;
         Mask_Address : System.Address; Mask_Length : Interfaces.C.size_t;
         Code_Address, Position_Address : System.Address) return Interfaces.C.int
      is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
         use System.Storage_Elements;
         use type System.Address;
         use type Interfaces.C.size_t;
         use type Interfaces.Unsigned_32;
         function Shape (A : System.Address; N : Interfaces.C.size_t) return Boolean is
           (N <= Interfaces.C.size_t (Natural'Last) and then
            (N = 0 or else (A /= System.Null_Address and then
             N <= Interfaces.C.size_t (Storage_Offset'Last) and then
             Integer_Address (N - 1) <= Integer_Address'Last - To_Integer (A))));
         function Disjoint (A : System.Address; N : Interfaces.C.size_t;
                            B : System.Address; M : Interfaces.C.size_t) return Boolean is
           (N = 0 or else M = 0 or else
            (if To_Integer (A) <= To_Integer (B) then Integer_Address (N) <= To_Integer (B) - To_Integer (A)
             else Integer_Address (M) <= To_Integer (A) - To_Integer (B)));
         U32_Length : constant Interfaces.C.size_t := Interfaces.Unsigned_32'Size / System.Storage_Unit;
         Size_Length : constant Interfaces.C.size_t := Interfaces.C.size_t'Size / System.Storage_Unit;
      begin
         if not Shape (Input_Address, Input_Length) or else not Shape (Mask_Address, Mask_Length)
           or else not Shape (Code_Address, U32_Length) or else Code_Address = System.Null_Address
           or else To_Integer (Code_Address) mod Interfaces.Unsigned_32'Alignment /= 0
           or else not Shape (Position_Address, Size_Length) or else Position_Address = System.Null_Address
           or else To_Integer (Position_Address) mod Interfaces.C.size_t'Alignment /= 0
           or else not Disjoint (Mask_Address, Mask_Length, Code_Address, U32_Length)
           or else not Disjoint (Mask_Address, Mask_Length, Position_Address, Size_Length)
           or else not Disjoint (Code_Address, U32_Length, Position_Address, Size_Length)
         then return -1; end if;
         declare
            Owned : constant String (1 .. Natural (Input_Length))
              with Import, Address => Borrowed_Input_Address (Input_Address, Input_Length);
            Mask : Worldline.Ordinary_Reservation_Lifecycle.Mask_Array (1 .. Natural (Mask_Length));
            Code : Interfaces.Unsigned_32;
            Position : Natural;
         begin
            -- Plan fully consumes the input before any output write; original input/output aliases remain admitted.
            Worldline.Ordinary_Reservation_Lifecycle.Plan (Owned, Mask, Code, Position);
            if Code = 0 then return 0; end if;
            for K in Mask'Range loop
               Byte_Pointers.To_Pointer (Mask_Address + Storage_Offset (K - 1)).all := Mask (K);
            end loop;
            Ordinary_U32_Pointers.To_Pointer (Code_Address).all := Code;
            Ordinary_Size_Pointers.To_Pointer (Position_Address).all := Interfaces.C.size_t (Position);
            return 1;
         end;
      exception
         when others => return -1;
      
      end;
   exception
      when others => return -1;
   end Ordinary_Reservation_Plan;

--  Input is finalization_journal.encode(original complete capture), not JSON

   function Runner_Lifecycle_Allowed_V1
        (Owner_Address : System.Address;
         Owner_Length : Interfaces.C.size_t;
         Requested : Interfaces.Unsigned_8) return Interfaces.Unsigned_8 is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
         package L renames Worldline.Runner_Lifecycle;
         use System.Storage_Elements;
         use type Interfaces.C.size_t;
      begin
         if Owner_Length > Interfaces.C.size_t (L.E.Count'Last) or else
           not Owner_Extent (Owner_Address, Owner_Length, 1) or else
           Requested > L.Action'Pos (L.Action'Last)
         then return 255; end if;
         declare
            Owned : constant L.E.Bytes (1 .. L.E.Count (Owner_Length))
              with Import, Address => Borrowed_Input_Address (Owner_Address, Owner_Length);
         begin
            -- The entire Count64 arena remains caller-owned and immutable through return.
            return Boolean'Pos (L.Allowed
              (Owned, (Owned'First, L.E.Count (Owned'Length)), L.Action'Val (Requested)));
         end;
      
      end;
   exception
      when others => return 255;
   end Runner_Lifecycle_Allowed_V1;

--  Borrow original bytes ONCE at that boundary; no String-sized payload cap.

   function Runner_Outcome_Decide_V1
        (Capture_Address : System.Address;
         Capture_Length : Interfaces.C.size_t;
         Output : System.Address;
         Capacity : Interfaces.C.size_t) return Interfaces.C.size_t is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);

      begin
         if Capture_Length > Interfaces.C.size_t (Worldline.Runner_Outcome.E.Count'Last) or else
           not Owner_Extent (Capture_Address, Capture_Length, 1) then return 0; end if;
         declare
            package E renames Worldline.Runner_Outcome.E;
            Owned : constant E.Bytes (1 .. E.Count (Capture_Length))
              with Import, Address => Borrowed_Input_Address (Capture_Address, Capture_Length);
         begin
            declare
               Text : constant String := Worldline.Runner_Outcome.Decide
                 (Owned, (Owned'First, Owned'Length));
            begin
            if Capacity >= Interfaces.C.size_t (Text'Length) and then
              Owner_Extent (Output, Interfaces.C.size_t (Text'Length), 1)
            then
               for I in Text'Range loop
                  Put_Byte (Output, System.Storage_Elements.Storage_Offset (I - Text'First),
                            Interfaces.Unsigned_8 (Character'Pos (Text (I))));
               end loop;
            end if;
            return Interfaces.C.size_t (Text'Length);
            end;
         end;
      
      end;
   exception
      when others => return 0;
   end Runner_Outcome_Decide_V1;


   function Recovery_Packet_Decide
        (Data : System.Address; Length : Interfaces.C.size_t;
         Collapse_Code, Owner_Code : System.Address) return Interfaces.Unsigned_8
      is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
         package K renames Worldline.Recovery_Packet;
         package E renames K.E;
         package U32_Pointers is new System.Address_To_Access_Conversions (Interfaces.Unsigned_32);
      begin
         if Length = 0 or else Length > Interfaces.C.size_t (E.Count'Last) or else
           not Owner_Extent (Data, Length, 1) or else
           not Owner_Extent (Collapse_Code, 1, 1) or else
           not Owner_Extent (Owner_Code, Interfaces.Unsigned_32'Object_Size / System.Storage_Unit,
                            Interfaces.Unsigned_32'Alignment) or else
           not Disjoint (Collapse_Code, Interfaces.Unsigned_8'Object_Size,
                         Owner_Code, Interfaces.Unsigned_32'Object_Size)
         then return 255; end if;
         -- The complete pure answer consumes all immutable input bytes before output;
         -- original input/output aliases remain valid because no later input is read.
         declare
            Owned : constant E.Bytes (1 .. E.Count (Length))
              with Import, Address => Borrowed_Input_Address (Data, Length);
         begin
            declare
               Answer : constant K.Result := K.Inspect (Owned, (1, E.Count (Length)));
            begin
               Byte_Pointers.To_Pointer (Collapse_Code).all := Answer.Collapse_Code;
               U32_Pointers.To_Pointer (Owner_Code).all := Answer.Owner_Code;
               return K.Status'Pos (Answer.State);
            end;
         end;
      exception when others => return 255;
      
      end;
   exception
      when others => return 255;
   end Recovery_Packet_Decide;

   function Recovery_Packet_Projection_Matches
        (Data : System.Address; Length : Interfaces.C.size_t;
         Expected : System.Address; Expected_Length : Interfaces.C.size_t)
         return Interfaces.Unsigned_8
      is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
         package K renames Worldline.Recovery_Packet;
         package E renames K.E;
      begin
         if Length = 0 or else Expected_Length = 0 or else
           Length > Interfaces.C.size_t (E.Count'Last) or else
           Expected_Length > Interfaces.C.size_t (E.Count'Last) or else
           not Owner_Extent (Data, Length, 1) or else
           not Owner_Extent (Expected, Expected_Length, 1)
         then return 255; end if;
         declare
            Owned : constant E.Bytes (1 .. E.Count (Length))
              with Import, Address => Borrowed_Input_Address (Data, Length);
            Projection : constant E.Bytes (1 .. E.Count (Expected_Length))
              with Import, Address => Borrowed_Input_Address (Expected, Expected_Length);
         begin
            return Boolean'Pos (K.Projection_Matches
              (Owned, (1, E.Count (Length)), Projection, (1, E.Count (Expected_Length))));
         end;
      exception when others => return 255;
      
      end;
   exception
      when others => return 255;
   end Recovery_Packet_Projection_Matches;

   function Recovery_Packet_Decide_With_Facts
        (Data : System.Address; Length : Interfaces.C.size_t;
         Facts : System.Address; Facts_Length : Interfaces.C.size_t;
         Collapse_Code, Owner_Code : System.Address) return Interfaces.Unsigned_8
      is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
         package K renames Worldline.Recovery_Packet;
         package E renames K.E;
         package U32_Pointers is new System.Address_To_Access_Conversions (Interfaces.Unsigned_32);
      begin
         if Length = 0 or else Facts_Length = 0 or else
           Length > Interfaces.C.size_t (E.Count'Last) or else
           Facts_Length > Interfaces.C.size_t (E.Count'Last) or else
           not Owner_Extent (Data, Length, 1) or else
           not Owner_Extent (Facts, Facts_Length, 1) or else
           not Owner_Extent (Collapse_Code, 1, 1) or else
           not Owner_Extent (Owner_Code, Interfaces.Unsigned_32'Object_Size / System.Storage_Unit,
                            Interfaces.Unsigned_32'Alignment) or else
           not Disjoint (Collapse_Code, Interfaces.Unsigned_8'Object_Size,
                         Owner_Code, Interfaces.Unsigned_32'Object_Size)
         then return 255; end if;
         declare
            Owned : constant E.Bytes (1 .. E.Count (Length))
              with Import, Address => Borrowed_Input_Address (Data, Length);
            Adjunct : constant E.Bytes (1 .. E.Count (Facts_Length))
              with Import, Address => Borrowed_Input_Address (Facts, Facts_Length);
         begin
            declare
               Answer : constant K.Result := K.Inspect
                 (Owned, (1, E.Count (Length)), Adjunct, (1, E.Count (Facts_Length)));
            begin
               Byte_Pointers.To_Pointer (Collapse_Code).all := Answer.Collapse_Code;
               U32_Pointers.To_Pointer (Owner_Code).all := Answer.Owner_Code;
               return K.Status'Pos (Answer.State);
            end;
         end;
      exception when others => return 255;
      
      end;
   exception
      when others => return 255;
   end Recovery_Packet_Decide_With_Facts;

   function Recovery_Syntax_Inputs
        (Data : System.Address; Length : Interfaces.C.size_t;
         Operation_Mode : Interfaces.Unsigned_8; Output : System.Address;
         Capacity : Interfaces.C.size_t) return Interfaces.C.size_t
      is
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
         package M renames Worldline.Recovery_Material_Replay;
         package E renames M.E;
      begin
         if Length = 0 or else Operation_Mode > 1 or else
           Length > Interfaces.C.size_t (E.Count'Last) or else
           Capacity > Interfaces.C.size_t (E.Count'Last) or else
           not Owner_Extent (Data, Length, 1) or else
           (Capacity > 0 and then not Owner_Extent (Output, Capacity, 1))
         then return Interfaces.C.size_t'Last; end if;
         declare
            Owned : constant E.Bytes (1 .. E.Count (Length))
              with Import, Address => Borrowed_Input_Address (Data, Length);
         begin
            declare
               Inputs : constant String := M.Syntax_Inputs
                 (Owned, (1, E.Count (Length)),
                  (if Operation_Mode = 0 then E.Recovery else E.Operation));
               Required : constant Interfaces.C.size_t := Inputs'Length;
            begin
               if Required = 0 then return Interfaces.C.size_t'Last; end if;
               if Required <= Capacity then
                  for I in Inputs'Range loop
                     Byte_Pointers.To_Pointer
                       (System.Storage_Elements."+"
                          (Output, System.Storage_Elements.Storage_Offset (I - Inputs'First))).all :=
                       Character'Pos (Inputs (I));
                  end loop;
               end if;
               return Required;
            end;
         end;
      exception when others => return Interfaces.C.size_t'Last;
      
      end;
   exception
      when others => return Interfaces.C.size_t'Last;
   end Recovery_Syntax_Inputs;

   -- Context clauses: with Worldline.Custody_V2_Mutation_Decision;
   --                  with Worldline.Custody_V2_Fold_Engine;
   --                  with Worldline.Custody_V2_Load_Input;
   --                  with Ada.Exceptions;
   package Custody_U64 is new System.Address_To_Access_Conversions (Interfaces.Unsigned_64);
   package Custody_I renames Worldline.Custody_V2_Load_Input;
   package Custody_F renames Worldline.Custody_V2_Fold_Engine;
   package Custody_M renames Worldline.Custody_V2_Mutation_Decision;
   use type Custody_I.Decode_Status;
   function Custody_Bytes_Fit (Pointer : System.Address; Length : Interfaces.C.size_t)
      return Boolean
   is
      use System.Storage_Elements;
   begin
      if Length = 0 then return True; end if;
      return Pointer /= System.Null_Address and then
        Length <= Interfaces.C.size_t (Custody_I.E.Count'Last) and then
        Length <= Interfaces.C.size_t (Storage_Offset'Last) and then
        To_Integer (Pointer) <= Integer_Address'Last - Integer_Address (Length - 1);
   end Custody_Bytes_Fit;
   function Custody_U64_Fits (Pointer : System.Address) return Boolean is
     (Custody_Bytes_Fit (Pointer, Interfaces.Unsigned_64'Size / System.Storage_Unit)
       and then System.Storage_Elements.To_Integer (Pointer) mod
         Interfaces.Unsigned_64'Alignment = 0);
   function Custody_Disjoint (Left : System.Address; Left_Length : Interfaces.C.size_t;
                              Right : System.Address; Right_Length : Interfaces.C.size_t)
      return Boolean
   is
      use System.Storage_Elements;
   begin
      return Left_Length = 0 or else Right_Length = 0 or else
        (To_Integer (Left) <= To_Integer (Right) and then
          Integer_Address (Left_Length) <= To_Integer (Right) - To_Integer (Left)) or else
        (To_Integer (Right) < To_Integer (Left) and then
          Integer_Address (Right_Length) <= To_Integer (Left) - To_Integer (Right));
   end Custody_Disjoint;
   function Custody_Load_Decide_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
   is
   begin
      if not Custody_Bytes_Fit (Input, Length) or else
        not Custody_U64_Fits (Status) or else not Custody_U64_Fits (Position) or else
        not Custody_Disjoint (Status, 8, Position, 8) or else
        not Custody_Disjoint (Input, Length, Status, 8) or else
        not Custody_Disjoint (Input, Length, Position, 8) then return Error_Invalid_Argument; end if;
      declare
         Data : Custody_I.E.Bytes (1 .. Custody_I.E.Count (Length))
           with Import, Address => Input;
         Size : constant Custody_I.Sizes := Custody_I.Counts (Data);
      begin
         Custody_U64.To_Pointer (Status).all := Custody_F.Status'Pos (Custody_F.Input_Malformed);
         Custody_U64.To_Pointer (Position).all := 0;
         if Size.Status /= Custody_I.Parsed then return Error_OK; end if;
         declare
            Value : Custody_I.Parsed_Input (Size.Arena, Size.Events, Size.Heads,
              Size.Roots, Size.Subjects, Size.Alternatives, Size.Blobs);
            Result : Custody_F.Observation;
         begin
            Custody_I.Decode (Data, Value);
            Result := Custody_F.Load_Decide (Value);
            Custody_U64.To_Pointer (Status).all := Interfaces.Unsigned_64 (Custody_F.Status'Pos (Result.Reason));
            Custody_U64.To_Pointer (Position).all := Interfaces.Unsigned_64 (Result.Position);
            return Error_OK;
         end;
      end;
   exception
      when Error : others =>
         Emit_Native_Diagnostic ("wl_custody_load_decide_v2: " & Ada.Exceptions.Exception_Information (Error));
         return Error_Internal;
   end Custody_Load_Decide_V2;
   function Custody_Mutation_Decide_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address; Output : System.Address;
      Capacity : Interfaces.C.size_t; Written : System.Address) return Interfaces.C.int
   is
   begin
      if not Custody_Bytes_Fit (Input, Length) or else
        not Custody_Bytes_Fit (Output, Capacity) or else
        not Custody_U64_Fits (Status) or else not Custody_U64_Fits (Position) or else
        not Custody_U64_Fits (Written) or else
        not Custody_Disjoint (Status, 8, Position, 8) or else
        not Custody_Disjoint (Status, 8, Written, 8) or else
        not Custody_Disjoint (Position, 8, Written, 8) or else
        not Custody_Disjoint (Input, Length, Output, Capacity) or else
        not Custody_Disjoint (Input, Length, Status, 8) or else
        not Custody_Disjoint (Input, Length, Position, 8) or else
        not Custody_Disjoint (Input, Length, Written, 8) or else
        not Custody_Disjoint (Output, Capacity, Status, 8) or else
        not Custody_Disjoint (Output, Capacity, Position, 8) or else
        not Custody_Disjoint (Output, Capacity, Written, 8) then return Error_Invalid_Argument; end if;
      declare
         Data : Custody_I.E.Bytes (1 .. Custody_I.E.Count (Length))
           with Import, Address => Input;
         Result : Custody_M.Observation;
         procedure Publish is
         begin
            Custody_U64.To_Pointer (Status).all := Interfaces.Unsigned_64 (Custody_M.Status_Code (Result));
            Custody_U64.To_Pointer (Position).all := Interfaces.Unsigned_64 (Result.Position);
            Custody_U64.To_Pointer (Written).all := Interfaces.Unsigned_64 (Result.Needed);
         end Publish;
      begin
         Custody_U64.To_Pointer (Status).all := Custody_F.Status'Pos (Custody_F.Input_Malformed);
         Custody_U64.To_Pointer (Position).all := 0;
         Custody_U64.To_Pointer (Written).all := 0;
         if Capacity = 0 then
            declare Empty : Custody_I.E.Bytes (1 .. 0); begin Custody_M.Decide (Data, Empty, Result); end;
         else
            declare Buffer : Custody_I.E.Bytes (1 .. Custody_I.E.Count (Capacity))
              with Import, Address => Output;
            begin Custody_M.Decide (Data, Buffer, Result); end;
         end if;
         Publish;
         if Capacity /= 0 and then Result.Needed > Custody_I.E.Count (Capacity) then return Error_Too_Large; end if;
         return Error_OK;
      end;
   exception
      when Error : others =>
         Emit_Native_Diagnostic ("wl_custody_mutation_decide_v2: " & Ada.Exceptions.Exception_Information (Error));
         return Error_Internal;
   end Custody_Mutation_Decide_V2;
   function Custody_Cleanup_Decide_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
   is
   begin
      if not Custody_Bytes_Fit (Input, Length) or else
        not Custody_U64_Fits (Status) or else not Custody_U64_Fits (Position) or else
        not Custody_Disjoint (Status, 8, Position, 8) or else
        not Custody_Disjoint (Input, Length, Status, 8) or else
        not Custody_Disjoint (Input, Length, Position, 8) then return Error_Invalid_Argument; end if;
      declare
         Data : Custody_I.E.Bytes (1 .. Custody_I.E.Count (Length))
           with Import, Address => Input;
         Result : Custody_M.Cleanup_Observation;
      begin
         Custody_U64.To_Pointer (Status).all :=
           Interfaces.Unsigned_64 (4 + Custody_F.Status'Pos (Custody_F.Input_Malformed));
         Custody_U64.To_Pointer (Position).all := 0;
         Custody_M.Cleanup_Decide (Data, Result);
         Custody_U64.To_Pointer (Status).all :=
           Interfaces.Unsigned_64 (Custody_M.Cleanup_Status_Code (Result));
         Custody_U64.To_Pointer (Position).all := Interfaces.Unsigned_64 (Result.Position);
         return Error_OK;
      end;
   exception
      when Error : others =>
         Emit_Native_Diagnostic ("wl_custody_cleanup_decide_v2: " & Ada.Exceptions.Exception_Information (Error));
         return Error_Internal;
   end Custody_Cleanup_Decide_V2;
   function Custody_Closed_Decide_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
   is
   begin
      if not Custody_Bytes_Fit (Input, Length) or else
        not Custody_U64_Fits (Status) or else not Custody_U64_Fits (Position) or else
        not Custody_Disjoint (Status, 8, Position, 8) or else
        not Custody_Disjoint (Input, Length, Status, 8) or else
        not Custody_Disjoint (Input, Length, Position, 8) then return Error_Invalid_Argument; end if;
      declare
         Data : Custody_I.E.Bytes (1 .. Custody_I.E.Count (Length))
           with Import, Address => Input;
         Result : Custody_M.Serving_Observation;
      begin
         Custody_U64.To_Pointer (Status).all := 0;
         Custody_U64.To_Pointer (Position).all := 0;
         Custody_M.Closed_Decide (Data, Result);
         Custody_U64.To_Pointer (Status).all :=
           Interfaces.Unsigned_64 (Custody_M.SE.Join_Status'Pos (Result.Kind));
         Custody_U64.To_Pointer (Position).all := Interfaces.Unsigned_64 (Result.Position);
         return Error_OK;
      end;
   exception
      when Error : others =>
         Emit_Native_Diagnostic ("wl_custody_closed_decide_v2: " & Ada.Exceptions.Exception_Information (Error));
         return Error_Internal;
   end Custody_Closed_Decide_V2;
   function Custody_Context_View_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address; Output : System.Address;
      Capacity : Interfaces.C.size_t; Written : System.Address) return Interfaces.C.int
   is
   begin
      if not Custody_Bytes_Fit (Input, Length) or else
        not Custody_Bytes_Fit (Output, Capacity) or else
        not Custody_U64_Fits (Status) or else not Custody_U64_Fits (Position) or else
        not Custody_U64_Fits (Written) or else
        not Custody_Disjoint (Status, 8, Position, 8) or else
        not Custody_Disjoint (Status, 8, Written, 8) or else
        not Custody_Disjoint (Position, 8, Written, 8) or else
        not Custody_Disjoint (Input, Length, Output, Capacity) or else
        not Custody_Disjoint (Input, Length, Status, 8) or else
        not Custody_Disjoint (Input, Length, Position, 8) or else
        not Custody_Disjoint (Input, Length, Written, 8) or else
        not Custody_Disjoint (Output, Capacity, Status, 8) or else
        not Custody_Disjoint (Output, Capacity, Position, 8) or else
        not Custody_Disjoint (Output, Capacity, Written, 8) then return Error_Invalid_Argument; end if;
      declare
         Data : Custody_I.E.Bytes (1 .. Custody_I.E.Count (Length))
           with Import, Address => Input;
         Result : Custody_M.Context_Observation;
         procedure Publish is
         begin
            Custody_U64.To_Pointer (Status).all := Interfaces.Unsigned_64 (Custody_F.Status'Pos (Result.Reason));
            Custody_U64.To_Pointer (Position).all := Interfaces.Unsigned_64 (Result.Position);
            Custody_U64.To_Pointer (Written).all := Interfaces.Unsigned_64 (Result.Needed);
         end Publish;
      begin
         Custody_U64.To_Pointer (Status).all := Custody_F.Status'Pos (Custody_F.Input_Malformed);
         Custody_U64.To_Pointer (Position).all := 0;
         Custody_U64.To_Pointer (Written).all := 0;
         if Capacity = 0 then
            declare Empty : Custody_I.E.Bytes (1 .. 0); begin Custody_M.Context_View (Data, Empty, Result); end;
         else
            declare Buffer : Custody_I.E.Bytes (1 .. Custody_I.E.Count (Capacity))
              with Import, Address => Output;
            begin Custody_M.Context_View (Data, Buffer, Result); end;
         end if;
         Publish;
         if Capacity /= 0 and then Result.Needed > Custody_I.E.Count (Capacity) then return Error_Too_Large; end if;
         return Error_OK;
      end;
   exception
      when Error : others =>
         Emit_Native_Diagnostic ("wl_custody_context_view_v2: " & Ada.Exceptions.Exception_Information (Error));
         return Error_Internal;
   end Custody_Context_View_V2;
   function Custody_Retry_Decide_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address; Output : System.Address;
      Capacity : Interfaces.C.size_t; Written : System.Address) return Interfaces.C.int
   is
   begin
      if not Custody_Bytes_Fit (Input, Length) or else
        not Custody_Bytes_Fit (Output, Capacity) or else
        not Custody_U64_Fits (Status) or else not Custody_U64_Fits (Position) or else
        not Custody_U64_Fits (Written) or else
        not Custody_Disjoint (Status, 8, Position, 8) or else
        not Custody_Disjoint (Status, 8, Written, 8) or else
        not Custody_Disjoint (Position, 8, Written, 8) or else
        not Custody_Disjoint (Input, Length, Output, Capacity) or else
        not Custody_Disjoint (Input, Length, Status, 8) or else
        not Custody_Disjoint (Input, Length, Position, 8) or else
        not Custody_Disjoint (Input, Length, Written, 8) or else
        not Custody_Disjoint (Output, Capacity, Status, 8) or else
        not Custody_Disjoint (Output, Capacity, Position, 8) or else
        not Custody_Disjoint (Output, Capacity, Written, 8) then return Error_Invalid_Argument; end if;
      declare
         Data : Custody_I.E.Bytes (1 .. Custody_I.E.Count (Length)) with Import, Address => Input;
         Result : Custody_M.Observation;
      begin
         Custody_U64.To_Pointer (Status).all := Custody_F.Status'Pos (Custody_F.Input_Malformed);
         Custody_U64.To_Pointer (Position).all := 0;
         Custody_U64.To_Pointer (Written).all := 0;
         if Capacity = 0 then
            declare Empty : Custody_I.E.Bytes (1 .. 0); begin Custody_M.Retry_Decide (Data, Empty, Result); end;
         else
            declare Buffer : Custody_I.E.Bytes (1 .. Custody_I.E.Count (Capacity)) with Import, Address => Output;
            begin Custody_M.Retry_Decide (Data, Buffer, Result); end;
         end if;
         Custody_U64.To_Pointer (Status).all := Interfaces.Unsigned_64 (Custody_M.Status_Code (Result));
         Custody_U64.To_Pointer (Position).all := Interfaces.Unsigned_64 (Result.Position);
         Custody_U64.To_Pointer (Written).all := Interfaces.Unsigned_64 (Result.Needed);
         if Capacity /= 0 and then Result.Needed > Custody_I.E.Count (Capacity) then return Error_Too_Large; end if;
         return Error_OK;
      end;
   exception
      when Error : others =>
         Emit_Native_Diagnostic ("wl_custody_retry_decide_v2: " & Ada.Exceptions.Exception_Information (Error));
         return Error_Internal;
   end Custody_Retry_Decide_V2;
   function Custody_Serving_Decide_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
   is
   begin
      if not Custody_Bytes_Fit (Input, Length) or else
        not Custody_U64_Fits (Status) or else not Custody_U64_Fits (Position) or else
        not Custody_Disjoint (Status, 8, Position, 8) or else
        not Custody_Disjoint (Input, Length, Status, 8) or else
        not Custody_Disjoint (Input, Length, Position, 8) then return Error_Invalid_Argument; end if;
      declare
         Data : Custody_I.E.Bytes (1 .. Custody_I.E.Count (Length))
           with Import, Address => Input;
         Result : Custody_M.Serving_Observation;
      begin
         Custody_U64.To_Pointer (Status).all := 0;
         Custody_U64.To_Pointer (Position).all := 0;
         Custody_M.Serving_Decide (Data, Result);
         Custody_U64.To_Pointer (Status).all :=
           Interfaces.Unsigned_64 (Custody_M.SE.Join_Status'Pos (Result.Kind));
         Custody_U64.To_Pointer (Position).all := Interfaces.Unsigned_64 (Result.Position);
         return Error_OK;
      end;
   exception
      when Error : others =>
         Emit_Native_Diagnostic ("wl_custody_serving_decide_v2: " & Ada.Exceptions.Exception_Information (Error));
         return Error_Internal;
   end Custody_Serving_Decide_V2;
   -- Merge after the common custody-v2 CAPI body snippet; reuse its geometry
   -- helpers. Encoding only: no authentication, permission, SQL or effects.
   function Custody_Successor_LE_V2
     (Input : System.Address; Length : Interfaces.C.size_t;
      Output : System.Address; Capacity : Interfaces.C.size_t;
      Needed : System.Address) return Interfaces.C.int
   is
   begin
      if not Custody_Bytes_Fit (Input, Length) or else
        not Custody_Bytes_Fit (Output, Capacity) or else
        not Custody_U64_Fits (Needed) or else
        not Custody_Disjoint (Input, Length, Output, Capacity) or else
        not Custody_Disjoint (Input, Length, Needed, 8) or else
        not Custody_Disjoint (Output, Capacity, Needed, 8) then return Error_Invalid_Argument; end if;
      declare
         Data : Custody_I.E.Bytes (1 .. Custody_I.E.Count (Length))
           with Import, Address => Input;
         N : Custody_I.E.Count;
         Complete : Boolean;
      begin
         Custody_U64.To_Pointer (Needed).all := 0;
         if Capacity = 0 then
            declare Empty : Custody_I.E.Bytes (1 .. 0); begin
               Custody_M.Successor_LE (Data, Empty, N, Complete);
            end;
         else
            declare Buffer : Custody_I.E.Bytes (1 .. Custody_I.E.Count (Capacity))
              with Import, Address => Output;
            begin Custody_M.Successor_LE (Data, Buffer, N, Complete); end;
         end if;
         Custody_U64.To_Pointer (Needed).all := Interfaces.Unsigned_64 (N);
         if N = 0 or else (Capacity /= 0 and then not Complete) then return Error_Too_Large; end if;
         return Error_OK;
      end;
   exception
      when Error : others =>
         Emit_Native_Diagnostic ("wl_custody_successor_le_v2: " & Ada.Exceptions.Exception_Information (Error));
         return Error_Internal;
   end Custody_Successor_LE_V2;
   type Custody_Operation_Query is
     (Startup_Query, Append_Query, Recovery_Query, Bootstrap_Query);

   function Custody_Operation_Decide_V2
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Status, Position : System.Address; Query : Custody_Operation_Query)
      return Interfaces.C.int
   is
      package L renames Worldline.Custody_V2_Load_Input;
      package J renames Worldline.Custody_V2_Operation_Journal;
      use type L.Decode_Status;
      use type L.E.Count;
      use System.Storage_Elements;
      function Actual_Process_ID return Interfaces.C.int
        with Import, Convention => C, External_Name => "getpid";
      function Actual_Effective_User_ID return Interfaces.C.unsigned
        with Import, Convention => C, External_Name => "geteuid";
      procedure Store (At_Address : System.Address; Value : Interfaces.Unsigned_64) is
      begin
         for I in 0 .. 7 loop
            Put_Byte
              (At_Address, Storage_Offset (I),
               Interfaces.Unsigned_8
                 (Interfaces.Shift_Right (Value, I * 8) and 16#FF#));
         end loop;
      end Store;
   begin
      declare
         Native_Call : Native_Call_Guard;
         pragma Unreferenced (Native_Call);
         Native_Status, Native_Position : Interfaces.Unsigned_64 := 0;
      begin
         if Data_Length > Interfaces.C.size_t (L.E.Count'Last) or else
           Data_Length > Interfaces.C.size_t (Storage_Offset'Last)
         then
            return Error_Too_Large;
         end if;
         if not Custody_Bytes_Fit (Data, Data_Length) or else
           Status = System.Null_Address or else Position = System.Null_Address or else
           not Custody_Bytes_Fit (Status, 8) or else
           not Custody_Bytes_Fit (Position, 8) or else
           not Custody_Disjoint (Data, Data_Length, Status, 8) or else
           not Custody_Disjoint (Data, Data_Length, Position, 8) or else
           not Custody_Disjoint (Status, 8, Position, 8)
         then
            return Error_Invalid_Argument;
         end if;
         Store (Status, 0);
         Store (Position, 0);
         declare
            Input : constant L.E.Bytes (1 .. L.E.Count (Data_Length))
              with Import, Address => Borrowed_Input_Address (Data, Data_Length);
         begin
            if Query = Bootstrap_Query then
               declare
                  -- The original C boundary observes the actual caller;
                  -- no producer field supplies a PID or effective user ID.
                  PID : constant Interfaces.C.int := Actual_Process_ID;
                  EUID : constant Interfaces.C.unsigned := Actual_Effective_User_ID;
                  Owned : aliased constant L.E.Bytes := Input;
                  Decision : constant J.Bootstrap_Decision := J.Bootstrap_Decide
                    (Owned, (Owned'First, Owned'Length),
                     Interfaces.Unsigned_32 (PID), Interfaces.Unsigned_32 (EUID));
               begin
                  Native_Status :=
                    Interfaces.Unsigned_64 (J.Bootstrap_Action'Pos (Decision.Status));
                  Native_Position := Interfaces.Unsigned_64 (Decision.Position);
               end;
            else
               declare
                  Sizes : constant L.Sizes := L.Counts (Input);
               begin
                  if Sizes.Status = L.Storage_Extent then
                     return Error_Too_Large;
                  end if;
                  if Sizes.Status /= L.Parsed then
                     return Error_OK;
                  end if;
                  declare
                     Value : L.Parsed_Input
                       (Sizes.Arena, Sizes.Events, Sizes.Heads, Sizes.Roots,
                        Sizes.Subjects, Sizes.Alternatives, Sizes.Blobs);
                  begin
                     -- Decode owns the complete source prefix and decoded
                     -- arena once; no borrowed view escapes this native call.
                     L.Decode (Input, Value);
                     if Value.Status /= L.Parsed then
                        return Error_OK;
                     end if;
                     case Query is
                        when Append_Query =>
                           declare
                              Candidate : constant L.E.Span := L.V.S.Field
                                (Value.Arena, L.V.S.Field
                                   (Value.Arena, Value.Owner_Roster,
                                    "operation_context"),
                                 "append_candidate");
                           begin
                              if J.Append_Allowed (Value, Candidate) then
                                 Native_Status := 1;
                              end if;
                           end;
                        when Recovery_Query =>
                           declare
                              Operation : constant L.E.Span := L.V.S.Field
                                (Value.Arena, L.V.S.Field
                                   (Value.Arena, Value.Owner_Roster,
                                    "operation_context"),
                                 "recovery_operation");
                           begin
                              Native_Status := Interfaces.Unsigned_64
                                (J.Recovery_Action'Pos
                                   (J.Recovery_Decide (Value, Operation)));
                           end;
                        when Startup_Query =>
                           declare
                              Current_Matches, Preparations_Done : Boolean;
                              Head : J.Head_Disposition;
                           begin
                              J.Startup_Decide
                                (Value, Current_Matches, Head, Preparations_Done);
                              if Current_Matches then
                                 Native_Status := Interfaces.Unsigned_64
                                   (J.Head_Disposition'Pos (Head));
                              end if;
                           end;
                        when Bootstrap_Query =>
                           null;
                     end case;
                  end;
               end;
            end if;
         end;
         Store (Status, Native_Status);
         Store (Position, Native_Position);
         return Error_OK;
      exception
         when Error : others =>
            Capture_Native_Exception ("wl_custody_operation_decide_v2: ", Error);
            return Error_Internal;
      end;
   exception
      when others => return Error_Internal;
   end Custody_Operation_Decide_V2;

   function Custody_Operation_Startup_Decide_V2
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
   is
   begin
      return Custody_Operation_Decide_V2
        (Data, Data_Length, Status, Position, Startup_Query);
   end Custody_Operation_Startup_Decide_V2;

   function Custody_Operation_Append_Decide_V2
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
   is
   begin
      return Custody_Operation_Decide_V2
        (Data, Data_Length, Status, Position, Append_Query);
   end Custody_Operation_Append_Decide_V2;

   function Custody_Operation_Recovery_Decide_V2
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
   is
   begin
      return Custody_Operation_Decide_V2
        (Data, Data_Length, Status, Position, Recovery_Query);
   end Custody_Operation_Recovery_Decide_V2;

   function Custody_Operation_Bootstrap_Decide_V2
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Status, Position : System.Address) return Interfaces.C.int
   is
   begin
      return Custody_Operation_Decide_V2
        (Data, Data_Length, Status, Position, Bootstrap_Query);
   end Custody_Operation_Bootstrap_Decide_V2;

   package CP renames Worldline.Custody_V2_Provision;
   type Provision_Output is record
      Status : Interfaces.C.int;
      Failing_Row : Interfaces.Integer_64;
   end record with Convention => C;
   package Provision_Output_Pointers is new System.Address_To_Access_Conversions (Provision_Output);
   function Custody_Provision_Version return Interfaces.Unsigned_32 is (2);
   function Custody_Provision_Layout (Kind, Field : Interfaces.Unsigned_8)
      return Interfaces.C.size_t is
      S : Retained_Span;
      R : Provision_Output;
   begin
      case Kind is
         when 1 =>
            case Field is
               when 0 => return Retained_Span'Object_Size / System.Storage_Unit;
               when 1 => return Retained_Span'Alignment;
               when 2 => return S.First'Position;
               when 3 => return S.Length'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when 2 =>
            case Field is
               when 0 => return Provision_Output'Object_Size / System.Storage_Unit;
               when 1 => return Provision_Output'Alignment;
               when 2 => return R.Status'Position;
               when 3 => return R.Failing_Row'Position;
               when others => return Interfaces.C.size_t'Last;
            end case;
         when others => return Interfaces.C.size_t'Last;
      end case;
   end Custody_Provision_Layout;
   function Custody_Provision_Verify
     (Data : System.Address; Data_Length : Interfaces.C.size_t;
      Spans : System.Address; Span_Count, Genesis_Count, Event_Count, Head_Count : Interfaces.C.size_t;
      Output : System.Address; Output_Size : Interfaces.C.size_t) return Interfaces.C.int
   is
      use System.Storage_Elements;
      use type RC.E.Count;
      use type Interfaces.Integer_64;
      Stride : constant Interfaces.C.size_t := Retained_Span'Object_Size / System.Storage_Unit;
      Expected : Interfaces.C.size_t := 37;
   begin
      -- Counts bound owned host storage only, never numeric quantities or key values.
      if Genesis_Count > (Interfaces.C.size_t'Last - Expected) / 2 then return Error_Invalid_Argument; end if;
      Expected := Expected + Genesis_Count * 2;
      if Event_Count > (Interfaces.C.size_t'Last - Expected) / 7 then return Error_Invalid_Argument; end if;
      Expected := Expected + Event_Count * 7;
      if Head_Count > (Interfaces.C.size_t'Last - Expected) / 3 then return Error_Invalid_Argument; end if;
      Expected := Expected + Head_Count * 3;
      if Span_Count /= Expected or else
        Data_Length > Interfaces.C.size_t (RC.E.Count'Last) or else
        Span_Count > Interfaces.C.size_t (RC.E.Count'Last) or else
        Span_Count > Interfaces.C.size_t (Storage_Offset'Last) / Stride or else
        not Owner_Extent (Data, Data_Length, 1) or else
        not Owner_Extent (Spans, Span_Count * Stride, Retained_Span'Alignment) or else
        Output_Size /= Provision_Output'Object_Size / System.Storage_Unit or else
        not Owner_Extent (Output, Output_Size, Provision_Output'Alignment)
      then return Error_Invalid_Argument; end if;
      declare
         A : RC.E.Bytes (1 .. RC.E.Count (Data_Length));
         type Span_Array is array (RC.E.Q.Byte_Index range <>) of RC.E.Span;
         Owned : Span_Array (1 .. RC.E.Count (Span_Count));
         G : RC.Genesis_Rows (1 .. RC.E.Count (Genesis_Count));
         E : RC.Event_Rows (1 .. RC.E.Count (Event_Count));
         H : RC.Head_Rows (1 .. RC.E.Count (Head_Count));
         Selected : CP.Selected_Artifacts;
         Prior : CP.M.Context_Inputs;
         P : RC.E.Count := 0;
         Cursor : RC.E.Count := 37;
         function Take return RC.E.Span is
         begin
            Cursor := Cursor + 1;
            return Owned (Cursor);
         end Take;
      begin
         for I in A'Range loop A (I) := Get_Byte (Data, Storage_Offset (I - 1)); end loop;
         for I in Owned'Range loop
            declare
               Raw : constant Retained_Span := Retained_Span_Pointers.To_Pointer
                 (Spans + Storage_Offset (Interfaces.C.size_t (I - 1) * Stride)).all;
            begin
               if Raw.First < 1 or else Raw.Length < 0 then return Error_Invalid_Argument; end if;
               Owned (I) := (RC.E.Q.Byte_Index (Raw.First), RC.E.Count (Raw.Length));
               if not RC.E.C.P.Valid (A, Owned (I)) then return Error_Invalid_Argument; end if;
            end;
         end loop;
         for Item in Selected'Range loop
            Selected (Item).Raw := Owned (P + 1);
            Selected (Item).Encoded := Owned (P + 2);
            Selected (Item).Path := Owned (P + 3);
            P := P + 3;
         end loop;
         P := 12;
         for Item in Prior'Range loop
            Prior (Item).Raw := Owned (P + 1);
            Prior (Item).Actual_Path := Owned (P + 2);
            Prior (Item).Retained_Path := Owned (P + 3);
            Prior (Item).Retained_SHA256 := Owned (P + 4);
            P := P + 4;
         end loop;
         -- Sequential assignments preserve declared field order; no evaluation-
         -- order dependence from side-effecting function calls in aggregates.
         for I in G'Range loop G (I).Name := Take; G (I).Value := Take; end loop;
         for I in E'Range loop
            E (I).Event_Id := Take; E (I).Previous := Take;
            E (I).Operation := Take; E (I).Kind := Take;
            E (I).Record_Archive := Take; E (I).Mac := Take; E (I).Base_Archive := Take;
         end loop;
         for I in H'Range loop
            H (I).Name := Take; H (I).Event_Id := Take; H (I).Mac := Take;
         end loop;
         declare
            Value : constant CP.Result := CP.Decide
              (A, Selected, Owned (10), Owned (11), Owned (12), Prior,
               Owned (33), Owned (34), Owned (35), Owned (36), Owned (37), G, E, H);
            Result : constant Provision_Output :=
              (Status => CP.Status'Pos (Value.State),
               Failing_Row => Interfaces.Integer_64 (Value.Position));
         begin
            -- All input bytes/spans/rows owned before writing potentially aliased output.
            Provision_Output_Pointers.To_Pointer (Output).all := Result;
         end;
      end;
      Flush_Native_Diagnostic_Trace;
      return Error_OK;
   exception when others =>
      Flush_Native_Diagnostic_Trace;
      return Error_Internal;
   end Custody_Provision_Verify;
   package Emitter_S renames Worldline.Root_Output_Sequence;
   package Emitter_C renames Worldline.Emitter_Allocation_Capture;
   package Emitter_Size is new System.Address_To_Access_Conversions
     (Interfaces.C.size_t);
   function Emitter_Size_Fits (Pointer : System.Address) return Boolean is
     (Custody_Bytes_Fit
        (Pointer, Interfaces.C.size_t'Size / System.Storage_Unit)
      and then System.Storage_Elements.To_Integer (Pointer) mod
        Interfaces.C.size_t'Alignment = 0);

   function Root_Worker_Output_Next_V1
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address; Ordinal : System.Address;
      Capacity : Interfaces.C.size_t; Ordinal_Length : System.Address)
      return Interfaces.C.int
   is
      Size_Bytes : constant Interfaces.C.size_t :=
        Interfaces.C.size_t'Size / System.Storage_Unit;
   begin
      if not Custody_Bytes_Fit (Input, Length) or else
        not Custody_Bytes_Fit (Ordinal, Capacity) or else
        not Custody_U64_Fits (Status) or else
        not Custody_U64_Fits (Position) or else
        not Emitter_Size_Fits (Ordinal_Length) or else
        not Custody_Disjoint (Status, 8, Position, 8) or else
        not Custody_Disjoint (Status, 8, Ordinal_Length, Size_Bytes) or else
        not Custody_Disjoint (Position, 8, Ordinal_Length, Size_Bytes) or else
        not Custody_Disjoint (Ordinal, Capacity, Status, 8) or else
        not Custody_Disjoint (Ordinal, Capacity, Position, 8) or else
        not Custody_Disjoint (Ordinal, Capacity, Ordinal_Length, Size_Bytes)
      then
         return Error_Invalid_Argument;
      end if;
      declare
         Buffer : Emitter_S.E.Bytes (1 .. Emitter_S.E.Count (Capacity));
         Result : Emitter_S.Output_Observation;
      begin
         declare
            Bounds : aliased Foreign_Array_Bounds :=
              (First => 1, Last => Interfaces.Integer_64 (Length));
         begin
            Emitter_C.Capture (Observe_Resource_Bytes (Input, Bounds), Buffer, Result);
         end;
         Flush_Native_Diagnostic_Trace;
         -- Input view has ceased to exist; all foreign writes follow capture.
         Custody_U64.To_Pointer (Status).all :=
           Interfaces.Unsigned_64 (Emitter_S.Allocation_Status'Pos (Result.Kind));
         Custody_U64.To_Pointer (Position).all :=
           Interfaces.Unsigned_64 (Result.Position);
         Emitter_Size.To_Pointer (Ordinal_Length).all :=
           Interfaces.C.size_t (Result.Needed);
         if Capacity /= 0 and then Result.Needed > Emitter_S.E.Count (Capacity)
         then
            return Error_Too_Large;
         end if;
         for J in 1 .. Result.Written loop
            Put_Byte
              (Ordinal, System.Storage_Elements.Storage_Offset (J - 1),
               Interfaces.Unsigned_8 (Buffer (J)));
         end loop;
         return Error_OK;
      end;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return Error_Internal;
   end Root_Worker_Output_Next_V1;

   function Root_Worker_Output_Replay_V1
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address; Ordinal : System.Address;
      Capacity : Interfaces.C.size_t; Ordinal_Length : System.Address)
      return Interfaces.C.int
   is
      Size_Bytes : constant Interfaces.C.size_t :=
        Interfaces.C.size_t'Size / System.Storage_Unit;
   begin
      if not Custody_Bytes_Fit (Input, Length) or else
        not Custody_Bytes_Fit (Ordinal, Capacity) or else
        not Custody_U64_Fits (Status) or else
        not Custody_U64_Fits (Position) or else
        not Emitter_Size_Fits (Ordinal_Length) or else
        not Custody_Disjoint (Status, 8, Position, 8) or else
        not Custody_Disjoint (Status, 8, Ordinal_Length, Size_Bytes) or else
        not Custody_Disjoint (Position, 8, Ordinal_Length, Size_Bytes) or else
        not Custody_Disjoint (Ordinal, Capacity, Status, 8) or else
        not Custody_Disjoint (Ordinal, Capacity, Position, 8) or else
        not Custody_Disjoint (Ordinal, Capacity, Ordinal_Length, Size_Bytes)
      then
         return Error_Invalid_Argument;
      end if;
      declare
         Buffer : Emitter_S.E.Bytes (1 .. Emitter_S.E.Count (Capacity));
         Result : Emitter_S.Output_Observation;
      begin
         declare
            Bounds : aliased Foreign_Array_Bounds :=
              (First => 1, Last => Interfaces.Integer_64 (Length));
         begin
            Emitter_C.Replay_Capture (Observe_Resource_Bytes (Input, Bounds), Buffer, Result);
         end;
         Flush_Native_Diagnostic_Trace;
         -- Input view has ceased to exist; all foreign writes follow capture.
         Custody_U64.To_Pointer (Status).all :=
           Interfaces.Unsigned_64 (Emitter_S.Allocation_Status'Pos (Result.Kind));
         Custody_U64.To_Pointer (Position).all :=
           Interfaces.Unsigned_64 (Result.Position);
         Emitter_Size.To_Pointer (Ordinal_Length).all :=
           Interfaces.C.size_t (Result.Needed);
         if Capacity /= 0 and then Result.Needed > Emitter_S.E.Count (Capacity)
         then
            return Error_Too_Large;
         end if;
         for J in 1 .. Result.Written loop
            Put_Byte
              (Ordinal, System.Storage_Elements.Storage_Offset (J - 1),
               Interfaces.Unsigned_8 (Buffer (J)));
         end loop;
         return Error_OK;
      end;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return Error_Internal;
   end Root_Worker_Output_Replay_V1;
   function Root_Worker_Output_Written_V1
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address; Ordinal : System.Address;
      Capacity : Interfaces.C.size_t; Ordinal_Length : System.Address)
      return Interfaces.C.int
   is
      Size_Bytes : constant Interfaces.C.size_t :=
        Interfaces.C.size_t'Size / System.Storage_Unit;
   begin
      if not Custody_Bytes_Fit (Input, Length) or else
        not Custody_Bytes_Fit (Ordinal, Capacity) or else
        not Custody_U64_Fits (Status) or else
        not Custody_U64_Fits (Position) or else
        not Emitter_Size_Fits (Ordinal_Length) or else
        not Custody_Disjoint (Status, 8, Position, 8) or else
        not Custody_Disjoint (Status, 8, Ordinal_Length, Size_Bytes) or else
        not Custody_Disjoint (Position, 8, Ordinal_Length, Size_Bytes) or else
        not Custody_Disjoint (Ordinal, Capacity, Status, 8) or else
        not Custody_Disjoint (Ordinal, Capacity, Position, 8) or else
        not Custody_Disjoint (Ordinal, Capacity, Ordinal_Length, Size_Bytes)
      then
         return Error_Invalid_Argument;
      end if;
      declare
         Buffer : Emitter_S.E.Bytes (1 .. Emitter_S.E.Count (Capacity));
         Result : Emitter_S.Output_Observation;
      begin
         declare
            Bounds : aliased Foreign_Array_Bounds :=
              (First => 1, Last => Interfaces.Integer_64 (Length));
         begin
            Emitter_C.Written_Capture (Observe_Resource_Bytes (Input, Bounds), Buffer, Result);
         end;
         Flush_Native_Diagnostic_Trace;
         -- Input view has ceased to exist; all foreign writes follow capture.
         Custody_U64.To_Pointer (Status).all :=
           Interfaces.Unsigned_64 (Emitter_S.Allocation_Status'Pos (Result.Kind));
         Custody_U64.To_Pointer (Position).all :=
           Interfaces.Unsigned_64 (Result.Position);
         Emitter_Size.To_Pointer (Ordinal_Length).all :=
           Interfaces.C.size_t (Result.Needed);
         if Capacity /= 0 and then Result.Needed > Emitter_S.E.Count (Capacity)
         then
            return Error_Too_Large;
         end if;
         for J in 1 .. Result.Written loop
            Put_Byte
              (Ordinal, System.Storage_Elements.Storage_Offset (J - 1),
               Interfaces.Unsigned_8 (Buffer (J)));
         end loop;
         return Error_OK;
      end;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return Error_Internal;
   end Root_Worker_Output_Written_V1;

   function Root_Worker_Output_Prefix_V1
     (Input : System.Address; Length : Interfaces.C.size_t;
      Status, Position : System.Address; Ordinal : System.Address;
      Capacity : Interfaces.C.size_t; Ordinal_Length : System.Address)
      return Interfaces.C.int
   is
      Size_Bytes : constant Interfaces.C.size_t :=
        Interfaces.C.size_t'Size / System.Storage_Unit;
   begin
      if not Custody_Bytes_Fit (Input, Length) or else
        not Custody_Bytes_Fit (Ordinal, Capacity) or else
        not Custody_U64_Fits (Status) or else
        not Custody_U64_Fits (Position) or else
        not Emitter_Size_Fits (Ordinal_Length) or else
        not Custody_Disjoint (Status, 8, Position, 8) or else
        not Custody_Disjoint (Status, 8, Ordinal_Length, Size_Bytes) or else
        not Custody_Disjoint (Position, 8, Ordinal_Length, Size_Bytes) or else
        not Custody_Disjoint (Ordinal, Capacity, Status, 8) or else
        not Custody_Disjoint (Ordinal, Capacity, Position, 8) or else
        not Custody_Disjoint (Ordinal, Capacity, Ordinal_Length, Size_Bytes)
      then
         return Error_Invalid_Argument;
      end if;
      declare
         Buffer : Emitter_S.E.Bytes (1 .. Emitter_S.E.Count (Capacity));
         Result : Emitter_S.Output_Observation;
      begin
         declare
            Bounds : aliased Foreign_Array_Bounds :=
              (First => 1, Last => Interfaces.Integer_64 (Length));
         begin
            Emitter_C.Prefix_Capture (Observe_Resource_Bytes (Input, Bounds), Buffer, Result);
         end;
         Flush_Native_Diagnostic_Trace;
         -- Input view has ceased to exist; all foreign writes follow capture.
         Custody_U64.To_Pointer (Status).all :=
           Interfaces.Unsigned_64 (Emitter_S.Allocation_Status'Pos (Result.Kind));
         Custody_U64.To_Pointer (Position).all :=
           Interfaces.Unsigned_64 (Result.Position);
         Emitter_Size.To_Pointer (Ordinal_Length).all :=
           Interfaces.C.size_t (Result.Needed);
         if Capacity /= 0 and then Result.Needed > Emitter_S.E.Count (Capacity)
         then
            return Error_Too_Large;
         end if;
         for J in 1 .. Result.Written loop
            Put_Byte
              (Ordinal, System.Storage_Elements.Storage_Offset (J - 1),
               Interfaces.Unsigned_8 (Buffer (J)));
         end loop;
         return Error_OK;
      end;
   exception
      when others =>
         Flush_Native_Diagnostic_Trace;
         return Error_Internal;
   end Root_Worker_Output_Prefix_V1;
end Worldline.C_API;

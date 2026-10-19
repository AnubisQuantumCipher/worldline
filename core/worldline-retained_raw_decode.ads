with Worldline.Collapse_Wire;
with Worldline.Canonical_Operation_Wire;
with Worldline.Canonical_Exchange_Wire;
with Worldline.Canonical_Owner_Completion_Wire;
with Resource_Run_Ledger_Wire;
with Resource_Scoped_Run_Ledger_Wire;
with Resource_Actor_Admission_Wire;
with Resource_Observation_Classification_Wire;
with Worldline.Resource_Actor_Execution_Wire;
with Worldline.Resource_Child_Execution_Wire;
with Worldline.Operation_Authority_Wire;
with Worldline.Chain_Authority_Wire;
with Worldline.Recovery_Authorization_V3_Wire;
with Resource_Quantities;
with System;
package Worldline.Retained_Raw_Decode with SPARK_Mode is
   package Q renames Resource_Quantities;
   package W renames Resource_Run_Ledger_Wire;
   package N renames Resource_Scoped_Run_Ledger_Wire;
   package D renames Resource_Actor_Admission_Wire;
   package O renames Resource_Observation_Classification_Wire;
   package X renames Worldline.Resource_Actor_Execution_Wire;
   package Y renames Worldline.Resource_Child_Execution_Wire;
   package T renames Worldline.Operation_Authority_Wire;
   package C renames Worldline.Chain_Authority_Wire;
   package RW renames Worldline.Recovery_Authorization_V3_Wire;
   package CW renames Worldline.Collapse_Wire;
   package CO renames Worldline.Canonical_Operation_Wire;
   package CX renames Worldline.Canonical_Exchange_Wire;
   package HC renames Worldline.Canonical_Owner_Completion_Wire;
   use type Q.Byte_Count;
   --  Preserve value images and also decode complete native object images.
   --  C components may include alignment padding beyond their value size.
   --  Only the two compiler-pinned sizes are admitted; padding validation
   --  examines every supplied byte and still rejects nonzero padding.
   function Load (Data : Q.Byte_Array) return D.Raw_Packet
     with Global => null, Pre => Data'Length = D.Raw_Packet'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return N.Raw_Packet
     with Global => null, Pre => Data'Length = N.Raw_Packet'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return N.Raw_State
     with Global => null, Pre => Data'Length = N.Raw_State'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return W.Raw_Context
     with Global => null, Pre => Data'Length = W.Raw_Context'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return W.Raw_Id
     with Global => null, Pre => Data'Length = W.Raw_Id'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return W.Raw_Epoch
     with Global => null, Pre => Data'Length = W.Raw_Epoch'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return W.Raw_Quantity
     with Global => null, Pre => Data'Length = W.Raw_Quantity'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return N.Raw_Current_Observation
     with Global => null, Pre => Data'Length = N.Raw_Current_Observation'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return N.Raw_Intent
     with Global => null, Pre => Data'Length = N.Raw_Intent'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return W.Raw_Request
     with Global => null, Pre => Data'Length = W.Raw_Request'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return W.Raw_Binding
     with Global => null, Pre => Data'Length = W.Raw_Binding'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return W.Raw_Row
     with Global => null, Pre => Data'Length = W.Raw_Row'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return D.Raw_Observation
     with Global => null, Pre => Data'Length = D.Raw_Observation'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return X.Raw_Crosswalk
     with Global => null, Pre => Data'Length = X.Raw_Crosswalk'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return C.Raw_Digest
     with Global => null, Pre => Data'Length = C.Raw_Digest'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return C.Raw_Hash
     with Global => null, Pre => Data'Length = C.Raw_Hash'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return Y.Raw_Input
     with Global => null, Pre => Data'Length = Y.Raw_Input'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return Y.Raw_Controller
     with Global => null, Pre => Data'Length = Y.Raw_Controller'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return Y.Raw_Process
     with Global => null, Pre => Data'Length = Y.Raw_Process'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return Y.Raw_Task
     with Global => null, Pre => Data'Length = Y.Raw_Task'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return Y.Raw_Namespace
     with Global => null, Pre => Data'Length = Y.Raw_Namespace'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return T.Raw_Input
     with Global => null, Pre => Data'Length = T.Raw_Input'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return T.Raw_Binding
     with Global => null, Pre => Data'Length = T.Raw_Binding'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return T.Raw_Ids
     with Global => null, Pre => Data'Length = T.Raw_Ids'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return T.Raw_UID
     with Global => null, Pre => Data'Length = T.Raw_UID'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return T.Raw_Quantity
     with Global => null, Pre => Data'Length = T.Raw_Quantity'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return T.Raw_Evidence
     with Global => null, Pre => Data'Length = T.Raw_Evidence'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return RW.Raw_Request
     with Global => null, Pre => (Data'Length = RW.Raw_Request'Size / System.Storage_Unit
       or else Data'Length = RW.Raw_Request'Object_Size / System.Storage_Unit);
   function Load (Data : Q.Byte_Array) return RW.Raw_Binding
     with Global => null, Pre => Data'Length = RW.Raw_Binding'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return RW.Raw_Digest
     with Global => null, Pre => Data'Length = RW.Raw_Digest'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return RW.Raw_Hash
     with Global => null, Pre => Data'Length = RW.Raw_Hash'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return RW.Raw_Epoch
     with Global => null, Pre => Data'Length = RW.Raw_Epoch'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return RW.Raw_Native
     with Global => null, Pre => Data'Length = RW.Raw_Native'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return T.Raw_Grant
     with Global => null, Pre => Data'Length = T.Raw_Grant'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return T.Raw_Rights
     with Global => null, Pre => Data'Length = T.Raw_Rights'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return T.Raw_Use
     with Global => null, Pre => (Data'Length = T.Raw_Use'Size / System.Storage_Unit
       or else Data'Length = T.Raw_Use'Object_Size / System.Storage_Unit);
   function Load (Data : Q.Byte_Array) return C.Raw_Row
     with Global => null, Pre => Data'Length = C.Raw_Row'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return D.Raw_Capability
     with Global => null, Pre => Data'Length = D.Raw_Capability'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return N.Raw_Scope_Frame
     with Global => null, Pre => Data'Length = N.Raw_Scope_Frame'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return N.Raw_Projection
     with Global => null, Pre => Data'Length = N.Raw_Projection'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return N.Raw_Physical_Key
     with Global => null, Pre => Data'Length = N.Raw_Physical_Key'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return N.Raw_Bucket
     with Global => null, Pre => Data'Length = N.Raw_Bucket'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return W.Raw_Native
     with Global => null, Pre => (Data'Length = W.Raw_Native'Size / System.Storage_Unit
       or else Data'Length = W.Raw_Native'Object_Size / System.Storage_Unit);
   function Load (Data : Q.Byte_Array) return O.Raw_Facts
     with Global => null, Pre => (Data'Length = O.Raw_Facts'Size / System.Storage_Unit
       or else Data'Length = O.Raw_Facts'Object_Size / System.Storage_Unit);
   function Load (Data : Q.Byte_Array) return W.Raw_Result
     with Global => null, Pre => Data'Length = W.Raw_Result'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return T.Raw_Result
     with Global => null, Pre => Data'Length = T.Raw_Result'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return HC.Raw_Input
     with Global => null, Pre => Data'Length = HC.Raw_Input'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return CX.Raw_Input
     with Global => null, Pre => (Data'Length = CX.Raw_Input'Size / System.Storage_Unit
       or else Data'Length = CX.Raw_Input'Object_Size / System.Storage_Unit);
   function Load (Data : Q.Byte_Array) return CO.Raw_Input
     with Global => null, Pre => (Data'Length = CO.Raw_Input'Size / System.Storage_Unit
       or else Data'Length = CO.Raw_Input'Object_Size / System.Storage_Unit);
   function Load (Data : Q.Byte_Array) return W.Raw_State
     with Global => null, Pre => Data'Length = W.Raw_State'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return CW.Raw_Request
     with Global => null, Pre => Data'Length = CW.Raw_Request'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return CW.Raw_Optional_Hash
     with Global => null, Pre => Data'Length = CW.Raw_Optional_Hash'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return CW.Raw_Bytes_32
     with Global => null, Pre => Data'Length = CW.Raw_Bytes_32'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return CW.Raw_Optional_Counter
     with Global => null, Pre => Data'Length = CW.Raw_Optional_Counter'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return CW.Raw_Bytes_8
     with Global => null, Pre => Data'Length = CW.Raw_Bytes_8'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return CX.Raw_Material
     with Global => null, Pre => (Data'Length = CX.Raw_Material'Size / System.Storage_Unit
       or else Data'Length = CX.Raw_Material'Object_Size / System.Storage_Unit);
   function Load (Data : Q.Byte_Array) return HC.Raw_Result
     with Global => null, Pre => Data'Length = HC.Raw_Result'Size / System.Storage_Unit;
   function Load (Data : Q.Byte_Array) return CX.Raw_Result
     with Global => null, Pre => Data'Length = CX.Raw_Result'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : D.Raw_Packet) return Boolean
     with Global => null, Pre => Data'Length = D.Raw_Packet'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Packet) return Boolean
     with Global => null, Pre => Data'Length = N.Raw_Packet'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_State) return Boolean
     with Global => null, Pre => Data'Length = N.Raw_State'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Context) return Boolean
     with Global => null, Pre => Data'Length = W.Raw_Context'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Id) return Boolean
     with Global => null, Pre => Data'Length = W.Raw_Id'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Epoch) return Boolean
     with Global => null, Pre => Data'Length = W.Raw_Epoch'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Quantity) return Boolean
     with Global => null, Pre => Data'Length = W.Raw_Quantity'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Current_Observation) return Boolean
     with Global => null, Pre => Data'Length = N.Raw_Current_Observation'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Intent) return Boolean
     with Global => null, Pre => Data'Length = N.Raw_Intent'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Request) return Boolean
     with Global => null, Pre => Data'Length = W.Raw_Request'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Binding) return Boolean
     with Global => null, Pre => Data'Length = W.Raw_Binding'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Row) return Boolean
     with Global => null, Pre => Data'Length = W.Raw_Row'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : D.Raw_Observation) return Boolean
     with Global => null, Pre => Data'Length = D.Raw_Observation'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : X.Raw_Crosswalk) return Boolean
     with Global => null, Pre => Data'Length = X.Raw_Crosswalk'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : C.Raw_Digest) return Boolean
     with Global => null, Pre => Data'Length = C.Raw_Digest'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : C.Raw_Hash) return Boolean
     with Global => null, Pre => Data'Length = C.Raw_Hash'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Input) return Boolean
     with Global => null, Pre => Data'Length = Y.Raw_Input'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Controller) return Boolean
     with Global => null, Pre => Data'Length = Y.Raw_Controller'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Process) return Boolean
     with Global => null, Pre => Data'Length = Y.Raw_Process'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Task) return Boolean
     with Global => null, Pre => Data'Length = Y.Raw_Task'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : Y.Raw_Namespace) return Boolean
     with Global => null, Pre => Data'Length = Y.Raw_Namespace'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Input) return Boolean
     with Global => null, Pre => Data'Length = T.Raw_Input'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Binding) return Boolean
     with Global => null, Pre => Data'Length = T.Raw_Binding'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Ids) return Boolean
     with Global => null, Pre => Data'Length = T.Raw_Ids'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_UID) return Boolean
     with Global => null, Pre => Data'Length = T.Raw_UID'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Quantity) return Boolean
     with Global => null, Pre => Data'Length = T.Raw_Quantity'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Evidence) return Boolean
     with Global => null, Pre => Data'Length = T.Raw_Evidence'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Request) return Boolean
     with Global => null, Pre => (Data'Length = RW.Raw_Request'Size / System.Storage_Unit
       or else Data'Length = RW.Raw_Request'Object_Size / System.Storage_Unit);
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Binding) return Boolean
     with Global => null, Pre => Data'Length = RW.Raw_Binding'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Digest) return Boolean
     with Global => null, Pre => Data'Length = RW.Raw_Digest'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Hash) return Boolean
     with Global => null, Pre => Data'Length = RW.Raw_Hash'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Epoch) return Boolean
     with Global => null, Pre => Data'Length = RW.Raw_Epoch'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : RW.Raw_Native) return Boolean
     with Global => null, Pre => Data'Length = RW.Raw_Native'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Grant) return Boolean
     with Global => null, Pre => Data'Length = T.Raw_Grant'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Rights) return Boolean
     with Global => null, Pre => Data'Length = T.Raw_Rights'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Use) return Boolean
     with Global => null, Pre => (Data'Length = T.Raw_Use'Size / System.Storage_Unit
       or else Data'Length = T.Raw_Use'Object_Size / System.Storage_Unit);
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : C.Raw_Row) return Boolean
     with Global => null, Pre => Data'Length = C.Raw_Row'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : D.Raw_Capability) return Boolean
     with Global => null, Pre => Data'Length = D.Raw_Capability'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Scope_Frame) return Boolean
     with Global => null, Pre => Data'Length = N.Raw_Scope_Frame'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Projection) return Boolean
     with Global => null, Pre => Data'Length = N.Raw_Projection'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Physical_Key) return Boolean
     with Global => null, Pre => Data'Length = N.Raw_Physical_Key'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : N.Raw_Bucket) return Boolean
     with Global => null, Pre => Data'Length = N.Raw_Bucket'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Native) return Boolean
     with Global => null, Pre => (Data'Length = W.Raw_Native'Size / System.Storage_Unit
       or else Data'Length = W.Raw_Native'Object_Size / System.Storage_Unit);
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : O.Raw_Facts) return Boolean
     with Global => null, Pre => (Data'Length = O.Raw_Facts'Size / System.Storage_Unit
       or else Data'Length = O.Raw_Facts'Object_Size / System.Storage_Unit);
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_Result) return Boolean
     with Global => null, Pre => Data'Length = W.Raw_Result'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : T.Raw_Result) return Boolean
     with Global => null, Pre => Data'Length = T.Raw_Result'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : HC.Raw_Input) return Boolean
     with Global => null, Pre => Data'Length = HC.Raw_Input'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CX.Raw_Input) return Boolean
     with Global => null, Pre => (Data'Length = CX.Raw_Input'Size / System.Storage_Unit
       or else Data'Length = CX.Raw_Input'Object_Size / System.Storage_Unit);
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CO.Raw_Input) return Boolean
     with Global => null, Pre => (Data'Length = CO.Raw_Input'Size / System.Storage_Unit
       or else Data'Length = CO.Raw_Input'Object_Size / System.Storage_Unit);
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : W.Raw_State) return Boolean
     with Global => null, Pre => Data'Length = W.Raw_State'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Request) return Boolean
     with Global => null, Pre => Data'Length = CW.Raw_Request'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Optional_Hash) return Boolean
     with Global => null, Pre => Data'Length = CW.Raw_Optional_Hash'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Bytes_32) return Boolean
     with Global => null, Pre => Data'Length = CW.Raw_Bytes_32'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Optional_Counter) return Boolean
     with Global => null, Pre => Data'Length = CW.Raw_Optional_Counter'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CW.Raw_Bytes_8) return Boolean
     with Global => null, Pre => Data'Length = CW.Raw_Bytes_8'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CX.Raw_Material) return Boolean
     with Global => null, Pre => (Data'Length = CX.Raw_Material'Size / System.Storage_Unit
       or else Data'Length = CX.Raw_Material'Object_Size / System.Storage_Unit);
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : HC.Raw_Result) return Boolean
     with Global => null, Pre => Data'Length = HC.Raw_Result'Size / System.Storage_Unit;
   function Source_Padding_Valid (Data : Q.Byte_Array; Raw : CX.Raw_Result) return Boolean
     with Global => null, Pre => Data'Length = CX.Raw_Result'Size / System.Storage_Unit;
end Worldline.Retained_Raw_Decode;

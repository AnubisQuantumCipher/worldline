with Worldline.Scoped_Archive;
with Worldline.Owner_Transitions;
with Worldline.Owner_Retry_Audit;
with Worldline.Owner_Conjunction;
with Evaluation_History;
with Worldline.Collapse_Wire;

--  Full original OwnerCollapseData replay. No producer/custody assertion is
--  conferred by this pure relation. All consulted material is reclassified.
package Worldline.Recovery_Owner_Replay with SPARK_Mode is
   package E renames Worldline.Scoped_Archive.E;
   package K renames Worldline.Owner_Transitions;
   package R renames Worldline.Owner_Retry_Audit;
   package C renames Worldline.Owner_Conjunction;
   package H renames Evaluation_History;
   package CW renames Worldline.Collapse_Wire;
   use type E.Count;
   type Status is
     (Malformed, Material_Refused, Input_Invalid, Before_Not_Authorized,
      Prefix_Changed, After_Invalid, Attempt_Not_Completed_Pass, Use_Not_Consumed,
      Current_Binding_Changed, Original_Collapse_Denied,
      Resulting_Requirement_Absent, Requirement_Changed, Owner_Scope_Mismatch,
      Owner_Not_Authorized, Retry_Not_Admitted, Ready);
   function Matches
     (Data : E.Bytes; Owner, Values, Subject, Primary, Prepared : E.Span;
      Facts_Data : E.Bytes; Capsules : E.Span)
      return Boolean with Global => null;
   --  Derived is the top-level native material result, never carried roster
   --  bytes. All other 35-field operands must match the original DTO exactly.
   function Decide
     (Data : E.Bytes; Owner, Values : E.Span; Derived : CW.Raw_Request;
      Facts_Data : E.Bytes; Capsules : E.Span)
      return Status with Global => null;

   --  Shared owner DTO projection for original recovery and operation archives.
   --  The arena has the original byte indices. A scalar's decoded bytes occupy
   --  its original encoded subtree's First; no caller classification is read.
   procedure Decode_Request
     (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out K.Request;
      At_Layer : E.Layer := E.Recovery)
     with Global => null,
       Pre => Arena'First = Data'First and then Arena'Last >= Data'Last,
       Post => (if not Valid'Old then not Valid);
   procedure Decode_Receipt
     (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out R.Use_Receipt;
      At_Layer : E.Layer := E.Recovery)
     with Global => null,
       Pre => Arena'First = Data'First and then Arena'Last >= Data'Last,
       Post => (if not Valid'Old then not Valid);
   procedure Decode_Identity
     (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out K.Optional_Identity;
      At_Layer : E.Layer := E.Recovery)
     with Global => null,
       Pre => Arena'First = Data'First and then Arena'Last >= Data'Last,
       Post => (if not Valid'Old then not Valid);
   procedure Decode_Epoch
     (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out H.Optional_Epoch;
      At_Layer : E.Layer := E.Recovery)
     with Global => null,
       Pre => Arena'First = Data'First and then Arena'Last >= Data'Last,
       Post => (if not Valid'Old then not Valid);
   procedure Decode_Cursor
     (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out H.Optional_Cursor;
      At_Layer : E.Layer := E.Recovery)
     with Global => null,
       Pre => Arena'First = Data'First and then Arena'Last >= Data'Last,
       Post => (if not Valid'Old then not Valid);
   procedure Decode_Scope
     (Data : E.Bytes; Item : E.Span; Arena : in out E.Bytes;
      Valid : in out Boolean; Value : out C.Full_Scope;
      At_Layer : E.Layer := E.Recovery)
     with Global => null,
       Pre => Arena'First = Data'First and then Arena'Last >= Data'Last,
       Post => (if not Valid'Old then not Valid);
   procedure Decode_Hash
     (Data : E.Bytes; Item : E.Span; Valid : in out Boolean;
      Value : out CW.Raw_Optional_Hash; At_Layer : E.Layer := E.Recovery)
     with Global => null, Post => (if not Valid'Old then not Valid);
end Worldline.Recovery_Owner_Replay;

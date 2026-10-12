with Canonical_Artifacts;
with Worldline.Archive_Base64;
with Worldline.Archive_Text;

--  Exact local views through the ACTUAL preserved encoders:
--  operation_capture.archive -> finalization_journal.encode -> value_bytes.
--  Local decoding is not whole-tree/schema validity, JSON equality or X4 Ready.
--  No caller authorization/equality flag and no numerical/tree-depth cap.
package Worldline.Archive_Envelope with SPARK_Mode is
   package C renames Canonical_Artifacts;
   package Q renames Archive_Base64.Q;
   subtype Bytes is Q.Byte_Array;
   subtype Span is C.Span;
   subtype Count is Q.Byte_Count;
   use type Count;
   use type Span;

   --  This bound is the fixed codec composition, not an input nesting limit.
   type Encoding_Level is range 0 .. 2;
   type Byte_View is record
      Encoded : Span := (1, 0);
      Level : Encoding_Level := 0;
   end record;
   --  Materialize is total: an invalid span or a non-canonical lower level
   --  yields the empty leaf, so no caller precondition recurses back into
   --  Bytes_Valid (GNATprove cannot discharge a variant through a mutually
   --  recursive precondition). For a valid view it returns exactly the bytes
   --  it always did, with a lower bound in the index subtype, so spans
   --  (First, Length) over the result are well formed.
   function Materialize (Data : Bytes; Item : Byte_View) return Bytes
     with Global => null,
       Subprogram_Variant => (Decreases => Item.Level),
       Post => Materialize'Result'First >= 1 and then
         Materialize'Result'Length <= Item.Encoded.Length;
   function Leaf_Canonical (Raw : Bytes) return Boolean is
     (Raw'First >= 1 and then
      Worldline.Archive_Base64.Canonical (Raw, (Raw'First, Raw'Length)))
     with Global => null;
   --  Bytes_Valid is defined by its postcondition: level 0 is a valid span of
   --  the arena; each further level is a valid lower level whose
   --  materialization is canonical base64. Callers that check it may rely on
   --  exactly that meaning; nothing about the encoding was changed.
   function Bytes_Valid (Data : Bytes; Item : Byte_View) return Boolean
     with Global => null, Subprogram_Variant => (Decreases => Item.Level),
       Post => Bytes_Valid'Result =
         (if Item.Level = 0 then C.P.Valid (Data, Item.Encoded)
          else Bytes_Valid (Data, (Item.Encoded, Item.Level - 1)) and then
            Leaf_Canonical (Materialize (Data, (Item.Encoded, Item.Level - 1))));

   type Layer is (Terminal, Finalization, Operation, Recovery, Finalization_Record);
   type Value_Kind is
     (Invalid, Null_Value, Boolean_Value, Integer_Value, Float_Value,
      Text_Value, Bytes_Value, List_Value, Tuple_Value, Object_Value,
      Record_Value, World_State_Value);
   type View is record
      Form : Value_Kind := Invalid;
      Raw : Span := (1, 0);
      At_Layer : Layer := Terminal;
      Payload : Byte_View;
      Sign, Boolean_Bit : Boolean := False;
      Children : Span := (1, 0);
      Module_Name, Record_Name : Byte_View;
   end record;

   --  Child lists are spans into the unchanged ORIGINAL bytes. Array_Element
   --  returns a raw subtree, never a reconstructed encoding. Ordinal is zero
   --  based and carries no numeric-value or roster limit.
   --  An element is a strict sub-span of its sequence (the brackets are not
   --  part of any element); a missing element is the empty span. Together with
   --  Decode's child bound below this is what lets structural recursion over a
   --  value (Equal and the other walkers) carry Decreases => Span.Length.
   function Array_Element (Data : Bytes; Sequence : Span; Ordinal : Count)
      return Span with Global => null,
      Post => Array_Element'Result.Length = 0 or else
        Array_Element'Result.Length < Sequence.Length;
   function Array_Length (Data : Bytes; Sequence : Span) return Count
      with Global => null,
        Post => Array_Length'Result <= Sequence.Length and then
          (if Array_Length'Result > 0 then Sequence.Length >= 2);
   function Is_Array (Data : Bytes; Item : Span) return Boolean
      with Global => null;
   function Decode (Data : Bytes; Encoded : Span; At_Layer : Layer)
      return View
     with Global => null,
       Subprogram_Variant => (Decreases => Layer'Pos (At_Layer)),
       Post => Decode'Result.Raw = Encoded and then
         Decode'Result.At_Layer = At_Layer and then
         Decode'Result.Children.Length <= Encoded.Length;
   function Text_Is (Data : Bytes; Item : View; Text : String) return Boolean
     with Global => null;
end Worldline.Archive_Envelope;

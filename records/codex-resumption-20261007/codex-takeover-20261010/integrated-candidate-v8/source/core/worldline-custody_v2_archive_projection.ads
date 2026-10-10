with Worldline.Scoped_Archive;
package Worldline.Custody_V2_Archive_Projection with SPARK_Mode is
   package S renames Worldline.Scoped_Archive;
   package E renames S.E;
   use type E.Count;
   function Borrow_Valid (Data : E.Bytes; Item : E.Byte_View) return Boolean
      with Global => null,
        Subprogram_Variant => (Decreases => Item.Level),
        Post => (if Borrow_Valid'Result then E.C.P.Valid (Data, Item.Encoded));
   function Byte_Length (Data : E.Bytes; Item : E.Byte_View) return E.Count
      with Global => null,
        Subprogram_Variant => (Decreases => Item.Level),
        Post => Byte_Length'Result <= Item.Encoded.Length;
   function Byte_At (Data : E.Bytes; Item : E.Byte_View; Offset : E.Count) return E.Q.Byte
      with Global => null,
        Subprogram_Variant => (Decreases => Item.Level);
   -- Complete immutable decoded byte equality, streamed through fixed codec
   -- tiers without materializing or concatenating either underlying payload.
   function Bytes_Equal (Left_Data, Right_Data : E.Bytes; Left, Right : E.Byte_View)
      return Boolean with Global => null,
        Post => (if Bytes_Equal'Result then
          E.C.P.Valid (Left_Data, Left.Encoded) and then
          E.C.P.Valid (Right_Data, Right.Encoded));
   -- Borrowed complete typed correspondence, not JSON or value coercion.
   -- Standard S.record leaves retain exact integer sign/magnitude, float bits,
   -- bytes, text, list/tuple shape, record field order and native record names.
   -- Original record() cannot represent byte keys, WorldState or every original
   -- record. Original_Image compares S.record(original archive bytes) with the
   -- complete validated operation image, preserving ALL original typed values.
   -- Relay_Frame is the native position profile: only the top-level payload
   -- member is such an original image; all metadata is standard scoped data.
   -- Profiles are selected by compiled consumers at declared capture positions,
   -- never interpreted from a user dictionary or a producer allowed flag.
   -- Every user dictionary, including encoding/raw keys, remains a dictionary.
   -- No original nesting, integer, float-bits or byte extent limit is added.
   type Projection_Profile is (Scoped_Tree, Original_Image, Relay_Frame);
   function Scoped_Archive_Operation_Matches
     (Scoped_Data, Operation_Data : E.Bytes;
      Scoped_Value, Operation_Value : E.Span;
      Profile : Projection_Profile := Scoped_Tree) return Boolean
     with Global => null,
       Subprogram_Variant => (Decreases => Scoped_Value.Length),
       Post => (if Scoped_Archive_Operation_Matches'Result then
         E.C.P.Valid (Scoped_Data, Scoped_Value) and then
         E.C.P.Valid (Operation_Data, Operation_Value));
end Worldline.Custody_V2_Archive_Projection;

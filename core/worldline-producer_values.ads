--  Original JSON values, including unbounded integer and finite-float tokens.
--  This parser supplies syntax and selectors, never acquisition authority.
package Worldline.Producer_Values with SPARK_Mode is
   type Value_Kind is (Missing, Null_Value, Boolean_Value, Integer_Value,
                      Number_Value, String_Value, Array_Value, Object_Value);
   type Node is record
      Form : Value_Kind := Missing;
      First, Last : Natural := 0;
   end record;
   No_Node : constant Node := (Missing, 0, 0);
   function Parse (Data : String) return Node with Global => null;
   function Member_Key (Data : String; Parent : Node; Index : Positive)
      return Node with Global => null;
   -- The same whole grammar has distinct admission predicates. Ordinary
   -- Parse/Field/Count retain json.loads last-key-wins semantics.
   function Standard_JSON (Data : String) return Boolean with Global => null;
   function Duplicate_Free (Data : String) return Boolean with Global => null;
   function Original_Exact_JSON (Data : String) return Boolean is
     (Standard_JSON (Data) and then Duplicate_Free (Data)) with Global => null;
   -- Canonical surrogatepass UTF8 unit width; no Unicode normalization.
   function UTF8_Width (Data : String; Offset : Natural) return Natural
     with Global => null,
       Post => UTF8_Width'Result <= 4 and then
         (if UTF8_Width'Result > 0 then
            Offset < Data'Length and then UTF8_Width'Result <= Data'Length - Offset);
   -- Original str(json.loads numeric value), including signed zero,
   -- nearest-even binary64 and Python nan/inf spellings.
   function Number_Image (Data : String; Item : Node) return String
     with Global => null;
   function Field (Data : String; Parent : Node; Name : String) return Node
     with Global => null,
       Post => (if Field'Result.Form /= Missing then
           Parent.Form = Object_Value and then Parent.First > 0 and then
           Parent.First < Parent.Last and then Parent.Last <= Data'Length and then
           Field'Result.First > Parent.First and then Field'Result.First <= Data'Length);
   function Element (Data : String; Parent : Node; Index : Positive) return Node
     with Global => null,
       Post => (if Element'Result.Form /= Missing then Parent.First > 0 and then
                  Element'Result.First > Parent.First and then Element'Result.First <= Data'Length);
   --  Position is a zero-based offset in the original source, initially
   --  Parent.First. Each call advances past one physical child/member.
   --  Missing means the closing delimiter was reached; inconsistent spans
   --  or syntax raise Program_Error rather than appearing to end early.
   procedure Next_Child
     (Data : String; Parent : Node; Position : in out Natural;
      Key, Item : out Node)
     with Global => null, Always_Terminates,
       Pre => Parent.Form in Array_Value | Object_Value and then
         Parent.First > 0 and then Parent.First < Parent.Last and then
         Parent.Last <= Data'Length and then
         Position in Parent.First .. Parent.Last - 1,
       Post => Position in Position'Old .. Parent.Last - 1 and then
         (if Item.Form = Missing then
             Position = Parent.Last - 1 and then Key.Form = Missing
          else
             Position > Position'Old and then Item.First > Parent.First and then
             Item.First > Position'Old and then Item.First <= Item.Last and then
             Item.Last < Parent.Last and then
             (if Parent.Form = Object_Value then
                 Key.Form = String_Value and then Key.First > Parent.First and then
                 Key.First < Key.Last and then Key.Last < Item.First
              else Key.Form = Missing));
   type Member_Entry is record
      Key, Item : Node := No_Node;
   end record;
   type Member_Array is array (Positive range <>) of Member_Entry;
   type Member_Index (Capacity : Natural) is limited record
      Length : Natural := 0;
      Entries : Member_Array (1 .. Capacity);
   end record;
   --  Exact physical-member capacity, constructed in place. The used prefix
   --  retains first decoded-key occurrence order and each key's last value.
   --  Sorting compares decoded bytes without allocating decoded key strings.
   --  Non-object/invalid spans, including malformed suffixes after valid
   --  members, have zero capacity and length; no validity precondition is imposed.
   function Members (Data : String; Parent : Node) return Member_Index
     with Global => null,
       Post => Members'Result.Length <= Members'Result.Capacity and then
         Members'Result.Capacity <= Data'Length and then
         (if Parent.Form /= Object_Value or else Parent.First = 0 or else
             Parent.First >= Parent.Last or else Parent.Last > Data'Length
          then Members'Result.Capacity = 0 and then Members'Result.Length = 0) and then
         (for all I in 1 .. Members'Result.Length =>
            Members'Result.Entries (I).Key.Form = String_Value and then
            Members'Result.Entries (I).Key.First > Parent.First and then
            Members'Result.Entries (I).Key.First <
              Members'Result.Entries (I).Key.Last and then
            Members'Result.Entries (I).Key.Last <
              Members'Result.Entries (I).Item.First and then
            Members'Result.Entries (I).Item.Form /= Missing and then
            Members'Result.Entries (I).Item.First <=
              Members'Result.Entries (I).Item.Last and then
            Members'Result.Entries (I).Item.Last < Parent.Last);
   function Count (Data : String; Parent : Node) return Natural
     with Global => null,
       Post => (if Count'Result > 0 then Parent.First in 1 .. Data'Length)
         and then Count'Result <= Data'Length
         and then Count'Result < Natural'Last;
   --  A bounded fragment of Text's decoder, for direct count/write consumers.
   --  Position starts at the string node's First and Last is that node's Last.
   --  Valid=False retains Text's malformed-decode signal, not a new fallback.
   type Decoded_Unit is record
      Bytes : String (1 .. 4) := (others => Character'Val (0));
      Length : Natural range 0 .. 4 := 0;
      Valid : Boolean := False;
   end record;
   procedure Decode_Unit
     (Data : String; Last : Positive; Position : in out Natural;
      Unit : out Decoded_Unit)
     with Global => null, Always_Terminates,
       Pre => Last <= Data'Length and then Position < Last - 1,
       Post => Position in Position'Old .. Last and then
         (if Unit.Valid then Unit.Length > 0 and then
             Unit.Length <= Position - Position'Old);
   function Text (Data : String; Item : Node) return String with Global => null;
   function Is_Text (Data : String; Item : Node; Expected : String) return Boolean
     with Global => null,
       Post => (if Is_Text'Result then Item.Form = String_Value);
   function Is_True (Data : String; Item : Node) return Boolean with Global => null;
   function Is_False (Data : String; Item : Node) return Boolean with Global => null;
   function Is_Null (Item : Node) return Boolean is (Item.Form = Null_Value)
     with Global => null;
   function Present (Item : Node) return Boolean is (Item.Form /= Missing)
     with Global => null;
   function Nonempty_Text (Data : String; Item : Node) return Boolean
     with Global => null;
   function Equal (Left : String; L : Node; Right : String; R : Node) return Boolean
     with Global => null,
       Subprogram_Variant => (Decreases =>
         (if L.Form = Missing then 0
          else Long_Long_Integer (Left'Length) + 1 - Long_Long_Integer (Natural'Min (L.First, Left'Length))));
   function Truth (Data : String; Item : Node) return Boolean with Global => null;
   function Decimal (Data : String; Item : Node) return String with Global => null;
   function Nonnegative (Data : String; Item : Node) return Boolean
     with Global => null;
   function Slice (Data : String; Item : Node) return String
     with Global => null,
       Post => Slice'Result'Length <= Data'Length and then
         (if Item.Form /= Missing and then Item.First > 0 and then
             Item.First <= Item.Last and then Item.Last <= Data'Length
          then Slice'Result'Length = Item.Last - Item.First + 1
          else Slice'Result'Length = 0);
   function Member_Name (Data : String; Parent : Node; Index : Positive)
      return String with Global => null;
   function Field (Data, Name : String) return String with Global => null;
   function Element (Data : String; Index : Natural) return String with Global => null;
   function Text (Data : String) return String with Global => null;
   function Kind (Data : String) return Value_Kind with Global => null;
   function Count (Data : String) return Natural
     with Global => null,
       Post => Count'Result <= Data'Length and then
         Count'Result < Natural'Last;
   function Truth (Data : String) return Boolean with Global => null;
   function Equal (Left, Right : String) return Boolean with Global => null;
   function Quote (Text : String) return String with Global => null;
   function Python_String (Value : String) return String with Global => null;
end Worldline.Producer_Values;

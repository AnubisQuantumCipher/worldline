with Worldline.Resources;

package Resource_Reservation_Lifecycle with SPARK_Mode is
   subtype Byte_Array is Worldline.Resources.Byte_Array;
   subtype Byte_Count is Worldline.Resources.Byte_Count;
   subtype Byte_Index is Worldline.Resources.Byte_Index;
   use type Worldline.Resources.Byte;

   type Identity_Span is record
      First : Byte_Index;
      Length : Byte_Count;
   end record;
   type Optional_Identity (Present : Boolean := False) is record
      case Present is
         when False => null;
         when True => Value : Identity_Span;
      end case;
   end record;
   type Liveness is (Unknown, Live, Gone);
   type Reservation_Entry is record
      Identity : Identity_Span;
      Observed : Liveness;
   end record;
   type Entry_Array is array (Byte_Index range <>) of Reservation_Entry;
   type Removal_Array is array (Byte_Index range <>) of Boolean;
   type Operation is (Unknown_Operation, Release_Exact, Reconcile_Observed);
   type Result_Status is
     (Invalid_Input, Invalid_Output_Layout, No_Change, Removal_Planned);

   function Span_Valid (Data : Byte_Array; Id : Identity_Span) return Boolean is
     (Id.Length = 0 or else
        (Id.First in Data'Range and then
         Id.Length - 1 <= Data'Last - Id.First))
   with Global => null;

   --  Exact bytes, including every zero byte. Empty identities compare equal;
   --  their unused First carries no semantic payload. No digest substitute.
   function Same_Identity
     (Data : Byte_Array; Left, Right : Identity_Span) return Boolean is
     (Span_Valid (Data, Left) and then Span_Valid (Data, Right) and then
      Left.Length = Right.Length and then
      (Left.Length = 0 or else
       (for all Offset in Byte_Count range 0 .. Left.Length - 1 =>
          Data (Left.First + Offset) = Data (Right.First + Offset))))
   with Global => null;

   function Inputs_Valid
     (Data : Byte_Array; Rows : Entry_Array;
      Requested : Optional_Identity; Mode : Operation) return Boolean is
     (Mode /= Unknown_Operation and then
      (if Mode = Release_Exact then Requested.Present and then
         Span_Valid (Data, Requested.Value)) and then
      (for all I in Rows'Range => Span_Valid (Data, Rows (I).Identity)) and then
      (for all I in Rows'Range =>
         (for all J in Rows'Range =>
            (if I < J then not Same_Identity
               (Data, Rows (I).Identity, Rows (J).Identity)))))
   with Global => null;

   function Remove_Row
     (Data : Byte_Array; Row : Reservation_Entry;
      Requested : Optional_Identity; Mode : Operation) return Boolean is
     (case Mode is
         when Unknown_Operation => False,
         when Release_Exact => Requested.Present and then
           Same_Identity (Data, Row.Identity, Requested.Value),
         when Reconcile_Observed => Row.Observed = Gone)
   with Global => null;

   function Any_Removal
     (Data : Byte_Array; Rows : Entry_Array;
      Requested : Optional_Identity; Mode : Operation) return Boolean is
     (for some I in Rows'Range =>
        Remove_Row (Data, Rows (I), Requested, Mode))
   with Global => null;

   function Plan_Conforms
     (Data : Byte_Array; Rows : Entry_Array;
      Requested : Optional_Identity; Mode : Operation;
      Before, After : Removal_Array; Status : Result_Status) return Boolean is
     (Before'First = After'First and then Before'Length = After'Length and then
      (if not Inputs_Valid (Data, Rows, Requested, Mode) then
          Status = Invalid_Input and then After = Before
       elsif After'Length /= Rows'Length then
          Status = Invalid_Output_Layout and then After = Before
       else
          Status = (if Any_Removal (Data, Rows, Requested, Mode)
                    then Removal_Planned else No_Change) and then
          (for all I in Rows'Range =>
             After (After'First + (I - Rows'First)) =
               Remove_Row (Data, Rows (I), Requested, Mode))))
   with Ghost, Global => null;

   --  Complete plan, no state mutation or side effect. Invalid inputs/layout
   --  preserve the entire caller-owned output; callers must inspect Status.
   --  The caller projects original records in their original order using this
   --  mask. Epoch/CAS, authenticated observations and effect custody are open.
   procedure Plan
     (Data : Byte_Array; Rows : Entry_Array;
      Requested : Optional_Identity; Mode : Operation;
      Removed : in out Removal_Array; Status : out Result_Status)
   with Global => null, Always_Terminates,
     Post => Plan_Conforms
       (Data, Rows, Requested, Mode, Removed'Old, Removed, Status);
end Resource_Reservation_Lifecycle;

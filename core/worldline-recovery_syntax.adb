with Worldline.Operation_Archive;
with Worldline.Producer_Values;
package body Worldline.Recovery_Syntax with SPARK_Mode is
   package O renames Worldline.Operation_Archive;
   package V renames Worldline.Producer_Values;
   use type E.Value_Kind;
   use type E.Count;
   function Field (Data : E.Bytes; Item : E.Span; Name : String) return E.Span is
     (O.Field (Data, Item, Name));
   function Byte_Field (Data : E.Bytes; Item : E.Span; Name : String) return Boolean is
      Value : constant E.View := E.Decode (Data, Field (Data, Item, Name), E.Operation);
   begin
      return Value.Form = E.Bytes_Value and then E.Bytes_Valid (Data, Value.Payload);
   end Byte_Field;
   function Operand_Text (Facts_Data : E.Bytes; Operand : E.Span) return String is
      Value : constant E.View := E.Decode (Facts_Data, Operand, E.Operation);
   begin
      if Value.Form /= E.Bytes_Value or else not E.Bytes_Valid (Facts_Data, Value.Payload) then
         return "";
      end if;
      declare
         Raw : constant E.Bytes := E.Materialize (Facts_Data, Value.Payload);
      begin
         if Raw'Length = 0 then return ""; end if;
         if Raw'Length > E.Count (Natural'Last) then
            raise Constraint_Error with "recovery operand exceeds String capacity";
         end if;
         return Result : String (1 .. Natural (Raw'Length))
           with Relaxed_Initialization
         do
            for I in Result'Range loop
               Result (I) := Character'Val (Raw (Raw'First + E.Count (I - 1)));
               pragma Loop_Invariant (Raw'First + E.Count (I - 1) in Raw'Range);
               pragma Loop_Invariant (Result (Result'First .. I)'Initialized);
            end loop;
            pragma Assert (Result'Initialized);
         end return;
      end;
   end Operand_Text;
   function Item_Valid (Data : E.Bytes; Item : E.Span) return Boolean is
      Value : constant E.View := E.Decode (Data, Item, E.Operation);
   begin
      return Value.Form = E.Object_Value and then E.Array_Length (Data, Value.Children) = 3
        and then Byte_Field (Data, Item, "result")
        and then Byte_Field (Data, Item, "declaration")
        and then Byte_Field (Data, Item, "capsule");
   end Item_Valid;
   function Valid (Facts_Data : E.Bytes; Capsules : E.Span) return Boolean is
      List : constant E.View := E.Decode (Facts_Data, Capsules, E.Operation);
      N : constant E.Count := E.Array_Length (Facts_Data, List.Children);
   begin
      if not O.Valid (Facts_Data, Capsules) or else List.Form /= E.List_Value then return False; end if;
      if N > 0 then
         for I in E.Count range 0 .. N - 1 loop
            if not Item_Valid (Facts_Data, E.Array_Element (Facts_Data, List.Children, I)) then
               return False;
            end if;
         end loop;
      end if;
      -- ERROR/null-audit observations remain exact transport; only their native
      -- consuming original row redecides source and parser authenticity.
      return True;
   end Valid;
   function Find
     (Original_Result : String; Facts_Data : E.Bytes; Capsules : E.Span)
      return Capsule_Operands
   is
      List : constant E.View := E.Decode (Facts_Data, Capsules, E.Operation);
      N : constant E.Count := E.Array_Length (Facts_Data, List.Children);
   begin
      if not Valid (Facts_Data, Capsules) or else N = 0 then return (others => <>); end if;
      for I in E.Count range 0 .. N - 1 loop
         declare
            Item : constant E.Span := E.Array_Element (Facts_Data, List.Children, I);
            Result_JSON : constant String := Operand_Text (Facts_Data, Field (Facts_Data, Item, "result"));
         begin
            if V.Equal (Original_Result, Result_JSON) then
               return (Present => True,
                       Declaration => Field (Facts_Data, Item, "declaration"),
                       Capture => Field (Facts_Data, Item, "capsule"));
            end if;
         end;
      end loop;
      return (others => <>);
   end Find;
end Worldline.Recovery_Syntax;

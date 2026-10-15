package body Worldline.Raw_JSON_Syntax with SPARK_Mode is
   use type C.Step_Status;
   use type C.Code_Point;

   function Source_Length (Data : Q.Byte_Array; Context : C.Cursor) return JS.Count is
      pragma Unreferenced (Data);
   begin
      return Context.Item.Length;
   end Source_Length;

   function Read_Unit
     (Data : Q.Byte_Array; Context : C.Cursor; Position : JS.Count)
      return JS.Reader_Unit
   is
      Unit : constant C.Step := C.Read
        (Data, (Item => Context.Item, Kind => Context.Kind, Offset => Position));
   begin
      case Unit.Status is
         when C.Decoded =>
            if Unit.Value < 128 then
               return (JS.ASCII_Unit, Unit.Next_Offset,
                       Character'Val (Natural (Unit.Value)));
            else
               return (JS.Non_ASCII_Unit, Unit.Next_Offset);
            end if;
         when C.End_Of_Text => return (JS.End_Of_Source, Position);
         when C.Invalid_Position | C.Invalid_Sequence =>
            return (JS.Invalid_Unit, Position);
      end case;
   end Read_Unit;

   function Parse (Data : Q.Byte_Array; Item : C.Span) return JS.Node is
      Context : constant C.Cursor := C.Initial (Data, Item);
   begin
      return Grammar.Parse (Data, Context, Context.Offset);
   end Parse;
end Worldline.Raw_JSON_Syntax;

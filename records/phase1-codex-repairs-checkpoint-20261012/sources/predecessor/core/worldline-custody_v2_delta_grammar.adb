package body Worldline.Custody_V2_Delta_Grammar with SPARK_Mode is
   use type E.Value_Kind;
   use type E.Layer;
   use type E.Q.Byte;
   function Child_Of (Parent, Child : E.Span) return Boolean is
     (Child.Length < Parent.Length and then Child.First >= Parent.First and then
      Child.First - Parent.First <= Parent.Length and then
      Child.Length <= Parent.Length - (Child.First - Parent.First));
   function Bound (Data : E.Bytes; Item : E.Span; Layer : E.Layer := E.Operation)
      return Bound_Result
   is
      View : constant E.View := E.Decode (Data, Item, Layer);
      Needed : E.Count := 0;
      Good : Boolean := True;
      procedure Add (Amount : E.Count) with Ghost, Always_Terminates is
      begin
         -- This uses actual occupied geometry, never a quantity/depth cap.
         if Needed > Item.Length or else Amount > Item.Length - Needed then
            Good := False;
         else Needed := Needed + Amount; end if;
      end Add;
      procedure Add_Child (Child : E.Span; At_Layer : E.Layer)
        with Ghost, Always_Terminates,
          Subprogram_Variant => (Decreases => Item.Length, Decreases => 1)
      is
         Result : Bound_Result;
      begin
         if not Good or else not Child_Of (Item, Child) then Good := False; return; end if;
         Result := Bound (Data, Child, At_Layer);
         if not Result.Valid then Good := False; return; end if;
         Add (Result.JSON_Length);
      end Add_Child;
   begin
      if not E.C.P.Valid (Data, Item) then return (False, 0); end if;
      case View.Form is
         when E.Invalid | E.Bytes_Value | E.Float_Value | E.Record_Value | E.World_State_Value =>
            return (False, 0);
         when E.Null_Value => Add (4);
         when E.Boolean_Value => Add (if View.Boolean_Bit then 4 else 5);
         when E.Integer_Value =>
            if View.Sign or else not A.Borrow_Valid (Data, View.Payload) or else
               A.Byte_Length (Data, View.Payload) > 1 or else
               (A.Byte_Length (Data, View.Payload) = 1 and then
                A.Byte_At (Data, View.Payload, 0) not in 1 .. 4) then return (False, 0); end if;
            Add (1);
         when E.Text_Value =>
            if not A.Borrow_Valid (Data, View.Payload) then return (False, 0); end if;
            declare Count : constant E.Count := A.Byte_Length (Data, View.Payload); begin
               for N in E.Count range 0 .. Count - 1 loop
                  pragma Loop_Variant (Increases => N);
                  declare Byte : constant E.Q.Byte := A.Byte_At (Data, View.Payload, N); begin
                     if Byte not in 32 .. 126 or else Byte = Character'Pos ('"') or else
                       Byte = Character'Pos ('\') then return (False, 0); end if;
                  end;
               end loop;
               -- No JSON quoting escape is needed by actual ASCII/hex leaves.
               -- Base64 decoded extent never exceeds its preserved encoded leaf;
               -- the positive typed header supplies both JSON quotation bytes.
               Add (2); Add (Count);
            end;
         when E.List_Value | E.Tuple_Value | E.Object_Value =>
            Add (2);
            declare Count : constant E.Count := E.Array_Length (Data, View.Children); begin
               for N in E.Count range 0 .. Count - 1 loop
                  pragma Loop_Variant (Increases => N);
                  pragma Loop_Invariant (Needed <= Item.Length);
                  if N > 0 then Add (1); end if;
                  if View.Form = E.Object_Value then
                     declare
                        Pair : constant E.View := E.Decode (Data,
                          E.Array_Element (Data, View.Children, N),
                          (if Layer = E.Terminal then E.Terminal else E.Layer'Pred (Layer)));
                        Key : constant E.Span := E.Array_Element (Data, Pair.Children, 0);
                        Value : constant E.Span := E.Array_Element (Data, Pair.Children, 1);
                     begin
                        if E.Array_Length (Data, Pair.Children) /= 2 or else
                           E.Decode (Data, Key, Layer).Form /= E.Text_Value then return (False, 0); end if;
                        Add_Child (Key, Layer); Add (1); Add_Child (Value, Layer);
                     end;
                  else Add_Child (E.Array_Element (Data, View.Children, N), Layer); end if;
                  if not Good then return (False, 0); end if;
               end loop;
            end;
      end case;
      return (Good, (if Good then Needed else 0));
   end Bound;
end Worldline.Custody_V2_Delta_Grammar;

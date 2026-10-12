with Worldline.Producer_Values;
package body Worldline.Source_Syntax with SPARK_Mode is
   package V renames Worldline.Producer_Values;
   use type V.Value_Kind;
   function Valid (Observation : String) return Boolean is
      Data : String renames Observation;
      Root : constant V.Node := V.Parse (Data);
      function F (Item : V.Node; Name : String) return V.Node is (V.Field (Data, Item, Name));
      function E (Item : V.Node; Index : Positive) return V.Node is (V.Element (Data, Item, Index));
      Nodes : constant V.Node := F (Root, "nodes");
      Scopes : constant V.Node := F (Root, "scopes");
      Node_Count : constant Natural := V.Count (Data, Nodes);
      Scope_Count : constant Natural := V.Count (Data, Scopes);
      function Index_Of (Item : V.Node; Bound : Natural) return Natural is
         Text : constant String := V.Decimal (Data, Item);
         Index : Natural := 0;
      begin
         if Text'Length = 0 then return Bound; end if;
         for C of Text loop
            if C not in '0' .. '9' or else Index > Bound / 10 or else
              (Index = Bound / 10 and then Character'Pos (C) - 48 > Bound mod 10) then return Bound; end if;
            Index := Index * 10 + Character'Pos (C) - 48;
         end loop;
         return Index;
      end Index_Of;
      function Reference (Item : V.Node) return Natural is
        (if Item.Form = V.Object_Value and then V.Count (Data, Item) = 1
         then Index_Of (F (Item, "node"), Node_Count) else Node_Count);
      --  Children of an array/object node start after their parent (Producer_Values
      --  Element/Field Posts); a non-container child ends the recursion.
      function Tree (Item : V.Node; Owner : Natural) return Boolean
        with Subprogram_Variant => (Decreases => (if Item.Form in V.Array_Value | V.Object_Value then 1 else 0),
                                    Increases => Item.First) is
      begin
         if Item.Form = V.Array_Value then
            for I in 1 .. V.Count (Data, Item) loop
               if not Tree (E (Item, I), Owner) then return False; end if;
            end loop;
         elsif Item.Form = V.Object_Value then
            if V.Present (F (Item, "node")) then
               declare Index : constant Natural := Reference (Item);
               begin
                  if Index >= Node_Count then return False; end if;
                  -- ast's shared operator/context singleton nodes may have a
                  -- previous identifier; non-leaf references are preorder.
                  if Index <= Owner and then V.Count (Data, F (E (Nodes, Index + 1), "fields")) /= 0 then return False; end if;
               end;
            else
               for I in 1 .. V.Count (Data, Item) loop
                  if not Tree (F (Item, V.Member_Name (Data, Item, I)), Owner) then return False; end if;
               end loop;
            end if;
         end if;
         return True;
      end Tree;
   begin
      if Root.Form /= V.Object_Value or else F (Root, "exception").Form /= V.Null_Value or else
        Nodes.Form /= V.Array_Value or else Scopes.Form /= V.Array_Value or else
        Node_Count = 0 or else Scope_Count = 0 or else
        not V.Is_Text (Data, F (E (Nodes, 1), "kind"), "Module") then return False; end if;
      for I in 1 .. Node_Count loop
         declare Item : constant V.Node := E (Nodes, I);
         begin
            if Item.Form /= V.Object_Value or else not V.Nonempty_Text (Data, F (Item, "kind")) or else
              F (Item, "fields").Form /= V.Object_Value or else F (Item, "attributes").Form /= V.Object_Value or else
              not Tree (F (Item, "fields"), I - 1) then return False; end if;
         end;
      end loop;
      for I in 1 .. Scope_Count loop
         declare
            Item : constant V.Node := E (Scopes, I);
            Members : constant V.Node := F (Item, "nodes");
            Children : constant V.Node := F (Item, "children");
            Scope_Root : constant Natural := Reference (F (Item, "root"));
         begin
            if Item.Form /= V.Object_Value or else Scope_Root >= Node_Count or else
              Members.Form /= V.Array_Value or else Children.Form /= V.Array_Value or else
              (if I = 1 then F (Item, "parent").Form /= V.Null_Value or else Scope_Root /= 0
               else Index_Of (F (Item, "parent"), Scope_Count) >= I - 1) then return False; end if;
            for J in 1 .. V.Count (Data, Members) loop
               if Reference (E (Members, J)) >= Node_Count then return False; end if;
            end loop;
            for J in 1 .. V.Count (Data, Children) loop
               declare Child : constant Natural := Index_Of (E (Children, J), Scope_Count);
               begin
                  if Child >= Scope_Count or else Child < I or else
                    Index_Of (F (E (Scopes, Child + 1), "parent"), Scope_Count) /= I - 1 then return False; end if;
               end;
            end loop;
         end;
      end loop;
      return True;
   end Valid;
end Worldline.Source_Syntax;

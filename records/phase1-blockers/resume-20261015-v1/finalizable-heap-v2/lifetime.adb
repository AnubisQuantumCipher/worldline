with Ada.Unchecked_Deallocation;
package body Lifetime with SPARK_Mode is
   procedure Free is new Ada.Unchecked_Deallocation (String, Text_Access);
   function Read (Object : Value) return String is
     (if Object.Data = null then "" else Object.Data.all);
   function Make (Text : String) return Value is
     (Value'(Data => new String'(Text)));
   procedure Adjust (Object : in out Value) is
   begin
      if Object.Data /= null then
         Object.Data := new String'(Object.Data.all);
      end if;
   end Adjust;
   procedure Finalize (Object : in out Value) is
   begin
      Free (Object.Data);
   end Finalize;
   procedure Touch (Object : in out Value) is
   begin
      null;
   end Touch;
   procedure Replace_First (Object : in out Value; Ch : Character) is
   begin
      Object.Data (Object.Data'First) := Ch;
   end Replace_First;
end Lifetime;

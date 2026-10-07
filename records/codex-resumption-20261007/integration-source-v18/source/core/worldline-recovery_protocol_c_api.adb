with System.Address_To_Access_Conversions;
with System.Storage_Elements;
with Worldline.Recovery_Protocol_Wire;
with Worldline.Recovery_Protocol_ABI;
package body Worldline.Recovery_Protocol_C_API with SPARK_Mode => On is
   package W renames Worldline.Recovery_Protocol_Wire;
   use System.Storage_Elements;
   use type System.Address;
   use type Interfaces.C.size_t;
   use type Interfaces.C.long;
   use type Interfaces.C.int;
   package Request_Pointers is new System.Address_To_Access_Conversions (W.Raw_Request);
   package Result_Pointers is new System.Address_To_Access_Conversions (W.Raw_Result);
   use type Request_Pointers.Object_Pointer;
   use type Result_Pointers.Object_Pointer;

   procedure Read_Request (Address : System.Address; Item : out W.Raw_Request)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Request_Pointers.Object_Pointer := Request_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Item := Pointer.all;
   end Read_Request;

   procedure Write_Result (Address : System.Address; Item : W.Raw_Result)
     with Exceptional_Cases => (others => True)
   is
      Pointer : constant Result_Pointers.Object_Pointer := Result_Pointers.To_Pointer (Address);
   begin
      if Pointer = null then
         raise Constraint_Error;
      end if;
      Pointer.all := Item;
   end Write_Result;

   function Version return Interfaces.Unsigned_32 is (1);
   function Layout (Kind, Field : Interfaces.Unsigned_32) return Interfaces.C.long is
      A : constant W.Raw_Request := (Before => 0, Cause => 0);
      B : constant W.Raw_Result := (After => 0);
   begin
      pragma Compile_Time_Error (A.Before'Position /= 0, "Request.Before");
      pragma Compile_Time_Error (A.Cause'Position /= 1, "Request.Cause");
      pragma Compile_Time_Error (B.After'Position /= 0, "Result.After");
      case Kind is
         when 1 =>
            case Field is
               when 0 => return W.Raw_Request'Size / System.Storage_Unit;
               when 1 => return W.Raw_Request'Alignment;
               when 2 => return 0;
               when 3 => return 1;
               when others => return -1;
            end case;
         when 2 =>
            case Field is
               when 0 => return W.Raw_Result'Size / System.Storage_Unit;
               when 1 => return W.Raw_Result'Alignment;
               when 2 => return 0;
               when others => return -1;
            end case;
         when others => return -1;
      end case;
   end Layout;
   function Shape (Address : System.Address; Length : Interfaces.C.size_t) return Boolean is
     (Address /= System.Null_Address and then Length > 0
      and then Length <= Interfaces.C.size_t (Storage_Offset'Last)
      and then Integer_Address (Length - 1) <= Integer_Address'Last - To_Integer (Address));
   function Decide
     (Input : System.Address; Input_Length : Interfaces.C.size_t;
      Output : System.Address; Output_Length : Interfaces.C.size_t) return Interfaces.C.int
   is
   begin
      if Input_Length /= W.Raw_Request'Size / System.Storage_Unit
        or else Output_Length /= W.Raw_Result'Size / System.Storage_Unit
        or else not Shape (Input, Input_Length) or else not Shape (Output, Output_Length)
        or else To_Integer (Input) mod W.Raw_Request'Alignment /= 0
        or else To_Integer (Output) mod W.Raw_Result'Alignment /= 0
      then
         return -1;
      end if;
      declare
         Raw : W.Raw_Request;
         Owned_Result : W.Raw_Result := (After => 0);
         Status : Interfaces.C.int;
      begin
         Read_Request (Input, Raw);
         Worldline.Recovery_Protocol_ABI.Apply (Raw, Owned_Result, Status);
         if Status /= Worldline.Recovery_Protocol_ABI.Success then
            return Status;
         end if;
         Write_Result (Output, Owned_Result);
      end;
      return 0;
   exception
      when others => return -1;
   end Decide;
end Worldline.Recovery_Protocol_C_API;

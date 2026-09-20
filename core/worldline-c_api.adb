with Ada.Streams;
with Ada.Streams.Stream_IO;
with Attest;
with Attest.SHA256;
with System.Address_To_Access_Conversions;
with System.Storage_Elements;
with Worldline.Causal_Graph;
with Worldline.Collapse;
with Worldline.Receipts;
with Worldline.Transitions;
with Worldline.World;

package body Worldline.C_API with SPARK_Mode => Off is

   use type Interfaces.C.size_t;
   use type Interfaces.Unsigned_8;
   use type Ada.Streams.Stream_Element_Offset;
   use type Interfaces.Unsigned_64;
   use type System.Address;

   package Byte_Pointers is new System.Address_To_Access_Conversions
     (Interfaces.Unsigned_8);

   Error_OK               : constant Interfaces.C.int := 0;
   Error_Invalid_Argument : constant Interfaces.C.int := 1;
   Error_IO               : constant Interfaces.C.int := 2;
   Error_Too_Large        : constant Interfaces.C.int := 3;
   Error_Internal         : constant Interfaces.C.int := 4;

   Invalid_Collapse_Request : constant Interfaces.Unsigned_8 := 255;

   Chunk_Length : constant Positive :=
     Attest.SHA256.Block_Bytes * Attest.SHA256.Block_Bytes;

   function Get_Byte
     (Base   : System.Address;
      Offset : System.Storage_Elements.Storage_Offset)
      return Interfaces.Unsigned_8
   is
      use System.Storage_Elements;
   begin
      return Byte_Pointers.To_Pointer (Base + Offset).all;
   end Get_Byte;

   procedure Put_Byte
     (Base   : System.Address;
      Offset : System.Storage_Elements.Storage_Offset;
      Value  : Interfaces.Unsigned_8)
   is
      use System.Storage_Elements;
   begin
      Byte_Pointers.To_Pointer (Base + Offset).all := Value;
   end Put_Byte;

   function Read_Hash (Base : System.Address) return Hash is
      Result : Hash;
   begin
      for I in Result'Range loop
         Result (I) :=
           Get_Byte
             (Base,
              System.Storage_Elements.Storage_Offset (I - Result'First));
      end loop;
      return Result;
   end Read_Hash;

   function To_Hash (Value : C_Hash) return Hash is
      Result : Hash;
   begin
      for I in Result'Range loop
         Result (I) := Value (C_Hash_Index (I - Result'First));
      end loop;
      return Result;
   end To_Hash;

   procedure Write_Hash (Base : System.Address; Value : Hash) is
   begin
      for I in Value'Range loop
         Put_Byte
           (Base,
            System.Storage_Elements.Storage_Offset (I - Value'First),
            Value (I));
      end loop;
   end Write_Hash;

   function Hash_File
     (Path       : System.Address;
      Path_Len   : Interfaces.C.size_t;
      Out_Digest : System.Address) return Interfaces.C.int
   is
      package SIO renames Ada.Streams.Stream_IO;
      File       : SIO.File_Type;
      Raw        : Ada.Streams.Stream_Element_Array
        (1 .. Ada.Streams.Stream_Element_Offset (Chunk_Length));
      Last       : Ada.Streams.Stream_Element_Offset;
      Buffer     : Attest.Byte_Array (0 .. Chunk_Length - 1);
      C          : Attest.SHA256.Context := Attest.SHA256.Initial;
   begin
      if Path = System.Null_Address
        or else Out_Digest = System.Null_Address
        or else Path_Len = 0
        or else Path_Len > Interfaces.C.size_t (Natural'Last)
      then
         return Error_Invalid_Argument;
      end if;

      declare
         Native_Path : String (1 .. Natural (Path_Len));
      begin
         for I in Native_Path'Range loop
            declare
               B : constant Interfaces.Unsigned_8 :=
                 Get_Byte
                   (Path,
                    System.Storage_Elements.Storage_Offset
                      (I - Native_Path'First));
            begin
               if B = 0 then
                  return Error_Invalid_Argument;
               end if;
               Native_Path (I) := Character'Val (Integer (B));
            end;
         end loop;

         SIO.Open (File, SIO.In_File, Native_Path);
      end;

      while not SIO.End_Of_File (File) loop
         SIO.Read (File, Raw, Last);
         declare
            Count : constant Natural :=
              Natural (Last - Raw'First + 1);
         begin
            if Attest.SHA256.Absorbed (C) >
              Attest.SHA256.Max_Message_Bytes -
                Interfaces.Unsigned_64 (Count)
            then
               SIO.Close (File);
               return Error_Too_Large;
            end if;

            for I in 0 .. Count - 1 loop
               Buffer (I) :=
                 Attest.Byte
                   (Raw (Raw'First + Ada.Streams.Stream_Element_Offset (I)));
            end loop;
            Attest.SHA256.Update (C, Buffer (0 .. Count - 1));
         end;
      end loop;

      SIO.Close (File);
      Write_Hash (Out_Digest, Attest.SHA256.Final (C));
      return Error_OK;
   exception
      when others =>
         if SIO.Is_Open (File) then
            SIO.Close (File);
         end if;
         return Error_IO;
   end Hash_File;

   function Hash_Bytes
     (Data       : System.Address;
      Data_Len   : Interfaces.C.size_t;
      Out_Digest : System.Address) return Interfaces.C.int
   is
      Buffer : Attest.Byte_Array (0 .. Chunk_Length - 1);
      C      : Attest.SHA256.Context := Attest.SHA256.Initial;
      Offset : Interfaces.C.size_t := 0;
   begin
      if Out_Digest = System.Null_Address
        or else (Data_Len > 0 and then Data = System.Null_Address)
      then
         return Error_Invalid_Argument;
      elsif Data_Len >
        Interfaces.C.size_t (Attest.SHA256.Max_Message_Bytes)
      then
         return Error_Too_Large;
      end if;

      while Offset < Data_Len loop
         declare
            Remaining : constant Interfaces.C.size_t := Data_Len - Offset;
            Count     : constant Natural :=
              (if Remaining > Interfaces.C.size_t (Buffer'Length)
               then Buffer'Length
               else Natural (Remaining));
         begin
            for I in 0 .. Count - 1 loop
               Buffer (I) :=
                 Get_Byte
                   (Data,
                    System.Storage_Elements.Storage_Offset
                      (Offset + Interfaces.C.size_t (I)));
            end loop;
            Attest.SHA256.Update (C, Buffer (0 .. Count - 1));
            Offset := Offset + Interfaces.C.size_t (Count);
         end;
      end loop;

      Write_Hash (Out_Digest, Attest.SHA256.Final (C));
      return Error_OK;
   exception
      when others =>
         return Error_Internal;
   end Hash_Bytes;

   function World_ID
     (Parent_ID        : System.Address;
      Filesystem_Root  : System.Address;
      Config_Root      : System.Address;
      Repository_Root  : System.Address;
      Environment_Root : System.Address;
      Evidence_Root    : System.Address;
      Out_Digest       : System.Address) return Interfaces.C.int
   is
   begin
      if Parent_ID = System.Null_Address
        or else Filesystem_Root = System.Null_Address
        or else Config_Root = System.Null_Address
        or else Repository_Root = System.Null_Address
        or else Environment_Root = System.Null_Address
        or else Evidence_Root = System.Null_Address
        or else Out_Digest = System.Null_Address
      then
         return Error_Invalid_Argument;
      end if;

      Write_Hash
        (Out_Digest,
         Worldline.World.Identity
           (Read_Hash (Parent_ID),
            Read_Hash (Filesystem_Root),
            Read_Hash (Config_Root),
            Read_Hash (Repository_Root),
            Read_Hash (Environment_Root),
            Read_Hash (Evidence_Root)));
      return Error_OK;
   exception
      when others =>
         return Error_Internal;
   end World_ID;

   function Causal_Link
     (Previous   : System.Address;
      Event_Root : System.Address;
      Out_Digest : System.Address) return Interfaces.C.int
   is
   begin
      if Previous = System.Null_Address
        or else Event_Root = System.Null_Address
        or else Out_Digest = System.Null_Address
      then
         return Error_Invalid_Argument;
      end if;
      Write_Hash
        (Out_Digest,
         Worldline.Causal_Graph.Link
           (Read_Hash (Previous), Read_Hash (Event_Root)));
      return Error_OK;
   exception
      when others =>
         return Error_Internal;
   end Causal_Link;

   function Receipt_Link
     (Previous     : System.Address;
      Receipt_Root : System.Address;
      Out_Digest   : System.Address) return Interfaces.C.int
   is
   begin
      if Previous = System.Null_Address
        or else Receipt_Root = System.Null_Address
        or else Out_Digest = System.Null_Address
      then
         return Error_Invalid_Argument;
      end if;
      Write_Hash
        (Out_Digest,
         Worldline.Receipts.Link
           (Read_Hash (Previous), Read_Hash (Receipt_Root)));
      return Error_OK;
   exception
      when others =>
         return Error_Internal;
   end Receipt_Link;

   function Transition_Allowed
     (From_State : Interfaces.Unsigned_8;
      To_State   : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
   is
      Last : constant Interfaces.Unsigned_8 :=
        Interfaces.Unsigned_8
          (Transitions.World_State'Pos (Transitions.World_State'Last));
   begin
      if From_State > Last or else To_State > Last then
         return 0;
      elsif Transitions.Allowed
        (Transitions.World_State'Val (Integer (From_State)),
         Transitions.World_State'Val (Integer (To_State)))
      then
         return 1;
      else
         return 0;
      end if;
   end Transition_Allowed;

   function Transaction_Transition_Allowed
     (From_State : Interfaces.Unsigned_8;
      To_State   : Interfaces.Unsigned_8) return Interfaces.Unsigned_8
   is
      Last : constant Interfaces.Unsigned_8 :=
        Interfaces.Unsigned_8
          (Transitions.Transaction_State'Pos
             (Transitions.Transaction_State'Last));
   begin
      if From_State > Last or else To_State > Last then
         return 0;
      elsif Transitions.Transaction_Allowed
        (Transitions.Transaction_State'Val (Integer (From_State)),
         Transitions.Transaction_State'Val (Integer (To_State)))
      then
         return 1;
      else
         return 0;
      end if;
   end Transaction_Transition_Allowed;

   function Collapse_Decide
     (Request : C_Collapse_Request_Access) return Interfaces.Unsigned_8
   is
      Last_State : constant Interfaces.Unsigned_8 :=
        Interfaces.Unsigned_8
          (Transitions.World_State'Pos (Transitions.World_State'Last));
   begin
      if Request = null
        or else Request.Reserved /= 0
        or else Request.Has_Conflicts > 1
        or else Request.Has_Foreign_Managed_Writes > 1
        or else Request.Candidate_State > Last_State
      then
         return Invalid_Collapse_Request;
      end if;

      declare
         Native_Request : constant Collapse.Collapse_Request :=
           (Candidate_State =>
              Transitions.World_State'Val
                (Integer (Request.Candidate_State)),
            Has_Conflicts => Request.Has_Conflicts = 1,
            Has_Foreign_Managed_Writes =>
              Request.Has_Foreign_Managed_Writes = 1,
            Expected_Parent => To_Hash (Request.Expected_Parent),
            Candidate_Parent => To_Hash (Request.Candidate_Parent),
            Expected_Owner => To_Hash (Request.Expected_Owner),
            Candidate_Owner => To_Hash (Request.Candidate_Owner),
            Expected_Base => To_Hash (Request.Expected_Base),
            Candidate_Base => To_Hash (Request.Candidate_Base),
            Expected_Delta => To_Hash (Request.Expected_Delta),
            Candidate_Delta => To_Hash (Request.Candidate_Delta),
            Expected_Root_Set => To_Hash (Request.Expected_Root_Set),
            Candidate_Root_Set => To_Hash (Request.Candidate_Root_Set),
            Expected_Staged_Root => To_Hash (Request.Expected_Staged_Root),
            Actual_Staged_Root => To_Hash (Request.Actual_Staged_Root));
      begin
         return Interfaces.Unsigned_8
           (Collapse.Decision'Pos (Collapse.Decide (Native_Request)));
      end;
   exception
      when others =>
         return Invalid_Collapse_Request;
   end Collapse_Decide;

end Worldline.C_API;

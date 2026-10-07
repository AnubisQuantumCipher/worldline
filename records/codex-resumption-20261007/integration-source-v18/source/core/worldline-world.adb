with Attest;
with Attest.SHA256;

package body Worldline.World with SPARK_Mode is

   Domain : constant Attest.Byte_Array :=
     [Attest.Byte (Character'Pos ('w')),
      Attest.Byte (Character'Pos ('o')),
      Attest.Byte (Character'Pos ('r')),
      Attest.Byte (Character'Pos ('l')),
      Attest.Byte (Character'Pos ('d')),
      Attest.Byte (Character'Pos ('l')),
      Attest.Byte (Character'Pos ('i')),
      Attest.Byte (Character'Pos ('n')),
      Attest.Byte (Character'Pos ('e')),
      Attest.Byte (Character'Pos ('-')),
      Attest.Byte (Character'Pos ('w')),
      Attest.Byte (Character'Pos ('o')),
      Attest.Byte (Character'Pos ('r')),
      Attest.Byte (Character'Pos ('l')),
      Attest.Byte (Character'Pos ('d')),
      Attest.Byte (Character'Pos ('-')),
      Attest.Byte (Character'Pos ('v')),
      Attest.Byte (Character'Pos ('1'))];

   function Identity
     (Parent_ID        : Hash;
      Filesystem_Root  : Hash;
      Config_Root      : Hash;
      Repository_Root  : Hash;
      Environment_Root : Hash;
      Evidence_Root    : Hash) return Hash
   is
      C : Attest.SHA256.Context := Attest.SHA256.Initial;
   begin
      Attest.SHA256.Update (C, Domain);
      Attest.SHA256.Update (C, Parent_ID);
      Attest.SHA256.Update (C, Filesystem_Root);
      Attest.SHA256.Update (C, Config_Root);
      Attest.SHA256.Update (C, Repository_Root);
      Attest.SHA256.Update (C, Environment_Root);
      Attest.SHA256.Update (C, Evidence_Root);
      return Attest.SHA256.Final (C);
   end Identity;

end Worldline.World;

package Worldline.World with SPARK_Mode is

   function Identity
     (Parent_ID       : Hash;
      Filesystem_Root : Hash;
      Config_Root     : Hash;
      Repository_Root : Hash;
      Environment_Root : Hash;
      Evidence_Root   : Hash) return Hash
     with Global => null;

end Worldline.World;

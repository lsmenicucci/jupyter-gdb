# save this as shell.nix
{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  packages = [ pkgs.lapack pkgs.gfortran ];

  # add clib to the shell environment
  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    pkgs.stdenv.cc.cc.lib
    pkgs.zlib
    pkgs.lapack
    pkgs.openblas
  ];
}

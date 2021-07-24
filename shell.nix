{pkgs? import <nixpkgs> {}}:
with pkgs;

let
  pythonEnv = python3.withPackages (ps: with ps; [
    pygame
  ]);

in
  mkShell {
    packages = [
      pythonEnv
      nvim_py
    ];
  }

{
  description = "Unified CLI for Zenith dotfiles and desktop system management";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    zenith-shell = {
      url = "github:zaeemali272/zenith-shell";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    ...
  } @ inputs: let
    inherit (nixpkgs.lib) genAttrs platforms lists systems;

    pkgsOf = nixpkgs.legacyPackages;
    systems' = lists.intersectLists platforms.linux systems.flakeExposed;
    eachSystem = genAttrs systems';
  in {
    packages = eachSystem (system: rec {
      zenith-cli = pkgsOf.${system}.callPackage ./default.nix {
        rev = self.rev or self.dirtyRev or "0.1.0";
        zenith-shell = inputs.zenith-shell.packages.${system}.default or null;
      };
      with-shell = zenith-cli.override { withShell = true; };
      default = zenith-cli;
    });

    devShells = eachSystem (system: {
      default = pkgsOf.${system}.mkShellNoCC {
        packages = [ self.packages.${system}.default ];
      };
    });
  };
}

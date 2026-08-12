{
  description = "ASIC puzzle Verilog simulation environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          iverilog
          hal-hardware-analyzer
          # verilator

          # Required when Verilator compiles generated C++.
          gcc
          gnumake
        ];
      };
    };
}

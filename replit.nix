{pkgs}: {
  deps = [
    pkgs.python311Packages.pytest
    pkgs.glibcLocales
    pkgs.freetype
    pkgs.xsimd
    pkgs.pkg-config
    pkgs.libxcrypt
  ];
}

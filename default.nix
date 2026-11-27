{
  rev ? "0.1.0",
  lib,
  python3,
  installShellFiles,
  swappy,
  libnotify,
  slurp,
  wl-clipboard,
  cliphist,
  xdg-utils,
  grim,
  fuzzel,
  gpu-screen-recorder,
  ffmpeg,
  dconf,
  killall,
  zenith-shell ? null,
  withShell ? false,
}:
python3.pkgs.buildPythonApplication {
  pname = "zenith-cli";
  version = "${rev}";
  src = ./.;
  pyproject = true;

  build-system = with python3.pkgs; [
    hatch-vcs
    hatchling
  ];

  dependencies = with python3.pkgs; [
    materialyoucolor
    pillow
  ];

  pythonImportsCheck = ["zenith"];

  nativeBuildInputs = [installShellFiles];
  propagatedBuildInputs =
    [
      swappy
      libnotify
      slurp
      wl-clipboard
      cliphist
      xdg-utils
      grim
      fuzzel
      gpu-screen-recorder
      ffmpeg
      dconf
      killall
    ]
    ++ lib.optional (withShell && zenith-shell != null) zenith-shell;

  env.SETUPTOOLS_SCM_PRETEND_VERSION = rev;

  postInstall = ''
    if [ -f completions/zenith.fish ]; then
      installShellCompletion --fish completions/zenith.fish
    fi
  '';

  meta = {
    description = "Unified CLI for Zenith dotfiles and desktop system management";
    homepage = "https://github.com/zaeemali272/zenith-cli";
    license = lib.licenses.mit;
    mainProgram = "zenith";
    platforms = lib.platforms.linux;
  };
}

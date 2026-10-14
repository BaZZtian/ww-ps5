# Release preparation

Preserve the owner's repository visibility. Game dumps, keys and generated
`game.wwhd` modules must stay outside published artifacts.

1. Build the ROM-free app with `ps5/tools/build-catalog.py` as described in
   [CATALOG-SETUP.md](CATALOG-SETUP.md). Run the module-loader and frame-pacing tests.
2. Test the app and a locally prepared game package on PS5. Check the missing-game
   screen, controls, saves and menus. Compilation alone is not gameplay proof.
3. Raise `ps5/sce_sys/param.json` contentVersion, update the READMEs and commit.
4. Package the tested executable with `ps5/tools/package-catalog.py`, using
   `--console-tested` only after console verification. Publish its `PPSA99641.zip`.
5. Package matching setup and source archives:

```sh
python3 ps5/tools/package-release.py --version v0.1.2 --runtime /path/to/runtime-bundle --host-tools /path/to/host-tools
python3 ps5/tools/package-release.py --version v0.1.2
python3 ps5/tools/validate.py --archive dist/Wind-Waker-HD-PS5-v0.1.2-setup.zip
```

The setup bundle includes the verified compiler headers and host tools from the
previous portable setup. Setup prepares the separate game module by default;
`ps5/tools/build.py` remains available for a monolithic source build.

Include dependency source archives, licenses and SHA-256 checksums. Check every
archive against its manifest. Never publish the privately generated game folder.
Use the owner's gh account, tag the packaged commit and publish a stable release
after testing. Download and verify the published assets. Use a new tag instead
of replacing assets in an existing published release.

Windows, macOS and Linux launchers are included for x86-64 and ARM64. Record
which hosts actually ran setup separately from console gameplay verification.

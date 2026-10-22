CURRENT INSTALLATION GUIDE: https://github.com/mshivam019/ww-ps5/blob/main/INSTALL.md
Use that guide for internal/USB storage, offline copying or Wi-Fi FTP.
M.2, Ethernet and PS5 Upload are optional. Paths in older instructions below
describe the developer setup, not required hardware or transfer software.

# Separate app and game setup

Available in v0.1.2. The separate app and game module have been tested on PS5
firmware 9.00, including the missing-game screen, save loading, controls and menu.

The app contains the PS5 runtime and renderer. Your game code and assets stay
in a separate, locally prepared `game/` folder. This remains a native PS5 port.

## Player flow

1. Install the matching `PPSA99641.zip` app.
2. Extract the matching computer setup bundle. Run `Prepare-Game-Windows.cmd`,
   `Prepare-Game-macOS.command`, or `sh prepare-game.sh` on Linux.
3. Select your **USA Wii U version 0** dump: WUX or extracted `code`, `content`
   and `meta` folders. WUX extraction also needs your locally supplied keys.
4. With the game closed, copy the generated `game/` and `user/` folders into
   the installed `PPSA99641` folder. Keep existing saves and settings.
5. Launch Wind Waker HD from the PS5 home screen.

`game/game.wwhd` is the compiled game-code module. The adjacent `code`, `content`
and `meta` folders are also required. It is not a renamed ROM or a complete game
archive. Never distribute this module or the game assets.

GameCube `.gcm`, `.iso` and `.rvz` dumps are for the original Wind Waker and
cannot be used by this Wii U HD port. Supplying only `cking.rpx` is insufficient.

A missing or incompatible module opens a setup screen. Press Cross to exit.
Use the converter supplied with the app version: incompatible module interfaces
are rejected before starting the game. Preserve `game/` when replacing app files.

## Developer build

Run the existing dependency/SDL setup first. Build the app without a ROM:

```sh
python3 ps5/tools/build-catalog.py --sdk /path/to/sdk --vulkan /path/to/PS5_Vulkan \
  --sdl-build build/sdl3-ps5 --sdl-source /path/to/SDL --jobs 4
python3 ps5/tools/package-catalog.py --executable build/catalog-app/eboot.bin \
  --libc /path/to/PS5_Vulkan/runtime/libc.prx --output dist/catalog-test
```

The builder creates a placeholder runtime to discover its exported functions,
then builds the app with forwarding functions and a separate module loader.
No generated game instructions are linked into this app. The original monolithic
build is still available with `WWHD_GAME_MODULE=OFF` (the default).

The compiler bundle used by player setup is unchanged. To prepare private data:

```sh
python3 ps5/tools/setup.py --game-package --game /path/to/extracted-game \
  --output /path/to/private/PPSA99641
```

## Validation

```sh
python3 ps5/tests/test-module-loader.py
python3 ps5/tests/test-frame-pacing.py
```

This runs synthetic code through the module loader under address/undefined
behavior sanitizers: callbacks, weak import overrides, relocations, invalid
headers, invalid relocations, missing imports, exception unwinding and absent
files. It does not run the game. The actual locally generated module also passed
host binding checks; an incompatible interface marker was rejected.

Before publishing a new stable release or catalog submission, test the missing
module screen, normal launch, saves, controls, touchpad menu and GamePad toggle
on PS5. Host tests cannot verify console executable-memory permissions.

The catalog icon is original vector artwork in `ps5/art/catalog-icon.svg`,
licensed under this repository's MPL-2.0 license. It uses no extracted game art.

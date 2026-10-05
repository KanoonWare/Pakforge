# PakForge

**PakForge v0.3.0-multipack beta** is a desktop catalog and installer for community-made HD texture packs used with video game emulators. It links to packs hosted by their creators or other third parties; PakForge does not host pack files.

## Current support

- **PlayStation 2** — active catalog
- **Nintendo 64** — active catalog
- GameCube, Wii, Switch, PlayStation 3, Xbox 360, Xbox, and PSP tabs are marked “Soon” and are not yet available.

The catalog offers multiple pack choices where available, shows creator credits with links, downloads archives to a local staging folder, and extracts pack files into the texture directory you choose. The app and catalog are beta software: links can change or stop working, and availability depends on third-party hosts.

## Run from source

You need Python 3 with Tk support. From the project directory, create an environment and install the app's Python dependencies:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install customtkinter pillow requests cryptography
python pakforge.py
```

On Linux, install your distribution's Tk package if Tkinter is not included with Python.

### Build a Windows executable

```powershell
python -m pip install pyinstaller
pyinstaller --clean --noconfirm PakForge.spec
```

The executable is written to `dist/PakForge.exe`.

## Use PakForge

1. Select **PS2** or **N64**, then choose a game and texture pack.
2. Check the pack creator credit in the game card; its link opens the creator or source page.
3. Set the emulator's texture directory. The initial paths are suggestions and can be changed in the app.
4. Select **Download Textures**. Downloads are staged under `downloads/<console>/` by default; use the folder control to choose another location.
5. Select **Replace Textures** to extract the pack into `<texture directory>/<game ID>/replacement`.

ZIP extraction is built in. Some catalog links use `.7z` or `.rar`; those files can be downloaded, but extracting them requires compatible unpacking support registered with Python.

PakForge stores preferences, selected packs, and replacement timestamps in `pakforge_config.json` beside the app. The download staging folder defaults to a `downloads` folder under the current working directory.

## Catalog contributions and credits

Game and pack entries live in [`n64_games.py`](n64_games.py) and [`ps2_games.py`](ps2_games.py). Keep each pack's `credit_name` and `credit_url` accurate when updating a link or adding a catalog entry. PakForge displays these credits in the app.

Please contribute links and metadata only. Do not add texture-pack archives, ROMs, game assets, or bundled box art to the repository. Cover art is referenced by URL in the catalog and loaded at runtime. Pack creators and third-party sites retain their rights to their work and content.

## Disclaimer

PakForge links to HD texture packs created and hosted by third-party community members. PakForge does not create, host, or claim ownership of any texture pack content, and does not distribute game ROMs or copyrighted game assets of any kind.

You are responsible for ensuring you own a legal copy of any game you use with these texture packs. Texture pack availability depends on third-party hosts and may change or be removed at any time.

If you are a texture pack creator and would like your work credited differently or removed from this list, please reach out through the contact info on [kanoonware.com](https://kanoonware.com).

## License

The project license has not been selected yet, and there is currently no `LICENSE` file. Third-party texture packs, cover art, and linked content are not covered by any future PakForge code license.

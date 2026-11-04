# OpenAL Soft runtime (Windows x64)

Unmodified OpenAL Soft 1.25.2 Win64 `soft_oal.dll`, installed as `OpenAL32.dll`
for the existing OpenTK OpenAL binding. Downloaded from the upstream distribution:

- Binary archive: https://openal-soft.org/openal-binaries/openal-soft-1.25.2-bin.zip
- Corresponding source: https://openal-soft.org/openal-releases/openal-soft-1.25.2.tar.bz2
- Upstream: https://openal-soft.org/

The archive's COPYING and corresponding source archive are included. This is a dynamically loaded LGPL library,
separate from the game; it can be replaced with a compatible build. No native
library modifications were made. This does not change the library's licence.
The build copies the DLL and these notices to the output. Other platforms use
their system OpenAL; unavailable devices/libraries are reported and play silently.

DLL SHA-256: `3963b06e319180700be0bcc0d027336664bb3a4975876b4a5442f10746fab5b4`.

# Animation folder convention

Each scene animation has one folder: `Assets/Animations/<AnimationName>/`.

- `animation.md` is the specification for that animation: intended action,
  sequence, sound and camera cues, required assets, gameplay transition,
  implementation status and unresolved decisions.
- Future scene-specific runtime data and files live beside that document.
  Do not create empty placeholder files or treat proposals as implemented.
- Reference shared models, textures and character clips in
  `Assets/Models/<Category>/<Asset>/` rather than duplicating them.
- Editable sources and provenance use `Art/assets/<animation_id>/`, matching
  the existing asset source convention. Python tooling remains local and ignored.

The selected opening is [ConeHat](ConeHat/animation.md). Other possible openings
live in [Art/ANIMATION_IDEAS.md](../../Art/ANIMATION_IDEAS.md).

Future openings should share a defined transition into gameplay, so changing
the opening does not require changing normal running gameplay. Playback,
selection and skipping still require implementation; this folder convention
does not add those features.

Existing character animation clips, such as the officer's run poses and
manifest, remain with their character model. This directory groups scene
animations that coordinate characters, props, camera and audio.

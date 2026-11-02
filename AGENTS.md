# Repository conventions

## Assets and animation scenes

- Shared runtime models, textures and character animation clips belong in
  `RunnerGame/Assets/Models/<Category>/<Asset>/`.
- Complete runtime map packages belong in `RunnerGame/Assets/Maps/<Map>/`.
- A scene animation belongs in
  `RunnerGame/Assets/Animations/<AnimationName>/`.
- Each scene animation must have an `animation.md` in its own folder. Keep
  that document specific to the scene: intended action, sequence, camera and
  sound cues, dependencies, gameplay transition, implementation status and
  unresolved decisions. Keep it current as the implementation changes.
- Put scene-specific runtime files beside `animation.md`. Reference shared
  models and clips in their existing folders instead of duplicating them.
- Keep alternative opening ideas in `RunnerGame/Art/ANIMATION_IDEAS.md`, with
  links to any selected scene specifications. Do not mix the idea backlog into
  an individual scene's specification or create duplicate specifications.
- Editable sources and provenance follow
  `RunnerGame/Art/assets/<asset_or_animation_id>/`. Python generation, export
  and review tooling stays local and ignored under the existing ignore rules.
- Existing character clips, such as the officer's run frames and animation
  manifest, stay with their character model; `Assets/Animations/` is for scenes
  coordinating characters, props, camera and audio.
- Keep relative documentation links and runtime asset paths working after
  moves. Preserve asset bytes and source/licence records. Clearly distinguish
  planned animation and audio from implemented and verified behaviour.

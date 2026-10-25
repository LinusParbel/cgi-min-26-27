# Street prop execution ledger

Plan:docs/superpowers/plans/2026-10-23-street-props.md

Previous batch approved by user ("it looks good for now lets move on") and installed:28files across5groups, allsource/runtimeSHA256 match. Incremental solutionbuild passed0warnings/errors. Existing warningCS0649 remains known from cleanrebuild.

Ruling: continue with the backlog's next street props using generic authored designs and established engine contract, without another scope permission round. New batch still shown before runtimeinstallation. User cannot see inlineimages, so final preview must open on desktop.

Preflight: tasks own distinct folders; furniture is one kit/one atlas, independently placeable zero-origin parts with bake separation. Pothole deliberately uses visible raised visual patch rather than hidden negative geometry under opaque road. Tree is generic original proceduralgeometry; no external asset licence assumption. Shared tools stayread-only. No interface/file ownership conflict.

Status:Task1ready;Task2/3pending;Task4pending. No commits.

Task1candidate complete: furniture5728exportedtri (bench2128/planter1836/lamp1764),1024sharedopaqueatlas, independentreviewPASS. Evaluatedsource5856includes128collapsedserializedbeveltriangles filtered deterministically. Planterwall/rimcoplanarity corrected with onecorrectionbake; remainingcorneroverlap trimmed with source/exportUVparity and no thirdbake. Source support/ground assertions and6negativefixtures verified. MinorplausiblecornerAOretained, no liveoverlap accepted.

Task2candidate complete: pothole528tri,512opaqueatlas, footprint1.191x.872m, visiblegeometry2.502-14.320mmaboveopaqueasphalt. IndependentreviewPASS including4negativefixtures andactualroadimage. Visualpatchonly,notexcavation/collision.

Task3treebuilderimplementingoriginalopaqueleafgeometry; noexternalassetsassumed. Task4sceneconfigprepared at docs/art/street-props-scene.json; treeplacement/completepreviewpending. Newpropsnotinstalled.

Schedulingnote: furniturecorrectionbakebrieflyoverlappedpotholebakebeforeparentqueueinstructionarrived; furniturefinishedbeforestop. Bothoutputsvalidated. No furtherconcurrentbakesapproved; treehasexclusivebakeslot.

## Final candidate state

All5props complete. Tree11516actualtri,4000opposed triangle pairs with distinctback vertices; initial one-sided UV-conversion failure fixed in oneauthorizedcorrectionbake alongside larger.20x.125m leaves. Actualnegativefixturemissingbacks rejects; deterministicrebuild hashes agree. Treegroundpositionx4.2,z-27 clearscurb/buildingbay; final54instances/26meshes/12textures render inspectedbyparentandindependentfinalreviewer.

Freshparent checks: furniture5728tri/pothole528tri/tree11516tri verifyexit0;14unittestsPASS; solution/reviewtoolbuilds exit0with0incrementalwarnings. FinalindependentreviewPASS, no mustfix. Firstmissing-tree-manifest renderattempt failed becausebuilderhadnotyetfinishedmetadata; finalrenderafterreadiness succeeded. No enginecodechanges.

Handoff:2026-10-23-street-props-handoff.md. Candidate files/hashes prepared, no newruntimeinstall before user'svisualreview. Previous28-fileessentialbatch remains installed. No commits.


Approved and installed2026-10-23 after user replied "okay" to reopened visual review. All14runtimefiles match the source SHA256 delivery list. Gameplay integration is separate. No commits.

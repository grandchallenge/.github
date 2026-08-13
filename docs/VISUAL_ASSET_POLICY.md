# GCL Visual Asset Format Policy

This policy governs format selection for visual assets published in Grand Challenge repositories, especially README illustrations, documentation figures, posters, diagrams, and other presentation media.

## Principle

Use the format that preserves the source artwork faithfully. Do not convert an asset to SVG merely because SVG is resolution-independent.

## Raster-originated artwork

Use **PNG** or a high-quality **JPEG** for artwork whose source is raster or whose appearance depends on fixed typography, texture, generated-image composition, screenshots, photographic content, or pixel-level layout.

This category includes:

- generated posters and infographics;
- typography-heavy illustrations;
- screenshots and UI captures;
- photographs and rendered scenes;
- raster charts or figures whose text and spacing have already been composed;
- existing PNG/JPEG artwork that already renders correctly.

For these assets:

1. Preserve the original raster whenever practical instead of reconstructing it as SVG.
2. Prefer PNG when text, line art, transparency, or lossless fidelity matters.
3. Use high-quality JPEG when photographic or continuous-tone content makes JPEG materially smaller without visible degradation.
4. For README-critical artwork, prefer PNG or baseline/non-progressive JPEG unless a progressive JPEG has been visually validated in the target renderer.
5. Do not display a raster image wider than its intrinsic pixel width unless visual inspection confirms that the upscale remains acceptable.
6. Avoid repeated lossy transcoding. Derive resized copies from the best available source.

## Vector-native artwork

SVG is appropriate when the source is genuinely vector-native and browser rendering preserves its layout. Typical examples are:

- geometric diagrams;
- line drawings;
- icons and logos;
- plots exported directly from a vector renderer;
- schematics and node-link diagrams whose geometry, text placement, and font metrics have been verified in the target environment.

Do not rebuild raster-originated artwork as SVG solely to obtain scalable display. Dense or typography-heavy SVG must be visually checked in GitHub/browser rendering before merge because font substitution and metric differences can alter spacing, wrapping, and legibility.

## Repository presentation checks

Before merging a visual asset used in a README or prominent documentation page:

1. Render the exact repository version in the intended GitHub/browser context.
2. Check the complete image, not only its first viewport or thumbnail.
3. Confirm text is legible, unsquashed, and not clipped or reflowed unexpectedly.
4. Confirm aspect ratio is preserved and the requested display width does not unnecessarily upscale the source.
5. Confirm the committed asset is complete and the README/document points to the intended file.
6. If conversion changes typography, spacing, colors, or composition, treat the conversion as failed and retain the faithful source format.

## Scope and authority

This is a presentation and authoring policy. It does not alter constitutional authority, certification authority, repository protection, or claim semantics. Repository-specific requirements may be stricter, but should not silently force raster-originated artwork into SVG.

The governing rule is simple: **raster-originated or typography-heavy artwork stays raster; SVG is reserved for genuinely vector-native material that renders correctly in context.**

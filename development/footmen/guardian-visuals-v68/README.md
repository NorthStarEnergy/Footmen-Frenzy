# Guardian visual update

Output: `FF799X_Rx_Veigar_GuardianVisuals_v68.w3x`, based on the completed combined v68 with the selected Veigar Dark Matter icon.

- Force Field (AFg1, X) uses the user's supplied `ForceField-selected.png`, kept at its original dimensions with standard BTN/DISBTN formatting. The generated `ForceField.png` is superseded and is not installed.
- Guardian Shield (AZd1) uses the prior Force Field BTN/DISBTN bytes exactly.
- The dome retains the existing animated shield, at half its former material opacity, with 30 sparse five-sided outlines on the surface. The outline material has 18% alpha, further multiplied by the existing effect fade. No filled panels were added.
- Guardian's lantern becomes a custom low-poly blue crystal pylon with gold supports, plus a matching icon. The original lantern unit remains available for other casters. Guardian alone creates the cloned hGpy unit.
- Runtime and editor custom script are patched together. Spell mechanics are unchanged. The Veigar meteor icon is retained unchanged.

Validation: JASS compiler passed; MDX encode/decode roundtrips and mesh indices passed; imported bytes read back exactly; 1,363 unrelated archive members preserved. Live game visibility and rendering remain untested. `model-preview.png` is a geometry illustration, not an engine screenshot.

## Artwork provenance

Built-in image_gen was used. Full generated source files are saved alongside this document. The user-supplied Force Field selection supersedes the generated wall artwork.

Forcefield generation prompt: Create one square Warcraft III spell icon, no border no text. Forcefield spell: just THREE luminous blue translucent pentagonal energy wall panels rising vertically from the ground in a short connected barrier, seen at a clear three-quarter downward game camera angle. Each panel has five sides, readable silhouette, pale cyan edge and subdued blue glass-like interior. Small restrained blue casting glow where the three walls meet a rough dark ground. Minimal simple painted classic Warcraft 3 icon art with broad soft brushwork, no ultra sharp detail, no characters, no buildings, no dome, no extra objects, no busy background. Fill frame with this one clear spell symbol. Dark navy backdrop, blue/cyan magic. Elegant simple readable at small size.

Pylon generation prompt: One square Warcraft III ability icon, simple soft hand-painted classic RTS art, broad painterly shading, no border no text. Subject: single small Protoss-inspired psionic pylon, a tall floating elongated faceted cyan-blue crystal with pointed top and bottom, held above a low base by three curved golden bronze supports. Clear silhouette and bright restrained white cyan core. This is Guardian's rescue beacon. Dark navy subtly smoky background with a little blue light below it. Only the pylon, no people no scene no intricate ornament no sparks everywhere. Elegant low detail, readable at small icon size, not photorealistic, not overly sharp.

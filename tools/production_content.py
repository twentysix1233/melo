from __future__ import annotations

from textwrap import dedent


ROOT_README = dedent(r'''
# Remotion Production Master Pack

This archive is an offline working library for building high-end product advertisements, launch films, demo reels, feature announcements, and social cuts with Remotion and Codex.

It combines four layers:

1. **Authoritative skills** from the Remotion and Remocn maintainers.
2. **Selected community skills** that add shot grammar, editorial rhythm, voiceover synchronization, and motion-design recipes.
3. **A complete Remocn source mirror**, plus a generated component catalogue grouped by category and block.
4. **A strict production system**: creative brief, beat map, motion direction, product cinematography, sound pass, independent critique, and render QA.

## Start here

1. Read `00_START_HERE/INSTALL_AND_USE.md`.
2. Put the custom skills from `01_AGENT_SKILLS/00_CUSTOM_PRODUCTION_STACK/` into your project-level `.codex/skills/` directory, or let Codex read them directly from this pack.
3. Keep `02_REMOCN_COMPONENT_LIBRARY/_INDEX/ALL_COMPONENTS.json` in the project context. The `remocn-component-curator` skill uses it as the offline selector.
4. Give Codex the project repository, real product screenshots or a runnable app, brand assets, and a concrete delivery format.
5. Use the master prompt in `03_PRODUCTION_BLUEPRINTS/01_MASTER_PROMPT_EN.md` or the Russian version beside it.
6. Do not accept “done” until `production-ad-critic` and `render-qa-engineer` both pass the cut.

## Core rule

The component library is material, not direction. A premium film is not created by stacking presets. Every movement must serve hierarchy, continuity, product comprehension, rhythm, or emotion.

## Provenance

Upstream code and skills remain under their original licences. Source URLs, commit hashes, licence files, and retrieval dates are stored beside each imported source and in `04_PROVENANCE_AND_LICENSES/`.
''').strip() + "\n"


INSTALL_AND_USE = dedent(r'''
# Install and use with Codex

## Recommended project layout

```text
my-remotion-ad/
├─ .codex/
│  └─ skills/
│     ├─ production-ad-director/
│     ├─ creative-strategy-storyboard/
│     ├─ motion-art-director/
│     ├─ product-ui-cinematography/
│     ├─ remocn-component-curator/
│     ├─ sound-design-editor/
│     ├─ production-ad-critic/
│     └─ render-qa-engineer/
├─ references/
├─ public/
├─ src/
├─ AGENTS.md
└─ package.json
```

Copy the folders from `01_AGENT_SKILLS/00_CUSTOM_PRODUCTION_STACK/` into `.codex/skills/`.

Install the maintained upstream skills as well:

```bash
npx skills add remotion-dev/skills --yes
npx skills add Remocn/remocn --yes
```

For the official Codex integration, see `01_AGENT_SKILLS/01_OFFICIAL/remotion-codex-plugin/`.

## Working order

1. `creative-strategy-storyboard` creates the message hierarchy, three opening directions, treatment, and beat map.
2. `production-ad-director` selects the direction and controls the full production.
3. `remocn-component-curator` chooses a restrained set of components from the offline index.
4. `motion-art-director` defines the movement system and transitions.
5. `product-ui-cinematography` turns real product behaviour into clear, cinematic shots.
6. `sound-design-editor` creates the rhythm and cue sheet.
7. `production-ad-critic` reviews the film independently and issues timestamped fixes.
8. `render-qa-engineer` validates determinism, assets, layouts, renders, and deliverables.

## Context to provide

Give the agent access to the actual application or repository whenever possible. Include the target audience, primary action, strongest proof, delivery aspect ratios, target duration, brand assets, and any legal copy. When information is absent, the agent must write assumptions into `creative/ASSUMPTIONS.md` instead of quietly inventing product claims.

## Minimum outputs before animation

```text
creative/
├─ brief.md
├─ assumptions.md
├─ directions.md
├─ selected-treatment.md
├─ beat-map.json
├─ shot-list.csv
├─ asset-manifest.md
└─ audio-cue-sheet.csv
```

## Minimum outputs before delivery

```text
qa/
├─ critic-pass-01.md
├─ critic-pass-final.md
├─ render-smoke-test.md
├─ frame-contact-sheet/
├─ safe-area-checks/
└─ delivery-manifest.json
```

## Non-negotiable quality gate

A cut is not complete while any critical failure remains or the independent score is below 90/100. “Looks good” is not a review. Every defect must have a timestamp, diagnosis, and concrete correction.
''').strip() + "\n"


CUSTOM_SKILLS: dict[str, str] = {
    "production-ad-director/SKILL.md": dedent(r'''
        ---
        name: production-ad-director
        description: Direct a premium Remotion product advertisement from repository inspection through final render. Use for launch films, SaaS promos, app demos, feature announcements, brand reels, and social ads that require a coherent concept, deliberate motion grammar, real product proof, sound, critique, and delivery variants.
        ---

        # Production Ad Director

        Act as the creative director, editor, and production owner. The goal is not to demonstrate how many effects are available. The goal is to make the product desirable and immediately understandable.

        ## Governing principles

        - Build one visual thesis for the film. Repetition with development is stronger than unrelated spectacle.
        - Treat the first three seconds as a separate deliverable. Produce three materially different openings before committing.
        - Show the strongest proof early. Do not spend half the runtime on a logo prelude.
        - Use real product behaviour and real copy. Never invent features, metrics, customers, awards, or interface states.
        - Every movement must answer one question: what should the viewer notice, understand, anticipate, or feel?
        - Components are raw material. Re-tokenize, combine, and simplify them so the film belongs to the product.
        - Prefer motivated transitions: shared geometry, camera continuation, object hand-off, colour carry, mask continuation, or semantic transformation.
        - Preserve readable holds. Motion without comprehension is decorative noise.
        - Use deterministic frame-driven animation. Never rely on CSS transitions, wall-clock time, or unseeded randomness.

        ## Production sequence

        ### 1. Product truth pass

        Inspect the repository, running application, README, landing page, screenshots, brand files, and existing copy. Write:

        - audience and buying context;
        - primary promise in one sentence;
        - strongest visible proof;
        - primary call to action;
        - claims that are verified;
        - claims that are unknown and therefore prohibited;
        - brand tokens and recurring shapes;
        - available assets and missing assets.

        Put unresolved assumptions in `creative/ASSUMPTIONS.md`.

        ### 2. Direction pass

        Create three directions. Each needs a title, one-sentence concept, opening image, motion thesis, typography behaviour, colour strategy, sound world, product-proof method, and risk. The directions must not be the same edit with different colours.

        Select one direction using the objective and audience, not personal novelty. Preserve the rejected directions for later hooks or format variants.

        ### 3. Treatment and beat map

        Define the film in beats rather than pages. Each beat must specify:

        - start and end frame;
        - communication job;
        - dominant visual object;
        - product truth shown;
        - entry, hold, and exit behaviour;
        - camera state;
        - text load and minimum reading time;
        - audio cue;
        - transition logic to the next beat.

        A typical product film may use hook → tension → product reveal → proof sequence → differentiator → resolution → CTA, but alter the order when the product demands it.

        ### 4. Asset and component plan

        Ask `remocn-component-curator` for a shortlist. Use one signature motion device and a small support vocabulary. Avoid a preset carousel. For every selected component, record why it is appropriate and what will be changed to match the brand.

        ### 5. Build in passes

        1. **Animatic:** timing, composition, copy, and camera with primitive shapes.
        2. **Product pass:** real UI, assets, masks, cursor choreography, and proof.
        3. **Art pass:** typography, colour, materials, depth, lighting, and texture.
        4. **Motion pass:** easing, overlap, continuity, secondary motion, and exits.
        5. **Sound pass:** music structure, impacts, UI detail, transitions, and mix.
        6. **Adaptation pass:** 16:9, 9:16, 1:1, captions, and platform-safe crops.

        Do not polish a broken animatic. Fix the idea and pacing before surface detail.

        ### 6. Independent review loop

        Run `production-ad-critic` without feeding it implementation excuses. Apply all critical fixes, then rerun. A score below 90/100 is a failed cut. A high score cannot override a critical failure.

        ### 7. Technical delivery

        Run `render-qa-engineer`. Produce a delivery manifest containing composition ID, dimensions, frame rate, duration, codec, audio, source commit, render command, output checksum, and known platform constraints.

        ## Anti-slop constraints

        Reject the cut when it contains any of the following:

        - generic gradient blobs unrelated to the product;
        - constant zooming used to fake energy;
        - a new transition style on every cut;
        - every word animated independently without hierarchy;
        - floating glass cards with no spatial logic;
        - illegible microcopy used as texture;
        - fake dashboards, fabricated metrics, or invented testimonials;
        - identical spring settings everywhere;
        - no stillness, no contrast, and no visual reset;
        - a CTA that arrives after attention has already collapsed.

        ## Required final report

        Summarize the chosen concept, runtime, formats, component shortlist, real product proof shown, critical critique fixes, render checks, and remaining limitations. Do not declare completion without evidence from rendered frames or a rendered video.
    ''').strip() + "\n",

    "creative-strategy-storyboard/SKILL.md": dedent(r'''
        ---
        name: creative-strategy-storyboard
        description: Convert a product, audience, and campaign objective into a sharp advertising concept, message hierarchy, treatment, storyboard, beat map, and shot list before Remotion implementation begins.
        ---

        # Creative Strategy and Storyboard

        Use this skill before animation. A weak proposition rendered beautifully remains a weak advertisement.

        ## Extract the strategic core

        Read the product and answer, using evidence:

        1. Who is the viewer and what are they already trying to accomplish?
        2. What friction or missed opportunity exists before the product?
        3. What changes after the product appears?
        4. What can be shown rather than claimed?
        5. What single action should happen after the film?

        Reduce the message to one primary promise, up to three proof points, and one CTA. Everything else is optional.

        ## Write three opening hypotheses

        Develop three openings with distinct mechanisms:

        - **Outcome first:** begin on the result, then reveal how it happens.
        - **Tension first:** make the pain visible in one compressed visual idea.
        - **Pattern break:** use a surprising product-native behaviour or transformation.

        For each opening, define the first frame, first line, first motion event, first sound event, proof visible by second three, and likely failure mode.

        ## Advertising copy rules

        - Use concrete verbs and observable outcomes.
        - Avoid “revolutionary”, “seamless”, “next-generation”, “all-in-one”, and other unsupported air.
        - Do not narrate what the viewer can already see unless the voiceover adds meaning.
        - Keep on-screen copy shorter than the spoken idea.
        - Prefer one strong phrase per beat over a paragraph distributed across moving cards.
        - Preserve exact legal or product language when supplied.

        ## Treatment format

        The selected treatment must include:

        - concept title and logline;
        - emotional curve;
        - visual system;
        - motion thesis;
        - product-proof method;
        - typography strategy;
        - sound world;
        - colour and material system;
        - edit rhythm;
        - ending and CTA;
        - adaptation notes for vertical and square formats.

        ## Beat map rules

        Every beat has one communication job. If a beat has two unrelated jobs, split it. If two beats repeat the same job without escalation, combine them.

        Estimate reading time from actual text and reserve a stable hold. Fast entrances do not justify fast comprehension. Plan overlap between audio and visuals deliberately; do not let every event hit on the same frame.

        ## Storyboard expectations

        Produce keyframes at the opening, each major reveal, each transition hand-off, and the ending. Include foreground, midground, background, camera, crop, safe area, text hierarchy, and motion arrows. A storyboard panel must explain spatial logic, not merely list the next component.

        ## Deliverables

        Write `brief.md`, `directions.md`, `selected-treatment.md`, `beat-map.json`, `shot-list.csv`, `asset-manifest.md`, and `copy-lock.md`. Mark every unverified claim as prohibited.
    ''').strip() + "\n",

    "motion-art-director/SKILL.md": dedent(r'''
        ---
        name: motion-art-director
        description: Define and enforce a coherent motion language for a premium Remotion advertisement, including hierarchy, timing, easing, camera, depth, transitions, secondary motion, and visual restraint.
        ---

        # Motion Art Director

        Create a movement system before tuning individual keyframes.

        ## Motion hierarchy

        Classify motion into four levels:

        - **Narrative motion:** changes the meaning or advances the story.
        - **Camera motion:** changes viewpoint, scale, or spatial relationship.
        - **Interface motion:** demonstrates product behaviour.
        - **Secondary motion:** adds weight, material response, and continuity.

        Narrative and camera motion take priority. Secondary motion must never compete with the proof.

        ## Motion tokens

        Define named timing and easing tokens rather than scattering numbers. At minimum provide restrained, standard, emphatic, and exit timings; camera and UI easing; stagger ranges; overshoot limits; blur limits; depth levels; and transition overlap. Reuse tokens with controlled variation.

        ## Spatial continuity

        Track where objects come from and where they go. A card that exits right can motivate the next object arriving from the same trajectory. A circular control can become a mask, aperture, orbit, or logo. A highlighted region can expand into the next scene. Prefer transformation over replacement.

        ## Camera grammar

        Use the camera only when it changes understanding or emotional scale. Establish a virtual stage with consistent perspective and depth. Distinguish:

        - reveal push;
        - proof punch-in;
        - lateral discovery;
        - orbit or parallax reveal;
        - pullback resolution;
        - locked frame for authority.

        Avoid continuous drift. Stillness makes decisive movement feel expensive.

        ## Timing rules

        - Allocate an entrance, readable hold, and exit.
        - Offset related events to create causality; avoid everything moving on one beat.
        - Use anticipation sparingly and only when it improves weight or direction.
        - Keep high-frequency motion short and local.
        - Give major changes a visual reset before the next dense section.
        - Tune at the actual delivery frame rate.

        ## Transition rules

        Choose transitions based on a shared property: position, geometry, colour, texture, luminance, semantic object, or camera direction. A transition should carry information or preserve orientation. Remove any transition that exists only because it is available.

        ## Typography motion

        Animate phrases according to syntax and hierarchy. Do not apply per-character animation to every line. Large display type may carry the signature effect; supporting copy should enter with quieter motion. Preserve line breaks intentionally across formats.

        ## Review method

        Render contact sheets at beat boundaries and short frame sequences around every transition. Review silhouettes with the text temporarily hidden, then review typography with decorative layers hidden. Fix hierarchy before adding polish.
    ''').strip() + "\n",

    "product-ui-cinematography/SKILL.md": dedent(r'''
        ---
        name: product-ui-cinematography
        description: Turn a real web or app interface into cinematic, truthful, and readable Remotion product shots using controlled capture, layer isolation, cursor choreography, camera moves, semantic highlights, and responsive reframing.
        ---

        # Product UI Cinematography

        The interface is evidence, not background decoration. Preserve truth while directing attention.

        ## Source hierarchy

        Prefer sources in this order:

        1. a runnable application with stable seeded data;
        2. exported design frames or high-resolution product screenshots;
        3. approved product mockups;
        4. a reconstructed interface only when explicitly marked and verified.

        Never fabricate a capability. Record the source and state used for each shot.

        ## Capture preparation

        Stabilize the product before capture: fixed viewport, deterministic data, disabled notifications, hidden personal information, loaded fonts, consistent theme, and controlled network state. Capture at higher resolution than delivery when camera movement or cropping is planned.

        ## Shot construction

        Build a shot around one proof. Use one or more of these methods:

        - isolate the relevant panel while retaining enough context;
        - use a restrained camera move to discover the proof;
        - dim or defocus irrelevant layers rather than shrinking everything;
        - promote a real UI element into the foreground while preserving its relationship to the interface;
        - use masks, depth, parallax, and reflections to establish materiality;
        - animate state changes at their true location instead of cutting to disconnected callouts.

        ## Cursor choreography

        The cursor is an actor. Give it a start position, intent, acceleration, target acquisition, click response, and exit. Do not teleport it between actions. Avoid showing the cursor when the product action is already self-explanatory.

        ## Camera and crop

        Keep important controls away from unsafe edges. For vertical adaptations, recompose the UI rather than scaling a desktop screen until it becomes unreadable. Use semantic crops, stacked regions, or a planned alternate camera path.

        ## Readability

        Verify the smallest important text at final delivery size. Decorative microcopy may be simplified, but never alter critical product copy. Use magnification only where the viewer needs it, and restore context after the detail shot.

        ## Required shot log

        For every product shot, record source state, viewport, capture file, proof shown, crop, camera path, cursor path, overlays, and whether any UI was reconstructed. Include a final product-truth review before render.
    ''').strip() + "\n",

    "remocn-component-curator/SKILL.md": dedent(r'''
        ---
        name: remocn-component-curator
        description: Select and adapt Remocn components from the offline catalogue for a specific advertising beat without creating a random preset showcase. Use the catalogue metadata, source code, use and avoid signals, vibe, tier, duration, and dependencies.
        ---

        # Remocn Component Curator

        Read `02_REMOCN_COMPONENT_LIBRARY/_INDEX/ALL_COMPONENTS.json` before choosing components. Inspect the source of every shortlisted component.

        ## Selection method

        For each beat, state the communication job, dominant object, available duration, motion role, visual tone, and transition requirement. Filter components using category, use signal, avoid signal, natural length, vibe, tier, dependencies, and format constraints.

        Return no more than three candidates per role. For each candidate explain:

        - why it supports the beat;
        - what could make it look generic;
        - what brand tokens must replace defaults;
        - whether its natural duration fits;
        - dependency and performance implications;
        - how it will hand off to the next shot.

        ## Restraint rules

        - Use one signature device per scene and quieter support motion around it.
        - Reuse a component family when repetition builds identity.
        - Do not use a component merely because it is visually impressive in isolation.
        - Do not combine two components that fight for the same focal role.
        - Prefer editing the component source over wrapping it in compensating hacks.
        - Preserve deterministic behaviour and inspect any randomization.

        ## Adaptation checklist

        Replace fonts, colours, radii, shadows, blur, spacing, easing, duration, and content. Remove demo-only decoration. Validate clipping and safe areas in every target aspect ratio. Confirm that the component still communicates when paused at its hold frame.

        ## Output

        Write `component-plan.md` with selected components, rejected alternatives, modifications, ownership of each timing range, and source paths. A component list without reasons is not an acceptable output.
    ''').strip() + "\n",

    "sound-design-editor/SKILL.md": dedent(r'''
        ---
        name: sound-design-editor
        description: Design editorial rhythm, music structure, voiceover timing, impacts, whooshes, UI detail, ambience, silence, and a controlled final mix for a Remotion product advertisement.
        ---

        # Sound Design and Edit

        Sound must clarify structure and add physical consequence. It must not become a pile of identical whooshes attached to every movement.

        ## Build the audio architecture

        Define music sections, voiceover phrases, major narrative hits, product interaction details, transition sounds, ambience, and intentional silence. Map them to frames in `audio-cue-sheet.csv`.

        ## Editorial rhythm

        Cut to musical structure when it supports the message, but allow visual anticipation and follow-through around the beat. Major events may land exactly; secondary events should often lead or trail. Avoid placing text entrance, camera stop, impact, and voice emphasis on every same frame.

        ## Sound hierarchy

        1. intelligible voice or critical product audio;
        2. narrative impacts and transitions;
        3. UI details;
        4. music;
        5. ambience and texture.

        When layers compete, remove rather than simply lower everything.

        ## Design rules

        - Give repeated UI actions a related sound family with small variation.
        - Reserve low-frequency weight for major structural events.
        - Use high-frequency detail for precision, not constant sparkle.
        - Match sound duration and material to motion weight.
        - Let silence frame the strongest reveal or CTA when appropriate.
        - Do not use copyrighted music or unlicensed samples in deliverables.

        ## Voiceover synchronization

        Align visuals to semantic phrases, not merely word timestamps. The proof should appear at or just before the phrase that names its value. Preserve breathing room and do not force the speaker into an unnatural cadence to satisfy animation.

        ## Mix and validation

        Prevent clipping, check mono compatibility, listen on headphones and small speakers, and validate the target platform's current loudness requirements. Keep editable stems or clearly separated source files. Report music, voice, effects, ambience, and master paths in the delivery manifest.
    ''').strip() + "\n",

    "production-ad-critic/SKILL.md": dedent(r'''
        ---
        name: production-ad-critic
        description: Independently review a rendered Remotion advertisement with an uncompromising production rubric. Produce timestamped defects, severity, evidence, exact fixes, and a score. Block completion below 90/100 or whenever a critical failure remains.
        ---

        # Production Ad Critic

        Review the rendered result, not the author's intentions. Do not reward complexity, effort, or the number of components used.

        ## Evidence required

        Inspect the full render at normal speed, muted, audio-only, and at least once at reduced speed. Review contact sheets and frames around every transition. Check each target aspect ratio at its real display size.

        ## Scoring rubric

        - Strategic clarity and product truth: 15
        - Opening and retention: 10
        - Visual hierarchy and composition: 10
        - Motion grammar and continuity: 15
        - Product demonstration clarity: 15
        - Edit rhythm and pacing: 10
        - Typography and copy: 10
        - Sound design and mix: 10
        - Technical polish and delivery readiness: 5

        Total: 100. Passing threshold: 90.

        ## Critical failures

        Any critical failure blocks completion regardless of score:

        - invented or misleading product claim;
        - unreadable primary message or CTA;
        - broken asset, missing font, clipping, black frame, or render artifact;
        - product action cannot be understood;
        - severe audio clipping or missing required audio;
        - unsafe crop in a required format;
        - legal copy omitted or altered;
        - transition that destroys orientation at a key proof moment;
        - obvious template residue that conflicts with the brand.

        ## Review dimensions

        Ask whether the first frame is intentional, the first three seconds earn attention, each beat has one job, the product appears soon enough, visual density breathes, motion has hierarchy, camera moves are motivated, text holds are readable, transitions share logic, sound reinforces structure, and the CTA resolves the film.

        Flag generic AI-video symptoms: random gradient atmospheres, excessive glass cards, constant micro-motion, uniform springiness, meaningless parallax, decorative tiny text, overused blur, unrelated transition styles, and a film that could advertise any product after changing the logo.

        ## Defect format

        For every issue write:

        ```text
        [SEVERITY] 00:07.12–00:08.03 — concise defect title
        Evidence: what is visible or audible.
        Why it matters: comprehension, hierarchy, brand, rhythm, or technical risk.
        Exact fix: concrete layout, timing, copy, motion, sound, or code change.
        Verification: what to inspect after the fix.
        ```

        Severity is critical, major, moderate, or minor.

        ## Final verdict

        Return the score table, critical failures, top five fixes by leverage, timestamps requiring rerender, and pass or fail. Never return “looks good” without evidence. Rerun after fixes; do not carry forward the previous score automatically.
    ''').strip() + "\n",

    "render-qa-engineer/SKILL.md": dedent(r'''
        ---
        name: render-qa-engineer
        description: Validate a Remotion production for deterministic rendering, correct assets and fonts, frame-safe layouts, performance, audio, responsive compositions, smoke renders, final renders, checksums, and reproducible delivery.
        ---

        # Render QA Engineer

        Treat the render pipeline as production software.

        ## Determinism

        Search for CSS animations and transitions, `Date.now`, timers, browser-only mutable state, network calls during render, and unseeded randomness. Use frame-derived values and seeded randomness. Ensure asynchronous assets use supported Remotion loading patterns and cannot race the renderer.

        ## Source checks

        Run type checking, linting, and tests. Validate composition IDs, dimensions, frame rates, durations, schemas, and default props. Confirm all `staticFile` paths, fonts, images, videos, audio files, and JSON assets exist with correct casing.

        ## Visual checks

        Render stills at frame zero, every beat boundary, every transition midpoint, the final frame, and additional frames where masks or camera movement reach extremes. Check clipping, z-order, aliasing, transparency, blur edges, shadows, colour banding, safe areas, and text wrapping.

        Validate each required aspect ratio independently. Do not assume a scaled 16:9 composition is a valid 9:16 composition.

        ## Motion checks

        Inspect frame sequences around cuts for flashes, duplicate frames, discontinuities, accidental easing resets, cursor teleportation, and elements that disappear before their exit completes. Confirm readable holds at delivery speed.

        ## Audio checks

        Verify sample rate compatibility, start offsets, fades, missing files, clipping, channel balance, and duration alignment. Render an audio-inclusive smoke segment before the full film.

        ## Performance checks

        Identify unnecessary full-frame blur, oversized images, unbounded particle counts, excessive DOM nodes, expensive shader resolution, and repeated decoding. Optimize without changing the approved look. Record renderer, concurrency, and environment.

        ## Reproducible delivery

        Produce exact render commands, source commit, dependency lockfile, environment notes, output dimensions, codec, pixel format, frame rate, audio settings, file size, SHA-256 checksum, and creation time. Keep a low-resolution review render separate from masters.

        ## Pass conditions

        Pass only when source checks succeed, smoke renders succeed, all required formats have safe-area evidence, no critical visual or audio defect remains, and the final files match the delivery manifest.
    ''').strip() + "\n",
}


BLUEPRINT_FILES: dict[str, str] = {
    "README.md": dedent(r'''
        # Production blueprints

        These files are working templates, not reading material. Copy them into the advertisement repository and fill them before the final animation pass.

        The recommended order is master prompt → creative brief → treatment and beat map → shot list → audio cue sheet → QA scorecard → iteration protocol → delivery checklist.
    ''').strip() + "\n",

    "01_MASTER_PROMPT_EN.md": dedent(r'''
        # Codex master prompt — premium product advertisement

        Build a production-grade Remotion advertisement for this project. First inspect the entire repository and the runnable product. Do not animate immediately.

        Use the installed skills in this order: `creative-strategy-storyboard`, `production-ad-director`, `remocn-component-curator`, `motion-art-director`, `product-ui-cinematography`, `sound-design-editor`, `production-ad-critic`, and `render-qa-engineer`.

        Requirements:

        1. Establish product truth, audience, primary promise, strongest proof, CTA, brand tokens, available assets, and prohibited unverified claims.
        2. Produce three genuinely different opening directions for the first three seconds. Select one with written reasoning.
        3. Write a treatment, frame-accurate beat map, shot list, asset manifest, copy lock, and audio cue sheet before polishing animation.
        4. Read the offline Remocn catalogue at `02_REMOCN_COMPONENT_LIBRARY/_INDEX/ALL_COMPONENTS.json`. Select a restrained component vocabulary. Explain why each component is used and how it will be reworked for this brand.
        5. Use real product states and real interface behaviour. Never fabricate features, users, metrics, awards, testimonials, or integrations.
        6. Build in passes: animatic, product proof, art direction, motion, sound, responsive adaptations, critique, and render QA.
        7. Keep all animation deterministic and frame-driven. No CSS animation, wall-clock timing, unseeded randomness, or render-time network dependency.
        8. Make the film feel authored: one visual thesis, motivated camera, clear hierarchy, readable holds, intentional stillness, coherent transitions, and sound with restraint.
        9. Render and inspect evidence. Create contact sheets and timestamped critique. Do not call the work finished below 90/100 or while a critical defect remains.
        10. Deliver the requested aspect ratios with a reproducible render manifest and checksums.

        Avoid generic AI-advertising residue: unrelated gradient blobs, endless glass cards, constant zoom, identical springs, tiny decorative text, arbitrary transition changes, empty “future of X” copy, and a film that could fit another product after replacing the logo.

        Begin by writing the product-truth report and the three opening directions. Do not begin final animation until those are approved by your own independent critic pass.
    ''').strip() + "\n",

    "02_MASTER_PROMPT_RU.md": dedent(r'''
        # Мастер-промпт для Codex — production-реклама продукта

        Собери production-grade рекламу этого проекта на Remotion. Сначала полностью изучи репозиторий и запусти настоящий продукт. Не начинай сразу пукать анимациями.

        Используй скиллы по порядку: `creative-strategy-storyboard`, `production-ad-director`, `remocn-component-curator`, `motion-art-director`, `product-ui-cinematography`, `sound-design-editor`, `production-ad-critic`, `render-qa-engineer`.

        Обязательные требования:

        1. Зафиксируй реальную ценность продукта, аудиторию, главное обещание, сильнейшее доказательство, CTA, бренд-токены, доступные ассеты и все неподтверждённые утверждения, которые запрещено выдумывать.
        2. Сделай три действительно разных концепта первых трёх секунд. Выбери один и письменно объясни решение.
        3. До полировки создай treatment, покадровую beat map, shot list, asset manifest, утверждённый текст и audio cue sheet.
        4. Прочитай офлайн-каталог `02_REMOCN_COMPONENT_LIBRARY/_INDEX/ALL_COMPONENTS.json`. Выбери маленький и связный набор компонентов. Для каждого объясни задачу и то, как он будет переделан под бренд.
        5. Показывай настоящие состояния и поведение продукта. Не выдумывай функции, пользователей, цифры, награды, отзывы и интеграции.
        6. Работай проходами: animatic, product proof, art direction, motion, sound, адаптации форматов, независимая критика и render QA.
        7. Вся анимация должна быть детерминированной и зависеть от кадра. Никаких CSS-анимаций, системного времени, случайности без seed и сетевых запросов во время рендера.
        8. Ролик должен ощущаться авторским: одна визуальная идея, мотивированная камера, ясная иерархия, читаемые паузы, тишина и неподвижность там, где они усиливают акцент, единая логика переходов и аккуратный звук.
        9. Сделай реальные рендеры и проверь их. Создай contact sheets и критику с таймкодами. Не объявляй работу готовой при оценке ниже 90/100 или пока остаётся критический дефект.
        10. Отдай нужные соотношения сторон с воспроизводимой командой рендера, manifest и SHA-256.

        Запрещён типичный ИИ-шлак: случайные градиентные облака, бесконечные стеклянные карточки, постоянный зум, одинаковые пружины, декоративный микротекст, новый переход на каждом склеивании, пустые слова про «будущее» и ролик, которому можно заменить логотип — и он станет рекламой любого другого продукта.

        Начни с отчёта о реальном продукте и трёх концептов открытия. Финальную анимацию не начинай, пока независимый critic-проход не подтвердит выбранное направление.
    ''').strip() + "\n",

    "03_CREATIVE_BRIEF.md": dedent(r'''
        # Creative brief

        ## Campaign objective
        <!-- One measurable communication objective. -->

        ## Audience and viewing context

        ## Primary promise

        ## Strongest visible proof

        ## Supporting proof points
        1.
        2.
        3.

        ## Primary CTA

        ## Verified claims

        ## Prohibited or unverified claims

        ## Product states available for capture

        ## Brand assets and tokens

        ## Required duration and formats

        ## Platform, sound-on/sound-off, caption, and legal constraints

        ## Success test
        <!-- What must a cold viewer understand after one watch? -->
    ''').strip() + "\n",

    "04_TREATMENT_AND_BEAT_MAP.md": dedent(r'''
        # Treatment and beat map

        ## Concept title and logline

        ## Emotional curve

        ## Visual thesis

        ## Motion thesis

        ## Product-proof method

        ## Typography system

        ## Sound world

        ## Ending and CTA

        ## Beat table

        | Beat | Frames | Communication job | Dominant visual | Product truth | Entry | Hold | Exit | Camera | Copy | Audio | Handoff |
        |---|---:|---|---|---|---|---|---|---|---|---|---|
        | 01 | 0– | | | | | | | | | | |
    ''').strip() + "\n",

    "05_SHOT_LIST.csv": "shot_id,start_frame,end_frame,beat,purpose,source_state,capture_asset,composition,camera,cursor,text,audio,transition,format_notes,status\nS01,0,0,hook,,,,,,,,,,,planned\n",

    "06_AUDIO_CUE_SHEET.csv": "cue_id,start_frame,end_frame,layer,description,source_file,fade_in_frames,fade_out_frames,priority,notes\nA01,0,0,music,,,,,4,\n",

    "07_QA_SCORECARD.md": dedent(r'''
        # QA scorecard

        | Dimension | Weight | Score | Evidence | Required fix |
        |---|---:|---:|---|---|
        | Strategic clarity and product truth | 15 | | | |
        | Opening and retention | 10 | | | |
        | Visual hierarchy and composition | 10 | | | |
        | Motion grammar and continuity | 15 | | | |
        | Product demonstration clarity | 15 | | | |
        | Edit rhythm and pacing | 10 | | | |
        | Typography and copy | 10 | | | |
        | Sound design and mix | 10 | | | |
        | Technical polish and delivery readiness | 5 | | | |
        | **Total** | **100** | | | |

        Passing threshold: 90/100 and zero critical failures.

        ## Critical failures

        ## Timestamped defects

        ## Top five changes by leverage

        ## Verdict
    ''').strip() + "\n",

    "08_ITERATION_PROTOCOL.md": dedent(r'''
        # Iteration protocol

        1. Freeze product truth and copy before surface polish.
        2. Compare three opening variants using the same product promise.
        3. Lock the beat map after the animatic passes comprehension and pacing.
        4. Add real product proof before decorative treatments.
        5. Perform separate composition, motion, typography, product-truth, sound, and technical reviews.
        6. Group fixes by root cause rather than patching symptoms frame by frame.
        7. After every major change, rerender the affected range and its incoming and outgoing transition.
        8. Run an independent critic pass with no implementation explanation.
        9. Record accepted trade-offs and rejected feedback.
        10. Finalize only after the full render, all format variants, and the delivery manifest pass.
    ''').strip() + "\n",

    "09_DELIVERY_CHECKLIST.md": dedent(r'''
        # Delivery checklist

        - [ ] Product claims verified
        - [ ] Copy lock approved
        - [ ] Required legal copy present
        - [ ] 16:9 master rendered and reviewed
        - [ ] 9:16 adaptation recomposed and reviewed
        - [ ] 1:1 adaptation recomposed and reviewed when required
        - [ ] Captions and sound-off comprehension checked
        - [ ] Fonts and licences archived
        - [ ] Music and SFX licences archived
        - [ ] No missing, low-resolution, or temporary assets
        - [ ] Contact sheet reviewed
        - [ ] Transition boundary frames reviewed
        - [ ] Audio checked on headphones and small speakers
        - [ ] No clipping or unintended silence
        - [ ] Typecheck, lint, tests, and smoke render pass
        - [ ] Final critic score at least 90 with zero critical failures
        - [ ] Render commands recorded
        - [ ] Source commit recorded
        - [ ] SHA-256 checksums generated
        - [ ] Review files and masters clearly separated
    ''').strip() + "\n",

    "10_MOTION_TOKENS.ts": dedent(r'''
        import {Easing, spring, type SpringConfig} from 'remotion';

        export const MOTION = {
          duration: {
            micro: 8,
            restrained: 14,
            standard: 22,
            emphatic: 34,
            camera: 42,
          },
          stagger: {
            tight: 1,
            standard: 2,
            relaxed: 4,
          },
          blur: {
            subtle: 6,
            standard: 12,
            heavy: 24,
          },
          depth: {
            foreground: 1.08,
            stage: 1,
            background: 0.94,
          },
          easing: {
            enter: Easing.bezier(0.22, 1, 0.36, 1),
            exit: Easing.bezier(0.4, 0, 1, 1),
            camera: Easing.bezier(0.16, 1, 0.3, 1),
            ui: Easing.bezier(0.2, 0.8, 0.2, 1),
          },
        } as const;

        export const SPRINGS: Record<string, SpringConfig> = {
          restrained: {damping: 24, stiffness: 170, mass: 1},
          standard: {damping: 18, stiffness: 150, mass: 0.9},
          emphatic: {damping: 14, stiffness: 180, mass: 0.8},
        };

        export const resolvedSpring = ({
          frame,
          fps,
          preset = 'standard',
        }: {
          frame: number;
          fps: number;
          preset?: keyof typeof SPRINGS;
        }) => spring({frame, fps, config: SPRINGS[preset]});
    ''').strip() + "\n",

    "11_BEAT_MAP.schema.json": dedent(r'''
        {
          "$schema": "https://json-schema.org/draft/2020-12/schema",
          "title": "Remotion production advertisement beat map",
          "type": "object",
          "required": ["fps", "durationInFrames", "beats"],
          "properties": {
            "fps": {"type": "number", "exclusiveMinimum": 0},
            "durationInFrames": {"type": "integer", "minimum": 1},
            "beats": {
              "type": "array",
              "minItems": 1,
              "items": {
                "type": "object",
                "required": ["id", "startFrame", "endFrame", "job", "dominantVisual", "entry", "hold", "exit", "handoff"],
                "properties": {
                  "id": {"type": "string"},
                  "startFrame": {"type": "integer", "minimum": 0},
                  "endFrame": {"type": "integer", "minimum": 1},
                  "job": {"type": "string"},
                  "dominantVisual": {"type": "string"},
                  "productTruth": {"type": "string"},
                  "entry": {"type": "string"},
                  "hold": {"type": "string"},
                  "exit": {"type": "string"},
                  "camera": {"type": "string"},
                  "copy": {"type": "string"},
                  "audio": {"type": "string"},
                  "handoff": {"type": "string"},
                  "components": {"type": "array", "items": {"type": "string"}}
                }
              }
            }
          }
        }
    ''').strip() + "\n",

    "12_REFERENCE_DECONSTRUCTION.md": dedent(r'''
        # Reference deconstruction worksheet

        Do not copy surface style. Extract the underlying decisions.

        ## Reference

        ## First-frame promise

        ## What changes by second three

        ## Shot and beat structure

        ## Dominant geometry

        ## Motion thesis

        ## Camera grammar

        ## Typography hierarchy

        ## Transition logic

        ## Product-proof technique

        ## Rhythm and sound events

        ## Deliberate stillness

        ## What would become generic if copied directly

        ## Transferable principle for this product
    ''').strip() + "\n",

    "13_AGENTS.md": dedent(r'''
        # AGENTS.md — Remotion production rules

        For any product advertisement or launch film, read the project skills before editing code. Product truth, creative direction, beat map, component plan, and asset manifest must exist before the final animation pass.

        Use the official Remotion skills for implementation correctness and the custom production stack for direction and review. Read the offline Remocn index before selecting components. Keep the chosen component vocabulary restrained and modify it to match the brand.

        Never invent product claims or interface behaviour. Keep all animation deterministic and frame-driven. Render evidence, create timestamped critique, and block completion below 90/100 or while a critical defect remains.
    ''').strip() + "\n",
}

# Personal Website — Style Guide for Subpages

Use this document so a subpage (built in a different repo) visually and behaviorally matches the main personal site (harishchandran.com). Implement the same design tokens, typography, spacing, and component patterns below.

---

## 1. Design Tokens (Single Source of Truth)

All brand colors are controlled by **three CSS variables** in `:root`. Use these so changing the main site updates the subpage too.

### 1.1 Master color variables (HSL components, no `hsl()`)

Define in your global CSS (e.g. `globals.css` or Tailwind theme):

```css
:root {
  /* Primary, secondary, and background — edit only these to retheme */
  --color-primary: 60 3% 8%;           /* dark, warm black (text/accents) */
  --color-secondary: 210 15% 35%;     /* neutral slate (surfaces/code blocks) */
  --color-background: 50 17% 93%;    /* warm off-white (page background) */
}
```

- **Primary**: Main text color and primary accents (links, buttons, borders, focus ring).
- **Secondary**: Slightly darker than background; used for code blocks, muted surfaces, hover contrast.
- **Background**: Page and card backgrounds; keep consistent so the subpage feels like the same site.

### 1.2 Derived theme variables

Map the three master variables into a full palette. Use **HSL components only** in variables (e.g. `60 3% 8%`), then wrap with `hsl(var(--name))` where you apply them:

```css
:root {
  --background: var(--color-background);
  --foreground: var(--color-primary);
  --primary: var(--color-primary);
  --primary-foreground: 158 32% 27%;   /* dark, for text on primary bg */
  --secondary: var(--color-secondary);
  --secondary-foreground: 210 20% 96%;
  --muted: 217 25% 15%;
  --muted-foreground: 215 16% 70%;
  --border: 217 19% 24%;
  --accent: var(--color-primary);
  --ring: var(--color-primary);
}
```

**Light theme** (if you support a `.light` class):

```css
.light {
  --background: 210 20% 98%;
  --foreground: var(--color-primary);
  --muted: 210 30% 96%;
  --muted-foreground: 217 15% 35%;
  --border: 220 13% 85%;
  --primary: var(--color-primary);
  --secondary: var(--color-secondary);
  /* ... rest mirror structure, with lighter neutrals */
}
```

### 1.3 Tailwind color mapping

In `tailwind.config.ts` (or equivalent), map theme colors to these variables so you can use `bg-background`, `text-foreground`, `text-muted-foreground`, `border-border`, etc.:

```ts
colors: {
  background: "hsl(var(--background))",
  foreground: "hsl(var(--foreground))",
  primary: "hsl(var(--primary))",
  "primary-foreground": "hsl(var(--primary-foreground))",
  secondary: "hsl(var(--secondary))",
  "secondary-foreground": "hsl(var(--secondary-foreground))",
  muted: "hsl(var(--muted))",
  "muted-foreground": "hsl(var(--muted-foreground))",
  border: "hsl(var(--border))",
  accent: "hsl(var(--accent))",
  ring: "hsl(var(--ring))",
}
```

---

## 2. Typography

### 2.1 Fonts

- **Headings**: **Stack Sans Notch** — variable `--font-stack-sans-notch`. Weights: 400 (Regular), 700 (Bold). Use for all `h1`–`h6`.
- **Body / UI**: **Vend Sans** — variable `--font-vend-sans`. Weights: 400 (Regular), 500 (Medium). Use for body text, buttons, labels.

If the subpage cannot load the same font files, use a similar pairing: a slightly characterful sans for headings and a clean sans for body (e.g. system-ui or a Google font equivalent). The important part is **heading vs body** distinction and **same color/size/weight** rules below.

### 2.2 Font application

- **Body**: `font-family: var(--font-vend-sans), sans-serif` (or Tailwind `font-sans` if mapped).
- **Headings**: `font-family: var(--font-stack-sans-notch), sans-serif` (or `font-heading`).
- **Base body**: `color: hsl(var(--foreground));` (or `text-foreground`). Antialiasing: `-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;`.

### 2.3 Scale and weight

| Element              | Size        | Weight   | Line height   | Color              |
|----------------------|------------|----------|---------------|--------------------|
| Page title (h1)      | 3rem–6rem (responsive) | Bold (700) | default       | `foreground`       |
| Section title (h2)   | 1.5rem–2xl | Semibold (600) | default | `foreground`       |
| Body / prose         | 1rem (base), 1.125rem (text-lg) | Normal (400) | 1.625–1.9   | `muted-foreground` |
| Prose headings       | —          | 600      | —             | `foreground`       |
| Small / meta         | 0.875rem   | Normal   | —             | `muted-foreground` |
| Inline code          | 0.875rem   | —        | —             | `primary` on `secondary` bg |

- Heading letter-spacing: `-0.025em`.
- Prose: `max-width: none` if full-width; otherwise constrain with something like `max-w-3xl` for readability.

---

## 3. Layout and spacing

- **Page background**: `background-color: hsl(var(--background));`. Optional subtle texture (e.g. radial dot grid) at low opacity.
- **Content width**: `max-w-3xl` (48rem) centered with `mx-auto` for articles and main content.
- **Page padding**: `pt-32 pb-24 px-4` (top padding for fixed hero, bottom for breathing room, horizontal for mobile).
- **Section spacing**: `space-y-6` or `space-y-7` between paragraphs; `space-y-4` between cards or list items; `mb-8` after page title, `mt-10` or `mt-16` before next major block.
- **Grid overlay** (optional): `bg-grid-dot bg-[size:40px_40px] opacity-20` as a decorative layer behind content.

---

## 4. Links

- **Default**: `color: hsl(var(--primary));` (same as foreground on this site).
- **Hover**: `color: hsl(var(--accent));` (same as primary here).
- **Transition**: `transition: color 200ms cubic-bezier(0.4, 0, 0.2, 1);`
- **Focus (a11y)**: `outline: 2px solid transparent; outline-offset: 2px; box-shadow: 0 0 0 2px hsl(var(--background)), 0 0 0 4px hsl(var(--ring));`

---

## 5. Prose (long-form content)

- **Container**: `prose prose-invert max-w-none` (or your equivalent). Prose text color: `muted-foreground`; headings: `foreground`, font-heading, weight 600.
- **Paragraphs**: `text-lg leading-relaxed` or `leading-[1.9]`, `text-muted-foreground`.
- **Code inline**: `background: hsl(var(--secondary)); color: hsl(var(--primary)); padding: 0.125rem 0.375rem; border-radius: 0.25rem; font-size: 0.875rem;` monospace.
- **Code block**: `background: hsl(var(--secondary) / 0.7); border: 1px solid hsl(var(--border)); border-radius: 0.75rem; padding: 1rem;` and light shadow using `hsl(var(--primary) / 0.1)`.
- **Selection**: `background: hsl(var(--primary) / 0.6); color: hsl(var(--primary-foreground));`

---

## 6. Inline badges (manifesto-style links)

Used for inline links that should look like subtle “chips” (e.g. “Duke”, “Altruato”, “chess”) so they match the surrounding text but are clearly tappable.

- **Container**: Inline-flex, baseline-aligned with surrounding text. Padding: `px-1.5 py-0`. Border: **2px dotted** in muted-foreground; background: same as page (`background`). Border radius: `rounded-md`.
- **Text**: Same as body: `text-muted-foreground`, `text-lg`, `leading-relaxed`, no extra font-weight.
- **Border color**: `hsl(var(--muted-foreground))` so it doesn’t overpower the text.
- **Alignment**: `inline-flex items-center align-baseline` so the whole badge (icon + text) sits on the same baseline as the line. For image icons (e.g. logos), use `align-middle` and a tiny nudge (e.g. `relative top-[1px]`) if they sit high; Lucide icons: `h-4 w-4 align-middle`.
- **Hover**: Slight scale (e.g. 1.05) is optional; no color change so the badge stays seamless with the paragraph.

Example Tailwind-style classes for the badge anchor:

`inline-flex items-center align-baseline gap-1.5 px-1.5 py-0 rounded-md border-2 border-dotted border-[hsl(var(--muted-foreground))] bg-background text-muted-foreground text-lg leading-relaxed transition-all`

---

## 7. Cards / list items (e.g. thought previews)

- **Container**: `rounded-xl border border-border bg-muted/30 p-6 transition-colors hover:border-primary/70`.
- **Meta line**: `text-primary`, `text-sm font-medium uppercase tracking-wide`, with optional icon (e.g. `h-5 w-5`).
- **Title**: `text-2xl font-semibold text-foreground`.
- **Excerpt / description**: `text-muted-foreground`, `mt-2`.
- **Footer line** (e.g. date, read time): `text-sm text-muted-foreground`, `mt-3`.

---

## 8. Primary buttons (“cube” style)

The main site uses a 3D “cube” button. If the subpage shares the same CSS bundle, you can reuse the same markup and classes. Otherwise, for a simpler match:

- **Visual**: Solid background in **primary** color, text in **background** (or primary-foreground if you need contrast). Border or shadow optional; keep it minimal.
- **Typography**: Bold, letter-spacing ~0.1em, font-sans (Vend Sans), ~17px.
- **Hover**: Slight darkening or invert (e.g. background → background color, text → primary) so it feels like the cube’s “pressed” state.
- **Focus**: Same ring as links: `ring: hsl(var(--ring))`, offset so it’s visible.

If you do implement the full cube: the outer “faces” use `primary`, the inner fill uses `background`; on hover the inner becomes `primary` and the text becomes `background`. All borders/edges stay primary on hover.

---

## 9. Transitions and motion

- **Links / interactive text**: 200ms color transition, ease as above.
- **Buttons / badges**: `transition-all`; hover scale around 1.05, tap 0.98 if desired.
- **Reduced motion**: Respect `prefers-reduced-motion: no-preference` before applying scale or decorative motion.

---

## 10. Summary checklist for the subpage

- [ ] Define `--color-primary`, `--color-secondary`, `--color-background` and derive `--foreground`, `--primary`, `--muted-foreground`, `--border`, `--background`, etc.
- [ ] Map Tailwind (or your utility system) to these variables (e.g. `bg-background`, `text-foreground`, `text-muted-foreground`, `border-border`).
- [ ] Use Stack Sans Notch for headings and Vend Sans for body (or close equivalents); same sizes and weights as above.
- [ ] Body text and prose use `muted-foreground`; headings use `foreground`.
- [ ] Links use `primary`/`accent` and the same focus ring.
- [ ] Inline badges: dotted border (muted-foreground), background color, baseline-aligned, same font size/weight as body.
- [ ] Cards: `border-border`, `bg-muted/30`, `hover:border-primary/70`, rounded-xl, same typography hierarchy.
- [ ] Page: `bg-background`, `max-w-3xl` content, `pt-32 pb-24 px-4`, optional grid overlay.
- [ ] Buttons: primary-colored, bold, with clear focus and optional hover state that matches the main site’s cube behavior.

Using this guide, the subpage will share the same two-toned, minimal aesthetic and feel like a continuous part of the personal website.

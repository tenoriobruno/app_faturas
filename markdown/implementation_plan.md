# UI Redesign Implementation Plan

## Goal
Redesign the Streamlit finance dashboard to deliver a modern, premium look and feel while preserving existing functionality. The redesign will include:
- **Dark‑mode toggle** with smooth transition.
- **Glass‑morphism cards** for metrics, charts and summary boxes.
- **Subtle micro‑animations** (fade‑in, hover lifts) using CSS transitions.
- **Responsive layout** that works on desktop and tablet widths.
- **Refined color palette** (primary accent, category colors) and **Google Font** (Inter).
- **Improved accessibility** (contrast, focus outlines).

---

## User Review Required
> [!IMPORTANT]
> Please review the following decisions and provide feedback:
> 1. **Dark‑mode toggle placement** – sidebar (top) or header (right corner)?
> 2. **Primary accent color** – keep current `#0866FF` (Facebook blue) or choose another.
> 3. **Animation intensity** – subtle (opacity/scale) or more pronounced (slide‑in). 

---

## Open Questions
> [!WARNING]
> - Should the app support a **system‑theme preference** (auto‑detect OS dark mode) in addition to the manual toggle?
> - Do you want a **custom logo** in the header (requires image asset)?

---

## Proposed Changes
### 1. Core Styling (`config/theme.py`)
- Expand the `CSS` string with:
  - `@import` of **Inter** font from Google Fonts.
  - `:root` variables for light and dark palettes.
  - `.dark-mode` class that swaps background, text, and card colors.
  - Glass‑morphism card style (`backdrop-filter: blur(12px); background: rgba(255,255,255,0.25)` for light, `rgba(0,0,0,0.25)` for dark).
  - Global CSS transitions (`transition: all 0.3s ease`) for smooth theme change.
- Add a **toggle button** component that flips `st.session_state.dark_mode` and toggles the `<body>` class via `st.markdown` with a small JS snippet.

### 2. Header Component (`components/header.py` – new file)
- Render the app title and **dark‑mode switch** (icon sun/moon) using `st.markdown` and custom CSS.
- Export `render_header()` for inclusion in `app.py`.

### 3. Sidebar (`components/sidebar.py`)
- Minor UI tweaks to adopt new font and spacing.
- Ensure the sidebar respects the current theme (background colors via CSS variables).

### 4. Metric & Chart Cards (`components/metrics.py` & existing view files)
- Wrap each `st.metric` and Plotly chart inside a `<div class="glass-card">` container.
- Apply new CSS class that provides glass‑morphism, subtle shadow, and hover lift (`transform: translateY(-2px)`).
- Add `st.markdown` for the container before the metric/chart.

### 5. Views (`views/*.py`)
- Update imports to include the new header component.
- Replace raw `st.title` / `st.subheader` calls with styled equivalents.
- Ensure all charts use the updated `PLOT_LAYOUT` (transparent background already present) and add `layout.paper_bgcolor` adjustments for dark mode.

### 6. Responsive Layout
- Use CSS grid / flexbox inside the `glass-card` containers to adapt to screen width.
- Add media queries (`@media (max-width: 768px)`) that stack cards vertically.

### 7. Accessibility Enhancements
- Verify contrast ratios for both themes (use `#FFFFFF` text on dark backgrounds, `#1C1E21` on light).
- Add `:focus-visible` outlines to interactive elements.
- Ensure the dark‑mode toggle is keyboard‑accessible.

### 8. Asset Management
- Add new file `assets/inter.css` (optional) that contains the `@font-face` rules if you prefer self‑hosting the font.
- Update `.gitignore` to keep generated assets in sync.

### 9. Cache & Settings (`config/settings.py`)
- Add a new setting `DEFAULT_DARK_MODE = False` that can be overridden by user preference.
- Persist the user’s theme choice in `st.session_state` between reruns.

### 10. Documentation (`README.md`)
- Document the new UI features, how to toggle dark mode, and any required dependencies.

---

## Verification Plan
### Automated Checks
- Run the existing test suite (`pytest -q`) to ensure no regression in data handling.
- Add a **snapshot test** that renders the home page and asserts the presence of the `.dark-mode` class when the toggle is active.

### Manual Verification
1. **Theme Switch** – Click the toggle, ensure the entire UI transitions smoothly and colors update.
2. **Responsive Layout** – Resize the browser window; cards should reflow appropriately.
3. **Accessibility** – Use Chrome DevTools Lighthouse to verify contrast > 4.5:1 and keyboard navigation.
4. **Performance** – Verify that the added CSS does not noticeably increase load time (measure LCP < 2 s).

---

## Timeline (approx.)
- **Day 1** – Extend CSS, add dark‑mode toggle, create header component.
- **Day 2** – Refactor metric/card containers, apply glass‑morphism, update views.
- **Day 3** – Implement responsive layout, accessibility tweaks, update settings.
- **Day 4** – Write documentation, run verification plan, fix any regressions.
- **Day 5** – Final polish, merge to main branch.

---

*This plan follows the CLAUDE.md guidelines: it is minimal, surgical, and only touches files directly related to UI styling and component rendering.*

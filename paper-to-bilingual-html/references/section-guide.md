# Section Guide

Use this reference to add the optional ultrawide section navigator to a bilingual paper. Keep its code and interaction rules separate from the base layout in `output-format.md`.

## When to include it

- Include the navigator when the document has at least two real top-level sections.
- Render it only when the viewport is wider than `1400px`.
- Generate one guide item for each top-level section that actually exists in the HTML. Do not create placeholder links.
- Use concise English section names in the guide labels because the labels must remain compact.
- Give the corresponding `.heading-row` a stable `id`, for example `id="section-related-work"`.

## Interaction behavior

- Resting state: every section is a `32px × 1px` line at 16% black.
- Current section: keep the line at `32px`, set it to 48% black, and expose the state with `aria-current="location"`.
- Hovered or keyboard-focused item: line grows to approximately `77px`, becomes 82% black, and reveals its section label at `left: 104px`.
- First, second, and third neighbors grow to approximately `53px`, `42px`, and `36px`; their colors become progressively lighter.
- Use `transform: scaleX()` for line growth. Do not animate `width`.
- Use a short `180ms ease` transition. Do not add looping, entrance, or scroll-driven animation.
- Gate hover styles behind `(hover: hover) and (pointer: fine)`.
- Preserve `:focus-visible` behavior and disable transitions under `prefers-reduced-motion`.
- The navigator links jump to the corresponding section anchors; do not intercept normal anchor behavior with JavaScript.
- Use the script below only to observe which section has crossed the reading line and update `aria-current`. It must not animate or rewrite scroll position.

## HTML

Place the navigator immediately before `<article class="paper">`.

```html
<nav class="section-guide" aria-label="Paper sections">
  <a class="section-guide__link" href="#section-abstract" aria-label="Abstract">
    <span class="section-guide__line" aria-hidden="true"></span>
    <span class="section-guide__label" aria-hidden="true">Abstract</span>
  </a>
  <a class="section-guide__link" href="#section-introduction" aria-label="Introduction">
    <span class="section-guide__line" aria-hidden="true"></span>
    <span class="section-guide__label" aria-hidden="true">Introduction</span>
  </a>
  <!-- Repeat only for top-level sections that exist. -->
</nav>

<article class="paper">
  <div class="bilingual-row heading-row" id="section-abstract">
    <div class="col en"><h2>Abstract</h2></div>
    <div class="col zh"><h2>摘要</h2></div>
  </div>
</article>
```

## CSS

```css
.section-guide {
  display: none;
  position: fixed;
  z-index: 20;
  top: 50%;
  left: 80px;
  width: 167px;
  transform: translateY(-50%);
}
.section-guide__link {
  position: relative;
  display: flex;
  align-items: center;
  width: 167px;
  height: 17px;
  color: rgba(0, 0, 0, 0.16);
  text-decoration: none;
  outline: none;
}
.section-guide__line {
  display: block;
  width: 32px;
  height: 1px;
  background: currentColor;
  transform: scaleX(1);
  transform-origin: left center;
  transition: transform 180ms ease, color 180ms ease;
}
.section-guide__label {
  position: absolute;
  left: 104px;
  top: 50%;
  color: #000;
  font: 400 14px/1.2 "Geist", system-ui, sans-serif;
  white-space: nowrap;
  opacity: 0;
  transform: translateY(-50%);
  transition: opacity 140ms ease;
}
.section-guide__link[aria-current="location"] {
  color: rgba(0, 0, 0, 0.48);
}
.section-guide__link:focus-visible {
  color: rgba(0, 0, 0, 0.82);
}
.section-guide__link:focus-visible .section-guide__line {
  transform: scaleX(2.4);
}
.section-guide__link:focus-visible .section-guide__label {
  opacity: 1;
}

@media (min-width: 1401px) {
  .section-guide {
    display: flex;
    flex-direction: column;
  }
}

@media (hover: hover) and (pointer: fine) {
  .section-guide__link:hover {
    color: rgba(0, 0, 0, 0.82);
  }
  .section-guide__link:hover .section-guide__line {
    transform: scaleX(2.4);
  }
  .section-guide__link:hover .section-guide__label {
    opacity: 1;
  }

  .section-guide__link:has(+ .section-guide__link:hover),
  .section-guide__link:hover + .section-guide__link {
    color: rgba(0, 0, 0, 0.52);
  }
  .section-guide__link:has(+ .section-guide__link:hover) .section-guide__line,
  .section-guide__link:hover + .section-guide__link .section-guide__line {
    transform: scaleX(1.65);
  }

  .section-guide__link:has(+ .section-guide__link + .section-guide__link:hover),
  .section-guide__link:hover + .section-guide__link + .section-guide__link {
    color: rgba(0, 0, 0, 0.34);
  }
  .section-guide__link:has(+ .section-guide__link + .section-guide__link:hover) .section-guide__line,
  .section-guide__link:hover + .section-guide__link + .section-guide__link .section-guide__line {
    transform: scaleX(1.3);
  }

  .section-guide__link:has(+ .section-guide__link + .section-guide__link + .section-guide__link:hover),
  .section-guide__link:hover + .section-guide__link + .section-guide__link + .section-guide__link {
    color: rgba(0, 0, 0, 0.24);
  }
  .section-guide__link:has(+ .section-guide__link + .section-guide__link + .section-guide__link:hover) .section-guide__line,
  .section-guide__link:hover + .section-guide__link + .section-guide__link + .section-guide__link .section-guide__line {
    transform: scaleX(1.125);
  }
}

@media (prefers-reduced-motion: reduce) {
  .section-guide__line,
  .section-guide__label {
    transition: none;
  }
}

@media print {
  .section-guide {
    display: none;
  }
}
```

## Current-section script

Place this script after the page content, immediately before `</body>`. The reading line is 30% from the top of the viewport. The most recent top-level heading that crosses that line becomes current.

```html
<script>
(() => {
  const links = Array.from(document.querySelectorAll(".section-guide__link"));
  const sections = links
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);
  if (!links.length || !sections.length) return;

  const updateCurrentSection = () => {
    const readingLine = window.innerHeight * 0.3;
    let current = sections[0];
    for (const section of sections) {
      if (section.getBoundingClientRect().top <= readingLine) current = section;
      else break;
    }
    for (const link of links) {
      if (link.getAttribute("href") === "#" + current.id) {
        link.setAttribute("aria-current", "location");
      } else {
        link.removeAttribute("aria-current");
      }
    }
  };

  updateCurrentSection();
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(updateCurrentSection, {
      rootMargin: "0px 0px -70% 0px",
      threshold: 0,
    });
    sections.forEach((section) => observer.observe(section));
  } else {
    window.addEventListener("scroll", updateCurrentSection, { passive: true });
  }
  window.addEventListener("resize", updateCurrentSection, { passive: true });
  window.addEventListener("hashchange", updateCurrentSection);
})();
</script>
```

## Verification

Check all of the following:

1. At `1400px`, the guide is hidden; at `1401px`, it appears.
2. Every guide link targets an existing, unique heading `id`.
3. Resting lines are all `32px`.
4. Exactly one link carries `aria-current="location"` after initial load and while scrolling; its line is 48% black.
5. Hovering a middle item produces the approximately `77/53/42/36/32px` falloff in both directions where neighbors exist.
6. Only the selected label is visible.
7. Keyboard focus shows the selected line and label.
8. Reduced-motion mode removes transitions.
9. Printing and narrow layouts do not show the guide.

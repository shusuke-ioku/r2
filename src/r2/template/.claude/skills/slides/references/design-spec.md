# Slides Design Specification

Quick reference for the visual system in `talk/style.typ`.

## Typst Imports

```typst
#import "style.typ": *
#enable-handout-mode(true)
#show: slides-style
```

## Slide Templates

### Title slide
```typst
#title-slide(
  title: [Paper Title],
  subtitle: [Paper Subtitle],
  author: [Author Name],
)
```

### Standard content slide
```typst
#slide[
  = Slide Heading
  #set align(horizon)
  #one-by-one[
    First point with bullet list:
    - Sub-point A
    - Sub-point B
  ][
    Second point revealed next
  ]
]
```

### Figure slide
```typst
#slide[
  = Figure Title
  #set align(horizon+center)
  #image("../analysis/output/figures/filename.png", width: 85%)
  #set align(left)
  - Key takeaway bullet
]
```

### Two-column slide
```typst
#slide[
  = Heading
  #set align(horizon)
  #grid(
    columns: (1.2fr, 1fr),
    column-gutter: 0em,
    [
      #one-by-one[
        Left column content
      ]
    ],
    image("../analysis/output/figures/map.png", width: 120%),
  )
]
```

### Table slide
```typst
#slide[
  = Table Title
  #set align(horizon+center)
  #one-by-one[
    #set align(center)
    #set text(size: .7em)
    #table(
      columns: (2.5fr, 1fr, 1fr),
      align: (left, center, center),
      inset: (x: 5pt, y: 6pt),
      stroke: none,
      table.hline(stroke: 1.2pt),
      [Header 1], [Header 2], [Header 3],
      table.hline(stroke: 0.4pt),
      [Row 1], [val], [val],
      table.hline(stroke: 1.2pt),
    )
  ][
    #set align(left)
    - Interpretation bullet
  ]
]
```

## Section Dividers

```typst
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
// MAJOR SECTION NAME
// %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

// ============================================================
// SLIDE TOPIC NAME
// ============================================================
```

## Character Budget

At 22pt PT Sans on 4:3 with 3em margins:
- Top-level bullet: ~55 characters max
- Nested bullet (1 indent): ~50 characters max
- Table header cell: ~12 characters ideal
- Heading text: ~40 characters ideal

These are estimates. Always compile and check the PDF.

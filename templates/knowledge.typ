// Local, package-free Typst layout for incremental per-course knowledge summaries.
#let knowledge(course: "", updated: "", covered: "", body) = {
  set document(title: course + " · 知识点总结", author: "")
  set page(
    paper: "a4",
    margin: (top: 21mm, bottom: 20mm, left: 23mm, right: 23mm),
    numbering: "1 / 1",
    number-align: center,
    header: context {
      if counter(page).get().first() > 1 {
        text(size: 8.5pt, fill: rgb("666666"))[#course · 知识点总结]
      }
    },
  )
  set text(font: ("Libertinus Serif", "SimSun"), size: 10.5pt, lang: "zh")
  set par(leading: 0.65em, justify: true)
  set heading(numbering: none)
  set math.equation(numbering: none)
  show heading.where(level: 1): it => block(above: 1.4em, below: 0.8em)[
    #text(size: 14pt, weight: "bold", fill: rgb("203e58"), it.body)
  ]
  show heading.where(level: 2): it => block(above: 1.1em, below: 0.5em)[
    #text(size: 11.5pt, weight: "bold", fill: rgb("2c3e50"), it.body)
  ]
  show heading.where(level: 3): it => block(above: 0.8em, below: 0.4em)[
    #text(size: 10.5pt, weight: "bold", it.body)
  ]
  align(center)[
    #text(size: 20pt, weight: "bold")[#course · 知识点总结]
    #v(3mm)
    #text(size: 9pt, fill: rgb("555555"))[最后更新：#updated  ·  已覆盖：#covered]
  ]
  v(2mm)
  line(length: 100%, stroke: 0.6pt + rgb("9eafbd"))
  v(2mm)
  outline(title: "目录", indent: 1.5em)
  v(3mm)
  body
}

#let keybox(title: "核心公式", body) = block(
  width: 100%,
  inset: 9pt,
  radius: 3pt,
  fill: rgb("f4f7fa"),
  stroke: (left: 2.5pt + rgb("203e58")),
)[
  #text(weight: "bold", fill: rgb("203e58"))[#title]
  #v(2pt)
  #body
]

#let tipbox(title: "易错点 / 直观理解", body) = block(
  width: 100%,
  inset: 9pt,
  radius: 3pt,
  fill: rgb("fdf8f2"),
  stroke: (left: 2.5pt + rgb("c06c2b")),
)[
  #text(weight: "bold", fill: rgb("c06c2b"))[#title]
  #v(2pt)
  #body
]

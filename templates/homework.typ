// Local, package-free Typst layout. Keep this file with each archived answer.
#let homework(course: "", assignment: "", assigned: "", due: "", body) = {
  set document(title: course + " · " + assignment, author: "")
  set page(
    paper: "a4",
    margin: (top: 21mm, bottom: 20mm, left: 23mm, right: 23mm),
    numbering: "1 / 1",
    number-align: center,
    header: context {
      if counter(page).get().first() > 1 {
        text(size: 8.5pt, fill: rgb("666666"))[#course · #assignment]
      }
    },
  )
  set text(font: ("Libertinus Serif", "SimSun"), size: 10.5pt, lang: "zh")
  set par(leading: 0.65em, justify: true)
  set heading(numbering: none)
  set math.equation(numbering: none)
  show heading.where(level: 1): it => block(above: 1.3em, below: 0.8em)[
    #text(size: 14pt, weight: "bold", fill: rgb("203e58"), it.body)
  ]
  show heading.where(level: 2): it => block(above: 1em, below: 0.5em)[
    #text(size: 11.5pt, weight: "bold", it.body)
  ]
  align(center)[
    #text(size: 21pt, weight: "bold")[#course · #assignment]
    #v(3mm)
    #text(size: 9pt, fill: rgb("555555"))[布置日期：#assigned  ·  截止：#due]
  ]
  v(2mm)
  line(length: 100%, stroke: 0.6pt + rgb("9eafbd"))
  v(2mm)
  body
}

# Contributing

Here are the design choices you should be aware of:
- the renderer uses a flex div soup, with small css utility classes
- most css classes are either utility classes (.row, .gap, .block) for quick design prototyping, or AST semantic classes (.if, .while, .funcdef,...)
- the syntax is entirely rendered from CSS: indentation, keywords, parenthesis, commas and spaces are all rendered in pure css. The HTML DOM acts as a direct mapping of the Python AST, to simplify code transformations.


There are currently 2 renderers:
- a static renderer, which generates static html during initial file loading
  - TODO: use generators for string processing efficiency
- a dynamic one, which patches the DOM during edition

Due to the Python/JS bridging, the dynamic renderer is much slower than the static renderer, and cannot process huge files instantly.


# Roadmap

CSS:
- use a style generator like SASS to build AST class styles from utility classes (this would simplify the renderer by removing style information)



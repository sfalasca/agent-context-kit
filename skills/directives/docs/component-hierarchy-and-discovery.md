---
description: Components form a levelized (acyclic) dependency graph, physical structure mirrors it, and folder depth reveals detail progressively
scope: root
covers: [architecture, design, components, modules, dependencies, levelization, folder-structure, coupling, discoverability]
---

# Component hierarchy and discovery

- Dependencies between components/modules must form a DAG (levelization): no cyclic dependencies.
  A component only depends on components at a lower architectural level than itself. If two
  components need each other, they are not two components — merge them, or extract the shared part
  into a genuinely lower-level component both can depend on.
- Physical structure (folders/packages) mirrors the logical dependency structure, not just topical
  grouping. Two things living in the same folder because they're "about the same feature" is not
  sufficient — if one depends on the other, that dependency direction should be visible from the
  folder layout (e.g. lower-level code nested under or separated from what depends on it), not
  discoverable only by reading imports.
- This mirroring is also what makes code reusable: a lower-level component pulled out because
  something above it depends on it is, by construction, a candidate library — it has no knowledge
  of its dependents and no reason not to be depended on by something else later. Structure driven by
  feature-grouping instead tends to bury genuinely reusable logic inside a feature folder, coupled to
  that feature's concerns, where nothing else can find or depend on it without reaching in. When
  extracting a component, ask whether it could become a standalone library as a check that the
  boundary is drawn in the right place, not just that the code moved.
- Progressive discovery: a top-level folder must be legible on its own — name plus a short doc —
  without opening its subfolders. Depth reveals detail, not prerequisite knowledge. Someone should be
  able to understand the system by descending level by level, never needing to jump back up to a
  sibling or ancestor folder to make sense of what they're currently looking at.
- Minimize physical coupling: a change to one component's internals must not ripple into unrelated
  components' interfaces or force them to change. Other components depend on a component's interface
  surface, not its implementation detail — if consumers reach past the interface (deep imports,
  reading internal files, relying on undocumented behavior), that's a levelization violation to fix,
  not a pattern to accommodate.
- When adding a new component or reorganizing folders, check the resulting dependency graph is still
  acyclic and still levelized before considering the change done — this is a structural property to
  verify, not something to eyeball (see [[tools-over-judgment]] if a dependency-graph tool exists or
  is worth adding). This is complementary to [[hierarchical-verification]]: levelization is a
  property of the design, checked when the structure changes, not a step in the fail-fast test
  pipeline.
- This applies at every scale: a monorepo's top-level packages, a single package's internal modules,
  and a folder's subfolders should all satisfy the same rules.

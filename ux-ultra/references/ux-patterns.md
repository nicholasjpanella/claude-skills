# Filters, navigation and scrolling rows

Read this when a screen has a filterable list, mobile navigation or a horizontal row of items. These rules come from Baymard Institute's 2025–2026 e-commerce usability benchmarks. They were tested on shops, but the problems are the same on any filterable collection. Only sources from the last two years go here. Topics with no recent evidence (data tables, list vs grid vs table, hamburger vs tab bar) are left out on purpose rather than filled from older research.

## Filters

- **Show the applied filters.** Keep a summary of active filters where the user can review and remove each one: above the list, above the filter sidebar, or under a horizontal filter bar on desktop; a scrolling or stacked row at the top of the list on phones. Many benchmarked sites still fail this.
- **Several values per filter.** Let users pick more than one value within a filter type (two colours, three sizes). Single-select forces them to filter, remember the results and start again. In testing, people commonly applied 5 or 6 filters, some up to 10.
- **Bar or sidebar by the number of filter types.** A horizontal filter bar works for about 8 filter types or fewer. It hides the options and their counts until each one is opened, and filters that spill into an "All filters" button get overlooked. With more filter types, use a sidebar.
- Write down the expected item count and the attributes people choose by in DESIGN.md before building filters, so the pattern is sized for the real data.

## Mobile navigation

- Phones rarely have navigation that stays visible, so mark where the user is inside the navigation panel: the current section looks different from the rest. Most benchmarked mobile sites don't do this.

## Horizontal scrolling rows

- Prefer showing a few items with a "Show all" control. If you do use a horizontal row, let the last visible item be visibly cut off so the row reads as scrollable, add scroll arrows on both sides for mouse users, and give screen-reader users the item count, since a cut-off item is only a visual hint.

## Check

- Apply three filters, including two values in one type, at 375px and desktop width: the applied summary shows all of them and each removes on its own.
- Open the mobile navigation from inside a section: the current section is marked.
- Scroll every horizontal row with a mouse at desktop width and with a swipe at 375px.

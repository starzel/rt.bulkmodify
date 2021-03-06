Changelog
=========

0.4.2 (unreleased)
------------------

- Version 0.4.1 was providing a bad setup handler target
  [keul]
- Fixed UnicodeDecodeError when the extracted text for preview contains
  non-ASCII chars. This close `#4`__.
  [keul]

__ https://github.com/RedTurtle/rt.bulkmodify/issues/4

- Add Portlet Replacement code
  [do3cc]

- Find text language independent
  [do3cc]

0.4.1 (2014-05-29)
------------------

- Requires zope.tal >= 3.6.1 if on Python 2.6. This close `#2`__.
  [keul]
- Make ``portal_css`` and ``portal_javascript`` happy: do not add
  load condition for JavaScript and CSS. This prevent fragmentation on
  loaded resources
  [keul]

__ https://github.com/RedTurtle/rt.bulkmodify/issues/2

0.4 (2013-10-07)
----------------

- Nicely display types check, plus a select all/none command
  [keul]
- Show a counter for documents really checked (means: for documents where
  the ``IBulkModifyContentChanger`` adapter has been found)
  [keul]
- Show an HTML preview also when replacing text (this close #3)
  [keul]
- Do not break if "text" can't be read (for example: for ComputedField named "text")
  [keul]

0.3 (2013-04-02)
----------------

- Calling a new search after a change were not working until
  you re-start the instance
  [keul]
- Fixed broken tests
  [keul]
- Better UI after changes (display only one message per content, and keep
  the content title)
  [keul]
- Calling additional changes on the same content were not working
  (or worst: it could perform a wrong substitution)
  [keul]
- Fixed a bug in the label/checkbox association when you have multiple match on same element
  [keul]
- Added a new checkbox type, for selecting all matches of the same document
  [keul]

0.2 (2013-03-26)
----------------

- Kept a link to content after server changes
  [keul]
- Open links in new windows
  [keul]
- When a document is updated multiple times, only *one* new
  version is created
  [keul]
- When request for replacements are submitted show a spinner and disable
  checkbox
  [keul]
- Display a counter about running searches
  [keul]
- JSHint cleanup and fix for Internet Explorer
  [keul]
- Is now possible to pause, then continue, a search operation
  [keul]

0.1.1 (2013-03-15)
------------------

- When loading data from Archetypes field, use the ``raw`` format.
  This prevent substitution from destroying ``resolveuid`` usage.
  [keul]
- When  performing searches, display immediately the "loading" info,
  not after the first completed request
  [keul]

0.1 (2013-03-14)
----------------

- Initial release

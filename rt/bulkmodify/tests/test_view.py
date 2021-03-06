# -*- coding: utf-8 -*-

import json

from zope.component import getMultiAdapter

from rt.bulkmodify.testing import BULK_MODIFY_INTEGRATION_TESTING

from .base import BaseTestCase
from .base import re_pattern
from .base import re_subn_pattern

class TestViewBatchSearch(BaseTestCase):

    layer = BULK_MODIFY_INTEGRATION_TESTING
    
    def setUp(self):
        BaseTestCase.setUp(self)
        self.view = getMultiAdapter((self.layer['portal'],
                                     self.layer['request']),
                                     name=u"batchSearch")

    def test_missing_parameters(self):
        view = self.view
        # no params
        self.assertEqual(json.loads(view()), {u'results': []})
        # only content_type
        view.request.set('content_type', ['foo'])
        self.assertEqual(json.loads(view()), {u'results': []})
        # only query
        view.request.set('content_type', {u'results': []})
        view.request.set('searchQuery', 'foo')
        self.assertEqual(json.loads(view()), {u'results': None})
        # both
        view.request.set('content_type', ['foo'])
        view.request.set('searchQuery', 'foo')
        self.assertEqual(json.loads(view()), {u'results': None})
        # an existing type, but no query
        view.request.set('content_type', ['Document', ])
        view.request.set('searchQuery', '')
        self.assertEqual(json.loads(view()), {u'results': []})

    def test_simple_search(self):
        view = self.view
        view.request.set('content_type', ['Document', ])
        view.request.set('searchQuery', re_pattern)
        results = json.loads(view())['results']
        
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]['title'], 'Page 1')
        self.assertEqual(results[0]['text'],
                         u'... dolor <span class="mark">&lt;a target="_blank" href="http://loripsum.net/"&gt;sit amet, consectetur adipisicing elit&lt;/a&gt;</span>, sed d...')
        self.assertEqual(results[2]['title'], 'Page 2')
        self.assertEqual(results[2]['text'],
                         u'...ongue. <span class="mark">&lt;a target="_blank" href="http://loripsum.net/"&gt;Duis ac augue diam&lt;/a&gt;</span>, digni...')

    def test_batching(self):
        view = self.view
        view.request.set('content_type', ['Document', ])
        view.request.set('searchQuery', re_pattern)
        view.request.set('b_size', 1)
        self.assertEqual(len(json.loads(view())), 3)
        view.request.set('b_start', 1)
        self.assertEqual(len(json.loads(view())), 3)
        view.request.set('b_start', 2)
        self.assertEqual(json.loads(view()), {u'results': None})

    def test_discarded_types(self):
        view = self.view
        view.request.set('content_type', ['Document', 'Folder'])
        view.request.set('searchQuery', 'this text is not found inside the document HTML')
        results = json.loads(view())
        self.assertEqual(results['results'], [])
        self.assertEqual(results['really_checked_docs'], 2)

    def test_discarded_types_with_portlets(self):
        view = self.view
        view.request.set('content_type', ['Document', 'Folder'])
        view.request.set('portlets', 'true')
        view.request.set('searchQuery', 'this text is not found inside the document HTML')
        results = json.loads(view())
        self.assertEqual(results['results'], [])
        self.assertEqual(results['really_checked_docs'], 3)

    def test_search_portlets(self):
        view = self.view
        view.request.set('content_type', ['Document', 'Folder'])
        view.request.set('portlets', 'true')
        view.request.set('searchQuery', "portlet")
        results = json.loads(view())
        self.assertEquals(2, len(results['results']))
        self.assertEquals(u'...I am a <span class="mark">portlet</span>&lt;/p&gt;\n&lt;/p&gt;\n...',
                          results['results'][0]['text'])
        self.assertEqual(results['really_checked_docs'], 3)


class TestViewBatchReplace(BaseTestCase):

    layer = BULK_MODIFY_INTEGRATION_TESTING
    
    def setUp(self):
        BaseTestCase.setUp(self)
        self.view = getMultiAdapter((self.layer['portal'],
                                     self.layer['request']),
                                     name=u"batchReplace")

    def test_missing_parameters(self):
        view = self.view
        # no params
        self.assertEqual(json.loads(view()), {u'results': []})
        view.request.set('content_type', ['foo'])
        # only content_type
        self.assertEqual(json.loads(view()), {u'results': []})
        # only query
        view.request.set('content_type', [])
        view.request.set('searchQuery', 'foo')
        self.assertEqual(json.loads(view()), {u'results': []})
        # only replace query
        view.request.set('searchQuery', '')
        view.request.set('replaceQuery', '')
        self.assertEqual(json.loads(view()), {u'results': []})
        # all three paarameters
        view.request.set('content_type', ['foo'])
        view.request.set('searchQuery', 'foo')
        view.request.set('replaceQuery', 'foo')
        self.assertNotEqual(json.loads(view()), 'foo')
        # an existing type, but no queries
        view.request.set('content_type', ['Document', ])
        view.request.set('searchQuery', '')
        view.request.set('replaceQuery', '')

    def test_simple_replace(self):
        view = self.view
        view.request.set('content_type', ['Document', ])
        view.request.set('searchQuery', re_pattern)
        view.request.set('replaceQuery', re_subn_pattern)
        results = json.loads(view())['results']

        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]['title'], 'Page 1')
        self.assertEqual(results[0]['old'],
                         u'<a target="_blank" href="http://loripsum.net/">sit amet, consectetur adipisicing elit</a>')
        self.assertEqual(results[0]['new'],
                         u'<a href="http://loripsum.net/" class="external-link">sit amet, consectetur adipisicing elit</a>')
        self.assertEqual(results[2]['title'], 'Page 2')
        self.assertEqual(results[2]['old'],
                         u'<a target="_blank" href="http://loripsum.net/">Duis ac augue diam</a>')
        self.assertEqual(results[2]['new'],
                         u'<a href="http://loripsum.net/" class="external-link">Duis ac augue diam</a>')

    def test_replace_portlets(self):
        view = self.view
        view.request.set('content_type', ['Document', 'Folder'])
        view.request.set('searchQuery', re_pattern)
        view.request.set('portlets', True)
        view.request.set('replaceQuery', re_subn_pattern)
        results = json.loads(view())['results']

        self.assertEqual(len(results), 6)
        self.assertEqual(results[5]['title'], 'Folder 1')
        self.assertEqual(results[5]['old'],
                         u'<a target="_blank" href="http://loripsum.net/">Duis ac augue diam</a>')
        self.assertEqual(results[5]['new'],
                         u'<a href="http://loripsum.net/" class="external-link">Duis ac augue diam</a>')

    def test_futile_replacement(self):
        view = self.view
        view.request.set('content_type', ['Document', ])
        view.request.set('searchQuery', re_pattern)
        view.request.set('replaceQuery', r'<a target="_blank" href="\g<url>">\g<text></a>')
        results = json.loads(view())['results']
        # if replacement return the original text, no replacement is needed
        self.assertEqual(len(results), 0)

    def test_replace_with_utility(self):
        view = self.view
        view.request.set('content_type', ['Document', ])
        view.request.set('searchQuery', re_pattern)
        view.request.set('replace_type', 'fake')
        results = json.loads(view())['results']
        self.assertEqual(results[0]['new'], 'NEW TEXT!')


class TestViewReplaceText(BaseTestCase):

    layer = BULK_MODIFY_INTEGRATION_TESTING

    def setUp(self):
        BaseTestCase.setUp(self)
        portal = self.layer['portal']
        self.view = getMultiAdapter((self.layer['portal'],
                                     self.layer['request']),
                                     name=u"replaceText")
        self.ids1 = ["%s-0" % '/'.join(portal['page1'].getPhysicalPath()[2:]),
                     "%s-1" % '/'.join(portal['page1'].getPhysicalPath()[2:])]
        self.ids2 = ["%s-0" % '/'.join(portal['news1'].getPhysicalPath()[2:])]
        self.ids3 = ["%s-0" % '/'.join(portal['page2'].getPhysicalPath()[2:]),
                     "%s-1" % '/'.join(portal['page2'].getPhysicalPath()[2:])]
        self.ids4 = ["%s-0" % '/'.join(portal['link1'].getPhysicalPath()[2:])]
        self.ids5 = ["%s-0" % '/'.join(portal['folder1'].getPhysicalPath()[2:])]
        self.ids6 = ["%s-0" % '/'.join(portal['page1'].getPhysicalPath()[2:]),
                     "%s-1" % '/'.join(portal['page1'].getPhysicalPath()[2:]),
                     "%s-2" % '/'.join(portal['page1'].getPhysicalPath()[2:])]

    def test_missing_parameters(self):
        view = self.view
        # no params
        self.assertEqual(json.loads(view()), [])
        # only ids
        view.request.set('id', self.ids1)
        self.assertEqual(json.loads(view()), [])

    def test_single_subn(self):
        portal = self.layer['portal']
        view = self.view
        view.request.set('id', self.ids1[1:])
        view.request.set('searchQuery', re_pattern)
        view.request.set('replaceQuery', re_subn_pattern)
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">reprehenderit in voluptate velit</a>' in portal.page1.getText())
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">sit amet, consectetur adipisicing elit</a>' in portal.page1.getText())
        self.assertEqual(json.loads(view()), [{"status": "OK"}])
        self.assertFalse('<a target="_blank" href="http://loripsum.net/">reprehenderit in voluptate velit</a>' in portal.page1.getText())
        self.assertTrue('<a href="http://loripsum.net/" class="external-link">reprehenderit in voluptate velit</a>' in portal.page1.getText())
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">sit amet, consectetur adipisicing elit</a>' in portal.page1.getText())

    def test_portlet_subn_folder(self):
        portal = self.layer['portal']
        view = self.view
        view.request.set('id', self.ids5)
        view.request.set('searchQuery', re_pattern)
        view.request.set('replaceQuery', re_subn_pattern)
        view.request.set('portlets', True)
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">Duis ac augue diam</a>' in self.layer['portlet1'].text)
        self.assertEqual([{"status": "OK"}], json.loads(view()))
        self.assertTrue('<a href="http://loripsum.net/" class="external-link">Duis ac augue diam</a>' in self.layer['portlet1'].text)

    def test_portlet_subn_document(self):
        portal = self.layer['portal']
        view = self.view
        view.request.set('id', self.ids6)
        view.request.set('searchQuery', re_pattern)
        view.request.set('replaceQuery', re_subn_pattern)
        view.request.set('portlets', True)
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">Duis ac augue diam</a>' in self.layer['portlet2'].text)
        self.assertEqual([{"status": "OK"}, {"status": "OK"}, {"status": "OK"}], json.loads(view()))
        self.assertTrue('<a href="http://loripsum.net/" class="external-link">Duis ac augue diam</a>' in self.layer['portlet2'].text)
        self.assertEqual('<p>\n    <ul>\n        <li>Sed tristique accumsan arcu et congue. <a href="http://loripsum.net/" class="external-link">Duis ac augue diam</a>, dignissim imperdiet lectus</li>\n    </ul>\n    <p>Also, I am a portlet</p>\n</p>\n', self.layer['portlet2'].text)

    def test_multiple_subn(self):
        portal = self.layer['portal']
        view = self.view
        view.request.set('id', self.ids1)
        view.request.set('searchQuery', re_pattern)
        view.request.set('replaceQuery', re_subn_pattern)
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">reprehenderit in voluptate velit</a>' in portal.page1.getText())
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">sit amet, consectetur adipisicing elit</a>' in portal.page1.getText())
        self.assertEqual(json.loads(view()), [{"status": "OK"}, {"status": "OK"}])
        self.assertFalse('<a target="_blank" href="http://loripsum.net/">reprehenderit in voluptate velit</a>' in portal.page1.getText())
        self.assertFalse('<a target="_blank" href="http://loripsum.net/">sit amet, consectetur adipisicing elit</a>' in portal.page1.getText())
        self.assertTrue('<a href="http://loripsum.net/" class="external-link">reprehenderit in voluptate velit</a>' in portal.page1.getText())
        self.assertTrue('<a href="http://loripsum.net/" class="external-link">sit amet, consectetur adipisicing elit</a>' in portal.page1.getText())

    def test_multiple_subn_for_one_version(self):
        portal = self.layer['portal']
        view = self.view
        portal_repository = portal.portal_repository
        portal_repository.applyVersionControl(portal.page1, comment='Init')
        view.request.set('id', self.ids1)
        view.request.set('new_version', True)
        view.request.set('searchQuery', re_pattern)
        view.request.set('replaceQuery', re_subn_pattern)
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">reprehenderit in voluptate velit</a>' in portal.page1.getText())
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">sit amet, consectetur adipisicing elit</a>' in portal.page1.getText())
        self.assertEqual(len(portal_repository.getHistoryMetadata(portal.page1)),
                         1)
        # we are now applying 2 changes in the same document
        self.view()
        self.assertEqual(len(portal_repository.getHistoryMetadata(portal.page1)),
                         2)

    def test_unknow_type(self):
        view = self.view
        view.request.set('id', self.ids4)
        view.request.set('searchQuery', 'foo')
        view.request.set('replaceQuery', 'bar')
        self.assertEqual(json.loads(view()),
                         [{u'status': u'error', u'message': u"Don't know how to handle http://nohost/plone/link1"}])

    def test_replace_with_utility(self):
        portal = self.layer['portal']
        view = self.view
        view.request.set('id', self.ids1)
        view.request.set('searchQuery', re_pattern)
        view.request.set('replace_type', 'fake')
        view()
        self.assertEqual(portal.page1.getRawText(),
                         """<p>
    <ul>   
        <li>Lorem ipsum dolor NEW TEXT!, sed do eiusmod tempor incididunt</li>
        <li>Duis aute irure dolor in NEW TEXT! esse cillum dolore eu fugiat nulla pariatur</li>
    </ul>\n</p>
""")


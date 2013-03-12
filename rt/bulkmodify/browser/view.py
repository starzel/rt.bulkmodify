# -*- coding: utf-8 -*-

import re
import json

from zope.component import getUtility
from zope.component import queryAdapter
from zope.component import getUtilitiesFor
from zope.interface import implements
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory

from plone.memoize.view import memoize

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from rt.bulkmodify import messageFactory as _
from rt.bulkmodify import utility
from rt.bulkmodify.interfaces import IBulkModifyContentChanger
from rt.bulkmodify.interfaces import IBulkModifyReplacementHandler

path_id_pattern = re.compile(r'^(.*)-(\d+)$')

class IBulkModify(Interface):
    """View for bulk modify"""
    
    def batchSearch():
        """Search for a subset of results and preview matches"""

    def batchReplace():
        """Search for a subset of result, and preview mach changes"""

    def replaceText():
        """Apply a regex replacement to documents"""


class BulkModifyView(BrowserView):
    implements(IBulkModify)

    @property
    @memoize
    def utilities(self):
        return getUtilitiesFor(IBulkModifyReplacementHandler)
    
    def type_vocabulary(self):
        factory = getUtility(IVocabularyFactory, 'plone.app.vocabularies.ReallyUserFriendlyTypes')
        return factory(self.context)

    def repl_type_vocabulary(self):
        results = [{'title': _('default_replacement_type_label',
                               default=u'Default replacement'),
                    'description': _('default_replacement_type_help',
                                     default=u'Default replacement method. Use the replacement string '
                                             u'from the "Replace regex" field below'),
                    'value': ''}]
        utilities = self.utilities
        for hname, hobj in utilities:
            results.append(dict(title=hobj.name,
                                description=hobj.description,
                                value=hname))
        return results

    def batchSearch(self):
        context = self.context
        request = self.request
        request.response.setHeader('Content-Type','application/json;charset=utf-8')
        search_query = request.get('searchQuery')
        b_start = request.get('b_start', 0)
        b_size = request.get('b_size', 20)
        flags = request.get('flags', 0)
        portal_type = request.get('content_type', [])
        catalog = getToolByName(context, 'portal_catalog')
        
        results = []

        if not portal_type or not search_query:
            return json.dumps(results)
        
        brains = catalog(portal_type=portal_type)[b_start:b_start+b_size]
        if not brains:
            # stop client side queries
            return json.dumps(None)
        for brain in brains:
            obj = brain.getObject()
            adapter = queryAdapter(obj, IBulkModifyContentChanger)
            if adapter:
                text = adapter.text
                inner_results = utility.text_search(text, search_query, flags=flags, preview=True)
                for result in inner_results:
                    result['url'] = brain.getURL()
                    result['id'] = brain.getPath()
                    result['uid'] = brain.UID
                    result['title'] = brain.Title
                    result['icon'] = brain.getIcon
                    result['normalized_portal_type'] = brain.portal_type.lower().replace(' ','-')
                results.extend(inner_results)
        return json.dumps(results)

    def get_content_diff_info(self, obj, search_query, replace_query, flags=0):
        adapter = queryAdapter(obj, IBulkModifyContentChanger)
        if adapter:
            text = adapter.text
            inner_results = utility.text_replace(text, search_query, replace_query, flags=flags)
            for result in inner_results:
                result['url'] = obj.absolute_url()
                result['id'] = '/'.join(obj.getPhysicalPath()[2:])
                result['uid'] = obj.UID()
                result['title'] = obj.Title()
                result['normalized_portal_type'] = obj.portal_type.lower().replace(' ','-')
            return inner_results
        return []

    def batchReplace(self):
        context = self.context
        request = self.request
        request.response.setHeader('Content-Type','application/json;charset=utf-8')
        search_query = request.get('searchQuery')
        replace_query = request.get('replaceQuery')
        replace_type = request.get('replace_type')
        b_start = request.get('b_start', 0)
        b_size = request.get('b_size', 20)
        flags = request.get('flags', 0)
        portal_type = request.get('content_type', [])
        catalog = getToolByName(context, 'portal_catalog')
        
        results = []
        
        if not portal_type or not search_query or (not replace_query and not replace_type):
            return json.dumps(results)
        
        brains = catalog(portal_type=portal_type)[b_start:b_start+b_size]
        if not brains:
            # stop client side queries
            return json.dumps(None)

        if replace_type:
            # let's load the proper replace type
            utilities = [u for u in self.utilities if u[0]==replace_type]
            replace_query = u[1].repl

        for brain in brains:
            obj = brain.getObject()
            inner_results = self.get_content_diff_info(obj, search_query, replace_query, flags=flags)
            for ir in inner_results:
                ir['icon'] = brain.getIcon
            results.extend(inner_results)
        return json.dumps(results)

    def changeDocumentText(self, obj, diff):
        """Change the text document. Return "true" if any change takes place"""
        adapter = queryAdapter(obj, IBulkModifyContentChanger)
        if adapter:
            text = adapter.text
            new_text = text[:diff['start']] + diff['new'] + text[diff['end']:]
            if text != new_text:
                adapter.text = new_text
                return True
        return False

    def replaceText(self):
        context = self.context
        request = self.request
        portal = getToolByName(context, 'portal_url').getPortalObject()
        request.response.setHeader('Content-Type','application/json;charset=utf-8')
        # ids MUST be of the same objects
        ids = request.get('id')
        search_query = request.get('searchQuery')
        replace_query = request.get('replaceQuery')
        replace_type = request.get('replace_type')
        flags = request.get('flags', 0)

        messages = []

        if ids and search_query and (replace_query or replace_type):
            
            if replace_type:
                # let's load the proper replace type
                utilities = [u for u in self.utilities if u[0]==replace_type]
                replace_query_klass = u[1]
                replace_query = u[1].repl

            for counter, id in enumerate(ids):
                match = path_id_pattern.match(id)
                path, id = match.groups()
                obj = portal.restrictedTraverse(path, default=None)
                id = int(id)
                if obj:
                    if replace_type:
                        replace_query_klass.context = obj
                    diff_info = self.get_content_diff_info(obj, search_query, replace_query, flags=flags)
                    if diff_info:
                        diff = diff_info[id-counter]
                        if self.changeDocumentText(obj, diff):
                            messages.append({'status': 'OK'})
                        else:
                            messages.append({'status': 'warn', 'message': 'No change is needed'})
                    else:
                        messages.append({'status': 'error', 'message': "Don't know how to handle %s" % obj.absolute_url()})
                else:
                    messages.append({'status': 'error', 'message': 'Document "%s" not found' % obj.absolute_url()})
        return json.dumps(messages)


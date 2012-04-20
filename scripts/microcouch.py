import getpass
import base64
import json
import urllib
import urllib2
from urlparse import urlunparse, urlparse


class PutRequest(urllib2.Request):
    def get_method(self):
        return "PUT"

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"
class MicroCouch:
    """
    An ugly class that provides minimal interactions with CouchDB
    """

    def __init__(self, database):
        parts = urlparse(database)

        self.auth = False
        self.created = False

        if parts.port:
            netloc = '%s:%s' % (parts.hostname, parts.port)
        else:
            netloc = parts.hostname

        url_tuple = (
                parts.scheme,
                netloc,
                parts.path,
                parts.params,
                parts.query,
                parts.fragment
                )
        self.url = urlunparse(url_tuple)
        self.do_auth(parts)
        self.create_db()

    def do_auth(self, parts):
        if parts.username and parts.password:
            auth_tuple = (parts.username, parts.password)
            self.auth = base64.encodestring('%s:%s' % auth_tuple).strip()
        elif parts.username:
            auth_tuple = (parts.username, getpass.getpass())
            self.auth = base64.encodestring('%s:%s' % auth_tuple).strip()

    def create_db(self):
        try:
            req = PutRequest(self.url)
            if self.auth:
                req.add_header("Authorization", "Basic %s" % self.auth)
            urllib2.urlopen(req)
            self.created = True
        except Exception, e:
            # The data base probably already exists
            print e
            pass

    def push(self, docs):
        """
        Push a list of docs to the database
        """
        def get_rev(doc):
            """
            Get the _rev for a doc if it has one, and add to the doc
            """
            if '_id' in doc.keys():
                docid = doc['_id']
                # HEAD the doc
                docurl = "%s/%s" % (self.url, urllib.quote_plus(docid))
                try:
                    head = urllib2.urlopen(HeadRequest(docurl))
                    # get its _rev, append _rev to the doc dict
                    doc['_rev'] = head.info().dict['etag'].strip('"')
                except urllib2.HTTPError, e:
                    pass
            return doc

        if not self.created:
            # if the database didn't exist the docs won't either!
            docs = map(get_rev, docs)

        req = urllib2.Request('%s/_bulk_docs' % self.url)
        req.add_header("Content-Type", "application/json")

        if self.auth:
            req.add_header("Authorization", "Basic %s" % self.auth)

        data = {'docs': docs}
        req.add_data(json.dumps(data))
        f = urllib2.urlopen(req)
        f.read()
        f.close()


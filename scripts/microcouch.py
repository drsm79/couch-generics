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

def push(docs, database):
    """
    Push a list of docs to the database
    """

    parts = urlparse(database)
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
    url = urlunparse(url_tuple)

    try:
        urllib2.urlopen(PutRequest(url))
    except:
        # The data base probably already exists
        pass

    def get_rev(doc):
        """
        Get the _rev for a doc if it has one, and add to the doc
        """
        if '_id' in doc.keys():
            docid = doc['_id']
            # HEAD the doc
            docurl = "%s/%s" % (url, urllib.quote_plus(docid))
            try:
                head = urllib2.urlopen(HeadRequest(docurl))
                # get its _rev, append _rev to the doc dict
                doc['_rev'] = head.info().dict['etag'].strip('"')
            except urllib2.HTTPError, e:
                pass
        return doc

    docs = map(get_rev, docs)

    auth = False

    if parts.username and parts.password:
        auth_tuple = (parts.username, parts.password)
        auth = base64.encodestring('%s:%s' % auth_tuple).strip()
    elif parts.username:
        auth_tuple = (parts.username, getpass.getpass())
        auth = base64.encodestring('%s:%s' % auth_tuple).strip()

    req = urllib2.Request('%s/_bulk_docs' % url)
    req.add_header("Content-Type", "application/json")

    if auth:
        req.add_header("Authorization", "Basic %s" % auth)

    data = {'docs': docs}
    req.add_data(json.dumps(data))
    f = urllib2.urlopen(req)
    f.read()
    f.close()


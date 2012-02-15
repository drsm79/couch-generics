#!/usr/bin/env python
"""
Retrieve a subset of a database and put it in another. Run via:
py scripts/fetch_subset.py -s http://localhost:5984/demo -d http://localhost:5984/demo2
"""
import json
import urllib
import urllib2
from optparse import OptionParser

def do_options():
  parser = OptionParser()
  parser.set_usage('copy a subset from one CouchDB to another')
  parser.add_option("-s", "--source", dest="source", metavar="SOURCE",
                help="copy from SOURCE (URL to database root)")
  parser.add_option("-d", "--dest", dest="dest", metavar="DESTINATION",
                help="write into DESTINATION (URL to database root)")
  parser.add_option("-l", "--limit", dest="limit", metavar="N", default=100,
                help="copy N documents, default=100")
  parser.add_option("-o", "--offset", dest="offset", metavar="N", default=0,
                help="skip the first N documents, default=0")

  return parser.parse_args()


def get_docs(src, limit, offset):
  """
  Get limit docs from src, skipping offset docs
  """
  values = {'limit': limit, 'offset': offset, 'include_docs': True}
  data = urllib.urlencode(values)
  req = urllib2.Request('%s/_all_docs?%s' % (src, data))
  f = urllib2.urlopen(req)
  docs = json.loads(f.read())
  f.close()
  def clean(d):
    d = d['doc']
    del d['_rev']
    return d
  return map(clean, docs['rows'])


def push_docs(dest, docs):
  """
  push docs to dest
  """
  url = '%s/_bulk_docs' % dest
  req = urllib2.Request(url)
  req.add_header("Content-Type", "application/json")
  req.add_data(json.dumps({'docs': docs}))
  f = urllib2.urlopen(req)
  f.close()


def copy_subset(src, dest, limit, offset):
  """
  copy limit documents, skipping offset docs, from src to dest
  """
  push_docs(dest, get_docs(src, limit, offset))

if __name__ == "__main__":
  options, args = do_options()
  copy_subset(options.source, options.dest, options.limit, options.offset)

#!/usr/bin/env python
#
# Copyright 2019 N-Dream AG Inc.


import urllib2
import urllib
import json
import os
import md5
import sys

def build(config=None):
  if isinstance(config, basestring):
    if os.path.exists(os.path.join(config, "build.json")):
      config = os.path.join(config, "build.json")
    if config.endswith(".json"):
      if not os.path.exists(config):
        raise Exception("Config not found: " + config)
      root = os.path.dirname(config)
      config = json.load(open(config))
      config["root"] = root
    else:
      raise Exception("No build.json found in " + config)

  js = _concat(config)
  es5 = True
  if not config.get("compile", True):
    es5 = False
  checksum = "/* Compiler Checksum: %s */\n" % md5.new(
    js + str(es5)).hexdigest()

  fp = config.get("output")
  close_after = False
  if isinstance(fp, basestring):
    fp = os.path.join(config.get("root", ""), fp)
    if os.path.exists(fp):
      candidate = open(fp).read()
      if candidate.startswith(checksum):
        print "Already compiled"
        return
    elif not os.path.exists(os.path.dirname(config["output"])):
      os.makedirs(os.path.join(config.get("root"),
                               os.path.dirname(config["output"])))
    fp = open(fp, "w")
    close_after = True
  elif not fp:
    fp = open("build.js", "w")
    close_after = True

  if es5:
    js = compile(js)

  fp.write(checksum + js)
  if close_after:
    fp.close()

def compile(js):
  print "Compiling"
  params = [
    ('js_code', js),
    ('language_out', 'ES5'),
    ('compilation_level', "SIMPLE_OPTIMIZATIONS"),
    ('output_format', 'json'),
    ('output_info', 'compiled_code'),
    ('output_info', 'errors'),
  ]
  params = urllib.urlencode(params)
  headers = { "Content-type": "application/x-www-form-urlencoded" }

  response = urllib2.urlopen(
    urllib2.Request("https://closure-compiler.appspot.com/compile",
    params, headers), timeout=55)

  if response.getcode() == 200:
    response = json.loads(response.read())
    if "errors" not in response:
      out = response["compiledCode"]
    else:
      raise Exception("Compiling JS failed: " + str(response["errors"]))
  else:
    raise Exception("Compiling JS failed with HTTP code: " +
                    str(response.status_code))
  return out

def _getAllFiles(config, path, seen):
  if path in seen:
    return
  seen.add(path)
  f = os.path.join(config.get("root", ""), path)
  if path in config.get("exclude", ""):
    return
  if os.path.exists(f):
    if not os.path.isdir(f):
      if f.lower().endswith(".js"):
        yield path
    else:
      for file in os.listdir(f):
        for sub in _getAllFiles(config, os.path.join(path,file), seen):
          yield sub
  else:
    raise Exception("Source does not exist: " + path)


def _concat(config):
  buffer = []
  if (config.get("header")):
    buffer.append(str(config.get("header")))
  sources = config.get("src", "src")
  if isinstance(sources, basestring):
    sources = [sources]
  if not isinstance(sources, list):
    raise "No source specified"
  seen = set([])
  for src in sources:
    for file in sorted(_getAllFiles(config, src, seen)):
      f = os.path.join(config.get("root", ""), file)
      print "Include: " + file
      if "namespace" in config and file in config["namespace"]:
        namespace = config["namespace"][file]
        print "  Overwriting module namepsace to " + namespace
        buffer.append("(function(wrapped_exports) {\n" +
                      "  var module = {\"exports\": {}};\n" +
                      "  var exports = module.exports;\n")
        buffer.append(open(f).read())
        namespace_parts = namespace.split(".")
        for i in xrange(len(namespace_parts)-1):
          js_namespace = ".".join(namespace_parts[0: i + 1])
          buffer.append(
            str("  wrapped_exports.%s = wrapped_exports.%s || {};" %
                (js_namespace, js_namespace)))
        buffer.append(str("  wrapped_exports.%s = module.exports;" %
                          namespace))
        buffer.append("})(typeof exports === 'undefined'? window : exports);")
      else:
        buffer.append(open(f).read())
  return "\n".join(buffer)


if __name__ == "__main__":
  args = [x for x in sys.argv if x != "--watch"]
  if args[0] == "python":
    args = args[1:]
  if len(args) == 1:
    print "Usage: build.py path_to_build_config.json"
  else:
    build(args[1])
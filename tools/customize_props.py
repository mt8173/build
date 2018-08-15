#!/usr/bin/env python
#
# Copyright (C) 2009 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import string

# This script will go through $TARGET_DEVICE_DIR/overrides.prop, and 
# 1) If property in overrides.prop exists in /system/build.prop, will use the value
#    in overrides.prop to modify /system/build.prop.
# 2) If propperty in overrides.prop does not exist in /system/build.prop or its value
#    is empty, will add the property to /system/build.prop

# Param prop is the property set of /system/build.prop.
# The prop object has get(name) and put(name,value) methods.
def mangle_build_prop(prop, over_lines):
  overrides = [s[:-1] for s in over_lines]
  for i in range(0, len(overrides)):
    l = overrides[i].replace(' ',' ')
    if l.startswith('#'):
      continue
    kv = l.split('=')
    if len(kv) != 2 :
      continue
    key = kv[0]
    value = kv[1]
    prop.put(key, value)

def get_pre_fingerprint(prop):
    product_brand = prop.get("ro.product.brand")
    product_name = prop.get("ro.product.name")
    product_device = prop.get("ro.product.device")
    pre_sum = product_brand + '/' + product_name + '/' + product_device
    return pre_sum

class PropFile:
  def __init__(self, lines):
    self.lines = [s[:-1] for s in lines]

  def get(self, name):
    key = name + "="
    for line in self.lines:
      if line.startswith(key):
        return line[len(key):]
    return ""

  def put(self, name, value):
    key = name + "="
    for i in range(0,len(self.lines)):
      if self.lines[i].startswith(key):
        self.lines[i] = key + value
        return
    self.lines.append(key + value)

  def write(self, f):
    f.write("\n".join(self.lines))
    f.write("\n")

def main(argv):
  filename = argv[1]
  f = open(filename)
  lines = f.readlines()
  f.close()

  override_file = argv[2]
  of = open(override_file)
  over_lines = of.readlines()
  of.close()

  properties = PropFile(lines)
  if filename.endswith("/build.prop"):
    old_pre_fingerprint = get_pre_fingerprint(properties)
    mangle_build_prop(properties, over_lines)
    new_pre_fingerprint = get_pre_fingerprint(properties)
    fingerprint = properties.get("ro.build.fingerprint")
    fingerprint = fingerprint.replace(old_pre_fingerprint, new_pre_fingerprint)
    properties.put("ro.build.fingerprint", fingerprint)
  else:
    sys.stderr.write("bad command line: " + str(argv) + "\n")
    sys.exit(1)

  f = open(filename, 'w+')
  properties.write(f)
  f.close()

if __name__ == "__main__":
  main(sys.argv)

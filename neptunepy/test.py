# -*- coding: utf-8 -*-
# @Author: bryanthayes
# @Date:   2017-04-24 12:58:15
# @Last Modified by:   bryanthayes
# @Last Modified time: 2017-04-24 13:07:01
from pkg_resources import resource_string, resource_listdir, resource_stream

# Itemize data files under neptunepy/resources/config:
print(resource_listdir('neptunepy.resources.config', ''))
configfile = resource_stream("neptunepy.resources.config", 'config.ini').read().decode()
print(configfile)
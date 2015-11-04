###
# Copyright (c) 2015, lostlabyrinth
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

# my libs
from lxml import etree
from bs4 import BeautifulSoup
import sys
if sys.version_info[0] > 2:
    import urllib.request, urllib.error, urllib.parse
else:  # python2.
    import urllib2
from random import choice
import json
import re
import xml.dom.minidom
import feedparser
import base64
#import socket
import random
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('IPLookup')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class IPLookup(callbacks.Plugin):
    """Allows for a user to lookup the location and ISP data for a specified IP address"""
    threaded = True

    def _rainbow(self, text):
        text = ''.join([ircutils.mircColor(x, choice(list(ircutils.mircColors.keys()))) for x in text])
        return text

    def _red(self, string):
        return ircutils.mircColor(string, 'red')

    def _yellow(self, string):
        """Returns a yellow string."""
        return ircutils.mircColor(string, 'yellow')

    def _green(self, string):
        """Returns a green string."""
        return ircutils.mircColor(string, 'green')

    def _blue(self, string):
        """Returns a blue string."""
        return ircutils.mircColor(string, 'blue')

    def _lightblue(self, string):
        """Returns a light blue string."""
        return ircutils.mircColor(string, 'light blue')

    def _orange(self, string):
        """Returns an orange string."""
        return ircutils.mircColor(string, 'orange')

    def _bold(self, string):
        """Returns a bold string."""
        return ircutils.bold(string)

    def _ul(self, string):
        """Returns an underline string."""
        return ircutils.underline(string)

    def _bu(self, string):
        """Returns a bold/underline string."""
        return ircutils.bold(ircutils.underline(string))

    ######################
    # INTERNAL FUNCTIONS #
    ######################

    def _size_fmt(self, num):
        for x in ['','k','M','B','T']:
            if num < 1000.0:
              return "%3.1f%s" % (num, x)
            num /= 1000.0

    def _myfloat(self, float_string):
        """It takes a float string ("1,23" or "1,234.567.890") and
        converts it to floating point number (1.23 or 1.234567890).
        """

        float_string = str(float_string)
        errormsg = "ValueError: Input must be decimal or integer string"
        try:
            if float_string.count(".") == 1 and float_string.count(",") == 0:
                return float(float_string)
            else:
                midle_string = list(float_string)
                while midle_string.count(".") != 0:
                    midle_string.remove(".")
                out_string = str.replace("".join(midle_string), ",", ".")
            return float(out_string)
        except ValueError as error:
            print("%s\n%s" %(errormsg, error))
            return None

    def _splitinput(self, txt, seps):
        default_sep = seps[0]
        for sep in seps[1:]:
            txt = txt.replace(sep, default_sep)
        return [i.strip() for i in txt.split(default_sep)]

    def _httpget(self, url, h=None, d=None, l=True):
        """General HTTP resource fetcher. Pass headers via h, data via d, and to log via l."""

        if self.registryValue('logURLs') and l:
            self.log.info(url)

        try:
            if h and d:
                page = utils.web.getUrl(url, headers=h, data=d)
            else:
                page = utils.web.getUrl(url)
            return page
        except Exception as e:
            self.log.error("ERROR opening {0} message: {1}".format(url, e))
            return None

    def ip(self, irc, msg, args, optip):
        """<ip.address>
        Use a GeoIP API to lookup the location of an IP.
        """

        url = 'http://www.telize.com/geoip/%s' % (optip)
        html = self._httpget(url)
        if not html:  # http fetch breaks.
            irc.reply("ERROR: Trying to open: {0}".format(url))
            return
        
        if sys.version_info[0] == 3:
            jsondata = json.loads(html.decode('utf-8'))
        else:
            jsondata = json.loads(html)

        isp = jsondata.get('isp')
	city = jsondata.get('city')
        country_code = jsondata.get('country_code')
        region = jsondata.get('region')
        longitude = jsondata.get('longitude')
        latitude = jsondata.get('latitude')
        ip = jsondata.get('ip')

        if ip:
            output = "IP: {0} | ISP: {1} | City: {2} | Region: {3}, {4} | Longitude: {5} | Latitude: {6}".format(self._bu(ip), isp, city, region, country_code, longitude, latitude)
            irc.reply(output)
        else:
            irc.reply("ERROR :: looking up '{0}' at {1}".format(optip, url))

    ip = wrap(ip, [('somethingWithoutSpaces')])

Class = IPLookup

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

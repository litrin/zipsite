#!/bin/env python
##
##	This is a project for Google App Engine 
##		that support create a webisite by ZIP packages!
##
##	By Litrin J. 2011/02
##	Website: www.litrin.net
##	Example: android-sdk.appspot.com
##

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.api import memcache
from DataStore import *
import time
import os
import logging


class xml(webapp.RequestHandler):
    
    XMLBody = ''
    
    def get(self):
        xml = memcache.get(self.request.path)
        
        if (xml is None) :
            
            xml = self.buildXml()
            memcache.add(self.request.path, xml, 60*60*24)
            
        self.response.headers['Content-Type'] = 'application/xml'
        self.response.out.write(xml)
        
        
    def getMaxLoad(self):
        DBHandle = DBCache.all()
        DBHandle.filter("MimeType = ", 'text/html').filter('Number = ', 0).order('-LoadCount').fetch(1)
        for Query in DBHandle:
            return Query.LoadCount 
    
    def buildXml(self):
        self.XMLBody = self.xmlHeader()
        offSet = 0
        count = self.buildElement(offSet)
        
        while (count == 1000):
            offSet += 1000
            count = self.buildElement(offSet)
            
        self.XMLBody += "</urlset>\n"
        
        return self.XMLBody
            
        
    def buildElement(self, offSet):
        maxLoadCount = float(self.getMaxLoad())
        DBHandle = DBCache.all()
        DBHandle.filter("MimeType = ", 'text/html').filter('Number = ', 0).order('-LoadCount').fetch(1000, offSet)
        
        i = 0 
        for Query in DBHandle:
            i += 1
            line="<url>\n"
            line+="\t<loc>" + self.request.host_url + Query.URL + "</loc>\n"

            timeString = str(Query.CreateTime.strftime('%Y-%m-%dT%H:%M:%S-08:00')) 
            line+="\t<lastmod>" + timeString + "</lastmod>\n"
            
            line+="\t<changefreq>weekly</changefreq>\n"
            
            priority = round( Query.LoadCount / maxLoadCount, 2 ) 
            if priority < 0.01 :
                priority = 0.01
            line+="\t<priority>" + str(priority) + "</priority>\n"
            
            line+="</url>\n"
            
            self.XMLBody += line
            
        return i
        
        
        
    def xmlHeader(self):
        header = "<?xml version='1.0' encoding='UTF-8'?>\n"
        header += "<?xml-stylesheet type=\"text/xsl\" href=\"/sitemap.xsl\"?>\n"
        header += "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\"\n"
        header += "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n"
        header += "xsi:schemaLocation=\"http://www.sitemaps.org/schemas/sitemap/0.9"
        header += "http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd\">\n"
        
        return header

        
class txt(webapp.RequestHandler):
    sitemapBody = ''
    def get(self):
        txt = memcache.get(self.request.path)

        if (txt is None) :
            
            txt = self.buildTxt()
            memcache.add(self.request.path, txt, 60*60*24)
            
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(txt)

    
    def buildTxt(self):
       
        offSet = 0
        count = self.buildTxtElement(offSet)
        
        while (count == 1000):
            offSet += 1000
            count = self.buildTxtElement(offSet)
            
        
        return self.sitemapBody
            
        
    def buildTxtElement(self, offSet):
        DBHandle = DBCache.all()
        DBHandle.filter("MimeType = ", 'text/html').filter('Number = ', 0).order('-LoadCount').fetch(1000, offSet)
        
        i = 0 
        for Query in DBHandle:
            self.sitemapBody += self.request.host_url + Query.URL  + '\n'
            
        return i
        

class xsl(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/xml'
        
        xsl = '''<xsl:stylesheet version="2.0" 
                xmlns:html="http://www.w3.org/TR/REC-html40"
                xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
	<xsl:template match="/">
		<html xmlns="http://www.w3.org/1999/xhtml">
			<head>
				<title>XML Sitemap</title>
				<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
				<style type="text/css">

					body {
						font-family:"Lucida Grande","Lucida Sans Unicode",Tahoma,Verdana;
						font-size:13px;
					}
					
					#intro {
						background-color:#CFEBF7;
						border:1px #2580B2 solid;
						padding:5px 13px 5px 13px;
						margin:10px;
					}
					
					#intro p {
						line-height:	16.8667px;
					}
					
					td {
						font-size:11px;
					}
					
					th {
						text-align:left;
						padding-right:30px;
						font-size:11px;
					}
					
					tr.high {
						background-color:whitesmoke;
					}
					
					#footer {
						padding:2px;
						margin:10px;
						font-size:8pt;
						color:gray;
					}
					
					#footer a {
						color:gray;
					}
					
					a {
						color:black;
					}
				</style>
			</head>
			<body>
				<h1>XML Sitemap</h1>
				<div id="intro">
					<p>
						This is a XML Sitemap which is supposed to be processed by search engines like <a href="http://www.google.com">Google</a>, <a href="http://search.msn.com">MSN Search</a> and <a href="http://www.yahoo.com">YAHOO</a>.<br />

						It was generated using <a href="http://code.google.com/p/zipsite/">zipSite</a> by <a href="http://www.litrin.net/">Litrin Jiang</a>.<br />
						You can find more information about XML sitemaps on <a href="http://sitemaps.org">sitemaps.org</a> and Google's <a href="http://code.google.com/sm_thirdparty.html">list of sitemap programs</a>.
					</p>

				</div>
				<div id="content">
					<table cellpadding="5">
						<tr style="border-bottom:1px black solid;">
							<th>URL</th>
							<th>Priority</th>
							<th>Change Frequency</th>

							<th>LastChange (GMT)</th>
						</tr>
						<xsl:variable name="lower" select="'abcdefghijklmnopqrstuvwxyz'"/>
						<xsl:variable name="upper" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>
						<xsl:for-each select="sitemap:urlset/sitemap:url">
							<tr>
								<xsl:if test="position() mod 2 != 1">
									<xsl:attribute  name="class">high</xsl:attribute>

								</xsl:if>
								<td>
									<xsl:variable name="itemURL">
										<xsl:value-of select="sitemap:loc"/>
									</xsl:variable>
									<a href="{$itemURL}">
										<xsl:value-of select="sitemap:loc"/>
									</a>
								</td>

								<td>
									<xsl:value-of select="concat(sitemap:priority*100,'%')"/>
								</td>
								<td>
									<xsl:value-of select="concat(translate(substring(sitemap:changefreq, 1, 1),concat($lower, $upper),concat($upper, $lower)),substring(sitemap:changefreq, 2))"/>
								</td>
								<td>
									<xsl:value-of select="concat(substring(sitemap:lastmod,0,11),concat(' ', substring(sitemap:lastmod,12,5)))"/>
								</td>

							</tr>
						</xsl:for-each>
					</table>
				</div>
				<div id="footer">
					Generated with <a href="http://code.google.com/p/zipsite/" title="zipsite">zipsite</a> by <a href="http://www.litrin.net/">Litrin Jiang</a>. This XSLT template is released under GPL.
				</div>

			</body>
		</html>
	</xsl:template>
</xsl:stylesheet>'''
        self.response.out.write(xsl)

def main():
    application = webapp.WSGIApplication([
                ('/sitemap.xsl', xsl),
                ('/sitemap.xml', xml),
                ('/sitemap.txt', txt),
                                    
            ], 
        debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()

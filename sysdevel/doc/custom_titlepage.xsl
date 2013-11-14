<?xml version='1.0'?>
<xsl:stylesheet  
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fo="http://www.w3.org/1999/XSL/Format"
    version="1.0">

  <!--
  Derived from the DocBook XSL Stylesheet distribution:

  Copyright
  *********
  Copyright (C) 1999-2007 Norman Walsh
  Copyright (C) 2003 Jiří Kosek
  Copyright (C) 2004-2007 Steve Ball
  Copyright (C) 2005-2008 The DocBook Project
  Copyright (C) 2011-2012 O'Reilly Media

  Permission is hereby granted, free of charge, to any person
  obtaining a copy of this software and associated documentation
  files (the ``Software''), to deal in the Software without
  restriction, including without limitation the rights to use,
  copy, modify, merge, publish, distribute, sublicense, and/or
  sell copies of the Software, and to permit persons to whom the
  Software is furnished to do so, subject to the following
  conditions:

  The above copyright notice and this permission notice shall be
  included in all copies or substantial portions of the Software.

  Except as contained in this notice, the names of individuals
  credited with contribution to this software shall not be used in
  advertising or otherwise to promote the sale, use or other
  dealings in this Software without prior written authorization
  from the individuals in question.

  Any stylesheet derived from this Software that is publically
  distributed will be identified with a different name and the
  version strings in any derived Software will be changed so that
  no possibility of confusion between the derived package and this
  Software will exist.

  Warranty
  ********
  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT.  IN NO EVENT SHALL NORMAN WALSH OR ANY OTHER
  CONTRIBUTOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
  OTHER DEALINGS IN THE SOFTWARE.

  Contacting the Author
  *********************
  The DocBook XSL stylesheets are maintained by Norman Walsh,
  <ndw@nwalsh.com>, and members of the DocBook Project,
  <docbook-developers@sf.net>


  Modifications:

  Copyright 2013.  Los Alamos National Security, LLC.

  This material was produced under U.S. Government contract
  DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which
  is operated by Los Alamos National Security, LLC for the
  U.S. Department of Energy. The U.S. Government has rights to use,
  reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR
  LOS ALAMOS NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR
  IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If
  software is modified to produce derivative works, such modified
  software should be clearly marked, so as not to confuse it with the
  version available from LANL.

  Licensed under the Mozilla Public License, Version 2.0 (the
  "License"); you may not use this file except in compliance with the
  License. You may obtain a copy of the License at
  http://www.mozilla.org/MPL/2.0/

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
  implied. See the License for the specific language governing
  permissions and limitations under the License.
  -->

  <!-- title page image -->
  <xsl:param name="cover_image"/>

  <!-- custom titlepage with image -->
  <xsl:template name="user.pagemasters">
    <xsl:variable name="image_path">
      <xsl:choose>
	<xsl:when test="$cover_image">
	  <xsl:value-of select="$cover_image"/>
	</xsl:when>
	<xsl:otherwise>http://docbook.sourceforge.net/release/images/blank.png</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <fo:page-sequence-master
	master-name="custom-titlepage">
      <fo:repeatable-page-master-alternatives>
	<fo:conditional-page-master-reference
	    master-reference="blank"
	    blank-or-not-blank="blank"/>
	<fo:conditional-page-master-reference
	    master-reference="custom-titlepage-first"
	    page-position="first"/>
	<fo:conditional-page-master-reference
	    master-reference="custom-titlepage-odd"
	    odd-or-even="odd"/>
	<fo:conditional-page-master-reference odd-or-even="even">
          <xsl:attribute name="master-reference">
            <xsl:choose>
              <xsl:when test="$double.sided != 0">titlepage-even</xsl:when>
              <xsl:otherwise>titlepage-odd</xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
	</fo:conditional-page-master-reference>
      </fo:repeatable-page-master-alternatives>
    </fo:page-sequence-master>
    
    <fo:simple-page-master
	master-name="custom-titlepage-first"
	page-width="{$page.width}"
	page-height="{$page.height}"
	margin-top="0mm"
	margin-bottom="0mm"
	margin-left="0mm"
	margin-right="0mm">
      <xsl:if test="$axf.extensions != 0">
	<xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">blank</xsl:with-param>
	</xsl:call-template>
      </xsl:if>
      <fo:region-body
	  margin="0cm"
	  column-gap="{$column.gap.titlepage}"
	  column-count="{$column.count.titlepage}">
	<xsl:attribute name="background-image">
          <xsl:call-template name="fo-external-image">
	    <xsl:with-param name="filename">
	      <xsl:value-of select="$image_path"/>
	    </xsl:with-param>
          </xsl:call-template>
	</xsl:attribute>
	<xsl:attribute name="background-attachment">fixed</xsl:attribute>
	<xsl:attribute name="background-position-horizontal">center</xsl:attribute>
	<xsl:attribute name="background-repeat">no-repeat</xsl:attribute>
	<xsl:attribute name="background-position-vertical">center</xsl:attribute>
      </fo:region-body>
      <fo:region-before
	  region-name="xsl-region-before-first"
	  extent="-20mm"
	  display-align="before"/>
      <fo:region-after
	  region-name="xsl-region-after-first"
	  extent="-20mm"
	  display-align="after"/>
    </fo:simple-page-master>
    
    <fo:simple-page-master
	master-name="custom-titlepage-odd"
	page-width="{$page.width}"
	page-height="{$page.height}"
	margin-top="{$page.margin.top}"
	margin-bottom="{$page.margin.bottom}"
	margin-left="{$page.margin.inner}"
	margin-right="{$page.margin.outer}">
      <xsl:if test="$axf.extensions != 0">
	<xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">blank</xsl:with-param>
	</xsl:call-template>
      </xsl:if>
      <fo:region-body
	  margin-bottom="{$body.margin.bottom}"
	  margin-top="{$body.margin.top}"
	  column-gap="{$column.gap.titlepage}"
	  column-count="{$column.count.titlepage}">
      </fo:region-body>
      <fo:region-before
	  region-name="xsl-region-before-odd"
	  extent="{$region.before.extent}"
	  display-align="before"/>
      <fo:region-after
	  region-name="xsl-region-after-odd"
	  extent="{$region.after.extent}"
	  display-align="after"/>
    </fo:simple-page-master>
    
    <fo:simple-page-master
	master-name="custom-titlepage-even"
	page-width="{$page.width}"
	page-height="{$page.height}"
	margin-top="{$page.margin.top}"
	margin-bottom="{$page.margin.bottom}"
	margin-left="{$page.margin.outer}"
	margin-right="{$page.margin.inner}">
      <xsl:if test="$axf.extensions != 0">
	<xsl:call-template name="axf-page-master-properties">
          <xsl:with-param name="page.master">blank</xsl:with-param>
	</xsl:call-template>
      </xsl:if>
      <fo:region-body
	  margin-bottom="{$body.margin.bottom}"
	  margin-top="{$body.margin.top}"
	  column-gap="{$column.gap.titlepage}"
	  column-count="{$column.count.titlepage}">
      </fo:region-body>
      <fo:region-before
	  region-name="xsl-region-before-even"
	  extent="{$region.before.extent}"
	  display-align="before"/>
      <fo:region-after
	  region-name="xsl-region-after-even"
	  extent="{$region.after.extent}"
	  display-align="after"/>
    </fo:simple-page-master>
  </xsl:template>

  <xsl:template name="select.user.pagemaster">
    <xsl:param name="element"/>
    <xsl:param name="pageclass"/>
    <xsl:param name="default-pagemaster"/>
    <xsl:choose>
      <xsl:when test="$default-pagemaster = 'titlepage'">
	<xsl:value-of select="'custom-titlepage'"/>
      </xsl:when>
      <xsl:otherwise>
	<xsl:value-of select="$default-pagemaster"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet> 

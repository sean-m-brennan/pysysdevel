<?xml version='1.0'?>
<xsl:stylesheet  
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    version="1.0">

  <!-- Catalog resolver finds this -->
  <xsl:import href="http://docbook.sourceforge.net/release/xsl-ns/current/fo/docbook.xsl"/>

  <xsl:import href="custom_titlepage.xsl"/>

  <!-- If 'yes', this adds a watermark. -->
  <xsl:param name="draft.mode" select="no"/>

  <!--
  <xsl:param name="cover_image">pysysdevel_cover.png</xsl:param>
  -->

  <!-- page break before the table of contents and each chapter. -->
  <xsl:attribute-set name="toc.margin.properties">
    <xsl:attribute name="break-before">page</xsl:attribute>
  </xsl:attribute-set>
  <xsl:attribute-set name="section.level1.properties">
    <xsl:attribute name="break-before">page</xsl:attribute>
  </xsl:attribute-set>

</xsl:stylesheet> 

<?xml version='1.0'?>
<xsl:stylesheet  
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    version="1.0">

  <!-- Ideally, use the latest stylesheets.
  <xsl:import href="http://docbook.sourceforge.net/release/xsl/current/fo/docbook.xsl"/>
  -->
  <!-- Saxon doesn't support http proxies by default, so use a local tree.
       Typically, just symlink to /usr/share/sgml/docbook/xsl-ns-stylesheets. -->
  <xsl:import href="xsl-stylesheets/fo/docbook.xsl"/>

  <xsl:import href="../support/custom_titlepage.xsl"/>

  <!-- Uncomment and adjust if using a local tree. -->
  <xsl:param name="xsl_base_path">xsl-stylesheets</xsl:param>

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

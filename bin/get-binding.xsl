<!-- Timothy Lebo -->
<xsl:transform version="2.0" 
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
   xmlns:sr="http://www.w3.org/2005/sparql-results#"
   exclude-result-prefixes="">

<xsl:output method="text"/>
<xsl:param name="name"/>

<xsl:template match="/">
   <xsl:apply-templates select="sr:sparql/sr:results/sr:result/sr:binding[@name=$name]"/>
</xsl:template>

<xsl:template match="sr:uri | sr:literal">
   <xsl:value-of select="concat(text(),$NL)"/>
</xsl:template>

<xsl:variable name="NL" select="'&#xa;'"/>

</xsl:transform>

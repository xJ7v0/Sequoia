class BuisnessWire:
   def get_news(self, ticker, useragent):
      headers = {"User-Agent": useragent}
      page = requests.get("https://www.businesswire.com/portal/site/home/template.BINARYPORTLET/search/resource.process/?javax.portlet.tpst=92055fbcbec7e639f1f554100d908a0c&javax.portlet.rst_92055fbcbec7e639f1f554100d908a0c_searchTerm=" + ticker + "&javax.portlet.rst_92055fbcbec7e639f1f554100d908a0c_resultsPage=1&javax.portlet.rst_92055fbcbec7e639f1f554100d908a0c_searchType=news&javax.portlet.rid_92055fbcbec7e639f1f554100d908a0c=searchPaging&javax.portlet.rcl_92055fbcbec7e639f1f554100d908a0c=cacheLevelPage&javax.portlet.begCacheTok=com.vignette.cachetoken&javax.portlet.endCacheTok=com.vignette.cachetoken", headers=headers)

      tree = html.fromstring(page.content)
      url = tree.xpath('//ul[@class="bw-news-list"]/li/h3/a/@href')
      headline = tree.xpath('//ul[@class="bw-news-list"]/li/h3/a/text()')
      date = tree.xpath('//ul[@class="bw-news-list"]/li/div[@class="bw-news-meta"]/time/text()')

      print(f"URL: {url}")
      print(f"Headline: {headline}")
      print(f"Date: {date}")

#!/usr/bin/env python
# coding: utf-8

# <h1 align=center><font size = 6>Crawl EdgeProperty Data</font></h1>

# ## Introduction
# 
# The purpose of this notebook is to crawl Edge Property data, you can refer this link for more details: [Edgeprop singapore](https://www.edgeprop.sg/property-search?listing_type=sale&property_type=&district=&bedroom_min=&asking_price_min=&asking_price_max=&floor_area_min=&floor_area_max=&land_area_min=&land_area_max=&tenure=&bathroom=&furnishing=&completed=&level=&completion_year_min=&completion_year_max=&rental_yield=&high_rental_volume=&high_sales_volume=&deals=&nearby_amenities=&amenities_distance=500&rental_type=&keyword_features=&keyword=&mrt_keywords=&school_keywords=&asset_id=&resource_type=&x=&y=&radius=1000&search_by=&search_by_distance=&search_by_location=&search_by_showmap=true&below_valuation=&map_zoom=&asset_lat=&asset_lng=&page=1&pageSize=10&order_by=recommended&is_search=true&v360=0&fittings=&saved_search_id=)
# 
# Since run all the cells again will consume too much time, I cleared all the output in the notebook.
# 
# ---

# ## Table of Contents
# 
# <div class="alert alert-block alert-info" style="margin-top: 20px">
# 
# 1. [Import Libraries](#0)<br>
# 2. [Collect all the pages' URL and get all Child links](#1)<br>
# 3. [Crawl Basic Property information from Child links and write to csv](#2) <br>
# </div>
# <hr>

# ## Import Libraries <a id="0"></a>

# In[ ]:


import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from requests.exceptions import ConnectionError
import csv
from lxml import html


# ## Collect all the pages' URL and get all Child links <a id="1"></a>

# In[ ]:


list_url = []
for i in range(1,2449): # 2449 subpages in total
    url = 'https://www.edgeprop.sg/property-search?listing_type=sale&property_type=&district=&bedroom_min=&asking_price_min=&asking_price_max=&floor_area_min=&floor_area_max=&land_area_min=&land_area_max=&tenure=&bathroom=&furnishing=&completed=&level=&completion_year_min=&completion_year_max=&rental_yield=&high_rental_volume=&high_sales_volume=&deals=&nearby_amenities=&amenities_distance=500&rental_type=&keyword_features=&keyword=&mrt_keywords=&school_keywords=&asset_id=&resource_type=&x=&y=&radius=1000&search_by=&search_by_distance=&search_by_location=&search_by_showmap=true&below_valuation=&map_zoom=&asset_lat=&asset_lng=&page='+str(i)+'&pageSize=10&order_by=recommended&is_search=true&v360=0&fittings=&saved_search_id='
    list_url.append(url)


# In[ ]:


len(list_url)


# In[ ]:


list_url[1]


# In[ ]:


# Request
list_soup = []
list_coverpage_properties = []

for url in list_url:
    try:
        r = requests.get(url)
    except ConnectionError as e:
        print(e)
    r.status_code
    coverpage = r.content
    
    soup = BeautifulSoup(coverpage, 'html')
    list_soup.append(soup)
    
    coverpage_properties = soup.find_all('div', class_="imgClick")
    list_coverpage_properties.extend(coverpage_properties)


# In[ ]:


# Empty lists for content, links and titles

list_child_links = []

for n in range(0, len(list_coverpage_properties)):
    if list_coverpage_properties[n].find('a') is not None:
        link = list_coverpage_properties[n].find('a')['href'] 
        list_child_links.append(link)
        # remove duplicates
        list_child_links = list(dict.fromkeys(list_child_links))


# In[ ]:


print("The number of all the pages is:", len(list_soup) , "\n" "The number of Child links is:", len(list_child_links))


# ## Crawl Basic Property information from Child links and write to csv  <a id="2"></a>

# In[ ]:


dict = []

for url in list_child_links:
    dic = {}
    page=requests.Session().get(url) 
    tree=html.fromstring(page.text) 
    try:
        title=tree.xpath('//h[@class="listing-details columns"]//span/text()') 
        price = tree.xpath('//div[@class="calculator-content-text text"]//span/text()')
        detail = tree.xpath('//div[@class="listing-icon-content"]//span[@class="show"]/text()') 
        detail2 = tree.xpath('//div[@class="right-content columns"]//span/text()') 
        dic['Name']=title
        dic['Bed']=detail[0]
        dic['Bath']=detail[1]
        dic['Type']=detail2[0]
        dic['Tenure']=detail2[1]
        dic['Psf']=detail2[2]
        dic['Floor']=detail2[3]
        dic['Top']=detail2[4]
        dic['Relisted']=detail2[5]
        dic['Furnish']=detail2[6]
        dic['Size']=detail2[7]
        dic['Price']=price[0]
        if len(price)>1 and price[1].rfind('Fair Value')>=0:
            dic['Fairvalue']=price[1]
        else:
            dic['Fairvalue']='-'
    except:
        print(url)
    dict.append(dic)

    # print(dict)


# In[ ]:


csv_columns = ['Address','Postcode','Name','Bed','Bath','Type','Tenure','Psf','Floor','Top','Relisted','Furnish','Size','Price','Fairvalue', 'URL']
with open('EdgeProp_Data.csv', 'w', newline='') as csvfile:
    fields = ['Address','Postcode', 'Name','Bed','Bath','Type','Tenure','Psf','Floor','Top','Relisted','Furnish','Size','Price','Fairvalue', 'URL']

    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()

    for row in dict:
        writer.writerow(row)


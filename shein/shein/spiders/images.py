import scrapy
import pandas as pd
import json
from ..items import SheinItem


df = pd.read_excel('shein.xlsx')

urls = df['link'].values.tolist()

class ImagesSpider(scrapy.Spider):
    name = 'images'
    allowed_domains = ['ar.shein.com']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'FEEDS':{
            'shein_jpg_links.csv':{
                'format':'csv',
                'overwrite':True
            }
        }
    }
    def start_requests(self):
        for link in urls:
           
            target=link.split('-p-')[1]
            slug=target.split('-')[0]
            
            url = "https://ar.shein.com/api/productAtom/atomicInfo/get?_ver=1.1.8&_lang=ar"

           

            payload = {
                "atomicParams": [{"goods_id": slug}],
                "fields": {"detailImage": True}
            }
            
            headers = {
                #"cookie": "default_currency=SAR; language=ar; cookieId=E785963D_4AF9_D9E4_C3AB_4C89F44501C5; sessionID_shein=s%253APkI5cPnaQWnloXk7lryBR6GAUu8h0tbe.A8JePkdVlj7u33jzQuiNz7qOlOJUuMJNDx%252FEiZHRZ3E",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
            }
            
            meta ={
                'slug':slug,
                'link':link
            }
            yield scrapy.Request(method='POST',url=url,body=json.dumps(payload),headers=headers,meta=meta)


    def parse(self, response):
        items = SheinItem()
        
        slug=response.meta.get('slug')
        data = response.json()
        
        for counter , i in enumerate(data['data'][f'{slug}']['detail_image'],start=1):
            image_url=i['origin_image']
            image_url=image_url.strip().replace('//','')
            
            items['link'] = response.meta.get('link')
            items[f'image{counter}'] = image_url
            
        yield items
            

        
        

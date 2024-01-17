import scrapy
import pandas as pd
import json
from ..items import SheinItem
from inline_requests import inline_requests
from urllib.parse import urlencode

API_KEY = 'ff3cc8159137f06335075d726050e683'


df = pd.read_excel('shein.xlsx')

#urls = df['link'].values.tolist()
data_dict = df.to_dict('records')
class ImagesSpider(scrapy.Spider):
    name = 'images'
    allowed_domains = ['ar.shein.com','shein.com','api.scraperapi.com']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'ROBOTSTXT_OBEY': False,
        'FEEDS':{
            'shein_jpg_links.csv':{
                'format':'csv',
                'overwrite':True
            }
        }
    }
    
    def start_requests(self):
        for product in data_dict[0:5]:
           
            target=product['link'].split('-p-')[1]
            
            en_link =  product['link'].replace('ar.','')
            

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
                'link':product['link'],
                'sku':product['SKU'],
                'color':product['color'],
                'size':product['size'],
                'column1':product['Column1'],
                'en_link':en_link
            }
            yield scrapy.Request(method='POST',url=url,body=json.dumps(payload),headers=headers,meta=meta)

    @inline_requests
    def parse(self, response):
        sku = response.meta.get('sku')
        color = response.meta.get('color')
        size = response.meta.get('size')
        slug=response.meta.get('slug')
        en_url = "https://www.shein.com/api/productInfo/quickView/get/?"
        ar_url = "https://ar.shein.com/api/productInfo/quickView/get/?"
        
        en_payload = { 'api_key': f'{API_KEY}', 'url': f'https://www.shein.com/api/productInfo/quickView/get/?_ver=1.1.8&_lang=en&goods_id={slug}&mallCode=1&lockmall=0&isQuick=1' } 
        ar_payload = { 'api_key': f'{API_KEY}', 'url': f'https://ar.shein.com/api/productInfo/quickView/get/?_ver=1.1.8&_lang=en&goods_id={slug}&mallCode=1&lockmall=0&isQuick=1' } 
        #{'api_key': 'APIKEY', 'url': 'https://httpbin.org/ip'}
        #querystring = {"_ver":"1.1.8","_lang":"en","goods_id":f"{slug}","mallCode":"1","lockmall":"0","isQuick":"1"}
        scraper_url = 'https://api.scraperapi.com/?'
        
        en_full = scraper_url + urlencode(en_payload)
        
        ar_full =  scraper_url + urlencode(ar_payload) 
        
        #en_link = response.meta.get('en_link')
        headers = {
        "cookie": "_abck=0F6E2B4B28F0264F947F7DEC81B4F882~-1~YAAQT6ERAuU7ru2MAQAA8b0K9gtv%2Ftqzp%2Bvb%2F%2BQ6aRJmsnXsiOf%2FQl7WPA4t5hpLa4TReWmBHwcLuPKYTKHYz0SIo8Xv%2FQq6%2B4cEbT1pJSJ35TtaKguq00cZvg12D1TJZHeDBDwIkAjrwllQS%2FrUkBBUbdd0r5964jw%2Bm%2BfWnTuTW6hQ9hV8BcLZn4R2MsIozB7GtK6Ky3xCm%2FFOFgW5c7iAUDvSsgiyb%2BeVC7yovU94h1vKkx7UtFqKTxFm01sLqDz9rmw2YlHWhO2bY6jNro29jXCoNcvB8kYCxg7MBrcvfpl5%2Fv4wJp0H9lzqoh6bhLKR8yMh%2BXiuJCBiWUdWu2KjEgr5Xb2HX47J3kIJ5UMz8WSIlgepeQsp%2FsGhM%2BS9w77y19dCnTrj41tQTaDi5sYdwhvm%2BBc%3D~-1~-1~-1; sessionID_shein=s%253AxaNR1NGfazVpK_8QCGwJQey4693Hthn1.J93FnHnn8MrKxqmxvXYDtX6L12Q%252FqQUtH2nmzzU2zJI",
        "authority": "www.shein.com",
        "accept": "application/json, text/plain, */*",
        "referer": "https://www.shein.com/cart",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
        
        #print(en_full)
        

        
        en_page_resp = yield scrapy.Request(en_full,headers=headers)
        
        ar_page_resp =  yield scrapy.Request(ar_full,headers=headers)

        
        en_data = en_page_resp.json()
        
        ar_data = ar_page_resp.json()
        
        ar_name =''
        
        en_name =''
        
        category = ''
        
        en_description_list = []
        ar_description_list = []
        try:
            en_name = en_data['info']['goods']['detail']['goods_name']
                        
            ar_name = ar_data['info']['goods']['detail']['goods_name']
            
            category = en_data['info']['goods']['currentCat']['cat_name']
            
            for i in en_data['info']['goods']['detail']['productDetails']:
                key = i['attr_name']
                value = i['attr_value']
                
                desc_items = f'{key}: {value}\n'
                
                en_description_list.append(desc_items)
            
        
            for i in ar_data['info']['goods']['detail']['productDetails']:
                key = i['attr_name']
                value = i['attr_value']
                
                desc_items = f'{key}: {value}\n'
                
                ar_description_list.append(desc_items)
        except KeyError as e:
            try:
                self.logger.error(f"KeyError: {e}. Retrying the request.")
                en_page_resp = yield scrapy.Request(en_full,headers=headers)
            
                ar_page_resp =  yield scrapy.Request(ar_full,headers=headers)

                
                en_data = en_page_resp.json()
                
                ar_data = ar_page_resp.json()
                en_name = en_data['info']['goods']['detail']['goods_name']
                
                category = en_data['info']['goods']['currentCat']['cat_name']
                            
                ar_name = ar_data['info']['goods']['detail']['goods_name']
                for i in en_data['info']['goods']['detail']['productDetails']:
                    key = i['attr_name']
                    value = i['attr_value']
                    
                    desc_items = f'{key}: {value}\n'
                    
                    en_description_list.append(desc_items)
                
            
                for i in ar_data['info']['goods']['detail']['productDetails']:
                    key = i['attr_name']
                    value = i['attr_value']
                    
                    desc_items = f'{key}: {value}\n'
                    
                    ar_description_list.append(desc_items)
            except KeyError as second_e:
                    self.logger.error(f"KeyError: {second_e}. Retrying the second request.")
                    en_page_resp = yield scrapy.Request(en_full,headers=headers)
                
                    ar_page_resp =  yield scrapy.Request(ar_full,headers=headers)

                    
                    en_data = en_page_resp.json()
                    
                    ar_data = ar_page_resp.json()
                    en_name = en_data['info']['goods']['detail']['goods_name']
                    
                    category = en_data['info']['goods']['currentCat']['cat_name']
                                
                    ar_name = ar_data['info']['goods']['detail']['goods_name']
                    for i in en_data['info']['goods']['detail']['productDetails']:
                        key = i['attr_name']
                        value = i['attr_value']
                        
                        desc_items = f'{key}: {value}\n'
                        
                        en_description_list.append(desc_items)
                    
                
                    for i in ar_data['info']['goods']['detail']['productDetails']:
                        key = i['attr_name']
                        value = i['attr_value']
                        
                        desc_items = f'{key}: {value}\n'
                        
                        ar_description_list.append(desc_items)        
                
            
            

        items = SheinItem()
        
        items['product_name_arabic'] = ar_name
        items['product_name_eng'] = en_name
        items['category'] = category
        items['sku'] = response.meta.get('sku')
        items['size'] = size
        
        items['product_code'] = f'{sku}-{size}-{color}'
        items['color'] = response.meta.get('color')
        items['column1'] = response.meta.get('column1')
        items['desc_en'] = ''.join(en_description_list)
        items['desc_ar'] = ''.join(ar_description_list)
        
        
        data = response.json()
        main_image = data['data'][f'{slug}']['main_image']['origin_image']
        for counter , i in enumerate(data['data'][f'{slug}']['detail_image'],start=1):
            image_url=i['origin_image']
            image_url=image_url.strip().replace('//','')
            
            items['link'] = response.meta.get('link')
            items[f'image{counter}'] = image_url
            
        items['main_image']= main_image.replace('//','')
        yield items

 


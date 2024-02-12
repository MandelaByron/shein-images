import scrapy
import pandas as pd
import json
from ..items import SheinItem
from inline_requests import inline_requests
from urllib.parse import urlencode
from .browser import main
import re
from .config import api_key
import requests
import traceback

order_data , cookies = main()

API_KEY = api_key





df = pd.DataFrame(order_data)

#sku_list=df['SKU'].values.tolist()
# Assuming df is your DataFrame with columns 'SKU' and 'SIZE'
# Group by 'SKU' and calculate the size of each group to get the quantity (QTY)
# df['QTY'] = df.groupby('SKU')['size'].transform('size')



# df = df.drop_duplicates().reset_index(drop=True)

#print(df)
# Create a new column 'PRODUCT_CODE' by combining 'SKU' and 'SIZE'
df['PRODUCT_CODE'] = df['SKU'] + '-' + df['size']

# Add a new column 'QTY' based on unique 'PRODUCT_CODE's
df['QTY'] = df.groupby('PRODUCT_CODE').transform('size')
df = df.drop_duplicates(subset=['PRODUCT_CODE']).reset_index(drop=True)
print(df)



def extract_product_id(url):
    # Define a regular expression pattern to match the product id in the URL
    pattern = re.compile(r'-p-(\d+)(?:-cat-|\.)')

    # Use the pattern to find the match in the URL
    match = pattern.search(url)

    # Check if a match is found
    if match:
        # Extract and return the product id
        product_id = match.group(1)
        return product_id
    else:
        # Return None if no match is found
        return None

#df = pd.read_excel('shein.xlsx')

#urls = df['link'].values.tolist()
#data_dict = df.to_dict('records')
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
        #print(len(order_data))
        for index, product in df.iterrows():
            #print(product)
            slug = extract_product_id(product['link'])

            qty = product['QTY']
            
            size = product['size']
            
            sku = product['SKU']
            #qty = sku_list.count(product['SKU'])
            
            meta ={
                'slug':slug,
                'link':product['link'],
                'sku':product['SKU'],
                'size':size,
                'qty':qty,
                'purchased_price':product['price'],

            }
      
            yield scrapy.Request(url=product['link'].replace("www",'ar'),cookies=cookies,meta=meta, errback=self.handle_error)
            
    def handle_error(self, failure):
        # Handle non-200 responses here
        if failure.check(scrapy.spidermiddlewares.httperror.HttpError):
            response = failure.value.response
            if response.status == 404:
                self.log(f'404 Error on page: {response.url}')
                # Continue processing even on 404
            else:
                # Handle other non-404 errors if needed
                self.log(f'Error on page: {response.url}, Status Code: {response.status}')
        else:
            # Handle other types of errors if needed
            self.log(f'Error: {failure.value}')
            
    def make_request(self, url, headers, payload=None):
        with requests.Session() as session:
            response = session.get(url, headers=headers, params=payload)
        response.raise_for_status()
        return response

    @inline_requests
    def parse(self, response):
        sku = response.meta.get('sku')
        
        
        
        size = response.meta.get('size')
        
        slug=response.meta.get('slug')

        
        en_payload = { 'api_key': f'{API_KEY}', 'url': f'https://www.shein.com/api/productInfo/quickView/get/?_ver=1.1.8&_lang=en&goods_id={slug}&mallCode=1&lockmall=0&isQuick=1','country_code':'us' } 
        ar_payload = { 'api_key': f'{API_KEY}', 'url': f'https://ar.shein.com/api/productInfo/quickView/get/?_ver=1.1.8&_lang=en&goods_id={slug}&mallCode=1&lockmall=0&isQuick=1' } 

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


        
        items = SheinItem()
        items['link'] = response.meta.get('link')
        items['sku'] = response.meta.get('sku')
        items['price'] = response.meta.get('purchased_price')
        items['qty'] = response.meta.get('qty')
        items['size'] = size
        try:
            en_page_resp = yield scrapy.Request(en_full,headers=headers)
        
            ar_page_resp =  yield scrapy.Request(ar_full,headers=headers)


            en_data = en_page_resp.json()
            
            ar_data = ar_page_resp.json()
            
            ar_name =''
            
            en_name =''
            
            category = ''
            
            color = ''
            
            en_description_list = []
            
            ar_description_list = []
            
            size_list = []

            if 'msg' in en_data and en_data['msg'] == 'goods not exist':
                en_name =ar_data['info']['goods']['detail']['goods_url_name']         
               
                ar_name = ar_data['info']['goods']['detail']['goods_name']
                
                category = ar_data['info']['goods']['currentCat']['cat_url_name']
                
                color = ar_data['info']['goods']['detail']['mainSaleAttribute'][0]['attr_value_en']
                
                
                for i in ar_data['info']['goods']['detail']['productDetails']:
                    key = i['attr_name_en']
                    value = i['attr_value_en']
                    
                    desc_items = f'{key}: {value}\n'
                    
                    en_description_list.append(desc_items)
                    
                for i in ar_data['info']['goods']['detail']['productDetails']:
                    key = i['attr_name']
                    value = i['attr_value']
                    
                    desc_items = f'{key}: {value}\n'
                    
                    ar_description_list.append(desc_items)
                
                size_data = ar_data['info']['goods']['attrSizeList']['sale_attr_list'][f'{slug}']['sku_list']
                for counter, i in enumerate(size_data):
                    stock = i['stock']
                    try:
                        size_name = i['sku_sale_attr'][0]['attr_value_name_en']
                    except:
                        size_name = "one-size"
                    
                    size_list.append(
                        {
                            "size":size_name,
                            "stock":stock
                        }
                    )
            else:
             
            
                en_name = en_data['info']['goods']['detail']['goods_name']           
                ar_name = ar_data['info']['goods']['detail']['goods_name']
                
                category = en_data['info']['goods']['currentCat']['cat_name']
                
                color = en_data['info']['goods']['detail']['mainSaleAttribute'][0]['attr_value_en']
                
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
                
                    
                size_data = en_data['info']['goods']['attrSizeList']['sale_attr_list'][f'{slug}']['sku_list']
                for counter, i in enumerate(size_data):
                    stock = i['stock']
                    try:
                        size_name = i['sku_sale_attr'][0]['attr_value_name_en']
                    except:
                        size_name = "one-size"
                    
                    size_list.append(
                        {
                            "size":size_name,
                            "stock":stock
                        }
                    )
            

            
            
            items['product_name_arabic'] = ar_name
            items['product_name_eng'] = en_name
            items['category'] = category

            items['color'] = color
            items['desc_en'] = ''.join(en_description_list)
            items['desc_ar'] = ''.join(ar_description_list)
            main_image = ar_data['info']['goods']['goods_imgs']['main_image']['origin_image']
            items['image1']= 'https://' + main_image.replace('//','')
            
            
            for counter , i in enumerate(ar_data['info']['goods']['goods_imgs']['detail_image'],start=2):
                if counter <= 10:
                    image_url=i['origin_image']
                    image_url=image_url.strip().replace('//','')
                    
                    
                    items[f'image{counter}'] = 'https://' + image_url
                    items['product_code'] = f"{sku}-{size}-{color}"#checkig
                    items['size'] = size
                    #items['stock'] = size['stock']
            yield items           
                        
        except Exception as e:
            try:
                print("Retrying --- error ---",e)
                #traceback.print_exc()
                en_page_resp = self.make_request(en_full,headers=headers)
            
                ar_page_resp =  self.make_request(ar_full,headers=headers)


                en_data = en_page_resp.json()
                
                #print(en_data)
                ar_data = ar_page_resp.json()
                
                ar_name =''
                
                en_name =''
                
                category = ''
                
                color = ''
                
                en_description_list = []
                ar_description_list = []
                
                size_list = []
            
                if 'msg' in en_data and en_data['msg'] == 'goods not exist':
                    
                    en_name =ar_data['info']['goods']['detail']['goods_url_name']         
                
                    ar_name = ar_data['info']['goods']['detail']['goods_name']
                    
                    category = ar_data['info']['goods']['currentCat']['cat_url_name']
                    
                    color = ar_data['info']['goods']['detail']['mainSaleAttribute'][0]['attr_value_en']
                    
                    
                    for i in ar_data['info']['goods']['detail']['productDetails']:
                        key = i['attr_name_en']
                        value = i['attr_value_en']
                        
                        desc_items = f'{key}: {value}\n'
                        
                        en_description_list.append(desc_items)
                        
                    for i in ar_data['info']['goods']['detail']['productDetails']:
                        key = i['attr_name']
                        value = i['attr_value']
                        
                        desc_items = f'{key}: {value}\n'
                        
                        ar_description_list.append(desc_items)
                    
                    size_data = ar_data['info']['goods']['attrSizeList']['sale_attr_list'][f'{slug}']['sku_list']
                    for counter, i in enumerate(size_data):
                        stock = i['stock']
                        try:
                            size_name = i['sku_sale_attr'][0]['attr_value_name_en']
                        except:
                            size_name = "one-size"
                        
                        size_list.append(
                            {
                                "size":size_name,
                                "stock":stock
                            }
                        )
                else:
                
                
                    en_name = en_data['info']['goods']['detail']['goods_name']           
                    ar_name = ar_data['info']['goods']['detail']['goods_name']
                    
                    category = en_data['info']['goods']['currentCat']['cat_name']
                    
                    color = en_data['info']['goods']['detail']['mainSaleAttribute'][0]['attr_value_en']
                    
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
                    
                        
                    size_data = en_data['info']['goods']['attrSizeList']['sale_attr_list'][f'{slug}']['sku_list']
                    for counter, i in enumerate(size_data):
                        stock = i['stock']
                        try:
                            size_name = i['sku_sale_attr'][0]['attr_value_name_en']
                        except:
                            size_name = "one-size"
                        
                        size_list.append(
                            {
                                "size":size_name,
                                "stock":stock
                            }
                        )
                    

                
                
                items['product_name_arabic'] = ar_name
                items['product_name_eng'] = en_name
                items['category'] = category
                items['sku'] = response.meta.get('sku')
                items['price'] = response.meta.get('purchased_price')
                items['qty'] = response.meta.get('qty')
                items['color'] = color
                items['desc_en'] = ''.join(en_description_list)
                items['desc_ar'] = ''.join(ar_description_list)
                main_image = ar_data['info']['goods']['goods_imgs']['main_image']['origin_image']
                items['image1']= 'https://' + main_image.replace('//','')
                
                
                for counter , i in enumerate(ar_data['info']['goods']['goods_imgs']['detail_image'],start=2):
                    if counter <= 10:
                        image_url=i['origin_image']
                        image_url=image_url.strip().replace('//','')
                        #size = size['size']
                        items['link'] = response.meta.get('link')
                        items[f'image{counter}'] = 'https://' + image_url
                        items['product_code'] = f"{sku}-{size}-{color}"#checkig
                        items['size'] = size
                        #items['stock'] = size['stock']
                #print(items)
                self.log(f"items_--{items}")
                yield items  
            except Exception as e:
                print("caught exception--retrying",e)
                try:
                    
                    #traceback.print_exc()
                    en_page_resp = self.make_request(en_full,headers=headers)
                
                    ar_page_resp =  self.make_request(ar_full,headers=headers)


                    en_data = en_page_resp.json()
                    
                    #print(en_data)
                    ar_data = ar_page_resp.json()
                    
                    ar_name =''
                    
                    en_name =''
                    
                    category = ''
                    
                    color = ''
                    
                    en_description_list = []
                    ar_description_list = []
                    
                    size_list = []
                
                    if 'msg' in en_data and en_data['msg'] == 'goods not exist':
                        
                        en_name =ar_data['info']['goods']['detail']['goods_url_name']         
                    
                        ar_name = ar_data['info']['goods']['detail']['goods_name']
                        
                        category = ar_data['info']['goods']['currentCat']['cat_url_name']
                        
                        color = ar_data['info']['goods']['detail']['mainSaleAttribute'][0]['attr_value_en']
                        
                        
                        for i in ar_data['info']['goods']['detail']['productDetails']:
                            key = i['attr_name_en']
                            value = i['attr_value_en']
                            
                            desc_items = f'{key}: {value}\n'
                            
                            en_description_list.append(desc_items)
                            
                        for i in ar_data['info']['goods']['detail']['productDetails']:
                            key = i['attr_name']
                            value = i['attr_value']
                            
                            desc_items = f'{key}: {value}\n'
                            
                            ar_description_list.append(desc_items)
                        
                        size_data = ar_data['info']['goods']['attrSizeList']['sale_attr_list'][f'{slug}']['sku_list']
                        for counter, i in enumerate(size_data):
                            stock = i['stock']
                            try:
                                size_name = i['sku_sale_attr'][0]['attr_value_name_en']
                            except:
                                size_name = "one-size"
                            
                            size_list.append(
                                {
                                    "size":size_name,
                                    "stock":stock
                                }
                            )
                    else:
                    
                    
                        en_name = en_data['info']['goods']['detail']['goods_name']           
                        ar_name = ar_data['info']['goods']['detail']['goods_name']
                        
                        category = en_data['info']['goods']['currentCat']['cat_name']
                        
                        color = en_data['info']['goods']['detail']['mainSaleAttribute'][0]['attr_value_en']
                        
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
                        
                            
                        size_data = en_data['info']['goods']['attrSizeList']['sale_attr_list'][f'{slug}']['sku_list']
                        for counter, i in enumerate(size_data):
                            stock = i['stock']
                            try:
                                size_name = i['sku_sale_attr'][0]['attr_value_name_en']
                            except:
                                size_name = "one-size"
                            
                            size_list.append(
                                {
                                    "size":size_name,
                                    "stock":stock
                                }
                            )
                        

                    
                    
                    items['product_name_arabic'] = ar_name
                    items['product_name_eng'] = en_name
                    items['category'] = category
                    items['sku'] = response.meta.get('sku')
                    items['price'] = response.meta.get('purchased_price')
                    items['qty'] = response.meta.get('qty')
                    items['color'] = color
                    items['desc_en'] = ''.join(en_description_list)
                    items['desc_ar'] = ''.join(ar_description_list)
                    main_image = ar_data['info']['goods']['goods_imgs']['main_image']['origin_image']
                    items['image1']= 'https://' + main_image.replace('//','')
                    
                    
                    for counter , i in enumerate(ar_data['info']['goods']['goods_imgs']['detail_image'],start=2):
                        if counter <= 10:
                            image_url=i['origin_image']
                            image_url=image_url.strip().replace('//','')
                            #size = size['size']
                            items['link'] = response.meta.get('link')
                            items[f'image{counter}'] = 'https://' + image_url
                            items['product_code'] = f"{sku}-{size}-{color}"#checkig
                            items['size'] = size
                            #items['stock'] = size['stock']
                    #print(items)
                    self.log(f"items_--{items}")
                    yield items
                except:
                    yield items
                


            

            

 


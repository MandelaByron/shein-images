# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# - Product name Arabic

# - ⁠Product name English

# - ⁠SKU

# - ⁠description Arabic

# - ⁠description English

# - ⁠images

class SheinItem(scrapy.Item):
    # define the fields for your item here like:
    link = scrapy.Field()
    product_name_arabic = scrapy.Field()
    product_name_eng = scrapy.Field()
    category = scrapy.Field()
    size = scrapy.Field()
    sku = scrapy.Field()
    product_code = scrapy.Field()
    color = scrapy.Field()
    column1 = scrapy.Field()
    desc_ar = scrapy.Field()
    desc_en =  scrapy.Field()
    main_image= scrapy.Field()
    image1=scrapy.Field()
    image2=scrapy.Field()
    image3=scrapy.Field()
    image4=scrapy.Field()
    image5=scrapy.Field()
    image6=scrapy.Field()
    image7=scrapy.Field()
    image8=scrapy.Field()
    image9=scrapy.Field()
    image10=scrapy.Field()

    
    

#!/usr/bin/python

# -*- coding: utf8 -*-
import scrapy
import logging

from scrapy.loader import ItemLoader
from scrapy.http import FormRequest
from fbcrawl.items import FbcrawlItem

class FacebookSpider(scrapy.Spider):
    """
    Parse FB group (needs credentials)
    """    
    name = "fbgroup"
    custom_settings = {
        'FEED_EXPORT_FIELDS': ['membersgroup','photosgroup','source','shared_from','date','text' \
                               'reactions','likes','ahah','love','wow', \
                               'sigh','grrr','comments','url']
    }
    
    def __init__(self, *args, **kwargs):
        #turn off annoying logging, set LOG_LEVEL=DEBUG in settings.py to see more logs
        logger = logging.getLogger('scrapy.middleware')
        logger.setLevel(logging.WARNING)
        super().__init__(*args,**kwargs)
        
        #email & pass need to be passed as attributes!
        if 'email' not in kwargs or 'password' not in kwargs:
            raise AttributeError('You need to provide valid email and password:\n'
                                 'scrapy fb -a email="EMAIL" -a password="PASSWORD"')
        else:
            self.logger.info('Email and password provided, using these as credentials')

        #group name parsing (added support for full urls)
        if 'group' not in kwargs:
            raise AttributeError('You need to provide a valid group name to crawl!'
                                 'scrapy fb -a group ="GroupNAME"')
        elif self.group.find('https://www.facebook.com/') != -1:
       # elif self.page.find('https://www.facebook.com/') != -1:
            self.group = self.group[25:]
            self.logger.info('Group attribute provided, scraping "{}"'.format(self.group))
        elif self.group.find('https://mbasic.facebook.com/') != -1:
            self.group = self.group[28:]
            self.logger.info('Group attribute provided, scraping "{}"'.format(self.group))
        elif self.group.find('https://m.facebook.com/') != -1:
            self.group = self.group[23:]
            self.logger.info('Group attribute provided, scraping "{}"'.format(self.group))
        else:
            self.logger.info('group attribute provided, scraping "{}"'.format(self.group))
        
        #parse year
        if 'year' not in kwargs:
            self.year = 2018
            self.logger.info('Year attribute not found, set scraping back to {}'.format(self.year))
        else:
            assert int(self.year) <= 2020 and int(self.year) >= 2006,\
            'Year must be an int number 2006 <= year <= 2020'
            self.year = int(self.year)    #arguments are passed as strings
            self.logger.info('Year attribute found, set scraping back to {}'.format(self.year))

        #parse lang, if not provided (but is supported) it will be guessed in parse_home
        if 'lang' not in kwargs:
            self.logger.info('Language attribute not provided, I will try to guess it from the fb interface')
            self.logger.info('To specify, add the lang parameter: scrapy fb -a lang="LANGUAGE"')
            self.logger.info('Currently choices for "LANGUAGE" are: "en", "es", "fr", "it", "pt"')
            self.lang = '_'                       
        elif self.lang == 'en'  or self.lang == 'es' or self.lang == 'fr' or self.lang == 'it' or self.lang == 'pt':
            self.logger.info('Language attribute recognized, using "{}" for the facebook interface'.format(self.lang))
        else:
            self.logger.info('Lang "{}" not currently supported'.format(self.lang))                             
            self.logger.info('Currently supported languages are: "en", "es", "fr", "it", "pt"')                             
            self.logger.info('Change your interface lang from facebook and try again')
            raise AttributeError('Language provided not currently supported')

        #current year, this variable is needed for parse_page recursion
        self.k = 2019
        #count number of posts, used to prioritized parsing and correctly insert in the csv
        self.count = 0
        
        self.start_urls = ['https://mbasic.facebook.com/']    

    def parse(self, response):
        '''
        Handle login with provided credentials
        '''
        return FormRequest.from_response(
                response,
                formxpath='//form[contains(@action, "login")]',
                formdata={'email': self.email,'pass': self.password},
                callback=self.parse_home
        )
  
    def parse_home(self, response):
        '''
        This method has multiple purposes:
        1) Handle failed logins due to facebook 'save-device' redirection
        2) Set language interface, if not already provided
        3) Navigate to given page 
        '''
        #handle 'save-device' redirection
        if response.xpath("//div/a[contains(@href,'save-device')]"):
            self.logger.info('Got stuck in "save-device" checkpoint')
            self.logger.info('I will now try to redirect to the correct page')
            return FormRequest.from_response(
                response,
                formdata={'name_action_selected': 'dont_save'},
                callback=self.parse_home
                )
            
        #set language interface
        if self.lang == '_':
            if response.xpath("//input[@placeholder='Search Facebook']"):
                self.logger.info('Language recognized: lang="en"')
                self.lang = 'en'
            elif response.xpath("//input[@placeholder='Buscar en Facebook']"):
                self.logger.info('Language recognized: lang="es"')
                self.lang = 'es'
            elif response.xpath("//input[@placeholder='Rechercher sur Facebook']"):
                self.logger.info('Language recognized: lang="fr"')
                self.lang = 'fr'
            elif response.xpath("//input[@placeholder='Cerca su Facebook']"):
                self.logger.info('Language recognized: lang="it"')
                self.lang = 'it'
            elif response.xpath("//input[@placeholder='Pesquisa no Facebook']"):
                self.logger.info('Language recognized: lang="pt"')
                self.lang = 'pt'
            else:
                raise AttributeError('Language not recognized\n'
                                     'Change your interface lang from facebook ' 
                                     'and try again')
                                                                 
        #navigate to provided group
        href = response.urljoin(self.group)
        self.logger.info('Scraping facebook group {}'.format(href))
        return scrapy.Request(url=href,callback=self.parse_group,meta={'index':1})

    def parse_group(self, response):
        '''
        Parse the given page selecting the posts.
        Then ask recursively for another page.
        '''
        #select all posts
        for post in response.xpath("//div[contains(@data-ft,'top_level_post_id')]"):            
            new = ItemLoader(item=FbcrawlItem(),selector=post)
            self.logger.info('Parsing post n = {}'.format(abs(self.count)))
            new.add_xpath('comments', "./div[2]/div[2]/a[1]/text()")        
            new.add_xpath('url', ".//a[contains(@href,'footer')]/@href")
            new.add_xpath('membersgroup', "//td/span[contains(@id,'u_0_2')]/text()")
            new.add_xpath('photosgroup', "//td/span[contains(@id,'u_0_4')]/text()")

            #page_url #new.add_value('url',response.url)
            #returns full post-link in a list
            post = post.xpath(".//a[contains(@href,'footer')]/@href").extract() 
            temp_post = response.urljoin(post[0])
            self.count -= 1
            yield scrapy.Request(temp_post, self.parse_post, priority = self.count, meta={'item':new})       

        #load following page
        #tries to click on "more", otherwise it looks for the appropriate
        #year for 1-click only and proceeds to click on others
        new_group = response.xpath("//div[2]/a[contains(@href,'permalinks&refid')]/@href").extract()
        new_group = response.urljoin(new_group[0])
        yield scrapy.Request(new_group, callback=self.parse_group) 
                
    def parse_post(self,response):
        new = ItemLoader(item=FbcrawlItem(),response=response,parent=response.meta['item'])
        new.add_xpath('source', "//td/div/h3/strong/a/text() | //span/strong/a/text() | //div/div/div/a[contains(@href,'post_id')]/strong/text()")
        new.add_xpath('shared_from','//div[contains(@data-ft,"top_level_post_id") and contains(@data-ft,\'"isShare":1\')]/div/div[3]//strong/a/text()')
        new.add_xpath('date','//div/div/abbr/text()')
        new.add_xpath('text','//div[@data-ft]//p//text() | //div[@data-ft]/div[@class]/div[@class]/text()')
        new.add_xpath('reactions',"//a[contains(@href,'reaction/profile')]/div/div/text()")  
        
        reactions = response.xpath("//div[contains(@id,'sentence')]/a[contains(@href,'reaction/profile')]/@href")
        reactions = response.urljoin(reactions[0].extract())
        yield scrapy.Request(reactions, callback=self.parse_reactions, meta={'item':new})
        
    def parse_reactions(self,response):
        new = ItemLoader(item=FbcrawlItem(),response=response, parent=response.meta['item'])
        new.context['lang'] = self.lang           
        new.add_xpath('likes',"//a[contains(@href,'reaction_type=1')]/span/text()")
        new.add_xpath('ahah',"//a[contains(@href,'reaction_type=4')]/span/text()")
        new.add_xpath('love',"//a[contains(@href,'reaction_type=2')]/span/text()")
        new.add_xpath('wow',"//a[contains(@href,'reaction_type=3')]/span/text()")
        new.add_xpath('sigh',"//a[contains(@href,'reaction_type=7')]/span/text()")
        new.add_xpath('grrr',"//a[contains(@href,'reaction_type=8')]/span/text()")        
        yield new.load_item()       
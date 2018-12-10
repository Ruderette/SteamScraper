# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
from steam.items import *
class SteamPipeline(object):
    def open_spider(self, spider):
        hostname = 'localhost'
        username = 'postgres'
        password = 'Monday.2' # your password
        database = 'games'
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
    
    def process_item(self, item, spider):
    
        self.cur.execute("INSERT INTO game_details(app_id,title, publisher, developer, release_date, date_trial, nb_reviews_positive, nb_reviews_negative, price, discount_price, sentiment, metascore, game_url, description, early_access, image_url, genre) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT ON CONSTRAINT title_one DO UPDATE SET publisher = excluded.publisher,developer = excluded.developer, release_date = excluded.release_date, date_trial = excluded.date_trial, nb_reviews_positive=excluded.nb_reviews_positive, nb_reviews_negative = excluded.nb_reviews_negative, price=excluded.price, discount_price=excluded.discount_price, sentiment=excluded.sentiment, metascore=excluded.metascore, game_url=excluded.game_url, description=excluded.description, early_access=excluded.early_access, image_url=excluded.image_url, genre=excluded.genre", (item['id'],item['app_name'],item['publisher'],item['developer'], item['release_date'], item['release_date_string'], item['positive'], item['negative'], item['price'], item['discount_price'], item['sentiment'], item['metascore'], item['url'] , item['description'], item['early_access'], item['image_url'], item['genre_test']))
    
        x = item['app_name']
        logger.debug(x)
        y=item['early_access']
        print(type(y))
       
       # Inserts the genre in the db + asssociates game with genre
        for genre in item['genre']:
           self.cur.execute("INSERT INTO genres (name_genre) VALUES(%s) ON CONFLICT ON CONSTRAINT name_genre_unique DO NOTHING",  (genre,))
           self.cur.execute("SELECT gd.id_game FROM game_details gd WHERE gd.title LIKE %s", ("%" + x + "%",))
           select_game_id = self.cur.fetchone()
           self.cur.execute("SELECT g.id_genre FROM genres g WHERE g.name_genre LIKE %s", ("%" + genre + "%",))
           select_genre_id = self.cur.fetchone()
           self.cur.execute("INSERT INTO game_genre (id_game, id_genre) VALUES(%s,%s) ON CONFLICT ON CONSTRAINT game_genre_unique DO NOTHING", (select_game_id, select_genre_id))
     
        # Inserts the tags in the db + associates game with tags
        for tag in item['tags']:
            self.cur.execute("INSERT INTO tags (name_tag) VALUES(%s) ON CONFLICT ON CONSTRAINT name_tag_unique DO NOTHING",  (tag,))
            self.cur.execute("SELECT gd.id_game FROM game_details gd WHERE gd.title LIKE %s", ("%" + x + "%",))
            select_game_id = self.cur.fetchone()
            self.cur.execute("SELECT t.id_tag FROM tags t WHERE t.name_tag LIKE %s", ("%" + tag + "%",))
            select_tag_id = self.cur.fetchone()
            self.cur.execute("INSERT INTO game_tag (id_game, id_tag) VALUES(%s,%s) ON CONFLICT ON CONSTRAINT game_tag_unique DO NOTHING", (select_game_id, select_tag_id))
        
        # Insert the specs in the db + associates game with specs
        for spec in item['specs']:
            self.cur.execute("INSERT INTO specs (name_spec) VALUES(%s) ON CONFLICT ON CONSTRAINT name_spec_unique DO NOTHING",  (spec,))
            self.cur.execute("SELECT gd.id_game FROM game_details gd WHERE gd.title LIKE %s", ("%" + x + "%",))
            select_game_id = self.cur.fetchone()
            self.cur.execute("SELECT s.id_spec FROM specs s WHERE s.name_spec LIKE %s", ("%" + spec + "%",))
            select_spec_id = self.cur.fetchone()
            self.cur.execute("INSERT INTO game_specs (id_game, id_spec) VALUES(%s,%s) ON CONFLICT ON CONSTRAINT game_spec_unique DO NOTHING", (select_game_id, select_spec_id))
        
        for publisher in item['publisher']:
            self.cur.execute("INSERT INTO publishers (name_publisher) VALUES(%s) ON CONFLICT ON CONSTRAINT name_publisher_unique DO NOTHING",  (publisher,))
            self.cur.execute("SELECT gd.id_game FROM game_details gd WHERE gd.title LIKE %s", ("%" + x + "%",))
            select_game_id = self.cur.fetchone()
            self.cur.execute("SELECT p.id_publisher FROM publishers p WHERE p.name_publisher LIKE %s", ("%" + publisher + "%",))
            select_publisher_id = self.cur.fetchone()
            self.cur.execute("INSERT INTO game_publisher (id_game, id_publisher) VALUES(%s,%s) ON CONFLICT ON CONSTRAINT game_publisher_unique DO NOTHING", (select_game_id, select_publisher_id))
        
        for dev in item['developer']:
            self.cur.execute("INSERT INTO developers (name_dev) VALUES(%s) ON CONFLICT ON CONSTRAINT name_dev_unique DO NOTHING",  (dev,))
            self.cur.execute("SELECT gd.id_game FROM game_details gd WHERE gd.title LIKE %s", ("%" + x + "%",))
            select_game_id = self.cur.fetchone()
            self.cur.execute("SELECT d.id_dev FROM developers d WHERE d.name_dev LIKE %s", ("%" + dev + "%",))
            select_dev_id = self.cur.fetchone()
            self.cur.execute("INSERT INTO game_dev (id_game, id_dev) VALUES(%s,%s) ON CONFLICT ON CONSTRAINT game_dev_unique DO NOTHING", (select_game_id, select_dev_id))
       
        self.connection.commit()
        #self.cur.fetchall()
        return item


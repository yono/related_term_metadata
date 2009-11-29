#!/usr/bin/env python
# vim:set fileencoding=utf-8:
'''
co_word.py
simpson 係数である単語とそれと共起した単語の類似度を計算する
'''
import sys
from math import log,sqrt
import MySQLdb
import config

def get_related_words(word):
    word1 = word

    dbname = 'cooccur'
    user = config.get_option(dbname,'user')
    passwd = config.get_option(dbname,'passwd')

    con = MySQLdb.connect(db=dbname,host='localhost',user=user,\
            passwd=passwd,use_unicode=True,charset='utf8')
    cur = con.cursor()

    cur.execute('select id,df from word where name = "%s"' % (word1))
    row = cur.fetchone()
    w1id = int(row[0])
    w1f = int(row[1])

    cur.execute('''
    select c.word2_id,w.df,c.simpson,c.cosine,w.name
    from word w,co c
    where c.word1_id = %d and w.id = c.word2_id and c.simpson > 0
    order by c.simpson desc limit 1000
    ''' % (w1id))
    ids = cur.fetchall()
    simpsons = []
    cosines = []
    words = {}
    for i in xrange(len(ids)):
        w2id = int(ids[i][0])
        w2f = int(ids[i][1])
        simpson = float(ids[i][2])
        cosine  = float(ids[i][3])
        word2   = ids[i][4]
        words[word2] = w2f

        simpsons.append((word2,simpson))
        cosines.append((word2,cosine))

    simpsons.sort(lambda x,y:cmp(x[1],y[1]),reverse=True)
    cosines.sort(lambda x,y:cmp(x[1],y[1]),reverse=True)

    newresult = {}
    news = {}
    for i in xrange(len(simpsons)):
        newresult[simpsons[i][0]] = {'s1':0,'s2':0,'c1':0,'c2':0}
        news[simpsons[i][0]] = news.get(simpsons[i][0], 0) + simpsons[i][1]/float(simpsons[0][1])
        newresult[simpsons[i][0]]['s1'] = i
        newresult[simpsons[i][0]]['s2'] = simpsons[i][1]/float(simpsons[0][1])
    for i in xrange(len(cosines)):
        newresult[cosines[i][0]]['c1'] = i
        newresult[cosines[i][0]]['c2'] = cosines[i][1]

    newslist = [(k,v) for k,v in news.items() if v > 0.3]
    newslist.sort(lambda x,y:cmp(x[1],y[1]),reverse=True)
    
    return newslist, newresult

def count_same(rdic1,rdic2):
    set1 = set(rdic1.keys())
    set2 = set(rdic2.keys())
    set1.intersection_update(set2)
    return len(set1)

if __name__ == '__main__':
    print get_related_word(word1)

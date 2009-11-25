#!/usr/bin/env python
# vim:set fileencoding=utf-8:
'''
co_word.py
simpson 係数である単語とそれと共起した単語の類似度を計算する
'''
import sys
from math import log,sqrt
import MySQLdb
import htmlutil

def get_related_word(word1, word2):
    con = MySQLdb.connect(db='graduate',host='localhost',user='root',\
            passwd='taberu-syati',use_unicode=True,charset='utf8')
    cur = con.cursor()
    
    cur.execute('select id,df from word where name = "%s"' %\
            (MySQLdb.escape_string(word1)))
    row = cur.fetchone()
    w1id = int(row[0])
    w1f = int(row[1])

    cur.execute('select id,df from word where name = "%s"' %\
            (MySQLdb.escape_string(word2)))
    row = cur.fetchone()
    w2id = int(row[0])
    w2f = int(row[1])

    cur.execute('''
        select c.mi_score from co c, word w1, word w2
        where c.word1_id = %d and w1.id = c.word1_id and c.word2_id = %d and w2.id = c.word2_id and 
        w2.df < 10000 and w2.df > 9 and w1.df < 10000 and w2.df > 9
    ''' % (w1id,w2id))
    res = cur.fetchone()
    if res is None:
        return {'d':0.0,'j':0.0,'s':0.0,'c':0.0}
    else:
        mi = float(res[0])

    co = {}
    cur.execute('''
        select webpage_id from appear where word_id = %d
        ''' % (w1id))
    rows = cur.fetchall()
    for j in xrange(len(rows)):
        wid = int(rows[j][0])
        co[wid] = co.get(wid, 0) + 1

    cur.execute('''
        select webpage_id from appear where word_id = %d
        ''' % (w2id))
    rows = cur.fetchall()
    for j in xrange(len(rows)):
        wid = int(rows[j][0])
        co[wid] = co.get(wid, 0) + 1

    w12freq = 0
    for j in co:
        if co[j] == 2:
            w12freq += 1

    w12 = float(w12freq)/float(w1f)
    w21 = float(w12freq)/float(w2f)
    if w12 == 0 or w21 == 0:
        return {'d':0.0,'j':0.0,'s':0.0,'c':0.0}

    dice = 2*w12freq/float(w1f+w2f)
    #dice = (w12freq)/float(w12+w21)
    #jaccard = w12freq/float(len(co))
    jaccard = w12freq/float(w1f+w2f+len(co))
    simpson = (w12freq)/float(min(w1f,w2f))
    cosine  = w12freq/sqrt(w1f*w2f)

    #print 'simpson:',simpson,' dice:',dice,' cosine:',cosine,' jaccard:',jaccard
    #result = (simpson + cosine + dice + mi)/4.0
    #result = (simpson + dice) / 2.0
    result = {'d':dice,'j':jaccard,'s':simpson,'c':cosine}

    return result

def get_related_words(word):
    word1 = word

    con = MySQLdb.connect(db='graduate',host='localhost',user='root',\
            passwd='taberu-syati',use_unicode=True,charset='utf8')
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
        #newresult[cosines[i][0]]['c2'] = cosines[i][1]/float(cosines[0][1])


    newslist = [(k,v) for k,v in news.items() if v > 0.3]
    newslist.sort(lambda x,y:cmp(x[1],y[1]),reverse=True)
    
    return newslist, newresult

def count_same(rdic1,rdic2):
    set1 = set(rdic1.keys())
    set2 = set(rdic2.keys())
    set1.intersection_update(set2)
    return len(set1)

if __name__ == '__main__':
    word1 = sys.argv[1].decode()
    word2 = sys.argv[2].decode()
    print get_related_word(word1,word2)

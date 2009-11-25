#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
metadata.py

テーブル中のファイルに対してメタデータを生成する
引数
i: テーブル中での id
cword1: 注目する関連語その1
cword2: 注目する関連語その2
"""
import sys
import MySQLdb
import htmlutil
import htmlutil_ext
from math import log
import co_word

class RelatedWord(object):
    def __init__(self,word,weight,src_words=[]):
        self.word = word
        self.weight = weight
        self.src_words = src_words

class MetaData(object):
    def __init__(self,DEBUG=False):
        # 初期化
        con = MySQLdb.connect(db='graduate',host='localhost',user='root',
                passwd='taberu-syati',use_unicode=True,charset='utf8')
        self.cur = con.cursor()

        self.hutil = htmlutil.HTMLUtil()
        self.hutil_ext = htmlutil_ext.HTMLUtil()
        self.simpson_threshold = 2.0
        self.cosine_threshold = 0.056
        self.DEBUG = DEBUG
        self.words = {}

    def make(self,id,cword1,cword2):
        cur = self.cur
        cwords = {} # 注目する関連語
        if cword1 == all and cword2 == all:
            cwords = {'mac':0,'java':0,'javascript':0,'firefox':0}
        else:
            cwords = {cword1:0, cword2:0}

        # HTMLを取得し、単語を抽出する
        cur.execute('select content from note_note where id = %d' % (id))
        html = cur.fetchone()[0].decode('utf-8')
        worddic = self.hutil.get_analysed_text(html)
        if len(worddic) == 0:
            worddic = self.hutil_ext.get_analysed_text(html)

        # HTML中の延べ単語数を取得
        allnum = 0
        for i in worddic:
            allnum += worddic[i]

        # HTML中の単語の idf を取得し、tf-idf順でソートする
        relatedwords = {}
        pagewords = []
        for i in worddic:
            cur.execute('select idf,df from word where name = "%s"' % (i))
            row = cur.fetchone()
            if row is not None:
                idf = float(row[0])
                df = int(row[1])
                if df < 10000 and df > 9:
                    pagewords.append(\
                        (i,idf*(log(worddic[i]+1,2)/log(max(2,allnum),2))))
        pagewords.sort(lambda x,y:cmp(x[1],y[1]),reverse=True)

        # 共起による関連語候補を取得
        for i in xrange(min(len(pagewords),20)):
            iword = pagewords[i][0]
            ivalue = pagewords[i][1]
            result,result2 = co_word.get_related_words(iword)
            if self.DEBUG:
                print '-----',iword,ivalue,'-----'
            for j in xrange(min(len(result),20)):
                word,value = result[j]
                cosine = result2[word]['c2']
                if word in cwords and cosine > 0.056:
                    if self.DEBUG:
                        print j,word,value,a
                if cosine > self.cosine_threshold:
                    if word not in relatedwords:
                        relatedwords[word] = \
                            RelatedWord(word,\
                            value*(ivalue/float(result[0][1])),[iword])
                    else:
                        relatedwords[word].weight = \
                                relatedwords[word].weight + \
                                value*(ivalue/float(result[0][1]))
                        relatedwords[word].src_words.append(iword)

        # Simpson 係数の閾値を越えたもののみを実際に関連語として使う
        newrelatedwords = {}
        for i in relatedwords:
            if relatedwords[i].weight > self.simpson_threshold and \
                    i not in worddic:
                newrelatedwords[i] = relatedwords[i]
        relatedwords = newrelatedwords

        # 関連度でソート
        wordslist = [v for v in relatedwords.values()]
        wordslist.sort(lambda x,y:cmp(x.weight,y.weight),reverse=True)

        # 出力
        if self.DEBUG:
            for i in xrange(len(wordslist)):
                print "%s\t%f" % (wordslist[i].word, wordslist[i].weight)
        
        return wordslist

    def search(self,word):
        cur = self.cur
        cur.execute("""
        select m.note_id,w2.name from metadata m,word w1,word w2
        where w1.name = '%s' and w1.id = m.word_id and w2.id = m.org_id
        order by weight desc
        """ % (MySQLdb.escape_string(word)))
        rows = cur.fetchall()
        return rows

    def regist(self, id):
        cur = self.cur
        wordslist = self.make(id)
        sql_list = []
        # 単語辞書を読み込む
        if len(self.words) == 0:
            cur.execute('select id,name from word')
            rows = cur.fetchall()
            for row in rows:
                wid = int(row[0])
                name = row[1].decode('utf-8')
                self.words[name] = wid

        # マルチプル Insert
        for data in wordslist:
            for src_word in data[i].src_words:
                sql_list.append("(%d,%d,%f,%d)" %\
                        (words[data.word],id,data.weight,words[src_word]))
        sql = """
        INSERT INTO metadata (word_id,note_id,weight,org_id) VALUES %s
        """ % (','.join(sql_list))
        cur.execute(sql)
        
if __name__ == '__main__':
    import sys
    id = int(sys.argv[1])
    m = MetaData(DEBUG=True)
    m.make(id,'all','all')

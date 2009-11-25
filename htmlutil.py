#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
概要：テキスト処理をおこなう

extract_two_byte()

htmlentity2unicode()

関数リスト
"""
import re
import htmlentitydefs
import unicodedata
import extractword

class HTMLUtil(object):

    def __init__(self):
        self.tags = ['blockquote','body','caption','center',
                'dd','div','dl','dt','form','h1','h2','h3','h4','h5','h6',
                'hr','li','oi','p','q','table','tbody','td','th','thead',
                'tfoot','title','tr','tt','ul']
        self.symbols = r'[\!\@\#\$\%\^\&\*\(\)\-\_\=\+\\\|\`\~\[\]\{\}\;\:\'\"\,\<\.\>/\?！＠＃＄％＾＆＊（）＿＝＋＼｜｀〜「」『』【】；：’”，＜．＞／？ 　©†‡¦»«®・]'
        self.extractword = extractword.extractword()

    def extract_two_byte(self,u_str):
        words = u_str.split(" ")
        one_byte = []
        two_byte = []
        for word in words:
            for i in xrange(len(word)):
                if ord(word[i]) > 127 and ord(word[i]) != 160:
                    two_byte.append(word)
                    break
            else:
                one_byte.append(word)

        dic = {"one":one_byte, "two":two_byte}
        return dic

    # 実体参照 & 文字参照を通常の文字に戻す
    def htmlentity2unicode(self,text):
        # 正規表現のコンパイル
        reference_regex = re.compile(u'&(#x?[0-9a-f]+|[a-z]+);', re.IGNORECASE)
        num16_regex = re.compile(u'#x\d+', re.IGNORECASE)
        num10_regex = re.compile(u'#\d+', re.IGNORECASE)
        
        resultlist = []
        i = 0
        while True:
            # 実体参照 or 文字参照を見つける
            match = reference_regex.search(text, i)
            if match is None:
                resultlist.append(text[i:])
                break
            
            resultlist.append(text[i:match.start()])
            i = match.end()
            name = match.group(1)
            
            try:
                # 実体参照
                if name in htmlentitydefs.name2codepoint.keys():
                    resultlist.append(unichr(htmlentitydefs.name2codepoint[name]))
                # 文字参照
                elif num16_regex.match(name):
                    # 16進数
                    resultlist.append(unichr(int(u'0'+name[1:], 16)))
                elif num10_regex.match(name):
                    # 10進数
                    resultlist.append(unichr(int(name[1:])))
            except:
                pass
            
        result = ''.join(resultlist)
        return result

    def remove_useless_text(self, html):

        result = html
        useless_tags = ["head","script","select","noscript", "style"]
        tags = "|".join(useless_tags)
        result = re.sub(r"(?is)<(%s)[^>]*>.*?</\1\s*>" % tags, "", result)
        result = re.sub(r'(?is)<!--.*?-->',"",result)
        result = unicodedata.normalize("NFKC",result)
        result = self.htmlentity2unicode(result)
        result = re.sub(r"(?is)\r|\n","\n",result)
        result = re.sub(r"(?is)[ \t　]+", " ",result)

        return result

    def get_analysed_text(self, html):
        
        t_result = re.search(r"(?is)<title[^>]*>\s*(.*?)\s*</title\s*>",html)
        titles = {}
        if t_result != None:
            titles = self.extractword.extract_noun(t_result.group(1))
            result = "%s\n%s" % (t_result.group(0), html) 
            #print t_result.group(1)
        else:
            result = html
        result = self.remove_useless_text(result)
        all_tag = re.compile(r'(?is)<.*?>')
        symbol = re.compile(self.symbols, re.I | re.S)
        result = all_tag.sub(" ", result)
        result = symbol.sub(" ",result)
        spaces = re.compile(r"(?is)[ \t　]+")
        result = spaces.sub(" ", result)
        worddic = self.extractword.extract_noun(result)

        #print titles
        for i in worddic:
            if i in titles:
                #print i
                worddic[i] *= 3

        return worddic

    def get_analysed_each_sentences(self, html):

        result = self.remove_useless_text(html)
        all_tag = re.compile(r'(?is)<.*?>')
        symbol = re.compile(self.symbols, re.I | re.S)
        tags = map(lambda x:"</*%s.*?>" % (x), self.tags)
        tagsplit = "|".join(tags)
        htmllist = re.split(tagsplit, result)
        all_tag = re.compile(r'(?is)<.*?>')
        symbol = re.compile(self.symbols, re.I | re.S)
        spaces = re.compile(r"^(?is)^[ \t　]*$")
        spacess = re.compile(r"(?is)^[ \t　]+|[ \t　]+$")
        punctuations = re.compile(u"(?is)。|．")
        newlist = []
        for i in xrange(len(htmllist)):
            htmllist[i] = all_tag.sub("",htmllist[i])
            htmllist[i] = symbol.sub(" ", htmllist[i])
            new = punctuations.split(htmllist[i])
            for j in new:
                if spaces.match(j) == None:
                    newlist.append(spacess.sub("",j))

        resultlist = []
        for i in xrange(len(newlist)): 
            worddic = self.extractword.extract_noun(newlist[i])
            resultlist.append(worddic)

        return resultlist

    def test_text(self, html):
        
        result = self.remove_useless_text(html)
        all_tag = re.compile(r'(?is)<.*?>')
        symbol = re.compile(self.symbols, re.I | re.S)
        result = all_tag.sub("", result)
        result = symbol.sub(" ",result)
        spaces = re.compile(r"^(?is)[ \t　]+")
        result = spaces.sub(" ", result)
        return result

if __name__ == "__main__":
    file = open("index.html").read().decode("utf-8")
    obj = HTMLUtil()
    #relist = obj.get_analysed_each_sentences(file)
    #for i in xrange(len(relist)):
    #    print "------------ %d --------------" % (i)
    #    for word in relist[i]:
    #        print word, relist[i][word]
    result = obj.get_analysed_text(file)
    for word in result:
        print word, result[word]


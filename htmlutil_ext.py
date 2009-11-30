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
import extractword_ext

class HTMLUtil(object):

    def __init__(self):
        import MeCab
        import extractcontent
        self.mecab = MeCab.Tagger()
        self.tags = ['blockquote','body','caption','center',
                'dd','div','dl','dt','form','h1','h2','h3','h4','h5','h6',
                'hr','li','oi','p','q','table','tbody','td','th','thead',
                'tfoot','title','tr','tt','ul','br']
        self.symbols = u'[\!\@\#\$\%\^\&\*\(\)\-\_\=\+\\\|\`\~\[\]\{\}\;\:\'\"\,\<\.\>/\?！＠＃＄％＾＆＊（）＿＝＋＼｜｀〜「」『』【】；：’”，＜．＞／？ 　©†‡¦»«®・]'
        self.extractword = extractword_ext.extractword()
        self.ext = extractcontent.ExtractContent()
        self.ss = [u'動詞',u'形容詞',u'形容動詞',u'名詞',u'連体詞',u'副詞',u'接続詞',u'感動詞']
        self.nss = [u'助動詞',u'助詞']

    def is_sentence(self, text):
        mecab = self.mecab
        res = mecab.parseToNode(text.encode('utf-8'))
        num_ss = 0
        num_nss = 0
        num_joshi = 0
        num_jodou = 0
        num_all = 0
        while res:
            surface = res.surface.decode()
            feature = res.feature.decode()
            features = feature.split(',')
            if features[0] in self.ss and features[1] != u'非自立':
                num_ss += 1
            elif features[0] in self.nss:
                num_nss += 1
                if features[0] == u'助詞':
                    num_joshi += 1
                else:
                    num_jodou += 1
            num_all += 1
            res = res.next
        
        if num_all == 0 or num_ss == 0:
            return False
        five_flags = [False] * 5
        if num_ss >= 7:
            five_flags[0] = True
        if float(num_ss)/float(num_all) <= 0.64:
            five_flags[1] = True
        if float(num_nss)/float(num_all) >= 0.22:
            five_flags[2] = True
        if float(num_joshi)/float(num_ss) >= 0.26:
            five_flags[3] = True
        if float(num_jodou)/float(num_ss) >= 0.06:
            five_flags[4] = True

        num = 0
        for i in five_flags:
            if i:
                num += 1
        
        if num >= 3:
            return True
        else:
            return False

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

    def split_sentence(self, html):
        all_tag = re.compile(r'(?is)<.*?>')
        punctuations = re.compile(u"(?is)。|．|？|！|\n\n")
        spaces = re.compile(r"^(?is)^[ \t　]*$")
        spacess = re.compile(r"(?is)^[ \t　]+|[ \t　]+$")
        tags = map(lambda x:r"</*%s.*?>" % (x), self.tags)
        tagsplit = "|".join(tags)
        htmllist = re.split(tagsplit, html)
        result = []
        for i in xrange(len(htmllist)):
            sen = all_tag.sub(" ", htmllist[i])
            senlist = punctuations.split(sen)
            for j in senlist:
                if spaces.match(j) == None:
                    text = spacess.sub("",j)
                    if self.is_sentence(text):
                        result.append(text)
        return result

    def get_analysed_text(self, html):
        
        ext = self.ext
        ext.analyse(html)
        result = ext.as_html()
        #content = "%s\n\n%s" % (ext.title, result[0])
        if result is not None:
            content = self.htmlentity2unicode(result[0])
            result = self.split_sentence(content)
            content = '\n'.join(result)
            content = "%s\n%s" % (ext.title, content)
            content = self.htmlentity2unicode(content)
            worddic = self.extractword.extract_noun(content)
        else:
            worddic = {}

        return worddic

    def get_analysed_each_sentences(self, html):

        ext = self.ext
        ext.analyse(html)
        result = ext.as_html()
        content = "%s\n\n%s" % (ext.title, result[0])
        content = self.htmlentity2unicode(content)
        result = self.split_sentence(content)

        resultlist = []
        for i in xrange(len(result)): 
            worddic = self.extractword.extract_noun(result[i])
            resultlist.append(worddic)

        return resultlist

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


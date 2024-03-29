#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import config
import MeCab

class extractword(object):
    
    def __init__(self):
    	section = 'mecab'
    	userdic = config.get_option(section,'userdic')
    	rcfile = config.get_option(section,'rcfile')
        #self.mecab = MeCab.Tagger('--userdic=%s --rcfile=%s' % (userdic,rcfile))
        self.mecab = MeCab.Tagger()

    def is_symbol_only(self,word):
        u = unicode
        regexp = \
        re.compile(r'^[!"#\$\%\&\'\(\)\*\+,\-\./:;\<\=\>\?\@\[\\\]\^\_\`\{\}\~\|！＠＃＄％＾＆＊（）＿＝＋＼｜｀〜「」『』【】；：’”，＜．＞／？ 　©†‡¦»«®・]+$')
        if regexp.search(u(word)) != None:
            return True
        else:
            return False

    def is_alphabet(self, word):
        regexp = re.compile(r'[a-z]')
        regexp2 = re.compile(u'[ぁ-ん]')
        regexp3 = re.compile(u'[ァ-ン]')
        if (regexp.match(word) != None or regexp2.match(word) != None \
                or regexp3.match(word) != None) and len(word) == 1:
            return True
        else:
            return False

    def is_digit(self, feature):
        allowed_feature = [
            u"名詞,数",
        ]
        for rule in allowed_feature:
            if feature.startswith(rule):
                return True
        else:
            return False

    def extract_noun(self, text):
        u = unicode
        worddic = {}
        result = []
        c = self.mecab
        res = c.parseToNode(text.encode("utf-8"))
        ignore = set([u'数',u'代名詞',u'非自立',u'記号',u'接頭',u'接尾'])
        while res:
            surface = u(res.surface).lower()
            feature = u(res.feature)
            features = feature.split(',')
            if features[0] == u'名詞' \
            and features[1] not in ignore and not surface.isdigit()\
            and not self.is_symbol_only(surface)\
            and not self.is_alphabet(surface):
                worddic[surface] = worddic.get(surface, 0) + 1
            res = res.next
        return worddic

if __name__ == "__main__":
    extract_noun(None)

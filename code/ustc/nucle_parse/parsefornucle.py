# -*- coding:UTF-8 -*-  
import xml.etree.ElementTree as ET  
import xml.dom.minidom as minidom
  
  
# 格式化输出xml文件  
def display(root):  
    rough_string = ET.tostring(root, 'utf-8')  
    reparsed = minidom.parseString(rough_string)  
    print reparsed.toprettyxml(indent="  " , encoding="utf-8");

def pre_deal(filename,outfile):
    fin = open(filename,'r')
    fout = open(outfile,'w')
    while True:
        line  = fin.readline()
        if not line:break
        if line.startswith(r'<REFERENCE>'):
            while not line.startswith(r'</REFERENCE>'):
                line = fin.readline()
        else:
            fout.write(line)
    fin.close()
    fout.close()
                

def parse(filename):
    try:
#         fin = open(filename,"r").read()
        tree = ET.parse(filename)
#         display(root)
        root = tree.getroot() #获得root节点
    except Exception, e:
        print e
        return -1   
    docs_src = root.findall("DOC") #找到DOCS节点下的所有DOC节点
    root_dst = ET.Element("docs")
    for doc_src in docs_src:
        doc_dst = ET.SubElement(root_dst,"doc")
        if doc_src.attrib.has_key("nid"):
            doc_dst.set("id", doc_src.attrib["nid"])
        paras_src = doc_src.find("TEXT").findall("P")
#         paras_src = [para for para in paras_src if para.tag != "REFERENCE" ]
        mistakes_src = doc_src.find("ANNOTATION").findall("MISTAKE")
        for para_src in paras_src:
            para_index = str(paras_src.index(para_src))
            para_dst = ET.SubElement(doc_dst,"para")
            para_dst.set("number",para_index)
#             para_dst.set("content",para_src.text[1:-1])
            para_content = ET.SubElement(para_dst,"content")
            para_content.text = para_src.text
            mistakes_in_para = [mistake for mistake in mistakes_src 
                                if mistake.attrib['start_par'] == para_index]
            mistakes_dst = ET.SubElement(para_dst,"mistakes")
            for mistake_in_para in mistakes_in_para:
                mistake_dst = ET.SubElement(mistakes_dst,"mistake")
                mistake_dst.set("number",str(mistakes_in_para.index(mistake_in_para)))
                mistake_dst.set("start_off",mistake_in_para.attrib["start_off"])
                
                '''mistake在段落的结尾处时，end_par = 下一段的段号，end_off = 0,需要区别处理'''
                if mistake_in_para.attrib["end_par"] == mistake_in_para.attrib["start_par"]:
                    mistake_dst.set("end_off",mistake_in_para.attrib["end_off"])
                else:
                    mistake_dst.set("end_off",str(len(para_src.text)-1))
                    
                    '''type与built-in的type会冲突'''
                type0 = ET.SubElement(mistake_dst,"type")
                type_src = mistake_in_para.find('TYPE')
                if type_src is not None:
                    type0.text = type_src.text
                    
                correction = ET.SubElement(mistake_dst,"correction")
                correction_src = mistake_in_para.find("CORRECTION")
                if correction_src is not None:
                    correction.text = correction_src.text
                    
                comment = ET.SubElement(mistake_dst,"comment")
                comment_src = mistake_in_para.find("COMMENT")
                if comment_src is not None:
                    comment.text = comment_src.text
        tree._setroot(root_dst)
        return tree
#     ET.dump(root_dst)
#     return root_dst

                
if __name__ == '__main__':
    pre_deal("test0.sgml","test1.sgml")
    tree = parse("test1.sgml")
    tree.write("./out.xml")
    print "Finished"
    
    
    
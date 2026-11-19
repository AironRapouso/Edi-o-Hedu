"""Dump a .docx as plain text (paragraphs with their style, tables as rows).
Usage: python -X utf8 read_docx.py <file.docx> > roteiro_shorts.txt
"""
import sys
import zipfile

import defusedxml.ElementTree as ET          # hardened parser: a .docx is a ZIP of XML and may come from anywhere

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def text_of(node):
    out = []
    for el in node.iter():
        if el.tag == W + "t":
            out.append(el.text or "")
        elif el.tag in (W + "tab",):
            out.append("\t")
        elif el.tag in (W + "br", W + "cr"):
            out.append("\n")
    return "".join(out)


def para(p):
    st = p.find(f"{W}pPr/{W}pStyle")
    style = st.get(W + "val") if st is not None else ""
    num = p.find(f"{W}pPr/{W}numPr") is not None
    bold = all(r.find(f"{W}rPr/{W}b") is not None for r in p.findall(W + "r") if text_of(r).strip()) and bool(p.findall(W + "r"))
    return style, num, bold, text_of(p)


with zipfile.ZipFile(sys.argv[1]) as z:
    root = ET.fromstring(z.read("word/document.xml"))
body = root.find(W + "body")
for el in body:
    if el.tag == W + "p":
        style, num, bold, t = para(el)
        if not t.strip():
            print()
            continue
        tag = f"[{style}] " if style and style.lower() not in ("normal",) else ""
        print(f"{tag}{'- ' if num else ''}{'**' if bold and not style else ''}{t}{'**' if bold and not style else ''}")
    elif el.tag == W + "tbl":
        print("<table>")
        for tr in el.iter(W + "tr"):
            cells = [" / ".join(x for x in (text_of(p).strip() for p in tc.iter(W + "p")) if x) for tc in tr.findall(W + "tc")]
            print("  | " + " | ".join(cells) + " |")
        print("</table>")

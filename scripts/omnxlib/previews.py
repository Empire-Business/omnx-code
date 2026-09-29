"""Bounded, static previews. No arbitrary path-serving, JavaScript or remote fetch.

HTML is converted to a conservative display-only document. Resource references
are reissued as capabilities bound to a manifest. No iframe receives API tokens.
"""
from __future__ import annotations
import html
import posixpath
import re
import struct
from html.parser import HTMLParser
from pathlib import PurePosixPath
from urllib.parse import urlsplit, unquote
from .core import *
from .privacy import safe_subject_path, redact

ENTRY_EXTS = {'.html', '.htm', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg'}
ASSET_EXTS = ENTRY_EXTS | {'.css', '.woff', '.woff2', '.ttf', '.otf'}
MAX_ASSET = 8 * 1024 * 1024
MAX_BUNDLE = 24 * 1024 * 1024
MAX_FILES = 150
MIME = {'.html':'text/html; charset=utf-8', '.htm':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.svg':'image/svg+xml', '.png':'image/png', '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.webp':'image/webp', '.gif':'image/gif', '.woff':'font/woff', '.woff2':'font/woff2', '.ttf':'font/ttf', '.otf':'font/otf'}

def inspect_png(fs,rel):
    """Read PNG header facts only; viewport, crop, and export scale need evidence."""
    portable_path(rel);require(PurePosixPath(rel).suffix.lower()=='.png','png_required','A referência oficial nova deve ser PNG.',4)
    raw=fs.read(rel,MAX_ASSET);require(raw is not None,'missing_subject','PNG não encontrado.',4)
    require(len(raw)>=33 and raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>I',raw[8:12])[0]==13 and raw[12:16]==b'IHDR','invalid_png','Cabeçalho PNG inválido.')
    width,height=struct.unpack('>II',raw[16:24])
    require(1<=width<=50000 and 1<=height<=50000 and width*height<=1_000_000_000,'png_dimensions','Dimensões PNG fora do limite seguro.')
    return result('Dimensões PNG lidas; pixels não equivalem automaticamente a CSS pixels.',reference=rel,width=width,height=height,aspect_ratio=round(width/height,6),bytes=len(raw),possible_crop='unknown',capture_type='unknown',export_scale='unknown',css_viewport='not_inferred',visual_content_inspected=False,guidance=['Confirme se é viewport, página inteira ou recorte antes de comparar.','Preserve tokens e hierarquia; adapte a composição a cada largura suportada.','PRD, decisões e rotas documentadas prevalecem sobre rótulos ou rotas desenhados.'])

def walk_files(fs, directory, *, maximum=20000, depth_limit=16):
    """Never follow links; maximum bounds files visited, not just matches returned."""
    root = fs.path(directory)
    if not root.exists(): return
    require(root.is_dir(), 'preview_directory', 'Diretório de propostas inválido.', 3)
    stack = [(root, 0)]; visited = 0
    while stack:
        parent, depth = stack.pop()
        require(depth <= depth_limit, 'scan_limit', 'Árvore de arquivos excede profundidade permitida.', 6)
        with os.scandir(parent) as scan:
            for entry in scan:
                visited += 1
                require(visited <= maximum, 'scan_limit', 'Inventário parcial: limite de arquivos atingido.', 6)
                if entry.is_symlink(): continue
                if entry.is_dir(follow_symlinks=False):
                    if not entry.name.startswith('.') and entry.name not in {'node_modules','vendor','archive'}:
                        stack.append((Path(entry.path), depth+1))
                elif entry.is_file(follow_symlinks=False):
                    yield Path(entry.path).relative_to(fs.root).as_posix()

def preview_base(fs, project):
    rel = project.get('paths', {}).get('ux_proposals', 'docs/ux/proposals')
    safe_subject_path(rel); fs.path(rel)
    return rel.rstrip('/')

def check_preview_path(fs, project, rel):
    safe_subject_path(rel)
    base = preview_base(fs, project)
    require(rel.startswith(base+'/'), 'preview_not_registered', 'Arquivo não pertence à galeria de telas.', 5)
    require(PurePosixPath(rel).suffix.lower() in ENTRY_EXTS, 'preview_type', 'Formato de preview não permitido.', 5)
    fs.path(rel)
    return rel

def bundle_manifest(fs, rel, *, project=None):
    """An HTML approval includes local display assets in its proposal directory."""
    safe_subject_path(rel)
    if project is not None: check_preview_path(fs, project, rel)
    primary = fs.read(rel, MAX_ASSET)
    require(primary is not None, 'missing_subject', 'Conteúdo da proposta não foi encontrado.', 4)
    paths = [rel]
    if PurePosixPath(rel).suffix.lower() in {'.html','.htm'}:
        parent = str(PurePosixPath(rel).parent)
        require(parent != '.', 'subject_bundle_scope', 'Coloque HTML em uma pasta de proposta delimitada.', 5)
        for candidate in walk_files(fs, parent, maximum=3000):
            if candidate != rel and PurePosixPath(candidate).suffix.lower() in ASSET_EXTS:
                paths.append(candidate)
                require(len(paths) <= MAX_FILES, 'preview_limit', 'Proposta possui arquivos demais; separe a área afetada.', 6)
    rows = []; total=0
    for path in sorted(paths):
        safe_subject_path(path)
        raw = primary if path==rel else fs.read(path, MAX_ASSET)
        require(raw is not None, 'stale_subject', 'Um recurso da proposta mudou durante a leitura.', 3)
        total += len(raw); require(total <= MAX_BUNDLE, 'preview_limit', 'Proposta excede limite de tamanho.', 6)
        rows.append({'path':path,'sha256':digest(raw)})
    return rows

def manifest_digest(rows): return object_digest(rows)

def _resource(value, current, root, allowed, grant):
    u=urlsplit(html.unescape(value.strip()))
    if u.scheme or u.netloc or u.query or u.fragment or '\\' in value: return None
    path=posixpath.normpath(posixpath.join(str(PurePosixPath(current).parent), unquote(u.path)))
    if not path.startswith(root+'/') or path not in allowed: return None
    return f'/preview/{grant}/'+__import__('urllib.parse',fromlist=['quote']).quote(path, safe='/')

def sanitize_css(text, current, root, allowed, grant):
    # CSS can fetch URLs. Keep only local, manifest-bound resources; deny all
    # imports. Modern browser CSP remains an independent network backstop.
    text = re.sub(r'/\*[\s\S]*?\*/', '', text)
    text = re.sub(r'@import\s+[^;]*(?:;|$)', '', text, flags=re.I)
    text = re.sub(r'(?i)(?:expression\s*\(|-moz-binding\s*:|behavior\s*:)', 'blocked:', text)
    # Escaped function names can obscure URLs; reject that stylesheet rather
    # than attempt to implement the entire CSS parser.
    if '\\' in text: return '/* CSS com escapes não é exibido pelo preview estático. */'
    def url(m):
        val=m.group(1).strip().strip('"\'')
        dest=_resource(val,current,root,allowed,grant)
        return 'url("'+dest+'")' if dest else 'url("")'
    return re.sub(r'url\s*\((.*?)\)', url, text, flags=re.I|re.S).replace('</','< /')

SAFE_TAGS=set('html head body title main section article aside nav header footer div span p br hr h1 h2 h3 h4 h5 h6 strong em b i u small sub sup mark label button input textarea select option fieldset legend table thead tbody tfoot tr td th caption colgroup col ul ol li dl dt dd figure figcaption img picture source details summary pre code blockquote a style link'.split())
DROP_CONTENT={'script','iframe','object','embed','template','noscript','svg','math','canvas','audio','video'}
VOID={'br','hr','input','img','source','link','col'}
SAFE_ATTRS={'class','id','title','alt','width','height','colspan','rowspan','placeholder','value','type','checked','selected','disabled','role','aria-label','aria-hidden','aria-expanded','open'}
class StaticHTML(HTMLParser):
    def __init__(self,current,root,allowed,grant):
        super().__init__(convert_charrefs=True);self.current=current;self.root=root;self.allowed=allowed;self.grant=grant;self.out=[];self.drop=[];self.in_style=False;self.css=[]
    def handle_starttag(self,tag,attrs):
        if self.drop:
            if tag in DROP_CONTENT:self.drop.append(tag)
            return
        if tag in DROP_CONTENT:self.drop.append(tag);return
        if tag=='meta' or tag=='base' or tag=='form' or tag not in SAFE_TAGS:return
        aa={k.lower():v or '' for k,v in attrs}
        if tag=='link':
            if aa.get('rel','').lower()!='stylesheet':return
            target=_resource(aa.get('href',''),self.current,self.root,self.allowed,self.grant)
            if not target:return
            self.out.append('<link rel="stylesheet" href="'+html.escape(target,quote=True)+'">');return
        if tag=='style':self.in_style=True;self.css=[];return
        cleaned=[]
        for key,val in aa.items():
            if key in SAFE_ATTRS or (key.startswith('aria-') and re.fullmatch('[a-z-]+',key)):
                if tag=='input' and key=='type' and val.lower() in {'file','password','submit','image'}:val='text'
                cleaned.append((key,redact(val)))
            elif key=='style':cleaned.append(('style',sanitize_css(val,self.current,self.root,self.allowed,self.grant)))
            elif tag in ('img','source') and key=='src':
                target=_resource(val,self.current,self.root,self.allowed,self.grant)
                if target:cleaned.append(('src',target))
        if tag=='a':cleaned.append(('role','link')) # no navigation, popups or downloads
        if tag=='button':cleaned=[x for x in cleaned if x[0]!='type']+[('type','button')]
        self.out.append('<'+tag+''.join(' '+k+'="'+html.escape(v,quote=True)+'"' for k,v in cleaned)+'>')
    def handle_endtag(self,tag):
        if self.drop:
            if tag==self.drop[-1]:self.drop.pop()
            return
        if tag=='style' and self.in_style:
            self.out.append('<style>'+sanitize_css(''.join(self.css),self.current,self.root,self.allowed,self.grant)+'</style>');self.in_style=False;return
        if tag in SAFE_TAGS and tag not in VOID:self.out.append('</'+tag+'>')
    def handle_data(self,data):
        if self.drop:return
        if self.in_style:self.css.append(data)
        else:self.out.append(html.escape(redact(data)))
    def handle_decl(self,decl):pass

def render_html(raw,current,allowed,grant):
    root=str(PurePosixPath(current).parent)
    p=StaticHTML(current,root,set(allowed),grant)
    try:p.feed(raw.decode('utf-8-sig'));p.close()
    except (UnicodeError,ValueError,RecursionError):raise MethodError('invalid_preview','HTML inválido para visualização estática.',4) from None
    return ('<!doctype html><meta charset="utf-8">'+''.join(p.out)).encode('utf-8')

def sanitize_svg(raw):
    # SVG is shown only as an image, with scripts/foreignObject/external
    # resources removed. Reject DTD/entities; no XML network/parser expansion.
    import xml.etree.ElementTree as ET
    require(b'<!DOCTYPE' not in raw.upper() and b'<!ENTITY' not in raw.upper(),'unsafe_svg','SVG com DTD/entidades não é exibido.',5)
    try: root=ET.fromstring(raw)
    except ET.ParseError:raise MethodError('invalid_preview','SVG inválido.',4) from None
    allowed={'svg','g','path','rect','circle','ellipse','line','polyline','polygon','text','tspan','defs','linearGradient','radialGradient','stop','clipPath','mask','use','title','desc'}
    for parent in root.iter():
        for child in list(parent):
            if child.tag.split('}')[-1] not in allowed:parent.remove(child)
        for k,v in list(parent.attrib.items()):
            name=k.split('}')[-1].lower()
            if name.startswith('on') or name=='style' or (name in ('href','src') and not v.startswith('#')) or ('url(' in v.lower() and not re.fullmatch(r'url\(#[\w-]+\)',v)):
                del parent.attrib[k]
    require(root.tag.split('}')[-1]=='svg','invalid_preview','Raiz SVG inválida.',4)
    return ET.tostring(root,encoding='utf-8')

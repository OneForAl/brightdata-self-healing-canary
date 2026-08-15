import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HOST = '0.0.0.0'
PORT = int(os.getenv('PORT', '8080'))
ADMIN_TOKEN = os.getenv('CANARY_ADMIN_TOKEN', 'change-me')
VARIANT = os.getenv('CANARY_VARIANT', 'baseline')

PRODUCTS = [
    {'id': 'p-101', 'name': 'Nebula Keyboard', 'price': 2499, 'currency': 'INR', 'category': 'Keyboards', 'rating': 4.6, 'in_stock': True},
    {'id': 'p-102', 'name': 'Orbit Mouse', 'price': 1499, 'currency': 'INR', 'category': 'Mice', 'rating': 4.3, 'in_stock': True},
    {'id': 'p-103', 'name': 'Quasar Headset', 'price': 3299, 'currency': 'INR', 'category': 'Audio', 'rating': 4.5, 'in_stock': False},
]

ALLOWED = {'baseline', 'class_rename', 'nested', 'attribute_rename', 'text_noise', 'reorder', 'hard_semantic'}

def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def product_card(p, variant):
    if variant == 'baseline':
        return f'''<article class="product-card" data-product-id="{p['id']}">\n  <h2 class="product-title">{esc(p['name'])}</h2>\n  <div class="product-meta"><span class="category">{esc(p['category'])}</span></div>\n  <div class="product-price" data-currency="{p['currency']}">{p['price']}</div>\n  <div class="product-rating">{p['rating']}</div>\n  <div class="stock">{'In stock' if p['in_stock'] else 'Out of stock'}</div>\n</article>'''
    if variant == 'class_rename':
        return f'''<div class="item" data-id="{p['id']}">\n  <h3 class="name">{esc(p['name'])}</h3>\n  <p class="taxonomy">{esc(p['category'])}</p>\n  <strong class="cost" data-money="{p['currency']}">{p['price']}</strong>\n  <span class="stars">{p['rating']}</span>\n  <span class="availability">{'Available' if p['in_stock'] else 'Unavailable'}</span>\n</div>'''
    if variant == 'nested':
        return f'''<section data-sku="{p['id']}" class="listing">\n  <header><h2>{esc(p['name'])}</h2></header>\n  <dl><div><dt>Category</dt><dd>{esc(p['category'])}</dd></div>\n      <div><dt>Price</dt><dd><span data-currency="{p['currency']}">{p['price']}</span></dd></div>\n      <div><dt>Rating</dt><dd>{p['rating']}</dd></div>\n      <div><dt>Status</dt><dd>{'In stock' if p['in_stock'] else 'Out of stock'}</dd></div></dl>\n</section>'''
    if variant == 'attribute_rename':
        return f'''<article class="product-card" data-sku="{p['id']}">\n  <h2 class="product-title">{esc(p['name'])}</h2>\n  <div class="product-meta"><span class="category">{esc(p['category'])}</span></div>\n  <div class="product-price" data-money-code="{p['currency']}">{p['price']}</div>\n  <div class="product-rating">{p['rating']}</div>\n  <div class="stock">{'In stock' if p['in_stock'] else 'Out of stock'}</div>\n</article>'''
    if variant == 'text_noise':
        return f'''<article class="result" data-ref="{p['id']}">\n  <div class="marketing"><small>Featured • Editor's pick</small></div>\n  <div class="content"><h2>{esc(p['name'])}</h2><p>Popular choice in {esc(p['category'])}.</p></div>\n  <div class="facts"><span>Price: ₹{p['price']}</span><span>Currency: {p['currency']}</span><span>Rating: {p['rating']}/5</span><span>Status: {'In stock' if p['in_stock'] else 'Out of stock'}</span></div>\n</article>'''
    if variant == 'reorder':
        return f'''<article data-product="{p['id']}" class="card">\n  <div class="product-rating">Rating {p['rating']}</div>\n  <div class="product-price">₹{p['price']}</div>\n  <h2>{esc(p['name'])}</h2>\n  <div class="category">{esc(p['category'])}</div>\n  <div class="stock">{'In stock' if p['in_stock'] else 'Out of stock'}</div>\n</article>'''
    if variant == 'hard_semantic':
        return f'''<article class="catalog-entry" data-item-key="{p['id']}">\n  <h2>{esc(p['name'])}</h2>\n  <p>Type: {esc(p['category'])}</p>\n  <p>MRP ₹{p['price']} ({p['currency']})</p>\n  <p>Score {p['rating']} out of 5</p>\n  <p>{'Currently available' if p['in_stock'] else 'Currently unavailable'}</p>\n</article>'''
    raise ValueError(f'unknown variant: {variant}')

def html():
    cards = '\n'.join(product_card(p, VARIANT) for p in PRODUCTS)
    return f'''<!doctype html><html><head><title>Canary Catalog</title></head><body><main><h1>Canary Catalog</h1><p id="canary-version">variant={VARIANT}</p><div id="catalog">{cards}</div></main></body></html>'''

class Handler(BaseHTTPRequestHandler):
    def send(self, code, content, content_type='text/html; charset=utf-8'):
        data = content.encode()
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/': self.send(200, html())
        elif path=='/health': self.send(200, json.dumps({'ok':True,'variant':VARIANT}), 'application/json')
        elif path=='/expected': self.send(200, json.dumps(PRODUCTS), 'application/json')
        else: self.send(404, 'not found', 'text/plain')
    def do_POST(self):
        global VARIANT
        path=urlparse(self.path).path
        prefix='/admin/variant/'
        token=self.headers.get('X-Canary-Token','')
        if path.startswith(prefix):
            if token != ADMIN_TOKEN: self.send(401, json.dumps({'error':'bad token'}), 'application/json'); return
            v=path[len(prefix):]
            if v not in ALLOWED: self.send(400, json.dumps({'error':'bad variant','allowed':sorted(ALLOWED)}), 'application/json'); return
            VARIANT=v; self.send(200, json.dumps({'ok':True,'variant':VARIANT}), 'application/json'); return
        self.send(404, 'not found', 'text/plain')
    def log_message(self, fmt, *args): pass

if __name__ == '__main__':
    print(f'Canary listening on {HOST}:{PORT}, variant={VARIANT}', flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

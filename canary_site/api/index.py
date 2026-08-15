from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
import os

app = FastAPI()

EXPECTED = [
    {"id":"p-101","name":"Nebula Keyboard","price":2499,"currency":"INR","category":"Keyboards","rating":4.6,"in_stock":True},
    {"id":"p-102","name":"Orbit Mouse","price":1499,"currency":"INR","category":"Mice","rating":4.3,"in_stock":True},
    {"id":"p-103","name":"Quasar Headset","price":3299,"currency":"INR","category":"Audio","rating":4.5,"in_stock":False},
]

# For Vercel, select the mutation using an environment variable.
# Change CANARY_VARIANT in the Vercel dashboard and redeploy.
VARIANT = os.getenv("CANARY_VARIANT", "baseline")


def product_html(p, variant):
    if variant == "class_rename":
        return f'''<div class="item" data-id="{p['id']}"><h3 class="name">{p['name']}</h3><strong class="cost" data-money="INR">{p['price']}</strong><p class="group">{p['category']}</p><span class="score">{p['rating']}</span><span class="availability">{'Available' if p['in_stock'] else 'Unavailable'}</span></div>'''
    if variant == "nested":
        return f'''<section class="catalog-entry"><dl><dt>ID</dt><dd>{p['id']}</dd><dt>Product</dt><dd>{p['name']}</dd><dt>Price</dt><dd>{p['price']} INR</dd><dt>Category</dt><dd>{p['category']}</dd><dt>Rating</dt><dd>{p['rating']}</dd><dt>Status</dt><dd>{'In stock' if p['in_stock'] else 'Out of stock'}</dd></dl></section>'''
    if variant == "attribute_rename":
        return f'''<article class="product-card" data-product-id="{p['id']}"><h2 class="product-title">{p['name']}</h2><div class="product-price" data-money-code="INR">{p['price']}</div><div class="product-category">{p['category']}</div><div class="product-rating">{p['rating']}</div><div class="stock">{'in stock' if p['in_stock'] else 'out of stock'}</div></article>'''
    if variant == "text_noise":
        return f'''<article class="product-card" data-product-id="{p['id']}"><h2 class="product-title">{p['name']}</h2><p>Limited-time launch offer. Popular choice for students and creators.</p><div class="product-price">Price: ₹{p['price']}</div><div class="product-category">Category: {p['category']}</div><div class="product-rating">Customer rating: {p['rating']}/5</div><div class="stock">{'Currently in stock' if p['in_stock'] else 'Currently unavailable'}</div></article>'''
    if variant == "reorder":
        price = f"₹ {p['price']:,}"
        return f'''<article class="product-card" data-product-id="{p['id']}"><div class="product-rating">{p['rating']}/5</div><div class="stock">{'Available now' if p['in_stock'] else 'Sold out'}</div><div class="product-category">{p['category']}</div><h2 class="product-title">{p['name']}</h2><div class="product-price">{price}</div></article>'''
    if variant == "hard_semantic":
        return f'''<div class="listing" data-sku="{p['id']}"><header>{p['name']}</header><p>SKU: {p['id']}</p><p>Amount payable: INR {p['price']}</p><p>Department: {p['category']}</p><p>Stars: {p['rating']}</p><p>Fulfilment: {'ready to ship' if p['in_stock'] else 'not available'}</p></div>'''
    return f'''<article class="product-card" data-product-id="{p['id']}"><h2 class="product-title">{p['name']}</h2><div class="product-price" data-currency="INR">{p['price']}</div><div class="product-category">{p['category']}</div><div class="product-rating">{p['rating']}</div><div class="stock">{'In stock' if p['in_stock'] else 'Out of stock'}</div></article>'''


@app.get("/", response_class=HTMLResponse)
def home():
    cards = "\n".join(product_html(p, VARIANT) for p in EXPECTED)
    return f'''<!doctype html><html><head><title>Canary Catalog</title></head><body><main><h1>Canary Catalog</h1><p id="variant">variant={VARIANT}</p><section id="catalog">{cards}</section></main></body></html>'''


@app.get("/health")
def health():
    return {"ok": True, "variant": VARIANT}


@app.get("/expected")
def expected():
    return {"variant": VARIANT, "products": EXPECTED}


@app.get("/admin/variant")
def admin_variant():
    return {"variant": VARIANT, "note": "On Vercel, change CANARY_VARIANT in Project Settings and redeploy."}

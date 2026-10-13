"""SatGate: demonstration-only Bitcoin checkout. No payments or funds involved."""
import json
import secrets
import sqlite3
import os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import RLock
from urllib.parse import urlsplit

PRODUCTS={"supporter":{"name":"Supporter pass","sats":2500},"builder":{"name":"Builder pass","sats":10000}}
ROOT=Path(__file__).resolve().parents[1]
DB_PATH=os.environ.get("SATGATE_DB","satgate.sqlite3")
LOCK=RLock()
def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS orders
          (id TEXT PRIMARY KEY, request_id TEXT UNIQUE NOT NULL, product TEXT NOT NULL,
           sats INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'pending')""")
def create_order(product, request_id):
    if product not in PRODUCTS or not isinstance(request_id,str) or not (12<=len(request_id)<=100) or not request_id.replace("-","").replace("_","").isalnum():
        raise ValueError("Invalid product or idempotency key")
    with LOCK, sqlite3.connect(DB_PATH) as db:
        row=db.execute("SELECT id,product,sats,status FROM orders WHERE request_id=?",(request_id,)).fetchone()
        if row:
            if row[1]!=product: raise ValueError("Idempotency key used for another product")
            return dict(zip(("id","product","sats","status"),row))
        order_id=secrets.token_hex(16)
        db.execute("INSERT INTO orders (id,request_id,product,sats,status) VALUES (?,?,?,?,?)",
                   (order_id,request_id,product,PRODUCTS[product]["sats"],"pending"))
        return {"id":order_id,"product":product,"sats":PRODUCTS[product]["sats"],"status":"pending"}
def get_order(order_id):
    if not isinstance(order_id,str) or len(order_id)!=32 or any(c not in "0123456789abcdef" for c in order_id):
        return None
    with LOCK, sqlite3.connect(DB_PATH) as db:
        row=db.execute("SELECT id,product,sats,status FROM orders WHERE id=?",(order_id,)).fetchone()
    return dict(zip(("id","product","sats","status"),row)) if row else None
def simulate_settle(order_id):
    with LOCK, sqlite3.connect(DB_PATH) as db:
        db.execute("UPDATE orders SET status='settled' WHERE id=? AND status='pending'",(order_id,))
    return get_order(order_id)
class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        data=json.dumps(payload).encode()
        self.send_response(status);self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Content-Length",str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        path=urlsplit(self.path).path
        if path=="/":
            body=(ROOT/"static"/"index.html").read_bytes()
            self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
        elif path=="/healthz":self.send_json(200,{"ok":True,"demo":True})
        elif path=="/api/products":self.send_json(200,{"products":PRODUCTS,"demo":True})
        elif path.startswith("/api/orders/"):
            o=get_order(path.split("/")[-1])
            self.send_json(200,{**o,"demo":True} if o else {"error":"Not found"}) if o else self.send_json(404,{"error":"Not found"})
        else:self.send_json(404,{"error":"Not found"})
    def do_POST(self):
        size=self.headers.get("Content-Length","")
        try:
            if not size.isdigit() or int(size)>4096:raise ValueError()
            data=json.loads(self.rfile.read(int(size)))
            if not isinstance(data,dict):raise ValueError()
        except (ValueError,TypeError,UnicodeError,json.JSONDecodeError):
            return self.send_json(400,{"error":"Invalid JSON"})
        path=urlsplit(self.path).path
        if path=="/api/checkout":
            try:o=create_order(data.get("product"),data.get("request_id"))
            except ValueError:return self.send_json(400,{"error":"Invalid checkout"})
            return self.send_json(201,{**o,"demo":True})
        if path=="/api/demo/settle":
            # Only simulated invoices exist in this version.
            o=simulate_settle(data.get("order_id"))
            return self.send_json(200,{**o,"demo":True,"simulated":True}) if o else self.send_json(404,{"error":"Not found"})
        self.send_json(404,{"error":"Not found"})
def main():
    init_db()
    host=os.environ.get("SATGATE_HOST","127.0.0.1")
    port=int(os.environ.get("SATGATE_PORT","8765"))
    print("SatGate demonstration-only (NO real payments) at http://%s:%s"%(host,port))
    ThreadingHTTPServer((host,port),Handler).serve_forever()
if __name__=="__main__":main()

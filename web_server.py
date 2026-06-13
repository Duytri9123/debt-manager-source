# -*- coding: utf-8 -*-
"""
B2B Management — Web Server
QSS theme from src/ui/theme.py → converted to CSS
"""
import os, sys, json, io
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request, send_file

sys.path.insert(0, os.path.dirname(__file__))

from src.database import Database
from src.services.customer_service import CustomerService
from src.services.order_service import OrderService
from src.services.debt_service import DebtService
from src.services.advance_service import AdvanceService
from src.services.excel_service import ExcelService


# ── CSS (converted from QSS in src/ui/theme.py — same colors, same everything) ──
CSS = """
:root{--bg:#f8fafc;--card:#fff;--text:#1e293b;--heading:#0f172a;--muted:#64748b;
--border:#f1f5f9;--borderm:#e2e8f0;--primary:#6366f1;--primaryh:#4f46e5;--primaryp:#4338ca;
--success:#10b981;--warning:#f59e0b;--danger:#ef4444;--info:#0ea5e9;
--sidebar:#0f172a;--navtext:#94a3b8;--radius:10px;--radiusl:14px;}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Inter,sans-serif;background:var(--bg);color:var(--text);font-size:13px;min-height:100vh}
a{color:var(--primary);text-decoration:none}
/* ── SIDEBAR ── */
.sidebar{position:fixed;top:0;left:0;bottom:0;width:220px;background:var(--sidebar);z-index:100;display:flex;flex-direction:column}
.sidebar-header{height:58px;display:flex;align-items:center;justify-content:space-between;padding:0 16px;border-bottom:1px solid rgba(148,163,184,.08)}
.logo{color:#fff;font-size:18px;font-weight:800;letter-spacing:0}
.sidebar-scroll{flex:1;overflow-y:auto;overflow-x:hidden;padding:12px 8px 8px}
.sidebar-scroll::-webkit-scrollbar{width:4px}
.sidebar-scroll::-webkit-scrollbar-thumb{background:rgba(148,163,184,.3);border-radius:2px}
.nav-btn{display:flex;align-items:center;gap:10px;width:100%;background:0 0;color:var(--navtext);border:none;border-radius:var(--radius);padding:11px 14px;text-align:left;font-size:15px;font-weight:500;cursor:pointer;transition:all .15s}
.nav-btn:hover{background:rgba(99,102,241,.12);color:#e2e8f0}
.nav-btn.active{background:var(--primary);color:#fff;font-weight:700}
.nav-icon{font-size:18px;width:22px;text-align:center}
.user-row{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.avatar{width:32px;height:32px;background:#312e81;color:#c7d2fe;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;flex-shrink:0}
.user-name{color:#f1f5f9;font-size:13px;font-weight:700}
.user-email{color:#818cf8;font-size:11px}
/* ── MAIN ── */
.main{margin-left:220px;min-height:100vh;display:flex;flex-direction:column}
.content{padding:24px;flex:1}
/* ── TITLES ── */
.page-title{color:var(--heading);font-size:22px;font-weight:800}
.page-subtitle{color:var(--muted);font-size:13px;margin-top:4px}
.section-title{color:var(--heading);font-size:15px;font-weight:700}
.form-label{color:#475569;font-size:12px;font-weight:600;display:block;margin-bottom:6px}
/* ── CARDS ── */
.stat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.stat-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radiusl);padding:16px 18px;transition:all .2s}
.stat-card:hover{border-color:var(--borderm)}
.stat-card .stat-title{color:#94a3b8;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:6px}
.stat-card .stat-value{color:var(--heading);font-size:24px;font-weight:800}
.stat-card-indigo{background:#eef2ff;border-color:#e0e7ff}.stat-card-indigo:hover{border-color:#c7d2fe}
.stat-card-success{background:#ecfdf5;border-color:#d1fae5}.stat-card-success:hover{border-color:#a7f3d0}
.stat-card-warning{background:#fffbeb;border-color:#fef3c7}.stat-card-warning:hover{border-color:#fde68a}
.stat-card-danger{background:#fef2f2;border-color:#fee2e2}.stat-card-danger:hover{border-color:#fecaca}
.stat-card-blue{background:#eff6ff;border-color:#dbeafe}
/* ── CARDS / FORMS ── */
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radiusl);padding:20px}
.card-form{background:var(--card);border:1px solid var(--borderm);border-radius:var(--radiusl);padding:18px}
.filter-bar{background:var(--card);border:1px solid var(--borderm);border-radius:var(--radiusl);padding:12px 16px;margin-bottom:16px}
/* ── BUTTONS ── */
.btn{display:inline-flex;align-items:center;gap:6px;border:none;border-radius:var(--radius);padding:10px 20px;font-size:13px;font-weight:600;cursor:pointer;transition:all .15s;white-space:nowrap}
.btn-primary{background:var(--primary);color:#fff}.btn-primary:hover{background:var(--primaryh)}.btn-primary:active{background:var(--primaryp)}
.btn-success{background:var(--success);color:#fff}.btn-success:hover{background:#059669}
.btn-warning{background:var(--warning);color:#fff}.btn-warning:hover{background:#d97706}
.btn-danger{background:var(--danger);color:#fff}.btn-danger:hover{background:#dc2626}
.btn-outline{background:#fff;color:var(--primary);border:1.5px solid var(--borderm)}.btn-outline:hover{background:#f8fafc;border-color:var(--primary)}
.btn-sm{padding:6px 14px;font-size:12px}
.btn-xs{padding:4px 10px;font-size:11px;border-radius:7px}
/* ── BADGES ── */
.badge{display:inline-block;border-radius:20px;padding:5px 14px;font-weight:700;font-size:11px}
.badge-success{background:#d1fae5;color:#065f46}
.badge-warning{background:#fef3c7;color:#92400e}
.badge-danger{background:#fee2e2;color:#991b1b}
.badge-info{background:#dbeafe;color:#1e40af}
.badge-neutral{background:#f1f5f9;color:#475569}
/* ── INPUTS ── */
input:not([type=checkbox]):not([type=radio]),textarea,select{
    background:#fff;border:1.5px solid var(--borderm);border-radius:var(--radius);
    padding:10px 14px;font-size:13px;color:var(--text);width:100%;font-family:inherit;transition:border .15s
}
input:focus,textarea:focus,select:focus{border-color:var(--primary);outline:none;box-shadow:0 0 0 3px rgba(99,102,241,.1)}
input:hover,textarea:hover,select:hover{border-color:#cbd5e1}
select{appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2364748b' d='M6 8L1 3h10z'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 14px center;padding-right:36px}
textarea{resize:vertical;min-height:80px}
::placeholder{color:#94a3b8}
input[type=date]{min-width:150px}
/* ── TABLES ── */
.data-table{width:100%;background:var(--card);border:1px solid var(--border);border-radius:var(--radiusl);border-collapse:collapse;overflow:hidden}
.data-table thead th{background:#fafbfc;color:#94a3b8;padding:12px 14px;text-align:left;font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:.8px;border-bottom:2px solid var(--border)}
.data-table tbody td{padding:10px 14px;border-bottom:1px solid #f8fafc;font-size:13px}
.data-table tbody tr:hover td{background:#f8fafc}
.data-table tbody tr:last-child td{border-bottom:none}
.text-right{text-align:right}
.text-center{text-align:center}
.empty-row td{text-align:center;color:var(--muted);padding:40px!important;font-size:14px}
/* ── MODAL ── */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:200;display:flex;align-items:center;justify-content:center;animation:fadeIn .15s}
.modal{background:var(--card);border-radius:16px;width:90%;max-width:700px;max-height:85vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.15);animation:slideUp .2s}
.modal-lg{max-width:1000px}
.modal-header{display:flex;align-items:center;justify-content:space-between;padding:18px 20px;border-bottom:1px solid var(--border)}
.modal-body{padding:20px}
.modal-footer{display:flex;justify-content:flex-end;gap:10px;padding:16px 20px;border-top:1px solid var(--border)}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.form-grid.span-2{grid-column:span 2}
.form-row{display:flex;flex-direction:column;gap:6px}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes slideUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}
/* ── TOAST ── */
.toast{position:fixed;bottom:24px;right:24px;z-index:300;padding:14px 20px;border-radius:var(--radius);color:#fff;font-weight:600;font-size:14px;animation:slideUp .25s;box-shadow:0 4px 20px rgba(0,0,0,.2)}
.toast-success{background:var(--success)}.toast-error{background:var(--danger)}
/* ── FLEX UTILS ── */
.flex{display:flex}.flex-col{flex-direction:column}.items-center{align-items:center}.justify-between{justify-content:space-between}.gap-2{gap:8px}.gap-3{gap:12px}.gap-4{gap:16px}.flex-1{flex:1}.flex-wrap{flex-wrap:wrap}
.mt-2{margin-top:8px}.mt-3{margin-top:12px}.mt-4{margin-top:16px}.mt-6{margin-top:24px}.mb-3{margin-bottom:12px}.mb-4{margin-bottom:16px}
/* ── SCROLLBAR ── */
::-webkit-scrollbar{width:6px;height:6px}::-webkit-scrollbar-track{background:0 0}::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:3px}::-webkit-scrollbar-thumb:hover{background:#94a3b8}
/* ── LINE ITEMS TABLE (order form) ── */
.line-table{width:100%;border-collapse:collapse}.line-table td{padding:4px 6px}.line-table input{border-radius:7px;padding:8px 10px}
/* ── SEGMENT ── */
.segmented{display:inline-flex;background:#f1f5f9;border-radius:12px;padding:4px;gap:2px}
.segment-btn{background:0 0;color:var(--muted);border:none;border-radius:9px;padding:8px 16px;font-size:12px;font-weight:600;cursor:pointer;transition:all .15s}
.segment-btn.active{background:#fff;color:var(--heading);box-shadow:0 1px 2px rgba(0,0,0,.05)}
"""

# ── HTML TEMPLATE ──
HTML = """<!DOCTYPE html>
<html lang="vi">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Quản lý B2B</title><style>{{css|safe}}</style></head>
<body>
<div class="sidebar">
  <div class="sidebar-header"><span class="logo">Quản lý công nợ</span></div>
  <div class="sidebar-scroll">
    {% for k,icon,label in nav_items %}
    <button class="nav-btn{%if k==page%} active{%endif%}" onclick="nav('{{k}}')">
      <span class="nav-icon">{{icon}}</span>{{label}}
    </button>
    {% endfor %}
  </div>
</div>
<div class="main">
  <div class="content" id="page-content">{{content|safe}}</div>
</div>
<div id="modal-container"></div>
<div id="toast-container"></div>
<script>
const API='/api';let currentPage='{{page}}';
function nav(p){window.location.href='/'+p}
function fmt(v){return Number(v||0).toLocaleString('vi-VN')+'đ'}
function date(v){return v?v.slice(0,10):'—'}
function openModal(html){document.getElementById('modal-container').innerHTML=html}
function closeModal(){document.getElementById('modal-container').innerHTML=''}
function toast(msg,type='success'){let t=document.getElementById('toast-container');t.innerHTML='<div class="toast toast-'+type+'">'+msg+'</div>';setTimeout(()=>t.innerHTML='',3000)}
async function api(url,opts={}){try{let r=await fetch(API+url,{headers:{'Content-Type':'application/json'},...opts});if(!r.ok)throw await r.json();return await r.json()}catch(e){toast(e.error||'Lỗi kết nối','error');throw e}}
document.addEventListener('click',e=>{if(e.target.classList.contains('modal-overlay'))closeModal()})
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal()})
</script>
</body></html>"""

# ── PAGE TEMPLATES ──

DASHBOARD = """
<div class="flex items-center justify-between mb-4">
  <div><h1 class="page-title">Dashboard</h1><p class="page-subtitle">Tổng quan hệ thống</p></div>
  <div class="segmented">
    <button class="segment-btn active">Tháng này</button>
    <button class="segment-btn">Quý này</button>
    <button class="segment-btn">Năm này</button>
  </div>
</div>
<div class="stat-grid mb-4" id="stats-all"></div>
<div class="stat-grid mb-4" id="stats-period"></div>
<div class="stat-grid">
  <div class="stat-card" style="grid-column:span 2"><div class="section-title mb-3">Doanh thu theo thời gian</div><div style="height:180px;display:flex;align-items:center;justify-content:center;color:var(--muted)">Biểu đồ sẽ hiển thị tại đây</div></div>
  <div class="stat-card" style="grid-column:span 2"><div class="section-title mb-3">Số đơn hàng theo thời gian</div><div style="height:180px;display:flex;align-items:center;justify-content:center;color:var(--muted)">Biểu đồ sẽ hiển thị tại đây</div></div>
</div>
<script>
(async()=>{try{let d=await api('/dashboard');
document.getElementById('stats-all').innerHTML=
  '<div class="stat-card stat-card-indigo"><div class="stat-title">Người dùng</div><div class="stat-value">'+d.allTimeStats.total_customers+'</div></div>'+
  '<div class="stat-card stat-card-blue"><div class="stat-title">Tổng đơn hàng</div><div class="stat-value">'+d.allTimeStats.total_orders+'</div></div>'+
  '<div class="stat-card stat-card-warning"><div class="stat-title">Công nợ chưa TT</div><div class="stat-value" style="color:#d97706">'+fmt(d.allTimeStats.total_debt_amount)+'</div></div>'+
  '<div class="stat-card stat-card-success"><div class="stat-title">Đã thu</div><div class="stat-value" style="color:#059669">'+fmt(d.allTimeStats.total_revenue)+'</div></div>';
document.getElementById('stats-period').innerHTML=
  '<div class="stat-card"><div class="stat-title">Doanh thu kỳ này</div><div class="stat-value">'+fmt(d.periodStats.revenue)+'</div></div>'+
  '<div class="stat-card"><div class="stat-title">Đơn hàng kỳ này</div><div class="stat-value">'+d.periodStats.orders+'</div></div>'+
  '<div class="stat-card"><div class="stat-title">Khách mới</div><div class="stat-value">'+d.periodStats.new_customers+'</div></div>'+
  '<div class="stat-card"><div class="stat-title">TB / Đơn</div><div class="stat-value">'+fmt(d.periodStats.avg_order_value)+'</div></div>';
}catch(e){}})()
</script>"""

CUSTOMERS = """
<div class="flex items-center justify-between mb-4">
  <div><h1 class="page-title">Hồ sơ Khách hàng</h1><p class="page-subtitle" id="cust-count">Đang tải...</p></div>
  <button class="btn btn-primary" onclick="showAddCustomer()">+  Thêm khách hàng</button>
</div>
<div class="filter-bar flex items-center gap-3">
  <input placeholder="Tìm tên, SĐT, địa chỉ..." id="cust-search" onkeyup="loadCustomers()" class="flex-1">
  <select id="cust-sort" onchange="loadCustomers()" style="width:180px">
    <option value="created_at">Sắp xếp: Ngày tạo</option>
    <option value="name">Sắp xếp: Tên</option>
    <option value="orders_count">Sắp xếp: Đơn hàng</option>
  </select>
  <button class="btn btn-outline btn-sm" onclick="document.getElementById('cust-search').value='';loadCustomers()">Xóa lọc</button>
</div>
<div style="overflow-x:auto"><table class="data-table"><thead><tr>
  <th>Khách hàng</th><th>MST</th><th>SĐT</th><th>Địa chỉ</th><th>Đơn hàng</th><th>Tổng ĐH</th><th>Công nợ</th>
</tr></thead><tbody id="cust-body"></tbody></table></div>
<script>
async function loadCustomers(){
  let s=document.getElementById('cust-search').value;
  let sort=document.getElementById('cust-sort').value;
  let d=await api('/customers?search='+s+'&sort='+sort);
  document.getElementById('cust-count').textContent=d.total+' khách hàng';
  let rows=d.data.map(c=>'<tr onclick="showCustomer('+c.id+')" style="cursor:pointer">'+
    '<td><b>'+c.name+'</b></td><td>'+(c.tax_code||'—')+'</td><td>'+(c.phone||'—')+'</td><td>'+(c.address||'—')+'</td>'+
    '<td class="text-right">'+(c.orders_count||0)+'</td><td class="text-right">'+fmt(c.total_order_value)+'</td>'+
    '<td class="text-right" style="color:'+(c.remaining_debt>0?'#dc2626':'#6b7280')+'">'+fmt(c.remaining_debt)+'</td></tr>').join('');
  document.getElementById('cust-body').innerHTML=rows||'<tr class="empty-row"><td colspan="7">Không có khách hàng nào</td></tr>';
}
function showAddCustomer(){openModal(`
<div class="modal-overlay"><div class="modal"><div class="modal-header"><h2 class="dialog-title">Thêm khách hàng mới</h2><button class="btn btn-outline btn-sm" onclick="closeModal()">✕</button></div>
<div class="modal-body"><div class="form-grid">
<div class="form-row"><label class="form-label">Tên khách hàng *</label><input id="c-name" placeholder="Nhập tên khách hàng"></div>
<div class="form-row"><label class="form-label">Số điện thoại</label><input id="c-phone" placeholder="Nhập số điện thoại"></div>
<div class="form-row"><label class="form-label">Email</label><input id="c-email" placeholder="Nhập email"></div>
<div class="form-row"><label class="form-label">Mã số thuế</label><input id="c-tax" placeholder="Nhập MST"></div>
<div class="form-row" style="grid-column:span 2"><label class="form-label">Địa chỉ</label><input id="c-addr" placeholder="Nhập địa chỉ"></div>
<div class="form-row" style="grid-column:span 2"><label class="form-label">Ghi chú</label><textarea id="c-notes" placeholder="Ghi chú" rows="2"></textarea></div>
</div></div>
<div class="modal-footer"><button class="btn btn-outline" onclick="closeModal()">Hủy</button>
<button class="btn btn-primary" onclick="saveCustomer()">Lưu khách hàng</button></div></div></div>`)}
async function saveCustomer(){
  let data={name:document.getElementById('c-name').value,phone:document.getElementById('c-phone').value,email:document.getElementById('c-email').value,tax_code:document.getElementById('c-tax').value,address:document.getElementById('c-addr').value,notes:document.getElementById('c-notes').value,is_active:true};
  if(!data.name)return toast('Tên khách hàng là bắt buộc','error');
  await api('/customers',{method:'POST',body:JSON.stringify(data)});closeModal();toast('Đã thêm khách hàng');loadCustomers()
}
async function showCustomer(id){
  let c=await api('/customers/'+id);
  openModal('<div class="modal-overlay"><div class="modal modal-lg"><div class="modal-header"><h2 class="dialog-title">'+c.name+'</h2><button class="btn btn-outline btn-sm" onclick="closeModal()">✕</button></div>'+
  '<div class="modal-body"><div class="flex items-center gap-4 mb-4"><div class="avatar" style="width:48px;height:48px;font-size:18px">'+(c.name||'?')[0]+'</div><div><b style="font-size:16px">'+c.name+'</b><div class="page-subtitle">MST: '+(c.tax_code||'—')+' | SĐT: '+(c.phone||'—')+' | '+(c.address||'—')+'</div></div></div>'+
  '<div class="stat-grid mb-4">'+['Đơn hàng','Đã thanh toán','Tổng công nợ','Còn phải thu'].map((t,i)=>
    '<div class="stat-card '+(i==1?'stat-card-success':i==2?'stat-card-warning':i==3?'stat-card-danger':'stat-card-blue')+'"><div class="stat-title">'+t+'</div><div class="stat-value">'+
    [c.orders_count||0,fmt(c.total_paid||0),fmt(c.total_debt||0),fmt(c.remaining_debt||0)][i]+'</div></div>').join('')+'</div>'+
  '<div class="stat-grid"><div class="card"><div class="section-title mb-3">Đơn hàng</div><table class="data-table"><thead><tr><th>Mã ĐH</th><th>Tên ĐH</th><th>Ngày</th><th>Tổng</th></tr></thead><tbody>'+
  ((c.orders||[]).map(o=>'<tr><td>'+o.order_number+'</td><td>'+(o.order_name||'—')+'</td><td>'+date(o.created_at)+'</td><td class="text-right">'+fmt(o.grand_total)+'</td></tr>').join('')||'<tr class="empty-row"><td colspan="4">Chưa có đơn hàng</td></tr>')+
  '</tbody></table></div><div class="card"><div class="section-title mb-3">Công nợ</div><table class="data-table"><thead><tr><th>Đơn</th><th>Tổng</th><th>Đã TT</th><th>Còn lại</th></tr></thead><tbody>'+
  ((c.debts||[]).map(d=>'<tr><td>'+(d.order_number||'—')+'</td><td class="text-right">'+fmt(d.original_amount)+'</td><td class="text-right">'+fmt(d.paid_amount)+'</td><td class="text-right" style="color:#dc2626">'+fmt(d.remaining_amount)+'</td></tr>').join('')||'<tr class="empty-row"><td colspan="4">Không có công nợ</td></tr>')+
  '</tbody></table></div></div></div></div></div>')
}
loadCustomers()
</script>"""

ORDERS = """
<div class="flex items-center justify-between mb-4">
  <div><h1 class="page-title">Theo dõi Đơn hàng KD</h1><p class="page-subtitle">Quản lý đơn hàng kinh doanh B2B</p></div>
  <div class="flex gap-2">
    <button class="btn btn-outline" onclick="importExcel()">Import Excel</button>
    <button class="btn btn-primary" onclick="showAddOrder()">+  Tạo đơn hàng</button>
  </div>
</div>
<div class="stat-grid mb-4" id="order-stats"></div>
<div class="filter-bar flex items-center gap-3 flex-wrap">
  <input placeholder="Tìm mã đơn, tên KH..." id="ord-search" onkeyup="loadOrders()" class="flex-1">
  <input type="date" id="ord-from" onchange="loadOrders()" style="width:150px">
  <input type="date" id="ord-to" onchange="loadOrders()" style="width:150px">
  <button class="btn btn-outline btn-sm" onclick="document.getElementById('ord-search').value='';loadOrders()">Reset</button>
</div>
<div style="overflow-x:auto"><table class="data-table"><thead><tr>
  <th>Mã đơn</th><th>Khách hàng</th><th>Tên đơn hàng</th><th>Ngày đặt</th><th>Ngày xuất</th><th>Trạng thái</th><th>Số SP</th><th>Tổng</th>
</tr></thead><tbody id="ord-body"></tbody></table></div>
<script>
(async function init(){
  let from=new Date();from.setMonth(from.getMonth()-12);
  document.getElementById('ord-from').value=from.toISOString().slice(0,10);
  document.getElementById('ord-to').value=new Date().toISOString().slice(0,10);
  loadOrders()
})()
async function loadOrders(){
  let s=document.getElementById('ord-search').value,f=document.getElementById('ord-from').value,t=document.getElementById('ord-to').value;
  let d=await api('/orders?search='+s+'&from='+f+'&to='+t);
  document.getElementById('order-stats').innerHTML=
    '<div class="stat-card stat-card-indigo"><div class="stat-title">Tổng đơn</div><div class="stat-value">'+d.stats.total_orders+'</div></div>'+
    '<div class="stat-card stat-card-blue"><div class="stat-title">Khách hàng</div><div class="stat-value">'+d.stats.total_customers+'</div></div>'+
    '<div class="stat-card stat-card-success"><div class="stat-title">Doanh thu</div><div class="stat-value" style="color:#059669">'+fmt(d.stats.total_revenue)+'</div></div>';
  let rows=d.data.map(o=>'<tr onclick="viewOrder('+o.id+')" style="cursor:pointer">'+
    '<td style="color:var(--primary);font-weight:600">'+o.order_number+'</td><td>'+o.customer_name+'</td><td>'+(o.order_name||'—')+'</td>'+
    '<td>'+date(o.created_at)+'</td><td>'+date(o.delivery_date)+'</td>'+
    '<td><span class="badge '+(o.payment_status=='paid'?'badge-success':o.payment_status=='partial'?'badge-warning':'badge-danger')+'">'+
    ({paid:'Đã TT',partial:'Một phần',unpaid:'Chưa TT'}[o.payment_status||'unpaid'])+'</span></td>'+
    '<td class="text-center">'+(o.items_count||0)+'</td><td class="text-right"><b>'+fmt(o.grand_total)+'</b></td></tr>').join('');
  document.getElementById('ord-body').innerHTML=rows||'<tr class="empty-row"><td colspan="8">Chưa có đơn hàng nào</td></tr>';
}
async function showAddOrder(){
  let customers=await api('/customers');let opts=customers.data.map(c=>'<option value="'+c.id+'">'+c.name+'</option>').join('');
  openModal('<div class="modal-overlay"><div class="modal modal-lg"><div class="modal-header"><h2 class="dialog-title">Tạo đơn hàng mới</h2><button class="btn btn-outline btn-sm" onclick="closeModal()">✕</button></div>'+
  '<div class="modal-body"><div class="form-grid">'+
  '<div class="form-row"><label class="form-label">Khách hàng *</label><select id="o-customer">'+opts+'</select></div>'+
  '<div class="form-row"><label class="form-label">SĐT</label><input id="o-phone"></div>'+
  '<div class="form-row"><label class="form-label">Ngày đặt *</label><input type="date" id="o-date" value="'+new Date().toISOString().slice(0,10)+'"></div>'+
  '<div class="form-row"><label class="form-label">Ngày xuất</label><input type="date" id="o-delivery" value="'+new Date().toISOString().slice(0,10)+'"></div>'+
  '<div class="form-row" style="grid-column:span 2"><label class="form-label">Tên đơn hàng</label><input id="o-name" placeholder="VD: Đơn tháng 5, Dự án ABC..."></div>'+
  '<div class="form-row"><label class="form-label">Trạng thái</label><select id="o-status"><option value="pending">Chờ xử lý</option><option value="processing">Đang xử lý</option><option value="delivered">Đã giao</option><option value="cancelled">Đã hủy</option></select></div>'+
  '<div class="form-row" style="grid-column:span 2"><label class="form-label">Ghi chú</label><textarea id="o-notes" rows="2"></textarea></div>'+
  '</div><div class="section-title mt-4 mb-3">Chi tiết sản phẩm</div>'+
  '<table class="line-table" id="line-items"><thead><tr><th>Mô tả *</th><th>Mã</th><th>Xuất xứ</th><th>ĐV</th><th>SL</th><th>Đơn giá</th><th>Thành tiền</th><th>Ghi chú</th><th></th></tr></thead><tbody id="line-body"></tbody></table>'+
  '<button class="btn btn-outline btn-sm mt-3" onclick="addLine()">+  Thêm dòng</button></div>'+
  '<div class="modal-footer"><button class="btn btn-outline" onclick="closeModal()">Hủy</button><button class="btn btn-primary" onclick="saveOrder()">Tạo đơn hàng</button></div></div></div>');
  addLine()
}
window._lineCount=0
function addLine(){let i=window._lineCount++;document.getElementById('line-body').insertAdjacentHTML('beforeend',
  '<tr id="line-'+i+'"><td><input class="line-input" placeholder="Mô tả SP"></td><td><input class="line-input" placeholder="Mã" style="width:80px"></td><td><input class="line-input" placeholder="VN" style="width:60px"></td><td><input class="line-input" placeholder="Cái" style="width:60px"></td>'+
  '<td><input type="number" class="line-input line-qty" value="1" min="0" style="width:80px" onchange="updateLineTotal('+i+')"></td>'+
  '<td><input type="number" class="line-input line-price" value="0" min="0" style="width:130px" onchange="updateLineTotal('+i+')"></td>'+
  '<td class="text-right" id="line-total-'+i+'" style="font-weight:700">0đ</td><td><input class="line-input" placeholder="Ghi chú" style="width:100px"></td>'+
  '<td><button class="btn btn-outline btn-xs" style="color:var(--danger);border-color:var(--danger)" onclick="document.getElementById(\'line-'+i+'\').remove()">✕</button></td></tr>')}
function updateLineTotal(i){let q=parseFloat(document.querySelector('#line-'+i+' .line-qty').value)||0;let p=parseFloat(document.querySelector('#line-'+i+' .line-price').value)||0;document.getElementById('line-total-'+i).textContent=fmt(q*p)}
async function saveOrder(){
  let items=[];document.querySelectorAll('#line-body tr').forEach(row=>{
    let desc=row.querySelectorAll('input')[0].value;if(!desc)return;
    let qty=parseFloat(row.querySelector('.line-qty').value)||0;
    let uprice=parseFloat(row.querySelector('.line-price').value)||0;
    items.push({description:desc,product_code:row.querySelectorAll('input')[1].value,origin:row.querySelectorAll('input')[2].value,unit:row.querySelectorAll('input')[3].value,quantity:qty,unit_price:uprice,line_total:qty*uprice,note:row.querySelectorAll('input')[6]?.value||''})
  });
  if(!items.length)return toast('Cần ít nhất 1 sản phẩm','error');
  let custSel=document.getElementById('o-customer');
  await api('/orders',{method:'POST',body:JSON.stringify({customer_id:custSel.value?parseInt(custSel.value):null,customer_name:custSel.selectedOptions[0].text,customer_phone:document.getElementById('o-phone').value,order_name:document.getElementById('o-name').value,status:document.getElementById('o-status').value,order_date:document.getElementById('o-date').value,delivery_date:document.getElementById('o-delivery').value,notes:document.getElementById('o-notes').value,items:items,tax_rate:10,create_debt:true})});
  closeModal();toast('Đã tạo đơn hàng');loadOrders()
}
async function viewOrder(id){let o=await api('/orders/'+id);openModal('<div class="modal-overlay"><div class="modal modal-lg"><div class="modal-header"><h2 class="dialog-title">'+(o.order_name||o.order_number)+'</h2><button class="btn btn-outline btn-sm" onclick="closeModal()">✕</button></div>'+
'<div class="modal-body"><div class="card-form mb-4"><div class="form-grid">'+
['Mã đơn:'+(o.order_number||'—'),'Khách hàng:'+(o.customer_name||'—'),'SĐT:'+(o.customer_phone||'—'),'Ngày đặt:'+date(o.created_at),'Ngày xuất:'+date(o.delivery_date),'Trạng thái:'+({pending:'Chờ XLL',processing:'Đang XL',delivered:'Đã giao',cancelled:'Đã hủy'}[o.status]||'—'),'Thanh toán:'+({paid:'Đã TT',partial:'Một phần',unpaid:'Chưa TT'}[o.payment_status]||'—'),'Tổng:'+fmt(o.grand_total)]
.map(x=>'<div><span style="color:#94a3b8;font-size:10px;font-weight:600;text-transform:uppercase">'+x.split(':')[0]+'</span><div style="font-weight:600">'+x.split(':').slice(1).join(':')+'</div></div>').join('')+'</div></div>'+
'<table class="data-table"><thead><tr><th>Mô tả</th><th>Mã</th><th>Xuất xứ</th><th>ĐV</th><th>SL</th><th>Đơn giá</th><th>Thành tiền</th></tr></thead><tbody>'+
(o.items||[]).map(i=>'<tr><td>'+i.product_name+'</td><td>'+(i.variant_sku||'—')+'</td><td>'+(i.origin||'—')+'</td><td>'+(i.unit||'—')+'</td><td class="text-center">'+i.quantity+'</td><td class="text-right">'+fmt(i.price)+'</td><td class="text-right"><b>'+fmt(i.line_total)+'</b></td></tr>').join('')+'</tbody></table>'+
'<div class="modal-footer" style="border:none;padding:16px 0 0"><button class="btn btn-outline" onclick="closeModal()">Đóng</button></div></div></div></div>')
}
</script>"""

DEBTS = """
<div class="flex items-center justify-between mb-4">
  <div><h1 class="page-title">Quản lý Công Nợ</h1><p class="page-subtitle">Theo dõi công nợ đơn hàng và lịch sử thanh toán</p></div>
  <div class="flex gap-2">
    <button class="btn btn-outline" onclick="showAddPayment()">Ghi nhận TT</button>
  </div>
</div>
<div class="stat-grid mb-4" id="debt-stats"></div>
<div class="filter-bar flex items-center gap-3">
  <input placeholder="Tìm mã đơn, tên KH..." id="debt-search" onkeyup="loadDebts()" class="flex-1">
  <select id="debt-status" onchange="loadDebts()" style="width:200px">
    <option value="">Tất cả trạng thái</option>
    <option value="pending">Chờ thanh toán</option>
    <option value="partial">Thanh toán một phần</option>
    <option value="paid">Đã thanh toán</option>
  </select>
</div>
<div style="overflow-x:auto"><table class="data-table"><thead><tr>
  <th>Mã đơn hàng</th><th>Khách hàng</th><th>Số tiền gốc</th><th>Đã thanh toán</th><th>Còn lại</th><th>Trạng thái</th><th>Ngày tạo</th><th></th>
</tr></thead><tbody id="debt-body"></tbody></table></div>
<script>
async function loadDebts(){
  let s=document.getElementById('debt-search').value,st=document.getElementById('debt-status').value;
  let d=await api('/debts?search='+s+'&status='+st);
  document.getElementById('debt-stats').innerHTML=
    '<div class="stat-card"><div class="stat-title">Tổng nợ gốc</div><div class="stat-value">'+fmt(d.stats.total_original)+'</div></div>'+
    '<div class="stat-card stat-card-success"><div class="stat-title">Đã thu</div><div class="stat-value" style="color:#059669">'+fmt(d.stats.total_paid)+'</div></div>'+
    '<div class="stat-card stat-card-danger"><div class="stat-title">Còn phải thu</div><div class="stat-value" style="color:#dc2626">'+fmt(d.stats.total_remaining)+'</div></div>'+
    '<div class="stat-card"><div class="stat-title">Quá hạn</div><div class="stat-value">'+d.stats.count_overdue+' đơn</div></div>';
  let rows=d.data.map(d=>'<tr>'+
    '<td><b>'+(d.order_name||d.order_number||'—')+'</b></td><td>'+(d.customer_name||'—')+'</td>'+
    '<td class="text-right">'+fmt(d.original_amount)+'</td><td class="text-right" style="color:#059669">'+fmt(d.paid_amount)+'</td>'+
    '<td class="text-right" style="color:'+(d.remaining_amount>0?'#dc2626':'#6b7280')+'"><b>'+fmt(d.remaining_amount)+'</b></td>'+
    '<td><span class="badge '+(d.status=='paid'?'badge-success':d.status=='partial'?'badge-info':'badge-warning')+'">'+
    ({pending:'Chờ TT',partial:'Một phần',paid:'Đã TT'}[d.status]||d.status)+'</span></td>'+
    '<td>'+date(d.created_at)+'</td><td><button class="btn btn-outline btn-xs" onclick="showPayDebt('+d.id+','+d.remaining_amount+')">Thanh toán</button></td></tr>').join('');
  document.getElementById('debt-body').innerHTML=rows||'<tr class="empty-row"><td colspan="8">Không có công nợ nào</td></tr>';
}
function showPayDebt(id,remaining){
  openModal('<div class="modal-overlay"><div class="modal"><div class="modal-header"><h2 class="dialog-title">Ghi nhận thanh toán</h2><button class="btn btn-outline btn-sm" onclick="closeModal()">✕</button></div>'+
  '<div class="modal-body"><div class="form-grid">'+
  '<div class="form-row"><label class="form-label">Số tiền * (Còn: '+fmt(remaining)+')</label><input type="number" id="pay-amount" value="'+remaining+'" min="1"></div>'+
  '<div class="form-row"><label class="form-label">Phương thức</label><input id="pay-method" placeholder="Tiền mặt / CK"></div>'+
  '<div class="form-row"><label class="form-label">Ngày thanh toán</label><input type="date" id="pay-date" value="'+new Date().toISOString().slice(0,10)+'"></div>'+
  '<div class="form-row"><label class="form-label">Ghi chú</label><textarea id="pay-notes" rows="2"></textarea></div>'+
  '</div></div><div class="modal-footer"><button class="btn btn-outline" onclick="closeModal()">Hủy</button>'+
  '<button class="btn btn-primary" onclick="savePayment('+id+')">Lưu thanh toán</button></div></div></div>')
}
async function savePayment(id){
  let d={amount:parseFloat(document.getElementById('pay-amount').value)||0,payment_method:document.getElementById('pay-method').value,paid_at:document.getElementById('pay-date').value,notes:document.getElementById('pay-notes').value};
  if(!d.amount)return toast('Số tiền phải > 0','error');
  await api('/debts/'+id+'/payments',{method:'POST',body:JSON.stringify(d)});
  closeModal();toast('Đã ghi nhận thanh toán');loadDebts()
}
function showAddPayment(){let sel=document.querySelector('#debt-body tr:hover');if(!sel)return toast('Chọn 1 dòng công nợ trước','error')}
loadDebts()
</script>"""

ADVANCES = """
<div class="flex items-center justify-between mb-4">
  <div><h1 class="page-title">Tạm ứng</h1><p class="page-subtitle">Quản lý các khoản tạm ứng</p></div>
  <button class="btn btn-primary" onclick="showAddAdvance()">+  Tạo tạm ứng</button>
</div>
<div class="filter-bar flex items-center gap-3">
  <input placeholder="Tìm số tạm ứng, mục đích..." id="adv-search" onkeyup="loadAdvances()" class="flex-1">
  <select id="adv-type" onchange="loadAdvances()" style="width:150px">
    <option value="">Tất cả</option><option value="employee">Nhân viên</option><option value="customer">Khách hàng</option><option value="supplier">Nhà cung cấp</option>
  </select>
  <select id="adv-status" onchange="loadAdvances()" style="width:160px">
    <option value="">Tất cả trạng thái</option><option value="pending">Chờ duyệt</option><option value="approved">Đã duyệt</option><option value="settled">Đã quyết toán</option><option value="cancelled">Đã hủy</option>
  </select>
</div>
<div style="overflow-x:auto"><table class="data-table"><thead><tr>
  <th>Số tạm ứng</th><th>Loại</th><th>Mục đích</th><th>Ngày</th><th>Số tiền</th><th>Đã hoàn</th><th>Còn lại</th><th>Trạng thái</th>
</tr></thead><tbody id="adv-body"></tbody></table></div>
<script>
async function loadAdvances(){
  let s=document.getElementById('adv-search').value,t=document.getElementById('adv-type').value,st=document.getElementById('adv-status').value;
  let d=await api('/advances?search='+s+'&type='+t+'&status='+st);
  let typeLabels={employee:'Nhân viên',customer:'Khách hàng',supplier:'Nhà CC'};
  let statusLabels={pending:['Chờ duyệt','warning'],approved:['Đã duyệt','info'],settled:['Đã quyết toán','success'],cancelled:['Đã hủy','danger']};
  let rows=d.data.map(a=>{let sl=statusLabels[a.status]||[a.status,'neutral'];_=a.amount||0;r=a.returned_amount||0;return'<tr>'+
    '<td>'+a.advance_number+'</td><td>'+typeLabels[a.type]+'</td><td>'+(a.purpose||'—')+'</td><td>'+date(a.advance_date)+'</td>'+
    '<td class="text-right">'+fmt(a.amount)+'</td><td class="text-right">'+fmt(a.returned_amount)+'</td><td class="text-right">'+fmt(Math.max(0,_-r))+'</td>'+
    '<td><span class="badge badge-'+sl[1]+'">'+sl[0]+'</span></td></tr>'}).join('');
  document.getElementById('adv-body').innerHTML=rows||'<tr class="empty-row"><td colspan="8">Chưa có tạm ứng nào</td></tr>';
}
function showAddAdvance(){
  openModal('<div class="modal-overlay"><div class="modal"><div class="modal-header"><h2 class="dialog-title">Tạo tạm ứng</h2><button class="btn btn-outline btn-sm" onclick="closeModal()">✕</button></div>'+
  '<div class="modal-body"><div class="form-grid">'+
  '<div class="form-row"><label class="form-label">Loại *</label><select id="a-type"><option value="employee">Nhân viên</option><option value="customer">Khách hàng</option><option value="supplier">Nhà cung cấp</option></select></div>'+
  '<div class="form-row"><label class="form-label">Người nhận</label><input id="a-person"></div>'+
  '<div class="form-row"><label class="form-label">Ngày tạm ứng *</label><input type="date" id="a-date" value="'+new Date().toISOString().slice(0,10)+'"></div>'+
  '<div class="form-row"><label class="form-label">Ngày hoàn dự kiến</label><input type="date" id="a-expected" value="'+new Date().toISOString().slice(0,10)+'"></div>'+
  '<div class="form-row"><label class="form-label">Số tiền *</label><input type="number" id="a-amount" value="0" min="0"></div>'+
  '<div class="form-row"><label class="form-label">Trạng thái</label><select id="a-status"><option value="pending">Chờ duyệt</option><option value="approved">Đã duyệt</option><option value="settled">Đã quyết toán</option><option value="cancelled">Đã hủy</option></select></div>'+
  '<div class="form-row"><label class="form-label">Mục đích</label><input id="a-purpose"></div>'+
  '<div class="form-row" style="grid-column:span 2"><label class="form-label">Ghi chú</label><textarea id="a-notes" rows="2"></textarea></div>'+
  '</div></div><div class="modal-footer"><button class="btn btn-outline" onclick="closeModal()">Hủy</button><button class="btn btn-primary" onclick="saveAdvance()">Tạo tạm ứng</button></div></div></div>')
}
async function saveAdvance(){
  let d={type:document.getElementById('a-type').value,employee_name:document.getElementById('a-type').value=='employee'?document.getElementById('a-person').value:null,supplier_name:document.getElementById('a-type').value=='supplier'?document.getElementById('a-person').value:null,advance_date:document.getElementById('a-date').value,expected_return_date:document.getElementById('a-expected').value,amount:parseFloat(document.getElementById('a-amount').value)||0,status:document.getElementById('a-status').value,purpose:document.getElementById('a-purpose').value,notes:document.getElementById('a-notes').value};
  if(!d.amount)return toast('Số tiền phải > 0','error');
  await api('/advances',{method:'POST',body:JSON.stringify(d)});
  closeModal();toast('Đã tạo tạm ứng');loadAdvances()
}
loadAdvances()
</script>"""


# ── FLASK APP ──

def create_web_app(db):
    app = Flask(__name__)
    customer_svc = CustomerService(db)
    order_svc = OrderService(db)
    debt_svc = DebtService(db)
    advance_svc = AdvanceService(db)

    def render_page(page, content):
        nav = [('dashboard','📊','Dashboard'),('customers','👥','Khách hàng'),('orders','📦','Đơn hàng'),('debts','💰','Công nợ'),('advances','💵','Tạm ứng')]
        return render_template_string(HTML, css=CSS, nav_items=nav, page=page, content=content, now=datetime.now())

    # ── Pages ──
    @app.route('/')
    @app.route('/dashboard')
    def index(): return render_page('dashboard', DASHBOARD)

    @app.route('/customers')
    def customers(): return render_page('customers', CUSTOMERS)

    @app.route('/orders')
    def orders(): return render_page('orders', ORDERS)

    @app.route('/debts')
    def debts(): return render_page('debts', DEBTS)

    @app.route('/advances')
    def advances(): return render_page('advances', ADVANCES)

    # ── API ──
    @app.route('/api/dashboard')
    def api_dashboard():
        os_ = order_svc.get_stats(); ds_ = debt_svc.get_stats(); cs_ = customer_svc.get_stats()
        return jsonify({'allTimeStats':{'total_orders':os_.get('total_orders',0),'total_revenue':os_.get('total_revenue',0),'total_customers':cs_.get('total_customers',0),
            'total_debt_amount':ds_.get('total_remaining',0),'total_debt_count':ds_.get('count_pending',0)+ds_.get('count_partial',0)},
            'periodStats':{'revenue':os_.get('total_revenue',0),'orders':os_.get('total_orders',0),'new_customers':cs_.get('total_customers',0),
            'avg_order_value':os_.get('total_revenue',0)/max(os_.get('total_orders',0),1)}})

    @app.route('/api/customers')
    def api_customers():
        search = request.args.get('search',''); sort = request.args.get('sort','created_at')
        data = customer_svc.get_all(search=search)
        if sort == 'name': data.sort(key=lambda x: (x.get('name') or '').lower())
        elif sort == 'orders_count': data.sort(key=lambda x: x.get('orders_count') or 0, reverse=True)
        else: data.sort(key=lambda x: x.get('created_at') or '', reverse=True)
        return jsonify({'data': data, 'total': len(data)})

    @app.route('/api/customers/<int:cid>')
    def api_customer(cid):
        c = customer_svc.get_by_id(cid)
        if not c: return jsonify({'error': 'Not found'}), 404
        try:
            c['orders'] = db.fetch_all("SELECT * FROM orders WHERE customer_id=? ORDER BY created_at DESC", (cid,))
            c['orders_count'] = len(c['orders'])
            c['debts'] = db.fetch_all("SELECT d.*, o.order_number FROM debts d LEFT JOIN orders o ON o.id=d.order_id WHERE d.customer_id=? ORDER BY d.created_at DESC", (cid,))
            c['total_paid'] = sum(float(d.get('paid_amount') or 0) for d in c['debts'])
            c['total_debt'] = sum(float(d.get('original_amount') or 0) for d in c['debts'])
            c['remaining_debt'] = sum(float(d.get('remaining_amount') or 0) for d in c['debts'])
        except: pass
        return jsonify(c)

    @app.route('/api/customers', methods=['POST'])
    def api_create_customer():
        cid = customer_svc.create(request.json)
        return jsonify(customer_svc.get_by_id(cid)), 201

    @app.route('/api/orders')
    def api_orders():
        search = request.args.get('search',''); frm = request.args.get('from',''); to = request.args.get('to','')
        data = order_svc.get_all(search=search, from_date=frm, to_date=to)
        return jsonify({'data': data, 'stats': order_svc.get_stats(), 'total': len(data)})

    @app.route('/api/orders/<int:oid>')
    def api_order(oid):
        o = order_svc.get_by_id(oid)
        return jsonify(o) if o else (jsonify({'error': 'Not found'}), 404)

    @app.route('/api/orders', methods=['POST'])
    def api_create_order():
        data = request.json; items = data.pop('items', [])
        oid = order_svc.create(data, items)
        return jsonify(order_svc.get_by_id(oid)), 201

    @app.route('/api/debts')
    def api_debts():
        search = request.args.get('search',''); status = request.args.get('status','')
        data = debt_svc.get_all(search=search, status=status)
        return jsonify({'data': data, 'stats': debt_svc.get_stats(), 'total': len(data)})

    @app.route('/api/debts/<int:did>/payments', methods=['POST'])
    def api_debt_payment(did):
        try:
            debt_svc.add_payment(did, request.json)
            return jsonify(debt_svc.get_by_id(did)), 201
        except ValueError as e: return jsonify({'error': str(e)}), 400

    @app.route('/api/advances')
    def api_advances():
        search = request.args.get('search',''); t = request.args.get('type',''); st = request.args.get('status','')
        data = advance_svc.get_all(search=search, type_filter=t, status=st)
        return jsonify({'data': data, 'total': len(data)})

    @app.route('/api/advances', methods=['POST'])
    def api_create_advance():
        aid = advance_svc.create(request.json)
        return jsonify({'id': aid}), 201

    @app.route('/api/import-excel', methods=['POST'])
    def api_import_excel():
        if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
        f = request.files['file']; path = os.path.join('uploads', f.filename)
        os.makedirs('uploads', exist_ok=True); f.save(path)
        try: return jsonify(ExcelService().import_orders_from_excel(path))
        except Exception as e: return jsonify({'error': str(e)}), 500

    return app


def main():
    from src.database import Database
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'b2b_management.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db = Database(db_path); db.initialize()
    print('✅ Database ready | 🌐 http://localhost:5100')
    app = create_web_app(db)
    app.run(host='0.0.0.0', port=5100, debug=True)


if __name__ == '__main__':
    main()

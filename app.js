const STORAGE_KEY = "stockPanelProducts";
const LOG_KEY = "stockPanelLogs";

const productForm = document.getElementById("productForm");
const movementForm = document.getElementById("movementForm");
const bulkAddBtn = document.getElementById("bulkAddBtn");
const csvInput = document.getElementById("csvInput");
const productTable = document.getElementById("productTable");
const logsUl = document.getElementById("logs");
const thresholdInput = document.getElementById("threshold");

let products = load(STORAGE_KEY, []);
let logs = load(LOG_KEY, []);

function load(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) ?? fallback;
  } catch {
    return fallback;
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(products));
  localStorage.setItem(LOG_KEY, JSON.stringify(logs));
}

function addLog(text) {
  logs.unshift(`${new Date().toLocaleString("tr-TR")}: ${text}`);
  logs = logs.slice(0, 50);
  saveState();
  renderLogs();
}

function getStatus(stock, threshold) {
  if (stock <= 0) return { label: "Stok Yok", cls: "out" };
  if (stock <= threshold) return { label: "Kritik", cls: "low" };
  return { label: "Yeterli", cls: "ok" };
}

function upsertProduct({ sku, name, price, stock }) {
  const index = products.findIndex((p) => p.sku === sku);
  if (index >= 0) {
    products[index].name = name || products[index].name;
    products[index].price = Number(price);
    products[index].stock += Number(stock);
    addLog(`${sku} güncellendi (+${stock} stok).`);
  } else {
    products.push({ sku, name, price: Number(price), stock: Number(stock) });
    addLog(`${sku} eklendi (${stock} adet).`);
  }
}

function renderProducts() {
  const threshold = Number(thresholdInput.value || 0);
  productTable.innerHTML = "";

  products
    .sort((a, b) => a.sku.localeCompare(b.sku, "tr"))
    .forEach((p) => {
      const status = getStatus(p.stock, threshold);
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${p.sku}</td>
        <td>${p.name}</td>
        <td>₺${p.price.toFixed(2)}</td>
        <td>${p.stock}</td>
        <td><span class="badge ${status.cls}">${status.label}</span></td>
      `;
      productTable.appendChild(tr);
    });

  saveState();
}

function renderLogs() {
  logsUl.innerHTML = "";
  logs.forEach((log) => {
    const li = document.createElement("li");
    li.textContent = log;
    logsUl.appendChild(li);
  });
}

productForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const data = new FormData(productForm);
  upsertProduct({
    sku: String(data.get("sku")).trim(),
    name: String(data.get("name")).trim(),
    price: Number(data.get("price")),
    stock: Number(data.get("stock")),
  });
  productForm.reset();
  renderProducts();
});

movementForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const data = new FormData(movementForm);
  const sku = String(data.get("sku")).trim();
  const qty = Number(data.get("qty"));
  const type = String(data.get("type"));

  const product = products.find((p) => p.sku === sku);
  if (!product) {
    addLog(`Hata: ${sku} bulunamadı.`);
    renderLogs();
    return;
  }

  if (type === "in") {
    product.stock += qty;
    addLog(`${sku} için stok girişi: +${qty}.`);
  } else {
    product.stock = Math.max(0, product.stock - qty);
    addLog(`${sku} için stok çıkışı: -${qty}.`);
  }

  movementForm.reset();
  renderProducts();
});

bulkAddBtn.addEventListener("click", () => {
  const lines = csvInput.value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  if (!lines.length) {
    addLog("CSV boş, işlem yapılmadı.");
    return;
  }

  let ok = 0;
  for (const line of lines) {
    const [sku, name, price, stock] = line.split(",").map((i) => i?.trim());
    if (!sku || !name || Number.isNaN(Number(price)) || Number.isNaN(Number(stock))) {
      addLog(`CSV satırı atlandı: ${line}`);
      continue;
    }
    upsertProduct({ sku, name, price: Number(price), stock: Number(stock) });
    ok++;
  }

  addLog(`Toplu içe aktarma tamamlandı. Başarılı satır: ${ok}.`);
  csvInput.value = "";
  renderProducts();
});

thresholdInput.addEventListener("input", renderProducts);

renderProducts();
renderLogs();

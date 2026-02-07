const tg = window.Telegram.WebApp;

tg.expand();
tg.MainButton.textColor = '#FFFFFF';
tg.MainButton.color = '#4e73f9';

// Данные
const products = [
    { id: 1, title: 'Вазочка"', price: 400.00, oldPrice: 1350.00, img: 'static/images/1.png', type: 'circle' },
    { id: 2, title: 'Ваночка', price: 350.00, oldPrice: 1150.00, img: 'static/images/2.png', type: 'circle' },
    { id: 3, title: 'Набор из декора"', price: 5000.00, oldPrice: 10000.00, img: 'static/images/3.png', type: 'rounded' },
    { id: 4, title: 'Арома свеча"', price: 900.00, oldPrice: 1500, img: 'static/images/4.png', type: 'circle' },
    { id: 5, title: 'Шкатулка', price: 370.00, oldPrice: 790.00, img: 'static/images/5.png', type: 'rounded' }
];

let cart = {};
let currentView = 'shop'; // 'shop' | 'cart' | 'checkout'

// --- РЕНДЕР ---
function renderProducts() {
    const list = document.getElementById('product-list');
    list.innerHTML = '';
    products.forEach(p => {
        const count = cart[p.id] || 0;
        const card = document.createElement('div');
        card.className = 'card';
        let buttonHTML = count === 0
            ? `<button class="action-btn btn-add" onclick="updateCart(${p.id}, 1)">В корзину</button>`
            : `<div class="action-btn counter-control">
                   <button class="counter-btn" onclick="updateCart(${p.id}, -1)">−</button>
                   <span class="counter-val">${count}</span>
                   <button class="counter-btn" onclick="updateCart(${p.id}, 1)">+</button>
               </div>`;
        card.innerHTML = `
            <img src="${p.img}" class="card-img ${p.type === 'rounded' ? 'rounded' : ''}">
            <div class="card-title">${p.title}</div>
            <div class="price-container">
                ${p.oldPrice ? `<span class="old-price">${p.oldPrice} руб.</span>` : ''}
                <span class="new-price">${p.price.toFixed(2)} руб.</span>
            </div>
            ${buttonHTML}
        `;
        list.appendChild(card);
    });
}

function renderCartView() {
    const list = document.getElementById('cart-items');
    list.innerHTML = '';
    let total = 0;
    for (const [id, count] of Object.entries(cart)) {
        if (count > 0) {
            const p = products.find(prod => prod.id == id);
            total += p.price * count;
            const item = document.createElement('div');
            item.style.cssText = 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; background: var(--card-bg); padding: 10px; border-radius: 12px;';
            item.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px;">
                    <img src="${p.img}" style="width: 40px; height: 40px; border-radius: 8px;">
                    <div><div style="font-weight: bold;">${p.title}</div><div style="font-size: 11px; color: #8b8b90;">${count} x ${p.price}</div></div>
                </div>
                <div style="font-weight: bold;">${(p.price * count).toFixed(0)}</div>
            `;
            list.appendChild(item);
        }
    }
    document.getElementById('cart-total-display').innerText = total.toFixed(2) + ' руб.';
}

// --- УПРАВЛЕНИЕ КОРЗИНОЙ ---
window.updateCart = function(id, change) {
    if (tg.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
    if (!cart[id]) cart[id] = 0;
    cart[id] += change;
    if (cart[id] <= 0) delete cart[id];

    if (currentView === 'shop') renderProducts();
    else if (currentView === 'cart') renderCartView();
    updateMainButton();
};

function calculateTotal() {
    let total = 0;
    for (const [id, count] of Object.entries(cart)) {
        total += products.find(p => p.id == id).price * count;
    }
    return total;
}

function updateMainButton() {
    const total = calculateTotal();
    if (total > 0) {
        tg.MainButton.show();
        if (currentView === 'shop') tg.MainButton.setText(`Корзина (${total.toFixed(0)})`);
        else if (currentView === 'cart') tg.MainButton.setText(`Оформить за ${total.toFixed(0)} руб.`);
        else if (currentView === 'checkout') tg.MainButton.setText(`Подтвердить заказ`);
    } else {
        tg.MainButton.hide();
        if (currentView !== 'shop') switchView('shop');
    }
}

// --- НАВИГАЦИЯ ---
function switchView(view) {
    currentView = view;
    document.getElementById('shop-view').style.display = 'none';
    document.getElementById('cart-view').style.display = 'none';
    document.getElementById('checkout-view').style.display = 'none';

    if (view === 'shop') {
        document.getElementById('shop-view').style.display = 'grid';
        tg.BackButton.hide();
        renderProducts();
    } else if (view === 'cart') {
        document.getElementById('cart-view').style.display = 'block';
        tg.BackButton.show();
        renderCartView();
    } else if (view === 'checkout') {
        document.getElementById('checkout-view').style.display = 'block';
        tg.BackButton.show();
    }
    updateMainButton();
}

tg.BackButton.onClick(() => {
    if (currentView === 'checkout') switchView('cart');
    else switchView('shop');
});

// --- ОТПРАВКА ЗАКАЗА ---
tg.MainButton.onClick(async () => {
    if (currentView === 'shop') {
        switchView('cart');
    } else if (currentView === 'cart') {
        switchView('checkout');
    } else if (currentView === 'checkout') {
        // 1. Валидация
        const name = document.getElementById('order-name').value;
        const phone = document.getElementById('order-phone').value;
        const comment = document.getElementById('order-comment').value;

        if (!name || !phone) {
            tg.showAlert("Пожалуйста, введите имя и телефон!");
            return;
        }

        // 2. Подготовка данных
        const cartItems = [];
        for (const [id, count] of Object.entries(cart)) {
            const p = products.find(prod => prod.id == id);
            cartItems.push({ title: p.title, price: p.price, count: count });
        }

        // 3. Отправка на сервер
        tg.MainButton.showProgress();

        try {
            const response = await fetch('/api/create-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Telegram-Init-Data': tg.initData // ВАЖНО для безопасности
                },
                body: JSON.stringify({
                    form: { name, phone, comment },
                    cart: cartItems,
                    total_price: calculateTotal()
                })
            });

            if (response.ok) {
                tg.MainButton.hideProgress();
                tg.close(); // Закрываем магазин после успеха
            } else {
                tg.MainButton.hideProgress();
                tg.showAlert("Ошибка сервера. Попробуйте позже.");
            }
        } catch (e) {
            tg.MainButton.hideProgress();
            tg.showAlert("Ошибка сети!");
        }
    }
});

// Start
renderProducts();
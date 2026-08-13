let cart = JSON.parse(localStorage.getItem('cart')) || [];

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function parsePrice(priceStr) {
    if(!priceStr) return 0;
    return parseFloat(priceStr.replace(/[^0-9.]/g, '')) || 0;
}

function generateId(title) {
    return title.toLowerCase().replace(/[^a-z0-9]/g, '-');
}

function addToCart(title, priceStr, imageSrc) {
    const id = generateId(title);
    const existingItem = cart.find(item => item.id === id);
    const price = parsePrice(priceStr);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: id,
            title: title,
            price: price,
            image: imageSrc,
            quantity: 1
        });
    }
    
    saveCart();
    renderCart();
    if(typeof openCart === 'function') openCart();
}

function updateQuantity(id, change) {
    const item = cart.find(item => item.id === id);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(id);
        } else {
            saveCart();
            renderCart();
        }
    }
}

function removeFromCart(id) {
    cart = cart.filter(item => item.id !== id);
    saveCart();
    renderCart();
}

function clearCart() {
    cart = [];
    saveCart();
    renderCart();
}

function renderCart() {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    
    const cartHeaderCount = document.getElementById('cart-header-count');
    if (cartHeaderCount) {
        cartHeaderCount.textContent = `(${totalItems})`;
    }

    const container = document.getElementById('cart-items-container');
    if (container) {
        container.innerHTML = '';
        if (cart.length === 0) {
            container.innerHTML = '<div class="text-center text-gray-500 mt-10">Your cart is empty.</div>';
        } else {
            cart.forEach(item => {
                const itemEl = document.createElement('div');
                itemEl.className = 'flex items-start gap-4 group relative mb-4';
                itemEl.innerHTML = `
                    <div class="w-20 h-20 bg-gray-100 rounded-xl overflow-hidden shrink-0 flex items-center justify-center p-2">
                        <img src="${item.image}" alt="${item.title}" class="w-full h-full object-contain mix-blend-multiply">
                    </div>
                    <div class="flex-1 pt-0.5">
                        <h3 class="text-[15px] font-medium text-[var(--primary-bg)] pr-6 leading-tight">${item.title}</h3>
                        <p class="text-[15px] font-bold text-[var(--primary-bg)] mt-1">$${item.price.toFixed(2)}</p>
                        <div class="flex items-center gap-4 mt-3">
                            <div class="flex items-center gap-4 bg-white border border-gray-200 rounded-xl px-2.5 py-1">
                                <button onclick="updateQuantity('${item.id}', -1)" class="text-gray-400 hover:text-[var(--primary-bg)] transition-colors"><i class="fa-solid fa-minus text-[10px]"></i></button>
                                <span class="text-[13px] font-bold text-[var(--primary-bg)] w-3 text-center">${item.quantity}</span>
                                <button onclick="updateQuantity('${item.id}', 1)" class="text-gray-400 hover:text-[var(--primary-bg)] transition-colors"><i class="fa-solid fa-plus text-[10px]"></i></button>
                            </div>
                        </div>
                    </div>
                    <button onclick="removeFromCart('${item.id}')" class="absolute top-0 right-0 text-[var(--primary-bg)]/50 hover:text-red-500 transition-colors">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                `;
                container.appendChild(itemEl);
            });
        }
    }

    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const subtotalEl = document.getElementById('cart-subtotal');
    if (subtotalEl) {
        subtotalEl.textContent = `$${subtotal.toFixed(2)}`;
    }

    const milestone1 = document.getElementById('milestone-1'); 
    const milestone2 = document.getElementById('milestone-2'); 
    
    if (milestone1) {
        const remaining = Math.max(0, 200 - subtotal);
        if (remaining === 0) {
            milestone1.querySelector('p:last-child').textContent = 'UNLOCKED';
            milestone1.classList.remove('bg-white/50');
            milestone1.classList.add('bg-[#f8c630]');
            const progress = milestone1.querySelector('.absolute');
            if(progress) progress.style.width = '100%';
        } else {
            milestone1.querySelector('p:last-child').textContent = `$${remaining.toFixed(2)} AWAY`;
            milestone1.classList.add('bg-white/50');
            milestone1.classList.remove('bg-[#f8c630]');
            const progress = milestone1.querySelector('.absolute');
            if(progress) progress.style.width = `${Math.min(100, (subtotal/200)*100)}%`;
        }
    }
    
    if (milestone2) {
        const remaining = Math.max(0, 150 - subtotal);
        if (remaining === 0) {
            milestone2.querySelector('p:last-child').textContent = 'UNLOCKED';
            milestone2.classList.remove('bg-white/50');
            milestone2.classList.add('bg-[#f8c630]');
            const progress = milestone2.querySelector('.absolute');
            if(progress) progress.style.width = '100%';
        } else {
            milestone2.querySelector('p:last-child').textContent = `$${remaining.toFixed(2)} AWAY`;
            milestone2.classList.add('bg-white/50');
            milestone2.classList.remove('bg-[#f8c630]');
            const progress = milestone2.querySelector('.absolute');
            if(progress) progress.style.width = `${Math.min(100, (subtotal/150)*100)}%`;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    renderCart();
    
    const emptyBasketLink = document.getElementById('empty-basket-btn');
    if (emptyBasketLink) {
        emptyBasketLink.addEventListener('click', (e) => {
            e.preventDefault();
            clearCart();
        });
    }
});

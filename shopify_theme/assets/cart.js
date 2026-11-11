// Shopify AJAX Cart Integration
let cartData = {};

async function fetchCart() {
    try {
        const response = await fetch('/cart.js');
        cartData = await response.json();
        renderCart();
    } catch (error) {
        console.error('Error fetching cart', error);
    }
}

function renderCart() {
    const container = document.getElementById('cart-items-container');
    const subtotalEl = document.getElementById('cart-subtotal');
    const countEl = document.getElementById('cart-header-count');
    
    if (!container) return;
    
    container.innerHTML = '';
    
    if (cartData.item_count === 0) {
        container.innerHTML = '<p class=\"text-center mt-10\">Your cart is empty.</p>';
        if (subtotalEl) subtotalEl.textContent = '$0.00';
        if (countEl) countEl.textContent = '(0)';
        return;
    }
    
    if (countEl) countEl.textContent = `(${cartData.item_count})`;
    if (subtotalEl) subtotalEl.textContent = `$${(cartData.total_price / 100).toFixed(2)}`;
    
    cartData.items.forEach(item => {
        const itemHtml = `
        <div class=\"flex gap-4 border border-[var(--primary-bg)]/20 p-4 rounded-2xl bg-white relative group\">
            <div class=\"w-24 h-24 bg-gray-50 rounded-xl flex-shrink-0 flex items-center justify-center p-2\">
                <img src=\"${item.image}\" alt=\"${item.product_title}\" class=\"w-full h-full object-contain mix-blend-multiply\">
            </div>
            <div class=\"flex-1 flex flex-col justify-between py-1\">
                <div class=\"flex justify-between items-start\">
                    <div>
                        <h3 class=\"font-bold text-[var(--primary-bg)] text-[15px] leading-tight\">${item.product_title}</h3>
                        ${item.variant_title ? `<p class=\"text-xs text-[var(--secondary-bg)] mt-1\">${item.variant_title}</p>` : ''}
                    </div>
                    <button onclick=\"changeItemQuantity('${item.key}', 0)\" class=\"text-gray-300 hover:text-red-500 transition-colors p-1\">
                        <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><line x1=\"18\" y1=\"6\" x2=\"6\" y2=\"18\"></line><line x1=\"6\" y1=\"6\" x2=\"18\" y2=\"18\"></line></svg>
                    </button>
                </div>
                <div class=\"flex justify-between items-end\">
                    <div class=\"flex items-center gap-3 border border-[var(--primary-bg)]/20 rounded-full px-2 py-1\">
                        <button onclick=\"changeItemQuantity('${item.key}', ${item.quantity - 1})\" class=\"w-6 h-6 flex items-center justify-center hover:bg-[var(--primary-bg)]/5 rounded-full transition\"><svg width=\"12\" height=\"12\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><line x1=\"5\" y1=\"12\" x2=\"19\" y2=\"12\"></line></svg></button>
                        <span class=\"text-sm font-bold w-4 text-center\">${item.quantity}</span>
                        <button onclick=\"changeItemQuantity('${item.key}', ${item.quantity + 1})\" class=\"w-6 h-6 flex items-center justify-center hover:bg-[var(--primary-bg)]/5 rounded-full transition\"><svg width=\"12\" height=\"12\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><line x1=\"12\" y1=\"5\" x2=\"12\" y2=\"19\"></line><line x1=\"5\" y1=\"12\" x2=\"19\" y2=\"12\"></line></svg></button>
                    </div>
                    <span class=\"font-bold text-[var(--primary-bg)]\">$${(item.final_line_price / 100).toFixed(2)}</span>
                </div>
            </div>
        </div>`;
        container.innerHTML += itemHtml;
    });
}

async function changeItemQuantity(key, quantity) {
    try {
        await fetch('/cart/change.js', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: key,
                quantity: quantity
            })
        });
        fetchCart();
    } catch (error) {
        console.error('Error changing quantity', error);
    }
}

// Intercept form submissions for Add To Cart
document.addEventListener('submit', async function(e) {
    if (e.target.action && e.target.action.includes('/cart/add')) {
        e.preventDefault();
        const formData = new FormData(e.target);
        try {
            await fetch('/cart/add.js', {
                method: 'POST',
                body: formData
            });
            fetchCart();
            if (typeof openCart === 'function') openCart();
        } catch (error) {
            console.error('Error adding to cart', error);
        }
    }
});

document.addEventListener('DOMContentLoaded', fetchCart);

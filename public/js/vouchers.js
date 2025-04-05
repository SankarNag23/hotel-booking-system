document.addEventListener('DOMContentLoaded', () => {
    loadVouchers();

    // Refresh vouchers when the page is loaded
    document.getElementById('refreshVouchers')?.addEventListener('click', () => {
        loadVouchers(true);
    });
});

async function loadVouchers(forceRefresh = false) {
    try {
        const response = await fetch(`/api/vouchers${forceRefresh ? '?refresh=true' : ''}`);
        const vouchers = await response.json();
        displayVouchers(vouchers);
    } catch (error) {
        console.error('Error loading vouchers:', error);
        showError('Failed to load vouchers. Please try again later.');
    }
}

function displayVouchers(vouchers) {
    const container = document.getElementById('vouchersContainer');
    if (!container) return;

    container.innerHTML = '';

    vouchers.forEach(voucher => {
        const card = document.createElement('div');
        card.className = 'voucher-card';
        card.innerHTML = `
            <div class="voucher-image">
                <img src="${voucher.imageUrl}" alt="${voucher.destination}">
            </div>
            <div class="voucher-content">
                <h3>${voucher.destination}</h3>
                <p>${voucher.description}</p>
                <button class="voucher-reveal-btn" data-voucher-id="${voucher.id}">
                    ${voucher.isHidden ? 'Reveal Voucher Code' : voucher.code}
                </button>
            </div>
        `;

        const revealBtn = card.querySelector('.voucher-reveal-btn');
        if (revealBtn && voucher.isHidden) {
            revealBtn.addEventListener('click', () => revealVoucher(voucher.id, revealBtn));
        }

        container.appendChild(card);
    });
}

async function revealVoucher(voucherId, button) {
    try {
        // Check if user is authenticated
        const userId = getUserId(); // Implement this based on your auth system
        if (!userId) {
            showAuthenticationPrompt();
            return;
        }

        const response = await fetch(`/api/vouchers/${voucherId}/reveal`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ userId })
        });

        if (!response.ok) {
            const error = await response.json();
            if (response.status === 401) {
                showAuthenticationPrompt();
            } else {
                throw new Error(error.message);
            }
            return;
        }

        const { code } = await response.json();
        button.textContent = code;
        button.classList.add('revealed');
        button.disabled = true;
    } catch (error) {
        console.error('Error revealing voucher:', error);
        showError('Failed to reveal voucher. Please try again later.');
    }
}

function showAuthenticationPrompt() {
    // Implement your authentication UI here
    const modal = document.createElement('div');
    modal.className = 'auth-modal';
    modal.innerHTML = `
        <div class="auth-content">
            <h2>Authentication Required</h2>
            <p>Please register or log in to reveal the voucher code.</p>
            <div class="auth-buttons">
                <button onclick="location.href='/register'">Register</button>
                <button onclick="location.href='/login'">Login</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

function getUserId() {
    // Implement this based on your authentication system
    // For now, return null to trigger authentication flow
    return null;
} 
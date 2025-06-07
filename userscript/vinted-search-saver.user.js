// ==UserScript==
// @name         Vinted Search Saver
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Saves Vinted searches for https://github.com/Fuyucch1/Vinted-Notifications/
// @author       Quai
// @match        https://*.vinted.de/*
// @match        https://*.vinted.fr/*
// @match        https://*.vinted.be/*
// @match        https://*.vinted.nl/*
// @match        https://*.vinted.it/*
// @match        https://*.vinted.pl/*
// @match        https://*.vinted.cz/*
// @match        https://*.vinted.es/*
// @match        https://*.vinted.se/*
// @match        https://*.vinted.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    
    // ===== USER CONFIGURATION =====
    // Change these settings to match your server configuration
    // If you're running the server locally, leave the default settings
    // If you're running the server on another machine or custom port, update accordingly
    const SERVER_CONFIG = {
        host: 'localhost',  // Change to your server IP or hostname if not running locally
        port: 8000,        // Change if using a different port
        protocol: 'http'   // Change to 'https' if your server uses SSL
    };
    
    // Construct the base URL from configuration
    const SERVER_BASE_URL = `${SERVER_CONFIG.protocol}://${SERVER_CONFIG.host}:${SERVER_CONFIG.port}`;

    const style = document.createElement('style');
    style.textContent = `
        .search-saver-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #4CAF50;
            color: white;
            padding: 15px;
            border-radius: 4px;
            z-index: 10000;
            display: none;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        .floating-save-button {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background-color: #09B1BA;
            color: white;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s, background-color 0.2s;
            z-index: 10000;
        }

        .floating-save-button.disabled {
            background-color: #d9534f;
            cursor: not-allowed;
            opacity: 0.8;
        }

        .floating-save-button.disabled svg {
            opacity: 0.7;
            position: relative;
        }

        .floating-save-button.disabled svg::after {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            width: 100%;
            height: 2px;
            background-color: currentColor;
            transform: rotate(-45deg);
        }

        .floating-save-button:hover {
            transform: scale(1.1);
            background-color: #0A9DA5;
        }

        .floating-save-button.disabled:hover {
            background-color: #c9302c;
            transform: scale(1.1);
        }

        .save-modal {
            position: fixed;
            bottom: 100px;
            right: 30px;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: none;
            z-index: 10000;
            width: 300px;
        }

        .save-modal input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            margin-bottom: 10px;
        }

        .save-modal button {
            width: 100%;
            padding: 8px;
            border: none;
            border-radius: 4px;
            background-color: #09B1BA;
            color: white;
            cursor: pointer;
            font-weight: 600;
            transition: background-color 0.2s;
        }

        .save-modal button:hover {
            background-color: #0A9DA5;
        }
    `;
    document.head.appendChild(style);

    const notification = document.createElement('div');
    notification.className = 'search-saver-notification';
    document.body.appendChild(notification);

    function showNotification(message) {
        notification.textContent = message;
        notification.style.display = 'block';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }


    function isValidSearchUrl(url) {
        try {
            const urlObj = new URL(url);
            return urlObj.pathname.includes('/catalog') || urlObj.searchParams.has('search_text');
        } catch {
            return false;
        }
    }

    async function saveSearch(name) {
        const currentUrl = window.location.href;

        if (!isValidSearchUrl(currentUrl)) {
            showNotification('❌ This page is not a valid Vinted search query');
            return;
        }

        try {
            const response = await fetch(`${SERVER_BASE_URL}/add_query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `query=${encodeURIComponent(currentUrl)}&name=${encodeURIComponent(name)}`,
            });

            if (response.ok) {
                showNotification('✅ Search successfully saved!');
            } else {
                showNotification('❌ Error saving the search');
            }
        } catch (error) {
            showNotification(`❌ Connection error to backend (${SERVER_BASE_URL})`);
            console.error('Error:', error);
        }
    }

    function createSaveInterface() {

        const floatingButton = document.createElement('button');
        floatingButton.className = 'floating-save-button';

        if (!isValidSearchUrl(window.location.href)) {
            floatingButton.classList.add('disabled');
        }
        floatingButton.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path><line x1="2" y1="4" x2="22" y2="20" stroke-width="2" class="strike-through" style="display: none; stroke: currentColor; stroke-linecap: round;"/></svg>';

        const updateStrikeThrough = () => {
            const strikeLine = floatingButton.querySelector('.strike-through');
            strikeLine.style.display = floatingButton.classList.contains('disabled') ? 'block' : 'none';
        };

        updateStrikeThrough();

        const saveModal = document.createElement('div');
        saveModal.className = 'save-modal';

        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.placeholder = 'Search name';

        const saveButton = document.createElement('button');
        saveButton.textContent = 'Save';

        saveModal.appendChild(nameInput);
        saveModal.appendChild(saveButton);

        floatingButton.addEventListener('click', () => {
            const currentUrl = window.location.href;
            if (!isValidSearchUrl(currentUrl)) {
                showNotification('❌ This page is not a valid Vinted search query');
                return;
            }
            saveModal.style.display = saveModal.style.display === 'none' ? 'block' : 'none';
        });

        const observer = new MutationObserver(() => {
            if (!isValidSearchUrl(window.location.href)) {
                floatingButton.classList.add('disabled');
            } else {
                floatingButton.classList.remove('disabled');
            }
            updateStrikeThrough();
        });

        observer.observe(document.body, { childList: true, subtree: true });

        saveButton.addEventListener('click', () => {
            const name = nameInput.value.trim();
            if (!name) {
                showNotification('❌ Please enter a name for the search');
                return;
            }
            saveSearch(name);
            nameInput.value = '';
            saveModal.style.display = 'none';
        });

        document.addEventListener('click', (e) => {
            if (!saveModal.contains(e.target) && !floatingButton.contains(e.target)) {
                saveModal.style.display = 'none';
            }
        });

        document.body.appendChild(floatingButton);
        document.body.appendChild(saveModal);
    }

    createSaveInterface();
})();
/** Author: Vishal Joshi (vishaljoshi9694@gmail.com) **/
import { getAuthHeaders, logout } from './auth.js';

const API_BASE = '/api';

async function handleResponse(response, endpoint) {
    if (response.status === 401) { logout(); return null; }
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: `API Error: ${response.status}` }));
        console.error(`API Error ${endpoint}:`, error);
        throw new Error(error.detail || `Request failed: ${response.status}`);
    }
    return response.json();
}

export async function getBrokers() {
    try {
        const response = await fetch(`${API_BASE}/brokers/`, { headers: getAuthHeaders() });
        return await handleResponse(response, '/brokers/') || [];
    } catch (error) { return []; }
}

export async function addBroker(brokerName, credentials) {
    try {
        const response = await fetch(`${API_BASE}/brokers/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify({ broker_name: brokerName, credentials })
        });
        return await handleResponse(response, '/brokers/');
    } catch (error) { alert(error.message); return null; }
}

export async function deleteBroker(brokerId) {
    try {
        const response = await fetch(`${API_BASE}/brokers/${brokerId}`, { method: 'DELETE', headers: getAuthHeaders() });
        return await handleResponse(response, `/brokers/${brokerId}`);
    } catch (error) { return null; }
}

export async function getUserProfile() {
    try {
        const response = await fetch(`${API_BASE}/auth/me`, { headers: getAuthHeaders() });
        return await handleResponse(response, '/auth/me');
    } catch (error) { return null; }
}

export async function getHoldings() {
    try {
        const response = await fetch(`${API_BASE}/holdings/`, { headers: getAuthHeaders() });
        return await handleResponse(response, '/holdings/');
    } catch (error) { return null; }
}

export async function getAISummary() {
    try {
        const response = await fetch(`${API_BASE}/ai/summary/holdings`, { headers: getAuthHeaders() });
        return await handleResponse(response, '/ai/summary/holdings');
    } catch (error) { return null; }
}

export async function getAISingleStock(symbol) {
    try {
        const response = await fetch(`${API_BASE}/ai/analyze/${symbol}`, { headers: getAuthHeaders() });
        return await handleResponse(response, `/ai/analyze/${symbol}`);
    } catch (error) { return null; }
}

export async function getAllBalances() {
    try {
        const response = await fetch(`${API_BASE}/trades/balance`, { headers: getAuthHeaders() });
        const data = await handleResponse(response, '/trades/balance');
        // Handle new structured response: { total_balance: X, brokers: {...} }
        return data || { total_balance: 0, brokers: {} };
    } catch (error) { return { total_balance: 0, brokers: {} }; }
}

export async function getTradeHistory() {
    try {
        const response = await fetch(`${API_BASE}/trades/history`, { headers: getAuthHeaders() });
        return await handleResponse(response, '/trades/history') || [];
    } catch (error) { return []; }
}

export async function getSignals(segment = 'STOCK') {
    try {
        const response = await fetch(`${API_BASE}/signals/?segment=${segment}`, { headers: getAuthHeaders() });
        return await handleResponse(response, '/signals/') || [];
    } catch (error) { return []; }
}

export async function placeOrder(orderData) {
    try {
        const response = await fetch(`${API_BASE}/trades/place`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify(orderData)
        });
        return await handleResponse(response, '/trades/place');
    } catch (error) { throw error; }
}

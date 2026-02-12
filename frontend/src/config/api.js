// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export const API = {
  auth: {
    register: `${API_BASE_URL}/auth/register`,
    login: `${API_BASE_URL}/auth/login`,
    me: `${API_BASE_URL}/auth/me`,
    connectWallet: `${API_BASE_URL}/auth/wallet/connect`,
  },
  groups: {
    list: `${API_BASE_URL}/groups`,
    create: `${API_BASE_URL}/groups/create`,
    get: (id) => `${API_BASE_URL}/groups/${id}`,
    addMember: (id) => `${API_BASE_URL}/groups/${id}/members`,
    removeMember: (groupId, memberId) => `${API_BASE_URL}/groups/${groupId}/members/${memberId}`,
  },
  expenses: {
    add: (groupId) => `${API_BASE_URL}/expenses/${groupId}/add`,
    list: (groupId) => `${API_BASE_URL}/expenses/${groupId}`,
  },
  settlements: {
    calculate: `${API_BASE_URL}/settlements/calculate`,
    get: (id) => `${API_BASE_URL}/settlements/${id}`,
    execute: (id) => `${API_BASE_URL}/settlements/${id}/execute`,
  },
};

export const apiCall = async (url, options = {}) => {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || error.message || `HTTP Error: ${response.status}`);
  }

  return response.json();
};

export const saveToken = (token) => {
  localStorage.setItem("token", token);
};

export const getToken = () => {
  return localStorage.getItem("token");
};

export const clearToken = () => {
  localStorage.removeItem("token");
};

export const isAuthenticated = () => {
  return !!localStorage.getItem("token");
};

export default API;

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

// Token management
const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const AUTH_STORAGE_KEYS = [ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY];

type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

type RegisterResponse = {
  success: boolean;
  message: string;
  email: string;
  organization_name: string;
  requires_otp: boolean;
};

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (token && isJwtExpired(token)) {
    clearTokens();
    return null;
  }
  return token;
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  const token = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (token && isJwtExpired(token)) {
    clearTokens();
    return null;
  }
  return token;
}

export function setTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  document.cookie = `${ACCESS_TOKEN_KEY}=${accessToken}; path=/; max-age=86400; SameSite=Lax`;
  document.cookie = `${REFRESH_TOKEN_KEY}=${refreshToken}; path=/; max-age=604800; SameSite=Lax`;
}

export function clearTokens(): void {
  if (typeof window === "undefined") return;
  AUTH_STORAGE_KEYS.forEach((key) => localStorage.removeItem(key));
  Object.keys(localStorage)
    .filter((key) => key.startsWith("auth:") || key.startsWith("recruiter:") || key.startsWith("org:"))
    .forEach((key) => localStorage.removeItem(key));
  Object.keys(sessionStorage)
    .filter((key) => key.startsWith("auth:") || key.startsWith("recruiter:") || key.startsWith("org:"))
    .forEach((key) => sessionStorage.removeItem(key));
  document.cookie = `${ACCESS_TOKEN_KEY}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; SameSite=Lax`;
  document.cookie = `${REFRESH_TOKEN_KEY}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; SameSite=Lax`;
  window.dispatchEvent(new Event("auth:cleared"));
}

function isJwtExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split(".")[1] ?? ""));
    if (!payload.exp) return false;
    return payload.exp * 1000 <= Date.now();
  } catch {
    return true;
  }
}

// Token refresh
async function refreshAccessToken(): Promise<string> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    throw new Error("No refresh token available");
  }

  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    clearTokens();
    throw new Error("Failed to refresh token");
  }

  const data = await response.json();
  setTokens(data.access_token, data.refresh_token);
  return data.access_token;
}

// API fetch with authentication and retry
export async function apiFetch<T>(
  path: string,
  init?: RequestInit & { skipAuth?: boolean },
  retryCount = 0
): Promise<T> {
  const accessToken = getAccessToken();
  const isFormData = typeof FormData !== "undefined" && init?.body instanceof FormData;
  const headers: Record<string, string> = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
  };
  if (init?.headers) {
    new Headers(init.headers).forEach((value, key) => {
      headers[key] = value;
    });
  }

  // Add auth header if token exists and not skipping auth
  if (accessToken && !init?.skipAuth) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

  // Handle 401 Unauthorized - try to refresh token
  if (response.status === 401 && !init?.skipAuth && accessToken && retryCount === 0) {
    try {
      const newToken = await refreshAccessToken();
      // Retry with new token
      return apiFetch<T>(path, { ...init, skipAuth: false }, retryCount + 1);
    } catch {
      // Refresh failed, clear tokens and redirect to login
      clearTokens();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      throw new Error("Authentication failed");
    }
  }

  if (response.status === 401 && !init?.skipAuth) {
    clearTokens();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new Error("Authentication failed");
  }

  if (!response.ok) {
    const error = await response.text();
    let message = error || `API error: ${response.status}`;
    try {
      const parsed = JSON.parse(error);
      const parsedMessage = parsed.detail || parsed.message;
      if (parsedMessage) {
        message = typeof parsedMessage === "string" ? parsedMessage : JSON.stringify(parsedMessage);
      }
    } catch {
      // Keep the raw response text when the backend does not return JSON.
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

// Auth API
export const authApi = {
  async register(data: { email: string; password: string; full_name: string; organization_name: string; organization_pin: string }) {
    return apiFetch<RegisterResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async login(data: { email: string; password: string }) {
    return apiFetch<TokenPair>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async me() {
    return apiFetch("/auth/me");
  },

  async logout() {
    try {
      await apiFetch("/auth/logout", {
        method: "POST",
      });
    } finally {
      clearTokens();
    }
  },

  async sendOtp(email: string) {
    return apiFetch("/auth/send-otp", {
      method: "POST",
      body: JSON.stringify({ email }),
      skipAuth: true,
    });
  },

  async verifyOtp(email: string, otp_code: string) {
    return apiFetch("/auth/verify-otp", {
      method: "POST",
      body: JSON.stringify({ email, otp_code }),
      skipAuth: true,
    });
  },

  async forgotPassword(email: string) {
    return apiFetch<{ success: boolean; message: string }>("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
      skipAuth: true,
    });
  },

  async verifyResetOtp(email: string, otp_code: string) {
    return apiFetch<{ success: boolean; message: string; reset_token: string }>("/auth/verify-reset-otp", {
      method: "POST",
      body: JSON.stringify({ email, otp_code }),
      skipAuth: true,
    });
  },

  async resetPassword(data: { email: string; reset_token: string; new_password: string; confirm_password: string }) {
    return apiFetch<{ success: boolean; message: string }>("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify(data),
      skipAuth: true,
    });
  },
};

// Jobs API
export const jobsApi = {
  async list() {
    return apiFetch("/jobs");
  },

  async get(id: string) {
    return apiFetch(`/jobs/${id}`);
  },

  async intelligence(id: string) {
    return apiFetch(`/jobs/${id}/intelligence`);
  },

  async create(data: any) {
    return apiFetch("/jobs", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async upload(title: string, file: File) {
    const formData = new FormData();
    if (title) formData.append("title", title);
    formData.append("file", file);
    return apiFetch("/jobs/upload", {
      method: "POST",
      headers: {},
      body: formData as any,
    });
  },

  async extract(file: File, title?: string) {
    const formData = new FormData();
    if (title) formData.append("title", title);
    formData.append("file", file);
    return apiFetch("/jobs/extract", {
      method: "POST",
      headers: {},
      body: formData as any,
    });
  },

  async delete(id: string) {
    return apiFetch(`/jobs/${id}`, { method: "DELETE" });
  },
};

// Resumes API
export const resumesApi = {
  async list() {
    return apiFetch("/resumes");
  },

  async upload(file: File, candidate: { candidate_name: string; email?: string; phone?: string; years_experience?: number; location?: string }) {
    const formData = new FormData();
    formData.append("candidate_name", candidate.candidate_name);
    if (candidate.email) formData.append("email", candidate.email);
    if (candidate.phone) formData.append("phone", candidate.phone);
    if (candidate.years_experience !== undefined) formData.append("years_experience", String(candidate.years_experience));
    if (candidate.location) formData.append("location", candidate.location);
    formData.append("file", file);
    return apiFetch("/resumes/upload", {
      method: "POST",
      headers: {}, // Let browser set Content-Type for FormData
      body: formData as any,
    });
  },

  async get(id: string) {
    return apiFetch(`/resumes/${id}`);
  },

  async delete(id: string) {
    return apiFetch(`/resumes/${id}`, { method: "DELETE" });
  },
};

// Candidates API
export const candidatesApi = {
  async list() {
    return apiFetch("/candidates");
  },

  async get(id: string) {
    return apiFetch(`/candidates/${id}`);
  },

  async delete(id: string) {
    return apiFetch(`/candidates/${id}`, { method: "DELETE" });
  },
};

// Search API
export const searchApi = {
  async candidates(data: { query: string; job_description_id?: string; limit?: number; offset?: number; skills?: string[]; location?: string }) {
    return apiFetch("/search/candidates", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

// AI API
export const aiApi = {
  async summary(candidateId: string) {
    return apiFetch("/ai/summary", {
      method: "POST",
      body: JSON.stringify({ candidate_id: candidateId }),
    });
  },

  async interviewQuestions(data: { candidate_id: string; job_description_id?: string; count: number }) {
    return apiFetch("/ai/interview-questions", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async compare(data: { candidate_ids: string[]; job_description_id?: string }) {
    return apiFetch("/ai/compare", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

// Matching API
export const matchingApi = {
  async rank(data: { job_description_id: string; limit?: number }) {
    return apiFetch("/matching/rank", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

// ATS API
export const atsApi = {
  async scoreCandidateForJob(jobId: string, candidateId: string) {
    return apiFetch(`/ats/jobs/${jobId}/candidates/${candidateId}/score`, {
      method: "POST",
    });
  },
};

// Feedback API
export const feedbackApi = {
  async ranking(data: { candidate_id: string; job_description_id?: string; action: string; rank_position?: number }) {
    return apiFetch("/feedback/ranking", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

// Analytics API
export const analyticsApi = {
  async executive() {
    return apiFetch("/analytics/executive");
  },
};

// Workspace API
export const workspaceApi = {
  async activation() {
    return apiFetch("/workspace/activation");
  },

  async loadDemo() {
    return apiFetch("/workspace/demo", {
      method: "POST",
    });
  },
};

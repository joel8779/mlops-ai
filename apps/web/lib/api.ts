export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

// Token management
const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";

type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearTokens(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
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
  if (response.status === 401 && accessToken && retryCount === 0) {
    try {
      const newToken = await refreshAccessToken();
      // Retry with new token
      return apiFetch<T>(path, { ...init, skipAuth: false }, retryCount + 1);
    } catch {
      // Refresh failed, clear tokens and redirect to login
      clearTokens();
      if (typeof window !== "undefined") {
        window.location.href = "/sign-in";
      }
      throw new Error("Authentication failed");
    }
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
  async register(data: { email: string; password: string; full_name: string; organization_name: string }) {
    return apiFetch<TokenPair>("/auth/register", {
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

  logout() {
    clearTokens();
    if (typeof window !== "undefined") {
      window.location.href = "/sign-in";
    }
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

  async create(data: any) {
    return apiFetch("/jobs", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

// Resumes API
export const resumesApi = {
  async upload(file: File) {
    const formData = new FormData();
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
};

// Candidates API
export const candidatesApi = {
  async list() {
    return apiFetch("/candidates");
  },

  async get(id: string) {
    return apiFetch(`/candidates/${id}`);
  },
};

// Search API
export const searchApi = {
  async candidates(data: { query: string; limit?: number; offset?: number; skills?: string[]; location?: string }) {
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

  async copilot(data: { query: string; context?: Record<string, any>; top_k?: number }) {
    return apiFetch("/ai/copilot", {
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
  async scoreResume(resumeId: string) {
    return apiFetch(`/ats/resumes/${resumeId}/score`, {
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

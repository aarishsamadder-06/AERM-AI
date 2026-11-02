export type Concern = "acne" | "dryness" | "redness" | "texture" | "dark_spots" | "sensitivity";
export type Product = { id: string; name: string; category: "cleanser" | "moisturizer" | "sunscreen" | "serum"; brand: string; price_inr: number; ingredients: string[]; concerns: Concern[]; why: string; match_explanation: string; usage: string; sample_data: boolean; source: string; image_url?: string | null; image_placeholder: string; fragrance_free: boolean; availability: "in_stock" | "limited" | "unavailable" };
export type RoutineStep = { time: "morning" | "evening" | "weekly"; step: string; action: string; rationale: string };
export type ImageQualityView = {
 view: "front" | "left" | "right";
 label: "quality_sufficient" | "insufficient";
 decision_score: number;
 score_kind: "decision_score";
};
export type ImageQualityAssessment = {
 available: boolean;
 model: string;
 views: ImageQualityView[];
 notice: string;
};
export type Analysis = { finding: { label: string; confidence: number; severity: "low" | "medium" | "high"; summary: string }; views: string[]; detected_concerns: Concern[]; matched_ingredients: string[]; rationale: string[]; routine: RoutineStep[]; observations: string[]; recommendations: string[]; products: Product[]; simulation_notice: string; image_quality?: ImageQualityAssessment | null };
const baseUrl = "";
let csrfToken: string | null = null;

async function getCsrfToken(forceRefresh = false): Promise<string> {
  if (csrfToken && !forceRefresh) return csrfToken;
  const response = await fetch(`${baseUrl}/api/auth/csrf`, { credentials: "include" });
  if (!response.ok) throw new Error("CSRF protection could not be initialized.");
  const body = await response.json();
  if (typeof body.csrf_token !== "string" || !body.csrf_token) {
    throw new Error("CSRF protection returned an invalid token.");
  }
  csrfToken = body.csrf_token;
  return body.csrf_token;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const method = (init?.method || "GET").toUpperCase();
  const headers = new Headers(init?.headers);
  const rotatesCsrf = path === "/api/auth/register" || path === "/api/auth/login";
  const needsCsrf = path === "/api/auth/register" || path === "/api/auth/login" || path === "/api/auth/logout";
  if (!["GET", "HEAD", "OPTIONS"].includes(method) && needsCsrf) {
    headers.set("X-CSRF-Token", await getCsrfToken());
  }
  const response = await fetch(`${baseUrl}${path}`, { credentials: "include", ...init, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail || "The request could not be completed.");
  }
  const body = response.status === 204 ? undefined : await response.json();
  if (rotatesCsrf) await getCsrfToken(true);
  if (path === "/api/auth/logout") csrfToken = null;
  return body;
}

export type User = { id: number; name: string; email: string };
export const register = (payload: { name: string; email: string; password: string }) =>
  request<User>("/api/auth/register", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
export const login = (payload: { email: string; password: string }) =>
  request<User>("/api/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
export const logout = () => request<void>("/api/auth/logout", { method: "POST" });
export const getCurrentUser = () => request<User>("/api/auth/me");

export function analyze(images: { front: File; left: File; right: File }, preferences: { budget_inr?: number; fragrance_free?: boolean } = {}): Promise<Analysis> {
  const data = new FormData();
  Object.entries(images).forEach(([slot, file]) => data.append(slot, file));
  if (preferences.budget_inr !== undefined) data.append("budget_inr", String(preferences.budget_inr));
  data.append("fragrance_free", String(preferences.fragrance_free ?? false));
  return request<Analysis>("/api/analyze", { method: "POST", body: data });
}
export type ProductFilters = { category?: string; brand?: string; max_budget?: number; ingredient?: string; fragrance_free?: boolean; sort?: "match" | "price_asc" | "price_desc" | "name" };
export const getProducts = (filters: ProductFilters = {}) => {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => { if (value !== undefined && value !== "" && value !== false) params.set(key, String(value)); });
  if (filters.fragrance_free) params.set("fragrance_free", "true");
  return request<Product[]>(`/api/products${params.size ? `?${params}` : ""}`);
};
export const getRecommendations = (concerns: Concern[], preferences: { budget_inr?: number; fragrance_free?: boolean; preferred_ingredients?: string[] } = {}) => request<{ products: Product[]; routine: RoutineStep[]; matched_ingredients: string[]; explanations: string[] }>("/api/recommendations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ concerns, ...preferences }) });

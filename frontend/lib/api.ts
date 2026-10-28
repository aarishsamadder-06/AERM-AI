export type Concern = "acne" | "dryness" | "redness" | "texture" | "dark_spots" | "sensitivity";
export type Product = { id: string; name: string; category: "cleanser" | "moisturizer" | "sunscreen" | "serum"; brand: string; price_inr: number; ingredients: string[]; concerns: Concern[]; why: string; match_explanation: string; usage: string; sample_data: boolean; source: string; image_url?: string | null; image_placeholder: string; fragrance_free: boolean; availability: "in_stock" | "limited" | "unavailable" };
export type RoutineStep = { time: "morning" | "evening" | "weekly"; step: string; action: string; rationale: string };
export type Analysis = { finding: { label: string; confidence: number; severity: "low" | "medium" | "high"; summary: string }; views: string[]; detected_concerns: Concern[]; matched_ingredients: string[]; rationale: string[]; routine: RoutineStep[]; observations: string[]; recommendations: string[]; products: Product[]; simulation_notice: string };
const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, init);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail || "The request could not be completed.");
  }
  return response.json();
}

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
